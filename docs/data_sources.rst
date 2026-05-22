Input files
===========

``pyIECWind`` reads a single plain-text input file describing the turbine and the
conditions to generate. Three layouts are auto-detected by
:func:`~pyiecwind.parse_input_file`; the **OpenFAST-style table** is recommended
for new work.

OpenFAST-style table (recommended)
----------------------------------

One parameter per row as ``value  key  - comment``, with a ``Cases`` section:

.. code-block:: text

   ! General
   True            si_unit      - True for SI (m, m/s), False for English (ft, ft/s)
   40.000          t1           - transient start time [s]
   2               wtc          - wind turbine class (1, 2, or 3)
   B               catg         - turbulence category (A, B, or C)
   0.000           slope_deg    - inflow inclination angle [deg]
   3               iec_edition  - IEC edition for alpha (1 or 3)

   ! Turbine
   150.000         hh           - hub height [m]
   240.000         dia          - rotor diameter [m]

   ! Operating Speeds
   4.000           vin          - cut-in wind speed [m/s]
   10.000          vrated       - rated wind speed [m/s]
   24.000          vout         - cut-out wind speed [m/s]

   ! Cases
   ECD             True   [+R, -R]          - options: +R, -R, +R+du, ...
   EWS             True   [V+12.0, H-12.0]  - options: V+U, V-U, H+U, H-U
   NWP             True   [10.0, 23.7]      - hub-height speeds in m/s
   EWM             True   [50]              - 50 or 01, or [50, 01]

A complete working example ships in ``examples/sample_case.ipt``.

Keyed layout
------------

A simpler ``key = value`` (or ``key: value``) layout, with conditions under a
``conditions:`` block:

.. code-block:: text

   si_unit = True
   t1 = 40.0
   wtc = 2
   catg = B
   slope_deg = 0.0
   iec_edition = 3
   hh = 80.0
   dia = 80.0
   vin = 4.0
   vrated = 10.0
   vout = 24.0
   conditions:
     - EWM50
     - NWP10.0

Legacy positional layout
------------------------

The historical fixed-line IECWind layout is still accepted for backward
compatibility. It is not recommended for new files.

Field reference
---------------

================  ====================================================  ===============
Field             Meaning                                               Allowed values
================  ====================================================  ===============
``si_unit``       Unit system (see :doc:`units`)                        boolean token
``t1``            Transient start time [s]                              finite float
``wtc``           Wind turbine class                                    1, 2, 3
``catg``          Turbulence category                                   A, B, C
``slope_deg``     Inflow inclination angle [deg]                        finite float
``iec_edition``   Edition for the shear exponent                        1, 3
``hh``            Hub height                                            > ``dia`` / 2
``dia``           Rotor diameter                                        > 0
``vin``           Cut-in wind speed                                     0 < ``vin``
``vrated``        Rated wind speed                                      > ``vin``
``vout``          Cut-out wind speed                                    > ``vrated``
================  ====================================================  ===============

Key names are case-insensitive and accept common aliases (for example
``turbine_class`` for ``wtc`` or ``rotor_diameter`` for ``dia``). Boolean tokens
are parsed strictly: ``True``/``False`` (and equivalents such as ``yes``/``no``,
``SI``/``English``) are accepted; any other token is rejected with line context.

Case rows
---------

Each case-family row is ``case_type  use_case  options_array``:

* ``use_case`` is ``True`` (generate the listed options), ``False`` (skip the
  row), or ``None`` (placeholder, ignored).
* ``options_array`` is a bracketed, comma-separated list expanded into individual
  condition codes (for example ``[+R, -R]`` becomes ``ECD+R`` and ``ECD-R``).

The available codes for each family are documented in :doc:`theory`; values
outside the supported grammar are rejected (see :doc:`limitations`).
