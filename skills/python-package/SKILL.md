---
name: python-package
description: "Scaffold the PRODUCTION sources of a Python project into the current working tree: src/<pkg>/ with __init__.py, a pure typed greeting module, and __main__.py (the CLI entry point that python -m <pkg> and the Docker image run). Test-territory counterpart is python-tests; this skill never creates or edits anything under tests/. Run after python-uv-build in the new-python-project workflow."
argument-hint: "<project-name> [package-name]"
license: MIT
---

# Python package scaffold (production only)

Generate the production sources — deterministically, via the bundled script. This is the
GREEN-territory half of the scaffold pair: **production sources only, never tests** (the
implementer's file-territory rule, applied to scaffolding).

Bundled script: `scaffold.sh` in this skill's folder.

## Run

```
bash <skill-dir>/scaffold.sh <project-name> [package-name]
```

Same name/package contract as python-uv-build — pass identical values or the mypy/pytest
gate will catch the mismatch. Refuses to run if `src/<pkg>/` already exists.

What it writes:

- `src/<pkg>/__init__.py` — package docstring.
- `src/<pkg>/greeting.py` — pure, fully typed `message(name: str = "World") -> str`.
- `src/<pkg>/__main__.py` — `main()` printing the greeting; `python -m <pkg>` works and is
  the Docker image's CMD.

## Report

Files written and the package they landed in.

## Guardrails

- Territory is absolute: nothing under `tests/`, no build files, no docs, no CI.
- If a needed change belongs in a test, report it for python-tests instead of writing it.
- Never overwrite an existing package (the script refuses).
