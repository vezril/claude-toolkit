## ADDED Requirements

### Requirement: File-based routing
The `delivery-flow` skill SHALL determine an item's position solely from the files in `delivery/<ITEM-KEY>/` and SHALL run the first step in the routing table whose output file is missing. It SHALL run one step per invocation unless the user explicitly asks it to run ahead, and SHALL always stop at a decision point.

#### Scenario: Resume from files
- **WHEN** `delivery/DEM-12/` contains `item.json` and `triage.json` but no later artifacts, and no vault binding is configured
- **THEN** the flow skips vault recall with a recorded reason and routes to the SDLC Planning/Solutioning step

#### Scenario: Status is computed, not remembered
- **WHEN** the user runs `delivery-flow DEM-12 --status`
- **THEN** the flow prints the routing table annotated with which artifacts exist, the latest edge result per artifact, and which decision point (if any) it is waiting on

### Requirement: Per-repo configuration
The flow SHALL read `.delivery-flow.yaml` at the repository root for tracker kind, forge kind, punch-out policy (triggers, cost budget, external trackers), deploy and auto-roll settings, per-step models, roster overrides, test command, artifact commit policy, and optional vault binding. It SHALL stop and ask when the file is missing, never guessing a tracker or forge.

#### Scenario: Missing config
- **WHEN** `delivery-flow` is invoked in a repository without `.delivery-flow.yaml`
- **THEN** the flow stops, names the template path to copy, and performs no tracker or forge call

### Requirement: Branching by item type and path
Triage SHALL classify each item as `bug`, `feature` or `task` and assign `quick` or `standard` path, recording the rationale in `triage.json` against its schema. Bugs SHALL go through root-cause analysis and a fix proposal before the quick path; features SHALL take the standard path; tasks SHALL take the quick path. Triage SHALL hand the item to a human instead of choosing when the item is ambiguous or requires architecture work that its type does not allow.

#### Scenario: Feature takes the standard path
- **WHEN** triage classifies an item as a feature
- **THEN** the flow invokes the SDLC orchestrator's standard path (requirements, OpenSpec change, stories) before implementation

#### Scenario: Ambiguous item hands off to a human
- **WHEN** a `task` item's description requires a new service boundary
- **THEN** triage sets `handoff: true` in `triage.json`, the policy check writes a punch-out, and the flow does not proceed to SDLC phases

### Requirement: Mandatory checks at handoffs
Edge checks SHALL be fired by the PostToolUse hook, not invoked by the flow (see `node-contracts-and-edges`). The flow SHALL read each artifact's latest `edge` result from the trace and SHALL NOT advance past a failed one, rerunning the producing step at most 3 times before stopping with `outcome: punched-out`. An adversarial review SHALL be mandatory after the breakdown (`challenge-breakdown.json`) and after verify (`challenge-implementation.json`), and a REFUTED verdict SHALL rerun the producing step with the findings as input.

#### Scenario: Failed edge blocks advance
- **WHEN** the latest `edge` result for `delivery/DEM-12/breakdown.json` is a failure
- **THEN** the flow reruns the breakdown step with the edge report and does not run the step that consumes it

#### Scenario: Refuted breakdown reruns
- **WHEN** `challenge-breakdown.json` carries verdict REFUTED
- **THEN** the flow reruns the breakdown step with the refutation findings, regenerating `breakdown.json` and invalidating any later artifacts

### Requirement: Outcome recording
Every item that reaches a terminal state SHALL have `outcome.json` with status `completed`, `punched-out`, `failed` or `abandoned`, a reason, and the step it ended at. A validated output file whose sha no longer matches its trace record SHALL mark the item `failed` with reason `manual-correction`.

#### Scenario: Manual correction is counted as failure
- **WHEN** a human hand-edits `pr.md` after it passed validation and was traced
- **THEN** the report step records `outcome.json` status `failed` with reason `manual-correction`
