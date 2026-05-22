# pyIECWind

[![CI](https://github.com/SMI-Lab-Inha/pyIECWind/actions/workflows/ci.yml/badge.svg)](https://github.com/SMI-Lab-Inha/pyIECWind/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/pyiecwind/badge/?version=latest)](https://pyiecwind.readthedocs.io/en/latest/)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![OpenFAST](https://img.shields.io/badge/OpenFAST-InflowWind-0A7E8C)

`pyIECWind` generates IEC 61400-1 wind-condition `.wnd` files for the OpenFAST
*InflowWind* module. It reproduces the wind-condition models of the legacy NREL
*IECWind* tool behind a typed, validated Python API, a reproducible command-line
interface, and a regression-locked test suite.

The six classical condition families — `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and
`EWM` — are supported across SI and English unit systems and IEC 61400-1
Editions 1 and 3. See [Scope and limitations](docs/limitations.rst) for the
precise boundary of what is implemented.

## Highlights

- **Validated inputs.** `IECParameters` is frozen and validated on construction;
  invalid turbine definitions fail immediately rather than producing misleading
  files.
- **Fail-closed generation.** The batch API raises on the first invalid condition
  by default; partial output is opt-in.
- **Verified output.** A committed golden `.wnd` corpus and an independent oracle
  derived from the IEC equations lock numeric results
  ([Validation](docs/validation.rst)).
- **Three input formats.** An OpenFAST-style table (recommended), a keyed format,
  and the legacy positional layout ([Input files](docs/data_sources.rst)).
- **Typed and documented.** `mypy --strict`, NumPy-style docstrings, and a Sphinx
  documentation set.

## Installation

```bash
python -m pip install pyiecwind
```

For a conda environment or a source/development install, see
[Installation](docs/installation.rst).

## Usage

Generate wind files from an input file:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

Write a starter template, or use the guided wizard:

```bash
pyiecwind template my_case.ipt
pyiecwind wizard -o outputs
```

From Python:

```python
from pyiecwind import generate_from_input_file

params, result = generate_from_input_file("examples/sample_case.ipt", output_dir="outputs")
print(f"generated {result.count} files")
```

See [Quickstart](docs/quickstart.rst) for more.

## Documentation

The full documentation is hosted at
[pyiecwind.readthedocs.io](https://pyiecwind.readthedocs.io/en/latest/). The
source is in [`docs/`](docs/) and builds with Sphinx
(`sphinx-build -W -b html docs docs/_build/html`). Key references:

- [Theory](docs/theory.rst) — the IEC equations behind each case family
- [Input files](docs/data_sources.rst) and [Units](docs/units.rst)
- [API reference](docs/api.rst) and [API contract](docs/api_contract.rst)
- [Validation](docs/validation.rst) and [Scope and limitations](docs/limitations.rst)

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
mypy
pytest --cov=pyiecwind
```

Contribution guidelines and the full quality-gate list are in
[Contributing](docs/contributing.rst).

## License

Released under the MIT License. See [LICENSE](LICENSE).
