# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import importlib.metadata

# -- Project information -----------------------------------------------------

project = "PyZEAL"
copyright = "2021, Philipp Schuette, Tobias Weich"
author = "Sebastian Albrecht and Philipp Schuette and Tobias Weich"

# The short X.Y version
version = importlib.metadata.version("pyzeta")
# The full version, including alpha/beta/rc tags
release = importlib.metadata.version("pyzeta")


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "nbsphinx",
    "sphinx.ext.doctest",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.bibtex",
]

bibtex_bibfiles = ["refs.bib"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "classic"
html_theme_options = {
    "rightsidebar": "false",
    "relbarbgcolor": "green",
    "footerbgcolor": "black",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/custom.css",
]

# Add type of source files
source_suffix = [".rst"]

autodoc_typehints = "description"
