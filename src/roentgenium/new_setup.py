import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .__init__ import __version__
from .entries import create_all_entries
from .gui import SelectableLabelApp
from .new_config import Config
from .new_items import create_all_groups


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


def load_items():
    CONFIG = Config(None)
    CONFIG.load_config()

    ALL_GROUPS = create_all_groups(CONFIG.ENTRIES_PATH)


def main(argv=None):
    args = parse_args(argv)

    # Start Qt app
    app = QApplication(sys.argv)

    # Apply style
    style_path = Path(args.style)
    if style_path.exists():
        with style_path.open("r") as f:
            app.setStyleSheet(f.read())

    # Launch main window
    main_window = SelectableLabelApp(ENTRIES, INPUT_FIELD, CONFIG)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
