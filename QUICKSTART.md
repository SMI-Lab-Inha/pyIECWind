# Quick Start

## 1. Install The Package

Recommended with Miniconda:

```powershell
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' env create -f environment.yml
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' run -n pyiecwind pyiecwind --help
```

Or with `pip` in an existing environment:

```bash
pip install -e .
```

## 2. Pick A Workflow

Interactive workflow for non-experts:

```bash
pyiecwind wizard -o outputs
```

Template workflow for repeatable studies:

```bash
pyiecwind template my_case.ipt
pyiecwind run my_case.ipt -o outputs
```

Example input file:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

The input file format is now OpenFAST-style:

```text
True    si_unit  - True for SI (m, m/s)
40.0    t1       - transient start time [s]
ECD     True     [+R]      - Extreme Coherent Gust with Direction Change. Options: +R, -R, ...
NWP     True     [23.7]    - Normal Wind Profile. Options: array of hub-height wind speeds in m/s
```

## 3. Check The Outputs

You should see one `.wnd` file per selected condition, for example:

```text
ECD+R.wnd
EWSV+12.0.wnd
EWM50.wnd
```

## Backward Compatibility

The legacy entry point still works:

```bash
python iec_wind.py run examples/sample_case.ipt -o outputs
```

## Run Tests

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -v
```
