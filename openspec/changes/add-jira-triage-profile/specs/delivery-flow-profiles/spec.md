## ADDED Requirements

### Requirement: A profile names an ordered subset of the routing table
`templates/delivery-flow/profiles.yaml` SHALL define named profiles, each listing the steps it
runs in order and declaring its terminal step. `.delivery-flow.yaml` SHALL accept a `profile:`
key naming one of them, and `flow-status.py` SHALL route only within the selected profile's
steps. A repository with no `profile:` key SHALL use `full`, whose step list is the complete
routing table, so existing behaviour is unchanged.

#### Scenario: Triage profile routes within its own steps

- **GIVEN** `.delivery-flow.yaml` sets `profile: triage`
- **WHEN** `flow-status.py <KEY>` runs on an item with `item.json` and `triage.json` present
- **THEN** the printed routing table contains only the `triage` profile's steps, and `Next:` names `breakdown`

#### Scenario: Absent profile key is the full table

- **GIVEN** `.delivery-flow.yaml` has no `profile:` key
- **WHEN** `flow-status.py <KEY>` runs
- **THEN** the routing table is the full 15-step table and routing is identical to before this change

#### Scenario: Unknown profile is refused

- **WHEN** `.delivery-flow.yaml` names a profile absent from `profiles.yaml`
- **THEN** `flow-status.py` exits 2 naming the unknown profile and the profiles available, and routes nothing

### Requirement: Profiles cover the routing table without gaps
The union of the steps across all shipped profiles SHALL equal the full routing table, and every
step in a profile SHALL exist in the routing table. A step present in the table but in no
profile, or named in a profile but absent from the table, SHALL fail the test suite.

#### Scenario: A step dropped from every profile is caught

- **WHEN** a step exists in the routing table and no profile lists it
- **THEN** the profile coverage test fails naming that step

### Requirement: Reaching a profile's terminus writes the outcome
When the terminal step of the selected profile passes its edge check, the report step SHALL run
and write `outcome.json` with outcome `completed`. A profile SHALL NOT finish by the mere absence
of a next step, so that a completed run and a stalled run are distinguishable in the trace. The
outcome vocabulary SHALL remain `completed`, `punched-out`, `failed`, `abandoned`.

#### Scenario: Terminus produces a terminal artifact

- **GIVEN** `profile: triage` whose terminus is `brief`
- **WHEN** `summary.md` is written and passes its edge
- **THEN** `outcome.json` records outcome `completed` for the item

#### Scenario: Stalled run is not reported complete

- **WHEN** the terminal step's edge has failed and has not been rerun
- **THEN** no `outcome.json` is written, and `flow-status.py` reports the failed edge rather than completion

### Requirement: The next profile is reported, never orchestrated by a model
On reaching a profile's terminus, `flow-status.py` SHALL name the next profile and the step it
would begin with, and SHALL stop. Continuation SHALL be a separate invocation. No LLM step SHALL
decide which profile runs, or when a profile has finished: profile selection and position SHALL
be computed from `.delivery-flow.yaml` and the artifacts on disk.

#### Scenario: Handoff is a printed sentence

- **WHEN** the `triage` profile reaches its terminus
- **THEN** the output names the next profile and its first step, and no further step runs in that invocation

#### Scenario: A later profile resumes from artifacts alone

- **GIVEN** `delivery/<KEY>/` holds `item.json`, `triage.json`, `breakdown.json`, `challenge-breakdown.json` and `outcome.json` from a `triage` run
- **WHEN** the profile is changed to `full` and `flow-status.py` runs
- **THEN** position is recomputed from those artifacts and `Next:` names the first step whose artifact is missing, with no record of which profile produced them

### Requirement: Profiles do not weaken certification or punch-outs
Profile selection SHALL NOT exempt a step from `check-certification.py`, and SHALL NOT suppress
a punch-out. An unresolved punch-out SHALL continue to block every step regardless of profile,
and `allow_uncertified` SHALL keep its meaning.

#### Scenario: Uncertified step still blocks inside a profile

- **WHEN** a profile lists a step absent from `steps.yaml` and not in `allow_uncertified`
- **THEN** the step is blocked and the run is not marked completed

### Requirement: The end-to-end rate is reported per profile
`delivery-report.py` SHALL group outcomes by the profile the item ran under, reporting per
profile the counts of `completed`, `punched-out`, `failed` and `abandoned`, and SHALL emit the
success rate under both readings of the punch-out denominator. A profile with no runs SHALL be
reported as having no rate rather than as zero.

#### Scenario: Certified chain has its own number

- **GIVEN** five items run under `profile: triage` and two under `full`
- **WHEN** `delivery-report.py` runs
- **THEN** the two profiles are reported separately, each with its outcome counts and both denominator readings

#### Scenario: No runs is not a zero rate

- **WHEN** a profile has no recorded outcomes
- **THEN** the report states that no runs exist for it rather than printing 0%
