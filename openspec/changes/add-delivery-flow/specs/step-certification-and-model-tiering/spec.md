## ADDED Requirements

### Requirement: Step registry
Every LLM task prompt the flow can run (orchestrator, triage, work-type classifier, the SDLC agents on the flow's paths, adversarial validator, PR description, post-back summary, delivery recall, and each enabled roster reviewer or architect) SHALL have an entry in `steps.yaml` declaring its prompt path, the certified version file, runtime model tier, eval suite path, certified results path, prompt sha256 at certification, criteria list, load-bearing map path, iteration log path, and escalation evidence when the tier is above Sonnet.

#### Scenario: The workflow itself is registered and certified end to end
- **WHEN** `check-certification.py delivery-flow` runs
- **THEN** it requires an end-to-end suite whose cases run a seeded item from intake to a terminal state and assert on the files produced, the outcome, the punch-out point and the trace, not only on routing decisions

#### Scenario: Unregistered step refused
- **WHEN** the flow is about to delegate to an agent that has no `steps.yaml` entry
- **THEN** it refuses the delegation and names the missing registry entry

### Requirement: Stage 3 bar per step
`check-certification.py <step>` SHALL exit 0 only when all of the following hold:
- the entry lists at least 3 distinct criteria;
- the results file shows at least 95% of asserts passing;
- the results were produced by a provider whose model tier is Sonnet or lower;
- the prompt file's current sha256 equals the recorded `prompt_sha256` and matches the certified version file;
- every scored row in the results was rendered with the certified prompt text, so an older run cannot certify an edited prompt;
- a load-bearing map file (kept beside the suite, not sent to the model) maps at least 90% of the prompt's instructions to criteria;
- the iteration log has at least 2 entries, each containing baseline, hypothesis, change, result and reasoning.

Otherwise it SHALL exit 1 naming each unmet condition.

#### Scenario: Prompt edit forces recertification
- **WHEN** `agents/story-planner.md` changes after certification
- **THEN** `check-certification.py story-planner` exits 1 reporting the sha256 mismatch

#### Scenario: Frontier-model eval does not count
- **WHEN** a step's certified results were produced with an Opus provider
- **THEN** `check-certification.py` exits 1 stating evals must run on Sonnet or lower

#### Scenario: Results from another prompt version are rejected
- **WHEN** the registry points at a results file produced with an earlier prompt version
- **THEN** `check-certification.py` exits 1 naming the rows not produced with the certified prompt

#### Scenario: Below the bar
- **WHEN** a step's results show 22 of 24 asserts passing
- **THEN** `check-certification.py` exits 1 reporting 91.7% against the 95% bar

### Requirement: Uncertified steps blocked unless explicitly allowed
The flow SHALL run `check-certification.py` before each step and SHALL refuse a step that fails it, unless `.delivery-flow.yaml` lists that step under `allow_uncertified`. In that case every trace record for the step SHALL carry `certified: false`. Roster entries whose agents are uncertified SHALL be excluded from dispatch unless allowed the same way.

#### Scenario: Allowed uncertified step is marked
- **WHEN** `allow_uncertified: [qa-test-architect]` is set and that step runs
- **THEN** its trace records carry `certified: false`

### Requirement: Certified-only end-to-end rate
`delivery-report.py` SHALL report the end-to-end rate both over all runs and over runs whose every trace record has `certified: true`, and SHALL label the certified-only figure as the Stage 4 number.

#### Scenario: Run with an uncertified step excluded
- **WHEN** a completed run contains one record with `certified: false`
- **THEN** it counts toward the all-runs rate and is excluded from the certified-only rate

### Requirement: Cheapest passing tier with evidence-gated escalation
A step's declared tier SHALL be the cheapest of Haiku or Sonnet whose suite passes at 95% or better. A tier above Sonnet SHALL require `escalation_evidence`: a committed results file showing the same suite below 95% on Sonnet. `check-certification.py` SHALL fail an above-Sonnet entry without it. A checker step SHALL differ from its generator step in model or run in a fresh context with a refute-framed prompt.

#### Scenario: Opus without evidence rejected
- **WHEN** `steps.yaml` declares `tier: opus` for `adversarial-validator` with no escalation evidence
- **THEN** `check-certification.py adversarial-validator` exits 1 requiring a Sonnet results file below 95%

#### Scenario: Haiku preferred when it passes
- **WHEN** the `pr-description` suite scores 96% on Haiku and 98% on Sonnet
- **THEN** the certified tier recorded for `pr-description` is `haiku`

### Requirement: Runtime model conformance
The trace hook SHALL set `model_conformant: false` on any record whose model is above the step's declared tier. `delivery-report.py` SHALL list non-conformant records with their cost over the declared tier. `delivery-flow --status` SHALL warn when the main session's model is above the orchestrator step's declared tier.

#### Scenario: Subagent ran on a heavier model
- **WHEN** a `story-planner` record shows an Opus model while its declared tier is Sonnet
- **THEN** the record has `model_conformant: false` and the report lists it with its extra cost

#### Scenario: Orchestrator session on Opus warned
- **WHEN** `delivery-flow DEM-12 --status` runs in a session using an Opus model and the orchestrator's tier is Sonnet
- **THEN** the status output includes a warning recommending a Sonnet session
