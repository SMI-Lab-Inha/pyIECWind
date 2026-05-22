"""Documentation health checks.

Documentation source is required to be **pure ASCII**. This is the bulletproof
guard against the mojibake that appears when a UTF-8 file (an em-dash, a degree
sign, a Greek symbol) is viewed or re-saved through a cp1252/latin-1 round trip --
a credibility problem in scientific docs. Mathematical notation is written with
reStructuredText math roles/directives (LaTeX), which are themselves ASCII.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def _doc_files() -> list[Path]:
    files = list((_ROOT / "docs").rglob("*.rst"))
    files += [_ROOT / "README.md", _ROOT / "CHANGELOG.md"]
    return [f for f in files if f.exists() and "_build" not in f.parts]


class DocsEncodingTests(unittest.TestCase):
    def test_doc_files_found(self) -> None:
        self.assertTrue(_doc_files(), "no documentation files discovered")

    def test_docs_are_valid_utf8(self) -> None:
        for path in _doc_files():
            with self.subTest(file=path.name):
                path.read_bytes().decode("utf-8")  # raises on invalid UTF-8

    def test_docs_are_ascii_only(self) -> None:
        for path in _doc_files():
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                non_ascii = [(i, ch) for i, ch in enumerate(line) if ord(ch) > 127]
                with self.subTest(file=path.name, line=lineno):
                    self.assertEqual(
                        non_ascii,
                        [],
                        f"{path.name}:{lineno} has non-ASCII {[hex(ord(c)) for _, c in non_ascii]}; "
                        "use ASCII (e.g. '-' for dashes) or reST math for symbols",
                    )


if __name__ == "__main__":
    unittest.main()
