import webbrowser
from typing import Any

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLineEdit, QMessageBox
# from PyQt6.QtCore import Qt

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.index_manager import IndexManager
from chatgpt_conversation_finder.quick_search import QuickSearch


class ChatGPTFinderGUI(QWidget):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.index_manager = IndexManager(self.config, init_type="load")
        self.quick_search = QuickSearch(self.config, self.index_manager)
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("ChatGPT Conversation Finder")
        self.setGeometry(100, 100, 400, 600)  # Adjust size as necessary
        layout = QVBoxLayout()
        self.listWidget = QListWidget()
        self.listWidget.clicked.connect(self.open_conversation)
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Type here to search...")
        self.lineEdit.textChanged.connect(self.update_list)
        layout.addWidget(self.listWidget)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)
        self.load_initial_data()
        self.lineEdit.setFocus()

    def create_title_to_msg_id_map(self, results: list[dict[str, Any]]) -> None:
        self.msg_ids = {}  # Store message IDs for each title
        for result in results:
            self.msg_ids[result["title"]] = result["id"]
        return

    def load_initial_data(self) -> None:
        # Load initial data
        results = self.quick_search.search_conversations("")
        self.create_title_to_msg_id_map(results)
        self.update_list_widget(results)

    def update_list(self, search_term: str) -> None:
        # Update the list based on search term
        results = self.quick_search.search_conversations(search_term)
        self.update_list_widget(results)

    def update_list_widget(self, results: list[dict[str, Any]]) -> None:
        self.listWidget.clear()
        for result in sorted(results, key=lambda x: x["create_time"], reverse=True):
            self.listWidget.addItem(f"{result['title']}")

    def open_conversation(self, index: Any) -> None:
        item = self.listWidget.item(index.row())
        if item:
            msg_id = self.msg_ids.get(item.text())
            try:
                url = f"https://chat.openai.com/c/{msg_id}"
                webbrowser.open(url)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to open conversation: " + str(e),
                    QMessageBox.StandardButton.Ok,
                )
