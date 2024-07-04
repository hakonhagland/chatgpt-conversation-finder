import re

from chatgpt_conversation_finder.exceptions import (
    ConfigException,
)


def test_config_exception() -> None:
    try:
        raise ConfigException("Testing")
    except ConfigException as exc:
        msg = str(exc)
        assert re.search(r"Testing", msg)
