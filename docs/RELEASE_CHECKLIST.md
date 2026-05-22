# Release Checklist

## Package Readiness

- Confirm `README.md` reflects the current CLI and input format
- Confirm `pyproject.toml` metadata, URLs, and keywords are current
- Confirm the example input file runs successfully
- Confirm no local machine paths or usernames remain in tracked files

## Documentation

- Review `docs/USER_GUIDE.md`
- Review `docs/INPUT_FORMAT.md`
- Review `docs/CASE_REFERENCE.md`
- Review `docs/MIGRATION.md`
- Make sure public documentation consistently refers to OpenFAST `InflowWind`

## Validation

Run the same gates CI enforces (install the dev and docs extras first with
`python -m pip install -e ".[dev,docs]"`):

```bash
ruff check .                 # lint
ruff format --check .        # formatting
mypy                         # type check
pytest --cov=pyiecwind       # tests + 90% coverage gate (includes golden + oracle)
sphinx-build -W -b html docs docs/_build/html   # docs (warnings as errors)
python -m build              # sdist + wheel
twine check dist/*           # package metadata
```

Then smoke-test the built wheel in a clean environment:

```bash
python -m venv /tmp/wheel-env
/tmp/wheel-env/bin/python -m pip install dist/*.whl
/tmp/wheel-env/bin/python -c "import pyiecwind; print(pyiecwind.__version__)"
/tmp/wheel-env/bin/pyiecwind template /tmp/smoke.ipt
```

If golden output changes intentionally, regenerate and review the diff before
committing: `PYIECWIND_UPDATE_GOLDEN=1 pytest tests/test_golden.py`.

## Repository Hygiene

- Check `git status`
- Remove obsolete legacy files from the index if they reappear
- Confirm `.gitignore` excludes generated `.wnd` files and temporary test outputs
- Review the GitHub Actions workflow for current Python versions

## Before Tagging Or Publishing

- Decide whether the version number should be bumped
- Write a short release note summarizing changes
- Push tags and documentation together so the published state is consistent
