# Example Study Workflow

This example shows a realistic `pyIECWind` workflow where one input file generates multiple IEC wind-condition files for use with OpenFAST `InflowWind`.

## Goal

Starting from a single `.ipt` file, we will:

1. define multiple IEC cases
2. generate a set of `.wnd` files
3. understand how those filenames map into OpenFAST `InflowWind` usage

## Input File

The shipped example file is:

```text
examples/sample_case.ipt
```

Its `Cases` block currently requests:

```text
ECD             True   [+R]                     - Extreme Coherent Gust with Direction Change
EWS             True   [V+12.0]                - Extreme Wind Shear
EOG             True   [R+2.0]                 - Extreme Operating Gust
EDC             True   [+R]                     - Extreme Direction Change
NWP             True   [23.7]                  - Normal Wind Profile
EWM             True   [50]                    - Extreme Wind Model
```

This means one run will expand into six output wind files.

## Run The Study

Generate the files into a dedicated output folder:

```bash
pyiecwind run examples/sample_case.ipt -o outputs
```

## Expected Output Files

For the current sample input, the generated filenames are:

```text
outputs/ECD+R.wnd
outputs/EWSV+12.0.wnd
outputs/EOGR+2.0.wnd
outputs/EDC+R.wnd
outputs/NWP23.7.wnd
outputs/EWM50.wnd
```

## What The Filenames Mean

Each filename directly reflects the expanded IEC condition code:

- `ECD+R.wnd`: extreme coherent gust with direction change, positive direction, rated speed
- `EWSV+12.0.wnd`: extreme vertical wind shear, positive shear, 12.0 user-unit hub-height speed
- `EOGR+2.0.wnd`: extreme operating gust at rated speed plus modifier
- `EDC+R.wnd`: extreme direction change, positive direction, rated speed
- `NWP23.7.wnd`: normal wind profile at 23.7 m/s
- `EWM50.wnd`: 50-year extreme wind model

This naming is useful in parametric studies because the resulting file already tells you which IEC case it represents.

## How This Maps Into OpenFAST InflowWind

`pyIECWind` generates the wind input files themselves. OpenFAST still needs to be configured to point `InflowWind` at the desired `.wnd` file for a given simulation.

Typical usage pattern:

1. generate a library of `.wnd` files with `pyIECWind`
2. choose one case for a simulation run
3. set the `InflowWind` wind-file path in your OpenFAST model to that `.wnd` file
4. run OpenFAST for that case
5. repeat for the other generated files

In practice, many users run a batch study where each OpenFAST case references one of the generated `.wnd` files.

## Concrete InflowWind Example

For the `examples/sample_case.ipt` file, the sample turbine geometry is:

- hub height: `150.0 m`
- rotor diameter / reference length: `240.0 m`

If you want to run OpenFAST with one generated wind file such as:

```text
outputs/EWM50.wnd
```

then the corresponding `InflowWind` section is typically set up as a uniform wind-file case, with the generated `.wnd` file referenced through `Filename_Uni`.

Illustrative snippet:

```text
------- InflowWind INPUT FILE -------------------------------------------------------------------------
IEA 15 MW Offshore Reference Turbine
-------------------------------------------------------------------------------------------------------
False                  Echo            - Echo input data to <RootName>.ech (flag)
2                      WindType        - wind file type (2 = uniform wind file)
0.0                    PropagationDir  - Direction of wind propagation (deg)
0.0                    VFlowAng        - Upflow angle (deg)
False                  VelInterpCubic  - Use cubic interpolation for velocity in time
1                      NWindVel        - Number of points to output the wind velocity
0.0                    WindVxiList     - Inertial X coordinate list (m)
0.0                    WindVyiList     - Inertial Y coordinate list (m)
150.0                  WindVziList     - Inertial Z coordinate list (m)
================== Parameters for Uniform wind file [used only for WindType = 2] ======================
"outputs/EWM50.wnd"    Filename_Uni    - Filename of time series data for uniform wind field
150.0                  RefHt_Uni       - Reference height for horizontal wind speed (m)
240.0                  RefLength       - Reference length for linear horizontal and vertical shear (-)
```

## Field Mapping

For a `pyIECWind` study using the current sample case:

- `Filename_Uni` points to the specific generated wind file for the selected IEC case
- `RefHt_Uni` should match the turbine hub height used in the `.ipt` file
- `RefLength` should match the rotor diameter used in the `.ipt` file
- `WindVziList` is commonly evaluated at hub height for a single-point velocity output example

This means that for the shipped example:

- `RefHt_Uni = 150.0`
- `RefLength = 240.0`

and `Filename_Uni` changes from case to case:

- `outputs/ECD+R.wnd`
- `outputs/EWSV+12.0.wnd`
- `outputs/EOGR+2.0.wnd`
- `outputs/EDC+R.wnd`
- `outputs/NWP23.7.wnd`
- `outputs/EWM50.wnd`

## Batch Study Interpretation

In a batch OpenFAST study, you would normally keep the structural and controller model fixed and vary only the wind-file reference between runs.

For example:

- Run 1 uses `Filename_Uni = "outputs/ECD+R.wnd"`
- Run 2 uses `Filename_Uni = "outputs/EWSV+12.0.wnd"`
- Run 3 uses `Filename_Uni = "outputs/EWM50.wnd"`

That is the practical bridge between one `pyIECWind` case-definition file and a family of OpenFAST simulations.

## Why This Is Useful

This workflow gives you:

- one human-readable source file for a study
- multiple deterministic `.wnd` outputs
- filenames that preserve the IEC case identity
- a clean bridge from IEC case definition to OpenFAST batch execution

## Variations

A few common extensions of this workflow are:

- adding multiple `NWP` wind speeds in one file, such as `[10.0, 14.0, 23.7]`
- adding both `EWM50` and `EWM01`
- creating separate `.ipt` files for parked, operating, and verification studies

## Related Documentation

- [`../examples/sample_case.ipt`](../examples/sample_case.ipt)
- [`USER_GUIDE.md`](USER_GUIDE.md)
- [`INPUT_FORMAT.md`](INPUT_FORMAT.md)
- [`CASE_REFERENCE.md`](CASE_REFERENCE.md)
