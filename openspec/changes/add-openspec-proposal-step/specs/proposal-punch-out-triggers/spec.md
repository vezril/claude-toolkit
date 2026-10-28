## ADDED Requirements

### Requirement: The decision gate derives from the proposal's planned file paths
Triggers SHALL be derived from `proposal.json` by path matching and counting, never by text
matching. The derivations are enumerated in the scenarios below.

#### Scenario: Size derives proposal-scope

- **WHEN** the task count exceeds `punch_out.proposal_task_ceiling`, or the count of distinct files exceeds `punch_out.proposal_file_ceiling`
- **THEN** `proposal-scope` fires

#### Scenario: Planned paths derive the boundary triggers

- **WHEN** a planned file path falls under a `punch_out.contract_paths` entry
- **THEN** `proposal-breaking` fires; and when one falls under a `punch_out.protected_paths` entry, `protected-path` fires

#### Scenario: A declared dependency derives new-dependency

- **WHEN** `dependencies_added` is non-empty
- **THEN** `new-dependency` fires

#### Scenario: A protected path in the plan stops the flow before implementation

- **GIVEN** a proposal whose tasks touch a file under a configured protected path
- **THEN** the `protected-path` trigger fires and a punch-out is written

#### Scenario: Rewording cannot evade a path derivation

- **GIVEN** a proposal whose prose avoids every risk word while its tasks still touch a contract path
- **THEN** `proposal-breaking` fires on the path

#### Scenario: A dependency addition is a decision

- **GIVEN** `dependencies_added` lists one entry
- **THEN** `new-dependency` fires naming it

#### Scenario: A small routine change passes through

- **GIVEN** a proposal under both ceilings touching no contract or protected path and adding no dependency
- **THEN** no proposal trigger fires and the flow proceeds to implementation without a human

### Requirement: Proposal ceilings are configuration
`punch_out.proposal_task_ceiling` and `punch_out.proposal_file_ceiling` SHALL be keys in
`.delivery-flow.yaml` with documented defaults, applied when unset, and documented in
`skills/delivery-flow/references/config.md`.

#### Scenario: Defaults apply when unset

- **GIVEN** no proposal ceilings in the config
- **THEN** the documented defaults are used

### Requirement: Proposal triggers fire on leaving the brief
The proposal triggers SHALL be evaluated when the flow would advance from `brief` to
`implementation`, not when `proposal.json` is written. A punch-out raised before the brief exists
would ask a human to decide with nothing to read.

#### Scenario: The explanation precedes the decision

- **WHEN** a proposal fires a trigger
- **THEN** `summary.md` has already been rendered, and the punch-out is raised at the step after it

#### Scenario: Writing the proposal does not itself block

- **WHEN** `proposal.json` is written and passes its edge
- **THEN** the flow advances to `brief` without a punch-out, whatever the proposal contains

### Requirement: Claims and derivations compose as before
A proposal trigger SHALL fire on the derivation or on the node's corresponding claim in
`proposal.json`. Disagreement SHALL be recorded on the edge as `policy_disagreement` evidence and
SHALL NOT fail the edge, consistent with the triage-sourced triggers.

#### Scenario: A suppressed proposal claim does not skip the gate

- **GIVEN** `proposal.json` sets `breaking: false` while a task touches a contract path
- **THEN** `proposal-breaking` fires from the derivation and the disagreement is recorded

### Requirement: The planned paths are rechecked against the realized diff
Because a proposal's file list is a prediction, the existing `protected_paths` and
`contract_paths` checks against the realized diff SHALL continue to run at `verify`. A proposal
that plans one set of files and implements another SHALL be caught there.

#### Scenario: The implementation strays into a protected path

- **GIVEN** a proposal that named no protected path and an implementation whose diff touches one
- **THEN** the realized-diff check fires a `protected-path` punch-out at `verify`
