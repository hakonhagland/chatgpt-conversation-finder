import re

import pytest
from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.index_manager import IndexManager


class TestGeneral:
    def test_bad_init_type(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        with pytest.raises(ValueError) as excinfo:
            IndexManager(config, init_type="unknown")
        assert re.search(r"Invalid init_type: unknown", str(excinfo))

    def test_get_prefix_index(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        index = index_manager.get_prefix_index()
        assert "un" in index
        assert index["un"] == {"0", "1"}

    def test_load_conversations(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        conversations = index_manager.load_conversations()
        conversation_id = "23670fbe-76a9-46d1-8c0a-52d48fc29d7a"
        assert conversation_id in conversations
        assert "karma" in conversations[conversation_id]

    def test_load_id_map(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        id_map = index_manager.load_id_map()
        conversation_id = "23670fbe-76a9-46d1-8c0a-52d48fc29d7a"
        assert conversation_id in id_map
        assert id_map[conversation_id] == 0
