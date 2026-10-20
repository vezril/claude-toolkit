## ADDED Requirements

### Requirement: Structured contracts between nodes
Every artifact that another step consumes SHALL be structured data (JSON or YAML) conforming to a schema in `schemas/`, and each schema SHALL name the step that produces it and the steps that consume it. Prose artifacts SHALL exist only as terminal outputs that no step consumes (`pr.md`, `post.md`). A step whose output another step reads SHALL NOT emit prose as its contract.

#### Scenario: Breakdown is schema-checked data
- **WHEN** the breakdown node produces its epics, stories and acceptance criteria
- **THEN** it writes `breakdown.json` conforming to `schemas/breakdown.schema.json`, not a written summary

#### Scenario: Terminal prose is allowed
- **WHEN** the PR description node writes `pr.md`
- **THEN** no schema conformance is required of it, and no step consumes it as input

### Requirement: Every node writes a sentinel
A node that writes a structured artifact SHALL also write `<artifact>.sentinel.json` containing the artifact path, its sha256, the counts the node claims it produced, the status it claims, the step, and a timestamp. A missing sentinel SHALL fail the edge.

#### Scenario: Sentinel accompanies the artifact
- **WHEN** the breakdown node writes `breakdown.json` with 3 epics and 8 stories
- **THEN** `breakdown.json.sentinel.json` records that sha256 and those counts

#### Scenario: Missing sentinel fails the edge
- **WHEN** an artifact is written with no sentinel beside it
- **THEN** the edge check fails naming the missing sentinel

### Requirement: Edge checks fire after the write, as hooks
Edge checks SHALL run from a PostToolUse hook on writes under `delivery/<KEY>/`, not from a call the orchestrator chooses to make. For the artifact written the hook SHALL verify that it exists and parses, its sha256 matches its sentinel, it conforms to its schema, the sentinel's claimed counts match the real counts, and it satisfies the input contract of the step that consumes it. On failure the hook SHALL exit 2 so the report returns to the model, and SHALL append an `edge` result to `trace.jsonl` either way.

#### Scenario: A check the model never asked for still runs
- **WHEN** a node writes `triage.json` and never invokes a validator
- **THEN** the edge hook validates it anyway and records the result in the trace

#### Scenario: Sentinel claim contradicted by the file
- **WHEN** `breakdown.json.sentinel.json` claims 8 stories and the file contains 5
- **THEN** the edge fails naming the count mismatch, even though the file conforms to its schema

#### Scenario: Inert outside delivery-flow repositories
- **WHEN** a write happens in a repository without `.delivery-flow.yaml`
- **THEN** the edge hook exits 0 and checks nothing

### Requirement: The flow cannot advance past a failed edge
The orchestrator SHALL read the latest `edge` result for an artifact from `trace.jsonl` and SHALL NOT run the consuming step while that result is a failure. It SHALL rerun the producing step at most 3 times, then write a punch-out.

#### Scenario: Failed edge blocks the next node
- **WHEN** `triage.json`'s latest edge result is a failure
- **THEN** the breakdown node does not run, and the triage step reruns with the edge report

#### Scenario: Repeated edge failure punches out
- **WHEN** a step's edge fails on 3 consecutive reruns
- **THEN** the flow writes a punch-out naming the step and the failing check, and stops

### Requirement: Adjacent steps' contracts must fit
Each registry entry SHALL declare the artifacts a step consumes. The edge check SHALL verify the produced artifact against the consuming step's input contract, so an artifact that is valid in isolation but unusable downstream fails at the handoff.

#### Scenario: Output missing a field the next node needs
- **WHEN** `breakdown.json` validates against its own schema but omits acceptance criteria, which the implementation step requires
- **THEN** the edge fails at the breakdown handoff, not inside the implementation step

### Requirement: Adversarial review is a node, with harness rules
The adversarial reviewer SHALL run in a fresh context, carry its own Stage 3 certification, and emit a structured verdict (`REFUTED`, `WEAKENED` or `SURVIVED`) with findings. The harness SHALL apply fixed rules to that verdict: REFUTED reruns the producing step with the findings, WEAKENED requires each finding addressed in the next version, SURVIVED proceeds. The reviewer SHALL NOT be counted as a guardrail, and SHALL NOT share context with the step it reviews.

#### Scenario: Refuted verdict routes deterministically
- **WHEN** `challenge-breakdown.json` carries verdict REFUTED
- **THEN** the harness reruns the breakdown node with the findings as input, without asking a model what to do about the verdict

#### Scenario: Reviewer context is reset
- **WHEN** the challenge node runs on an artifact
- **THEN** it receives the artifact and the raw material, and not the reasoning or conversation that produced it

### Requirement: Loop bounds are explicit
The workflow definition SHALL state its loop bounds: at most 3 reruns of a step, a punch-out after a second REFUTED verdict on the same step, and a per-item cost budget. Every rerun SHALL appear in the trace.

#### Scenario: Second refutation stops the loop
- **WHEN** the same step is REFUTED a second time
- **THEN** the flow writes a punch-out instead of rerunning
