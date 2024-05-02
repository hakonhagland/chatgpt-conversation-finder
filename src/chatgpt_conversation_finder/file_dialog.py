import logging
import os
import sys

from PyQt6.QtWidgets import QApplication, QFileDialog
# from PyQt6.QtCore import QDir

from chatgpt_conversation_finder.config import Config

class FileDialog:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.folder_path = self.config.get_filedialog_default_dir()
        logging.info(f"folder path = {self.folder_path}")

    def select_zip_file(self):
        # List all zip files in the folder sorted by modification time
        try:
            files = [f for f in os.listdir(self.folder_path) if f.endswith('.zip')]
            files.sort(
                key=lambda x: os.path.getmtime(os.path.join(self.folder_path, x)), reverse=True
            )
        except FileNotFoundError:
            print("The specified folder does not exist")
            return None

        if not files:
            print("No zip files found in the folder")
            return None

        # Create a file dialog for opening a file
        dialog = QFileDialog()
        dialog.setDirectory(self.folder_path)
        dialog.setNameFilter("Zip files (*.zip)")
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, False)  # Set the option directly
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        dialog.selectFile(os.path.join(self.folder_path, files[0]))  # Select the most recently modified zip file by default

        # Show the dialog and get the selected file
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            return dialog.selectedFiles()[0]
        else:
            return None

    def get_conversations_json_path(self):
        app = QApplication(sys.argv)
        #window = QWidget()
        #window.resize(320, 240)
        #window.setWindowTitle("Select zip filename for conversations")

        selected_file = self.select_zip_file()
        return selected_file

        #window.show()
        #sys.exit(app.exec())
