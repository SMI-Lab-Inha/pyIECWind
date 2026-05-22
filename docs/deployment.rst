Building and packaging
======================

This page covers building distributions and the planned conda-forge submission.
The end-to-end release procedure is in :doc:`release_checklist`.

Building distributions
----------------------

.. code-block:: console

   $ python -m pip install -e ".[dev]"
   $ python -m build           # writes sdist + wheel to dist/
   $ twine check dist/*        # validates package metadata

The build is warning-free, and the sdist is self-contained: it ships the complete
test suite, the golden corpus, and the documentation source, so the tests can be
run from an unpacked sdist.

Wheel smoke test
----------------

.. code-block:: console

   $ python -m venv /tmp/wheel-env
   $ /tmp/wheel-env/bin/python -m pip install dist/*.whl
   $ /tmp/wheel-env/bin/python -c "import pyiecwind; print(pyiecwind.__version__)"
   $ /tmp/wheel-env/bin/pyiecwind template /tmp/smoke.ipt

Conda-forge submission
----------------------

A ``conda-forge``-style recipe lives in ``recipe/meta.yaml``. It is configured as
``noarch: python`` with a runtime dependency on ``numpy >=1.24`` and the
``pyiecwind`` CLI entry point.

.. important::

   The ``sha256`` in ``recipe/meta.yaml`` is the hash of the tagged source
   archive and must be recomputed whenever the version tag changes, because the
   archive contents (and therefore the hash) are fixed only once the tag exists:

   .. code-block:: console

      $ curl -sL https://github.com/SMI-Lab-Inha/pyIECWind/archive/refs/tags/vX.Y.Z.tar.gz | sha256sum

   (substitute the release version for ``vX.Y.Z``). Update both
   ``recipe/meta.yaml`` and any documentation referencing the hash with the result
   on every release.

Submission workflow:

#. Confirm the GitHub tag (``vX.Y.Z``) exists and the source URL resolves.
#. Recompute and set the ``sha256`` as above.
#. Fork ``conda-forge/staged-recipes`` and add ``recipes/pyiecwind/meta.yaml``
   from this repository's recipe.
#. Open a PR (a suggested body is in ``recipe/STAGED_RECIPES_PR_BODY.md``) and let
   conda-forge CI and linting run.
#. After merge, conda-forge creates the ``pyiecwind-feedstock``; future version
   bumps happen there rather than in ``staged-recipes``.

The intended ``recipe-maintainers`` entry is the GitHub handle ``SMI-Lab-Inha``.
