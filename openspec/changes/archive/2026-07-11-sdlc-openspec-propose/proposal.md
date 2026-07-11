# Proposal: sdlc-openspec-propose

## Why

The SDLC team's Solutioning phase produces architecture and stories as loose repo files, while the playbook only *mentions* OpenSpec as a brownfield option. Meanwhile this repo's own work has proven the OpenSpec propose flow (change container → proposal → design → delta specs → tasks → validate → archive) as the better spec-building discipline: artifact-driven state with a CLI that enforces it. Building the specs through `openspec propose` makes the pipeline's "artifacts drive state" principle mechanical instead of conventional.

## What Changes

- **Solutioning builds its specs through the OpenSpec propose flow.** After the PRD is approved, the orchestrator opens a change (`openspec new change <feature>`); the phase then fills the artifact chain: `proposal.md` (what/why distilled from the PRD), `design.md` (the change-scoped how + ADR pointers, from the solution-architect), `specs/` (delta specs in Requirement/Scenario format — the story-planner's spec-building step), `tasks.md` (sequenced checklist referencing the story files).
- **Story files stay the per-story implementation unit** — story-schema.md and `lint-story.py` are unchanged; `tasks.md` references the story files rather than replacing them.
- **The readiness gate gains a second deterministic layer:** `openspec validate --change <name>` runs alongside `lint-story.py`; either failing short-circuits the gate back to the story-planner ("gate mechanically before you gate with judgment").
- **Implementation consumes the change; archive closes it.** Dev runs against tasks.md + story files; after the last story ships, `openspec archive` promotes the deltas into the living specs — this becomes a required Implementation-phase closing step.
- **Doc-sync law honored in the same change (this is an SDLC-workflow rewiring):** `skills/sdlc-orchestration/SKILL.md`, `agents/sdlc-orchestrator.md`, `agents/story-planner.md`, `agents/README.md`, `docs/using-the-sdlc-dev-team.md` (Phase 3 walkthrough, worked example, cheat sheet), `docs/figures/solutioning-phase.svg` + `docs/figures/readiness-gate.svg` (amber = deterministic script boxes for `openspec validate`), and the `skills/prime` team bindings if affected.

## Capabilities

### New Capabilities
- `sdlc-solutioning-openspec`: the OpenSpec propose step in Solutioning — change container, artifact mapping, the validate layer in the readiness gate, and the archive step closing Implementation.

### Modified Capabilities
<!-- none in openspec/specs/ — the SDLC workflow was not previously specced; story-schema/lint-story deliberately untouched -->

## Impact

- Process docs + agents only — no scaffold scripts, no runtime code: the 8-9 files listed above.
- Non-goals: no change to story-schema.md / lint-story.py (the schema↔linter pairing rule stands); no change to the quick track (small fixes may still skip the pipeline; OpenSpec-lite remains available); no auto-archiving (the human closes the change).
