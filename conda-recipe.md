# Conda Notes

This repository now includes a real conda-forge style recipe at:

```text
recipe/meta.yaml
```

## Local Conda Environment

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

## Conda-Forge Submission

The `recipe/meta.yaml` file is intended as the starting point for a
`conda-forge/staged-recipes` submission.

Typical workflow:

1. Fork `conda-forge/staged-recipes`.
2. Create `recipes/pyiecwind/meta.yaml` there using this repository's recipe.
3. Open a PR and let conda-forge CI and linting run.
4. Address review comments.
5. Once merged, conda-forge will create the feedstock.

## Current Recipe Shape

The recipe is set up as:

- `noarch: python`
- `python >=3.10`
- runtime dependency on `numpy >=1.24`
- CLI entry point `pyiecwind`
- source archive based on the GitHub `v0.1.0` tag

## Maintainer Note

The recipe currently uses `SMI-Lab-Inha` under `recipe-maintainers`.
If conda-forge prefers an individual GitHub username instead of the
organization handle, replace it before submission.
