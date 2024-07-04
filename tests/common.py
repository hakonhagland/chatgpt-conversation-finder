from typing import Any, Protocol

from pathlib import Path

# NOTE: These type aliases cannot start with "Test" because then pytest will
#       believe that they are test classes, see https://stackoverflow.com/q/76689604/2173773

QtBot = Any  # Missing type hints here


class PrepareConfigDir(Protocol):  # pragma: no cover
    def __call__(self, add_config_ini: bool, downloads_dir: Path | None = None) -> Path:
        pass
