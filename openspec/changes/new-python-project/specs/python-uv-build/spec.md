# python-uv-build

## ADDED Requirements

### Requirement: Deterministic uv build scaffold

The skill SHALL generate, via its bundled script: `pyproject.toml` (project metadata with static version 0.1.0, empty runtime dependencies, a dev dependency group with ruff/mypy/pytest, and `[tool.ruff]`/`[tool.mypy]`/`[tool.pytest.ini_options]` configuration), `.python-version` (3.12), `.gitignore`, and a multi-stage `Dockerfile` that runs `python -m <pkg>`. It SHALL NOT write `uv.lock` (generated at verify time), application sources, tests, README/LICENSE, or CI files.

#### Scenario: Scaffold the build

- **WHEN** invoked with project name `athena-service` in an empty working tree
- **THEN** pyproject.toml, .python-version, .gitignore, and Dockerfile exist and nothing else
- **AND** re-running refuses (pyproject.toml exists)

### Requirement: Package-name parameter with scala-consistent derivation

The skill SHALL derive the python package as the project name minus a `-service`/`-svc` suffix, hyphens converted to underscores, and SHALL accept an override parameter.

#### Scenario: Derivation and override

- **WHEN** invoked for `athena-service` with no override
- **THEN** the package is `athena`
- **WHEN** invoked with override `mytool`
- **THEN** the package is `mytool`

### Requirement: README enrichment

After repo-starter-docs has created the generic README, the skill SHALL replace the Getting-started TODO with uv usage (`uv sync`, `uv run pytest`, `uv run python -m <pkg>`, ruff/mypy commands), the Docker usage, and the CI/CD summary — preserving the description and license sections.

#### Scenario: Enrich, don't overwrite

- **GIVEN** README.md exists from repo-starter-docs
- **WHEN** enrichment runs
- **THEN** description and license sections survive and Getting-started content is present
