## ADDED Requirements

### Requirement: The certification core is workflow-agnostic

`scripts/workflow/` SHALL provide the certification core, and no workflow-specific path,
artifact name or step name SHALL appear in it.

#### Scenario: The core carries no workflow-specific identifiers

- **WHEN** `scripts/workflow/` is searched for workflow-specific paths, artifact names or step
  names
- **THEN** none are found

#### Scenario: The core covers the whole apparatus

- **WHEN** a workflow needs step-registry loading, profile-aware routing, trace append, edge
  dispatch, outcome writing with manual-correction detection, certification enforcement, or
  signature and pricing helpers
- **THEN** each is served by `scripts/workflow/`

### Requirement: A workflow declares itself with a descriptor

A workflow SHALL declare itself with a descriptor file naming its step registry, schema
directory, artifact root, profiles, punch-out triggers and model policy.

#### Scenario: Delivery-flow behaviour is unchanged by the extraction

- **GIVEN** the substrate has been extracted and `delivery-flow` re-pointed at it
- **WHEN** `pytest tests/delivery-flow/` and `tests/delivery-flow/bypass/run-bypass.py` run
- **THEN** both pass with no behavioural difference from the committed pre-extraction baseline,
  and the bypass suite still blocks all 15 attacks

#### Scenario: Existing import paths keep working

- **GIVEN** a script or hook importing from `scripts/delivery-flow/common.py`
- **WHEN** it runs after the extraction
- **THEN** the import resolves through a re-export shim and the caller is unaffected

#### Scenario: A second workflow needs no new substrate

- **GIVEN** a descriptor for a workflow that is not `delivery-flow`
- **WHEN** its router, trace, edge dispatch and outcome writing are exercised
- **THEN** they are served by `scripts/workflow/` with no workflow-specific code added

### Requirement: Hooks resolve the active workflow rather than hard-coding one

`hooks/check-edge.py`, `hooks/trace-step.py` and `hooks/enforce-punch-outs.py` SHALL resolve the
active workflow descriptor from the repository instead of keying on `.delivery-flow.yaml` or the
`delivery/<ITEM-KEY>/` path shape. Each SHALL remain inert, exiting 0, where no descriptor is
present. A hook SHALL NOT fail a tool call on its own internal error.

#### Scenario: A repo with no workflow is untouched

- **GIVEN** a repository containing no workflow descriptor
- **WHEN** any file is written
- **THEN** all three hooks exit 0 and record nothing

#### Scenario: Two workflows coexist

- **GIVEN** a repository holding both a `delivery-flow` and an `sdlc` descriptor
- **WHEN** an artifact belonging to one of them is written
- **THEN** only that workflow's edges run, and its verdict is appended to its own trace

### Requirement: Certification state gates delegation for every workflow

`check-certification.py` SHALL refuse delegation to a step whose registry entry is not certified,
for any registered workflow. A registry entry SHALL record the certified prompt's sha so that
editing the prompt un-certifies the step until it is re-certified.

#### Scenario: An uncertified segment cannot run

- **GIVEN** an `sdlc` registry in which only the `readiness` segment is certified
- **WHEN** the orchestrator attempts to delegate to a step in the `implementation` segment
- **THEN** the certification check exits non-zero naming the uncertified step, and delegation
  does not occur

#### Scenario: Editing a certified prompt re-blocks it

- **GIVEN** a certified step whose prompt sha is recorded in the registry
- **WHEN** the prompt file is edited
- **THEN** the certification check exits non-zero until the step is re-certified and the sha
  updated

### Requirement: The trace records the model actually used

For each step the trace SHALL record the model the step actually ran on, the tokens consumed, the
cost, the artifact sha, and the edge verdict. Where the model used differs from the tier declared
in the registry, the trace SHALL flag the drift.

#### Scenario: Declared tier and actual model disagree

- **GIVEN** a step declared at the haiku tier in the registry
- **WHEN** it runs on sonnet
- **THEN** the trace records sonnet and flags drift from the declared tier

### Requirement: Attack evidence is produced by a reusable harness

The bypass harness SHALL run against any registered workflow's punch-out gates, not only
`delivery-flow`'s, and SHALL emit a committed report naming each attack and whether it was
blocked.

#### Scenario: A workflow's gates are attacked

- **GIVEN** a registered workflow declaring punch-out triggers
- **WHEN** the bypass harness runs against it
- **THEN** it emits a report listing every attack attempted and its result, and exits non-zero
  if any attack succeeded
