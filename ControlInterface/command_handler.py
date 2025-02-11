from Daemon.daemon import JobQueueDaemon
from Interpreter.main import JCLiInterpreter

class CommandHandler:
    def __init__(self):
        self.daemon = JobQueueDaemon()
        self.interpreter = JCLiInterpreter()
        self.commands = {
            "START": self.start_daemon,
            "STOP": self.stop_daemon,
            "SUBMIT": self.submit_job,
            "STATUS": self.job_status,
            "HELP": self.show_help,
            "EXIT": self.exit_interface
        }
        self.is_running = True

    def handle_command(self, command_line):
        """
        Parses and executes the given command line input.

        Args:
            command_line (str): The command entered by the user.
        """
        parts = command_line.strip().split(maxsplit=1)
        command = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"[CommandHandler] Unknown command: '{command}'. Type 'HELP' for a list of commands.")

    def start_daemon(self, _):
        if not self.daemon.running:
            self.daemon.start()
            print("[CommandHandler] Daemon started.")
        else:
            print("[CommandHandler] Daemon is already running.")

    def stop_daemon(self, _):
        if self.daemon.running:
            self.daemon.stop()
            print("[CommandHandler] Daemon stopped.")
        else:
            print("[CommandHandler] Daemon is not running.")

    def submit_job(self, file_path):
        if not file_path:
            print("[CommandHandler] Usage: SUBMIT <path_to_jcli_script>")
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
                print(f"[CommandHandler] Job '{job.name}' submitted successfully.")

        except FileNotFoundError:
            print(f"[CommandHandler] Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"[CommandHandler] An unexpected error occurred: {e}")


    def job_status(self, _):
        for job_name, status in self.daemon.job_lifecycle.job_status.items():
            print(f"[Status] Job '{job_name}': {status}")

    def show_help(self, _):
        print("""
Available Commands:
  START               - Start the JCLi Daemon
  STOP                - Stop the JCLi Daemon
  SUBMIT <JCL Script> - Submit a new job
  STATUS              - Display the status of all jobs
  HELP                - Show this help message
  EXIT                - Exit the JCLi Control Interface
        """)

    def exit_interface(self, _):
        print("[CommandHandler] Exiting JCLi Control Interface.")
        self.is_running = False
