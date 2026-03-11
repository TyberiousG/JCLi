__all__ = ["JCLiControlInterface", "CommandHandler", "InteractiveShell"]


def __getattr__(name):
    if name == "JCLiControlInterface":
        from .cli import JCLiControlInterface

        return JCLiControlInterface
    if name == "CommandHandler":
        from .command_handler import CommandHandler

        return CommandHandler
    if name == "InteractiveShell":
        from .interactive_shell import InteractiveShell

        return InteractiveShell
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
