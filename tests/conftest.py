# import logging
import shutil
from pathlib import Path
from typing import Callable

# import typing
import pytest
from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from .common import PrepareConfigDir

PytestDataDict = dict[str, str]


@pytest.fixture(scope="session")
def test_file_path() -> Path:
    return Path(__file__).parent / "files"


@pytest.fixture(scope="session")
def test_data() -> PytestDataDict:
    return {
        "chats_zip_fn": "chats.zip",
        "config_dir": "config",
        "data_dir": "data",
        "downloads_dir": "Downloads",
        "invalid_conversations_json_fn": "conversations_invalid.json",
    }


@pytest.fixture()
def chats_zip_path(test_file_path: Path, test_data: PytestDataDict) -> Path:
    chats_zip_fn = test_file_path / test_data["data_dir"] / test_data["chats_zip_fn"]
    return chats_zip_fn


@pytest.fixture()
def config_oject(
    data_dir_path: Path,
    prepare_config_dir: PrepareConfigDir,
    mocker: MockerFixture,
) -> Config:
    data_dir = data_dir_path
    config_dir = prepare_config_dir(add_config_ini=True)
    mocker.patch(
        "platformdirs.user_config_dir",
        return_value=config_dir,
    )
    data_dir = data_dir_path
    mocker.patch(
        "platformdirs.user_data_dir",
        return_value=data_dir,
    )
    return Config()


@pytest.fixture()
def config_dir_path(
    prepare_config_dir: PrepareConfigDir,
) -> Path:
    return prepare_config_dir(add_config_ini=False)


# @pytest.fixture()
# def data_dir_path(
#    prepare_data_dir: Callable[[bool], Path], test_data: PytestDataDict
# ) -> Path:
#    return prepare_data_dir(True)

# @pytest.fixture()
# def conversations_json_path(
#    test_file_path: Path, test_data: PytestDataDict
# ) -> Path:
#    conversations_fn = test_file_path / test_data["data_dir"] / Config.conversation_json_fn
#    return conversations_fn


@pytest.fixture()
def data_dir_path(
    prepare_data_dir: Callable[[bool], Path], test_data: PytestDataDict
) -> Path:
    return prepare_data_dir(True)


@pytest.fixture()
def downloads_dir(
    tmp_path: Path,
    test_data: PytestDataDict,
) -> Path:
    dir_ = tmp_path / test_data["downloads_dir"]
    dir_.mkdir()
    return dir_


@pytest.fixture()
def prepare_config_dir(
    tmp_path: Path, test_file_path: Path, test_data: PytestDataDict
) -> PrepareConfigDir:
    def _prepare_config_dir(
        add_config_ini: bool, downloads_dir: Path | None = None
    ) -> Path:
        config_dir = tmp_path / test_data["config_dir"]
        config_dir.mkdir()
        config_dirlock_fn = test_file_path / test_data["config_dir"] / Config.dirlock_fn
        shutil.copy(config_dirlock_fn, config_dir)
        if add_config_ini:
            config_ini_fn = test_file_path / test_data["config_dir"] / Config.config_fn
            save_fn = config_dir / config_ini_fn.name
            if downloads_dir is not None:
                with open(config_ini_fn, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("%%DOWNLOADS_DIR%%", str(downloads_dir))
                with open(save_fn, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                shutil.copy(config_ini_fn, save_fn)
        return config_dir

    return _prepare_config_dir


@pytest.fixture()
def prepare_data_dir(
    tmp_path: Path, test_file_path: Path, test_data: PytestDataDict
) -> Callable[[bool], Path]:
    def _prepare_data_dir(valid: bool) -> Path:
        data_dir = tmp_path / test_data["data_dir"]
        data_dir.mkdir()
        data_dirlock_fn = test_file_path / test_data["data_dir"] / Config.dirlock_fn
        shutil.copy(data_dirlock_fn, data_dir)
        conversations_fn = (
            test_file_path / test_data["data_dir"] / Config.conversation_json_fn
        )
        if valid:
            shutil.copy(conversations_fn, data_dir)
        else:
            conversations_invalid_fn = (
                test_file_path
                / test_data["data_dir"]
                / test_data["invalid_conversations_json_fn"]
            )
            shutil.copy(
                conversations_invalid_fn, data_dir / Config.conversation_json_fn
            )
        return data_dir

    return _prepare_data_dir
