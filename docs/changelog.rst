Changelog
=========

The canonical, always-current changelog is ``CHANGELOG.md`` in the repository
root; the notable entries are reproduced here.

Unreleased
----------

Added
^^^^^

* ``__version__`` on the package, single-sourced from package metadata.
* Structured generation results (``GenerationResult``, ``GenerationError``) and a
  ``strict=`` mode on ``generate_all`` / ``generate_from_input_file``.
* ``IECWindWarning`` for advisory validation issues (escapable to errors).
* ``--continue-on-error`` on the ``run`` command; the CLI exits non-zero on failure.
* A golden ``.wnd`` corpus plus golden, property/invariant, and independent-oracle
  test suites locking numeric output.
* Hypothesis property tests and a dependency-free benchmark.
* reStructuredText documentation built with Sphinx (API reference, theory,
  validation, API contract, and more).
* Developer tooling (ruff, mypy ``--strict``, pytest-cov with a 90% gate),
  warnings-as-errors, and a cross-platform CI matrix with lint, type-check,
  coverage, wheel build/smoke, and docs build.

Changed
^^^^^^^

* Library code no longer prints; all user-facing output is owned by the CLI.
* ``generate_all`` / ``generate_from_input_file`` fail closed (``strict=True``).
* ``IECParameters`` is a frozen, self-validating dataclass with tuple conditions.
* License metadata modernised to the SPDX form (PEP 639).

Fixed
^^^^^

* Version drift between ``models.py`` and ``pyproject.toml``.
* EOG/EDC silently ignored speed modifiers on the cut-in/cut-out references; these
  are now rejected.
* Unsupported IEC editions were silently coerced; they now raise unless
  ``legacy=True``.
* Unknown ``si_unit`` tokens were treated as English units; they are now rejected.

0.1.0
-----

First public release: installable package, CLI (``run``, ``template``,
``wizard``), OpenFAST-style input format, and the ECD/EWS/EOG/EDC/NWP/EWM
condition families.
