# Spec Delta

## Purpose

How test priority reaches the dev pair, so that a change carries the tests its risk warrants
rather than as many as the pair chose to write — with the priority recorded as checkable data
rather than left as a judgement inside the step.

## ADDED Requirements

### Requirement: Every story carries a risk-priority map

A story handed to the dev pair SHALL carry a priority for each acceptance criterion, drawn from
the P0–P3 scale. The map SHALL be part of the story or proposal artifact, so a reviewer can
read the priority that governed the tests.

#### Scenario: the priorities are data, not inference
- **WHEN** a story reaches the dev pair
- **THEN** each acceptance criterion carries an explicit P0–P3 priority

#### Scenario: an unprioritised criterion is an error
- **WHEN** a story has an acceptance criterion with no priority
- **THEN** the step fails naming that criterion, rather than assigning a priority itself

### Requirement: The dev pair tests P0 and P1 and nothing below

The test author SHALL write tests covering every P0 and P1 criterion, and SHALL NOT write tests
for P2 or P3 criteria. Lower-priority criteria SHALL remain in the story as untested
requirements rather than being removed.

#### Scenario: P0 and P1 are covered
- **WHEN** a story carries three P0 criteria and one P1
- **THEN** the tests cover all four

#### Scenario: P2 and P3 are left untested and still recorded
- **WHEN** a story carries a P2 criterion
- **THEN** no test is written for it and the criterion remains in the story, marked as out of test scope

#### Scenario: the pair does not re-prioritise to widen scope
- **WHEN** the test author judges a P2 criterion important
- **THEN** it reports that as a finding against the priority map rather than writing the test

### Requirement: The verify edge checks scope in both directions

Verification SHALL check that every P0 and P1 criterion has a test and that no test claims a
criterion below P1. Both directions SHALL be checked, because covering too much is the failure
this capability exists to bound.

#### Scenario: a missing P0 test fails verification
- **WHEN** a P0 criterion has no test
- **THEN** verification fails naming the uncovered criterion

#### Scenario: a test beyond the scope fails verification
- **WHEN** a test is written for a P3 criterion
- **THEN** verification fails naming the out-of-scope test

#### Scenario: a test covering several criteria is counted for each
- **WHEN** one test covers two P0 criteria
- **THEN** both count as covered, and no additional test is required for either
