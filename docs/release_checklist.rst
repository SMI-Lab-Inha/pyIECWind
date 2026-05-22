Release checklist
=================

Run through this list before tagging and publishing a release.

Package readiness
-----------------

* Confirm :doc:`README <index>` and the docs reflect the current CLI and input
  format.
* Confirm ``pyproject.toml`` metadata, URLs, and keywords are current.
* Confirm the version in ``recipe/meta.yaml`` matches ``pyproject.toml``.
* Confirm the example input file (``examples/sample_case.ipt``) runs.
* Confirm no local machine paths or usernames remain in tracked files.

Quality gates
-------------

Install the dev and docs extras (``python -m pip install -e ".[dev,docs]"``) and
run the full set:

.. code-block:: console

   $ ruff check .
   $ ruff format --check .
   $ mypy
   $ pytest --cov=pyiecwind
   $ sphinx-build -W -b html docs docs/_build/html
   $ python -m build
   $ twine check dist/*

Then smoke-test the built wheel in a clean environment (see :doc:`deployment`).

Tag and source archive
-----------------------

.. important::

   Do these in order — the conda ``sha256`` is only valid once the tag exists.

#. Update the changelog: move ``Unreleased`` entries under the new version and date.
#. Commit and merge to the default branch.
#. Tag and push:

   .. code-block:: console

      $ git tag -a v0.1.0 -m "pyIECWind 0.1.0"
      $ git push origin v0.1.0

#. Recompute the source archive hash and update ``recipe/meta.yaml``:

   .. code-block:: console

      $ curl -sL https://github.com/SMI-Lab-Inha/pyIECWind/archive/refs/tags/v0.1.0.tar.gz | sha256sum

#. Build and publish the distribution (PyPI), and proceed with the conda-forge
   submission in :doc:`deployment`.

Post-release
------------

* Verify ``pip install pyiecwind`` resolves the new version.
* Verify the source URL in ``recipe/meta.yaml`` resolves and its hash matches.
* Re-run this checklist if the tagged archive is re-cut for any reason.
