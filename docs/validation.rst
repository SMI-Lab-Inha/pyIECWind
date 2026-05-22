Validation
==========

``pyIECWind`` implements the IEC 61400-1 wind-condition models historically
provided by NREL *IECWind*. Numeric output is protected by two independent
layers, backed by structural property tests.

Golden regression corpus
-------------------------

A committed set of reference ``.wnd`` files under ``tests/golden/`` pins the exact
output of every generator across a representative matrix: all six families, both
unit systems, IEC Editions 1 and 3, turbine classes I-III, turbulence categories
A-C, and a non-zero inflow inclination. ``tests/test_golden.py`` regenerates each
case and compares it:

* comment and header lines are compared **exactly**, after masking the version
  stamp (which legitimately changes between releases);
* data rows are compared **column-by-column within** :math:`\pm 5\times10^{-4}`,
  half of the rendered three-decimal precision, which catches any displayed-digit
  change while tolerating signed-zero and last-bit rounding.

To change output intentionally, regenerate the corpus and review the diff:

.. code-block:: console

   $ PYIECWIND_UPDATE_GOLDEN=1 python -m pytest tests/test_golden.py

No formula change should land without a reviewed golden diff.

Independent oracle
------------------

Because the corpus is produced by the same code it guards, ``tests/test_oracle.py``
adds a second, independent calculation path. Each family's headline quantity is
recomputed directly from the IEC equations in :doc:`theory` — with the standard's
reference values transcribed independently of the package — and compared against
the generated output. A coding error (a wrong coefficient, sign, or unit) makes
the oracle disagree even when the golden files still match themselves.

Property and invariant tests
----------------------------

``tests/test_invariants.py`` and ``tests/test_property.py`` lock structural and
physical properties independent of the exact numbers:

* transient durations and row counts;
* the eight-column row shape;
* the power-law exponent used (edition-dependent, or 0.11 for EWM);
* unit scaling between SI and English;
* direction-ramp monotonicity;
* rejection of unordered operating speeds and out-of-range conditions.

The property tests (Hypothesis) additionally verify the format/parse round-trip
and the condition-code grammar across a wide range of randomly generated but
always-valid turbine definitions.

Toolchain gates
---------------

Every change is checked by ``ruff`` (lint and formatting), ``mypy --strict``,
``pytest`` with a 90% coverage gate and warnings treated as errors, a
``sphinx-build -W`` documentation build, and a wheel/sdist build verified with
``twine``. See :doc:`contributing` and :doc:`release_checklist`.
