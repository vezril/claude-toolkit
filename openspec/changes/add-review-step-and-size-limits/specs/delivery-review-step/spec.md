# Spec Delta

## Purpose

The reviewer node that reads a change's diff before a pull request is opened, dispatching the
specialists the roster already names for the story's work kind, and recording its findings as a
schema-backed artifact the PR description is obliged to address.

## ADDED Requirements

### Requirement: A diff is reviewed before a pull request is opened

The `full` profile SHALL run a `review` step after `challenge-implementation` and before
`pr-description`. `review.json` SHALL be the artifact routing keys on, and `open-pr` SHALL NOT
be reachable while `review.json` is absent or its edge is failing.

#### Scenario: the review step runs before the PR description
- **WHEN** `challenge-implementation` has produced a passing verdict and `review.json` does not exist
- **THEN** the flow reports `review` as the next step, not `pr-description`

#### Scenario: a missing review blocks the PR
- **WHEN** `review.json` is absent and an attempt is made to advance to `open-pr`
- **THEN** the flow refuses to advance and names the missing artifact

### Requirement: The reviewers come from the roster, not from the orchestrator's judgement

The reviewers dispatched SHALL be those the roster names for the story's work kind, resolved by
the existing roster resolution and de-duplicated. The orchestrator SHALL NOT choose reviewers,
and a work kind whose roster entry names no reviewer SHALL be an error rather than a silent
skip.

#### Scenario: the work kind selects the reviewers
- **WHEN** a story's work kind names two reviewers in the roster
- **THEN** both are dispatched, and `review.json` records which reviewed it

#### Scenario: a roster entry with no reviewer is an error
- **WHEN** a story resolves to a work kind whose roster entry has an empty reviewer list
- **THEN** the step fails with that stated cause, and does not record a review that nobody performed

### Requirement: The reviewer reads the code, not the reasoning that produced it

Each reviewer SHALL run in a fresh context and SHALL be handed the diff, the story or proposal
it implements, and `verify.json`. It SHALL NOT be handed `implementation.json`'s narrative or
the conversation that produced the change.

#### Scenario: the review is independent of the implementation's account of itself
- **WHEN** a reviewer is dispatched
- **THEN** its inputs are the diff, the story and the verify results, and nothing that argues the change is correct

### Requirement: This step is distinct from challenging the implementation

`review` SHALL assess the code. `challenge-implementation` SHALL continue to cross-examine the
implementation record. Neither SHALL be treated as satisfying the other, and both SHALL appear
in the routing table.

#### Scenario: a passing challenge does not substitute for a review
- **WHEN** `challenge-implementation.json` records SURVIVED and `review.json` is absent
- **THEN** the flow still requires `review` before `pr-description`

### Requirement: Review findings are carried forward, not dropped

Where a review records findings, they SHALL be surfaced through the same `carry_forward`
mechanism the breakdown challenge uses, and `pr-description` SHALL be obliged to address each
one. A finding SHALL NOT be discharged by the reviewer's own assertion that it was handled.

#### Scenario: findings reach the PR description
- **WHEN** `review.json` carries two findings
- **THEN** both are returned as `carry_forward` to the step that writes the PR description

#### Scenario: a blocking review does not advance on self-report
- **WHEN** a review's verdict requires its findings addressed and the diff has not changed since the review
- **THEN** the flow refuses to advance and requires a fresh review against the diff that now exists

### Requirement: The step ships uncertified and says so

`review` SHALL be listed in `allow_uncertified` until it carries a prompt-edd package. Every
trace record for the step SHALL carry `certified: false`, and runs including it SHALL be
excluded from any certified-only success rate.

#### Scenario: an uncertified review is recorded as such
- **WHEN** the review step runs under `allow_uncertified`
- **THEN** its trace records `certified: false` and the run is outside the certified-only rate

#### Scenario: the certified triage chain is unaffected
- **WHEN** the `triage` profile runs
- **THEN** no `review` step is routed and the certified-only rate for that profile is unchanged
