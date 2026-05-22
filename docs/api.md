# API Reference

The public API is intentionally small. Everything below is importable directly
from the top-level `pyiecwind` package.

```{eval-rst}
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

Input and templates
--------------------

.. autofunction:: parse_input_file

.. autofunction:: write_template

.. autofunction:: format_openfast_input

Diagnostics
-----------

.. autoexception:: IECWindWarning
```
