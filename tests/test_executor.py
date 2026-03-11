import sys
import tempfile
import unittest
from pathlib import Path

from jcli.executor import JobExecutor
from jcli.logging import LogManager
from jcli.models import JobDefinition, JobState, StepDefinition
from jcli.store import JobStore


class ExecutorTests(unittest.TestCase):
    def test_executor_captures_output_and_return_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            store = JobStore(tmp_path / "jobs.db")
            logs = LogManager(tmp_path / "logs")
            executor = JobExecutor(store, logs)
            job = JobDefinition(
                name="ECHO",
                job_class="A",
                priority=1,
                user="tester",
                steps=[
                    StepDefinition(
                        name="STEP1",
                        program=sys.executable,
                        arguments='-c "print(\'hello from job\')"',
                    )
                ],
            )
            job_id = store.submit_job(job)
            state = executor.execute_job(job_id)
            self.assertEqual(JobState.SUCCEEDED, state)
            record = store.get_job(job_id)
            step = store.get_steps(job_id)[0]
            self.assertEqual(JobState.SUCCEEDED, record.state)
            self.assertEqual(0, record.exit_code)
            self.assertIn("hello from job", Path(step.stdout_path).read_text(encoding="utf-8"))
            logs.close()

    def test_executor_marks_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            store = JobStore(tmp_path / "jobs.db")
            logs = LogManager(tmp_path / "logs")
            executor = JobExecutor(store, logs)
            job = JobDefinition(
                name="FAIL",
                job_class="A",
                priority=1,
                user="tester",
                steps=[StepDefinition(name="STEP1", program=sys.executable, arguments='-c "import sys; sys.exit(7)"')],
            )
            job_id = store.submit_job(job)
            state = executor.execute_job(job_id)
            self.assertEqual(JobState.FAILED, state)
            self.assertEqual(7, store.get_job(job_id).exit_code)
            logs.close()


if __name__ == "__main__":
    unittest.main()
