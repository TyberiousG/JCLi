import os
from datetime import datetime

class JobLogger:
    def __init__(self, log_dir="logs/jobs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def log_output(self, job_name, stdout, stderr):
        """
        Logs the standard output and error of a job.

        Args:
            job_name (str): The name of the job.
            stdout (str): Standard output from the job.
            stderr (str): Standard error from the job.
        """
        log_file = os.path.join(self.log_dir, f"{job_name}_output.log")
        with open(log_file, "a") as f:
            f.write(f"--- Job Output Logged at {datetime.now()} ---\n")
            if stdout:
                f.write("[STDOUT]\n" + stdout + "\n")
            if stderr:
                f.write("[STDERR]\n" + stderr + "\n")
            f.write("\n")

    def log_status(self, job_name, status):
        """
        Logs the status of a job (QUEUED, RUNNING, COMPLETED, FAILED).

        Args:
            job_name (str): The name of the job.
            status (str): The current status of the job.
        """
        status_file = os.path.join(self.log_dir, f"{job_name}_status.log")
        with open(status_file, "a") as f:
            f.write(f"[{datetime.now()}] Job '{job_name}' status: {status}\n")
