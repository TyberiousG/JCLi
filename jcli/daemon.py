from __future__ import annotations

import os
import signal
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from .executor import JobExecutor
from .logging import LogManager
from .models import JobState
from .scheduler import JobScheduler, SchedulerConfig
from .store import JobStore


class DaemonLockError(RuntimeError):
    pass


class JCLiDaemon:
    def __init__(
        self,
        store: JobStore,
        scheduler: JobScheduler,
        executor: JobExecutor,
        logs: LogManager,
        *,
        pid_file: str | Path,
        poll_interval: float = 1.0,
    ):
        self.store = store
        self.scheduler = scheduler
        self.executor = executor
        self.logs = logs
        self.pid_file = Path(pid_file)
        self.poll_interval = poll_interval
        self._running = False
        self._pool = ThreadPoolExecutor(max_workers=self.scheduler.config.max_concurrent_jobs)

    def start(self) -> None:
        self._acquire_pid()
        recovered = self.store.recover_interrupted_jobs()
        self.store.clear_stop_request(os.getpid())
        self.logs.system(f"Daemon started with pid={os.getpid()} recovered={recovered}.")
        self._running = True

        def _handle_signal(signum, _frame):
            self.logs.system(f"Daemon received signal {signum}; stopping.")
            self._running = False
            self.store.request_stop(os.getpid())

        signal.signal(signal.SIGTERM, _handle_signal)
        signal.signal(signal.SIGINT, _handle_signal)

        try:
            while self._running and not self.store.stop_requested():
                self._reap_finished()
                for job in self.scheduler.next_jobs():
                    self.store.transition_job(job.id, JobState.RUNNING)
                    self._pool.submit(self.executor.execute_job, job.id)
                time.sleep(self.poll_interval)
        finally:
            self._pool.shutdown(wait=True)
            self.logs.system("Daemon stopping gracefully.")
            self.store.clear_stop_request(None)
            self._release_pid()

    def _reap_finished(self) -> None:
        # Futures are fire-and-forget because job state is persisted by the executor.
        return None

    def _acquire_pid(self) -> None:
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        if self.pid_file.exists():
            pid_text = self.pid_file.read_text(encoding="utf-8").strip()
            if pid_text.isdigit():
                pid = int(pid_text)
                try:
                    os.kill(pid, 0)
                    raise DaemonLockError(f"Daemon already running with pid {pid}.")
                except OSError:
                    pass
        self.pid_file.write_text(str(os.getpid()), encoding="utf-8")

    def _release_pid(self) -> None:
        if self.pid_file.exists():
            self.pid_file.unlink()


def build_daemon(db_path: str | Path, log_dir: str | Path, pid_file: str | Path, *, max_concurrent_jobs: int = 2, poll_interval: float = 1.0) -> JCLiDaemon:
    store = JobStore(db_path)
    logs = LogManager(log_dir)
    scheduler = JobScheduler(store, SchedulerConfig(max_concurrent_jobs=max_concurrent_jobs))
    executor = JobExecutor(store, logs)
    return JCLiDaemon(store, scheduler, executor, logs, pid_file=pid_file, poll_interval=poll_interval)
