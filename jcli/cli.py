from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from .daemon import DaemonLockError, build_daemon
from .logging import LogManager
from .models import JobState
from .parser import JCLParser
from .store import JobStore


def default_state_dir() -> Path:
    return Path(os.environ.get("JCLI_HOME", Path.cwd() / ".jcli"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jcli", description="Job Control for Linux")
    parser.add_argument("--state-dir", default=str(default_state_dir()))
    parser.add_argument("--db-path")
    parser.add_argument("--log-dir")
    parser.add_argument("--pid-file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Start the daemon")
    start.add_argument("--foreground", action="store_true")
    start.add_argument("--poll-interval", type=float, default=1.0)
    start.add_argument("--max-concurrent-jobs", type=int, default=2)

    stop = subparsers.add_parser("stop", help="Stop the daemon")
    stop.add_argument("--timeout", type=float, default=10.0)

    submit = subparsers.add_parser("submit", help="Submit a JCLi script")
    submit.add_argument("script")

    subparsers.add_parser("status", help="Show job status")

    show_job = subparsers.add_parser("show-job", help="Show details for a job")
    show_job.add_argument("job")

    show_logs = subparsers.add_parser("show-logs", help="Show logs for a job or step")
    show_logs.add_argument("job")
    show_logs.add_argument("--step")
    show_logs.add_argument("--stream", choices=["stdout", "stderr", "job"], default="job")

    cancel = subparsers.add_parser("cancel", help="Cancel a queued or held job")
    cancel.add_argument("job")

    hold = subparsers.add_parser("hold", help="Hold a queued job")
    hold.add_argument("job")

    release = subparsers.add_parser("release", help="Release a held job")
    release.add_argument("job")

    run_daemon = subparsers.add_parser("run-daemon", help=argparse.SUPPRESS)
    run_daemon.add_argument("--poll-interval", type=float, default=1.0)
    run_daemon.add_argument("--max-concurrent-jobs", type=int, default=2)
    return parser


def _resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    state_dir = Path(args.state_dir)
    db_path = Path(args.db_path) if args.db_path else state_dir / "jcli.db"
    log_dir = Path(args.log_dir) if args.log_dir else state_dir / "logs"
    pid_file = Path(args.pid_file) if args.pid_file else state_dir / "daemon.pid"
    state_dir.mkdir(parents=True, exist_ok=True)
    return db_path, log_dir, pid_file


def _load_job(store: JobStore, job_token: str):
    return store.get_job(int(job_token)) if job_token.isdigit() else store.get_job_by_name(job_token.upper())


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    db_path, log_dir, pid_file = _resolve_paths(args)
    store = JobStore(db_path)
    logs = LogManager(log_dir)
    try:
        if args.command in {"start", "run-daemon"}:
            daemon = build_daemon(
                db_path,
                log_dir,
                pid_file,
                max_concurrent_jobs=args.max_concurrent_jobs,
                poll_interval=args.poll_interval,
            )
            if args.command == "start" and not args.foreground:
                command = [
                    sys.executable,
                    "-m",
                    "jcli.cli",
                    "--state-dir",
                    str(Path(args.state_dir)),
                    "run-daemon",
                    "--poll-interval",
                    str(args.poll_interval),
                    "--max-concurrent-jobs",
                    str(args.max_concurrent_jobs),
                ]
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                print(f"Daemon started with pid {process.pid}.")
                return 0
            try:
                daemon.start()
                return 0
            except DaemonLockError as exc:
                print(str(exc), file=sys.stderr)
                return 1

        if args.command == "stop":
            store.request_stop()
            if pid_file.exists():
                pid = int(pid_file.read_text(encoding="utf-8").strip())
                deadline = time.time() + args.timeout
                while time.time() < deadline:
                    if not pid_file.exists():
                        print("Daemon stopped.")
                        return 0
                    time.sleep(0.2)
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass
            print("Stop requested.")
            return 0

        if args.command == "submit":
            parse_result = JCLParser().parse_file(args.script)
            if parse_result.errors:
                for error in parse_result.errors:
                    print(f"{error.code} line {error.line}: {error.message}", file=sys.stderr)
                return 2
            job_id = store.submit_job(parse_result.job, held=parse_result.job.job_class == "H")
            print(f"Submitted job {parse_result.job.name} as id {job_id}.")
            return 0

        if args.command == "status":
            for job in store.list_jobs():
                print(f"{job.id:04d} {job.name:<12} {job.state.value:<10} class={job.job_class} priority={job.priority} user={job.user}")
            return 0

        if args.command == "show-job":
            job = _load_job(store, args.job)
            if job is None:
                print("Job not found.", file=sys.stderr)
                return 1
            print(f"Job {job.id} {job.name}")
            print(f"State: {job.state.value}")
            print(f"Class/Priority: {job.job_class}/{job.priority}")
            print(f"User: {job.user}")
            print(f"Current step: {job.current_step or '-'}")
            print(f"Exit code: {job.exit_code if job.exit_code is not None else '-'}")
            for step in store.get_steps(job.id):
                print(f"  {step.ordinal}. {step.name} {step.state.value} rc={step.return_code if step.return_code is not None else '-'} {step.program} {step.arguments}".rstrip())
            return 0

        if args.command == "show-logs":
            job = _load_job(store, args.job)
            if job is None:
                print("Job not found.", file=sys.stderr)
                return 1
            if args.stream == "job":
                path = logs.job_log_path(job.id, job.name)
                if not path.exists():
                    print("No job log found.")
                    return 0
                print(path.read_text(encoding="utf-8"))
                return 0
            if not args.step:
                print("--step is required for stdout/stderr logs.", file=sys.stderr)
                return 1
            stdout_path, stderr_path = logs.step_log_paths(job.id, args.step.upper())
            path = stdout_path if args.stream == "stdout" else stderr_path
            if not path.exists():
                print("No step log found.")
                return 0
            print(path.read_text(encoding="utf-8"))
            return 0

        if args.command in {"cancel", "hold", "release"}:
            job = _load_job(store, args.job)
            if job is None:
                print("Job not found.", file=sys.stderr)
                return 1
            if args.command == "cancel":
                store.cancel_job(job.id)
                store.add_event(job.id, "INFO", "job.cancelled", f"Job {job.name} cancelled by operator.")
                print(f"Cancelled job {job.id}.")
            elif args.command == "hold":
                if job.state != JobState.QUEUED:
                    print("Only queued jobs can be held.", file=sys.stderr)
                    return 1
                store.hold_job(job.id)
                print(f"Held job {job.id}.")
            elif args.command == "release":
                if job.state != JobState.HELD:
                    print("Only held jobs can be released.", file=sys.stderr)
                    return 1
                store.release_job(job.id)
                print(f"Released job {job.id}.")
            return 0

        parser.error("unsupported command")
        return 2
    finally:
        logs.close()


if __name__ == "__main__":
    raise SystemExit(main())
