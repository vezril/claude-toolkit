---
name: requirements-engineering
description: Eliciting, structuring, and validating software requirements — producing a high-quality PRD/SRS that locks the "what" before the "how". Covers functional vs non-functional (quality) requirements, turning vague language into measurable/testable criteria, the PRD "spine" (vision, target users with jobs-to-be-done, user journeys, glossary, functional requirements with stable IDs and testable consequences, non-goals, MVP scope, success metrics with counter-metrics, assumptions/open questions), the SPEC kernel (Why / Capabilities / Constraints / Non-goals / Success signal), user-story writing (INVEST, role-action-benefit, splitting, acceptance criteria), structured elicitation techniques (5 Whys, pre-mortem, Socratic, tree-of-thoughts, etc.), and validation/Definition-of-Ready review. Synthesizes the BMAD PRD template + SPEC kernel + elicitation registry, Mike Cohn's user stories, and ISO/IEC/IEEE 29148 practice. Use when writing or reviewing a PRD/SRS/product brief, capturing or clarifying requirements, defining acceptance criteria, splitting epics into stories, quantifying non-functional requirements, or doing a requirements/Definition-of-Ready review. Feeds software-architecture and spec-driven-development; part of the sdlc-orchestration pipeline.
---

# Requirements Engineering

Turn fuzzy intent into a **clear, testable, prioritized requirements artifact** — a PRD/SRS that the architect and developers can build from without guessing. The governing rule (from [[spec-driven-development]]): **lock the *what* before the *how*.** Synthesizes the BMAD PRD template + SPEC kernel + elicitation registry, Mike Cohn's user-story practice, and ISO/IEC/IEEE 29148.

Sits in the Planning phase of [[sdlc-orchestration]]; feeds [[software-architecture]] and [[spec-driven-development]].

## Functional vs non-functional

- **Functional requirements** — *what the system does*: features, behaviors, inputs→outputs. Write each as a discrete, testable statement with a **stable ID** (`FR-1`, `FR-2`) so downstream artifacts (architecture, stories, tests) can reference it.
- **Non-functional / quality requirements (the "-ilities")** — *how well* it does it: performance, scalability, availability, security, usability, etc. These become the **architecture characteristics** that drive design ([[software-architecture]]). They are the most-skipped and most-expensive-to-retrofit, so capture them explicitly.

**Make the vague measurable.** "High performance" is not a requirement; "p95 API latency < 200 ms at 1,000 req/s" is. Every quality requirement needs a number and a way to verify it (see *Measuring* in [[software-architecture]]). If a stakeholder can't make it measurable, that's an open question, not a requirement.

## The PRD spine

A good PRD has an essential spine (adapt-in extras for consumer/enterprise/regulated contexts):

