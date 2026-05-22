API reference
=============

The public API is intentionally small and is importable directly from the
top-level :mod:`pyiecwind` package. The stability guarantees for these names are
described in :doc:`api_contract`.

.. currentmodule:: pyiecwind

Parameters
----------

.. autoclass:: IECParameters
   :members:

Generation
----------

.. autofunction:: generate_all

.. autofunction:: generate_from_input_file

.. autoclass:: GenerationResult
   :members:

.. autoclass:: GenerationError
   :members:

Condition generators
--------------------

Each generator writes one ``.wnd`` file and returns its path. They are available
from the :mod:`pyiecwind.core` compatibility facade.

.. currentmodule:: pyiecwind.core

.. autofunction:: gen_ecd

.. autofunction:: gen_ews

.. autofunction:: gen_eog

.. autofunction:: gen_edc

.. autofunction:: gen_nwp

.. autofunction:: gen_ewm

Input and templates
--------------------

.. currentmodule:: pyiecwind

.. autofunction:: parse_input_file

.. autofunction:: write_template

.. autofunction:: format_openfast_input

Diagnostics
-----------

.. autoexception:: IECWindWarning
