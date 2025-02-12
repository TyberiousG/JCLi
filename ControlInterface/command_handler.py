from Daemon.daemon import JobQueueDaemon
from Interpreter.main import JCLiInterpreter
from QueueInterface.queue_menu import QueueMenu  # Import the Queue Menu

class CommandHandler:
    def __init__(self):
        self.daemon = JobQueueDaemon()
        self.interpreter = JCLiInterpreter()
        self.queue_menu = QueueMenu(self.daemon)  # Initialize Queue Menu
        self.commands = {
            "START": self.start_daemon,
            "STOP": self.stop_daemon,
            "SUBMIT": self.submit_job,
            "STATUS": self.job_status,
            "QUEUE": self.show_queue,      # Add the QUEUE command
            "HELP": self.show_help,
            "EXIT": self.exit_interface
        }
        self.is_running = True

    def handle_command(self, command_line):
        parts = command_line.strip().split(maxsplit=1)
        command = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"$JCLH Unknown command: '{command}'. Type 'HELP' for a list of commands.")

    def start_daemon(self, _):
        if not self.daemon.running:
            self.daemon.start()
            print("$JCLH Daemon started.")
        else:
            print("$JCLH Daemon is already running.")

    def stop_daemon(self, _):
        if self.daemon.running:
            self.daemon.stop()
            print("$JCLH Daemon stopped.")
        else:
            print("$JCLH Daemon is not running.")

    def submit_job(self, file_path):
        if not file_path:
            print("$JCLH Usage: SUBMIT <path_to_jcli_script>")
            return

        try:
            with open(file_path, 'r') as file:
                jcl_script = file.read()

            job = self.interpreter.parser.parse(jcl_script)
            errors = self.interpreter.validator.validate(job)

            if errors:
                for error in errors:
                    print(f"Validation Error: {error}")
            else:
                self.daemon.submit_job(job)
                print(f"$JCLH Job '{job.name}' submitted successfully.")

        except FileNotFoundError:
            print(f"$JCLH Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"$JCLH An unexpected error occurred: {e}")

    def job_status(self, _):
        for job_name, status in self.daemon.job_lifecycle.job_status.items():
            print(f"$JCLS Job '{job_name}': {status}")

    def show_queue(self, _):
        self.queue_menu.run()  # Launch the interactive Queue Menu

    def show_help(self, _):
        print("""
Available Commands:
  START               - Start the JCLi Daemon
  STOP                - Stop the JCLi Daemon
  SUBMIT <JCL Script> - Submit a new job
  STATUS              - Display the status of all jobs
  QUEUE               - View and manage the job queue
  HELP                - Show this help message
  EXIT                - Exit the JCLi Control Interface
        """)

    def exit_interface(self, _):
        print("$JCLH Exiting JCLi Control Interface.")
        self.is_running = False
