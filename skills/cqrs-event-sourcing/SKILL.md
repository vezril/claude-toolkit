---
name: cqrs-event-sourcing
description: The event-driven data & consistency patterns for distributed/microservice systems — CQRS, Event Sourcing, Sagas, and Domain Events — distilled from Chris Richardson's microservices.io pattern language plus the CQRS/event-sourcing community. Covers why database-per-service forces these patterns; CQRS (separate command/write model from query/read model, read-side views/projections kept in sync via events, eventual consistency, when not to use); Event Sourcing (persist state as an immutable append-only sequence of domain events, the event store, rebuild by replay, snapshots, the dual-write problem and transactional outbox, event versioning, deletion/GDPR); Sagas (transactions spanning services without 2PC, choreography vs orchestration coordination, compensating transactions, lack-of-isolation countermeasures); and Domain Events (past-tense facts an aggregate publishes to drive consistency and reactions). Use when designing data consistency across services, deciding whether to apply CQRS/event sourcing, modeling sagas/compensation, choosing choreography vs orchestration, designing an event store or read-model projections, or reasoning about eventual consistency. Pattern-level and vendor-neutral; pairs with domain-driven-design, event-storming, software-architecture, and the Akka persistence/projections runtimes.
---

# CQRS & Event Sourcing (event-driven data patterns)

The interlocking patterns that solve the *hardest* part of microservices — **data consistency and querying across service boundaries** — distilled from **Chris Richardson's microservices.io** pattern language and the CQRS/event-sourcing community. Four patterns that travel together: **Domain Events**, **Event Sourcing**, **CQRS**, and **Sagas**.

These are **pattern-level and vendor-neutral**. Cross-links: [[domain-driven-design]] (aggregates/bounded contexts that emit and consume these events), [[event-storming]] (the workshop that discovers the domain events), [[software-architecture]] (the event-driven / microservices *style* these implement), [[akka-persistence]] (event sourcing on a concrete runtime), [[akka-projections]] (the CQRS read side on Akka), [[functional-programming]] (immutable events; state = left-fold over events), [[secure-coding]] (event-store GDPR / crypto-shredding).

## Why these patterns exist: database-per-service

