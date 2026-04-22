# Input Format

## Recommended Structure

The preferred input file is an OpenFAST-style text file with:

- one parameter per row
- aligned columns for readability
- a dedicated `Cases` section
- descriptive comments on every row

General row structure:

```text
value           key          - comment
```

Case row structure:

```text
case_type       use_case     options_array            - comment
```

## Example

```text
! General
True            si_unit      - True for SI (m, m/s), False for English (ft, ft/s)
40.000          t1           - transient start time [s]
2               wtc          - wind turbine class (1, 2, or 3)
B               catg         - turbulence category (A, B, or C)
0.000           slope_deg    - inflow inclination angle [deg]
3               iec_edition  - IEC edition for alpha (1 or 3)

! Turbine
80.000          hh           - hub height [m]
80.000          dia          - rotor diameter [m]

! Operating Speeds
4.000           vin          - cut-in wind speed [m/s]
10.000          vrated       - rated wind speed [m/s]
24.000          vout         - cut-out wind speed [m/s]

! Cases
ECD             True   [+R, -R]                  - Extreme Coherent Gust with Direction Change. Options: +R, -R, +R+du, +R-du, -R+du, -R-du
EWS             True   [V+12.0, H-12.0]          - Extreme Wind Shear. Options: V+U, V-U, H+U, H-U
NWP             True   [10.0, 23.7]              - Normal Wind Profile. Options: array of hub-height wind speeds in m/s
EWM             True   [50]                      - Extreme Wind Model. Options: 50 or 01, or an array such as [50, 01]
```

## Parameter Reference

`si_unit`

- `True`: SI units for general length and speed inputs
- `False`: English units for general length and speed inputs

`t1`

- time at which the transient event begins

`wtc`

- wind turbine class: `1`, `2`, or `3`

`catg`

- turbulence category: `A`, `B`, or `C`

`slope_deg`

- inflow inclination angle in degrees

`iec_edition`

- IEC edition controlling the normal power-law exponent
- currently `1` and `3` are supported

`hh`

- hub height

`dia`

- rotor diameter

`vin`

- cut-in wind speed

`vrated`

- rated wind speed

`vout`

- cut-out wind speed

## Case Rows

Each case-family row contains:

- the case type, such as `ECD`
- a `True`, `False`, or `None` flag
- an option array

Behavior:

- `True`: generate all listed options
- `False`: ignore the row
- `None`: placeholder row, ignored by the parser

## Legacy Compatibility

Older keyed and fixed-line input styles are still accepted for backward compatibility, but they are not the recommended interface for new users or public examples.
