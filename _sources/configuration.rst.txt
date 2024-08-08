Configuration
=============

The configuration file is named ``config.ini`` and is located in sub directory
``chatgpt-conversation-finder`` inside the directory ``user_config_dir`` as defined
by the `platformdirs <https://pypi.org/project/platformdirs/>`_ package.

.. note::
    You can open the config file in the default editor by running sub command ``edit-config``
    see :doc:`usage` for more information.

The syntax for the config file is described in the documentation for the
`configparser <https://docs.python.org/3/library/configparser.html>`_ module
in the Python standard library.

.. note::
    See the default config file
    `default_config.ini <https://github.com/hakonhagland/chatgpt-conversation-finder/blob/main/src/chatgpt_conversation_finder/data/default_config.ini>`_
    for the current values of the default editor. The values you specify in configuration file
    will override the default values.
