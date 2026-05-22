pyIECWind
=========

``pyIECWind`` generates IEC 61400-1 wind-condition ``.wnd`` files for the
OpenFAST *InflowWind* module. It implements the IEC 61400-1 wind-condition models
historically provided by the legacy *IECWind* tool from the National Laboratory of
the Rockies (formerly the National Renewable Energy Laboratory, NREL), behind a
typed, validated Python API, a reproducible command-line interface, and a
regression-locked test suite.

It implements the six classical condition families - ECD, EWS, EOG, EDC, NWP,
and EWM - across both SI and English unit systems and IEC 61400-1 Editions 1
and 3.

.. note::

   ``pyIECWind`` generates inflow files; it does not run OpenFAST. Internal
   calculations are performed in SI units (see :doc:`units`).

.. toctree::
   :caption: Getting started
   :maxdepth: 2

   installation
   quickstart

.. toctree::
   :caption: Reference
   :maxdepth: 2

   theory
   units
   data_sources
   api
   api_contract

.. toctree::
   :caption: Quality and scope
   :maxdepth: 2

   validation
   limitations

.. toctree::
   :caption: Project
   :maxdepth: 1

   contributing
   deployment
   release_checklist
   changelog

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
