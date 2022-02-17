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
# add square skill helpers
sys.path.append(os.path.abspath('../square-skill-helpers'))
# add square skill api
sys.path.append(os.path.abspath('../square-skill-api'))


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
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_markdown_tables",
    "sphinx_copybutton",
    "sphinx-favicon",
    "sphinxcontrib.autodoc_pydantic",
]


autosummary_generate = True
autoclass_content = "class"

# enable pydantic model docs
autodoc_pydantic_model_show_json = True
autodoc_pydantic_settings_show_json = False

# mocking imports for autodoc
autodoc_mock_imports = ["dotenv", "elasticsearch", "transformers", "torch", "pydantic", "numpy", "starlette",
                        "sentence_transformers", "onnxruntime", "fastapi"]

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
html_logo = "images/SQ_Web_Light_90px.png"


# Material theme options (see theme.conf for more information)
html_theme_options = {
    # 'body_max_width': '70%',
    "html_minify": True,
    "html_prettify": False,
    "css_minify": True,

    # Set the name of the project to appear in the navigation.
    'nav_title': 'SQuARE',
    # Set the color and the accent color
    # 'color_primary': '#086494',
    # 'color_accent': '#086494',
    'master_doc': False,

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://github.com/UKP-SQuARE/square-core',

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/UKP-SQuARE/square-core',
    'repo_name': 'square-core',

    # 'nav_links': [{'href': 'http://square.ukp-lab.de', 'title': 'SQuARE Platform', 'external': 'True'},
                  # {'href': 'index', 'title': 'Getting Started', 'internal': 'True'},
                  # {'href': '', 'title': 'Components', 'internal': ''},
                  # {'href': '', 'title': 'API', 'internal': ''}
                  # ],

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 1,
    # If False, expand all TOC entries
    'globaltoc_collapse': True,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': True,

    "version_dropdown": True,
    "version_json": "_static/versions.json",
    "version_info": {
        "v0.0.1": "",
    },

}


html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

favicons = [
    {
        "rel": "icon",
        "static-file": "SQ_Web_Light.png",
        "type": "image/png",
    },

    {
        "rel": "apple-touch-icon",
        "static-file": "SQ_Web_Light.png",
        "type": "image/png",
    },
]


def setup(app):
    app.add_css_file('custom.css')
