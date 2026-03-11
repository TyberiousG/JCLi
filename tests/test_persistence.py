import tempfile
import unittest
from pathlib import Path

from jcli.models import JobDefinition, JobState, StepDefinition
from jcli.store import JobStore


class PersistenceTests(unittest.TestCase):
    def test_hold_release_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JobStore(Path(tmp) / "jobs.db")
            job = JobDefinition(
                name="HOLDME",
                job_class="H",
                priority=5,
                user="tester",
                steps=[StepDefinition(name="STEP1", program="python", arguments="--version")],
            )
            job_id = store.submit_job(job, held=True)
            self.assertEqual(JobState.HELD, store.get_job(job_id).state)
            store.release_job(job_id)
            self.assertEqual(JobState.QUEUED, store.get_job(job_id).state)
            store.transition_job(job_id, JobState.RUNNING)
            recovered = store.recover_interrupted_jobs()
            self.assertEqual(1, recovered)
            self.assertEqual(JobState.QUEUED, store.get_job(job_id).state)


if __name__ == "__main__":
    unittest.main()
