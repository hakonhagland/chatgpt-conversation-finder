import json
import logging
from typing import Any

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.helpers import Helpers
from chatgpt_conversation_finder.prefix_index_manager import PrefixIndexManager
from chatgpt_conversation_finder.sanitizer import Sanitizer
from chatgpt_conversation_finder.word_index_manager import WordIndexManager


class IndexManager:
    def __init__(self, config: Config, init_type: str = "load") -> None:
        """
        :param config: Config object
        :param init_type: "load" or "create": Whether to load the index from disk or create a new one
        """
        self.config = config
        self.json_path = self.config.get_conversations_json_path()
        self.raw_conversations = Helpers.load_json(str(self.json_path))
        self.conversation_info = Helpers.get_conversations_info(self.raw_conversations)
        if init_type == "load":
            self.conversations = self.load_conversations()
            self.id_map = self.load_id_map()
        elif init_type == "create":
            self.conversations = self.sanitize_conversations()
            self.id_map = self.generate_id_map()
        else:
            raise ValueError(f"Invalid init_type: {init_type}")
        self.word_index_manager = WordIndexManager(
            self.config, self.conversations, self.id_map, init_type
        )
        self.prefix_index_manager = PrefixIndexManager(
            self.config, self.conversations, self.id_map, init_type
        )

    def get_conversations(self) -> dict[str, set[str]]:
        return self.conversations

    def get_conversation_info(self) -> dict[str, dict[str, Any]]:
        return self.conversation_info

    def get_id_map(self) -> dict[str, int]:
        return self.id_map

    def get_max_prefix_length(self) -> int:
        return self.config.get_max_prefix_length()

    def get_prefix_index(self) -> dict[str, set[str]]:
        return self.prefix_index_manager.get_index()

    def get_prefix_index_manager(self) -> PrefixIndexManager:
        return self.prefix_index_manager

    def get_word_index(self) -> dict[str, set[str]]:
        return self.word_index_manager.get_index()

    def get_inverse_id_map(self) -> dict[int, str]:
        return {v: k for k, v in self.id_map.items()}

    def generate_id_map(self) -> dict[str, int]:
        # Convert ids on the form a1612574-7ed9-461b-9191-8b891f63686d to integers
        # TODO: To save even more space, we could convert the integers to base64
        id_map = {}
        for i, id in enumerate(self.conversations.keys()):
            id_map[id] = i
        self.save_id_map(id_map)
        return id_map

    def load_conversations(self) -> dict[str, set[str]]:
        self.json_path = self.config.get_sanitized_conversations_path()
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                conversations = json.load(f)
            # We need to convert the lists back to sets
            conversations = {k: set(v) for k, v in conversations.items()}
            logging.info(f"Conversations loaded from {self.json_path}")
        except FileNotFoundError:
            logging.warning(
                f"Sanitized conversations file not found at {self.json_path}."
                f"Creating a new file."
            )
            conversations = self.sanitize_conversations()
        return conversations  # type: ignore

    def load_id_map(self) -> dict[str, int]:
        """Load id map from disk or generate it if it does not exist"""
        id_map_path = self.config.get_idmap_path()
        try:
            with open(id_map_path, "r", encoding="utf-8") as f:
                id_map = json.load(f)
            logging.info(f"ID map loaded from {id_map_path}")
        except FileNotFoundError:
            logging.warning(
                f"ID map file not found at {id_map_path}. Creating a new ID map."
            )
            id_map = self.generate_id_map()
        return id_map  # type: ignore

    def match_prefix(self, prefix: str) -> set[str]:
        return self.prefix_index_manager.match_prefix(prefix)

    def sanitize_conversations(self) -> dict[str, set[str]]:
        flatten_conversations = Helpers.flatten_conversations(self.raw_conversations)
        sanitizer = Sanitizer()
        conversations = sanitizer.sanitize_conversations_lower_case(
            flatten_conversations
        )
        self.save_conversations(conversations)
        return conversations

    def save_conversations(self, conversations: dict[str, set[str]]) -> None:
        conversations_path = self.config.get_sanitized_conversations_path()
        # We need to convert the sets to lists to be able to save them to disk
        conversations_converted = {k: list(v) for k, v in conversations.items()}
        with open(conversations_path, "w", encoding="utf-8") as f:
            json.dump(conversations_converted, f, indent=4, sort_keys=True)
        logging.info(f"Sanitized conversations saved to {conversations_path}")

    def save_id_map(self, id_map: dict[str, int]) -> None:
        # TODO: Convert to base64 for efficiency
        id_map_path = self.config.get_idmap_path()
        with open(id_map_path, "w", encoding="utf-8") as f:
            json.dump(id_map, f, indent=4, sort_keys=True)
        logging.info(f"ID map saved to {id_map_path}")
