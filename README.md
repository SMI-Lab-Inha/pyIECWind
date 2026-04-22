# pyIECWind

`pyIECWind` is a packaged, modernized Python version of the legacy NREL `IECWind` workflow for generating IEC wind-condition `.wnd` files for AeroDyn/OpenFAST-style studies.

The repository now has:

- an installable Python package in `src/pyiecwind`
- a console command, `pyiecwind`
- an interactive `wizard` mode for non-expert users
- a template-driven `run` workflow for scripted or repeatable case generation
- an OpenFAST-style input format with case-family rows
- a full unit test suite plus GitHub Actions CI

## Project Layout

```text
src/pyiecwind/    package code
tests/            smoke tests
examples/         sample input file
.github/          GitHub Actions CI
iec_wind.py       backward-compatible wrapper
pyproject.toml    package metadata
```

## Install

### Conda

Using your Miniconda installation directly:

```powershell
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' env create -f environment.yml
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' run -n pyiecwind pyiecwind --help
```

Manual environment creation:

```powershell
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' create -n pyiecwind python=3.11 numpy pip -y
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' run -n pyiecwind python -m pip install -e .
```

### Pip

```bash
pip install -e .
```

## Quick Start

Generate from an input file:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

The packaged example input now uses an OpenFAST-style layout:

```text
40.000   t1    - transient start time [s]
2        wtc   - wind turbine class
ECD      True  [+R]  - Extreme Coherent Gust with Direction Change. Options: ...
```

Create a commented template:

```bash
pyiecwind template my_case.ipt
```

Launch the interactive wizard:

```bash
pyiecwind wizard -o outputs
```

You can also keep using the old script name:

```bash
python iec_wind.py run examples/sample_case.ipt -o outputs
```

## Why The Wizard Matters

The `wizard` mode is aimed at users who do not already know the IEC case syntax. It walks through:

- turbine class and turbulence category
- geometry and operating speeds
- condition selection
- condition-specific options such as direction, shear type, recurrence period, or speed modifiers

It can also save a reproducible `.ipt` file alongside the generated `.wnd` files.

## Testing

Run the full local test suite with:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -v
```

GitHub Actions runs the same suite automatically on pushes and pull requests across Python 3.10 to 3.12.

## Supported Conditions

- `ECD`: Extreme Coherent Gust with Direction Change
- `EWS`: Extreme Wind Shear
- `EOG`: Extreme Operating Gust
- `EDC`: Extreme Direction Change
- `NWP`: Normal Wind Profile
- `EWM`: Extreme Wind Model

## Notes

- Internal calculations remain in SI units.
- The current packaging effort preserves the existing Python port as the computational engine.
- `NWP` still follows legacy behavior: the embedded speed is interpreted in `m/s`.

## Existing Reference Material

- [IECWind_User_Guide.md](/Users/burak/Desktop/IEC_Wind/IECWind_User_Guide.md)
- [QUICKSTART.md](/Users/burak/Desktop/IEC_Wind/QUICKSTART.md)
- [examples/sample_case.ipt](/Users/burak/Desktop/IEC_Wind/examples/sample_case.ipt)
- [environment.yml](/Users/burak/Desktop/IEC_Wind/environment.yml)
- [.github/workflows/ci.yml](/Users/burak/Desktop/IEC_Wind/.github/workflows/ci.yml)
