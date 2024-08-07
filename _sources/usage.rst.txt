Usage
=====

First download your ChatGPT conversations from the OpenAI API:

* Sign in to ChatGPT.
* In the top right corner of the page click on your profile icon.
* Click Settings.
* Click Data Controls menu.
* Under Export Data click Export.
* In the confirmation screen click Confirm export.
* You should receive an email with your data.
  Note: The link in the email expires after 24 hours
* From the email, click the `"Download data export"` button to download a ``.zip`` file. The file will usually end up in your
  Downloads folder.

Next, run the command ``chatgpt-conversation-finder update-data`` with the path to
the downloaded ``.zip`` file. Alternatively, you can omit the path and the program
will present a file dialog for you to select the file.
The dialog is by default initialized with the newest ``.zip`` file in your Downloads folder.

After the data has been extracted, you can search for conversations using the command ``chatgpt-conversation-finder gui``. This will open a GUI where you can search for conversations by entering a search term in the search bar.

By clicking on a conversation in the list, it will open in your default browser.

Commands
--------

.. note::
    This documentation can also be obtained by running
    ``chatgpt-conversation-finder --help`` from the terminal window.

    Or, to get help for a specific subcommand, run
    ``chatgpt-conversation-finder <subcommand> --help``.

.. rstcheck: ignore-directives click
.. click:: chatgpt_conversation_finder.main:main
  :prog: chatgpt-conversation-finder
  :nested: full
