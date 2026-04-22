# pyIECWind

[![CI](https://github.com/SMI-Lab-Inha/pyIECWind/actions/workflows/ci.yml/badge.svg)](https://github.com/SMI-Lab-Inha/pyIECWind/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![OpenFAST](https://img.shields.io/badge/OpenFAST-InflowWind-0A7E8C)

`pyIECWind` is a modern Python package for generating IEC wind-condition `.wnd` files for the OpenFAST `InflowWind` module.

It is designed as a practical successor to legacy `IECWind` workflows: easier to install, easier to understand, easier to script, and easier for new users to adopt without having to learn historical fixed-format input files first.

If people are still searching for `IECWind`, `IEC wind file generator`, or legacy NREL-style extreme wind case tooling, this repository is intended to be the place they can land and immediately use.

## Supported IEC Standards

`pyIECWind` is based on the IEC wind-condition framework from `IEC 61400-1`.

The current implementation explicitly supports:

- `IEC 61400-1 Edition 1` for the normal wind-profile shear exponent option `iec_edition = 1`
- `IEC 61400-1 Edition 3` for the normal wind-profile shear exponent option `iec_edition = 3`

Important scope note:

- the `iec_edition` input in this package currently affects the power-law shear exponent selection used in the generated wind files
- the supported extreme wind-condition families are the classic `IECWind`-style cases: `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and `EWM`
- this repository does not claim blanket support for every clause, edition, or newer revision of `IEC 61400-1`

## Why This Project Exists

The original `IECWind` workflow is still useful, but many users now need:

- a package that installs cleanly in modern Python environments
- documentation that explains the case definitions and input style
- an interface that works for both scripted studies and non-expert users
- compatibility with historical `IECWind` inputs where needed
- output files that can be used directly with OpenFAST `InflowWind`

`pyIECWind` keeps the validated IEC case-generation behavior while presenting it through a Python-first package and command-line workflow.

## Features

- Generates `.wnd` files for `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and `EWM`
- Writes files for OpenFAST `InflowWind`
- Supports OpenFAST-style input tables with aligned `value  key  - comment` rows
- Groups case-family selections under a `Cases` block
- Includes an interactive wizard for users who prefer prompts over manual editing
- Preserves support for historical keyed and fixed-line input styles
- Ships with tests and a GitHub Actions CI workflow

## Installation

### Conda

Create the recommended environment:

```bash
conda env create -f environment.yml
conda run -n pyiecwind pyiecwind --help
```

Or install into an existing conda environment:

```bash
conda create -n pyiecwind python=3.11 numpy pip -y
conda run -n pyiecwind python -m pip install -e .
```

### Pip

```bash
python -m pip install -e .
```

## Quick Start

Generate wind files from the included example:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

Write a starter template:

```bash
pyiecwind template my_case.ipt
```

Use the guided workflow:

```bash
pyiecwind wizard -o outputs
```

Default filenames:

- `pyiecwind template` writes `pyiecwind_template.ipt`
- `pyiecwind run` without an explicit file reads `pyiecwind.ipt`

## Example Input

The recommended format is an OpenFAST-style table:

```text
True            si_unit      - True for SI (m, m/s), False for English (ft, ft/s)
40.000          t1           - transient start time [s]
2               wtc          - wind turbine class (1, 2, or 3)
B               catg         - turbulence category (A, B, or C)
0.000           slope_deg    - inflow inclination angle [deg]
3               iec_edition  - IEC edition for alpha (1 or 3)
```

Case selection is grouped under a `Cases` section:

```text
ECD             True   [+R, -R]                  - Extreme Coherent Gust with Direction Change. Options: +R, -R, +R+du, +R-du, -R+du, -R-du
EWS             True   [V+12.0, H-12.0]          - Extreme Wind Shear. Options: V+U, V-U, H+U, H-U
NWP             True   [10.0, 23.7]              - Normal Wind Profile. Options: array of hub-height wind speeds in m/s
EWM             True   [50]                      - Extreme Wind Model. Options: 50 or 01, or an array such as [50, 01]
```

See [`examples/sample_case.ipt`](examples/sample_case.ipt) for a complete working file.

## Documentation

- [`QUICKSTART.md`](QUICKSTART.md)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)
- [`docs/STUDY_EXAMPLE.md`](docs/STUDY_EXAMPLE.md)
- [`docs/INPUT_FORMAT.md`](docs/INPUT_FORMAT.md)
- [`docs/CASE_REFERENCE.md`](docs/CASE_REFERENCE.md)
- [`docs/MIGRATION.md`](docs/MIGRATION.md)
- [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md)

## Project Layout

```text
src/pyiecwind/              package source
examples/                   example input files
docs/                       user and maintainer documentation
tests/                      automated test suite
.github/workflows/ci.yml    GitHub Actions workflow
environment.yml             conda environment definition
pyproject.toml              package metadata
```

## Testing

Run the full test suite:

```bash
PYTHONPATH=src:tests python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -v
```

## Notes

- Internal calculations are performed in SI units.
- `NWP` retains the historical `IECWind` convention that the embedded speed is interpreted in `m/s`.
- This package generates inflow files; it does not run OpenFAST itself.
- The supported IEC standard references are currently `IEC 61400-1 Edition 1` and `Edition 3` as used by the package input and implemented case logic.
