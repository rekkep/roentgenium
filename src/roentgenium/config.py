import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Union

import toml


def get_config_dir(self, user_path: Optional[Union[str, Path]] = None):
    """Determine where to store/read config files."""

    if user_path:
        config_dir = Path(user_path).expanduser()
    else:
        # Default: ~/.config/roentgenium (Linux/macOS) or %APPDATA%\roentgenium (Windows)
        if os.name == "nt":
            config_dir = (
                Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
                / "roentgenium"
            )
        else:
            config_dir = Path.home() / ".config" / "roentgenium"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


class AppConfig:
    def __init__(
        self,
        config_dir: Path | None = None,
        default_dir: Path | None = None,
    ) -> None:
        self.config_dir = get_config_dir(config_dir)

        if default_dir:
            self._copy_default_configs(default_dir)

        # Paths to files
        self.PATH_CONFIG = self.config_dir / "config.toml"
        self.PATH_ENTRIES = self.config_dir / "entries.toml"
        self.PATH_STYLE = self.config_dir / "style.qss"

        # Load main config
        if not self.PATH_CONFIG.exists():
            raise FileNotFoundError(f"Config file not found: {self.PATH_CONFIG}")
        self.config = toml.load(self.PATH_CONFIG)

        # ----------------------------
        # Window position
        # ----------------------------
        self.WINDOW_X: int = self.config["window"]["x"]
        self.WINDOW_Y: int = self.config["window"]["y"]
        self.WINDOW_WIDTH: int = self.config["window"]["width"]
        self.WINDOW_HEIGHT: int = self.config["window"]["height"]
        self.WINDOW_TOP_OFFSET: int = self.config["window"]["top_offset"]

        # ----------------------------
        # Window margin
        # ----------------------------
        self.WINDOW_MARGIN_LEFT: int = self.config["window"]["margin_left"]
        self.WINDOW_MARGIN_TOP: int = self.config["window"]["margin_top"]
        self.WINDOW_MARGIN_RIGHT: int = self.config["window"]["margin_right"]
        self.WINDOW_MARGIN_BOTTOM: int = self.config["window"]["margin_bottom"]

        # ----------------------------
        # File paths
        # ----------------------------
        self.PATH_ENTRIES: Path = Path(self.config["path"]["entries"])
        self.PATH_STYLE: Path = Path(self.config["path"]["style"])
        self.PATH_CONFIG: Path = Path(self.config["path"]["config"])

        # ----------------------------
        # Entry list
        # ----------------------------
        self.ENTRIES_VISIBLE_ENTRIES: int = self.config["entries"]["visible_entries"]
        self.ENTRIES_START_INDEX: int = self.config["entries"]["start_index"]
        self.ENTRIES_WINDOW_START: int = self.config["entries"]["window_start"]
        self.ENTRIES_DELTA: int = self.config["entries"]["delta"]

        # ----------------------------
        # Fuzzy searching
        # ----------------------------
        self.FUZZY_LIMIT: int = self.config["fuzzy"]["fuzzy_limit"]

    def _copy_default_configs(self, source_dir: Path):
        """Copy default config files from project to user config folder."""
        default_files = ["config.toml", "entries.toml", "style.qss"]

        for f in default_files:
            src = Path(source_dir) / f
            dest = self.config_dir / f
            if not dest.exists():
                shutil.copy(src, dest)

    def set_to_default(self):
        # ----------------------------
        # Window position
        # ----------------------------
        self.WINDOW_X = 0
        self.WINDOW_Y = 0
        self.WINDOW_WIDTH = 400
        self.WINDOW_HEIGHT = 200
        self.WINDOW_TOP_OFFSET = 200

        # ----------------------------
        # Window margin
        # ----------------------------
        self.WINDOW_MARGIN_LEFT = 0
        self.WINDOW_MARGIN_TOP = 0
        self.WINDOW_MARGIN_RIGHT = 0
        self.WINDOW_MARGIN_BOTTOM = 0

        # ----------------------------
        # File paths
        # ----------------------------
        self.PATH_ENTRIES = Path("config/entries.toml")
        self.PATH_STYLE = Path("config/style.qss")
        self.PATH_CONFIG = Path("config/config.toml")

        # ----------------------------
        # Entry list
        # ----------------------------
        self.ENTRIES_VISIBLE_ENTRIES = 5
        self.ENTRIES_START_INDEX = 0
        self.ENTRIES_WINDOW_START = 0
        self.ENTRIES_DELTA = 1

        # ----------------------------
        # Fuzzy searching
        # ----------------------------
        self.FUZZY_LIMIT = 30
