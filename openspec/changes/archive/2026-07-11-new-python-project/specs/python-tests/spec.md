# python-tests

## ADDED Requirements

### Requirement: Test sources only, package read from src/

The skill SHALL generate, via its bundled script, `tests/test_greeting.py` (default greeting + named greeting cases) and SHALL NOT touch `src/` or any build/CI/docs file. It SHALL read the package name from the directory under `src/` rather than re-deriving it, and SHALL fail with a clear error if `src/` has no package yet.

#### Scenario: Tests scaffold and pass

- **GIVEN** python-uv-build and python-package have run
- **WHEN** python-tests runs and `uv run pytest` executes
- **THEN** all generated tests pass and no file under `src/` was modified

#### Scenario: Missing production package

- **GIVEN** `src/` contains no package
- **WHEN** the script runs
- **THEN** it stops with an error naming python-package as the prerequisite
