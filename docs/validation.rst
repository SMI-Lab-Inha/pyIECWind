Validation
==========

``pyIECWind`` implements the IEC 61400-1 wind-condition models historically
provided by NREL *IECWind*. Numeric output is protected by layers of **differing
evidential strength**, and it is important to be precise about what each one does
and does not establish:

#. **Golden regression** -- self-generated; detects *regressions*, not
   original-formulation errors.
#. **Independent analytical oracle** -- a second, hand-derived implementation of
   each model; detects coding errors in the generators.
#. **Property/invariant tests** -- structural and physical guarantees.
#. **External reference comparison** -- comparison against trusted external output
   (e.g. NREL *IECWind* binaries). *Not yet performed* (see below).

Golden regression corpus
-------------------------

A committed set of reference ``.wnd`` files under ``tests/golden/`` pins the exact
output of every generator across a representative matrix: all six families, both
unit systems, IEC Editions 1 and 3, turbine classes I-III, turbulence categories
A-C, and a non-zero inflow inclination.

.. note::

   The golden files are produced by this package, so they are a **regression**
   safeguard, not independent academic validation: they prove the output has not
   *changed*, not that it was correct to begin with. Independent correctness is
   the job of the oracle layer below.

``tests/test_golden.py`` regenerates each case and compares it:

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
recomputed directly from the IEC equations in :doc:`theory` - with the standard's
reference values transcribed independently of the package - and compared against
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

External reference validation (future work)
-------------------------------------------

The strongest layer -- a value-level comparison against output from NREL
*IECWind* or another trusted, independent implementation -- has **not** yet been
performed. Until it is, ``pyIECWind`` is described as *compatible with selected
legacy IECWind-style workflows* rather than as a verified byte-for-byte
reproduction. Contributions of legacy reference cases are welcome.

Reproducibility matrix
----------------------

The committed scenarios (``tests/golden_cases.py``) cover the dimensions below.
Every case is locked by the golden corpus and the property/invariant tests; the
families listed are additionally cross-checked by the analytical oracle for the
baseline scenarios. Data rows are compared within :math:`\pm 5\times10^{-4}`;
header lines exactly.

.. list-table::
   :header-rows: 1
   :widths: 20 8 8 10 8 34 8

   * - Scenario
     - Edition
     - Class
     - Category
     - Units
     - Families (output type)
     - Inflow
   * - ``si_baseline``
     - 3
     - II
     - B
     - SI
     - ECD, EWS, EOG, EDC (transient); NWP, EWM (steady)
     - 0 deg
   * - ``english_baseline``
     - 3
     - II
     - B
     - English
     - all six
     - 0 deg
   * - ``edition1``
     - 1
     - II
     - B
     - SI
     - all six
     - 0 deg
   * - ``class1_cat_a``
     - 3
     - I
     - A
     - SI
     - ECD, EWS, EOG, EDC, EWM
     - 0 deg
   * - ``class3_cat_c``
     - 3
     - III
     - C
     - SI
     - ECD, EWS, EOG, EDC, EWM
     - 0 deg
   * - ``slope8``
     - 3
     - II
     - B
     - SI
     - all six
     - 8 deg

Test sources: golden (``tests/test_golden.py``), oracle (``tests/test_oracle.py``),
invariants and properties (``tests/test_invariants.py``, ``tests/test_property.py``).

Toolchain gates
---------------

Every change is checked by ``ruff`` (lint and formatting), ``mypy --strict``,
``pytest`` with a 90% coverage gate and warnings treated as errors, a
``sphinx-build -W`` documentation build, and a wheel/sdist build verified with
``twine``. See :doc:`contributing` and :doc:`release_checklist`.
