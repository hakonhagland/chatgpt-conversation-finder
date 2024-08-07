import pytest
from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.constants import RegexFlags
from chatgpt_conversation_finder.grep_handler import GrepConversationsHandler


class TestGeneral:
    def test_no_matches(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
        config_oject: Config,
    ) -> None:
        config = config_oject
        regex_flags = RegexFlags.from_str("")
        grep_handler = GrepConversationsHandler(config)
        grep_handler.grep("xyzxyz_not_existing_pattern", regex_flags)
        captured = capsys.readouterr()
        assert captured.out == "\x1b[34mNo matches found.\x1b[39m\n"
