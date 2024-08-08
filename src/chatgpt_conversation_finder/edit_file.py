import logging
import platform
import subprocess

from pathlib import Path

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.exceptions import ConfigException


class EditFile:
    def __init__(self, config: Config):
        self.config = config

    def edit_config_file(self) -> None:
        """Edit the config file."""
        config_path = self.config.get_config_path()
        self.edit_file(config_path)

    def edit_file(self, file: Path) -> None:
        """Edit the config file."""
        cfg = self.config.config["Editor"]
        if platform.system() == "Linux":
            editor = cfg["Linux"]
            cmd = editor
            args = [str(file)]
        elif platform.system() == "Darwin":
            cmd = "open"
            editor = cfg["MacOS"]
            args = ["-a", editor, str(file)]
        elif platform.system() == "Windows":
            editor = cfg["Windows"]
            cmd = editor
            args = [str(file)]
        else:
            raise ConfigException(f"Unknown platform: {platform.system()}")
        logging.info(f"Running: {cmd} {args}")
        subprocess.Popen([cmd, *args], start_new_session=True)
