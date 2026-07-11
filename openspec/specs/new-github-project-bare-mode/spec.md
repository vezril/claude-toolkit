# new-github-project-bare-mode Specification

## Purpose
TBD - created by archiving change decompose-scala-scaffold. Update Purpose after archive.
## Requirements
### Requirement: docs and ship flags

The `new-github-project` workflow SHALL accept optional boolean args `docs` and `ship`, both defaulting to `true`, where `docs:false` skips the starter-docs phase and `ship:false` skips the commit/PR/merge phase. Existing invocations without the flags SHALL behave exactly as before.

#### Scenario: Bare mode

- **WHEN** invoked with `{name, visibility, docs:false, ship:false}`
- **THEN** only repo creation (seeded, protected `main`) runs
- **AND** the workflow returns synchronously with `status: complete` and no PR fields

#### Scenario: Defaults unchanged

- **WHEN** invoked with only `{name, visibility}`
- **THEN** all four phases run and non-auto mode still returns `awaiting-merge-approval`

#### Scenario: Ship without docs is rejected as pointless

- **WHEN** invoked with `{docs:false, ship:true}`
- **THEN** the workflow fails fast with a clear error (there would be nothing to ship)

### Requirement: OpenSpec configuration at bootstrap

The workflow SHALL initialize the OpenSpec configuration for Claude Code (`openspec init --tools claude`) in every bootstrapped repo — bare mode included — leaving the generated files uncommitted so they ride the next ship step (the docs PR in full mode, the flavor's scaffold PR in bare mode). A missing openspec CLI SHALL be a completed-with-warning skip, not a failure. (Added by the human on 2026-07-11, superseding the earlier drop-list decision to leave OpenSpec init to each project.)

#### Scenario: Bare mode carries OpenSpec into the flavor PR

- **WHEN** a flavor workflow bootstraps via bare mode and ships its scaffold
- **THEN** the scaffold PR contains `openspec/` and the `.claude/` opsx commands/skills

#### Scenario: CLI absent

- **WHEN** the openspec CLI is not on PATH
- **THEN** the step reports skipped with a reason, a WARNING is logged, and the workflow continues

### Requirement: Protection degrades gracefully under plan restrictions

When GitHub rejects branch protection with the plan-restriction 403 (private repository on the free plan), the workflow SHALL continue with a loud warning instead of failing: the result's protection object carries `unavailable: true` and the reason, and the human is told the repo is unprotected (PR discipline by convention only). The workflow SHALL NOT change repo visibility on its own initiative. (Discovered in the live run of 2026-07-11; decided by the human: degrade gracefully.)

#### Scenario: Private repo on the free plan

- **GIVEN** the account is on the GitHub free plan
- **WHEN** the workflow bootstraps a `private` repo
- **THEN** repo creation succeeds, the protection step reports `unavailable: true` with the plan reason, a WARNING is logged, and subsequent phases run normally

