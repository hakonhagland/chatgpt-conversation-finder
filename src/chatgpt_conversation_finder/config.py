import configparser
import importlib.resources  # access non-code resources
import logging
from configparser import ConfigParser
from pathlib import Path

import nltk
import platformdirs

from chatgpt_conversation_finder.constants import GrepColor
from chatgpt_conversation_finder.exceptions import ConfigException


class Config:
    # NOTE: This is made a class variable since it must be accessible from
    #   pytest before creating an object of this class
    chats_zip_fn = "chats.zip"
    config_fn = "config.ini"
    conversation_json_fn = "conversations.json"
    dirlock_fn = ".dirlock"
    idmap_fn = "idmap.json"
    prefix_index_fn = "prefix_index.json"
    sanitized_conversations_fn = "sanitized_conversations.json"
    word_index_fn = "word_index.json"

    def __init__(self) -> None:
        self.appname = "chatgpt_conversation_finder"
        self.lockfile_string = "author=HH, appname=chatgpt_conversation_finder"
        self.config_dir = self.check_config_dir()
        self.config_path = Path(self.config_dir) / self.config_fn
        self.read_config()
        self.datadir_path = self.get_data_dir_path()
        self.setup_nltk()

    def check_config_dir(self) -> Path:
        config_dir = platformdirs.user_config_dir(appname=self.appname)
        path = Path(config_dir)
        lock_file = path / self.dirlock_fn
        if path.exists():
            if path.is_file():
                raise ConfigException(
                    f"Config directory {str(path)} is a file. Expected directory"
                )
            self.check_correct_config_dir(lock_file)
        else:
            path.mkdir(parents=True)
            with open(str(lock_file), "a", encoding="utf_8") as fp:
                fp.write(self.lockfile_string)
        return path

    def check_correct_config_dir(self, lock_file: Path) -> None:
        """The config dir might be owned by another app with the same name"""
        if lock_file.exists():
            if lock_file.is_file():
                with open(str(lock_file), encoding="utf_8") as fp:
                    line = fp.readline()
                    if line.startswith(self.lockfile_string):
                        return
                msg = "bad content"
            else:
                msg = "is a directory"
        else:
            msg = "missing"
        raise ConfigException(
            f"Unexpected: Config dir lock file: {msg}. "
            f"The data directory {str(lock_file.parent)} might be owned by another app."
        )

    def check_correct_data_dir(self, lock_file: Path) -> None:
        """The data dir might be owned by another app with the same name"""
        if lock_file.exists():
            if lock_file.is_file():
                with open(str(lock_file), encoding="utf_8") as fp:
                    line = fp.readline()
                    if line.startswith(self.lockfile_string):
                        return
                msg = "bad content"
            else:
                msg = "is a directory"
        else:
            msg = "missing"
        raise ConfigException(
            f"Unexpected: Data dir lock file: {msg}. "
            f"The data directory {str(lock_file.parent)} might be owned by another app."
        )

    def get_config_dir(self) -> Path:
        return self.config_dir  # pragma: no cover

    def get_conversations_json_path(self) -> Path:
        return self.datadir_path / self.conversation_json_fn  # pragma: no cover

    def get_data_dir(self) -> Path:
        return self.datadir_path  # pragma: no cover

    def get_data_dir_path(self) -> Path:
        data_dir = platformdirs.user_data_dir(appname=self.appname)
        path = Path(data_dir)
        lock_file = path / self.dirlock_fn
        if path.exists():
            if path.is_file():
                raise ConfigException(
                    f"Data directory {str(path)} is a file. Expected directory"
                )
            self.check_correct_data_dir(lock_file)
        else:
            path.mkdir(parents=True)
            with open(str(lock_file), "a", encoding="utf_8") as fp:
                fp.write(self.lockfile_string)
        return path

    def get_config_path(self) -> Path:
        return self.config_path

    def get_filedialog_default_dir(self) -> str:
        path = self.config["FileDialog"]["default_dir"]
        if path == "_USER_DOWNLOAD_DIR_":
            path = platformdirs.user_downloads_dir()
        return path

    def get_grep_item(self, item: str, default: str) -> GrepColor:
        try:
            color = self.config["Grep"][item]
        except KeyError:
            logging.warning(
                f"Missing '{item}' in [Grep] section of config. Using default color '{default}'."
            )
            color = default
        return GrepColor.from_str(color)

    def get_grep_match_color(self) -> GrepColor:
        return self.get_grep_item("match_color", default="red")

    def get_grep_match_header_color(self) -> GrepColor:
        return self.get_grep_item("header_color", default="green")

    def get_grep_match_trailer_color(self) -> GrepColor:
        return self.get_grep_item("trailer_color", default="blue")

    def get_idmap_path(self) -> Path:
        return self.datadir_path / self.idmap_fn

    def get_max_prefix_length(self) -> int:
        return int(self.config["SearchIndex"]["max_prefix_length"])

    def get_prefix_index_path(self) -> Path:
        return self.datadir_path / self.prefix_index_fn

    def get_sanitized_conversations_path(self) -> Path:
        return self.datadir_path / self.sanitized_conversations_fn

    def get_word_index_path(self) -> Path:
        return self.datadir_path / self.word_index_fn

    def read_config(self) -> None:
        path = self.get_config_path()
        if path.exists():
            if not path.is_file():
                raise ConfigException(
                    f"Config filename {str(path)} exists, but filetype is not file"
                )
        else:
            with open(str(self.get_config_path()), "w", encoding="utf_8") as _:
                pass  # only create empty file
        config = configparser.ConfigParser()
        self.read_defaults(config)
        config.read(str(path))
        logging.info(f"Read config file: {str(path)}")
        self.config = config

    def read_defaults(self, config: ConfigParser) -> None:
        path = importlib.resources.files("chatgpt_conversation_finder.data").joinpath(
            "default_config.ini"
        )
        config.read(str(path))

    def setup_nltk(self) -> None:
        nltk_path = importlib.resources.files(
            "chatgpt_conversation_finder.data"
        ).joinpath("nltk_data")
        nltk.data.path.insert(0, str(nltk_path))
        # os.environ['NLTK_DATA'] = str(nltk_path)  # This doesn't work because nltk is
        #                                          #  already imported at this point
