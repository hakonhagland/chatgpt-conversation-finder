import re
from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.exceptions import ConfigException
from .common import PrepareConfigDir


class TestDir:
    def test_configdir_is_file(
        self,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        data_dir = data_dir_path
        config_dir = config_dir_path
        config_dir = config_dir / "file"  # make it a file
        config_dir.touch()
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        with pytest.raises(ConfigException) as excinfo:
            Config()
        assert re.search(r"Config directory \S+ is a file.", str(excinfo))

    def test_configdir_nonexistant(
        self,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        data_dir = data_dir_path
        config_dir = config_dir_path
        config_dir = config_dir / "nonexistant"
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        Config()
        assert True

    @pytest.mark.parametrize(
        "bad_content, is_directory, missing",
        [
            [False, False, False],
            [True, False, False],
            [False, True, False],
            [False, False, True],
        ],
    )
    def test_configdir_lockfile(
        self,
        bad_content: bool,
        is_directory: bool,
        missing: bool,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        data_dir = data_dir_path
        config_dir = config_dir_path
        lock_fn = config_dir / Config.dirlock_fn
        if bad_content:
            with open(str(lock_fn), "w", encoding="utf_8") as fp:
                fp.write("xyz")
        if is_directory:
            lock_fn.unlink()
            lock_fn.mkdir()
        if missing:
            lock_fn.unlink()
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        if bad_content or is_directory or missing:
            with pytest.raises(ConfigException) as excinfo:
                Config()
        else:
            Config()
        if bad_content:
            assert re.search(r"Unexpected: Config dir lock file:", str(excinfo))
        elif is_directory:
            assert re.search(
                r"Unexpected: Config dir lock file: is a directory.", str(excinfo)
            )
        elif missing:
            assert re.search(
                r"Unexpected: Config dir lock file: missing.", str(excinfo)
            )
        else:
            assert True

    @pytest.mark.parametrize(
        "bad_content, is_directory, missing",
        [
            [False, False, False],
            [True, False, False],
            [False, True, False],
            [False, False, True],
        ],
    )
    def test_datadir_lockfile(
        self,
        bad_content: bool,
        is_directory: bool,
        missing: bool,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        data_dir = data_dir_path
        config_dir = config_dir_path
        lock_fn = data_dir / Config.dirlock_fn
        if bad_content:
            with open(str(lock_fn), "w", encoding="utf_8") as fp:
                fp.write("xyz")
        if is_directory:
            lock_fn.unlink()
            lock_fn.mkdir()
        if missing:
            lock_fn.unlink()
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        if bad_content or is_directory or missing:
            with pytest.raises(ConfigException) as excinfo:
                Config()
        else:
            Config()
        if bad_content:
            assert re.search(r"Unexpected: Data dir lock file:", str(excinfo))
        elif is_directory:
            assert re.search(
                r"Unexpected: Data dir lock file: is a directory.", str(excinfo)
            )
        elif missing:
            assert re.search(r"Unexpected: Data dir lock file: missing.", str(excinfo))
        else:
            assert True

    def test_datadir_is_file(
        self,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        data_dir = data_dir_path
        config_dir = config_dir_path
        data_dir = data_dir / "file"  # make it a file
        data_dir.touch()
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        with pytest.raises(ConfigException) as excinfo:
            Config()
        assert re.search(r"Data directory \S+ is a file.", str(excinfo))

    def test_datadir_nonexistant(
        self,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        data_dir = data_dir_path
        config_dir = config_dir_path
        data_dir = data_dir / "nonexistant"
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        Config()
        assert True


class TestConfigFile:
    def test_config_file_not_file(
        self,
        mocker: MockerFixture,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
    ) -> None:
        data_dir = data_dir_path
        config_dir = prepare_config_dir(add_config_ini=False)
        config_file = config_dir / Config.config_fn
        config_file.mkdir()
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        with pytest.raises(ConfigException) as excinfo:
            Config()
        assert re.search(
            r"Config filename \S+ exists, but filetype is not file", str(excinfo)
        )
