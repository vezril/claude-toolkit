## ADDED Requirements

### Requirement: Every punch-out trigger has a derivation independent of the gated node
For each trigger read from `triage.json` — `scope`, `architecture`, `breaking` —
`check-punch-out.py` SHALL compute a derivation from the item and the breakdown without reading
the node's boolean. No trigger SHALL depend solely on a flag written by the node it gates.

#### Scenario: Scope derives from the item text and the breakdown size

- **WHEN** the item text states no expected outcome, or the breakdown exceeds the epic or story ceiling
- **THEN** the `scope` derivation fires

#### Scenario: Architecture derives from breadth and from boundary vocabulary

- **WHEN** the breakdown spans more declared domains than the ceiling, or its text carries architecture vocabulary, or it names a `contract_paths` entry
- **THEN** the `architecture` derivation fires

#### Scenario: Breaking derives from breaking-change vocabulary and shared contracts

- **WHEN** the item or breakdown text carries breaking-change vocabulary, or names a `contract_paths` entry
- **THEN** the `breaking` derivation fires

#### Scenario: A suppressed flag still fires the trigger

- **GIVEN** `triage.json` sets `breaking_change: false` and `breakdown.json` names a path under `contract_paths`
- **WHEN** the punch-out check runs
- **THEN** the `breaking` trigger fires on the derivation and the flow stops

#### Scenario: Node request is still honoured

- **GIVEN** `triage.json` sets `handoff: true` and no derivation fires
- **WHEN** the punch-out check runs
- **THEN** the `scope` trigger fires, because a node asking for a human is never overridden

### Requirement: A trigger fires on either the derivation or the claim
A trigger SHALL fire when the derivation indicates it, when the node's flag indicates it, or
both. Suppressing a flag SHALL NOT prevent a trigger whose derivation fires. This, not the
disagreement record below, is what closes the hole: the gate no longer depends on a boolean
written by the step it gates.

#### Scenario: A suppressed flag does not skip the gate

- **GIVEN** `triage.json` sets every flag false and the item text says "this is a breaking change"
- **THEN** the `breaking` trigger fires from the derivation and a punch-out is written

#### Scenario: A node asking for a human is never overruled

- **GIVEN** `triage.json` sets `handoff: true` and no derivation fires
- **THEN** the `scope` trigger fires anyway

### Requirement: Disagreement is recorded as evidence, not failed as an edge
Where a derivation and a claim disagree, the edge record for the producing artifact SHALL carry
a `policy_disagreement` entry naming the trigger, the claimed value, the derived value and the
evidence, and `check-punch-out.py` SHALL report it. Disagreement SHALL NOT fail the edge.
(Rationale, including why the stronger rule was wrong: design.md D5.)

#### Scenario: Disagreement is visible in the trace

- **GIVEN** `triage.json` claims no breaking change and the item text says "breaking change"
- **WHEN** the edge for `triage.json` runs
- **THEN** the edge passes, its trace record carries a `policy_disagreement` entry for `breaking`, and the `breaking` punch-out is still written

#### Scenario: Agreement records nothing

- **GIVEN** the claim and the derivation agree
- **THEN** the edge record carries no `policy_disagreement` entry

#### Scenario: An undetermined derivation is not disagreement

- **GIVEN** `triage.json` has been written and `breakdown.json` has not
- **WHEN** the edge for `triage.json` runs
- **THEN** the count and domain derivations are reported as undetermined rather than as false, and they produce no disagreement entry

### Requirement: Derivation ceilings are configuration
The epic-count ceiling for `scope` and the domain-count ceiling for `architecture` SHALL be keys
under `punch_out` in `.delivery-flow.yaml` with documented defaults, so they can be tuned against
real runs without editing the checker. Ceilings SHALL be documented in
`skills/delivery-flow/references/config.md`.

#### Scenario: Default applies when unset

- **GIVEN** no ceiling keys in the config
- **WHEN** the check runs
- **THEN** the documented defaults are used and the run is unaffected by their absence

### Requirement: Derivations are recorded as evidence
Each fired trigger's punch-out file SHALL state whether it came from the derivation, the claim,
or both, and SHALL quote the evidence that produced it. A reviewer SHALL be able to tell from the
punch-out alone which mechanism stopped the flow.

#### Scenario: Punch-out names its source

- **WHEN** a trigger fires on the derivation only
- **THEN** the punch-out file states that the node's flag did not request it and quotes the derived evidence

### Requirement: The bypass suite attacks the derivations
`tests/delivery-flow/bypass/` SHALL gain cases that attempt to evade each derived trigger:
suppressing the node flag, renaming a path to fall outside `contract_paths`, splitting a
breakdown to stay under a ceiling, and editing `triage.json` by hand after the edge has passed.
Each case SHALL assert that the attempt is blocked or recorded, and the suite's report SHALL be
submitted including any holes it finds.

#### Scenario: Hand-edited artifact is detected

- **GIVEN** `triage.json` is edited by hand after its edge passed
- **WHEN** the next step runs
- **THEN** the sha mismatch against the trace marks the run `failed` with reason `manual-correction`

#### Scenario: Flag suppression is covered by a test

- **WHEN** the bypass suite runs
- **THEN** a case exists for each derived trigger asserting that suppressing the node's flag does not evade it
