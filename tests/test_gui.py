from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.gui import ChatGPTFinderGUI
from .common import PrepareConfigDir, QtBot


class TestDir:
    def test_line_edit(
        self,
        # caplog: LogCaptureFixture,
        # capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
        qapp: QApplication,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        data_dir = data_dir_path
        config_dir = prepare_config_dir(add_config_ini=False)
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
        gui = ChatGPTFinderGUI(config)  # Adjust the path as necessary
        qtbot.addWidget(gui)
        gui.show()
        edit = gui.lineEdit
        edit.setText("religion")
        with qtbot.waitSignal(edit.returnPressed, timeout=500):
            qtbot.keyPress(edit, Qt.Key.Key_Enter)
        assert True

    @pytest.mark.parametrize("open_fail", [False, True])
    def test_list_widget(
        self,
        open_fail: bool,
        # caplog: LogCaptureFixture,
        # capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        data_dir_path: Path,
        prepare_config_dir: PrepareConfigDir,
        qapp: QApplication,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        data_dir = data_dir_path
        config_dir = prepare_config_dir(add_config_ini=False)
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
        gui = ChatGPTFinderGUI(config)  # Adjust the path as necessary
        qtbot.addWidget(gui)
        gui.show()
        edit = gui.lineEdit
        edit.setText("religion")
        list_widget = gui.listWidget

        # Get the topmost item in the listWidget
        top_item = list_widget.item(0)
        # Get the rectangle of the topmost item
        top_item_rect = list_widget.visualItemRect(top_item)
        # Calculate the position to click (center of the item's rect)
        click_position = top_item_rect.center()
        # Map the position to the viewport
        viewport = list_widget.viewport()
        if viewport is None:  # pragma: no cover
            raise Exception("Viewport is None")
        viewport_position = viewport.mapToGlobal(click_position)
        list_widget_position = list_widget.mapFromGlobal(viewport_position)
        mock_warning = mocker.patch(
            "chatgpt_conversation_finder.gui.QMessageBox.warning", return_value=""
        )
        # with qtbot.waitSignal(list_widget.clicked, timeout=500):
        with qtbot.waitCallback() as callback:
            if open_fail:

                def side_effect(url: str) -> None:
                    callback()
                    raise Exception("Failed to open")

                mocker.patch("webbrowser.open", side_effect=side_effect)
            else:
                mocker.patch("webbrowser.open", side_effect=callback)
            qtbot.mouseClick(
                list_widget.viewport(),
                Qt.MouseButton.LeftButton,
                pos=list_widget_position,
            )
        if open_fail:
            mock_warning.assert_called_once_with(
                gui,
                "Error",
                "Failed to open conversation: Failed to open",
                QMessageBox.StandardButton.Ok,
            )
        else:
            assert True
