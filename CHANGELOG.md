# Changelog

All notable changes to `pyIECWind` will be documented in this file.

The format is inspired by Keep a Changelog, adapted to the current needs of this project.

## [0.1.0] - 2026-04-22

First public release of `pyIECWind`.

### Added

- Installable Python package structure under `src/pyiecwind`
- Command-line interface with `run`, `template`, and `wizard` workflows
- OpenFAST-style input formatting with aligned `value  key  - comment` rows
- Case-table support for `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and `EWM`
- User documentation in `docs/`
- GitHub Actions CI workflow
- Automated test coverage for parsing, validation, generation, CLI behavior, and package surface
- First public release tag: `v0.1.0`

### Changed

- Refactored the original monolithic implementation into clearer package modules
- Replaced legacy default filenames with `pyiecwind.ipt` and `pyiecwind_template.ipt`
- Clarified that generated `.wnd` files are intended for OpenFAST `InflowWind`
- Explicitly documented current `IEC 61400-1` scope, including `Edition 1` and `Edition 3` support through `iec_edition`

### Removed

- Legacy top-level files and script-era artifacts that were no longer appropriate for the public package layout

## Unreleased

### Added

- `__version__` exposed on the package, single-sourced from package metadata
- Structured generation results (`GenerationResult`, `GenerationError`) and a
  `strict=` mode on `generate_all` / `generate_from_input_file`
- `IECWindWarning` category for advisory validation issues (escapable to errors)
- `--continue-on-error` flag on the `run` command; the CLI now exits nonzero when
  conditions fail to generate
- Golden-reference `.wnd` corpus under `tests/golden/`, plus golden, property/invariant,
  and independent-oracle test suites locking numeric output
- Developer tooling configuration (ruff, mypy, pytest-cov with a 90% coverage gate)
- Sphinx documentation (API reference, architecture, and verification matrix)
- Cross-platform CI matrix (Linux/macOS/Windows × Python 3.10–3.13) with lint,
  type-check, coverage gate, wheel build/smoke, and docs build
- `MANIFEST.in` so the sdist ships a complete, runnable test suite and the docs source
- Documentation encoding guard (rejects mojibake / invalid UTF-8 in markdown)
- `legacy=` option on `parse_input_file` to opt into legacy edition coercion

### Changed

- Library code no longer prints; all user-facing output is owned by the CLI
- Generators return the written `Path`; `write_template` returns its path
- The `.wnd` header version stamp now reflects the single-sourced package version
- `generate_all` / `generate_from_input_file` now **fail closed** (`strict=True`
  by default); the CLI opts into collecting failures with `strict=False`
- `IECParameters` is now a frozen, self-validating dataclass with `conditions`
  stored as a tuple, so invalid turbine/input states cannot be constructed
- `pyiecwind.core` no longer re-exports private helpers or alias tables

### Fixed

- Version drift between `models.py` (1.0.0) and `pyproject.toml` (0.1.0)
- EOG/EDC silently ignored speed modifiers on the cut-in (I) and cut-out (O)
  references; these are now rejected instead of producing misleading files
- Unsupported IEC editions were silently coerced to edition 3; they now raise
  unless `legacy=True` is passed
- Unknown `si_unit` values were treated as English units; they are now rejected
