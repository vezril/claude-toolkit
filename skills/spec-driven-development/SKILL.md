---
name: spec-driven-development
description: Spec-driven development for AI-assisted coding — lock the "what" in a canonical spec before any "how," then drive implementation from sharded, self-contained story/spec files. Covers the SPEC kernel (Why / Capabilities with success signals / Constraints / Non-goals / Success signal) and "spec law," the intent-before-implementation discipline, decomposing a spec into epics and INVEST stories, the self-contained story file (context, acceptance criteria, references, dev record) so each unit of work needs no extra chat history, document sharding for context management, and quick-spec vs full-spec tracks. Adapted from the BMAD spec kernel and story workflow. Use when starting a feature with AI agents, writing a spec or story file, breaking a PRD/architecture into stories, deciding what context an implementation step needs, or sharding a large doc. Pairs with requirements-engineering (the upstream PRD) and sdlc-orchestration (the pipeline); the stories feed tdd and the developer agents.
---

# Spec-Driven Development

Make the **specification the source of truth** for AI-assisted implementation: distill intent into a canonical spec, **lock the *what* before the *how***, then hand the agent **self-contained units of work** that carry their own context. Adapted from the BMAD SPEC kernel and story workflow. This is the discipline that makes [[sdlc-orchestration]]'s "artifacts drive state" and "fresh context per workflow" actually work.

Cross-links: [[requirements-engineering]] (the upstream PRD/SRS this draws from), [[software-architecture]] (constraints that shape stories), [[tdd]] (acceptance criteria → tests), [[sdlc-orchestration]] (the pipeline).

## Why spec-first for agents

Agents make **inconsistent decisions** when context is implicit or scattered across a chat. A written spec + focused story files give every step a stable, complete, reviewable context — so work is **resumable, parallelizable, and auditable**, and the model isn't guessing what was decided three messages ago. The mantra: *lock the WHAT before the HOW.*

## The SPEC kernel

Distill any intent into five fields (also in [[requirements-engineering]]); this is the contract everything else derives from:

- **Why** — the motivating problem/goal.
- **Capabilities** — what the system must let users do; **each carries its own success signal**; stable `CAP-N` IDs.
- **Constraints** — the limits that genuinely bend decisions (tech, regulatory, time, budget).
- **Non-goals** — explicitly out of scope.
- **Success signal** — concrete, observable evidence the whole thing worked.

**Spec law (the rules that keep a spec honest):**
1. Capabilities carry **intent + success**, not implementation.
2. Intents are **WHAT, not HOW**.
3. Constraints must **actually change a decision** (else cut them).
4. **Non-goals explicit.**
5. **Success signals concrete** (observable/measurable).
6. **Capability IDs stable** across edits.
7. Every load-bearing source claim is **preserved**.
8. Prose stays **lean**.

**Mutation contract:** there is **one canonical spec file**, and it's the single writer/source of truth. Edits go through it; downstream artifacts reference its IDs.

## From spec to stories

Decompose the locked spec (and the [[software-architecture]] it produced) into **epics → stories**:

- **Epic** — a coherent slice of capability (group of related stories).
- **Story** — one INVEST unit (Independent, Negotiable, Valuable, Estimable, Small, Testable) — see [[requirements-engineering]]. Sequence stories so dependencies come first; in BMAD's v6 ordering, stories are created **after** architecture, because the tech decisions shape how work splits.

## The self-contained story file

The key artifact for implementation. A story file carries **everything an agent needs to implement it in a fresh context** — no reliance on chat history:

```markdown
# Story {epic}.{n}: {title}
Status: ready-for-dev
## Story
As a {role}, I want {action}, so that {benefit}.
## Acceptance Criteria
- AC-1 … (Given/When/Then or checklist — testable)
## Tasks / Subtasks
- [ ] Task (AC: #)
## Dev Notes
- Constraints, patterns to follow (from architecture)
### References
- [Source: docs/prd.md#FR-3]
- [Source: docs/architecture.md#api-patterns]
## Dev Agent Record   (filled during implementation)
- Model used / Debug log / Completion notes / File list
```

The **References** section is what makes it self-contained — it points at the exact spec/architecture sections, so the dev agent loads only those. Acceptance criteria are the contract for [[tdd]] and [[test-strategy]].

## Document sharding (context management)

Large docs (500+ lines: a big PRD or architecture) blow an agent's context and bury the relevant part. **Shard** them: split on level-2 (`##`) headers into a folder of numbered section files (`01-context.md`, `02-data-architecture.md`, …) plus an `index.md`. Then a story references only the shard it needs. Sharding enables **parallel work** and keeps each agent's context focused — the practical mechanism behind "fresh context per workflow."

## Tracks

- **Quick spec** — for a small/simple task: a one-page spec (`spec-*.md`) capturing intent + acceptance, then implement directly. Skips the full PRD/architecture pipeline.
- **Full spec-driven** — for a product/feature: PRD ([[requirements-engineering]]) → architecture ([[software-architecture]]) → epics & stories → per-story dev. The default for non-trivial work.

Match the track to the work (see [[sdlc-orchestration]] tracks); don't write a full PRD for a typo fix, don't vibe-code a platform.

## Anti-patterns

- Implementation details leaking into the spec (HOW in the WHAT).
- Multiple competing "spec" files — no single source of truth.
- Story files that depend on chat history instead of carrying their own references (breaks fresh-context resumability).
- Stories without testable acceptance criteria.
- Feeding a whole 1,000-line doc into the agent instead of sharding to the relevant section.
- Editing accepted capabilities without keeping IDs stable (breaks traceability).

## Always-apply

1. **Lock the WHAT** in a canonical SPEC (5 fields, spec law) before any HOW.
2. One **canonical spec**; downstream artifacts reference its stable IDs.
3. Decompose into **INVEST stories** with **testable acceptance criteria**.
4. Make each **story file self-contained** (references the exact spec/architecture sections).
5. **Shard** large docs; give each agent only the context it needs.

## Related

- [[requirements-engineering]] — the PRD/SRS and elicitation upstream of the spec.
- [[software-architecture]] — the constraints and patterns stories must follow.
- [[tdd]] / [[test-strategy]] — acceptance criteria become tests.
- [[sdlc-orchestration]] — artifacts-as-state and fresh-context principles this implements.
- Source: the BMAD spec kernel + story/sharding workflow (MIT), adapted.
