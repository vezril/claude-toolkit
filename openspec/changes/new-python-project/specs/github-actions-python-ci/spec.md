# github-actions-python-ci

## ADDED Requirements

### Requirement: Python CI/CD scaffold

The skill SHALL generate `.github/actions/setup-uv/` (SHA-pinned astral-sh/setup-uv, uv-managed Python from `.python-version`, cache keyed on `uv.lock`), `ci.yml` (on PRs to `development`/`main`: `ruff check`, `ruff format --check` as its own job, `mypy src`, `pytest` — all via `uv sync --locked` — plus a gitleaks scan), `dev.yml` (`:dev` + `:dev-<short-sha>` images from pushes to `development`), and `release.yml` (`vX.Y.Z` tag: tag-on-main ancestry check, semver image immutability, `:X.Y.Z` + `:latest`, GitHub Release). It writes only `.github/`.

#### Scenario: CI green on the scaffold PR

- **GIVEN** the full python scaffold (including the committed `uv.lock`) on a feature branch
- **WHEN** the PR is opened
- **THEN** lint, format, types, tests, and gitleaks all pass

### Requirement: Docker publishing degrades without secrets

dev.yml and release.yml SHALL skip (not fail) every image step when the `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets are absent, using the same env-indirection check as the scala CI; tests and the GitHub Release still run.

#### Scenario: dockerhub:false project

- **GIVEN** a repo without Docker Hub secrets
- **WHEN** dev.yml runs on a push to `development`
- **THEN** the test steps run, all image steps are skipped, and the workflow concludes green
