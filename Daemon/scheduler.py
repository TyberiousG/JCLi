import heapq
from Daemon.priority_manager import PriorityManager

class JobScheduler:
    def __init__(self):
        self.priority_manager = PriorityManager()
        self.job_queue = []  # A min-heap for priority queueing
        self._sequence = 0

    def add_job(self, job):
        # Convert priority class (A, B, C) to a numeric value for the heap
        priority_value = self.priority_manager.get_priority_value(job.job_class, job.priority)
        self._sequence += 1
        heapq.heappush(self.job_queue, (priority_value, self._sequence, job))
        print(f"[Scheduler] Job '{job.name}' added to queue with priority {priority_value}.")

    def get_next_job(self):
        if self.job_queue:
            priority_value, _, job = heapq.heappop(self.job_queue)
            print(f"[Scheduler] Fetching job '{job.name}' with priority {priority_value}.")
            return job
        return None

    def remove_job(self, job_name):
        for index, (_, _, queued_job) in enumerate(self.job_queue):
            if queued_job.name == job_name:
                del self.job_queue[index]
                heapq.heapify(self.job_queue)
                return queued_job
        return None

    def list_jobs(self):
        return [job for _, _, job in sorted(self.job_queue)]

    def has_pending_jobs(self):
        return len(self.job_queue) > 0
