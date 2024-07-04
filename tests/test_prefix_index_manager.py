import re

import pytest
from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.index_manager import IndexManager
from chatgpt_conversation_finder.prefix_index_manager import PrefixIndexManager


class TestGeneral:
    def test_bad_init_type(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        with pytest.raises(ValueError) as excinfo:
            PrefixIndexManager(
                config,
                index_manager.get_conversations(),
                index_manager.get_id_map(),
                init_type="unknown",
            )
        assert re.search(r"Invalid init_type: unknown", str(excinfo))

    def test_load_index(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        prefix_index_manager = index_manager.get_prefix_index_manager()
        index = prefix_index_manager.load_prefix_index()
        assert "un" in index
        assert index["un"] == {"0", "1"}
