## Checklist

- [x] I have added a new recipe under `recipes/pyiecwind`
- [x] The recipe builds a pure Python package as `noarch: python`
- [x] The source URL is pinned to a GitHub release tag
- [x] The SHA256 hash has been computed and included
- [x] The package license file is included upstream
- [x] The recipe includes basic import and CLI tests

## Package Summary

`pyiecwind` is a modern Python package for legacy IECWind-style IEC wind-condition generation for the OpenFAST `InflowWind` module.

It provides:

- an installable Python package
- a command-line interface
- OpenFAST-style text input files
- support for classic IECWind-style cases including `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and `EWM`

## Notes For Reviewers

- The package is pure Python and is intended to build as `noarch: python`
- The runtime dependency surface is intentionally small: `python` and `numpy`
- The package includes a console entry point `pyiecwind`
- The current upstream release is `v0.1.0`
