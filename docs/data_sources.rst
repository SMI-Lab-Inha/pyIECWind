Input file format (v1)
======================

``pyIECWind`` reads a single plain-text input file describing the turbine and the
conditions to generate. This page is the normative specification of that format,
**Input Format v1**. :func:`~pyiecwind.parse_input_file` implements it; anything
not described here is unsupported and may be rejected.

The format provides three interchangeable *layouts* that all produce the same
validated :class:`~pyiecwind.IECParameters`:

* **openfast-table-v1** -- one parameter per row, ``value  key  - comment``
  (recommended for new work; this is what the tool emits).
* **keyed-v1** -- ``key = value`` or ``key: value`` pairs.
* **legacy-v1** -- the historical fixed-line IECWind positional layout.

By default the layout is auto-detected. A file may pin its layout explicitly with
a format directive (see `Pinning the layout`_); doing so is recommended for
archival and review, and makes auto-detection a compatibility fallback rather
than the primary contract.

Lexical rules
-------------

These rules apply to the ``openfast-table-v1`` and ``keyed-v1`` layouts. The
``legacy-v1`` layout is positional and is described separately below.

Encoding and lines
~~~~~~~~~~~~~~~~~~~

* Files are UTF-8 text. Both ``\n`` and ``\r\n`` line endings are accepted.
* The file is processed line by line; line numbers in error messages are
  1-based and count every physical line, including blanks and comments.

Whitespace
~~~~~~~~~~

* Leading and trailing whitespace on a line is ignored.
* Blank lines are ignored anywhere.
* In ``openfast-table-v1`` rows, fields are separated by a run of **two or more**
  spaces. A single space is treated as part of a field, so column alignment is
  free-form as long as at least two spaces separate ``value``, ``key``, and the
  optional comment.
* In ``keyed-v1`` lines, whitespace around the ``=`` / ``:`` separator and around
  the value is ignored.

Comments
~~~~~~~~

* A line whose first non-whitespace character is ``!`` or ``#`` is a comment and
  is ignored (except for the directives below).
* In ``openfast-table-v1`` rows, a trailing ``- comment`` after the key is
  ignored. Everything from the first ``-`` that follows the key to end of line is
  commentary.

Pinning the layout
~~~~~~~~~~~~~~~~~~~

A comment line of the form::

   ! format: <id>

(equivalently ``# format = <id>`` or ``! format_version: <id>``; the keyword and
id are case-insensitive) pins the layout and overrides auto-detection. Recognised
ids are ``openfast-table-v1``, ``keyed-v1``, and ``legacy-v1`` (the short forms
``openfast``, ``keyed``, ``legacy`` are accepted as aliases). An unrecognised id
is an error. Files emitted by ``pyiecwind template`` and the wizard carry
``! format: openfast-table-v1`` so they are self-describing.

Scalar fields
-------------

Every input must define the eleven scalar fields below exactly once. Length and
speed fields are interpreted in the file's own unit system (see
`Unit semantics`_).

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
``turbine_class`` or ``turbine class`` for ``wtc``; ``rotor_diameter`` for
``dia``). Hyphens and spaces in a key are normalised to underscores.

Duplicate-field policy
~~~~~~~~~~~~~~~~~~~~~~~

Each scalar field may appear **at most once**. Defining a field twice -- directly
or through a different alias for the same field -- is rejected with both line
numbers, rather than silently keeping the last value. This catches typos such as
two conflicting ``wtc`` lines. (Condition rows are additive and are *not*
subject to this rule.)

Boolean and unit tokens
~~~~~~~~~~~~~~~~~~~~~~~~

``si_unit`` is parsed strictly. The following tokens are accepted
(case-insensitive); any other token is an error reported with line context:

* **SI / True:** ``True``, ``T``, ``.TRUE.``, ``yes``, ``y``, ``SI``,
  ``metric``, ``1``.
* **English / False:** ``False``, ``F``, ``.FALSE.``, ``no``, ``n``,
  ``English``, ``imperial``, ``us``, ``0``.

Unit semantics
--------------

