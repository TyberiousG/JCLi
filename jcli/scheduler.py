from __future__ import annotations

from dataclasses import dataclass

from .models import JobRecord
from .store import JobStore


@dataclass(slots=True)
class SchedulerConfig:
    max_concurrent_jobs: int = 2


class JobScheduler:
    def __init__(self, store: JobStore, config: SchedulerConfig):
        self.store = store
        self.config = config

    def next_jobs(self) -> list[JobRecord]:
        available_slots = max(self.config.max_concurrent_jobs - self.store.count_running_jobs(), 0)
        if available_slots == 0:
            return []
        return self.store.get_next_queued_jobs(available_slots)
