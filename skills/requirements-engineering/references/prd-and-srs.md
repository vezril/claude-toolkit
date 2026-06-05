# PRD / SRS template & the SPEC kernel

Templates and the requirements-quality standard. Adapted from the BMAD PRD template (MIT) and ISO/IEC/IEEE 29148.

## PRD template (the spine)

```markdown
# PRD: <Product / Feature>

## Vision
<One paragraph: the problem and the desired outcome — the "why".>

## Target Users
- **Persona A** — context; **Job to be done:** <the progress they're trying to make>
- ...

## Key User Journeys
- **UJ-1** <name> — <the flow, start to finish>
- **UJ-2** ...

## Glossary
- **Term** — definition (shared/ubiquitous language)

## Functional Requirements
- **FR-1** — <what the system does> — *so that* <testable consequence> (refs: UJ-1)
- **FR-2** — ...

## Non-Functional Requirements (quality attributes / "-ilities")
- **NFR-1 Performance** — p95 latency < 200 ms at 1,000 req/s
- **NFR-2 Availability** — 99.9% monthly
- **NFR-3 Security** — <measurable/verifiable statement>
  (these become the architecture characteristics — see software-architecture)

## Non-Goals
- Explicitly NOT doing X (and why)

## MVP Scope
- Smallest releasable slice: FR-1, FR-3 ...

## Success Metrics
- **SM-1** — <metric + target> (validates FR-1) — **counter-metric:** <must not get worse>

## Assumptions
## Open Questions
```

**Conventions:** stable IDs everywhere (`FR-N`, `NFR-N`, `UJ-N`, `SM-N`); every FR has a testable consequence; every metric names a counter-metric; cross-reference by ID (FRs → UJs, SMs → FRs).

## The SPEC kernel (lightweight contract)

For smaller work, or as the lock before a full PRD:

```markdown
# SPEC: <thing>
## Why         — motivating problem/goal
## Capabilities
- CAP-1 — <what users can do> · success: <observable signal>
- CAP-2 — ...
## Constraints — limits that actually bend decisions (tech/legal/time/budget)
## Non-goals   — explicitly out of scope
## Success signal — concrete, observable evidence the whole thing worked
```

"Spec law": capabilities carry intent + success; intents are WHAT not HOW; constraints must genuinely change a decision; non-goals explicit; success signals concrete; capability IDs stable. Lock the WHAT before the HOW; one canonical SPEC is the source of truth.

## ISO/IEC/IEEE 29148 — characteristics of a good requirement

Each requirement (and the set) should be:

- **Necessary** — removing it leaves a deficiency.
- **Unambiguous** — one interpretation only.
- **Complete** — needs no further amplification to be understood.
- **Singular** — one requirement, not several ANDed together.
- **Feasible** — achievable within constraints.
- **Verifiable** — you can test/inspect/demonstrate it's met (this is why measurability matters).
- **Correct** — accurately states a real need.
- **Conforming** — follows the standard form/template.

Set-level: **consistent** (no contradictions), **complete** (no gaps), **non-redundant**, **traceable** (forward to design/tests, backward to source need — this is what the stable IDs enable).

**Requirement attributes to record** (29148): identifier, priority (e.g. MoSCoW: Must/Should/Could/Won't), source/rationale, status, and verification method (test / analysis / inspection / demonstration).

## The four 29148 specification documents

29148 (clause 9) defines a progression of requirement information items, each for a different stakeholder/abstraction level — useful when you need formal rigor beyond a single PRD:

- **BRS — Business Requirements Specification** — the *business* view: business purpose/scope, major stakeholders, business processes, operational policies/rules, operational modes, **high-level operational concept** and scenarios, business-operational quality, project constraints. (The "why the business wants this.")
- **StRS — Stakeholder Requirements Specification** — the *user/stakeholder* view: stakeholder purpose & scope, the stakeholders, system processes, operational policies/rules/constraints, operational modes & states, **user requirements**, operational concept and scenarios. (The "what users need.")
- **SyRS — System Requirements Specification** — the *system* view (often spanning hardware+software): functional requirements, usability, performance, system-interface requirements, modes/states, physical characteristics, environmental conditions, **security**, information management, policy/regulation, life-cycle sustainment, packaging/handling/shipping.
- **SwRS / SRS — Software Requirements Specification** — the *software* view: the classic SRS (functional + the quality requirements / "-ilities", interfaces, constraints).

For most product work a single **PRD** (the spine above) collapses BRS+StRS+SwRS pragmatically; reach for the separate 29148 items in regulated, safety-critical, systems-engineering, or contractual contexts. The flow BRS → StRS → SyRS → SwRS mirrors the toolkit pipeline: business intent → user needs → system architecture ([[software-architecture]]) → software requirements.

## Requirement attributes & measurement (29148)
Record per requirement: **identifier**, **priority** (e.g. MoSCoW), **source/rationale**, **status**, **verification method** (test / analysis / inspection / demonstration), and dependencies. 29148 also calls for **measurement** of requirements (size/volatility/traceability coverage) — i.e. you can manage the requirement set quantitatively, not just write it.

## Quick mapping
PRD "FR with testable consequence" = 29148 *verifiable + singular*. PRD "NFR with a number" = 29148 *verifiable* quality requirement → architecture characteristic. PRD IDs = 29148 *traceability*. SPEC non-goals = scope boundary. PRD "vision + target users" ≈ BRS/StRS; "FR/NFR" ≈ SwRS. Use the PRD spine day-to-day; reach for the 29148 document set and attribute/verification vocabulary when rigor, safety, or audit matters.
