# User Guide

## Overview

`pyIECWind` generates IEC design load case wind files in `.wnd` format for use with the OpenFAST `InflowWind` module.

The implementation is based on the `IEC 61400-1` wind-condition framework used by legacy `IECWind`, with explicit support for `Edition 1` and `Edition 3` through the `iec_edition` input used in this package.

The package supports three user styles:

- command-line use with a prepared input file
- template-first use, where a user edits a generated example
- wizard-driven use for non-expert users

## Recommended Workflow

1. Install the package in a Python or conda environment.
2. Generate a starter input file with `pyiecwind template my_case.ipt`.
3. Edit the general parameters and `Cases` block.
4. Run `pyiecwind run my_case.ipt -o outputs`.
5. Use the generated `.wnd` files in OpenFAST `InflowWind`.

## Command Summary

Generate from an input file:

```bash
pyiecwind run my_case.ipt -o outputs
```

Write a template:

```bash
pyiecwind template my_case.ipt
```

Launch the guided wizard:

```bash
pyiecwind wizard -o outputs
```

Run as a module:

```bash
python -m pyiecwind run my_case.ipt -o outputs
```

## Outputs

Each selected IEC case expands into one or more `.wnd` files. For example:

```text
ECD+R.wnd
EWSV+12.0.wnd
EWM50.wnd
```

The exact filenames are based on the expanded condition codes.

## Units

- Internal calculations are performed in SI units.
- General geometric and operational speed values can be given in SI or English units depending on `si_unit`.
- `NWP` speeds remain explicitly interpreted as `m/s`, matching historical `IECWind` behavior.

## Standard Scope

The package should be understood as supporting the historical `IECWind` family of wind conditions within the `IEC 61400-1` framework.

This means:

- the repository explicitly exposes `iec_edition = 1` and `iec_edition = 3`
- these settings map to the implemented power-law shear exponent behavior used in the generated files
- users should not assume that every feature from every revision of `IEC 61400-1` is implemented unless documented explicitly

## Supported Input Styles

`pyIECWind` accepts:

- the recommended OpenFAST-style table format
- a modern keyed format using `name = value`
- the historical fixed-line layout used by older `IECWind` workflows

For new work, use the OpenFAST-style format.

## Where To Go Next

- For the input file structure, see [`INPUT_FORMAT.md`](INPUT_FORMAT.md).
- For individual case meanings and options, see [`CASE_REFERENCE.md`](CASE_REFERENCE.md).
- For moving from old `IECWind` workflows, see [`MIGRATION.md`](MIGRATION.md).
