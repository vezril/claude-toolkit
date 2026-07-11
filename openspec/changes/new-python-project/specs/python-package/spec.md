# python-package

## ADDED Requirements

### Requirement: Production sources only

The skill SHALL generate, via its bundled script, `src/<pkg>/__init__.py`, a pure `greeting.py` module (typed `message(name: str = "World") -> str`), and `__main__.py` (CLI entry printing the greeting) — and SHALL NOT create or edit anything under `tests/` or the build/CI/docs files.

#### Scenario: Package scaffold

- **GIVEN** python-uv-build has run for `athena-service`
- **WHEN** python-package runs
- **THEN** `src/athena/` contains `__init__.py`, `greeting.py`, `__main__.py` and `uv run python -m athena` prints the greeting
- **AND** nothing under `tests/` was touched

#### Scenario: Overwrite refusal

- **GIVEN** `src/<pkg>/` already exists
- **WHEN** the script runs
- **THEN** it refuses with a clear error
