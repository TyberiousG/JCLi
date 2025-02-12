class QueueCommands:
    def __init__(self, daemon):
        self.daemon = daemon

    def handle_command(self, command):
        parts = command.split()
        if len(parts) != 2:
            print("SYNTAX ERROR. R,C,F,RL - ENTER JOB. READY.")
            return

        action, job_name = parts
        job = self._find_job(job_name)

        if not job:
            print(f"JOB '{job_name}' NOT FOUND. REENTER. READY.")
            return

        if action == "R":
            self.restart_job(job)
        elif action == "C":
            self.cancel_job(job)
        elif action == "F":
            self.force_job(job)
        elif action == "RL":
            self.release_held_job(job)
        else:
            print("UNKNOWN COMMAND. REENTER. READY.")

    def _find_job(self, job_name):
   
        for job in self.daemon.job_queue:
            if job.name == job_name:
                return job

        
        for job in self.daemon.held_jobs:
            if job.name == job_name:
                return job

        return None

    def restart_job(self, job):
        print(f"$R '{job.name}'...")
        self.cancel_job(job)  # Cancel the job first
        self.daemon.submit_job(job)  # Resubmit the job

    def cancel_job(self, job):
        print(f"$C '{job.name}'...")
        self.daemon.job_queue.remove(job)
        self.daemon.job_lifecycle.job_status[job.name] = "CANCELLED"

    def force_job(self, job):
        print(f"$F '{job.name}'...")
        self.daemon.job_queue.remove(job)
        self.daemon.execute_job(job)
        self.daemon.job_lifecycle.job_status[job.name] = "FORCED"
        
    def release_held_job(self, job):
        if self.daemon.job_lifecycle.job_status.get(job.name) == "HELD":
            self.daemon.held_jobs.remove(job)  # ✅ Remove from held jobs
            self.daemon.scheduler.add_job(job)
            self.daemon.job_lifecycle.update_status(job, "QUEUED")
            print(f"$RL Job '{job.name}' has been released from hold and queued for execution.")
        else:
            print(f"$RL '{job.name}' is not currently held.")