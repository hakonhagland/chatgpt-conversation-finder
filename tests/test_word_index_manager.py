import logging
import re

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.index_manager import IndexManager
from chatgpt_conversation_finder.word_index_manager import WordIndexManager


class TestGeneral:
    def test_bad_init_type(
        self,
        mocker: MockerFixture,
        config_oject: Config,
    ) -> None:
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        with pytest.raises(ValueError) as excinfo:
            WordIndexManager(
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
        caplog: LogCaptureFixture,
    ) -> None:
        caplog.set_level(logging.INFO)
        config = config_oject
        index_manager = IndexManager(config, init_type="create")
        word_index_manager = WordIndexManager(
            config,
            index_manager.get_conversations(),
            index_manager.get_id_map(),
            init_type="create",
        )
        word_index_manager.load_index()
        assert caplog.records[-1].msg.startswith("Index loaded from")
