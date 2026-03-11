from __future__ import annotations

import shlex
import subprocess

from .logging import LogManager
from .models import JobState, StepResult, utc_now
from .store import JobStore


class JobExecutor:
    def __init__(self, store: JobStore, logs: LogManager):
        self.store = store
        self.logs = logs

    def execute_job(self, job_id: int) -> JobState:
        job = self.store.get_job(job_id)
        if job is None:
            raise ValueError(f"Unknown job id {job_id}")
        steps = self.store.get_steps(job_id)
        self.store.transition_job(job_id, JobState.RUNNING)
        self.logs.append_job_event(job_id, job.name, f"Job {job.name} entered RUNNING.")

        final_state = JobState.SUCCEEDED
        final_code = 0
        for step in steps:
            self.store.transition_job(job_id, JobState.RUNNING, current_step=step.name)
            self.store.transition_step(step.id, JobState.RUNNING)
            self.logs.append_job_event(job_id, job.name, f"Starting step {step.name}: {step.program} {step.arguments}".strip())
            result = self._run_step(job_id, step.program, step.arguments, step.name)
            stdout_path, stderr_path = self.logs.write_step_output(job_id, step.name, result.stdout, result.stderr)
            self.store.transition_step(
                step.id,
                result.state,
                return_code=result.return_code,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
            )
            self.logs.append_job_event(
                job_id,
                job.name,
                f"Finished step {step.name} with rc={result.return_code} state={result.state.value}.",
                payload={"duration_seconds": result.duration_seconds},
            )
            if result.state != JobState.SUCCEEDED:
                final_state = JobState.FAILED
                final_code = result.return_code
                break

        self.store.transition_job(job_id, final_state, current_step=None, exit_code=final_code)
        self.logs.append_job_event(job_id, job.name, f"Job {job.name} completed with state {final_state.value}.")
        return final_state

    def _run_step(self, job_id: int, program: str, arguments: str, step_name: str) -> StepResult:
        started = utc_now()
        try:
            completed = subprocess.run(
                [program, *shlex.split(arguments)],
                capture_output=True,
                text=True,
                check=False,
            )
            finished = utc_now()
            return StepResult(
                step_name=step_name,
                state=JobState.SUCCEEDED if completed.returncode == 0 else JobState.FAILED,
                return_code=completed.returncode,
                started_at=started,
                finished_at=finished,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
        except Exception as exc:
            finished = utc_now()
            self.logs.system(f"Step {step_name} for job {job_id} failed before launch: {exc}", level=40)
            return StepResult(
                step_name=step_name,
                state=JobState.FAILED,
                return_code=127,
                started_at=started,
                finished_at=finished,
                stdout="",
                stderr=str(exc),
            )
