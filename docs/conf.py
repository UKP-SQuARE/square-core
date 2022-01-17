# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))
# add model API path
sys.path.append(os.path.abspath('../square-model-inference-api/inference_server'))
# add datastore API path
sys.path.append(os.path.abspath('../datastore-api'))


# -- Project information -----------------------------------------------------

project = 'SQuARE'
copyright = '2021, UKP'
author = 'UKP'

# The full version, including alpha/beta/rc tags
release = ''


# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.autosectionlabel',
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_markdown_tables",
    "sphinx_copybutton",
]


autosummary_generate = True
autoclass_content = "class"

# mocking imports for autodoc
autodoc_mock_imports = ["elasticsearch"]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# theme to use
html_theme = 'sphinx_material'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# logo path
html_logo = "images/SQ_Web_Dark_160px.png"


# Material theme options (see theme.conf for more information)
html_theme_options = {

    "html_minify": False,
    "html_prettify": True,
    "css_minify": True,

    # Set the name of the project to appear in the navigation.
    'nav_title': 'SQuARE',
    # Set the color and the accent color
    'color_primary': '#086494',
    'color_accent': '#086494',

    'master_doc': False,

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/UKP-SQuARE/square-core',
    'repo_name': 'square-core',

    # 'nav_links': [{'href': 'index', 'title': 'Home', 'internal': 'True'},
                  # {'href': 'index', 'title': 'Getting Started', 'internal': 'True'},
                  # {'href': '', 'title': 'Components', 'internal': ''},
                  # {'href': '', 'title': 'API', 'internal': ''}
                  # ],

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 6,
    # If False, expand all TOC entries
    'globaltoc_collapse': True,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,

    "version_dropdown": True,
    "version_json": "_static/versions.json",
    "version_info": {
        "v0.0.1": "",
    },

}

html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
