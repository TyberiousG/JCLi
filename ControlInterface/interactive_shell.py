class InteractiveShell:
    def __init__(self, command_handler):
        self.command_handler = command_handler

    def run(self):
        """
        Starts the interactive shell loop, allowing continuous user input.
        """
        while self.command_handler.is_running:
            try:
                user_input = input("JCLi> ").strip()
                if user_input:
                    self.command_handler.handle_command(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\n[InteractiveShell] Exiting JCLi Control Interface.")
                self.command_handler.is_running = False
            except Exception as e:
                print(f"[InteractiveShell] Error: {e}")
