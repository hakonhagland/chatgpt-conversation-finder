import os
import sys

project = "chatgpt-conversation-finder"
copyright = "2024, Håkon Hægland"
author = "Håkon Hægland"
release = "0.1"

sys.path.insert(0, os.path.abspath("../src"))
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx_autodoc_typehints",
    "sphinx_click",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_context = {
    "display_github": True,
    "github_user": "hakonhagland",
    "github_repo": "chatgpt-conversation-finder",
    "github_version": "main",
    "conf_py_path": "/docs/",
}
autodoc_default_options = {
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "members": True,
    "show-inheritance": True,
}
