import subprocess
from Logging.logger import Logger  # Placeholder for logging integration

class JobLifecycle:
    def __init__(self):
        self.job_status = {}  # Tracks status of jobs by name
        self.logger = Logger()  # Placeholder logger instance

    def update_status(self, job, status):
        """
        Updates the status of a job.

        Args:
            job: The job object.
            status (str): New status ('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED').
        """
        self.job_status[job.name] = status
        print(f"$JCLL Job '{job.name}' status updated to: {status}")
        self.logger.log_job_status(job.name, status)

    def execute_job(self, job):
        """
        Executes the job using subprocess.

        Args:
            job: The job object to execute.
        """
        try:
            print(f"$JCLL Executing job '{job.name}'...")
            result = subprocess.run(
                [job.program] + job.arguments.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Log output similar to SYSOUT
            self.logger.log_job_output(job.name, result.stdout, result.stderr)
            
            if result.returncode == 0:
                self.update_status(job, "COMPLETED")
            else:
                self.update_status(job, "FAILED")
                print(f"$JCLL Job '{job.name}' failed with return code {result.returncode}")
        except Exception as e:
            self.update_status(job, "FAILED")
            self.logger.log_job_output(job.name, "", f"Execution error: {str(e)}")
            print(f"$JCLL Error executing job '{job.name}': {e}")
