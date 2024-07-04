from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.index_manager import IndexManager
from chatgpt_conversation_finder.quick_search import QuickSearch


class TestGeneral:
    def test_search_complete_word(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        quick_search = QuickSearch(config, index_manager)
        result = quick_search.search_conversations("religion lar")
        assert len(result) == 3

    def test_search_complete_words(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        quick_search = QuickSearch(config, index_manager)
        result = quick_search.search_conversations("religion world lar")
        assert len(result) == 3

    def test_search_unknown_word(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        quick_search = QuickSearch(config, index_manager)
        result = quick_search.search_conversations("religion lion lar")
        assert len(result) == 0
