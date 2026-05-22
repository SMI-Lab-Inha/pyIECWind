Changelog
=========

The canonical changelog is ``CHANGELOG.md`` in the repository root; the notable
entries are reproduced here.

0.1.0 - 2026-05-22
------------------

First public release of ``pyIECWind``: a typed, validated, and regression-locked
package for generating IEC 61400-1 wind-condition ``.wnd`` files for the OpenFAST
*InflowWind* module.

Added
^^^^^

* Installable package (``src/pyiecwind``) with a ``pyiecwind`` CLI (``run``,
  ``template``, ``wizard``) and a ``python -m pyiecwind`` entry point.
* The six IEC condition families -- ``ECD``, ``EWS``, ``EOG``, ``EDC``, ``NWP``,
  and ``EWM`` -- across SI and English units and IEC 61400-1 Editions 1 and 3.
* Three input layouts (OpenFAST-style table, keyed, and legacy positional) parsed
  into a frozen, self-validating ``IECParameters``, plus an OpenFAST-style
  formatter and template writer.
* Structured generation results (``GenerationResult``, ``GenerationError``) with a
  fail-closed ``strict=`` mode, ``IECWindWarning`` for advisory diagnostics, and a
  ``--continue-on-error`` CLI flag.
* ``__version__`` single-sourced from the installed package metadata.
* Verification: a committed golden ``.wnd`` corpus, an independent oracle derived
  from the IEC equations, and property/invariant tests (Hypothesis).
* reStructuredText documentation built with Sphinx, with a Read the Docs
  configuration.
* Tooling and CI: ruff, mypy ``--strict``, pytest with a 90% coverage gate and
  warnings-as-errors, a cross-platform matrix, wheel build/smoke, a docs build,
  and a benchmark smoke step.
* A conda-forge-ready recipe and a self-contained sdist.

Notes
^^^^^

* Library code never prints; all user-facing output and exit codes are owned by
  the CLI.
* Generation fails closed by default: the first invalid condition raises rather
  than producing partial output.
* Speed modifiers are valid only on the rated (``R``) reference; unsupported IEC
  editions and unknown unit tokens are rejected (legacy coercion is opt-in).
* This release supersedes an earlier internal ``v0.1.0`` tag.
