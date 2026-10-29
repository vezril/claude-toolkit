## ADDED Requirements

### Requirement: A repo opts in with one command, not hand-authored YAML
`init-delivery-flow.py` SHALL generate `.delivery-flow.yaml` for a target repository, detecting
what it can from the repository and requiring input only for what cannot be detected. The
generated file SHALL be commented, SHALL pass `load_config`, and SHALL leave the repository a
valid delivery-flow repo that `flow-status.py` can route.

#### Scenario: A detected repo is initialized

- **WHEN** init runs in a git repository with a GitHub remote and a recognizable build file
- **THEN** it writes `.delivery-flow.yaml` naming the forge, the base branch, the tracker and the test command, and `flow-status.py` routes in that repo without further editing

#### Scenario: The result is immediately usable

- **WHEN** init has run
- **THEN** `load_config` parses the file and the configured profile resolves

### Requirement: Detection covers forge, base branch, tracker, test command and protected paths
Detection SHALL cover: the forge and base branch from the git remote; the tracker from the
remote, or Jira when a project key is supplied; the test command from the build files present;
and `protected_paths` restricted to paths that actually exist in the repository.

#### Scenario: The test command comes from the build files

- **WHEN** the repository contains `build.sbt`, or `pyproject.toml`, or `package.json` with a test script, or `Cargo.toml`, or `go.mod`, or `pom.xml`, or a Gradle build
- **THEN** the corresponding test command is written

#### Scenario: Protected paths are not invented

- **WHEN** the repository has no `charts/` directory
- **THEN** `charts` does not appear in `protected_paths`

#### Scenario: The base branch comes from the remote

- **WHEN** the remote's HEAD names a default branch
- **THEN** `forge.base` is that branch rather than an assumed `main`

### Requirement: Undetectable facts are asked for, never guessed
The Jira project key, whether the tracker is external, the signing-key path, and
`contract_paths` SHALL NOT be guessed. Init SHALL accept them as options, and where one is
absent it SHALL write the key with a comment stating that a human must decide it. Supplying a
Jira project key SHALL select the Jira tracker.

#### Scenario: A client's Jira is declared, not inferred

- **WHEN** init runs with a Jira project key and no external flag
- **THEN** `tracker.external` is written as `true` with a comment saying the cautious reading was assumed and must be confirmed

#### Scenario: Contract paths are left to a human

- **WHEN** init runs
- **THEN** `contract_paths` is written empty with a comment that only a human knows which paths are shared contracts

#### Scenario: Credentials are never written

- **WHEN** init runs for a Jira tracker
- **THEN** the file contains no credential, and the output names the environment variables the adapter reads

### Requirement: Init is additive and confined
Init SHALL refuse to overwrite an existing `.delivery-flow.yaml` unless `--force` is given, SHALL
support `--dry-run`, and SHALL refuse to write outside the target repository.

#### Scenario: An existing config is not clobbered

- **GIVEN** the repository already has `.delivery-flow.yaml`
- **THEN** init exits non-zero naming the file, and writes nothing

#### Scenario: Dry run writes nothing

- **WHEN** init runs with `--dry-run`
- **THEN** it prints the file it would write and creates nothing

#### Scenario: A target outside a git repository is refused

- **WHEN** the target directory is not a git repository
- **THEN** init exits non-zero rather than writing a config where no repo root exists
