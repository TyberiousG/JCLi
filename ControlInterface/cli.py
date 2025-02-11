from ControlInterface.command_handler import CommandHandler
from ControlInterface.interactive_shell import InteractiveShell

class JCLiControlInterface:
    def __init__(self):
        self.command_handler = CommandHandler()
        self.shell = InteractiveShell(self.command_handler)

    def start(self):
        """
        Starts the JCLi Control Interface.
        """
        print("[JCLi Control Interface] Welcome to JCLi!")
        print("Type 'HELP' to see available commands.")
        self.shell.run()

if __name__ == "__main__":
    interface = JCLiControlInterface()
    interface.start()
