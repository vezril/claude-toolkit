# Architecture styles — profiles, ratings, choosing

From *Fundamentals of Software Architecture* (Richards & Ford), Part II (chs. 9–18). Each style is a fundamental structure with a distinct **trade-off profile**; the book rates each on a 1–5 star scale across characteristics. Below: what each is, when to reach for it, and its standout strengths/weaknesses.

## Monolithic vs distributed (the first fork)
The number of **architecture quanta** is the deepest split. **Monolithic** (single deployable): simpler, cheaper, easier to reason about; limited independent scaling/deployment. **Distributed** (many quanta): scalability, deployability, evolvability — at the cost of the **fallacies of distributed computing** (below) and operational complexity. Don't go distributed without the drivers to justify it.

## The styles

**Layered (n-tier)** — presentation/business/persistence/database layers, each closed.
- *Use when:* small apps, tight budget/time, starting out, simple domains.
- *Strong:* simplicity, cost, ease of build. *Weak:* scalability, elasticity, deployability, fault tolerance. *Watch:* the **architecture sinkhole anti-pattern** (requests pass through layers doing nothing).

**Pipeline (pipes & filters)** — unidirectional pipes between stateless filters (transformers).
- *Use when:* ETL, data transformation, sequential processing, shell-style composition.
- *Strong:* modularity, testability, simplicity. *Weak:* elasticity, fault tolerance.

**Microkernel (plug-in)** — a minimal core system + plug-in components.
- *Use when:* products, IDEs, tools, apps with clear customization/extension points.
- *Strong:* extensibility, maintainability, testability, simplicity. *Weak:* scalability, elasticity (usually a single quantum).

**Service-based** — a few **coarse-grained** domain services + a shared database + (often) a UI.
- *Use when:* you want much of microservices' modularity/agility without the distributed-data complexity — a pragmatic, popular middle ground.
- *Strong:* deployability, testability, evolvability, cost/simplicity (vs microservices). *Weak:* elasticity (coarse), shared-DB coupling.

**Event-driven** — async event flow; **mediator** topology (orchestrated) or **broker** topology (choreographed).
- *Use when:* high scalability/responsiveness, complex async workflows, reactive systems.
- *Strong:* performance, scalability, elasticity, fault tolerance. *Weak:* testability, simplicity, hard to reason about; eventual consistency. Pairs with [[event-storming]] and [[akka]].

**Space-based** — replicated in-memory data grid + processing units; removes the central DB bottleneck (data pumped async to the DB).
- *Use when:* extreme/variable load (ticketing, flash sales), elasticity is paramount.
- *Strong:* elasticity, scalability, performance. *Weak:* testability, simplicity, cost — high complexity.

**Orchestration-driven SOA** — enterprise service bus, heavy taxonomy and reuse.
- *Mostly cautionary/historical:* reuse goals created tight coupling and brittleness. Know it to avoid it.

**Microservices** — fine-grained, single-purpose, **independently deployable** services; **database-per-service**; bounded by [[domain-driven-design]] contexts; communicate via API/events.
- *Use when:* independent deployability/scalability per capability, many teams, high evolvability.
- *Strong:* deployability, evolvability, scalability, fault isolation, testability (per service). *Weak:* performance (network hops), simplicity, cost; **distributed transactions** require **sagas**; needs serious observability ([[site-reliability-engineering]]).

## The fallacies of distributed computing (read before going distributed)
The network is reliable · latency is zero · bandwidth is infinite · the network is secure · topology doesn't change · there is one administrator · transport cost is zero · the network is homogeneous. Each is false; each is a source of production incidents. Distributed architectures must design *against* all eight.

## Choosing a style (decision criteria, ch. 18)
Derive the **least-worst** fit from:
1. **Dominant architecture characteristics** — which "-ilities" drive (from `characteristics.md`). Match to the style whose profile favors them.
2. **Domain vs technical partitioning** — domain-partitioned (microservices, service-based) vs technically layered.
3. **Number of quanta** — single (monolithic styles) vs many (distributed). Do parts of the system need *different* characteristics? → distributed.
4. **Data architecture** — shared DB (service-based) vs database-per-service (microservices) vs in-memory grid (space-based).
5. **Team topology & Conway's Law** — the architecture will mirror the org; choose deliberately.
6. **Cost & complexity budget** — the simplest style that meets the drivers wins.

There is **no universally best style** — only the best trade-off for *these* drivers, teams, and constraints. Start as simple as the drivers allow (often a monolith/modular-monolith); distribute when a real driver forces it.
