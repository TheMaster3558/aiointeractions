# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import builtins

builtins.__sphinx_build__ = True  # type: ignore

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath('..'))


import aiointeractions

project = aiointeractions.__name__
copyright = aiointeractions.__copyright__
author = aiointeractions.__author__
release = aiointeractions.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx_copybutton', 'sphinx_tabs.tabs']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'shibuya'
html_static_path = ['_static']

html_theme_options = {
    'accent_color': 'yellow',
    'announcement': 'aiointeractions is no longer compatible with discord.py starting from discord.py v2.4',
    'nav_links': [
        {
            'title': 'PyPi',
            'url': 'https://pypi.org/project/aiointeractions',
            'summary': 'You can install aiointeractions here!',
        }
    ],
    'github_url': 'https://github.com/TheMaster3558/aiointeractions',
    'youtube_url': 'https://www.youtube.com/channel/UCEbHD3v3kPmVdlQ74FkUkGw',
    'page_layout': 'default'
}

html_context = {
    'source_type': 'github',
    'source_user': 'TheMaster3558',
    'source_repo': 'aiointeractions',
}

html_logo = '_static/logo.png'


autodoc_typehints = 'none'
