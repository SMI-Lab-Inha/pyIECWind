# Quick Start

## 1. Install

With conda:

```bash
conda env create -f environment.yml
conda run -n pyiecwind pyiecwind --help
```

With pip:

```bash
python -m pip install -e .
```

## 2. Choose A Workflow

Use the guided workflow:

```bash
pyiecwind wizard -o outputs
```

Use a template-driven workflow:

```bash
pyiecwind template my_case.ipt
pyiecwind run my_case.ipt -o outputs
```

Run the shipped example:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

## 3. Understand The Input Layout

The recommended input format uses OpenFAST-style parameter rows and case-family rows:

```text
True            si_unit      - True for SI (m, m/s), False for English (ft, ft/s)
40.000          t1           - transient start time [s]
ECD             True   [+R]       - Extreme Coherent Gust with Direction Change. Options: +R, -R, +R+du, ...
NWP             True   [23.7]     - Normal Wind Profile. Options: array of hub-height wind speeds in m/s
```

See [`examples/sample_case.ipt`](examples/sample_case.ipt) for a complete example.

Default filenames:

- `pyiecwind template` writes `pyiecwind_template.ipt`
- `pyiecwind run` without an explicit file reads `pyiecwind.ipt`

IEC standard note:

- `pyIECWind` currently implements the `IEC 61400-1` case framework used by legacy `IECWind`
- the `iec_edition` input currently supports `Edition 1` and `Edition 3`

More detailed documentation:

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)
- [`docs/STUDY_EXAMPLE.md`](docs/STUDY_EXAMPLE.md)
- [`docs/INPUT_FORMAT.md`](docs/INPUT_FORMAT.md)
- [`docs/CASE_REFERENCE.md`](docs/CASE_REFERENCE.md)

## 4. Check The Outputs

One `.wnd` file is written for each selected case, for example:

```text
ECD+R.wnd
EWSV+12.0.wnd
EWM50.wnd
```

## 5. Run Tests

```bash
PYTHONPATH=src:tests python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -v
```
