API contract
============

This page defines what is public, how it behaves, and what callers may rely on
across releases. The reference listing is in :doc:`api`.

Public surface
--------------

Two modules are supported import facades:

``pyiecwind``
    The primary package namespace. Everything needed for normal use is importable
    from here: :class:`~pyiecwind.IECParameters`,
    :func:`~pyiecwind.parse_input_file`, :func:`~pyiecwind.generate_all`,
    :func:`~pyiecwind.generate_from_input_file`,
    :func:`~pyiecwind.write_template`,
    :func:`~pyiecwind.format_openfast_input`,
    :class:`~pyiecwind.GenerationResult`, :class:`~pyiecwind.GenerationError`,
    :class:`~pyiecwind.IECWindWarning`, the default filenames, and
    ``__version__``.

``pyiecwind.core``
    A compatibility facade that additionally exposes the individual condition
    generators (``gen_ecd``, ``gen_ews``, ``gen_eog``, ``gen_edc``, ``gen_nwp``,
    ``gen_ewm``) and the shared constants.

Every module declares an explicit ``__all__``. **Any name not listed in a
module's ``__all__`` - in particular underscore-prefixed helpers - is internal
and may change or disappear without notice.** Importing internals from their
defining modules is unsupported.

Versioning
----------

The project follows semantic versioning. ``__version__`` is single-sourced from
the installed package metadata, so the runtime value, ``pip show``, and the
distribution always agree; a test guards against drift. Breaking changes to the
public surface above will be accompanied by a major-version bump and a changelog
entry (:doc:`changelog`).

Behavioural guarantees
----------------------

Validated, immutable parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~pyiecwind.IECParameters` is a frozen dataclass that validates on
construction. Every public path - the parser, the wizard, and direct
construction - goes through the same validation, so an object that violates the
IEC class/category/edition, geometry, or speed-ordering rules cannot exist. The
``conditions`` field is stored as a tuple; instances cannot be mutated into an
invalid state afterwards.

Fail-closed generation
^^^^^^^^^^^^^^^^^^^^^^^^

:func:`~pyiecwind.generate_all` and
:func:`~pyiecwind.generate_from_input_file` default to ``strict=True``: the first
invalid condition raises :class:`ValueError`, so a caller never silently receives
partial output. Pass ``strict=False`` to collect failures into the returned
:class:`~pyiecwind.GenerationResult` instead (the CLI does this and chooses its
exit code from the result).

Condition grammar
^^^^^^^^^^^^^^^^^

Condition codes follow the grammar in :doc:`theory`. Speed modifiers are valid
only on the rated (``R``) reference; a modifier on cut-in (``I``) or cut-out
(``O``) is rejected rather than silently ignored.

Diagnostics
^^^^^^^^^^^

Library code does not print. Advisory, non-fatal validation issues are emitted as
:class:`~pyiecwind.IECWindWarning` and can be escalated to errors:

.. code-block:: python

   import warnings
   from pyiecwind import IECWindWarning

   warnings.simplefilter("error", IECWindWarning)

Hard errors are raised as :class:`ValueError` (or :class:`FileNotFoundError` for a
missing input file). Only the command-line interface writes to stdout/stderr and
selects a process exit code.

Module layout
-------------

For contributors, the internal organisation is single-responsibility:

==================  ============================================================
Module              Responsibility
==================  ============================================================
``models``          Constants, ``IECParameters``, ``IECWindWarning``, ``VERSION``.
``parsing``         Read and validate the three input layouts.
``generation``      The six generators, the writer, and the batch helpers.
``template``        Render parameters back to an input file / template.
``core``            Public compatibility facade (re-exports only).
``cli``             Argument parsing, the wizard, and all user-facing output.
``__main__``        The ``python -m pyiecwind`` entry point.
==================  ============================================================

Concurrency and thread-safety
-----------------------------

* ``IECParameters`` is immutable and safe to share across threads or processes
  without copying.
* Generation holds no global mutable state; each call builds its own writer.
  Generating different conditions, or the same conditions into different output
  directories, is safe to run concurrently.
* The one shared resource is the filesystem. Writing the **same** output path
  from multiple workers at once is **not** safe - give each worker a distinct
  ``output_dir``. The batch helpers already write one file per condition code.
