# IECWind Python User Guide

## Table Of Contents

- [Overview](#overview)
- [What The Script Produces](#what-the-script-produces)
- [Supported IEC Condition Types](#supported-iec-condition-types)
- [Requirements](#requirements)
- [Basic Usage](#basic-usage)
- [Input File Formats](#input-file-formats)
- [Input Parameters](#input-parameters)
- [Derived Quantities Used In The Physics](#derived-quantities-used-in-the-physics)
- [Output File Format](#output-file-format)
- [Wind Condition Reference](#wind-condition-reference)
- [How Output Units Work](#how-output-units-work)
- [Practical Workflow](#practical-workflow)
- [Example Input Files](#example-input-files)
- [Common Errors And What They Mean](#common-errors-and-what-they-mean)
- [Important Implementation Notes](#important-implementation-notes)
- [Suggested Best Practices](#suggested-best-practices)
- [Minimal Example](#minimal-example)
- [Source Of Truth](#source-of-truth)

## Overview

`iec_wind.py` is a Python reimplementation and modernization of the legacy `IECwind.f90` utility. It generates IEC extreme wind condition files in AeroDyn `.wnd` format for use in wind turbine simulation workflows.

The script reads an input file, computes the requested IEC wind cases, and writes one `.wnd` file per condition code.

This implementation is based on the logic in:

- `iec_wind.py`
- `IECwind.f90`

The guide below is written to match the behavior of the current Python script as implemented in this directory.

## What The Script Produces

For each requested condition code, the script writes a file named:

```text
<condition>.wnd
```

Examples:

```text
EWSV+12.0.wnd
EWM50.wnd
NWP23.7.wnd
```

Each `.wnd` file contains:

- a descriptive comment header
- a column header section
- one or more rows of wind data in AeroDyn-compatible format

## Supported IEC Condition Types

The script currently supports:

- `ECD`: Extreme Coherent Gust with Direction Change
- `EWS`: Extreme Wind Shear
- `EOG`: Extreme Operating Gust
- `EDC`: Extreme Direction Change
- `NWP`: Normal Wind Profile
- `EWM`: Extreme Wind Model

## Requirements

### Python Dependency

The script requires:

- Python 3
- `numpy`

Install `numpy` with either:

```bash
pip install numpy
```

or

```bash
conda install numpy
```

### Files In This Directory

Key files in the current working directory:

- `iec_wind.py`: the Python implementation
- `IECwind.f90`: the legacy Fortran implementation
- `IEC.ipt`: the main input file
- generated `.wnd` files: one per condition

## Basic Usage

Run with the default input file:

```bash
python iec_wind.py
```

This reads:

```text
IEC.IPT
```

Run with a named input file:

```bash
python iec_wind.py my_case.ipt
```

Generate a commented template:

```bash
python iec_wind.py --template
```

Or write the template to a specific file:

```bash
python iec_wind.py --template my_template.ipt
```

Show help:

```bash
python iec_wind.py --help
```

## Input File Formats

The Python script supports two input styles:

- the original legacy fixed-line format used by `IECwind.f90`
- a newer key/value format that is easier to read and edit

Both formats are accepted by the same parser.

## Recommended Format: Key/Value Input

Example:

```text
! IECWind input file
si_unit = True
t1 = 40.0
wtc = 2
catg = B
slope_deg = 0.0
iec_edition = 3
hh = 80.0
dia = 80.0
vin = 4.0
vrated = 10.0
vout = 24.0

conditions:
  - ECD+R
  - ECD-R
  - EWSV+12.0
  - EWSH-12.0
  - EOGR+2.0
  - EDC+R
  - NWP23.7
  - EWM50
```

### Comments

The script ignores lines beginning with:

- `!`
- `#`

It also strips inline comments after `!` or `#`.

### Accepted Field Names

The parser accepts several aliases for convenience. The canonical keys are:

- `si_unit`
- `t1`
- `wtc`
- `catg`
- `slope_deg`
- `iec_edition`
- `hh`
- `dia`
- `vin`
- `vrated`
- `vout`
- `conditions`

It also accepts some alternate names such as:

- `units`
- `wind_turbine_class`
- `turbulence_category`
- `hub_height`
- `rotor_diameter`
- `cut_in_speed`
- `rated_speed`
- `cut_out_speed`
- `condition`

### Conditions Block

You can specify conditions in either of two ways.

Block style:

```text
conditions:
  - ECD+R
  - EWSV+12.0
  - EWM50
```

Repeated single-line style:

```text
condition = ECD+R
condition = EWSV+12.0
condition = EWM50
```

## Legacy Format

The old Fortran-style format is still supported. It relies on values appearing on expected line numbers and is less user-friendly, but existing input files do not need to be rewritten.

## Input Parameters

### `si_unit`

Controls the user unit system in the input file and output file.

- `True`: SI units are used for lengths and speeds
- `False`: English units are used for lengths and speeds

When `si_unit = False`:

- lengths are entered as `ft`
- speeds are entered as `ft/s`

Internally, the script converts everything to SI:

- lengths in `m`
- speeds in `m/s`

The conversion factor used by the script is:

```text
1 m = 3.2808 ft
```

### `t1`

The time, in seconds, at which the transient portion of the wind event begins.

Before `t1`, the script writes a steady initial row at `t = 0.0`.

Typical values:

- `30.0`
- `40.0`
- `60.0`

### `wtc`

Wind turbine class:

- `1`
- `2`
- `3`

This selects the IEC reference extreme wind speed:

```text
Class 1 -> Vref = 50.0 m/s
Class 2 -> Vref = 42.5 m/s
Class 3 -> Vref = 37.5 m/s
```

Derived values:

```text
Ve50 = 1.4 * Vref
Ve1  = 0.8 * Ve50
```

So:

```text
Class 1: Ve50 = 70.0 m/s, Ve1 = 56.0 m/s
Class 2: Ve50 = 59.5 m/s, Ve1 = 47.6 m/s
Class 3: Ve50 = 52.5 m/s, Ve1 = 42.0 m/s
```

### `catg`

Turbulence category:

- `A`
- `B`
- `C`

Mapped turbulence intensities:

```text
A -> Iref = 0.16
B -> Iref = 0.14
C -> Iref = 0.12
```

These are used in the longitudinal turbulence standard deviation:

$$
\sigma_1 = I_\text{ref} \left(0.75\, V_\text{hub} + 5.6\right)
$$

### `slope_deg`

Wind inflow inclination angle in degrees.

- positive: upward flow
- negative: downward flow

The script warns if:

```text
|slope_deg| > 8.0
```

Internally:

$$
\text{slope\_rad} = \text{radians}(\text{slope\_deg})
$$

The hub-height wind is split into horizontal and vertical components as:

$$
V_h = V_\text{hub} \cos(\gamma)
$$

$$
V_v = V_\text{hub} \sin(\gamma)
$$

where $\gamma = \text{slope\_rad}$.

### `iec_edition`

Controls the power-law vertical shear exponent `alpha` used for most conditions:

- `1` → `alpha = 0.20`
- `3` → `alpha = 0.14`

If another value is given, the script warns and defaults to Edition 3 behavior:

```text
alpha = 0.14
```

Important exception:

- `EWM` always uses `alpha = 0.11`

### `hh`

Hub height in the selected user units.

Internally converted to meters.

### `dia`

Rotor diameter in the selected user units.

Internally converted to meters.

Validation:

```text
dia > 0
hh > dia / 2
```

The second rule ensures the rotor does not intersect the ground.

### `vin`, `vrated`, `vout`

Operating wind speeds in the selected user units:

- `vin`: cut-in wind speed
- `vrated`: rated wind speed
- `vout`: cut-out wind speed

Validation:

```text
vin < vrated < vout
```

Internally they are stored in SI units.

## Derived Quantities Used In The Physics

The script computes several derived values from the input.

### Turbulence Length Scale

The turbulence length scale $\Lambda_1$ is:

$$
\Lambda_1 =
\begin{cases}
0.7\, HH & \text{if } HH < 60\ \text{m} \\
42.0      & \text{if } HH \ge 60\ \text{m}
\end{cases}
$$

In the code this is called `turb_scale`.

### Diameter-To-Scale Ratio

$$
\text{TurbRat} = \frac{D}{\Lambda_1}
$$

where $D$ is the rotor diameter. In the code this is `turb_rat`.

### Longitudinal Turbulence Standard Deviation

$$
\sigma_1 = I_\text{ref}\left(0.75\, V_\text{hub} + 5.6\right)
$$

This is implemented for each relevant wind case.

### Time Discretization

Transient cases use a fixed time step:

```text
DT = 0.1 s
```

If a transient has duration $T$, the script creates:

$$
N = \text{round}(T / DT) + 1
$$

time values:

$$
t = t_1 + \left[0,\ DT,\ 2DT,\ \dots\right]
$$

so that the transient begins at $t_1$ and extends to approximately $t_1 + T$.

## Output File Format

Each output row contains 8 columns:

1. `Time`
2. `WindSpeed`
3. `WindDir`
4. `VertSpeed`
5. `HorizShear`
6. `PwrLawVertShr`
7. `LinVertShear`
8. `GustSpeed`

The script writes them in tab-separated numeric format.

Interpretation:

1. `Time`: time in seconds
2. `WindSpeed`: mean horizontal wind speed component
3. `WindDir`: directional deviation in degrees
4. `VertSpeed`: vertical wind speed component
5. `HorizShear`: dimensionless horizontal shear term
6. `PwrLawVertShr`: power-law vertical shear exponent `alpha`
7. `LinVertShear`: dimensionless linear vertical shear term
8. `GustSpeed`: additive gust speed component

## Wind Condition Reference

### 1. `ECD`: Extreme Coherent Gust With Direction Change

#### Code Format

```text
ECD[+/-]R[+/-speed_modifier]
```

Examples:

```text
ECD+R
ECD-R
ECD+R+2.0
ECD-R-1.8
```

Meaning:

- `+` or `-`: sign of yaw excursion
- `R`: the base speed is `vrated`
- optional speed modifier: added to `vrated` in the selected user units

#### Constraints

The speed modifier must satisfy:

```text
|modifier| <= 2.0 m/s
```

or equivalently about:

```text
|modifier| <= 6.5 ft/s
```

The script also enforces:

```text
Vhub <= Vref
```

#### Transient Duration

```text
T = 10.0 s
```

#### Implemented Equations

The script uses:

$$
V_{cg}(t) = \frac{1}{2} V_{CG} \left(1 - \cos\left(\frac{\pi t}{T}\right)\right)
$$

with $V_{CG} = 15.0\ \text{m/s}$.

Direction change amplitude:

$$
\theta =
\begin{cases}
180^\circ                & \text{if } V_\text{hub} \le 4 \\
720  V_\text{hub}       & \text{if } V_\text{hub} > 4
\end{cases}
$$

Time-varying direction:

$$
\theta(t) = \frac{1}{2}\Theta \left(1 - \cos\left(\frac{\pi t}{T}\right)\right)
$$

The gust is projected into the output columns using the inflow angle:

$$
V_{\text{gust},h} = V_{cg} \cos(\gamma)
$$

$$
V_\text{vert} = \left(V_\text{hub} + V_{cg}\right) \sin(\gamma)
$$

#### Notes

- `ECD` writes one steady row at $t = 0$
- transient rows then begin at $t = t_1$
- the direction change is stored in the `WindDir` column
- the gust component is stored in `GustSpeed`

### 2. `EWS`: Extreme Wind Shear

#### Code Format

```text
EWS[V/H][+/-][speed]
```

Examples:

```text
EWSV+12.0
EWSV-12.0
EWSH+24.0
EWSH-12.0
```

Meaning:

- `V`: vertical shear
- `H`: horizontal shear
- `+` or `-`: sign of shear
- `speed`: hub-height wind speed in the selected input unit system

#### Constraints

The specified speed must satisfy:

```text
Vin <= Vhub <= Vout
```

#### Transient Duration

```text
T = 12.0 s
```

#### Implemented Equations

First:

$$
\sigma_1 = I_\text{ref}\left(0.75\, V_\text{hub} + 5.6\right)
$$

Then:

$$
V_{G50} = \beta\, \sigma_1
$$

with $$\beta = 6.4$$

Maximum shear magnitude:

$$
Shr_\text{max} = \frac{2\left(2.5 + 0.2\, V_{G50}\, \text{TurbRat}^{0.25}\right)}{V_\text{hub}}
$$

Time-varying shear:

$$
Shr(t) = \pm \frac{Shr_\text{max}}{2} \left(1 - \cos\left(\frac{2\pi t}{T}\right)\right)
$$

#### Output Mapping

For horizontal EWS:

- `HorizShear = Shr(t)`
- `LinVertShear = 0`

For vertical EWS:

- `HorizShear = 0`
- `LinVertShear = Shr(t)`

The power-law shear exponent column remains at the `iec_edition`-dependent value of `alpha`.

### 3. `EOG`: Extreme Operating Gust

#### Code Format

```text
EOG[I/O/R][+/-speed_modifier]
```

Examples:

```text
EOGI
EOGO
EOGR
EOGR+2.0
EOGR-2.0
```

Meaning:

- `I`: use `vin`
- `O`: use `vout`
- `R`: use `vrated`
- optional modifier on `R`: adjust `vrated`

#### Constraints

When using the optional rated-speed modifier:

```text
|modifier| <= 2.0 m/s
```

#### Transient Duration

```text
T = 10.5 s
```

#### Implemented Equations

First:

$$
\sigma_1 = I_\text{ref}\left(0.75\, V_\text{hub} + 5.6\right)
$$

Then the gust amplitude is:

$$
V_\text{gust} = \min\left(1.35\left(V_{e1} - V_\text{hub}\right),\ \frac{3.3\,\sigma_1}{1 + 0.1\,\text{TurbRat}}\right)
$$

The time history is implemented as:

$$
u(t) = V_\text{hub} - 0.37\, V_\text{gust} \sin\left(\frac{3\pi t}{T}\right)\left(1 - \cos\left(\frac{2\pi t}{T}\right)\right)
$$

In the code, the perturbation term is stored as:

$$
\Delta u(t) = -0.37\, V_\text{gust} \sin\left(\frac{3\pi t}{T}\right)\!\left(1 - \cos\left(\frac{2\pi t}{T}\right)\right)
$$

and then mapped to output as:

$$
V_{\text{gust},h} = \Delta u \cos(\gamma)
$$

$$
V_\text{vert} = \left(V_\text{hub} + \Delta u\right)\sin(\gamma)
$$

#### Notes

The header reports maximum gust speed using:

```text
2 * 0.37 * Vgust
```

and places the reported maximum at:

```text
t = t1 + 0.5 * T
```

This matches the current script behavior.

### 4. `EDC`: Extreme Direction Change

#### Code Format

```text
EDC[+/-][I/O/R][+/-speed_modifier]
```

Examples:

```text
EDC+I
EDC-I
EDC+O
EDC-R
EDC+R+2.0
EDC-R-2.0
```

Meaning:

- `+` or `-`: direction sign
- `I`: use `vin`
- `O`: use `vout`
- `R`: use `vrated`
- optional modifier on `R`

#### Constraints

When the rated-speed modifier is used:

```text
|modifier| <= 2.0 m/s
```

#### Transient Duration

```text
T = 6.0 s
```

#### Implemented Equations

First:

$$
\sigma_1 = I_\text{ref}\left(0.75\, V_\text{hub} + 5.6\right)
$$

Then the direction amplitude is:

$$
\theta = 4 \arctan\left(\frac{\sigma_1}{V_\text{hub}\left(1 + 0.1\,\text{TurbRat}\right)}\right)
$$

The code computes this in radians and converts to degrees:

$$
\theta_\text{deg} = \frac{180^\circ}{\pi}\,\theta
$$

with sign applied afterward.

The time-varying direction is:

$$
\theta(t) = \frac{1}{2}\,\theta_\text{deg} \left(1 - \cos\left(\frac{\pi t}{T}\right)\right)
$$

#### Output Mapping

- `WindDir = theta(t)`
- `GustSpeed = 0`
- `HorizShear = 0`
- `LinVertShear = 0`

### 5. `NWP`: Normal Wind Profile

#### Code Format

```text
NWP[speed]
```

Examples:

```text
NWP4.0
NWP10.0
NWP23.7
```

#### Important Unit Behavior

This is a special case.

The embedded speed in the condition code is always interpreted as m/s, even when `si_unit = False`. This is not a typo in this guide. It is the current implemented behavior and intentionally matches the original Fortran logic.

#### Output

`NWP` generates a single steady-state row with:

- steady wind speed
- no transient
- `alpha = p.alpha`

### 6. `EWM`: Extreme Wind Model

#### Code Format

```text
EWM50
EWM01
```

Meaning:

- `50`: use $V_{e50} = 1.4\, V_\text{ref}$
- `01`: use $V_{e1} = 0.8\, V_{e50}$

#### Output

`EWM` generates a single steady-state row with:

- no transient
- no gust term
- no direction change
- fixed shear exponent: `alpha = 0.11`

#### Implemented Equations

$$
V_{e50} = 1.4\, V_\text{ref}
$$

$$
V_{e1} = 0.8\, V_{e50}
$$

The selected value is used directly as the hub-height wind speed.

## How Output Units Work

Internally the script computes in SI units (metres, metres per second, radians for internal trigonometric operations).

When writing the `.wnd` file:

- speed-like outputs are multiplied by `len_convert`
- angular outputs remain in degrees
- shear terms remain dimensionless

Therefore:

- if `si_unit = True`, outputs are in m and m/s
- if `si_unit = False`, outputs are in ft and ft/s

Exception: the `NWP` speed embedded in the condition code is still interpreted in m/s.

## Practical Workflow

### Step 1: Create Or Edit An Input File

Use the template:

```bash
python iec_wind.py --template IEC_template.ipt
```

Then edit:

- turbine class
- turbulence category
- slope
- geometry
- operating speeds
- condition list

### Step 2: Run The Script

```bash
python iec_wind.py IEC_template.ipt
```

### Step 3: Check Console Summary

The script prints a summary like:

```text
WTC=2  CATG=B  Edition=3
HH=80.0 m  Dia=80.0 m
Vin=4.0  Vrated=10.0  Vout=24.0  [m/s]
TurbI=0.14  TurbScale=42.0 m  TurbRat=1.905
Vref=42.5  Ve50=59.5  Ve1=47.6  [m/s]
Alpha=0.14  Slope=0.0 deg
```

This is a quick check that the script interpreted your input the way you intended.

### Step 4: Inspect Generated Files

Each requested condition creates a `.wnd` file in the same directory.

## Example Input Files

### Example 1: Typical SI Case

```text
si_unit = True
t1 = 40.0
wtc = 2
catg = B
slope_deg = 0.0
iec_edition = 3
hh = 80.0
dia = 80.0
vin = 4.0
vrated = 10.0
vout = 24.0

conditions:
  - ECD+R
  - ECD-R
  - EWSV+12.0
  - EWSH+12.0
  - EOGI
  - EOGR+2.0
  - EDC+R
  - NWP23.7
  - EWM50
```

### Example 2: English Units

```text
si_unit = False
t1 = 40.0
wtc = 2
catg = B
slope_deg = 0.0
iec_edition = 3
hh = 262.47
dia = 262.47
vin = 13.12
vrated = 32.81
vout = 78.74

conditions:
  - ECD+R
  - EWSV+39.4
  - EOGR+6.5
  - EDC-R
  - EWM01
```

Note:

- all numeric fields above are in English units
- but `NWP` codes would still need their embedded speed in m/s

## Common Errors And What They Mean

### File Not Found

If the input file is missing, the script raises:

```text
Cannot find input file '...'
```

### Missing Conditions

If no conditions are provided:

```text
No wind conditions found in input file.
```

### Invalid Turbine Class

Allowed values: `1`, `2`, `3`.

### Invalid Turbulence Category

Allowed values: `A`, `B`, `C`.

### Invalid Geometry

Possible causes:

- `dia <= 0`
- `hh <= dia / 2`

### Invalid Wind Speed Ordering

Possible causes:

- `vrated <= vin`
- `vout <= vrated`

### Condition Parse Errors

The script validates condition code syntax and prints detailed parse errors, for example:

```text
Cannot parse EDC condition '...'
Expected format: EDC[+/-][I/O/R][±speed_modifier]
```

### Unknown Condition Prefix

If the first three letters are not recognized, the script skips that case:

```text
ERROR: Unknown condition type 'XXX' in code 'XXX...'. Skipping.
```

## Important Implementation Notes

These points are especially important if you are comparing results to other IEC tools or to the original Fortran program.

### 1. Internal Units Are Always SI

Even if the input is provided in English units, the script converts values to SI internally.

### 2. `NWP` Uses Speed In m/s Regardless Of `si_unit`

This is one of the easiest mistakes to make.

Example:

```text
NWP23.7
```

always means 23.7 m/s, not 23.7 ft/s.

### 3. `EWM` Uses Fixed `alpha = 0.11`

It does not use the `iec_edition` shear exponent.

### 4. `ECD`, `EOG`, And `EDC` Rated-Speed Modifiers Are Limited

The script enforces:

```text
|modifier| <= 2.0 m/s
```

### 5. `ECD` Also Enforces `Vhub <= Vref`

This is checked explicitly in the Python implementation.

## Suggested Best Practices

- Prefer the key/value input format for new work.
- Generate a fresh template with `--template` when starting a new case.
- Keep condition lists small while debugging.
- Check the printed summary before trusting the generated files.
- Be careful with `NWP` units.
- Use descriptive filenames for different turbine/site cases.

## Minimal Example

If you just want the smallest useful example:

```text
si_unit = True
t1 = 40.0
wtc = 2
catg = B
slope_deg = 0.0
iec_edition = 3
hh = 80.0
dia = 80.0
vin = 4.0
vrated = 10.0
vout = 24.0

conditions:
  - ECD+R
  - EWSV+12.0
  - EOGR
  - EDC+R
  - EWM50
```

Run:

```bash
python iec_wind.py
```

or:

```bash
python iec_wind.py IEC.ipt
```

## Source Of Truth

This guide is based on the current implementation in `iec_wind.py`. If you later modify equations, constants, parsing rules, or output formatting in the Python source, this guide should be updated to stay in sync.
