import time
from QueueInterface.queue_commands import QueueCommands

class QueueMenu:
    def __init__(self, daemon):
        self.daemon = daemon
        self.queue_commands = QueueCommands(daemon)
        self.running = True

    def display_queue(self):
        print("\n" + "="*50)
        print("=================| QUEUED JOBS |==================")
        print("="*50)

        if not self.daemon.scheduler.job_queue and not self.daemon.held_jobs:
            print("No jobs are currently queued.")
        else:
            # Display jobs in the scheduler queue
            for job in self.daemon.scheduler.list_jobs():
                status = self.daemon.job_lifecycle.job_status.get(job.name, "QUEUED")
                print(f"JOB${job.name} | Class: {job.job_class} | Priority: {job.priority} | Status: {status} | User: {job.user}")
            for job in self.daemon.held_jobs:
                print(f"JOB${job.name} | Class: {job.job_class} | Priority: {job.priority} | Status: HELD | User: {job.user}")

            print("="*50)
            print("Commands: R C F RL <job>")
            print("Type 'EXIT' to return to the main menu.")
            print("="*50)

    def run(self):
        self.running = True  # Reset running flag every time the menu is launched

        while self.running:
            self.display_queue()
            command = input("$JCLQ ").strip().upper()

            if command == "EXIT":
                self.running = False
            elif command:
                self.queue_commands.handle_command(command)
