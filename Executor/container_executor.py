import subprocess
from Logging.logger import Logger

class ContainerExecutor:
    def __init__(self):
        self.logger = Logger()

    def execute(self, job):
        self.logger.log_event(f"Executing container: {job.program}")
        try:
            docker_command = ["docker", "run"] + job.arguments.split() + [job.program]

            result = subprocess.run(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.logger.log_job_output(job.name, result.stdout, result.stderr)

            status = "COMPLETED" if result.returncode == 0 else "FAILED"
            self.logger.log_event(f"Container job '{job.name}' finished with status: {status}")

            return {"status": status, "stdout": result.stdout, "stderr": result.stderr}

        except Exception as e:
            self.logger.log_error(f"Error executing container job '{job.name}': {e}")
            return {"status": "FAILED", "stdout": "", "stderr": str(e)}
