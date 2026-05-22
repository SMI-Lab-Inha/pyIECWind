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
matrix. It runs as a smoke step in CI (no wall-clock threshold is enforced — CI
runners are too noisy for a meaningful bound); use it locally to spot
regressions:

.. code-block:: console

   $ python benchmarks/bench_generation.py

Conventions
-----------

* Every module declares an explicit ``__all__``; names not listed are internal
  (see :doc:`api_contract`).
* Library code does not print or hold global mutable state.
* Public API uses NumPy-style docstrings.
* Generated numeric output is locked; output-changing edits require a reviewed
  golden diff.
