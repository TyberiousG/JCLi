import os
from datetime import datetime

class EventLogger:
    def __init__(self, log_dir="logs/system"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.event_log_file = os.path.join(self.log_dir, "events.log")
        self.error_log_file = os.path.join(self.log_dir, "errors.log")

    def log_event(self, event_message):
        """
        Logs general system events (e.g., daemon start/stop, job submission).

        Args:
            event_message (str): A message describing the system event.
        """
        with open(self.event_log_file, "a") as f:
            f.write(f"[{datetime.now()}] EVENT: {event_message}\n")

    def log_error(self, error_message):
        """
        Logs system errors (e.g., failed job executions, system exceptions).

        Args:
            error_message (str): A message describing the error.
        """
        with open(self.error_log_file, "a") as f:
            f.write(f"[{datetime.now()}] ERROR: {error_message}\n")
