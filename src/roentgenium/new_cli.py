import argparse

from .__init__ import __version__


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="roentgenium", description="A configurable PySide6 application launcher."
    )
    parser.add_argument(
        "--config", default="config/entries.toml", help="Path to the entries TOML file"
    )
    parser.add_argument(
        "--style", default="config/style.qss", help="Path to the QSS style file"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args(argv)
