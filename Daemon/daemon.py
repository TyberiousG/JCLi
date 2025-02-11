import threading
import time
from Daemon.scheduler import JobScheduler
from Daemon.job_lifecycle import JobLifecycle

class JobQueueDaemon:
    def __init__(self):
        self.scheduler = JobScheduler()
        self.job_lifecycle = JobLifecycle()
        self.running = False
        self.lock = threading.Lock()  # Ensures thread-safe queue operations

    def start(self):
        print("[JCLi Daemon] Starting daemon...")
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        print("[JCLi Daemon] Stopping daemon...")
        self.running = False

    def submit_job(self, job):
        with self.lock:
            print(f"[JCLi Daemon] Submitting job: {job.name}")
            self.scheduler.add_job(job)
            self.job_lifecycle.update_status(job, "QUEUED")

    def run(self):
        while self.running:
            with self.lock:
                job = self.scheduler.get_next_job()
                if job:
                    print(f"[JCLi Daemon] Dispatching job: {job.name}")
                    self.job_lifecycle.update_status(job, "RUNNING")
                    self.job_lifecycle.execute_job(job)
                    self.job_lifecycle.update_status(job, "COMPLETED")
            time.sleep(1)  # Prevents CPU overuse in the loop
