from Logging.job_logger import JobLogger
from Logging.event_logger import EventLogger

class Logger:
    def __init__(self):
        self.job_logger = JobLogger()
        self.event_logger = EventLogger()

    def log_job_output(self, job_name, stdout, stderr):
        """
        Logs the output of a job (similar to SYSOUT in z/OS).

        Args:
            job_name (str): The name of the job.
            stdout (str): Standard output from the job.
            stderr (str): Standard error from the job.
        """
        self.job_logger.log_output(job_name, stdout, stderr)

    def log_job_status(self, job_name, status):
        """
        Logs the status of a job (QUEUED, RUNNING, COMPLETED, FAILED).

        Args:
            job_name (str): The name of the job.
            status (str): The status to log.
        """
        self.job_logger.log_status(job_name, status)

    def log_event(self, event_message):
        """
        Logs general system events.

        Args:
            event_message (str): A message describing the system event.
        """
        self.event_logger.log_event(event_message)

    def log_error(self, error_message):
        """
        Logs system errors.

        Args:
            error_message (str): A message describing the error.
        """
        self.event_logger.log_error(error_message)
