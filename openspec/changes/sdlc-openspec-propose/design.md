# Design: sdlc-openspec-propose

## The Solutioning phase, rewired

```
Before:  PRD ──► solution-architect ──► story-planner ──► readiness gate ──► Implementation
                 (architecture+ADRs)    (epics/stories)   (lint-story → LLM → human)

After:   PRD ──► openspec new change <feature>            ← orchestrator opens the container
                 ├─ proposal.md   ← what/why from the PRD (orchestrator distills; human confirms scope)
                 ├─ design.md     ← solution-architect: change-scoped how + ADR pointers
                 ├─ specs/…       ← story-planner: delta specs (Requirement/Scenario, ADDED/MODIFIED/REMOVED)
                 └─ tasks.md      ← story-planner: sequenced checklist referencing the story files
                 story files      ← story-planner, unchanged schema (lint-story.py still normative)
         ──► readiness gate ──► Implementation ──► … ──► openspec archive
             layer 0a: lint-story.py <stories-dir>
             layer 0b: openspec validate --change <feature>     ← NEW, same short-circuit rule
             layer 1:  LLM alignment review
             layer 2:  human approval
```

## Decisions

**The change container opens at the start of Solutioning, not Planning.** The PRD remains a
standalone repo document (Planning's artifact, reusable across changes); `proposal.md` is its
distillation for one change. Greenfield and brownfield now take the same path — the playbook's
"brownfield? use delta specs" note becomes the standard route.

**Ownership per artifact follows the existing cast.** Orchestrator: opens the change, writes
proposal.md (sequence-and-state work, not content). Solution-architect: design.md — the
system-level HLD/ADRs stay repo docs; design.md carries only this change's how and points at
them. Story-planner: delta specs + tasks.md + story files — "building the specs" is one role's
territory, keeping maker-checker intact.

**Two deterministic gate layers, one rule.** `lint-story.py` checks story form;
`openspec validate` checks change-artifact form. Either non-zero exit short-circuits the
readiness gate straight back to the story-planner (bounded, ~3 iterations, then escalate) —
identical semantics to the existing lint layer, so the gate figure gains one amber box, not a
new concept.

**Archive is Implementation's closing step.** After the last story ships and the retrospective
runs, `openspec archive <feature>` promotes the deltas into `openspec/specs/` — the living
specs become the system's source of truth over time. Human-triggered, never automatic.

**Figures:** `solutioning-phase.svg` gains the change-container framing around the
architect/story-planner boxes; `readiness-gate.svg` gains the `openspec validate` amber box
beside `lint-story.py`. Color language per CLAUDE.md: amber = deterministic script; the
propose artifacts themselves are teal/LLM work.

**Prime bindings:** the stack-binding table routes *roles*; OpenSpec is stack-neutral, so
prime changes only if its playbook narrates Solutioning steps (check during implementation;
update the narration, not the bindings).

## Risks

- Artifact duplication drift (PRD ↔ proposal.md, HLD ↔ design.md): mitigated by the
  distill-and-point rule — change artifacts summarize and reference, never fork content.
- The openspec CLI becomes a hard dependency of the pipeline's gate: acceptable — it's already
  a dependency of this repo's own process; the gate reports a missing CLI as a blocked gate,
  not a pass.
- Docs are the implementation here; the risk is a missed mirror file. The task list enumerates
  every surface named by the CLAUDE.md doc-sync law, and the final task greps for stragglers.
