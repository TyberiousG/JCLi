from Executor.shell_executor import ShellExecutor
from Executor.binary_executor import BinaryExecutor
from Executor.container_executor import ContainerExecutor
from Logging.logger import Logger

class JobExecutor:
    def __init__(self):
        self.shell_executor = ShellExecutor()
        self.binary_executor = BinaryExecutor()
        self.container_executor = ContainerExecutor()
        self.logger = Logger()

    def execute(self, job):
        self.logger.log_event(f"Starting execution for job '{job.name}'.")

        if job.program.endswith('.sh'):
            result = self.shell_executor.execute(job)
        elif job.program.endswith('.bin') or job.program.startswith('/'):
            result = self.binary_executor.execute(job)
        elif job.program.endswith('.container'):
            result = self.container_executor.execute(job)
        else:
            self.logger.log_event(f"Unknown job type for '{job.program}'. Defaulting to binary execution.")
            result = self.binary_executor.execute(job)

        status = result.get("status", "UNKNOWN")
        self.logger.log_job_status(job.name, status)
        self.logger.log_event(f"Job '{job.nam