In a microservice architecture each service owns its data ([[software-architecture]]'s **Database per Service**). That single choice creates two problems a monolith never had:

1. **A business transaction spans services** → you can't use one local ACID transaction (and **2PC is not an option**). → **Saga**.
2. **A query needs data from several services** → you can't `JOIN` across databases. → **CQRS** (or API Composition).

And to publish the events both rely on, **reliably**, you hit the **dual-write problem** (update the DB *and* publish an event atomically) → **Event Sourcing** (or Transactional Outbox), built on **Domain Events**. So the four patterns aren't independent fashions — they fall out of database-per-service. Underpinning all of it: **eventual consistency** replaces the immediate consistency of a monolith.

## Domain Events

A **domain event** is *something that happened to an aggregate that domain experts care about* — `OrderCreated`, `CreditReserved`, `PaymentFailed`. Properties:

- **Past tense**, immutable fact; carries the data describing what happened (+ id, timestamp, aggregate id).
- An **aggregate publishes** a domain event when its state changes; other aggregates/services subscribe to **maintain consistency** and **trigger reactions** (a saga step, a read-model update, a notification).
- This is the unit discovered on the [[event-storming]] wall and the messages of an event-driven architecture.

Domain events are the substrate the other three patterns are built from.

## Event Sourcing

> **Persist the state of an aggregate as a sequence of immutable domain events.** The event log — append-only — is the **source of truth**; current state is reconstructed by **replaying** the events.

- **Event store** — an append-only log of events per aggregate; you append new events and read the stream. (Conceptually `state = events.foldLeft(empty)(apply)` — a [[functional-programming]] left fold.)
- **Solves the dual-write problem reliably:** persisting the event *is* the state change, and the same event is what you publish — so updating state and emitting the event are one atomic act (Richardson lists event sourcing as a way to "atomically update state and publish events").
- **Benefits:** a perfect **audit log** / history; **temporal queries** ("what did this look like last Tuesday?"); no object-relational impedance mismatch; a natural fit for event-driven integration and CQRS.
- **Challenges:** it's unfamiliar; **querying the event store is hard** (you can only fetch by aggregate id) → almost always paired with **CQRS** for queries; **event versioning/schema evolution** (events live forever — use upcasting, weak schemas, versioned event types); **replay cost** at scale → **snapshots** (periodically persist a materialized state to replay from); **deleting data** is at odds with an immutable log → **crypto-shredding** for GDPR (encrypt per-subject, delete the key — see [[secure-coding]]).

See `references/cqrs-and-event-sourcing.md` for the mechanics and the practical "actually getting it done" gotchas.

## CQRS — Command Query Responsibility Segregation

> **Separate the model that handles commands (writes) from the model(s) that handle queries (reads).** The read side is one or more **materialized views** kept in sync by subscribing to the write side's **domain events**.

- Extends **CQS** (Bertrand Meyer: a method is either a command that changes state *or* a query that returns data, never both) from methods to whole models.
- **Why:** with database-per-service, a query spanning services has no home; and write models (normalized, invariant-enforcing) differ from read models (denormalized, query-shaped). CQRS lets each be optimized independently and supports **multiple denormalized read views** of the same events.
- **How the read side stays current:** the command side emits domain events (often via event sourcing); **projections** consume them and update read models (SQL view, search index, cache, document store).
- **Benefits:** efficient, purpose-built queries; multiple views; scales reads and writes independently; necessary companion to event sourcing.
- **Drawbacks:** more moving parts; **replication lag → eventual consistency** between write and read (the UI must handle "you won't see it instantly"); duplicated data.
- **The big caution (Greg Young / Fowler / cqrs.com):** CQRS is **not** a top-level architecture — apply it **per bounded context where it pays**, not to the whole system. For simple CRUD it adds cost for no benefit. "Most systems should not use CQRS for the entire system."

See `references/cqrs-and-event-sourcing.md`.

## Sagas

> **A business transaction that spans services, implemented as a sequence of local transactions**, each updating one service and publishing an event/message that triggers the next. On failure, run **compensating transactions** to undo the prior steps (no automatic rollback).

Two coordination styles:

- **Choreography** — no central coordinator; each local transaction **publishes domain events** that trigger the next participant. Simple, decoupled, good for few participants; can become hard to follow ("who reacts to what?") and risks cyclic dependencies as it grows.
- **Orchestration** — a central **saga orchestrator** tells each participant which local transaction to run (via command/reply). Easier to understand, test, and manage complex flows; centralizes coordination logic; the orchestrator can become a hotspot.

Key realities:
- **No isolation (the "I" in ACID).** Sagas are ACD, not ACID — concurrent sagas can see intermediate state → anomalies (lost update, dirty read). Apply **countermeasures**: semantic lock (e.g. a `PENDING` state), commutative updates, pessimistic view, reread value, by-value.
- **Compensation must be designed** — every forward step needs an explicit undo (cancel the order, release the credit). Some steps are **pivot** (the point of no return) or **retriable**.
- Reliable publishing still needs **event sourcing or the transactional outbox** (the dual-write problem applies to each local transaction).
- Answering a synchronous caller of an async saga: respond on completion, or return an id and let the client poll / get notified.

See `references/sagas-and-domain-events.md`.

## How they fit together

```
Database per Service ──forces──> Saga (cross-service consistency)
                     └─forces──> CQRS (cross-service queries)
Aggregates ──emit──> Domain Events ──> drive Sagas (choreography) & CQRS projections
Event Sourcing ──stores state as──> Domain Events  (and solves reliable publishing)
                                     everything runs on EVENTUAL CONSISTENCY
```

A common combination: aggregates are **event-sourced**, their **domain events** drive **CQRS** read models *and* **choreographed sagas**, with **snapshots** for replay and a **read model** for queries. But you can adopt each independently — CQRS without event sourcing (events from an outbox), sagas without event sourcing (outbox), etc.

## When NOT to use these

- **Simple CRUD / single service / strong-consistency needs** → a boring monolith with ACID transactions is *better*. Don't pay the eventual-consistency and complexity tax without the database-per-service problem that justifies it.
- **Event-sourcing everything** — reserve it for aggregates that benefit from audit/temporal/event-driven needs; not every table is an event stream.
- **CQRS on the whole system** — apply per bounded context where reads and writes genuinely diverge.
- These patterns trade **simplicity and immediate consistency** for **scalability, decoupling, and auditability**. Make that trade deliberately ([[software-architecture]]: everything is a trade-off).

## Anti-patterns

- Adopting CQRS/event sourcing for simple CRUD or a single-service app (complexity for nothing).
- Ignoring **eventual consistency** in the UX (assuming a read reflects a just-issued write).
- The **dual-write** bug: updating the DB then publishing an event in two steps without event sourcing/outbox (events lost on crash → inconsistent state).
- Sagas with **no compensating transactions**, or ignoring **isolation** anomalies (no countermeasures).
- **Distributed monolith**: synchronous request chains across services instead of events/sagas.
- Unversioned events / no schema-evolution plan; no snapshots (replays grow unbounded); no GDPR/deletion story for an immutable log.
- Choreography for a complex many-participant flow (unfollowable) — switch to orchestration.

## Always-apply

1. Reach for these only when **database-per-service** (or a real audit/temporal need) creates the problem — otherwise prefer a monolith + ACID.
2. **Domain events** are past-tense immutable facts; aggregates publish them.
3. **Event sourcing** = state as an append-only event log (replay to rebuild; snapshots; plan event versioning + deletion/GDPR); it also fixes reliable publishing.
4. **CQRS** = separate write/read models, read side as event-driven projections; **per bounded context**, not system-wide; design for **eventual consistency**.
5. **Sagas** for cross-service transactions: choreography (events, simple) vs orchestration (central, complex flows); **design compensations + isolation countermeasures**; publish via event sourcing/outbox (never a raw dual write).

## How to use the references

- **`references/cqrs-and-event-sourcing.md`** — CQRS read/write models & projections, the event store, snapshots, event versioning, deletion/GDPR, the dual-write problem & transactional outbox, and the SSENSE "actually getting it done" gotchas.
- **`references/sagas-and-domain-events.md`** — sagas (choreography vs orchestration, compensation, ACD & countermeasures, answering sync callers), domain events, and the database-per-service connective tissue.

## Related

- [[domain-driven-design]] — aggregates, bounded contexts, and the domain events these patterns move; CQRS/ES are tactical DDD's natural persistence.
- [[event-storming]] — the workshop that discovers domain events, commands, and policies (which become saga reactions).
- [[software-architecture]] — the event-driven & microservices styles + database-per-service that force these; the trade-off lens.
- [[akka-persistence]] — event-sourced entities on a concrete runtime; [[akka-projections]] — the CQRS read side.
- [[functional-programming]] — immutable events; current state as a fold over the event log.
- [[secure-coding]] — crypto-shredding for GDPR over an immutable event store.
- Sources: Chris Richardson, microservices.io (Saga, CQRS, Domain Event, Event Sourcing, Database per Service) & *Microservices Patterns*; the CQRS community (cqrs.com, Greg Young; CQS from Bertrand Meyer); practitioner guides (SSENSE).
