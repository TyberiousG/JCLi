import heapq
from Daemon.priority_manager import PriorityManager

class JobScheduler:
    def __init__(self):
        self.priority_manager = PriorityManager()
        self.job_queue = []  # A min-heap for priority queueing

    def add_job(self, job):
        # Convert priority class (A, B, C) to a numeric value for the heap
        priority_value = self.priority_manager.get_priority_value(job.job_class, job.priority)
        heapq.heappush(self.job_queue, (priority_value, job))
        print(f"[Scheduler] Job '{job.name}' added to queue with priority {priority_value}.")

    def get_next_job(self):
        if self.job_queue:
            priority_value, job = heapq.heappop(self.job_queue)
            print(f"[Scheduler] Fetching job '{job.name}' with priority {priority_value}.")
            return job
        return None

    def has_pending_jobs(self):
        return len(self.job_queue) > 0
