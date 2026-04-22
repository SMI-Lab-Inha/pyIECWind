# pyIECWind

`pyIECWind` is a modern Python package for generating IEC extreme wind-condition files in AeroDyn/OpenFAST `.wnd` format.

The project preserves the core IEC wind-condition logic while providing:

- an installable Python package
- a command-line interface for template-based and guided workflows
- an OpenFAST-style input format
- automated tests and GitHub Actions CI

## Features

- Supports `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and `EWM` condition families
- Generates one `.wnd` file per expanded IEC case
- Accepts OpenFAST-style case-table inputs, modern keyed inputs, and the legacy fixed-line format
- Includes an interactive wizard for non-expert users
- Ships with a sample input file and a commented template generator

## Installation

### Conda

Create the recommended environment from `environment.yml`:

```bash
conda env create -f environment.yml
conda run -n pyiecwind pyiecwind --help
```

Or create the environment manually:

```bash
conda create -n pyiecwind python=3.11 numpy pip -y
conda run -n pyiecwind python -m pip install -e .
```

### Pip

```bash
python -m pip install -e .
```

## Quick Start

Generate wind files from the example input:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

Write a commented template:

```bash
pyiecwind template my_case.ipt
```

Launch the interactive wizard:

```bash
pyiecwind wizard -o outputs
```

The compatibility entry point remains available:

```bash
python iec_wind.py run examples/sample_case.ipt -o outputs
```

## Input Format

The recommended input style is an OpenFAST-like table with one row per parameter and one row per case family. For example:

```text
True            si_unit      - True for SI (m, m/s), False for English (ft, ft/s)
40.000          t1           - transient start time [s]
2               wtc          - wind turbine class (1, 2, or 3)

ECD             True   [+R]       - Extreme Coherent Gust with Direction Change. Options: +R, -R, +R+du, ...
NWP             True   [23.7]     - Normal Wind Profile. Options: array of hub-height wind speeds in m/s
EWM             True   [50]       - Extreme Wind Model. Options: 50 or 01
```

See [`examples/sample_case.ipt`](examples/sample_case.ipt) for a complete example.

## Project Layout

```text
src/pyiecwind/              package implementation
examples/                   example input file
tests/                      automated test suite
.github/workflows/ci.yml    GitHub Actions workflow
iec_wind.py                 backward-compatible wrapper
pyproject.toml              package metadata
environment.yml             conda environment definition
src/README.md               package-internal overview
```

## Testing

Run the full test suite locally with:

```bash
PYTHONPATH=src:tests python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -v
```

GitHub Actions runs the same suite automatically on pushes and pull requests.

## Reference Files

- [`QUICKSTART.md`](QUICKSTART.md)
- [`IECWind_User_Guide.md`](IECWind_User_Guide.md)
- [`examples/sample_case.ipt`](examples/sample_case.ipt)
- [`environment.yml`](environment.yml)
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## Notes

- Internal calculations are performed in SI units.
- `NWP` retains the legacy IECWind convention that the embedded speed is interpreted in `m/s`.
