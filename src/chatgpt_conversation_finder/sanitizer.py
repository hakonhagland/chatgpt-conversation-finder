import re

import nltk


class Sanitizer:
    """Se documentation in quick_search.py for more information on the methods in this class."""

    def __init__(self) -> None:
        self.stop_words = nltk.corpus.stopwords.words("english")

    def remove_empty_tokens(self, tokens: list[str]) -> None:
        # Remove empty tokens
        tokens[:] = [token for token in tokens if token]

    def remove_leading_char(self, tokens: list[str], char: str) -> None:
        """Remove repeated leading characters from tokens. For example,
        dots at the beginning of the token should not have to be entered as part
        of the search term. They are usually not significant for the search term."""
        for i, token in enumerate(tokens):
            # Replace two or more leading chars with a single char
            while token.startswith(char * 2):
                token = char + token[2:]
            tokens[i] = token

    def remove_surrounding_quotes(self, tokens: list[str]) -> None:
        """Remove surrounding single or double quotes from tokens. Surrounding quotes
        are not significant for the search term. They are usually not entered as part of
        the search term."""
        for i, token in enumerate(tokens):
            # Strip surrounding single or double quotes in pairs
            # Allow for trailing apostrophes for possessives
            while True:
                if token.startswith('"') and token.endswith('"'):
                    token = token[1:-1]
                elif token.startswith("'") and token.endswith("'"):
                    token = token[1:-1]
                elif token.startswith("'"):
                    token = token[1:]
                elif token.startswith('"'):
                    token = token[1:]
                elif token.endswith('"'):
                    token = token[:-1]
                else:
                    break
            tokens[i] = token

    def remove_tokens_with_single_characters(
        self, tokens: list[str], character_set_str: str
    ) -> None:
        # Remove tokens with characters repeated from the character_set
        # For example, if character_set = "'-" the following tokens will be removed:
        # "'", "''", "'''", ..., "-", "--", "---", ...
        # Convert the character set to a set for efficient membership testing
        character_set = set(character_set_str)
        # Use a list comprehension to filter tokens
        # Keep a token if it is not entirely made up of characters in character_set
        # Or if it's not just a repeated character from character_set
        tokens[:] = [
            token
            for token in tokens
            if not (
                # Check if the token is made up of characters only from character_set
                all(char in character_set for char in token)
                and
                # Check if the token is a repeated sequence of a character from character_set
                (len(set(token)) == 1)
            )
        ]

    def remove_trailing_char(self, tokens: list[str], char: str) -> None:
        """Remove trailing characters from tokens. For example, dots and equal signs
        at the end of the token should not have to be entered as part of the search term.
        They are usually not significant for the search term."""
        for i, token in enumerate(tokens):
            # Remove trailing chars
            while token.endswith(char):
                token = token[:-1]
            tokens[i] = token

    def sanitize_conversations(
        self, conversations: dict[str, str], lower_case: bool, create_set: bool
    ) -> dict[str, set[str]]:
        # Load English stopwords
        conversations_sanitized = {}
        for id, content in conversations.items():
            # Keep only alphanumeric characters, apostrophes, hyphens,
            # dots, equal signs, and underscores
            content = re.sub(r"[^\w\'\-_.=]+", " ", content)
            # Tokenize the text into words
            tokens = content.split()
            tokens = [token.lower() for token in tokens] if lower_case else tokens
            self.remove_trailing_char(tokens, ".")
            self.remove_trailing_char(tokens, "=")
            # Remove stop words
            tokens = [token for token in tokens if token.lower() not in self.stop_words]
            self.remove_surrounding_quotes(tokens)
            self.remove_leading_char(tokens, ".")
            self.remove_tokens_with_single_characters(tokens, "'-=._\"")
            self.remove_empty_tokens(tokens)
            # self.remove_long_tokens(tokens)
            if create_set:
                self.split_tokens_at_non_word_chars(tokens)
                conversations_sanitized[id] = set(tokens)
            else:
                conversations_sanitized[id] = tokens  # type: ignore
        return conversations_sanitized

    def sanitize_conversations_lower_case(
        self, conversations: dict[str, str]
    ) -> dict[str, set[str]]:
        return self.sanitize_conversations(
            conversations, lower_case=True, create_set=True
        )

    def sanitize_conversations_exact_phrase(
        self, conversations: dict[str, str]
    ) -> dict[str, set[str]]:
        return self.sanitize_conversations(
            conversations, lower_case=False, create_set=False
        )

    def split_tokens_at_non_word_chars(self, tokens: list[str]) -> None:
        # Split tokens at non-word characters, but also keep original token
        # For example, "foo-bar" will be split into ["foo", "bar"]
        new_tokens = []
        for token in tokens:
            # Split token at non-word characters
            split_tokens = re.split(r"\W", token)
            # Add the split tokens to the new tokens list
            new_tokens.extend([t for t in split_tokens if t])
        # Update the original tokens list
        tokens[:] = new_tokens
