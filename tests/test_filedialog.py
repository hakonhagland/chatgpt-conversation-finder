from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture
from PyQt6.QtWidgets import QApplication, QFileDialog

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.file_dialog import FileDialog
from .common import PrepareConfigDir


class TestDir:
    def test_dir_does_not_exist(
        self,
        # caplog: LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
        qapp: QApplication,
        tmp_path: Path,
    ) -> None:
        data_dir = data_dir_path
        downloads_dir = tmp_path / "Downloads"
        config_dir = prepare_config_dir(
            add_config_ini=True, downloads_dir=downloads_dir
        )
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        config = Config()
        filename = FileDialog(qapp, config).select_zip_file()
        assert filename is None
        assert (
            f"The specified folder {downloads_dir} does not exist"
            in capsys.readouterr().out
        )

    def test_dir_no_files(
        self,
        # caplog: LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
        downloads_dir: Path,
        qapp: QApplication,
    ) -> None:
        data_dir = data_dir_path
        config_dir = prepare_config_dir(
            add_config_ini=True, downloads_dir=downloads_dir
        )
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        config = Config()
        filename = FileDialog(qapp, config).select_zip_file()
        assert filename is None
        assert (
            f"No zip files found in folder {downloads_dir}" in capsys.readouterr().out
        )

    def test_dialog_not_accepted(
        self,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
        downloads_dir: Path,
        qapp: QApplication,
    ) -> None:
        data_dir = data_dir_path
        zip_file = downloads_dir / "file.zip"
        zip_file.touch()
        config_dir = prepare_config_dir(
            add_config_ini=True, downloads_dir=downloads_dir
        )
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )

        def mock_exec(dialog: QFileDialog) -> QFileDialog.DialogCode:
            dialog.selectedFiles = lambda: ["non_existent_file.zip"]  # type: ignore
            return QFileDialog.DialogCode.Rejected

        monkeypatch.setattr(QFileDialog, "exec", mock_exec)
        config = Config()
        filename = FileDialog(qapp, config).select_zip_file()
        assert filename is None
        assert "Cancelled file selection" in capsys.readouterr().out

    def test_dialog_accepted(
        self,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
        downloads_dir: Path,
        qapp: QApplication,
    ) -> None:
        data_dir = data_dir_path
        zip_filename = "file.zip"
        zip_file = downloads_dir / zip_filename
        zip_file.touch()
        config_dir = prepare_config_dir(
            add_config_ini=True, downloads_dir=downloads_dir
        )
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )

        def mock_exec(dialog: QFileDialog) -> QFileDialog.DialogCode:
            dialog.selectedFiles = lambda: [zip_filename]  # type: ignore
            return QFileDialog.DialogCode.Accepted

        monkeypatch.setattr(QFileDialog, "exec", mock_exec)
        config = Config()
        filename = FileDialog(qapp, config).select_zip_file()
        assert filename is not None
        assert Path(filename).name == zip_filename
