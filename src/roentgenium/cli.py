import argparse
import sys

from PySide6.QtWidgets import QApplication

from .__init__ import __version__
from .config import Config
from .gui import MainWindow
from .items import create_all_groups


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
    parser.add_argument("--groups", default="all", help="Selected Groups")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Point to default templates in project root
    # PROJECT_ROOT = Path(__file__).resolve().parents[2]
    # SOURCE_DIR = PROJECT_ROOT / "config"

    CONFIG = Config(None)
    CONFIG.load_config()

    ALL_GROUPS = create_all_groups(CONFIG.config_dir / "entries.toml")

    # Start Qt app
    app = QApplication(sys.argv)

    # Apply style
    style_path = CONFIG.STYLE_PATH
    with style_path.open("r") as f:
        app.setStyleSheet(f.read())

    # Launch main window
    used_groups = args.groups
    if used_groups == "all":
        first_group_name = next(iter(ALL_GROUPS))
        first_group = ALL_GROUPS[first_group_name]
        main_window = MainWindow(
            CONFIG, list(ALL_GROUPS.values()), first_group.input_field
        )

    else:
        print("FIX MULTIPLE GROUPS")
        sys.exit(app.exec())

    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
