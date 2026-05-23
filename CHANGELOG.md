# Changelog

All notable changes to `pyIECWind` will be documented in this file.

The format is inspired by Keep a Changelog, adapted to the needs of this project.

## [0.2.1] - 2026-05-23

### Added

- A version-consistency guard: the test suite now fails if `CITATION.cff`'s
  `version` drifts from the installed package version, and checks that its
  `date-released` is a valid ISO (`YYYY-MM-DD`) date. The citation metadata is
  hand-maintained, so this prevents it from silently falling behind a release.

## [0.2.0] - 2026-05-22

Input-contract and CLI hardening. No changes to the numeric `.wnd` output of any
valid case. Note the changed CLI default below: `pyiecwind run` now fails closed.

### Added

- Atomic generation: `generate_all(..., atomic=True)` (and the matching
  `generate_from_input_file(..., atomic=True)`) stage every file in a temporary
  directory and only commit them once the whole batch has been generated, so a
  mid-batch failure under `strict=True` leaves no partial output behind.
- Optional `! format: <id>` input directive (`openfast-table-v1`, `keyed-v1`,
  `legacy-v1`) that pins the layout and overrides auto-detection; auto-detection
  is now the documented compatibility fallback. Emitted files (template, wizard)
  carry the directive so they are self-describing.
- A formal **Input Format v1** specification in the documentation (lexical rules,
  duplicate-field policy, condition-code grammar, unit semantics, and
  invalid-file examples), and a per-family traceability table in the theory page
  mapping each equation to its code, oracle test, and golden scenarios.

### Changed

- The `run` command (and the no-argument default) now fail closed by default:
  an unparseable input or invalid condition aborts with a clean message and
  writes no files (atomic + strict). The existing `--continue-on-error` flag now
  selects the previous lenient behaviour (generate the valid conditions, skip and
  report the rest). The interactive wizard also fails closed.
- Input parsers reject a scalar field defined more than once (directly or via an
  alias), reporting both line numbers, instead of silently keeping the last
  value.
- Development status classifier moved from Alpha to Beta now that the input
  contract and release-package contents are settled.
- The golden corpus stores its version stamp in masked form (`pyIECWind vX`), so
  it is version-independent and no longer needs regenerating after a release bump.

### Fixed

- Input files are read with `utf-8-sig`, so a leading byte-order mark (common in
  files saved by Windows editors) no longer corrupts the first line.
- A repeated condition code (it maps to the same `.wnd` file) is now generated
  once instead of being staged twice, which previously broke `atomic=True` with a
  `FileNotFoundError` and left partial output behind.

## [0.1.2] - 2026-05-22

Packaging, release-process, and documentation fixes. No changes to generated
`.wnd` output.

### Added

- The source distribution now ships `CITATION.cff` and the `examples/` directory.
- The release workflow attaches the built sdist and wheel to the GitHub Release
  (alongside the build-provenance attestation).
- `pip-audit` is part of the `dev` extra so the dependency audit runs locally.

### Changed

- Documentation theme switched to `sphinx_rtd_theme` (Read the Docs theme).
- The documentation changelog is now generated from `CHANGELOG.md` (single source),
  and release-process docs use version-agnostic placeholders.
- The `Documentation` project URL points to Read the Docs.

## [0.1.1] - 2026-05-22

Documentation, provenance, and supply-chain hardening. No changes to generated
`.wnd` output.

### Added

- `CITATION.cff` and a Read the Docs build configuration.
- Provenance and citations (IEC 61400-1 Clause 6, NREL IECWind, OpenFAST
  InflowWind) and a per-scenario reproducibility matrix in the documentation.
- Machine-readable `--json` benchmark output with a documented threshold policy.
- Supply-chain hardening: Dependabot, a `pip-audit` dependency-audit CI job, and a
  release workflow with a build-provenance attestation and PyPI trusted publishing.

### Changed

- Documentation source is now pure ASCII (fixing em-dashes that rendered as
  mojibake) and enforced by the docs test; the README is rebuilt as an academic
  front door with a scope table, the tolerance policy, citations, and tempered
  IECWind-compatibility claims.
- Validation documentation is framed by evidential strength (golden regression vs
  independent analytical oracle vs property tests vs not-yet-done external
  comparison).
- Public-API docstrings gained `Notes` sections with standard references.

## [0.1.0] - 2026-05-22

First public release of `pyIECWind`: a typed, validated, and regression-locked
package for generating IEC 61400-1 wind-condition `.wnd` files for the OpenFAST
*InflowWind* module.

### Added

- Installable package (`src/pyiecwind`) with a `pyiecwind` CLI (`run`, `template`,
  `wizard`) and a `python -m pyiecwind` entry point.
- The six IEC condition families - `ECD`, `EWS`, `EOG`, `EDC`, `NWP`, and `EWM` -
  across SI and English units and IEC 61400-1 Editions 1 and 3.
- Three input layouts (OpenFAST-style table, keyed, and legacy positional) parsed
  into a frozen, self-validating `IECParameters`, plus an OpenFAST-style formatter
  and template writer.
- Structured generation results (`GenerationResult`, `GenerationError`) with a
  fail-closed `strict=` mode, `IECWindWarning` for advisory diagnostics, and a
  `--continue-on-error` CLI flag.
- `__version__` single-sourced from the installed package metadata.
- Verification: a committed golden `.wnd` corpus, an independent oracle derived
  from the IEC equations, and property/invariant tests (Hypothesis).
- reStructuredText documentation built with Sphinx (theory with equations, units,
  input files, API reference, API contract, validation, limitations, deployment),
  with a Read the Docs configuration.
- Tooling and CI: ruff, mypy `--strict`, pytest with a 90% coverage gate and
  warnings-as-errors, a cross-platform matrix (Linux/macOS/Windows x Python
  3.10-3.13), wheel build/smoke, a docs build, and a benchmark smoke step.
- A conda-forge-ready recipe and a self-contained sdist that ships the tests, the
  golden corpus, and the documentation source.

### Notes

- Library code never prints; all user-facing output and exit codes are owned by
  the CLI.
- Generation fails closed by default: the first invalid condition raises rather
  than producing partial output.
- Speed modifiers are valid only on the rated (`R`) reference; unsupported IEC
  editions and unknown unit tokens are rejected (legacy coercion is opt-in via
  `parse_input_file(..., legacy=True)`).
- This release supersedes an earlier internal `v0.1.0` tag; the published tag now
  points to this hardened source.
