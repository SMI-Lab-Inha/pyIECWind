# Case Reference

## Overview

`pyIECWind` supports the following IEC case families:

- `ECD`: Extreme Coherent Gust with Direction Change
- `EWS`: Extreme Wind Shear
- `EOG`: Extreme Operating Gust
- `EDC`: Extreme Direction Change
- `NWP`: Normal Wind Profile
- `EWM`: Extreme Wind Model

## ECD

Meaning:

- Extreme Coherent Gust with Direction Change

Options:

- `+R`
- `-R`
- `+R+du`
- `+R-du`
- `-R+du`
- `-R-du`

Notes:

- `R` refers to rated wind speed
- `du` is a user-unit modifier relative to rated speed

## EWS

Meaning:

- Extreme Wind Shear

Options:

- `V+U`
- `V-U`
- `H+U`
- `H-U`

Notes:

- `V` means vertical shear
- `H` means horizontal shear
- `U` is a hub-height wind speed in the selected user units

## EOG

Meaning:

- Extreme Operating Gust

Options:

- `I`
- `O`
- `R`
- `R+du`
- `R-du`

Notes:

- `I` means cut-in
- `O` means cut-out
- `R` means rated

## EDC

Meaning:

- Extreme Direction Change

Options:

- `+I`
- `-I`
- `+O`
- `-O`
- `+R`
- `-R`
- `+R+du`
- `-R-du`

Notes:

- sign indicates direction of the yaw excursion
- `I`, `O`, and `R` follow the same meaning as in `EOG`

## NWP

Meaning:

- Normal Wind Profile

Options:

- array of wind speeds such as `[4.0, 10.0, 23.7]`

Notes:

- `NWP` values are interpreted in `m/s`
- this behavior intentionally matches historical `IECWind`

## EWM

Meaning:

- Extreme Wind Model

Options:

- `50`
- `01`
- arrays such as `[50, 01]`

Notes:

- `50` means 50-year recurrence
- `01` means 1-year recurrence

## Practical Advice

- Start with a small set of cases while validating a workflow
- Keep comments in the input file explicit when sharing with collaborators
- Use separate output directories when running different design studies
