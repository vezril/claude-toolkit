# dockerhub-setup Specification

## Purpose
TBD - created by archiving change decompose-scala-scaffold. Update Purpose after archive.
## Requirements
### Requirement: End-to-end Docker Hub wiring

The skill SHALL, given a repo name: create the Docker Hub repository, mint a dedicated CI access token via the Hub API (label `<repo>-ci`), and set `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as GitHub Actions secrets on the matching GitHub repo.

#### Scenario: Full wiring

- **GIVEN** `DOCKERHUB_USERNAME` and an admin `DOCKERHUB_TOKEN` are in the environment
- **WHEN** dockerhub-setup runs for `athena-service`
- **THEN** hub repo `calvinference/athena` exists, a new `athena-ci` token exists, and both GitHub secrets are set to the CI token's credentials

### Requirement: Credential hygiene

The skill SHALL read admin credentials only from the environment, SHALL never echo any token value, and SHALL pipe secret values directly into `gh secret set`. Absent credentials → stop with setup instructions; never solicit a password in chat.

#### Scenario: No credentials

- **GIVEN** the env vars are unset
- **WHEN** the skill runs
- **THEN** it stops, explains which env vars are needed and how to create an admin PAT manually, and reports the step as skipped

### Requirement: Token-minting fallback

If minting the CI token fails (2FA, plan limits, API change), the skill SHALL fall back to setting the existing admin PAT as the secret and SHALL flag this loudly in its report (account-wide credential in CI).

#### Scenario: Minting fails

- **WHEN** `POST /v2/access-tokens` is rejected
- **THEN** secrets are still set (admin PAT), and the report states the fallback and the recommended manual remediation

