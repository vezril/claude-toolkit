# github-actions-scala-ci

## ADDED Requirements

### Requirement: CI/CD workflow scaffold

The skill SHALL generate `.github/workflows/ci.yml` (format check + compile + test on PRs and main), `dev.yml` and `release.yml` (image build/publish), and the shared setup-scala composite action, matching the constellation conventions.

#### Scenario: CI green on the scaffold PR

- **GIVEN** the full scaffold on a feature branch
- **WHEN** the PR is opened
- **THEN** ci.yml runs scalafmtCheckAll + compile + test and passes

### Requirement: Degrade gracefully without Docker Hub

The image-publishing jobs SHALL be skipped (not failed) when the `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets are absent, using the env-indirection pattern (secrets are not directly readable in `if:` conditions).

#### Scenario: dockerhub:false project

- **GIVEN** a repo with no Docker Hub secrets
- **WHEN** dev.yml runs on a push to development
- **THEN** build/test steps run, the publish job is skipped, and the workflow concludes green
