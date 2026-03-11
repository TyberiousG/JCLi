from Executor.shell_executor import ShellExecutor
from Executor.binary_executor import BinaryExecutor
from Executor.container_executor import ContainerExecutor
from Logging.logger import Logger
import shlex

class JobExecutor:
    def __init__(self):
        self.shell_executor = ShellExecutor()
        self.binary_executor = BinaryExecutor()
        self.container_executor = ContainerExecutor()
        self.logger = Logger()

    def execute(self, job):
        self.logger.log_event(f"Starting execution for job '{job.name}'.")

        steps = job.steps or [{"program": job.program, "arguments": job.arguments}]
        final_result = {"status": "COMPLETED", "stdout": "", "stderr": ""}

        for step in steps:
            step_job = type("StepJob", (), {
                "name": job.name,
                "program": step["program"],
                "arguments": step.get("arguments", ""),
            })()

            if step_job.program.endswith('.sh'):
                result = self.shell_executor.execute(step_job)
            elif step_job.program.endswith('.container'):
                result = self.container_executor.execute(step_job)
            else:
                result = self.binary_executor.execute(step_job)

            final_result = result
            if result.get("status") != "COMPLETED":
                break

        status = final_result.get("status", "UNKNOWN")
        self.logger.log_job_status(job.name, status)
        self.logger.log_event(f"Job '{job.name}' finished with status: {status}.")
        return final_result
