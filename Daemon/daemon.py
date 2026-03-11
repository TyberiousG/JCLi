import threading
import time
from Daemon.scheduler import JobScheduler
from Daemon.job_lifecycle import JobLifecycle

class JobQueueDaemon:
    def __init__(self):
        self.scheduler = JobScheduler()
        self.job_lifecycle = JobLifecycle()
        self.running = False
        self.job_queue = []
        self.held_jobs = []
        self.lock = threading.Lock()  # Ensures thread-safe queue operations

    def start(self):
        print("$JCLD Starting daemon...")
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        print("$JCLD Stopping daemon...")
        self.running = False

    def submit_job(self, job):
        with self.lock:
            print(f"$JCLD Submitting job: {job.name}")

            if job.job_class == "H":
                self.held_jobs.append(job)  # ✅ Add to held jobs list
                self.job_lifecycle.update_status(job, "HELD")
                print(f"$JCLD Job '{job.name}' is held until manually released.")
            else:
                self.scheduler.add_job(job)
                self.job_lifecycle.update_status(job, "QUEUED")

    def run(self):
        while self.running:
            with self.lock:
                job = self.scheduler.get_next_job()
                if job:
                    print(f"$JCLD Dispatching job: {job.name}")
                    self.job_lifecycle.update_status(job, "RUNNING")
                    self.job_lifecycle.execute_job(job)
            time.sleep(1)  # Prevents CPU overuse in the loop
