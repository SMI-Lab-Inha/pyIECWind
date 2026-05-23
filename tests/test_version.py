from __future__ import annotations

import re
import unittest
from datetime import date
from importlib.metadata import version
from pathlib import Path

import pyiecwind
from pyiecwind import VERSION, models


def _cff_field(name: str) -> str:
    """Return the value of a top-level scalar field in CITATION.cff.

    Parsed with a regex so the test needs no YAML dependency; the file is a flat
    list of ``key: value`` pairs, so this is sufficient and dependency-free.
    """

    root = Path(__file__).resolve().parents[1]
    text = (root / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\s*(.+?)\s*$", text, re.MULTILINE)
    assert match is not None, f"CITATION.cff is missing a '{name}' field"
    return match.group(1).strip().strip('"').strip("'")


class VersionTests(unittest.TestCase):
    """Guard against the historical drift where models.py hardcoded a version
    (1.0.0) different from the one declared in pyproject.toml (0.1.0)."""

    def test_dunder_version_matches_module_constant(self) -> None:
        self.assertEqual(pyiecwind.__version__, VERSION)

    def test_models_version_matches_public_version(self) -> None:
        self.assertEqual(models.VERSION, VERSION)

    def test_version_is_single_sourced_from_package_metadata(self) -> None:
        self.assertEqual(VERSION, version("pyiecwind"))

    def test_pyproject_version_matches_installed_metadata(self) -> None:
        try:
            import tomllib
        except ModuleNotFoundError:
            self.skipTest("tomllib requires Python 3.11+")

        root = Path(__file__).resolve().parents[1]
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["version"], version("pyiecwind"))

    def test_citation_version_matches_installed_metadata(self) -> None:
        # CITATION.cff is hand-maintained YAML, not single-sourced like the
        # package version; this guard fails the build if it drifts behind a release.
        self.assertEqual(_cff_field("version"), version("pyiecwind"))

    def test_citation_release_date_is_iso(self) -> None:
        released = _cff_field("date-released")
        try:
            date.fromisoformat(released)
        except ValueError:
            self.fail(f"CITATION.cff date-released {released!r} is not an ISO YYYY-MM-DD date")


if __name__ == "__main__":
    unittest.main()
