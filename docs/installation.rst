Installation
============

``pyIECWind`` requires Python 3.10 or newer and depends only on NumPy.

.. note::

   ``pyIECWind`` is not yet published on PyPI, so ``pip install pyiecwind`` is not
   available. Install from source, ideally inside a conda environment as shown
   below. A PyPI release and a ``conda-forge`` package are planned (see
   :doc:`deployment`).

Recommended: Miniconda (step by step)
-------------------------------------

If you are coming from an engineering background and do not already have a Python
workflow, this is the most reliable way to get started. It installs an isolated
environment so ``pyIECWind`` cannot interfere with any other Python on your
machine.

**1. Install Miniconda.** Download and run the installer for your operating system
from https://www.anaconda.com/docs/getting-started/miniconda/install. Miniconda is
a small distribution that provides ``conda`` (an environment and package manager)
and Python. On Windows, accept the defaults and then open the **Anaconda Prompt**;
on macOS/Linux, open a terminal.

**2. Get the code.** Clone the repository (or download the ZIP from GitHub and
extract it), then change into the folder:

.. code-block:: console

   git clone https://github.com/SMI-Lab-Inha/pyIECWind.git
   cd pyIECWind

**3. Create the environment.** This reads ``environment.yml`` and builds an
isolated environment named ``pyiecwind`` with the correct Python, NumPy, and
``pyIECWind`` itself:

.. code-block:: console

   conda env create -f environment.yml

**4. Activate it.** Do this in every new terminal session before using the tool:

.. code-block:: console

   conda activate pyiecwind

**5. Check it works:**

.. code-block:: console

   pyiecwind --help

You are ready -- continue with the :doc:`quickstart`.

Alternative installs
--------------------

If you already manage your own Python environments:

.. code-block:: console

   # into an existing conda environment
   conda create -n pyiecwind python=3.11 numpy pip -y
   conda activate pyiecwind
   python -m pip install -e .

   # or a plain pip install from a source checkout
   python -m pip install -e .

Optional dependency groups
--------------------------

Two extras are available for contributors:

``dev``
    Test and quality tooling: ``pytest``, ``pytest-cov``, ``hypothesis``,
    ``ruff``, ``mypy``, ``build``, ``twine``, and ``pip-audit``.

``docs``
    Documentation tooling: ``sphinx``, the ``sphinx-rtd-theme`` theme, and
    ``myst-parser``.

.. code-block:: console

   python -m pip install -e ".[dev]"
   python -m pip install -e ".[docs]"

Verifying the installation
--------------------------

.. code-block:: console

   pyiecwind --help
   python -c "import pyiecwind; print(pyiecwind.__version__)"

The version is single-sourced from the installed package metadata, so the import
above and ``pip show pyiecwind`` always agree.
