from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.helpers import Helpers
from chatgpt_conversation_finder.sanitizer import Sanitizer


class TestGeneral:
    def test_remove_leading_dots(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        sanitizer = Sanitizer()
        tokens = ["foo", "..hello"]
        sanitizer.remove_leading_char(tokens, char=".")
        assert len(tokens) == 2
        assert tokens[0] == "foo"
        assert tokens[1] == ".hello"

    def test_remove_surrounding_quotes(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        sanitizer = Sanitizer()
        tokens = ["foo", '"hello"', "'world'", "'bar", '"baz', 'qux"']
        sanitizer.remove_surrounding_quotes(tokens)
        assert len(tokens) == 6
        assert tokens[0] == "foo"
        assert tokens[1] == "hello"
        assert tokens[2] == "world"
        assert tokens[3] == "bar"
        assert tokens[4] == "baz"
        assert tokens[5] == "qux"

    def test_sanitize_exact_phrase(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        json_path = config.get_conversations_json_path()
        raw_conversations = Helpers.load_json(str(json_path))
        conversations = Helpers.flatten_conversations(raw_conversations)
        sanitizer = Sanitizer()
        result = sanitizer.sanitize_conversations_exact_phrase(conversations)
        conversation_id = "23670fbe-76a9-46d1-8c0a-52d48fc29d7a"
        assert "Hinduism" in result[conversation_id]
