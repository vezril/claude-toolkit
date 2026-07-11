---
name: python-tests
description: "Scaffold the TEST sources of a Python project into the current working tree: tests/test_greeting.py covering the default and named greeting cases with pytest. Production-territory counterpart is python-package; this skill never touches src/ and reads the real package name from the generated production sources rather than re-deriving it (fails with a clear error if src/ has no package yet). Run after python-package in the new-python-project workflow."
argument-hint: "<project-name>"
license: MIT
---

# Python tests scaffold (tests only)

Generate the scaffold's test suite — deterministically, via the bundled script. This is
the RED-territory half of the scaffold pair: **test sources only, never production** (the
test-writer's file-territory rule, applied to scaffolding).

Bundled script: `scaffold.sh` in this skill's folder.

## Run

```
bash <skill-dir>/scaffold.sh <project-name>
```

No package argument: the script finds the package under `src/` (first directory with an
`__init__.py`) — the production sources are the source of truth. It fails with a clear
error naming python-package as the prerequisite if `src/` is empty, and refuses to run if
`tests/` already exists.

What it writes:

- `tests/test_greeting.py` — default greeting and named greeting cases, typed test
  functions (mypy-strict friendly).

## Report

Files written and the package they were read against.

## Guardrails

- Territory is absolute: nothing under `src/`, no build files, no docs, no CI.
- If a test reveals a production bug, report it for python-package — don't fix it here.
- Never overwrite an existing `tests/` (the script refuses).
