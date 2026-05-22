"""Sphinx configuration for the pyIECWind documentation."""

from __future__ import annotations

import os
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

# Allow autodoc to import the package when building from a source checkout.
sys.path.insert(0, os.path.abspath("../src"))

project = "pyIECWind"
author = "Jae Hoon Seo"
copyright = f"2025, {author}"  # noqa: A001 - Sphinx requires this name

try:
    release = _distribution_version("pyiecwind")
except PackageNotFoundError:  # pragma: no cover - building from an uninstalled tree
    release = "0.0.0+unknown"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
]

source_suffix = {".rst": "restructuredtext"}
root_doc = "index"

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autoclass_content = "both"
napoleon_numpy_docstring = True
napoleon_google_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = f"pyIECWind {release}"
