import json
import locale
import logging
import sys
import webbrowser

import click
import colorama
from sphinx_click.rst_to_ansi_formatter import make_rst_to_ansi_formatter
from PyQt6.QtWidgets import QApplication

from chatgpt_conversation_finder.chats_json_handler import ChatsJsonHandler
from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.constants import RegexFlags
from chatgpt_conversation_finder.edit_file import EditFile
from chatgpt_conversation_finder.file_dialog import FileDialog
from chatgpt_conversation_finder.grep_handler import GrepConversationsHandler
from chatgpt_conversation_finder.gui import ChatGPTFinderGUI
from chatgpt_conversation_finder.helpers import Helpers
from chatgpt_conversation_finder.index_manager import IndexManager
from chatgpt_conversation_finder.validate_conversations import ValidateConversations

# Most users should depend on colorama >= 0.4.6, and use just_fix_windows_console().
colorama.just_fix_windows_console()
# Set the locale to the user's default setting
locale.setlocale(locale.LC_ALL, "")
# Set the documentation URL for make_rst_to_ansi_formatter()
doc_url = "https://hakonhagland.github.io/chatgpt-conversation-finder/main/index.html"
# CLI colors for make_rst_to_ansi_formatter()
cli_colors = {
    "heading": {"fg": colorama.Fore.GREEN, "style": colorama.Style.BRIGHT},
    "url": {"fg": colorama.Fore.CYAN, "style": colorama.Style.BRIGHT},
    "code": {"fg": colorama.Fore.BLUE, "style": colorama.Style.BRIGHT},
}
click_command_cls = make_rst_to_ansi_formatter(doc_url, colors=cli_colors)


@click.group(cls=make_rst_to_ansi_formatter(doc_url, group=True, colors=cli_colors))
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """``chatgpt-conversation-finder`` let's you open a
    ChatGPT conversation in your default web browser. It has the following sub commands:

    * ``create-search-index``: generates a search index for the conversations.json file.
    * ``extract-conversations``: extracts conversations from the ``conversations.json`` file.
    * ``edit-confg``: opens the config.ini file in your default text editor.
    * ``grep``: runs grep on the ``conversations.json`` file for a given regex.
    * ``gui``: opens a GUI for searching conversations. Let's you open a conversation in your default web browser.
    * ``open``: opens a conversation with a given ID in your default web browser.
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


@main.command(cls=click_command_cls)
def edit_config() -> None:
    """``chatgpt-conversation-finder edit-config`` lets you edit the config file"""
    config = Config()
    EditFile(config).edit_config_file()


@main.command(cls=click_command_cls)
@click.argument("search_term", type=str, required=True)
def search_term(search_term: str) -> None:
    """Search for an exact term in the conversations or in their titles.
    This will print out the title, ID, and
    creation time of all conversations that contain the search term. The search is case-insensitive.
    This command has been superceded by the ``grep`` command which is more powerful."""
    config = Config()
    chats_json_handler = ChatsJsonHandler(config)
    matches = chats_json_handler.search_conversations(search_term)
    for match in matches:
        print(
            f"Title: {match['title']}, ID: {match['id']}, "
            f"Created: {Helpers.format_create_time(match['create_time'])}"
        )


@main.command(cls=click_command_cls)
@click.argument("regex", type=str, required=True)
@click.option("--flags", "-f", type=str, default="", help="Regex flags")
def grep(regex: str, flags: str) -> None:
    """``chatgpt-conversation-finder grep`` runs grep on the ``conversations.json`` file.
    Valid values for the ``--flags`` option are: ``IGNORECASE``, ``MULTILINE``, and ``DOTALL``.
    See the `Python documentation <https://docs.python.org/3/library/re.html#flags>`_ for their meaning.
    Multiple flags can be combined, e.g. ``IGNORECASE|MULTILINE``. The shortcut forms ``I``, ``M``, and
    ``S`` can also be used. Further, flag names can also be given in lowercase. Examples:
    ``IGNORECASE``, ``IGNORECASE|MULTILINE``, ``I|M``, ``i|m``, ``i|s``, ``i|s``, ``i|s|m``.
    """
    regex_flags = RegexFlags.from_str(flags)
    config = Config()
    grep_handler = GrepConversationsHandler(config)
    grep_handler.grep(regex, regex_flags)


@main.command(cls=click_command_cls)
def gui() -> None:
    """``chagpt-conversation-finder gui`` opens the GUI.  This will open a GUI where you can
    search for conversations by entering a search term in the search bar. By clicking on a
    conversation in the list, it will open in your default browser."""
    app = QApplication(sys.argv)
    config = Config()
    gui = ChatGPTFinderGUI(config)  # Adjust the path as necessary
    gui.show()
    sys.exit(app.exec())


@main.command(cls=click_command_cls)
@click.argument("conversation_id", type=str, required=True)
def open(conversation_id: str) -> None:
    """``chagpt-conversation-finder open`` opens a conversation with a given ID in your default
    web browser. This is most useful after running the ``grep`` command to find a conversation. Then
    you will have the ID of the conversation you want to open."""
    # config = Config()
    try:
        url = f"https://chat.openai.com/c/{conversation_id}"
        webbrowser.open(url)
    except Exception as e:
        logging.error(f"Error opening conversation: {e}")
    else:
        logging.info(f"Opened conversation with ID {id}")


@main.command(cls=click_command_cls)
def pretty_print() -> None:
    """``chagpt-conversation-finder pretty-print`` pretty prints the
    ``conversations.json`` file to stdout. This is the file that will be extracted by the
    ``update-data`` command."""
    config = Config()
    #    fn = config.get
    chats_json_handler = ChatsJsonHandler(config)
    conversations = chats_json_handler.get_conversations()
    print(json.dumps(conversations, indent=4))


@main.command(cls=click_command_cls)
@click.argument("filename", type=str, required=False)
def update_data(filename: str) -> None:
    """``chagpt-conversation-finder update-data`` updates the ``conversations.json``
    data file from a downloaded chat data file in .zip format from OpenAI website.
    The ``FILENAME`` is copied to the user's data directory (as defined by the
    ``platformdirs`` package). Then extracts the ``.zip`` file and replaces any existing
    ``conversations.json`` file with the new one. If ``FILENAME`` is not provided, a dialog
    will open to select the file. The default directory for the download dialog is
    the user's ``Downloads`` directory. If you wish, you can change the default directory
    by editing the ``config.ini`` file.

    Args: ``FILENAME`` is the path to the ``.zip`` file containing the chat data. If not given,
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


@main.command(cls=click_command_cls)
def create_search_index() -> None:
    """``chagpt-conversation-finder create-search-index`` generates a search index
    for the ``conversations.json`` file. You most likely do not need to run this command
    as the ``update-data`` command automatically creates the search index."""
    config = Config()
    IndexManager(config, init_type="create")
    logging.info("Search index created")


@main.command(cls=click_command_cls)
def validate_conversations() -> None:
    """``chagpt-conversation-finder validate-conversations`` validates the
    ``conversations.json`` file. Currently, this only checks for conversations with no title."""
    config = Config()
    if ValidateConversations(config).validate():
        logging.info("All conversations are valid.")
    else:
        logging.error("Some conversations are invalid.")


if __name__ == "__main__":
    main()  # pragma: no cover
