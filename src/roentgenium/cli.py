import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .__init__ import __version__
from .config import AppConfig
from .entries import create_all_entries
from .gui import SelectableLabelApp


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


def main(argv=None):
    args = parse_args(argv)

    # Point to default templates in project root
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    SOURCE_DIR = PROJECT_ROOT / "config"

    CONFIG = AppConfig(default_dir=SOURCE_DIR)

    # Load entries
    ENTRIES, INPUT_FIELD = create_all_entries(file_path=Path(args.config))

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
