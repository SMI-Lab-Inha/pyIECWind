# Migration From Legacy IECWind

## What Changes

`pyIECWind` is meant to replace script-centric or fixed-format `IECWind` usage with a package and CLI that are easier to install and automate.

Main differences:

- the package is installed with Python packaging tools instead of being run as a loose script
- the preferred input style is an OpenFAST-like table instead of a fixed-line text file
- documentation is organized around cases, workflows, and examples
- the output target is described explicitly as OpenFAST `InflowWind`

## What Stays Compatible

The package still supports:

- historical fixed-line input files
- keyed input files
- the legacy `NWP` convention of interpreting the embedded speed in `m/s`

## Recommended Migration Path

1. Take one known legacy case.
2. Re-express it using `pyiecwind template`.
3. Compare the generated `.wnd` outputs with your old workflow.
4. Move study automation to `pyiecwind run`.
5. Keep legacy examples only as validation artifacts, not as primary user-facing inputs.

## For Maintainers

If you are publishing this repository for outside users:

- keep public examples in the OpenFAST-style format
- avoid reintroducing top-level legacy files
- document compatibility behavior only where it helps migration
- present `pyIECWind` as the primary interface, not the historical script model
