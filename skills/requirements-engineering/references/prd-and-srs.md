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

## Quick mapping
PRD "FR with testable consequence" = 29148 *verifiable + singular*. PRD "NFR with a number" = 29148 *verifiable* quality requirement → architecture characteristic. PRD IDs = 29148 *traceability*. SPEC non-goals = scope boundary. Use the PRD spine day-to-day; reach for 29148 vocabulary when rigor/audit matters.
