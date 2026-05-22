# Verification

pyIECWind reproduces the wind-condition models of IEC 61400-1 as implemented by
the legacy NREL IECWind tool. This page is the maintainer-facing map from each
model to its implementation and to the golden references that lock its output.

## How output is locked

Every generator's numeric output is pinned by a committed corpus of reference
`.wnd` files under `tests/golden/`. `tests/test_golden.py` regenerates each case
and compares it to its golden file:

- comment/header lines are compared **exactly**, after masking the version stamp
  (which legitimately changes between releases);
- data rows are compared **column-by-column within ±5e-4**, half of the rendered
  three-decimal precision, which catches any displayed-digit change while
  tolerating signed-zero and last-bit rounding noise.

Structural and physical properties (transient durations, row counts, column
shape, the power-law exponent, unit scaling, direction-change endpoints) are
locked independently by `tests/test_invariants.py`.

To change output intentionally, regenerate and review the diff:

```console
$ PYIECWIND_UPDATE_GOLDEN=1 python -m pytest tests/test_golden.py
```

No formula change should land without a reviewed golden diff.

## Model map

Shared inputs follow IEC 61400-1: the reference turbulence intensity `Iref`
(A=0.16, B=0.14, C=0.12), the reference wind speed `Vref` by turbine class
(I=50, II=42.5, III=37.5 m/s), the turbulence scale `Λ = 0.7·z` for hub heights
below 60 m (otherwise 42 m), and the standard deviation `σ₁ = Iref·(0.75·Vhub + 5.6)`.

| Family | Model | Key relations | Implementation | Locked by |
| --- | --- | --- | --- | --- |
| NWP | Normal Wind Profile | steady hub speed; power-law exponent α by edition (Ed.1 = 0.2, Ed.3 = 0.14) | `gen_nwp` | `si_baseline`, `english_baseline`, `edition1`, `slope8` |
| EWM | Extreme Wind Model (steady) | `Ve50 = 1.4·Vref`, `Ve1 = 0.8·Ve50`; fixed shear exponent α = 0.11 | `gen_ewm` | all scenarios (50- and 1-year) |
| EOG | Extreme Operating Gust | `Vgust = min(1.35·(Ve1 − Vhub), 3.3·σ₁ / (1 + 0.1·D/Λ))`; 10.5 s transient | `gen_eog` | `si_baseline` (I/O/R ± du), others (R) |
| EDC | Extreme Direction Change | `θe = 4·arctan(σ₁ / (Vhub·(1 + 0.1·D/Λ)))`; 6 s cosine ramp | `gen_edc` | `si_baseline` (±I/O/R ± du), others |
| ECD | Extreme Coherent Gust with Direction Change | `Vcg = 15 m/s`; `θcg = 180°` for Vhub ≤ 4 m/s else `720°/Vhub`; 10 s cosine ramp | `gen_ecd` | `si_baseline` (±R ± du), others |
| EWS | Extreme Wind Shear | `Vg50 = 6.4·σ₁`; `shear = 2·(2.5 + 0.2·Vg50·(D/Λ)^0.25) / Vhub`; 12 s ramp | `gen_ews` | `si_baseline` (V/H ±), `english_baseline`, others |

Constants live in `pyiecwind.models` (`VCG`, `BETA`, `EWM_ALPHA`, `DT`, `VREF`,
`TURB_I`, `ALPHA_BY_EDITION`); the derived per-turbine quantities (`σ₁` inputs,
`turb_scale`, `turb_rat`, `vref`, `ve50`, `ve1`, `alpha`) are properties on
`IECParameters`.

## Scope

**Supported:** IEC 61400-1 Editions 1 and 3; turbine classes I–III; turbulence
categories A–C; SI and English unit systems; inflow inclination up to 8°.

**Not supported:** Edition 2 (warned, treated as Edition 3); turbine class S;
site-specific or measured turbulence; the EWS direction/horizontal coupling
beyond the single-axis transients above.
