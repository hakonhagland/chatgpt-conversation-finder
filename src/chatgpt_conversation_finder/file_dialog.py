import logging
import os

from PyQt6.QtWidgets import QApplication, QFileDialog
# from PyQt6.QtCore import QDir

from chatgpt_conversation_finder.config import Config


class FileDialog:
    def __init__(self, app: QApplication, config: Config) -> None:
        # NOTE: QApplication instance, is not used explicitly in this class but needs
        #       still needs to be created to avoid a crash when using QFileDialog
        self.app = app
        self.config = config
        self.folder_path = self.config.get_filedialog_default_dir()
        logging.info(f"folder path = {self.folder_path}")

    def select_zip_file(self) -> str | None:
        # List all zip files in the folder sorted by modification time
        try:
            files = [f for f in os.listdir(self.folder_path) if f.endswith(".zip")]
            files.sort(
                key=lambda x: os.path.getmtime(os.path.join(self.folder_path, x)),
                reverse=True,
            )
        except FileNotFoundError:
            print(f"The specified folder {self.folder_path} does not exist")
            return None
        if not files:
            print(f"No zip files found in folder {self.folder_path}")
            return None

        # Create a file dialog for opening a file
        dialog = QFileDialog()
        dialog.setDirectory(self.folder_path)
        dialog.setNameFilter("Zip files (*.zip)")
        dialog.setOption(
            QFileDialog.Option.DontUseNativeDialog, False
        )  # Set the option directly
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        dialog.selectFile(
            os.path.join(self.folder_path, files[0])
        )  # Select the most recently modified zip file by default

        # Show the dialog and get the selected file
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            return dialog.selectedFiles()[0]
        else:
            print("Cancelled file selection.")
            return None

    def get_conversations_json_path(self) -> str | None:
        selected_file = self.select_zip_file()
        return selected_file
