Installation
============

``pyIECWind`` requires Python 3.10 or newer and depends only on NumPy.

From PyPI
---------

.. code-block:: console

   $ python -m pip install pyiecwind

From source
-----------

.. code-block:: console

   $ git clone https://github.com/SMI-Lab-Inha/pyIECWind.git
   $ cd pyIECWind
   $ python -m pip install -e .

Conda
-----

Create the provided environment:

.. code-block:: console

   $ conda env create -f environment.yml
   $ conda run -n pyiecwind pyiecwind --help

or install into an existing environment:

.. code-block:: console

   $ conda create -n pyiecwind python=3.11 numpy pip -y
   $ conda run -n pyiecwind python -m pip install -e .

A ``conda-forge`` package is planned; see :doc:`deployment`.

Optional dependency groups
--------------------------

Two extras are available for contributors:

``dev``
    Test and quality tooling: ``pytest``, ``pytest-cov``, ``hypothesis``,
    ``ruff``, ``mypy``, ``build``, and ``twine``.

``docs``
    Documentation tooling: ``sphinx`` and the ``furo`` theme.

.. code-block:: console

   $ python -m pip install -e ".[dev]"
   $ python -m pip install -e ".[docs]"

Verifying the installation
--------------------------

.. code-block:: console

   $ pyiecwind --help
   $ python -c "import pyiecwind; print(pyiecwind.__version__)"

The version is single-sourced from the installed package metadata, so the
import above and ``pip show pyiecwind`` always agree.
