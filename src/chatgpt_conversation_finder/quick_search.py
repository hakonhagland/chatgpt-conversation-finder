import logging
from typing import Any

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.index_manager import IndexManager


class QuickSearch:
    """Quick search for conversations based on an inverted index. We need quick search
    to provide instant search results/response in the GUI when the user types in the
    search bar. A delay here would make the GUI feel unresponsive.

    Procedure:
    1. Load the conversations JSON file.
    2. Flatten each conversation into a single string.
    3. Sanitize the conversation content for use with the inverted index and word search.
    4. Assume the user usually adds or removes a single character at a time. This means
       we can optimize the search by starting with the previous matched conversations
       and then filtering based on the new character.
    5. If the user types a space, we can assume they are starting a new word and can
       search for that word in the inverted index.
    6. If the input word is only lower case, we will try match it against mixed upper
       and lower case. For example, "foo" will match "Foo", "FOO", and "foo", and so on.
    7. If the input word is upper case or mixed upper and lower case, we will only
       attempt an exact match. So "Foo" will only match "Foo"
    8. If the user wants to match only "foo" in lower-case, he can put it in double quotes.
    9. The inverted word index is a dictionary where the key is a word and the value is
       a set of conversation IDs that contain that word. Since this index contains words,
       it will not match "afoob" with "foo". However, certain non-word characters like
       hyphens, underscores, and dots are will be treated as word separators. So "a-foo-b"
       will match "foo" as a word.
    10. If the user wants to match a substring of a word, they can use a wildcard "*".
    11. As the user types in a word it will match the substring at beginning of the word.
        When the user types a space, it will match the entire word (and not a substring of
        a larger word).
    12. The search results are displayed in the GUI as the user types.
    """

    def __init__(self, config: Config, index_manager: IndexManager) -> None:
        self.config = config
        self.index_manager = index_manager
        self.id_info = self.index_manager.get_conversation_info()
        self.word_index = self.index_manager.get_word_index()
        self.id_alias = self.index_manager.get_inverse_id_map()

    def search_conversations(self, search_term: str) -> list[dict[str, Any]]:
        logging.debug(f"Search term: '{search_term}'")
        # TODO: Handle quoted phrases for exact match
        # First, convert to lowercase for case-insensitive search
        search_term = search_term.lower()
        # Check if the last character in the original search_term is a space
        trailing_space = search_term.endswith(" ")
        # Now strip the trailing spaces to clean up the input for processing
        search_term = search_term.strip()
        tokens = search_term.split()
        logging.debug(f"Searching for tokens: {tokens}")
        matching_conversations = None
        prefix_word = None
        if (not trailing_space) and len(tokens) > 0:
            # The last token is to be considered a prefix word
            prefix_word = tokens.pop()
        if len(tokens) > 0:
            for token in tokens:
                if token in self.word_index:
                    if matching_conversations is None:
                        # IMPORTANT: We need to make a copy here,
                        #    otherwise we will be modifying the original set
                        matching_conversations = self.word_index[token].copy()
                        logging.debug(
                            f"..Number of matching conversations: {len(matching_conversations)}"
                        )
                    else:
                        logging.debug(f"..Intersecting with token: {token}")
                        matching_conversations &= self.word_index[token]
                else:
                    logging.debug(f"..Token not found in index: {token}")
                    matching_conversations = set()
                    break
        if prefix_word:
            logging.debug(f"Searching for prefix word: {prefix_word}")
            matching_conversations = self.match_prefix_word(
                prefix_word, matching_conversations
            )
        elif len(tokens) == 0:
            # If the search term is empty, return all conversations
            matching_conversations = set(self.id_alias.keys())  # type: ignore
        results = []
        logging.debug(
            "Number of matching conversations: "
            f"{len(matching_conversations) if matching_conversations is not None else 0}"
        )
        for conversation_alias in matching_conversations:  # type: ignore
            conversation_id = self.id_alias[int(conversation_alias)]
            conversation_info = self.id_info.get(conversation_id)
            if conversation_info:
                results.append(conversation_info)
        logging.debug(f"Number of results: {len(results)}")
        return results

    def manual_prefix_search(
        self, prefix_word: str, matching_conversations: set[str]
    ) -> set[str]:
        """Perform a manual prefix search for a prefix word.
        :param prefix_word: The prefix word to search for
        :param matching_conversations: The set of matching conversations to filter. This set is a mapping of conversation aliases to conversation IDs aliases.
        """
        prefix_matching_conversations = set()
        conversations = self.index_manager.get_conversations()
        for conversation_alias in matching_conversations:
            conversation_id = self.id_alias[int(conversation_alias)]
            tokens = conversations[conversation_id]
            for token in tokens:
                if token.startswith(prefix_word):
                    prefix_matching_conversations.add(conversation_alias)
                    break
        return prefix_matching_conversations

    def match_prefix_word(
        self, prefix_word: str, matching_conversations: set[str] | None
    ) -> set[str]:
        """Match a prefix word to the set of matching conversations."""
        max_prefix_length = self.index_manager.get_max_prefix_length()
        manual_search = False
        if len(prefix_word) > max_prefix_length:
            manual_prefix_word = prefix_word
            prefix_word = prefix_word[:max_prefix_length]
            manual_search = True
        logging.debug(f"match_prefix_word(): manual_search = {manual_search}")
        prefix_matching_conversations = self.index_manager.match_prefix(prefix_word)
        logging.debug(
            f"match_prefix_word(): Prefix matching conversations: {len(prefix_matching_conversations)}"
        )
        if matching_conversations is None:
            matching_conversations = prefix_matching_conversations
        else:
            matching_conversations &= prefix_matching_conversations
        if manual_search:
            return self.manual_prefix_search(manual_prefix_word, matching_conversations)
        return matching_conversations
