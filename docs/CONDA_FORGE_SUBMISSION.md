# Conda-Forge Submission Guide

This guide is the next-step handoff for publishing `pyiecwind` on `conda-forge`.

## What You Already Have

This repository already contains a submission-ready starting recipe at:

```text
recipe/meta.yaml
```

The recipe is structured as:

- `noarch: python`
- `python >=3.10`
- `numpy >=1.24`
- CLI entry point: `pyiecwind`
- source archive pinned to GitHub tag `v0.1.0`
- SHA256 already computed

## Important Maintainer Check

The intended conda-forge maintainer for this package is Jae Hoon Seo.

Confirmed GitHub handle:

```text
SMI-Lab-Inha
```

The `recipe-maintainers` value in `recipe/meta.yaml` is now set accordingly.

Current value:

```yaml
extra:
  recipe-maintainers:
    - SMI-Lab-Inha
```

This satisfies conda-forge's expectation that `recipe-maintainers` contains a GitHub username rather than a plain display name.

## Submission Workflow

1. Fork `conda-forge/staged-recipes`
2. Create a branch from `main`
3. Create the directory:

```text
recipes/pyiecwind/
```

4. Copy this repository's `recipe/meta.yaml` into:

```text
recipes/pyiecwind/meta.yaml
```

5. Commit the new recipe
6. Open a PR to `conda-forge/staged-recipes`
7. Let CI and linting run
8. Address reviewer comments
9. After merge, wait for the `pyiecwind-feedstock` repository to be created

## Recommended Pre-Submission Checks

- Make sure the GitHub tag `v0.1.0` exists
- Make sure the source URL in `meta.yaml` resolves correctly
- Make sure the package license is still MIT
- Make sure the package version in `meta.yaml` matches `pyproject.toml`
- Make sure the CLI command `pyiecwind --help` still works

## Suggested PR Title

```text
Add pyiecwind
```

## Suggested PR Body

Use the text in [`recipe/STAGED_RECIPES_PR_BODY.md`](../recipe/STAGED_RECIPES_PR_BODY.md).

## After Feedstock Creation

Once the staged-recipes PR is merged:

- conda-forge creates the feedstock automatically
- future version bumps happen in the feedstock, not in `staged-recipes`
- the feedstock becomes the long-term home of the conda recipe
