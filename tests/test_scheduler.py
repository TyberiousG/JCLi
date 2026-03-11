import tempfile
import unittest
from pathlib import Path

from jcli.models import JobDefinition, StepDefinition
from jcli.scheduler import JobScheduler, SchedulerConfig
from jcli.store import JobStore


def make_job(name: str, job_class: str, priority: int) -> JobDefinition:
    return JobDefinition(
        name=name,
        job_class=job_class,
        priority=priority,
        user="tester",
        steps=[StepDefinition(name="STEP1", program="python", arguments="--version")],
    )


class SchedulerTests(unittest.TestCase):
    def test_priority_and_fifo_ordering(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JobStore(Path(tmp) / "jobs.db")
            ids = [
                store.submit_job(make_job("LOW", "C", 5)),
                store.submit_job(make_job("HIGH1", "A", 3)),
                store.submit_job(make_job("HIGH2", "A", 3)),
            ]
            scheduler = JobScheduler(store, SchedulerConfig(max_concurrent_jobs=3))
            jobs = scheduler.next_jobs()
            self.assertEqual(["HIGH1", "HIGH2", "LOW"], [job.name for job in jobs])
            self.assertEqual(3, len(ids))

    def test_max_concurrent_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JobStore(Path(tmp) / "jobs.db")
            store.submit_job(make_job("JOB1", "A", 1))
            store.submit_job(make_job("JOB2", "A", 1))
            scheduler = JobScheduler(store, SchedulerConfig(max_concurrent_jobs=1))
            jobs = scheduler.next_jobs()
            self.assertEqual(1, len(jobs))


if __name__ == "__main__":
    unittest.main()
