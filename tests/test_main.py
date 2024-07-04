import logging
from pathlib import Path
from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture
from PyQt6.QtWidgets import QApplication, QFileDialog
from click.testing import CliRunner
from pytest_mock.plugin import MockerFixture

import chatgpt_conversation_finder.main as main
from .common import QtBot


class TestGuiCmd:
    def test_help(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        result = runner.invoke(main.gui, ["--help"])
        assert result.stdout.startswith("Usage: gui [OPTIONS]")

    def test_invoke(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        config_dir_path: Path,
        data_dir_path: Path,
        qtbot: QtBot,
        qapp: QApplication,
    ) -> None:
        caplog.set_level(logging.INFO)
        data_dir = data_dir_path
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        mocker.patch(
            "chatgpt_conversation_finder.main.QApplication",
            return_value=qapp,
        )
        mock = mocker.MagicMock()
        mocker.patch(
            "chatgpt_conversation_finder.main.ChatGPTFinderGUI", return_value=mock
        )
        # mock.show = mocker.MagicMock()
        mocker.patch("sys.exit", return_value=None)
        runner = CliRunner()
        args = ["gui"]
        with qtbot.waitCallback() as callback:
            mocker.patch.object(qapp, "exec", callback)
            result = runner.invoke(main.main, args)
        assert result.exit_code == 0


@pytest.mark.parametrize("verbose", [True, False])
class TestMainCmd:
    def test_help(
        self,
        verbose: bool,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        args = ["gui", "--help"]
        if verbose:
            args.insert(0, "-v")
        result = runner.invoke(main.main, args)
        assert result.stdout.startswith("Usage: main gui [OPTIONS]")


class TestPrettyPrintCmd:
    def test_invoke(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        data_dir = data_dir_path
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        args = ["pretty-print"]
        result = runner.invoke(main.main, args)
        assert result.exit_code == 0
        assert result.stdout.startswith(
            """[\n    {\n        "title": "Is Hinduism a religion?","""
        )


class TestSearchTermCmd:
    def test_help(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        # Invoke the subcommand search_term
        result = runner.invoke(main.search_term, ["--help"])
        assert result.stdout.startswith("Usage: search-term [OPTIONS] SEARCH_TERM")

    @pytest.mark.parametrize("term", ["hinduism", "moksha"])
    def test_invoke(
        self,
        term: str,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
        tmp_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        args = ["search-term", term]
        with runner.isolated_filesystem(temp_dir=tmp_path):  # type: ignore
            result = runner.invoke(main.main, args)
        assert result.stdout.startswith("Title: Is Hinduism a religion?")


class TestUpdateData:
    def test_invoke(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
        tmp_path: Path,
        chats_zip_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        args = ["update-data", str(chats_zip_path)]
        with runner.isolated_filesystem(temp_dir=tmp_path):  # type: ignore
            result = runner.invoke(main.main, args)
        assert result.exit_code == 0
        assert caplog.records[-1].msg.startswith("Search index created")

    def test_invoke_no_filename(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        data_dir_path: Path,
        config_dir_path: Path,
        tmp_path: Path,
        chats_zip_path: Path,
        qapp: QApplication,
    ) -> None:
        caplog.set_level(logging.INFO)
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        mocker.patch(
            "chatgpt_conversation_finder.main.QApplication",
            return_value=qapp,
        )

        def mock_exec(dialog: QFileDialog) -> QFileDialog.DialogCode:
            dialog.selectedFiles = lambda: [chats_zip_path]  # type: ignore
            return QFileDialog.DialogCode.Accepted

        monkeypatch.setattr(QFileDialog, "exec", mock_exec)
        runner = CliRunner()
        args = ["update-data"]
        with runner.isolated_filesystem(temp_dir=tmp_path):  # type: ignore
            result = runner.invoke(main.main, args)
        assert result.exit_code == 0
        assert caplog.records[-1].msg.startswith("Search index created")


class TestCreateSearchIndex:
    def test_invoke(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
        config_dir_path: Path,
        tmp_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = data_dir_path
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        args = ["create-search-index"]
        with runner.isolated_filesystem(temp_dir=tmp_path):  # type: ignore
            result = runner.invoke(main.main, args)
        assert result.exit_code == 0
        assert caplog.records[-1].msg.startswith("Search index created")


class TestValidateConversations:
    @pytest.mark.parametrize("valid", [True, False])
    def test_invoke(
        self,
        valid: bool,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        prepare_data_dir: Callable[[bool], Path],
        config_dir_path: Path,
        tmp_path: Path,
    ) -> None:
        caplog.set_level(logging.INFO)
        config_dir = config_dir_path
        mocker.patch(
            "platformdirs.user_config_dir",
            return_value=config_dir,
        )
        data_dir = prepare_data_dir(valid)
        mocker.patch(
            "platformdirs.user_data_dir",
            return_value=data_dir,
        )
        runner = CliRunner()
        args = ["validate-conversations"]
        with runner.isolated_filesystem(temp_dir=tmp_path):  # type: ignore
            result = runner.invoke(main.main, args)
        assert result.exit_code == 0
        if valid:
            assert caplog.records[-1].msg.startswith("All conversations are valid")
        else:
            assert caplog.records[-1].msg.startswith("Some conversations are invalid")
