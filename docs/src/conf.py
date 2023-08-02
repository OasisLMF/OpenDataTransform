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
import datetime
from sphinx.ext import autodoc

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "Open Data Transformation"
# copyright = ""
author = "Insurance Development Forum"
html_title = "Open Data Transformation"
html_short_title = "Open Data Transformation"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'autoapi.extension',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'friendly'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "sphinx-material"
# html_theme = "alabaster"
# html_theme = "sphinx_rtd_theme"
html_theme = 'furo'


html_show_copyright = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_favicon = "idf_square.ico"
html_logo = "IDF_Original.jpg"
# html_css_files = "custom.css"

html_css_files = [
    'https://fonts.googleapis.com/css?family=Raleway',
]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": " #862633",
        "color-brand-content": "#d22630",
        "font-stack": "Raleway, sans-serif",
        "font-stack--monospace": "Courier, monospace",
    }
}



autoapi_type = "python"
autoapi_dirs = ["../../converter"]
autoapi_root = "package"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
]
