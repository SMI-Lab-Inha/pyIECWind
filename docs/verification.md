# Verification

pyIECWind implements the wind-condition models of IEC 61400-1 historically
provided by NREL's IECWind tool. This page is the maintainer-facing map from each
model to its implementation and to the references that lock its output.

## How output is locked

Output is protected by two independent layers:

1. **Golden regression corpus.** A committed set of reference `.wnd` files under
   `tests/golden/` pins the exact output of every generator. `tests/test_golden.py`
   regenerates each case and compares it to its golden file:

   - comment/header lines are compared **exactly**, after masking the version
     stamp (which legitimately changes between releases);
   - data rows are compared **column-by-column within $\pm 5 \times 10^{-4}$**,
     half of the rendered three-decimal precision, which catches any displayed
     digit change while tolerating signed-zero and last-bit rounding noise.

2. **Independent oracle.** Because the corpus is produced by the same code it
   guards, `tests/test_oracle.py` adds a second calculation path: each family's
   headline quantity is recomputed directly from the IEC 61400-1 equations, with
   the standard's reference values transcribed independently of the package, and
   compared against the generated output. A coding bug (wrong coefficient, sign,
   or unit) makes the oracle disagree even when the golden files still match.

Structural and physical properties (transient durations, row counts, column
shape, the power-law exponent, unit scaling, direction-change endpoints) are
locked separately by `tests/test_invariants.py`.

To change output intentionally, regenerate and review the diff:

```console
$ PYIECWIND_UPDATE_GOLDEN=1 python -m pytest tests/test_golden.py
```

No formula change should land without a reviewed golden diff.

## Model map

Shared inputs follow IEC 61400-1: the reference turbulence intensity $I_{ref}$
(A = 0.16, B = 0.14, C = 0.12), the reference wind speed $V_{ref}$ by turbine
class (I = 50, II = 42.5, III = 37.5 m/s), the turbulence scale
$\Lambda = 0.7\,z$ for hub heights $z < 60$ m (otherwise 42 m), and the standard
deviation $\sigma_1 = I_{ref}\,(0.75\,V_{hub} + 5.6)$.

| Family | Model | Key relations | Implementation | Locked by |
| --- | --- | --- | --- | --- |
| NWP | Normal Wind Profile | steady hub speed; power-law exponent $\alpha$ by edition (Ed.1 = 0.2, Ed.3 = 0.14) | `gen_nwp` | `si_baseline`, `english_baseline`, `edition1`, `slope8` |
| EWM | Extreme Wind Model (steady) | $V_{e50} = 1.4\,V_{ref}$, $V_{e1} = 0.8\,V_{e50}$; fixed shear exponent $\alpha = 0.11$ | `gen_ewm` | all scenarios (50- and 1-year) |
| EOG | Extreme Operating Gust | $V_{gust} = \min\!\left(1.35\,(V_{e1} - V_{hub}),\; 3.3\,\sigma_1 / (1 + 0.1\,D/\Lambda)\right)$; 10.5 s transient | `gen_eog` | `si_baseline` (I/O/R +/- du), others (R) |
| EDC | Extreme Direction Change | $\theta_e = 4\,\arctan\!\left(\sigma_1 / (V_{hub}\,(1 + 0.1\,D/\Lambda))\right)$; 6 s cosine ramp | `gen_edc` | `si_baseline` (+/- I/O/R +/- du), others |
| ECD | Extreme Coherent Gust with Direction Change | $V_{cg} = 15$ m/s; $\theta_{cg} = 180^\circ$ for $V_{hub} \le 4$ m/s else $720^\circ / V_{hub}$; 10 s cosine ramp | `gen_ecd` | `si_baseline` (+/- R +/- du), others |
| EWS | Extreme Wind Shear | $V_{g50} = 6.4\,\sigma_1$; $\text{shear} = 2\,(2.5 + 0.2\,V_{g50}\,(D/\Lambda)^{0.25}) / V_{hub}$; 12 s ramp | `gen_ews` | `si_baseline` (V/H +/-), `english_baseline`, others |

Constants live in `pyiecwind.models` (`VCG`, `BETA`, `EWM_ALPHA`, `DT`, `VREF`,
`TURB_I`, `ALPHA_BY_EDITION`); the derived per-turbine quantities are properties
on `IECParameters`.

## Scope

**Supported:** IEC 61400-1 Editions 1 and 3; turbine classes I-III; turbulence
categories A-C; SI and English unit systems; inflow inclination up to 8 deg.

**Not supported (rejected, or coerced only under explicit `legacy=True`):**
Edition 2 and other unsupported editions; turbine class S; site-specific or
measured turbulence; speed modifiers on the cut-in (I) and cut-out (O) references
(only the rated reference R accepts a modifier).
