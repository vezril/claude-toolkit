# CQRS & Event Sourcing — mechanics & gotchas

Depth on the two patterns plus the dual-write problem and the practitioner gotchas (Richardson's microservices.io; the CQRS community; the SSENSE "practical guide").

## CQRS

**The split.** Command side = the write model: handles commands, enforces invariants, owns the authoritative state, emits domain events. Query side = one or more read models: denormalized, query-shaped materialized views, updated by subscribing to those events. Generalizes **CQS** (Meyer: a method either changes state *or* returns a value, never both) from methods to models.

**Read-side projections.** A *projection* (a.k.a. view updater) consumes the domain event stream and writes a **read model** tuned for specific queries — a SQL view, Elasticsearch index, Redis cache, or document store. You can maintain **several** read models from the same events, each optimized for a different query/UI. The read model is disposable: you can rebuild it by **replaying** events (especially when event-sourced).

**Forces / when it pays.**
- A query needs data spanning multiple services (no cross-service JOIN) — CQRS (a view that subscribes to the services' events) or **API Composition** (query each service and join in memory — simpler, but inefficient/ chatty for large or complex joins).
- The write model and read model genuinely differ (normalized + invariant-heavy writes vs denormalized, fast reads).
- You need many different views of the same data, or independent read/write scaling.

**Drawbacks.** More components and operational complexity; **replication lag** → the read model is **eventually consistent** with the write model (design the UX for it: optimistic update, "pending", poll, or notify). Duplicated/derived data to manage.

**The caution (Greg Young, Fowler, cqrs.com).** CQRS is powerful but **easily over-applied**. It is *not* a system-wide architecture — use it **inside the bounded contexts where reads and writes diverge enough to justify it**. For straightforward CRUD it's needless complexity. cqrs.com / Young: most of a system should *not* be CQRS; introduce it surgically.

## Event Sourcing

**The model.** Instead of storing current state and mutating it, **append immutable domain events** to a per-aggregate stream; the **event log is the source of truth**. Rebuild current state by **replaying** events through an `apply` function: conceptually `state = foldLeft(emptyState)(events)(apply)` — pure, deterministic ([[functional-programming]]).

**Event store.** Append-only; operations are essentially `appendEvents(aggregateId, expectedVersion, events)` and `readStream(aggregateId)`. **Optimistic concurrency** via `expectedVersion` (reject if the stream moved). Often the store also publishes/【exposes a feed of】the appended events for subscribers.

**Reliable publishing (why it matters).** A service must **atomically** update its state *and* make the event available. Event sourcing achieves this because the event *is* the state change — one append, no dual write. (The alternative without event sourcing is the **Transactional Outbox** — write the event to an `outbox` table in the same local transaction as the state change, then a relay publishes it.)

**Benefits.** Built-in **audit trail** (every change, with intent); **temporal queries** / time-travel (replay to any point); eliminates ORM impedance mismatch; first-class fit for event-driven integration and CQRS; easy debugging ("what events led here?").

**Challenges & their fixes.**
- **Querying is hard** — you can only load by aggregate id; ad-hoc queries are impossible against the log → **pair with CQRS** read models.
- **Snapshots** — replaying thousands of events per load is slow → periodically persist a snapshot of state and replay only events after it.
- **Event versioning / schema evolution** — events are immutable and live forever, so v1 events must still be readable years later. Techniques: additive/weak schema (tolerant reader), **upcasting** (transform old event shapes to new on read), versioned event types, never repurpose a field.
- **Deleting data / GDPR** — you can't simply delete from an immutable log. **Crypto-shredding**: encrypt personal data per subject with a key; to "delete," discard the key (data becomes unrecoverable). See [[secure-coding]].
- **Idempotent consumers** — events may be delivered more than once (at-least-once); consumers/projections must dedupe (track processed event ids).
- **Eventual consistency** everywhere downstream.

## The dual-write problem (the trap both patterns address)

Updating the database and publishing to a message broker as **two separate operations** is unsafe: a crash between them loses the event (state changed, nobody told) or publishes a phantom (event sent, transaction rolled back). **Never** do `save(); publish();` as two steps. Fixes: **Event Sourcing** (the append is the publish) or **Transactional Outbox** (same-transaction outbox table + relay). This is the single most important reliability point in event-driven systems.

## Practical "getting it done" gotchas (SSENSE practical guide)

- **Don't event-source everything** — only aggregates that benefit (audit, complex state transitions, event-driven needs). CRUD lookups don't need it.
- **Model events around business intent**, not CRUD (`ItemAddedToCart`, not `CartRowUpdated`) — events are part of your domain language.
- **Plan versioning from day one** (you will change event shapes).
- **Snapshots and read models are rebuildable** — treat them as caches over the log, not sources of truth.
- **Idempotency + ordering** — design consumers for at-least-once delivery and per-aggregate ordering.
- **Eventual-consistency UX** — surface "pending"/"processing" states; don't assume read-after-write.
- **Operational maturity** — you now run an event store + projections + a broker; invest in observability ([[site-reliability-engineering]]).
- Start small: introduce ES in one aggregate/bounded context, with CQRS for its queries, before spreading it.
