import re

from chatgpt_conversation_finder.constants import RegexFlags


class TestRegexFlags:
    def test_from_str(self) -> None:
        regex_flags = RegexFlags.from_str("i")
        assert regex_flags.value == RegexFlags.IGNORECASE.value

    def test_to_re_flags(self) -> None:
        regex_flags = RegexFlags.from_str("i")
        flags = regex_flags.to_re_flags()
        assert flags == re.IGNORECASE
