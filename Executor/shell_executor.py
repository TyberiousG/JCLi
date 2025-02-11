import subprocess
from Logging.logger import Logger

class ShellExecutor:
    def __init__(self):
        self.logger = Logger()

    def execute(self, job):
        self.logger.log_event(f"Executing shell script: {job.program}")
        try:
            result = subprocess.run(
                ["/bin/bash", job.program] + job.arguments.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.logger.log_job_output(job.name, result.stdout, result.stderr)
            status = "COMPLETED" if result.returncode == 0 else "FAILED"
            self.logger.log_event(f"Shell job '{job.name}' finished with status: {status}")

            return {"status": status, "stdout": result.stdout, "stderr": result.stderr}

        except Exception as e:
            self.logger.log_error(f"Error executing shell job '{job.name}': {e}")
            return {"status": "FAILED", "stdout": "", "stderr": str(e)}
