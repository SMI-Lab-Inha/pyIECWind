Scope and limitations
======================

``pyIECWind`` deliberately implements a focused subset of IEC 61400-1. This page
states what is and is not supported so results are not over-interpreted.

Supported
---------

* **Standard:** IEC 61400-1 Editions 1 and 3, via the ``iec_edition`` field,
  which selects the normal power-law shear exponent (0.2 or 0.14).
* **Condition families:** the six classical IECWind-style cases - ECD, EWS, EOG,
  EDC, NWP, and EWM (see :doc:`theory`).
* **Turbine classes:** I, II, III.
* **Turbulence categories:** A, B, C.
* **Unit systems:** SI and English (see :doc:`units`).
* **Inflow inclination:** up to 8 degrees (larger values are accepted with an
  :class:`~pyiecwind.IECWindWarning`).

Not supported
-------------

The following are intentionally out of scope and are rejected (or accepted only
under an explicit legacy flag):

* **IEC 61400-1 Edition 2** and any other edition number. Unsupported editions
  raise unless ``parse_input_file(..., legacy=True)`` is passed, in which case
  they are coerced to Edition 3 with a warning.
* **Turbine class S** (site-specific design) and custom reference speeds.
* **Site-specific or measured turbulence**; only the standard normal turbulence
  model is used.
* **Speed modifiers on the cut-in (I) and cut-out (O) references.** A modifier is
  valid only on the rated (R) reference; ``EOGI+2.0`` and similar are rejected
  rather than silently producing a mislabelled file.
* **Newer or vendor-specific clauses** of IEC 61400-1 beyond the models above.

Other notes
-----------

* This package generates inflow files only; it does not run OpenFAST.
* The ``iec_edition`` field currently affects the power-law shear exponent
  selection; it is not a blanket claim of full edition compliance.
* Generated files are intended for the OpenFAST *InflowWind* module.
