# pyIECWind

`pyIECWind` is a modern Python package that generates IEC 61400-1 wind-condition
`.wnd` files for OpenFAST's InflowWind, reproducing the behaviour of the legacy
NREL IECWind tool with a typed API, validated inputs, and a reproducible CLI.

It supports the six standard condition families — ECD, EWS, EOG, EDC, NWP and
EWM — across both SI and English units and IEC 61400-1 Editions 1 and 3.

```{toctree}
:caption: User Guide
:maxdepth: 2

USER_GUIDE
INPUT_FORMAT
CASE_REFERENCE
STUDY_EXAMPLE
MIGRATION
```

```{toctree}
:caption: Reference
:maxdepth: 2

api
architecture
verification
changelog
```

```{toctree}
:caption: Maintainer
:maxdepth: 1

RELEASE_CHECKLIST
CONDA_FORGE_SUBMISSION
```

## Indices

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
