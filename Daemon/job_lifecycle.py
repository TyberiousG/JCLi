import subprocess
import shlex
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
            steps = job.steps or [{"name": "STEP1", "program": job.program, "arguments": job.arguments}]

            for step in steps:
                command = [step["program"]] + shlex.split(step.get("arguments", ""))
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                stdout = result.stdout
                stderr = result.stderr
                if step.get("name"):
                    stdout = f"[{step['name']}]\n{stdout}" if stdout else ""
                    stderr = f"[{step['name']}]\n{stderr}" if stderr else ""

                self.logger.log_job_output(job.name, stdout, stderr)

                if result.returncode != 0:
                    self.update_status(job, "FAILED")
                    print(f"$JCLL Job '{job.name}' failed with return code {result.returncode}")
                    return

            self.update_status(job, "COMPLETED")
        except Exception as e:
            self.update_status(job, "FAILED")
            self.logger.log_error(f"Execution error for job '{job.name}': {str(e)}")
            self.logger.log_job_output(job.name, "", f"Execution error: {str(e)}")
            print(f"$JCLL Error executing job '{job.name}': {e}")