``si_unit`` controls how length and speed fields are *read from* and *written to*
files; values are always stored internally in SI (m, m/s). With ``si_unit = True``
they are metres and m/s; with ``si_unit = False`` they are feet and ft/s. The
full unit model, including the conversion factor, is in :doc:`units`. Two rules
deserve emphasis because they are easy to get wrong:

* The speed embedded in an ``NWP<speed>`` code is **always in m/s**, regardless
  of ``si_unit`` -- this matches the historical IECWind convention.
* The EWS hub speed ``U`` and the ``du`` speed modifiers (ECD/EOG/EDC) are in the
  file's user units; a modifier's magnitude must not exceed 2 in those units.

Condition codes
---------------

Conditions are specified as *case rows* in ``openfast-table-v1`` or under a
``conditions:`` block in ``keyed-v1``. Each row expands into one or more
condition codes drawn from the grammar below. ``U`` denotes a wind speed in user
units and ``du`` a speed modifier (magnitude <= 2 in user units, valid only on
the rated ``R`` reference). The physics behind each family is in :doc:`theory`.

============  ==========================================  ==========================================
Family        Code grammar                                Example codes
============  ==========================================  ==========================================
ECD           ``ECD[+/-]R[[+/-]du]``                       ``ECD+R``, ``ECD-R+1.5``
EWS           ``EWS[V/H][+/-]U``                           ``EWSV+12.0``, ``EWSH-12.0``
EOG           ``EOG{I,O,R}[[+/-]du]`` (``du`` on R only)   ``EOGI``, ``EOGR+2.0``
EDC           ``EDC[+/-]{I,O,R}[[+/-]du]`` (``du`` on R)   ``EDC+R``, ``EDC-I``
NWP           ``NWP<speed_in_m_per_s>``                    ``NWP10.0``, ``NWP23.7``
EWM           ``EWM{50,01}``                               ``EWM50``, ``EWM01``
============  ==========================================  ==========================================

Codes outside this grammar -- a modifier above 2, a modifier on a non-rated
reference, an EWS speed outside ``[vin, vout]``, or a malformed code -- are
rejected (see :doc:`limitations`).

Case rows (openfast-table-v1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each case-family row is ``case_type  use_case  options_array``:

* ``use_case`` is ``True`` (generate the listed options), ``False`` (skip the
  row), or ``None`` (placeholder, ignored).
* ``options_array`` is a bracketed, comma-separated list expanded into individual
  condition codes (for example ``[+R, -R]`` becomes ``ECD+R`` and ``ECD-R``).

Layouts
-------

openfast-table-v1 (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ! format: openfast-table-v1

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

keyed-v1
~~~~~~~~

A simpler ``key = value`` (or ``key: value``) layout, with conditions under a
``conditions:`` block. Each ``- code`` line adds a condition; a code may be
prefixed with ``True``/``False``/``None`` to toggle it.

.. code-block:: text

   ! format: keyed-v1
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

legacy-v1
~~~~~~~~~

The historical fixed-line IECWind positional layout is still accepted for
backward compatibility. Field meaning is determined by line position rather than
by a key, so the lexical rules above do not apply. It is not recommended for new
files; prefer ``openfast-table-v1``.

Invalid files
-------------

The parser fails closed: a malformed file raises :class:`ValueError` with line
context rather than producing a partial or surprising result. Representative
examples and the errors they produce:

================================================  ==========================================================
Input fragment                                    Error
================================================  ==========================================================
``wtc = 2`` then ``wtc = 3``                      ``Duplicate field 'wtc' on line N; already set on line M``
``si_unit = maybe``                               ``Cannot interpret si_unit value 'maybe' on line N``
``mystery = 7``                                   ``Unknown input key on line N``
(omitting ``vout``)                               ``Missing required input field(s): vout``
``! format: bogus-v9``                            ``Unknown format directive 'bogus-v9'``
``EWS  True  [V+99.0]`` with ``vout = 24``        ``EWS wind speed ... must be between Vin ... and Vout``
================================================  ==========================================================

Format stability
----------------

This specification is **v1**. Backward-incompatible changes (new required fields,
changed grammar, or removed aliases) will be released under a new id
(``...-v2``) so that a pinned ``! format: ...-v1`` file keeps parsing as written.
Additive, backward-compatible refinements may be made within v1.
