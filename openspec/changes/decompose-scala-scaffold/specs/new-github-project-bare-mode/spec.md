# new-github-project-bare-mode

## ADDED Requirements

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
