Quickstart
==========

This page walks through generating wind files from the command line and from the
Python API. It assumes ``pyIECWind`` is installed (see :doc:`installation`).

Command-line interface
----------------------

The ``pyiecwind`` command exposes three subcommands.

Generate from an input file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

   $ pyiecwind run examples/sample_case.ipt -o outputs

This reads an input file (see :doc:`data_sources`), validates it, and writes one
``.wnd`` file per active condition into ``outputs/``. With no file argument,
``pyiecwind run`` reads ``pyiecwind.ipt`` from the current directory. The command
exits non-zero if any condition fails to generate; pass ``--continue-on-error``
to override that.

Write a starter template
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

   $ pyiecwind template my_case.ipt

With no argument this writes ``pyiecwind_template.ipt``. Edit the values and case
rows, then run it.

Guided wizard
^^^^^^^^^^^^^

.. code-block:: console

   $ pyiecwind wizard -o outputs

The wizard prompts for each parameter and condition, then generates the files and
(optionally) saves a reproducible input file.

Python API
----------

The same workflow is available programmatically. The public API is small and
importable from the top-level package:

.. code-block:: python

   from pyiecwind import generate_from_input_file

   params, result = generate_from_input_file("examples/sample_case.ipt", output_dir="outputs")
   print(f"generated {result.count} files")

To build parameters directly instead of parsing a file:

.. code-block:: python

   from pyiecwind import IECParameters, generate_all

   params = IECParameters(
       si_unit=True, t1=40.0, wtc=2, catg="B", slope_deg=0.0, iec_edition=3,
       hh=80.0, dia=80.0, vin=4.0, vrated=10.0, vout=24.0,
       conditions=("ECD+R", "EWSV+12.0", "EWM50"),
   )
   result = generate_all(params, output_dir="outputs")

``IECParameters`` validates on construction and is immutable, so an invalid
turbine definition raises immediately rather than producing a misleading file.
By default :func:`~pyiecwind.generate_all` *fails closed* (``strict=True``) — the
first invalid condition raises. See :doc:`api_contract` for the full contract.

Next steps
----------

* :doc:`data_sources` — the input file formats and every field.
* :doc:`theory` — the IEC equations behind each case family.
* :doc:`api` — the full API reference.
