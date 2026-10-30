# Architecture characteristics — catalog, identifying, measuring

From *Fundamentals of Software Architecture* (Richards & Ford), chs. 4–7. An architecture characteristic is a **non-domain** ("non-functional") concern that (a) influences structural design, (b) is critical/important to success, and (c) is implicit or explicit. They're the *drivers* of the whole design.

## The catalog (partial — the list is open-ended)

**Operational** (how the system runs):
- **Availability** — uptime (e.g. 99.9%).
- **Performance** — latency, throughput, response time under load.
- **Scalability** — handles more *users/requests* gracefully.
- **Elasticity** — handles *spikes*; ramps capacity up/down fast.
- **Reliability / safety** — fails rarely; safe when it does.
- **Recoverability** — RTO/RPO; how fast you recover from failure.
- **Continuity** — disaster recovery.

**Structural** (code/deployment quality):
- **Modularity, maintainability** — how easily you change it.
- **Extensibility** — how easily you add to it.
- **Deployability** — ceremony/frequency/risk of releasing.
- **Testability** — how amenable to automated testing.
- **Configurability, portability, supportability, localization.**

**Cross-cutting** (don't fit neatly):
- **Security** — auth, encryption, data protection.
- **Usability / accessibility** — learnability, reach.
- **Privacy, compliance** (GDPR/HIPAA/PCI), **auditability**, **authentication/authorization**.

## The trade-off reality

Characteristics **conflict** — more security usually costs performance; high scalability costs simplicity; elasticity costs cost. You **cannot maximize all** of them. Richards & Ford: pick the **driving** characteristics (rule of thumb: **keep it to ~7 or fewer**), and accept you're choosing the **"least worst"** combination, not an optimum. Naming too many is itself an anti-pattern — it dilutes the design.

## Identifying characteristics

Two sources:
1. **From domain concerns** — translate stakeholder priorities into characteristics. (e.g. "we're scaling to a new market" → scalability + localization; "we handle health data" → security + compliance + privacy.) Get stakeholders to pick their **top 3** — it forces prioritization.
2. **From requirements** — read them out of the explicit requirements ([[requirements-engineering]] NFRs).

Plus the split:
- **Explicit** — stated in the requirements.
- **Implicit** — never stated but expected anyway (availability, security, basic usability). Missing these is a common, expensive failure. Surface them.

## Measuring & governing

A characteristic you can't measure can't be designed for or defended.

- **Operational measures** — latency p50/p95/p99, throughput req/s, uptime %, RTO/RPO.
- **Structural measures** — cyclomatic complexity, coupling/cohesion metrics, % test coverage, deployment frequency/lead time (DORA — see [[devops]]).
- **Process measures** — agility, time-to-market.

**Fitness functions** — objective, automated tests of an architecture characteristic (e.g. an automated check that no cyclic dependencies exist, that p95 latency stays under budget, that no module imports across a boundary). Wire them into CI ([[github-actions]]) so the architecture is **governed continuously**, not just reviewed once. This is how "the architecture" stays true over time rather than decaying.

## Scope: the architecture quantum

Characteristics apply at the scope of an **architecture quantum** — an independently deployable artifact with high functional cohesion and its own data. Different quanta can have *different* characteristics (the payments service needs more security/availability than the reporting service). Identifying quanta tells you where characteristics differ and where you can split monolith → distributed.
