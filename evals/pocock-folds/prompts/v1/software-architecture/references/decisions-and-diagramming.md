# Architecture decisions, risk & diagramming

From *Fundamentals of Software Architecture* (chs. 19–21), the C4 model (c4model.com), and Michael Nygard's ADRs.

## Architecture Decision Records (ADRs)

Record every **significant, hard-to-reverse** decision with its rationale — "why over how." Michael Nygard's format (one short markdown file per decision, numbered, in the repo):

```markdown
# N. <short title of the decision>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-M

## Context
The forces at play: the problem, constraints, characteristics, options considered.
(Facts and pressures — not the decision yet.)

## Decision
The change we're making, stated in active voice: "We will …".

## Consequences
What becomes easier AND harder as a result — the positive and the
**negative** outcomes, and any new risks/follow-ups.
```

Keep them immutable: don't edit an accepted ADR — supersede it with a new one and mark the old `Superseded by`. ADRs give you a decision log that survives team turnover and prevents re-litigating settled questions.

**Decision anti-patterns (ch. 19):**
- **Cover Your Assets** — avoiding/delaying a decision for fear of being wrong. Cure: decide at the last *responsible* moment, then commit.
- **Groundhog Day** — the same decision is re-debated repeatedly because the rationale was never captured. Cure: ADRs.
- **Email-Driven Architecture** — decisions made/announced in email/chat and then lost. Cure: ADRs in the repo as the single source of truth.

Criteria for a good decision: significance (is it architecturally significant?), rationale recorded, consequences (incl. negative) acknowledged, and **compliance ensured** (governance/fitness functions so the decision is actually followed — see `characteristics.md`).

## Analyzing architecture risk (ch. 20)

- **Risk matrix** — score each risk on **impact (1–3) × likelihood (1–3)** → 1–9; 1–2 low, 3–4 medium, 6–9 high. Drives prioritization.
- **Risk storming** — a collaborative technique: architects/devs **independently** mark areas of a diagram with risk for a *given* characteristic (availability, then scalability, then security, …), then **converge** and discuss divergences. Doing it per-characteristic and independently-then-together avoids groupthink and blind spots.
- **Agile story risk analysis** — assess risk per story during planning.
- Risk analysis is **continuous** — re-storm as the design and system evolve.

## Diagramming & communicating (ch. 21) + the C4 model

**The C4 model (Simon Brown)** — "maps of your code," a hierarchy at four zoom levels (use the top two most):

1. **System Context** — the system as one box, its **users** (actors) and the **external systems** it talks to. Audience: everyone, including non-technical.
2. **Container** — the deployable/runnable units *inside* the system: web app, mobile app, API service, database, message bus. (A "container" = an app or datastore, **not** a Docker container necessarily.) Audience: technical.
3. **Component** — the major components *inside one container* and their responsibilities/relationships.
4. **Code** — class/ER level. Rarely worth drawing by hand; generate if needed.

Supplementary C4 diagrams: **System Landscape** (multiple systems), **Dynamic** (runtime collaboration), **Deployment** (mapping containers to infrastructure).

**C4 principles:** a small, consistent **notation**; every diagram has a **title, legend/key**, and unambiguous labels (name + technology + responsibility); "notation independent" but consistent. It's a way to *think and communicate*, not a rigid standard.

**Richards & Ford diagramming guidelines:** titles on everything, consistent lines/arrows (specify what they mean), use keys, avoid "magic" (unexplained icons/colors), and keep labels meaningful. On standards: **UML** (class/sequence still useful), **C4** (recommended default for structure), **ArchiMate** (enterprise). 

**Practice:** default to **C4**, draw the top two levels, keep diagrams **as code** (Mermaid, Structurizr, PlantUML) so they live in the repo and version with the architecture. Pair with [[event-storming]]'s big-picture wall for the domain/flow view. And remember the book's point: the architect must **present** — a design nobody understands isn't done.
