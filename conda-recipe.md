# Conda Installation

Create the recommended environment from the provided file:

```bash
conda env create -f environment.yml
conda run -n pyiecwind pyiecwind --help
```

If you prefer to create the environment manually:

```bash
conda create -n pyiecwind python=3.11 numpy pip -y
conda run -n pyiecwind python -m pip install -e .
```
