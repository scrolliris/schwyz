import sys

from pyramid.scripts.pserve import PServeCommand

from schwyz.env import load_dotenv_vars


def main(argv=None, quiet=False):
    """Runs original pserve with .env support."""
    if not argv:
        argv = sys.argv
    load_dotenv_vars()

    command = PServeCommand(argv, quiet=quiet)
    return command.run()


if __name__ == '__main__':
    sys.exit(main() or 0)
