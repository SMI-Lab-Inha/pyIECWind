from __future__ import annotations

import unittest
from importlib.metadata import version
from pathlib import Path

import pyiecwind
from pyiecwind import VERSION, models


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


if __name__ == "__main__":
    unittest.main()
