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

Run the full test suite:

```bash
PYTHONPATH=src:tests python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -v
```

## Repository Hygiene

- Check `git status`
- Remove obsolete legacy files from the index if they reappear
- Confirm `.gitignore` excludes generated `.wnd` files and temporary test outputs
- Review the GitHub Actions workflow for current Python versions

## Before Tagging Or Publishing

- Decide whether the version number should be bumped
- Write a short release note summarizing changes
- Push tags and documentation together so the published state is consistent
