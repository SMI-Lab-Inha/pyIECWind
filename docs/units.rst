Units
=====

``pyIECWind`` uses a single, explicit convention: **all internal computation is
in SI units (metres, m/s)**, and the unit system only affects how values are
read from input and rendered in output.

The ``si_unit`` flag
--------------------

The ``si_unit`` field of :class:`~pyiecwind.IECParameters` selects the *display*
and *input* unit system:

============  ==========================  ==========================
``si_unit``   Length                      Speed
============  ==========================  ==========================
``True``      metres (m)                  metres per second (m/s)
``False``     feet (ft)                   feet per second (ft/s)
============  ==========================  ==========================

Regardless of this flag, ``IECParameters`` stores ``hh``, ``dia``, ``vin``,
``vrated``, and ``vout`` in SI. The conversion factor between the two systems is
:math:`1~\text{m} = 3.2808~\text{ft}`.

Where the unit system applies
-----------------------------

The unit system affects three things:

#. **Input scaling.** When parsing English-unit input, length and speed fields
   are divided by 3.2808 to obtain the SI values stored on the object.
#. **Output rendering.** Length and speed columns and header lines in the
   ``.wnd`` file are multiplied back by the same factor so the file is expressed
   in the requested system.
#. **Condition-code speeds.** Speeds embedded in condition codes (the ``U`` in
   ``EWSV+U``, and the modifier in ``ECD+R+du``/``EOGR+du``/``EDC+R+du``) are
   interpreted in the selected user units.

Exceptions and conventions
--------------------------

* **NWP speeds are always in m/s.** The number in an ``NWP<speed>`` code is read
  as m/s irrespective of ``si_unit``, deliberately matching legacy IECWind. The
  rendered ``.wnd`` column is still shown in the file's unit system.
* **Angles** (``slope_deg``, direction changes) are always in degrees.
* **Time** (``t1``, the transient sampling) is always in seconds.
* **The power-law exponent** :math:`\alpha` is dimensionless.

Worked example
--------------

For ``NWP10.0`` with ``si_unit = False``, the steady hub speed is 10 m/s
internally; the wind-speed column is rendered as
:math:`10 \times 3.2808 = 32.808` ft/s. This relationship is asserted directly
in the test suite (see :doc:`validation`).
