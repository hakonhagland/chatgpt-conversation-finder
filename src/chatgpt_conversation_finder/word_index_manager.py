# import base64
import json
import logging

from chatgpt_conversation_finder.config import Config


class WordIndexManager:
    """Manage the search index for the conversations and the id map.
    The search index is a dictionary where the keys are tokens and the values are
    sets of conversation ids. The id map is a dictionary where the keys are conversation ids
    and the values are integers. The id map is used to save space in the search index.
    """

    def __init__(
        self,
        config: Config,
        conversations: dict[str, set[str]],
        id_map: dict[str, int],
        init_type: str = "load",  # "load" or "create"
    ) -> None:
        """
        :param config: Config object
        :param conversations: A dictionary where the keys are conversation ids and the values are sets of tokens
        :param id_map: A dictionary where the keys are conversation ids and the values are integers
        :param init_type: "load" or "create": Whether to load the index from disk or create a new one
        """
        self.config = config
        self.conversations = conversations
        self.id_map = id_map
        if init_type == "load":
            self.load_index()
        elif init_type == "create":
            self.create_search_index(conversations, id_map)
        else:
            raise ValueError(f"Invalid init_type: {init_type}")

    def create_search_index(
        self, conversations: dict[str, set[str]], id_map: dict[str, int]
    ) -> None:
        """Generates a search index for the conversations and saves
        it to the search index file"""
        index: dict[str, set[str]] = {}
        for id, content in conversations.items():
            for token in content:
                if token not in index:
                    index[token] = set()
                # Add the id of the conversation to the token's set
                index[token].add(str(id_map[id]))
        self.index = index
        self.conversations = conversations
        self.id_map = id_map
        # We only need to generate the search index each time the conversations change
        # That is, after the cli command "chatgpt-conversation-finder update-data" has been run
        # So we save the index here, such that we don't have to generate it again
        self.save_index()

    def get_index(self) -> dict[str, set[str]]:
        logging.debug("WordIndexManager.get_index()...")
        return self.index

    def load_index(self) -> None:
        """Load index from disk or generate it if it does not exist"""
        index_path = self.config.get_word_index_path()
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
                self.index = {k: set(v) for k, v in index.items()}
            logging.info(f"Index loaded from {index_path}")
        except FileNotFoundError:
            logging.warning(
                f"Index file not found at {index_path}. Creating a new index."
            )
            self.create_search_index(self.conversations, self.id_map)

    def save_index(self) -> None:
        # Convert sets to lists for JSON compatibility
        dict_for_json = {k: list(v) for k, v in self.index.items()}
        # Save the index to a file
        index_path = self.config.get_word_index_path()
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(dict_for_json, f, indent=4, sort_keys=True)
        logging.info(f"Index saved to {index_path}")
