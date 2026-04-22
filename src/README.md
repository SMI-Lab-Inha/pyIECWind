# Source Layout

This directory contains the `pyIECWind` package implementation.

## Modules

- `pyiecwind/core.py`: input parsing, IEC condition expansion, and `.wnd` generation
- `pyiecwind/cli.py`: command-line interface and guided wizard
- `pyiecwind/__init__.py`: public package exports
- `pyiecwind/__main__.py`: `python -m pyiecwind` entry point

## Design Notes

- The package keeps the validated IEC wind-condition physics while using a Python-first interface.
- Input files are centered on an OpenFAST-style table format, with compatibility support for older keyed and fixed-line formats.
- Tests live in the top-level `tests/` directory rather than inside `src/`.
