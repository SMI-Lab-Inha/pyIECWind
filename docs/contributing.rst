Contributing
============

Development setup
-----------------

.. code-block:: console

   $ git clone https://github.com/SMI-Lab-Inha/pyIECWind.git
   $ cd pyIECWind
   $ python -m pip install -e ".[dev,docs]"

Quality gates
-------------

The same checks CI enforces can be run locally. ``pytest`` is configured with the
source and test paths and the coverage gate, so no ``PYTHONPATH`` is needed.

.. code-block:: console

   $ ruff check .              # lint
   $ ruff format --check .     # formatting
   $ mypy                      # type check (strict)
   $ pytest --cov=pyiecwind    # tests + 90% coverage gate, warnings as errors
   $ sphinx-build -W -b html docs docs/_build/html   # docs (warnings as errors)

Tests
-----

The suite combines several layers (see :doc:`validation`):

* unit tests for parsing, validation, generation, and the CLI;
* a golden ``.wnd`` regression corpus;
* an independent oracle that re-derives each model from the IEC equations;
* property-based tests (Hypothesis) and structural invariant tests.

If a change intentionally alters generated output, regenerate the golden corpus
and review the diff before committing:

.. code-block:: console

   $ PYIECWIND_UPDATE_GOLDEN=1 python -m pytest tests/test_golden.py

Benchmark
---------

A lightweight, dependency-free benchmark times generation over the full scenario
matrix:

.. code-block:: console

   $ python benchmarks/bench_generation.py            # human-readable
   $ python benchmarks/bench_generation.py 20 --json  # machine-readable baseline

**Threshold policy.** CI runs the benchmark as a *smoke* step: it must complete
without error (catching changes that break generation), but no wall-clock
threshold is gated, because shared CI runners are too noisy for a stable bound
that would not flap. Performance regressions are tracked *offline* instead: record
a JSON baseline on a fixed machine (``--json``) and compare a later run's
``per_file_us`` / ``best_ms`` against it, investigating regressions beyond roughly
20%. Promote this to an automated gate only on a dedicated, low-noise runner.

Conventions
-----------

* Every module declares an explicit ``__all__``; names not listed are internal
  (see :doc:`api_contract`).
* Library code does not print or hold global mutable state.
* Public API uses NumPy-style docstrings.
* Generated numeric output is locked; output-changing edits require a reviewed
  golden diff.
