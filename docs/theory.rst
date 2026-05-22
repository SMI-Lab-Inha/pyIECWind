Theory
======

This page documents the mathematical model behind every generated wind file.
The equations follow IEC 61400-1 as implemented historically by *IECWind* (from
the National Laboratory of the Rockies, formerly NREL); each is paired with the
function that implements it (:doc:`api`) and is locked by the corpus and oracle
described in :doc:`validation`.

Common quantities
-----------------

All transient cases share a small set of standard IEC quantities. Symbols used
below:

.. list-table::
   :header-rows: 1
   :widths: 12 28 60

   * - Symbol
     - Name
     - Definition
   * - :math:`V_\mathrm{hub}`
     - Hub-height wind speed
     - Case-dependent reference speed (cut-in, rated, cut-out, or explicit).
   * - :math:`I_\mathrm{ref}`
     - Reference turbulence intensity
     - 0.16 (A), 0.14 (B), 0.12 (C).
   * - :math:`V_\mathrm{ref}`
     - Reference wind speed
     - 50 (class I), 42.5 (class II), 37.5 (class III) m/s.
   * - :math:`\Lambda_1`
     - Turbulence scale parameter
     - :math:`0.7\,z` for hub height :math:`z < 60` m, otherwise 42 m.
   * - :math:`\sigma_1`
     - Hub-height standard deviation
     - :math:`\sigma_1 = I_\mathrm{ref}\,(0.75\,V_\mathrm{hub} + 5.6)`.
   * - :math:`D`
     - Rotor diameter
     - Input ``dia``.
   * - :math:`\alpha`
     - Power-law shear exponent
     - 0.2 (Edition 1), 0.14 (Edition 3); 0.11 for EWM.

The standard deviation of the longitudinal turbulence is

.. math::

   \sigma_1 = I_\mathrm{ref}\,(0.75\,V_\mathrm{hub} + 5.6).

Transient cases are sampled at :math:`\Delta t = 0.1` s starting from the
transient start time :math:`t_1`. A leading steady row at :math:`t = 0` precedes
each transient, so a transient of duration :math:`T` yields
:math:`\lfloor T/\Delta t \rceil + 2` data rows.

Output columns
--------------

Each ``.wnd`` data row has eight columns: time, horizontal wind speed, wind
direction, vertical wind speed, horizontal linear shear, the power-law exponent
:math:`\alpha`, vertical linear shear, and gust speed. The hub-height speed is
decomposed by the inflow inclination angle :math:`\phi` (``slope_deg``):

.. math::

   V_h = V_\mathrm{hub}\cos\phi, \qquad V_v = V_\mathrm{hub}\sin\phi.

Normal Wind Profile (NWP)
-------------------------

A steady profile following the power law

.. math::

   V(z) = V_\mathrm{hub}\left(\frac{z}{z_\mathrm{hub}}\right)^{\alpha},

with :math:`\alpha` selected by ``iec_edition`` (0.2 for Edition 1, 0.14 for
Edition 3). The embedded speed in an ``NWP<speed>`` code is always in m/s,
matching legacy IECWind. Implemented by :func:`~pyiecwind.gen_nwp`.

Extreme Wind Model (EWM)
------------------------

The steady extreme wind speeds derive from the class reference speed:

.. math::

   V_\mathrm{e50} = 1.4\,V_\mathrm{ref}, \qquad V_\mathrm{e1} = 0.8\,V_\mathrm{e50}.

``EWM50`` uses :math:`V_\mathrm{e50}` (50-year recurrence) and ``EWM01`` uses
:math:`V_\mathrm{e1}` (1-year). A fixed shear exponent :math:`\alpha = 0.11` is
written regardless of edition. Implemented by :func:`~pyiecwind.gen_ewm`.

Extreme Operating Gust (EOG)
----------------------------

The gust magnitude is the smaller of a turbulence-driven and an extreme-wind
limit:

.. math::

   V_\mathrm{gust} = \min\!\left(
       1.35\,(V_\mathrm{e1} - V_\mathrm{hub}),\;
       \frac{3.3\,\sigma_1}{1 + 0.1\,D/\Lambda_1}
   \right).

Over the transient duration :math:`T = 10.5` s the hub speed follows

.. math::

   V(t) = V_\mathrm{hub} - 0.37\,V_\mathrm{gust}\,
          \sin\!\left(\frac{3\pi t}{T}\right)
          \left(1 - \cos\frac{2\pi t}{T}\right),
          \qquad 0 \le t \le T.

Implemented by :func:`~pyiecwind.gen_eog`.

Extreme Direction Change (EDC)
------------------------------

The extreme direction-change amplitude is

.. math::

   \theta_e = \pm 4\arctan\!\left(
       \frac{\sigma_1}{V_\mathrm{hub}\,(1 + 0.1\,D/\Lambda_1)}
   \right),

where the sign is taken from the code. The direction ramps over
:math:`T = 6` s with a half-cosine:

.. math::

   \theta(t) = \tfrac{1}{2}\,\theta_e\left(1 - \cos\frac{\pi t}{T}\right).

Implemented by :func:`~pyiecwind.gen_edc`.

Extreme Coherent Gust with Direction Change (ECD)
-------------------------------------------------

A coherent gust of fixed magnitude :math:`V_\mathrm{cg} = 15` m/s is applied
together with a direction change

.. math::

   \theta_\mathrm{cg} =
   \begin{cases}
     180^\circ & V_\mathrm{hub} \le 4~\mathrm{m/s} \\[4pt]
     \dfrac{720^\circ}{V_\mathrm{hub}} & V_\mathrm{hub} > 4~\mathrm{m/s}.
   \end{cases}