- **Vision** — the one-paragraph why.
- **Target users** — personas with **jobs-to-be-done** (the progress they're trying to make), not demographics.
- **Key user journeys** — the main flows, ID'd (`UJ-1`); functional requirements reference them.
- **Glossary** — shared definitions ([[domain-driven-design]]'s ubiquitous language starts here).
- **Functional requirements** — globally numbered `FR-N`, each with a **testable consequence** ("so that…/verified by…").
- **Non-goals** — what you're explicitly *not* doing (prevents scope creep and clarifies intent).
- **MVP scope** — the smallest releasable slice.
- **Success metrics** — how you'll know it worked, **with counter-metrics** (the thing that must *not* get worse). Each metric validates one or more FRs.
- **Assumptions & open questions** — surfaced, not buried.

See `references/prd-and-srs.md` for the full template and an ISO 29148 mapping.

## The SPEC kernel (the irreducible contract)

Before a full PRD — or for smaller work — distill intent into five fields ([[spec-driven-development]] uses this as the lock):

- **Why** — the motivating problem/goal.
- **Capabilities** — what it must let users do, each carrying its own **success signal**; stable `CAP-N` IDs.
- **Constraints** — the limits that actually bend decisions (tech, regulatory, time, budget).
- **Non-goals** — explicitly out of scope.
- **Success signal** — concrete, observable evidence the whole thing worked.

Rules of thumb: capabilities are **WHAT not HOW**; constraints must genuinely change a decision (or cut them); non-goals and success signals must be concrete; capability IDs are stable.

## User stories (the unit of implementation)

For the story breakdown ([[spec-driven-development]] turns these into story files):

- **Form:** "As a `<role>`, I want `<action>`, so that `<benefit>`." The benefit clause is what keeps stories user-centered.
- **INVEST** — good stories are **I**ndependent, **N**egotiable, **V**aluable, **E**stimable, **S**mall, **T**estable.
- **A story is a placeholder for a conversation**, not a spec — keep them lean; detail emerges in the "three amigos" (PO + dev + QA) discussion.
- **Acceptance criteria** make a story testable (Given/When/Then or a checklist); they're the bridge to [[test-strategy]].
- **Splitting** big stories: by workflow steps, business-rule variations, happy/error paths, CRUD operations, or data variations — not by architectural layer.

## Elicitation techniques

Requirements rarely arrive complete; pull them out deliberately. A registry worth keeping (pick 2–3 per session):

- **5 Whys** — drill from symptom to root need.
- **Pre-mortem** — "it's a year later and this failed; why?" surfaces risks and hidden requirements.
- **Socratic questioning** — challenge assumptions behind each stated need.
- **Tree/graph of thoughts** — branch options before committing.
- **Inversion / steelmanning / red-team** — argue the opposite or the strongest counter-case.
- **Jobs-to-be-done interview** — what progress is the user hiring this to make?
- **Working-backwards / PRFAQ** — write the press release first to stress-test the concept.

See `references/elicitation-and-validation.md` for the fuller catalog and how to run a session.

## Validation / Definition of Ready

A PRD/story isn't done because it's written — review it (ideally with a **different, stronger model** per [[sdlc-orchestration]]):

- Are all quality requirements **measurable**? Are FRs **testable** and ID'd?
- Do success metrics map to FRs? Are **non-goals** explicit? **Counter-metrics** present?
- Are assumptions and open questions surfaced (not silently resolved)?
- Is it internally consistent (no FR contradicting a constraint)?
- **Definition of Ready** for a story: clear, estimable, testable acceptance criteria, dependencies known.

## Anti-patterns

- Unmeasurable quality requirements ("fast", "secure", "scalable" with no number).
- Solutioning in the requirements ("use Postgres" is a *how* — belongs in [[software-architecture]] unless it's a real constraint).
- Requirements with no ID, so nothing downstream can trace to them.
- No non-goals (everything is in scope → scope creep).
- Success metrics with no counter-metric (optimizing one thing while quietly breaking another).
- Giant stories that aren't INVEST; acceptance criteria missing.
- Gathering requirements once and freezing them instead of refining (use correct-course in [[sdlc-orchestration]]).

## Always-apply

1. Separate **functional** from **non-functional**; make every quality requirement **measurable + verifiable**.
2. Give requirements **stable IDs** (`FR-N`/`CAP-N`/`UJ-N`) so architecture, stories, and tests can trace to them.
3. Always include **non-goals** and **counter-metrics**.
4. Write stories to **INVEST** with explicit **acceptance criteria**.
5. **Lock the what before the how**; validate with a separate reviewer; surface assumptions/open questions.

## How to use the references

- **`references/prd-and-srs.md`** — the PRD spine template, the SPEC kernel, and an ISO/IEC/IEEE 29148 mapping (requirement attributes, characteristics of a good requirement).
- **`references/elicitation-and-validation.md`** — the elicitation method catalog + how to run a session, and the validation / Definition-of-Ready checklist.

## Related

- [[spec-driven-development]] — turns the locked spec into stories and dev context.
- [[software-architecture]] — consumes the non-functional requirements as architecture characteristics.
- [[domain-driven-design]] / [[event-storming]] — modeling the domain and ubiquitous language behind the requirements.
- [[test-strategy]] / [[tdd]] — acceptance criteria become tests.
- [[sdlc-orchestration]] — the Planning phase this skill owns.
- Sources: BMAD PRD template + SPEC kernel + elicitation registry (MIT); Mike Cohn, *User Stories Applied* / Mountain Goat; ISO/IEC/IEEE 29148.
