# Spec Delta

## Purpose

A bound on how large a single change may grow before a human decides whether it should be
split, measured from the diff that actually exists rather than from any node's description of
it.

## ADDED Requirements

### Requirement: A change's size is bounded by configured ceilings

The repository configuration SHALL carry `punch_out.max_diff_files` and
`punch_out.max_diff_lines`. Exceeding either SHALL raise a punch-out. The ceilings SHALL be
per-repository configuration, not plugin-level defaults, because what counts as a large change
differs by repository.

#### Scenario: a diff within both ceilings proceeds
- **WHEN** a change touches fewer files and fewer lines than the configured ceilings
- **THEN** no size punch-out is raised and the flow advances

#### Scenario: exceeding either ceiling raises a punch-out
- **WHEN** a change exceeds `max_diff_files` but stays inside `max_diff_lines`
- **THEN** a punch-out is raised naming the ceiling breached and the measured value

#### Scenario: an absent ceiling is not an unlimited one
- **WHEN** the configuration omits a size ceiling
- **THEN** the omission is reported rather than treated as permission for any size

### Requirement: The size is derived from the diff, never from a claim about it

The measurement SHALL be computed from the actual diff. It SHALL NOT read any field in which a
node describes the change's size or scope, so that rewording an artifact cannot clear the
trigger.

#### Scenario: a node cannot talk its way under the ceiling
- **WHEN** an artifact describes the change as small while the diff exceeds a ceiling
- **THEN** the punch-out is still raised, and the disagreement is recorded as evidence

#### Scenario: the measured value is recorded
- **WHEN** a size punch-out is raised
- **THEN** the measured file count and line count are recorded alongside the ceilings they breached

### Requirement: The punch-out fires where the diff first exists in full

The size check SHALL be evaluated at `verify`, the first point at which the complete diff for
the change exists. It SHALL be re-evaluated if the diff changes afterwards.

#### Scenario: the check runs once the change is complete
- **WHEN** the implementation is finished and verify runs
- **THEN** the size ceilings are evaluated against the full diff

#### Scenario: a later edit re-opens the question
- **WHEN** the diff grows past a ceiling after a size check already passed
- **THEN** the check is re-evaluated against the diff that now exists

### Requirement: Only a human resolves a size punch-out

A size punch-out SHALL be resolved only by a signed human decision. The flow SHALL NOT split a
change, raise a ceiling, or proceed on its own assessment that the size is justified.

#### Scenario: the flow cannot clear its own size punch-out
- **WHEN** a size punch-out is open
- **THEN** outward actions are refused and no artifact written by the flow clears it

#### Scenario: a human may accept an oversized change
- **WHEN** a human records a decision to proceed despite the breach
- **THEN** the flow advances and the decision remains in the run's record