Over :math:`T = 10` s both the gust and the direction rise with a half-cosine:

.. math::

   V(t) = V_\mathrm{hub} + \tfrac{1}{2}\,V_\mathrm{cg}\left(1 - \cos\frac{\pi t}{T}\right),
   \qquad
   \theta(t) = \tfrac{1}{2}\,\theta_\mathrm{cg}\left(1 - \cos\frac{\pi t}{T}\right).

The hub speed is offset by the rated speed and an optional modifier
(:math:`\le 2` m/s in user units). Implemented by :func:`~pyiecwind.gen_ecd`.

Extreme Wind Shear (EWS)
------------------------

A transient linear shear (vertical or horizontal) is applied across the rotor.
With :math:`V_\mathrm{g50} = 6.4\,\sigma_1`, the peak shear is

.. math::

   s_\mathrm{max} = \frac{2\left(2.5 + 0.2\,V_\mathrm{g50}\,(D/\Lambda_1)^{0.25}\right)}{V_\mathrm{hub}},

ramped over :math:`T = 12` s with a full cosine cycle:

.. math::

   s(t) = \pm\,\tfrac{1}{2}\,s_\mathrm{max}\left(1 - \cos\frac{2\pi t}{T}\right).

The axis (``V``/``H``) selects whether :math:`s(t)` is written to the vertical or
horizontal linear-shear column, and the sign sets its direction. Implemented by
:func:`~pyiecwind.gen_ews`.

Traceability
------------

Each condition family maps to one implementing function, one independent oracle
check that recomputes its headline quantity from the equations on this page (see
:doc:`validation`), and one or more golden scenarios that lock its byte output.
The standard reference is IEC 61400-1, Clause 6 (wind conditions), for both
Edition 1 and Edition 3; the exact sub-clause and table numbering differs between
editions and is not reproduced here (consult the standard directly).

.. list-table::
   :header-rows: 1
   :widths: 10 26 18 26 22

   * - Family
     - Governing equation (this page)
     - Code
     - Independent oracle test
     - Golden scenarios
   * - NWP
     - Power-law profile; :math:`\alpha` per ``iec_edition``
     - :func:`~pyiecwind.gen_nwp`
     - ``test_oracle.test_nwp_steady_speed``
     - si_baseline, english_baseline, edition1, slope8
   * - EWM
     - :math:`V_\mathrm{e50}=1.4V_\mathrm{ref}`, :math:`V_\mathrm{e1}=0.8V_\mathrm{e50}`; fixed :math:`\alpha=0.11`
     - :func:`~pyiecwind.gen_ewm`
     - ``test_oracle.test_ewm_extreme_wind_speeds``
     - all six scenarios
   * - EOG
     - Gust amplitude :math:`V_\mathrm{gust}` over :math:`T=10.5` s
     - :func:`~pyiecwind.gen_eog`
     - ``test_oracle.test_eog_gust_amplitude``
     - si_baseline, english_baseline, edition1, class1_cat_a, class3_cat_c, slope8
   * - EDC
     - Direction amplitude :math:`\theta_e` over :math:`T=6` s
     - :func:`~pyiecwind.gen_edc`
     - ``test_oracle.test_edc_direction``
     - si_baseline, english_baseline, edition1, class1_cat_a, class3_cat_c, slope8
   * - ECD
     - :math:`V_\mathrm{cg}=15` m/s and :math:`\theta_\mathrm{cg}` over :math:`T=10` s
     - :func:`~pyiecwind.gen_ecd`
     - ``test_oracle.test_ecd_direction_and_gust``
     - si_baseline, english_baseline, edition1, class1_cat_a, class3_cat_c, slope8
   * - EWS
     - Peak shear :math:`s_\mathrm{max}` over :math:`T=12` s
     - :func:`~pyiecwind.gen_ews`
     - ``test_oracle.test_ews_shear``
     - si_baseline, english_baseline, edition1, class1_cat_a, class3_cat_c, slope8

Only the power-law shear exponent :math:`\alpha` depends on ``iec_edition``
(0.2 for Edition 1, 0.14 for Edition 3, and a fixed 0.11 for EWM); the transient
gust, shear, and direction-change magnitudes above are edition-independent in
this implementation.

Provenance and scope
--------------------

The equations above are implemented from the wind-condition definitions of
IEC 61400-1, Clause 6 (external conditions / wind conditions), as historically
realised by *IECWind*. They are **re-derived independently** in this package
rather than ported from the original source, and are cross-checked by the
analytical oracle described in :doc:`validation`. No copyrighted IEC standard text is
reproduced here; consult the standard itself for the normative definitions and
the precise clause numbering, which differs between editions. ``iec_edition``
selects only the normal power-law shear exponent (0.2 for Edition 1, 0.14 for
Edition 3); it is not a claim of full edition compliance (see :doc:`limitations`).

References
----------

* IEC 61400-1, *Wind turbines -- Part 1: Design requirements*, Clause 6 (Wind
  conditions), Editions 1 and 3. International Electrotechnical Commission.
* M. L. Buhl Jr., *IECWind*, National Laboratory of the Rockies
  (formerly the National Renewable Energy Laboratory).
  https://www.nlr.gov/wind/nwtc/iecwind
* OpenFAST *InflowWind* module documentation, National Laboratory of the Rockies
  (formerly the National Renewable Energy Laboratory).
  https://openfast.readthedocs.io/
