from jcli.cli import main as cli_main


class JCLiControlInterface:
    """Compatibility shim for the original interactive entry point."""

    def start(self):
        return cli_main()


if __name__ == "__main__":
    raise SystemExit(cli_main())
