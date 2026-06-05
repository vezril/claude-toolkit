---
name: sdlc-orchestration
description: Orchestrating a multi-agent, AI-assisted software development lifecycle (SDLC) — the meta-skill that runs the pipeline from idea to shipped code. Covers the four phases (Analysis → Planning → Solutioning → Implementation), the maker-checker (generator + reviewer + clarifier) pattern per phase, artifact-driven state (the repo's files, not chat history, determine where you are), human-in-the-loop gates, required-vs-optional steps, the per-story build cycle, and the discipline of running each workflow in a fresh context and using a separate/stronger model for validation. Synthesizes the BMAD-method workflow and the multi-agent SDLC literature, adapted with execution-grounded review (run code/tests/plans, don't just opine). Use when planning or running an end-to-end feature/project with agents, deciding what SDLC step comes next, choosing which specialist skill/agent to invoke, setting up the artifact pipeline (brief → PRD/SRS → architecture → stories → code → tests), or coordinating a team of role agents. Routes to requirements-engineering, software-architecture, spec-driven-development, test-strategy, agentic-workflows, tdd, devops, and the role subagents.
---

# SDLC Orchestration

How to drive a feature or project through an **AI-assisted, multi-agent software development lifecycle** — the conductor that sequences the specialist roles, gates the handoffs, and keeps a human in the loop. Synthesized from the **BMAD method** workflow and the multi-agent SDLC literature, with one deliberate upgrade: **reviews are execution-grounded** (run the code, the tests, `terraform plan`, the linter) rather than the LLM-judgment-only gates the source material relies on.

This is the meta-skill. It owns *sequence and state*; the specialist skills own *content*. Cross-links: [[requirements-engineering]], [[software-architecture]], [[spec-driven-development]], [[test-strategy]], [[agentic-workflows]] (the runtime patterns), [[tdd]], [[clean-code]] / [[software-design]], [[domain-driven-design]] / [[event-storming]], [[devops]] / [[github-actions]].

## The four phases

A feature flows through four phases; each produces artifacts that become the *context* for the next. (Scrum equivalents in parentheses.)

1. **Analysis** (product discovery) — explore the problem before writing requirements. Optional: brainstorming, market/domain/technical research, a **product brief**. Output: brief + research notes.
2. **Planning** (backlog creation) — define *what* to build. Required: a **PRD/SRS**. Optional: validate/edit it, a **UX design**. Output: the requirements doc. → [[requirements-engineering]]
3. **Solutioning** (sprint 0 / technical refinement) — define *how*. Required: **architecture**, **epics & stories**, and an **implementation-readiness check** across PRD + architecture + stories. → [[software-architecture]], [[spec-driven-development]]
4. **Implementation** (sprint execution) — build it one story at a time. Required: **sprint planning**, **create story**, **dev story**. Optional but recommended: validate story, **QA automation**, **code review**, **retrospective** (per epic). → [[tdd]], [[test-strategy]], the reviewer agents

## The artifact pipeline

```
idea → product brief → PRD/SRS → architecture (+ ADRs) → epics & stories → code + tests → (deploy)
```

Each stage consumes the prior artifact and emits a new, versioned one. The PRD tells the architect which constraints matter; the architecture tells the dev which patterns to follow; the story gives focused, complete context for one unit of implementation. Keep artifacts as files in the repo.

## The maker-checker pattern (per phase)

Every phase decomposes into the same shape — this is the reusable unit:

- **Clarifier** — resolves ambiguity with the human/stakeholder *before* generating (turns "high performance" into a number).
- **Generator (maker)** — produces the artifact from its inputs.
- **Reviewer (checker)** — critiques it against the source artifacts and standards, and **(our addition) executes** what can be executed.

It loops, bounded, until the reviewer is satisfied or a max-iteration cap is hit, then a **human approves**. This maps to the role agents: requirements-analyst, solution-architect, story-planner, developer + reviewer, qa-test-architect.

## Operating principles (carry these over)

- **Artifacts drive state, not chat history.** Determine "where are we?" by which output files exist, not by what was said in the conversation. This makes the process resumable and stateless.
- **Required steps block progress.** You cannot skip the PRD, architecture, epics & stories, readiness check, sprint planning, story creation, or dev — each later phase depends on the prior artifact.
- **Run each workflow in a fresh context window.** Don't chain multiple phases in one conversation; load only the artifacts that phase needs (shard large docs — see [[spec-driven-development]]).
- **Use a separate, stronger model for validation.** Validation/readiness checks benefit from a different high-quality model than the generator, to avoid self-confirmation bias.
- **Human-in-the-loop at every gate.** The human approves phase transitions; agents propose, humans dispose.
- **Lock the *what* before the *how*.** Requirements and the SPEC kernel come before architecture and code ([[spec-driven-development]]).
- **Execute, don't opine.** A review that doesn't run the code/tests/plan is a guess. Ground every checker in real tool output. (The biggest weakness of the source frameworks.)

## Tracks (match process weight to the work)

- **Quick track** — bug fix / small feature: a lightweight spec + quick dev, skipping phases 1–3. (See [[spec-driven-development]] quick spec.)
- **Standard** — a product/feature: full PRD + architecture + stories.
- **Enterprise** — compliance/multi-tenant: add security and ops/IaC artifacts ([[secure-coding]], [[devops]]).

Don't run the heavyweight pipeline on a one-line change; don't vibe-code a platform.

## Roles → skills/agents map

| Phase | Role (agent) | Skill |
|-------|--------------|-------|
| Analysis | analyst / researcher | [[requirements-engineering]] |
| Planning | requirements-analyst (PRD/SRS) | [[requirements-engineering]], [[spec-driven-development]] |
| Solutioning | solution-architect | [[software-architecture]], [[domain-driven-design]], [[event-storming]] |
| Solutioning | story-planner (epics/stories) | [[spec-driven-development]] |
| Implementation | developer | [[tdd]], [[clean-code]], language skills |
| Implementation | qa-test-architect | [[test-strategy]] |
| Review/ops | reviewers, ci | [[clean-code]], [[secure-coding]], [[github-actions]] |

The runtime mechanics of wiring these agents together (orchestrator-worker, evaluator-optimizer, routing) live in [[agentic-workflows]].

## Anti-patterns

- Treating chat history as state instead of artifacts (loses resumability).
- Skipping the requirements/architecture artifacts and going straight to code on non-trivial work.
- One giant conversation that chains all phases (context pollution); not sharding large docs.
- Self-validation — the generator grading its own output with the same model.
- **LLM-judgment-only gates** that never run the code/tests — the cardinal sin to fix.
- Running the full heavyweight process on a trivial change.

## Always-apply

1. Identify the **phase** and the **track** first; produce/consume the right **artifact**.
2. Decompose each phase into **clarify → generate → review (execute) → human-approve**, bounded.
3. **Artifacts as state**, **fresh context per workflow**, **separate validator model**, **HITL gates**.
4. Route content work to the specialist skill/agent; keep this skill about sequence and state.
5. Ground every review in **real execution**.

## Related

- [[requirements-engineering]] · [[software-architecture]] · [[spec-driven-development]] · [[test-strategy]] — the phase specialists.
- [[agentic-workflows]] — how to wire the agents together at runtime (Anthropic patterns, Claude Agent SDK, LangGraph).
- [[tdd]] · [[clean-code]] · [[software-design]] · [[domain-driven-design]] · [[event-storming]] · [[secure-coding]] · [[devops]] · [[github-actions]] — invoked within phases.
- Sources: the BMAD-method workflow & docs (MIT); the multi-agent SDLC series (Aravinda Kumar); adapted with execution-grounded review.
