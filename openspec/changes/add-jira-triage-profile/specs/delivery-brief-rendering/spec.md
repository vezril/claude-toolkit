## ADDED Requirements

### Requirement: The brief is rendered by a script, not a node
`scripts/delivery-flow/render-brief.py` SHALL produce `summary.md` from `item.json`,
`triage.json`, `breakdown.json` and `challenge-breakdown.json` using a fixed template, and SHALL
contain no LLM call. It SHALL NOT appear in `skills/delivery-flow/steps.yaml`, because it is not
a node and has no prompt to certify. Reruns over unchanged inputs SHALL be byte-identical.

#### Scenario: Brief is reproducible

- **WHEN** the renderer runs twice over the same artifacts
- **THEN** the two `summary.md` files are byte-identical

#### Scenario: Renderer is not a registered step

- **WHEN** `check-certification.py --all` runs
- **THEN** `brief` is not reported as an uncertified step, because it is a script step rather than a node

### Requirement: The brief has a fixed shape in a fixed order
`summary.md` SHALL contain, in this order: what the ticket asks for, the classification and path
from `triage.json`, the epics and stories with their counts, the challenge verdict, the findings
that must be addressed, and any open punch-out with the decision being asked. Section order and
headings SHALL NOT vary between runs or items. Where a section has no content, it SHALL be
present and state that explicitly rather than being omitted.

#### Scenario: Empty section is stated, not dropped

- **GIVEN** a `SURVIVED` verdict with no findings
- **WHEN** the brief renders
- **THEN** the findings section is present and states that there are none

#### Scenario: Quick-path item keeps the same shape

- **GIVEN** a `bug` on the quick path, with no breakdown
- **WHEN** the brief renders
- **THEN** every section is present in the same order, with the breakdown and challenge sections stating that the quick path skipped them

### Requirement: Coverage of the structured inputs is a hard edge
The edge check for `summary.md` SHALL verify that every epic id and story id in
`breakdown.json` appears in the brief, that the verdict from `challenge-breakdown.json` appears,
that every finding the verdict requires to be addressed appears, and that the brief introduces no
identifier absent from its input artifacts. Failure SHALL be reported to the model and recorded
in the trace as an edge failure, as for any other artifact.

#### Scenario: A dropped story fails the edge

- **GIVEN** `breakdown.json` holds 8 stories and the brief names 7
- **THEN** the edge fails naming the missing story id

#### Scenario: An invented identifier fails the edge

- **WHEN** the brief names a file or story id that occurs in none of its inputs
- **THEN** the edge fails naming that identifier

#### Scenario: Verdict must be carried

- **GIVEN** a `WEAKENED` verdict with two findings
- **WHEN** the brief omits one finding
- **THEN** the edge fails naming the omitted finding

### Requirement: Readability is measured into the trace, not gated
The edge check SHALL compute Flesch-Kincaid grade and Gunning Fog for `summary.md` using
`skills/readability/scripts/readability.py` and SHALL record both in the trace record for the
step. These metrics SHALL NOT cause the edge to fail, because the prose the brief inherits is
written by the breakdown node and the renderer cannot change it.

#### Scenario: A hard-to-read brief still passes

- **GIVEN** inherited acceptance criteria that push the grade above the target
- **WHEN** the edge runs
- **THEN** the metrics are recorded in the trace and the edge passes on coverage

#### Scenario: Metrics are available per run

- **WHEN** the trace is read for an item
- **THEN** the brief's step record carries both readability scores

### Requirement: The brief is terminal prose
`summary.md` SHALL be consumed by no step. It SHALL be exempt from schema conformance, and any
future step requiring its content SHALL read the structured artifacts instead.

#### Scenario: No step declares the brief as input

- **WHEN** `steps.yaml` and `profiles.yaml` are inspected
- **THEN** no step lists `summary.md` among its inputs
