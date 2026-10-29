## ADDED Requirements

### Requirement: The pipeline is registered as certifiable segments

`skills/sdlc-orchestration/steps.yaml` SHALL register the sdlc pipeline as named segments of two
to three nodes each. Every segment SHALL declare its nodes, its terminal step, its hand-off
artifact and that artifact's schema, and its certification state. A segment's hand-off SHALL be
schema-backed data where the next segment's nodes consume it, and MAY be prose only where a human
is the sole reader.

#### Scenario: A segment can be run alone and stop

- **GIVEN** a run scoped to the `readiness` segment
- **WHEN** the segment's terminal step completes and its edge passes
- **THEN** `outcome.json` is written with `completed` and routing stops rather than continuing
  into the next segment

#### Scenario: A prose hand-off into a node is refused

- **GIVEN** a segment declaring a prose hand-off artifact
- **WHEN** the next segment's nodes consume that artifact
- **THEN** the registry is invalid and the check names the offending segment

### Requirement: The readiness gate runs as a hook, not an instruction

The readiness checks SHALL run through the edge dispatch on `PostToolUse` after the story set is
written. The orchestrator SHALL NOT be the thing that invokes them. A failed edge SHALL be
recorded in the trace and the orchestrator SHALL refuse to advance past it.

#### Scenario: Skipping is not possible

- **GIVEN** an orchestrator that does not invoke any validation command
- **WHEN** a story set is written
- **THEN** the readiness edge still runs and still records a verdict

#### Scenario: A failed edge blocks advance without claiming prevention

- **GIVEN** a story set that fails the readiness edge
- **WHEN** the hook completes
- **THEN** the artifact still exists on disk, the trace records the failed verdict, and the
  orchestrator refuses to advance to the next segment

#### Scenario: A missing external validator blocks rather than passes

- **GIVEN** a repository where the `openspec` CLI is not installed
- **WHEN** the readiness edge runs
- **THEN** it records a blocking failure naming the missing CLI, and never passes by absence

### Requirement: The reviewer is a certified node and the rules are the edge

The readiness reviewer SHALL run in a fresh context, carry its own Stage 3 certification, and
emit a verdict valid against `schemas/readiness-verdict.schema.json` with one of `REFUTED`,
`WEAKENED` or `SURVIVED` plus findings. A harness in the substrate SHALL apply fixed rules to
that verdict: `REFUTED` reruns the producing node, `WEAKENED` requires every finding addressed
before advance, `SURVIVED` proceeds. The orchestrator SHALL NOT interpret the verdict.

#### Scenario: The verdict drives the pipeline mechanically

- **GIVEN** a readiness verdict of `REFUTED`
- **WHEN** the harness applies its rules
- **THEN** the story-planner node is rerun, with no orchestrator judgment involved

#### Scenario: Findings must be addressed on WEAKENED

- **GIVEN** a verdict of `WEAKENED` carrying three findings
- **WHEN** advance is attempted with one finding unaddressed
- **THEN** the harness refuses the advance and names the outstanding finding

#### Scenario: An unstructured review is not a check

- **GIVEN** a reviewer that emits prose instead of a schema-valid verdict
- **WHEN** the edge runs
- **THEN** the verdict is recorded as invalid and the pipeline does not advance

### Requirement: Model policy is cheapest-tier-first with escalation evidence

Each node SHALL be certified on the cheapest model tier whose suite passes, trying haiku before
sonnet. Escalation to a more expensive tier SHALL require a committed results file showing the
cheaper tier below the bar on the same suite. The checker SHALL differ from the generator — a
different model, or the same model in a fresh context with a refute-framed prompt.

#### Scenario: Escalation without evidence is refused

- **GIVEN** a node declared at the sonnet tier with no committed haiku results file
- **WHEN** its certification is checked
- **THEN** the check exits non-zero naming the missing escalation evidence

### Requirement: Runs are recorded at story granularity with manual correction detected

Outcome records SHALL distinguish `completed`, `punched-out`, `failed` and `abandoned`, at the
granularity of one story through a segment. Where an artifact's sha differs from the sha recorded
in the trace, the run SHALL be marked `failed` with reason `manual-correction`. Both readings of
the punch-out denominator SHALL be emitted.

#### Scenario: A hand-edit to pass a gate is a failed run

- **GIVEN** a story set that failed the readiness edge
- **WHEN** a human edits the artifact so the gate passes and the run continues
- **THEN** the sha comparison detects it and the run is recorded `failed` with reason
  `manual-correction`, not `completed`

#### Scenario: A punch-out is not a failure

- **GIVEN** a run that reached a human decision point and stopped
- **THEN** the outcome is `punched-out`, and the report emits the success rate both including and
  excluding it from the denominator

#### Scenario: Per-segment rates, not a pipeline promise

- **WHEN** the report is produced
- **THEN** it states a rate per certified segment and does not assert an end-to-end rate for
  segments that are not certified
