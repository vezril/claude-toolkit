---
name: software-architecture
description: System-level software architecture, distilled from Richards & Ford's *Fundamentals of Software Architecture* plus the C4 model (diagramming) and Michael Nygard's ADRs (decisions). Covers architecture characteristics (the operational/structural/cross-cutting "-ilities"), identifying/measuring/governing them, modularity, components and the architecture quantum, the major architecture styles (layered, pipeline, microkernel, service-based, event-driven, space-based, orchestration-driven SOA, microservices) with their trade-off ratings, choosing a style, making and recording architecture decisions (ADRs + anti-patterns), analyzing architecture risk (risk matrix, risk storming), diagramming/communicating architecture (C4's Context/Container/Component/Code levels, UML/ArchiMate), and the architect role (trade-off analysis, breadth over depth, leadership). Use when designing or reviewing system architecture, choosing an architecture style, identifying/measuring non-functional characteristics, writing an HLD or an ADR, doing architecture risk analysis, or producing C4 diagrams. Sits above software-design (module level) and consumes requirements-engineering's non-functional requirements; part of the sdlc-orchestration Solutioning phase.
---

# Software Architecture

Design and reason about systems at the **architecture level** — the structure, the cross-cutting characteristics, the styles, and the consequential, hard-to-reverse decisions. Distilled from **Richards & Ford, *Fundamentals of Software Architecture*** (the spine), the **C4 model** (diagramming), and **Michael Nygard's ADRs** (decisions). The throughline of the book: **everything in architecture is a trade-off; there are no right answers, only the "least worst" set of trade-offs** — so the architect's job is to *analyze* trade-offs, not chase a best.

Sits one level **above** [[software-design]] (deep modules / module-level complexity) and consumes the non-functional requirements from [[requirements-engineering]] as its driving characteristics. Owns the Solutioning phase of [[sdlc-orchestration]]. Cross-links [[domain-driven-design]] / [[event-storming]] (the domain model behind partitioning) and [[devops]] (deployment/operational concerns).

## What architecture is

Richards & Ford define it as the union of four things: the **structure** (the style — microservices, layered, …), the **architecture characteristics** (the "-ilities" the system must support), the **architecture decisions** (the rules for how it's built), and the **design principles** (guidelines, not hard rules). The first law: *"Everything in software architecture is a trade-off."* Corollary: *"Why is more important than how."*

## Architecture characteristics (the "-ilities")

A characteristic is a **non-domain** requirement that influences structure. Three buckets:

- **Operational** — availability, performance, scalability, elasticity, reliability, recoverability, continuity.
- **Structural** — modularity, maintainability, extensibility, deployability, testability, configurability, portability.
- **Cross-cutting** — security, usability, accessibility, privacy, authentication/authorization, compliance.

Key disciplines:
- **Choose few.** Supporting every characteristic is impossible (they conflict — e.g. security vs performance, simplicity vs scalability). Pick the handful that actually matter; this is the "least worst" choice. Prefer the *driving* characteristics, ideally ≤ 7.
- **Identify** them from **domain concerns** (stakeholder priorities) and from **requirements** (explicit) — plus the **implicit** ones nobody states but everyone expects (e.g. security). → `references/characteristics.md`
- **Measure & govern.** A characteristic you can't measure is a wish. Define operational/structural/objective measures, then govern with fitness functions / automated checks in CI ([[github-actions]]).

These characteristics are exactly the **non-functional requirements** from [[requirements-engineering]] — made measurable and turned into design drivers.

## Modularity, components & the quantum

- **Modularity** is the conceptual grouping; **components** are the physical building blocks (the unit of the architecture). Component-based thinking: partition the system, identify initial components, **assign requirements to them**, analyze their characteristics, restructure, and watch **granularity**.
- Two partitioning axes: **technical partitioning** (layers) vs **domain partitioning** (by business area — aligns with [[domain-driven-design]]). Conway's Law makes this an org decision too.
- **Architecture quantum** — an independently deployable unit with high functional cohesion and its own data. The number of quanta is the key fork: **monolithic (single quantum)** vs **distributed (many)**.

## Architecture styles

Each style is a fundamental structure with a characteristic **trade-off profile** (the book rates each on a star scale). Know them, and pick by fit — see `references/styles.md` for the comparison:

- **Layered (n-tier)** — simple, low cost; weak on scalability/elasticity/deployability. Good default/starter; watch the "architecture sinkhole" anti-pattern.
- **Pipeline (pipes & filters)** — sequential transforms; great modularity/testability; ETL, data flows.
- **Microkernel (plug-in)** — core + plug-ins; great extensibility; products/IDEs/tools.
- **Service-based** — coarse-grained domain services sharing a DB; pragmatic middle ground, much of microservices' benefit with less complexity.
- **Event-driven** — async, broker/mediator topologies; high scalability/responsiveness; hard to test/reason about; pairs with [[event-storming]] and [[akka]].
- **Space-based** — replicated in-memory data grid to remove the DB bottleneck; extreme elasticity/scalability; high complexity.
- **Orchestration-driven SOA** — enterprise service bus, heavy reuse; mostly historical/cautionary.
- **Microservices** — fine-grained, independently deployable, database-per-service, bounded contexts ([[domain-driven-design]]); high deployability/scalability/evolvability but distributed-systems tax (transactions → **sagas**, observability → [[site-reliability-engineering]]).

**Distributed ≠ better.** The book's *fallacies of distributed computing* (network is reliable/zero-latency/infinite-bandwidth/secure/…) are mandatory reading before going distributed.

## Choosing a style

Decide from: the **architecture characteristics** that dominate, the **domain partitioning** vs technical, the **number of quanta** needed, data architecture, and team/Conway constraints. There is no universal best — derive the **least-worst** fit for *these* drivers. → `references/styles.md` has the decision criteria.

## Architecture decisions & ADRs

Significant, hard-to-reverse decisions must be **recorded with their rationale** ("why over how"). Use **ADRs** (Michael Nygard format): **Title, Status** (proposed/accepted/deprecated/superseded), **Context, Decision, Consequences** (positive *and* negative). Avoid the decision anti-patterns: **Cover Your Assets** (won't decide for fear of being wrong), **Groundhog Day** (re-deciding because rationale wasn't recorded), **Email-Driven Architecture** (decisions lost in inboxes). → `references/decisions-and-diagramming.md`

## Analyzing architecture risk

- **Risk matrix** — rate each risk on **impact × likelihood** (low/medium/high) → a 1–9 score.
- **Risk storming** — a collaborative pass where architects independently mark risk areas on a diagram, then converge; do it per characteristic (availability, scalability, security…).
- Also: agile story risk analysis. Risk analysis is continuous, not a one-time gate.

## Diagramming & communicating

- **C4 model** — four zoom levels: **Context** (system + users + external systems), **Container** (apps/services/datastores), **Component** (inside a container), **Code** (rarely needed). "Maps, not blueprints" — a hierarchy of diagrams at different zoom for different audiences. → `references/decisions-and-diagramming.md`
- The book's diagramming guidelines (titles, consistent notation/keys, no magic) and a note on **UML / C4 / ArchiMate**. Use C4 by default; pair with **Mermaid**/diagrams-as-code so they live in the repo.
- The architect must also **present** — communication is half the job.

## The architect role

Architects **make architecture decisions, continually analyze** the architecture (keep it from decaying), keep current with trends, ensure compliance with decisions, have broad **breadth over deep specialization**, possess business-domain knowledge, and have **interpersonal/leadership** skill (negotiation, facilitation, leading by example). The "least worst" mindset and trade-off analysis are the core competence.

## Anti-patterns

- Chasing a "best" architecture instead of the **least-worst trade-off** for the actual drivers.
- Trying to support **every** characteristic (they conflict; you get none well).
- **Unmeasurable** characteristics ("scalable" with no number).
- Going **distributed/microservices** by default, ignoring the fallacies and the complexity tax.
- Decisions with **no recorded rationale** (Groundhog Day) or **no decision** at all (Cover Your Assets).
- Architecture diagrams with inconsistent/implicit notation; "ivory tower" architects who don't code or communicate.
- Generic layered architecture as a reflex when the drivers call for something else.

## Always-apply

1. Start from the **driving characteristics** (≤ ~7, measurable) derived from [[requirements-engineering]] NFRs.
2. Pick the **least-worst style** for those drivers + domain + quanta; respect the distributed-computing fallacies.
3. **Record consequential decisions as ADRs** (context, decision, consequences incl. negatives).
4. **Risk-storm** the design against each key characteristic.
5. Communicate with **C4** (maps at multiple zoom), notation consistent, diagrams-as-code in the repo.

## How to use the references

- **`references/characteristics.md`** — the operational/structural/cross-cutting catalog; identifying (domain vs requirements, explicit vs implicit); measuring & governing (fitness functions).
- **`references/styles.md`** — each style's description, when to use, and trade-off ratings; the decision criteria and the distributed-computing fallacies.
- **`references/decisions-and-diagramming.md`** — the ADR template + anti-patterns, risk matrix/storming, and the C4 model in detail.

## Related

- [[software-design]] — the level below: deep modules, complexity, interfaces (Ousterhout).
- [[requirements-engineering]] — supplies the non-functional requirements that become characteristics.
- [[domain-driven-design]] / [[event-storming]] — domain partitioning, bounded contexts, event-driven design.
- [[devops]] / [[site-reliability-engineering]] / [[github-actions]] — deployability, operations, fitness-function governance.
- [[akka]] — a concrete actor/event-driven runtime for several of these styles.
- [[sdlc-orchestration]] — the Solutioning phase this skill owns.
- Sources: *Fundamentals of Software Architecture* (Mark Richards & Neal Ford, O'Reilly 2020); the C4 model (Simon Brown, c4model.com); ADRs (Michael Nygard).
