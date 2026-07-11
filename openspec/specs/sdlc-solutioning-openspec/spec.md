# sdlc-solutioning-openspec Specification

## Purpose
TBD - created by archiving change sdlc-openspec-propose. Update Purpose after archive.
## Requirements
### Requirement: Solutioning builds specs through the OpenSpec propose flow

The SDLC pipeline SHALL open an OpenSpec change (`openspec new change <feature>`) at the start of Solutioning (after PRD approval) and SHALL produce the phase's artifacts as that change's chain: `proposal.md` (what/why distilled from the PRD, by the orchestrator), `design.md` (change-scoped how + ADR pointers, by the solution-architect), delta specs under `specs/` (Requirement/Scenario format, by the story-planner), and `tasks.md` (sequenced checklist referencing the story files, by the story-planner). Change artifacts SHALL distill and reference the PRD/HLD, never fork their content.

#### Scenario: Standard-track feature enters Solutioning

- **GIVEN** an approved PRD
- **WHEN** Solutioning runs to completion
- **THEN** `openspec/changes/<feature>/` contains proposal.md, design.md, at least one delta spec, and tasks.md, each owned by its designated role
- **AND** story files exist per the unchanged story schema, referenced from tasks.md

### Requirement: Readiness gate gains the openspec validate layer

The implementation-readiness gate SHALL run `openspec validate <feature>` as a deterministic layer alongside `lint-story.py`; a non-zero exit from either SHALL short-circuit the gate back to the story-planner (bounded iterations, then human escalation) before any LLM alignment review runs. A missing openspec CLI SHALL block the gate with a clear report, not pass it.

#### Scenario: Invalid change artifacts

- **GIVEN** a change whose delta spec fails validation
- **WHEN** the readiness gate runs
- **THEN** the gate short-circuits with the validator output, no LLM review runs, and the story-planner receives the rework

### Requirement: Archive closes Implementation

After the change's last story ships, the pipeline SHALL have the human trigger `openspec archive <feature>`, promoting the deltas into the living `openspec/specs/`; archiving SHALL never be automatic.

#### Scenario: Feature complete

- **WHEN** all tasks/stories of the change are done and shipped
- **THEN** the orchestrator names `openspec archive <feature>` as the required closing step and waits for the human

### Requirement: Workflow docs updated in the same change

Per the repo's doc-sync law, this rewiring SHALL land with `skills/sdlc-orchestration/SKILL.md`, `agents/sdlc-orchestrator.md`, `agents/story-planner.md`, `agents/README.md`, `docs/using-the-sdlc-dev-team.md`, and the affected figures (`solutioning-phase.svg`, `readiness-gate.svg`, amber = deterministic script) updated together, plus the `skills/prime` narration if it describes Solutioning steps.

#### Scenario: Mirror check

- **WHEN** the change ships
- **THEN** a grep across the playbook, figures, agents, and mirrors shows the propose step and validate layer described consistently everywhere the Solutioning flow is narrated

