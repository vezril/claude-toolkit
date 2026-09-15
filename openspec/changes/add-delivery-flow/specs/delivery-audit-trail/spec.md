## ADDED Requirements

### Requirement: One trace record per step, including the orchestrator
For every subagent completion inside a delivery-flow repository, the trace hook SHALL append one JSON line to `delivery/<KEY>/trace.jsonl` containing `ts`, `item`, `step`, `agent`, `session_id`, `agent_id`, `model`, `input_tokens`, `output_tokens`, `cache_creation_tokens`, `cache_read_tokens`, `cost_usd`, `artifact` and `validator` (name, exit code, summary). The main session's usage since its previous record SHALL be recorded as `step: orchestrator`. The step SHALL be taken from `delivery/<KEY>/.current-step`.

#### Scenario: Subagent step traced
- **WHEN** the triage subagent finishes while `.current-step` names `triage` for DEM-12
- **THEN** `trace.jsonl` gains one record with `step: "triage"`, the subagent's model, and token counts summed from its transcript

#### Scenario: Multi-model step split
- **WHEN** a step's transcript contains turns from two different models
- **THEN** the hook writes one record per model for that step, each with its own token counts and cost

### Requirement: Usage comes from transcripts, never self-report
Token counts SHALL be read from the Claude Code transcript `usage` fields. Agents SHALL NOT be asked to report their own token usage or cost.

#### Scenario: No transcript, no fabricated numbers
- **WHEN** the hook cannot locate the subagent transcript
- **THEN** it writes the record with null token fields and `trace_error` describing the lookup failure

### Requirement: Usage counted once per API message
The trace hook and report SHALL sum usage once per distinct `message.id` in a transcript, because Claude Code repeats the same `usage` object on every content block of one API message. They SHALL price 5-minute and 1-hour cache writes separately, using `usage.cache_creation.ephemeral_5m_input_tokens` and `ephemeral_1h_input_tokens`.

#### Scenario: Repeated usage not double-counted
- **WHEN** a subagent transcript contains 6 assistant lines sharing one `message.id` with `output_tokens: 3`
- **THEN** the step's record shows `output_tokens: 3`, not 18

### Requirement: Cost from a dated pricing table
Cost SHALL be computed from `pricing.yaml` (USD per million tokens per model and token class, with `source` and `as_of`). A model absent from the table SHALL produce `cost_usd: null` and `pricing_missing: true`.

#### Scenario: Unknown model flagged
- **WHEN** a record's model is not in `pricing.yaml`
- **THEN** the record has `cost_usd: null` and `pricing_missing: true`, and the report lists the model under missing pricing

### Requirement: Inert outside delivery-flow repositories
The trace hook SHALL exit 0 without reading transcripts or writing files when the session's git root has no `.delivery-flow.yaml`.

#### Scenario: Unrelated repo untouched
- **WHEN** a subagent finishes in a repository without `.delivery-flow.yaml`
- **THEN** the hook exits 0 and creates no file

### Requirement: End-to-end report
`delivery-report.py <root>` SHALL aggregate `trace.jsonl` and `outcome.json` files and emit Markdown and CSV. The output SHALL contain: per-item outcome, total tokens and cost; per-step token and cost distribution; per-model totals; and a weekly series of end-to-end rate `completed / (completed + failed)`, with the punch-out rate reported separately. It SHALL state the pricing `as_of` date used.

#### Scenario: Punch-outs are not failures
- **WHEN** a week has 4 completed, 1 failed and 2 punched-out items
- **THEN** the report shows an end-to-end rate of 80% and a punch-out rate of 2 of 7 items

### Requirement: Failure traceable to its origin step
Given an item with a failed or refuted output, the trace SHALL let a reader identify the step, agent, model and validator result that produced the first failing output.

#### Scenario: Trace a refuted spec
- **WHEN** `challenge-spec.md` is REFUTED for DEM-12
- **THEN** `trace.jsonl` contains the record for the Solutioning step that produced the refuted `spec-ready.md`, including its model and validator exit code
