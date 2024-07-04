import json
import logging

from chatgpt_conversation_finder.config import Config


class PrefixIndexManager:
    """Manages the prefix search index for the conversations.

    Prefixes are needed when the user starts typing a search term and we want to
    show the results as they type. The user is not finished typing the complete word
    or search term yet, so we need to show partial results based on the prefixes.

    Once, the user types a space, we can assume they have completed a word and we can
    use the word index to show the final results.

    IDEA: We build one index based on the sanitized lower-case words and another index
    based on the original case-sensitive words.

    IDEA: We only need, say the first 3 characters of each word, to build the prefix index.
    Once, the user type the 4th
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
        self.max_prefix_length = config.get_max_prefix_length()
        if init_type == "load":
            self.prefix_index = self.load_prefix_index()
        elif init_type == "create":
            self.prefix_index = self.create_search_index()
        else:
            raise ValueError(f"Invalid init_type: {init_type}")

    def create_search_index(self) -> dict[str, set[str]]:
        """Generates a prefix search index for the self.conversations and saves
        it to the search index file. The prefix index is a dictionary where the
        keys are prefixes and the values are sets of conversation ids.

        The maximum length of the prefix is determined by self.max_prefix_length.
        A longer length will result in a larger index but faster search times.
        """
        prefix_index: dict[str, set[str]] = {}
        for id, content in self.conversations.items():
            for token in content:
                for j in range(1, self.max_prefix_length + 1):
                    if len(token) < j:
                        continue
                    prefix = token[:j]
                    if prefix not in prefix_index:
                        prefix_index[prefix] = set()
                    prefix_index[prefix].add(str(self.id_map[id]))
        self.save_prefix_index(prefix_index)
        return prefix_index

    def get_index(self) -> dict[str, set[str]]:
        return self.prefix_index

    def load_prefix_index(self) -> dict[str, set[str]]:
        """Load prefix index from disk or generate it if it does not exist"""
        prefix_index_path = self.config.get_prefix_index_path()
        try:
            with open(prefix_index_path, "r", encoding="utf-8") as f:
                prefix_index = json.load(f)
                prefix_index = {k: set(v) for k, v in prefix_index.items()}
            logging.info(f"Prefix index loaded from {prefix_index_path}")
        except FileNotFoundError:
            logging.warning(
                f"Prefix index file not found at {prefix_index_path}. Creating a new prefix index."
            )
            prefix_index = self.create_search_index()
        return prefix_index  # type: ignore

    def match_prefix(self, prefix: str) -> set[str]:
        """Match a prefix to the set of matching conversations."""
        return self.prefix_index.get(prefix, set())

    def save_prefix_index(self, prefix_index: dict[str, set[str]]) -> None:
        prefix_index_path = self.config.get_prefix_index_path()
        # We need to convert the prefix index to a dictionary with lists
        # because json does not support sets
        prefix_index_converted = {k: list(v) for k, v in prefix_index.items()}
        with open(prefix_index_path, "w", encoding="utf-8") as f:
            json.dump(prefix_index_converted, f, indent=4, sort_keys=True)
        logging.info(f"Prefix index saved to {prefix_index_path}")
