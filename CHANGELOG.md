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

- Future changes will be tracked here
