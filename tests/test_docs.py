"""Lightweight documentation health checks.

Guards against the mojibake that creeps in when a UTF-8 file is re-saved through a
cp1252/latin-1 round trip (e.g. a "+/-" sign showing up as two garbled bytes).
Such corruption is a trust killer in scientific docs, so every markdown source is
checked for valid UTF-8 and for the common mojibake signatures.

Markers are built from explicit byte values so this test file stays pure ASCII.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def _mojibake(*byte_values: int) -> str:
    """Render UTF-8 lead bytes as they appear when decoded as latin-1/cp1252."""

    return bytes(byte_values).decode("latin-1")


# The hallmark substrings of "UTF-8 decoded as cp1252 then re-encoded". The
# comments give the original character whose UTF-8 encoding produces the marker.
_MOJIBAKE_MARKERS = (
    _mojibake(0xC2, 0xB1),  # +/- (U+00B1)
    _mojibake(0xC2, 0xB0),  # degree sign (U+00B0)
    _mojibake(0xC3),  # accented latin lead byte
    _mojibake(0xCE, 0x9B),  # Greek capital lambda (U+039B)
    _mojibake(0xE2, 0x80),  # smart quotes / en/em dashes
    _mojibake(0xE2, 0x82),  # subscripts
    _mojibake(0xE2, 0x88),  # minus / math operators
    _mojibake(0xE2, 0x89),  # <= / >=
    _mojibake(0xE2, 0x96),  # box-drawing
    _mojibake(0xEF, 0xBB, 0xBF),  # UTF-8 BOM bytes in the text body
)


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

    def test_docs_have_no_mojibake(self) -> None:
        for path in _doc_files():
            text = path.read_text(encoding="utf-8")
            for index, marker in enumerate(_MOJIBAKE_MARKERS):
                with self.subTest(file=path.name, marker=index):
                    self.assertNotIn(marker, text, f"mojibake in {path.name}")


if __name__ == "__main__":
    unittest.main()
