import os
import shutil
from pathlib import Path

import tomllib


class Config:
    def __init__(self, usr_config_path: str | None = None):
        self.DEFAULT_CONFIG_PATH = Path(__file__).parent / "config"

        self.get_config_dir(usr_config_path)

        self.ENTRIES_PATH = self.config_dir / "entries.toml"
        self.STYLE_PATH = self.config_dir / "style.qss"

    def get_config_dir(self, usr_config_path: str | None = None):
        """
        Gets the config path
        """

        if usr_config_path:
            self.config_dir = Path(usr_config_path).expanduser()
        else:
            # check what operating system is used
            if os.name == "nt":  # windows
                print("not supportet yet. Define a config_path!")
            else:
                # macos or linux
                self.config_dir = Path.home() / ".config" / "roentgenium"

    def write_defaults_config(self):
        """
        Creates the default config in home/.config/roentgenium/
        """

        self.config_dir.mkdir(parents=True, exist_ok=True)

        for file in self.DEFAULT_CONFIG_PATH.iterdir():
            try:
                shutil.copy(file, self.config_dir / file.name)
                print(f"File '{file}' copied to '{self.config_dir / file.name}")
            except FileNotFoundError:
                print(f"Source file '{file}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def load_config(self):
        """
        Loads config
        """
        CONFIG_FILE = self.config_dir / "config.toml"

        # Load main config
        if not CONFIG_FILE.exists():
            self.write_defaults_config()

        try:
            with CONFIG_FILE.open("rb") as f:
                config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"TOML decode error: {e}")

        # config = toml.load(CONFIG_FILE)

        # ----------------------------
        # Config dir
        # ----------------------------
        self.config_dir: Path = Path(config["path"]["config"]).expanduser()

        # ----------------------------
        # Window position
        # ----------------------------
        self.WINDOW_X: int = config["window"]["x"]
        self.WINDOW_Y: int = config["window"]["y"]
        self.WINDOW_WIDTH: int = config["window"]["width"]
        self.WINDOW_HEIGHT: int = config["window"]["height"]
        self.WINDOW_TOP_OFFSET: int = config["window"]["top_offset"]

        # ----------------------------
        # Window margin
        # ----------------------------
        self.WINDOW_MARGIN_LEFT: int = config["window"]["margin_left"]
        self.WINDOW_MARGIN_TOP: int = config["window"]["margin_top"]
        self.WINDOW_MARGIN_RIGHT: int = config["window"]["margin_right"]
        self.WINDOW_MARGIN_BOTTOM: int = config["window"]["margin_bottom"]

        # ----------------------------
        # Entry config
        # ----------------------------
        self.ENTRIES_VISIBLE_ENTRIES: int = config["entries"]["visible_entries"]
        self.ENTRIES_START_INDEX: int = config["entries"]["start_index"]
        self.ENTRIES_WINDOW_START: int = config["entries"]["window_start"]
        self.ENTRIES_DELTA: int = config["entries"]["delta"]

        # ----------------------------
        # Fuzzy searching
        # ----------------------------
        self.FUZZY_LIMIT: int = config["fuzzy"]["fuzzy_limit"]

    # def load_style(self):
    #     """
    #     Loads style config
    #     """
    #     STYLE_FILE = self.config_dir / "style.qss"

    #     # Load main config
    #     if not STYLE_FILE.exists():
    #         self.write_defaults_config()

    #     config = toml.load(STYLE_FILE)
