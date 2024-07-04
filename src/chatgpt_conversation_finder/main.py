import json
import locale
import logging
import sys

import click
from sphinx_click.rst_to_ansi_formatter import make_rst_to_ansi_formatter
from PyQt6.QtWidgets import QApplication

from chatgpt_conversation_finder.chats_json_handler import ChatsJsonHandler
from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.file_dialog import FileDialog
from chatgpt_conversation_finder.gui import ChatGPTFinderGUI
from chatgpt_conversation_finder.helpers import Helpers
from chatgpt_conversation_finder.index_manager import IndexManager
from chatgpt_conversation_finder.validate_conversations import ValidateConversations

# Set the locale to the user's default setting
locale.setlocale(locale.LC_ALL, "")
# Set the documentation URL for make_rst_to_ansi_formatter()
doc_url = "https://hakonhagland.github.io/chatgpt-conversation-finder/main/index.html"


@click.group(cls=make_rst_to_ansi_formatter(doc_url, group=True))
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """``chatgpt-conversation-finder`` is a simple Qt app that let's you open a
    ChatGPT conversation in your default web browser. It has the following sub commands:

    * ``create-search-index``: generates a search index for the conversations.json file.
    * ``extract-conversations``: extracts conversations from the ``conversations.json`` file.
    * ``gui``: opens a GUI for searching conversations. Let's you open a conversation in your default web browser.
    * ``pretty-print``: pretty prints the ``conversations.json`` file to stdout.
    * ``search-term``: searches the ``conversations.json`` file for all conversations matching the given search term.
    * ``update-data``: updates the ``conversations.json`` data file from a downloaded chat data file in .zip format from OpenAI website.
    * ``validate-conversations``: validates the ``conversations.json`` file."""

    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)


@main.command(cls=make_rst_to_ansi_formatter(doc_url))
@click.argument("search_term", type=str, required=True)
def search_term(search_term: str) -> None:
    """"""
    config = Config()
    chats_json_handler = ChatsJsonHandler(config)
    matches = chats_json_handler.search_conversations(search_term)
    for match in matches:
        print(
            f"Title: {match['title']}, ID: {match['id']}, "
            f"Created: {Helpers.format_create_time(match['create_time'])}"
        )


@main.command(cls=make_rst_to_ansi_formatter(doc_url))
def gui() -> None:
    """``chagpt-conversation-finder gui`` opens the GUI."""
    app = QApplication(sys.argv)
    config = Config()
    gui = ChatGPTFinderGUI(config)  # Adjust the path as necessary
    gui.show()
    sys.exit(app.exec())


@main.command(cls=make_rst_to_ansi_formatter(doc_url))
def pretty_print() -> None:
    """``chagpt-conversation-finder pretty-print`` pretty prints the
    conversations.json file to stdout."""
    config = Config()
    #    fn = config.get
    chats_json_handler = ChatsJsonHandler(config)
    conversations = chats_json_handler.get_conversations()
    print(json.dumps(conversations, indent=4))


@main.command(cls=make_rst_to_ansi_formatter(doc_url))
@click.argument("filename", type=str, required=False)
def update_data(filename: str) -> None:
    """``chagpt-conversation-finder update-data`` updates the conversations.json
    data file from a downloaded chat data file in .zip format from OpenAI website.
    The ``FILENAME`` is copied to the user's data directory (as defined by the
    platformdirs package). Then extracts the .zip file and replaces any existing
    conversations.json file with the new one. If FILENAME is not provided, a dialog
    will open to select the file. The default directory for the download dialog is
    the user's Downloads directory. If you wish, you can change the default directory
    by editing the config.ini file.

    Args: ``FILENAME`` is the path to the .zip file containing the chat data. If not given,
    a dialog will open to select the file.

    Example: ``chatgpt-conversation-finder update-data ~/Downloads/chat_data.zip``
    """
    config = Config()
    if filename is None:
        app = QApplication(sys.argv)
        filename = FileDialog(app, config).get_conversations_json_path()
        if filename is None:
            logging.error("No file selected")
            return
        logging.info(f"filename = {filename}")
    Helpers.extract_conversations_json_file(config.get_data_dir(), filename)
    logging.info("Creating search index...")
    IndexManager(config, init_type="create")
    logging.info("Search index created")


@main.command(cls=make_rst_to_ansi_formatter(doc_url))
def create_search_index() -> None:
    """``chagpt-conversation-finder create-search-index`` generates a search index
    for the ``conversations.json`` file."""
    config = Config()
    IndexManager(config, init_type="create")
    logging.info("Search index created")


@main.command(cls=make_rst_to_ansi_formatter(doc_url))
def validate_conversations() -> None:
    """``chagpt-conversation-finder validate-conversations`` validates the
    conversations.json file."""
    config = Config()
    if ValidateConversations(config).validate():
        logging.info("All conversations are valid.")
    else:
        logging.error("Some conversations are invalid.")


if __name__ == "__main__":
    main()  # pragma: no cover
