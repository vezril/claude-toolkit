# Sagas & Domain Events — detail

Depth on sagas and domain events, and the database-per-service tissue that connects all four patterns. (Richardson's microservices.io, *Microservices Patterns*.)

## Domain Events

**Definition.** *An event representing something that happened to an aggregate that domain experts care about.* Past-tense, immutable, named in the ubiquitous language ([[domain-driven-design]]): `OrderCreated`, `CreditReserved`, `OrderApproved`, `PaymentFailed`.

**Shape.** Event type/name, aggregate id, timestamp, sequence/version, and the payload describing what changed. Keep them about *business facts*, not database rows.

**Uses.**
- **Maintain consistency across aggregates/services** — when one aggregate changes, it publishes an event; others react to stay consistent (the eventual-consistency alternative to a cross-aggregate transaction).
- **Trigger reactions** — a saga step, a CQRS projection update, a notification, an analytics feed.
- The messages of event-driven integration; the things discovered as orange stickies in [[event-storming]].

**Relationship to the others.** Event sourcing *stores* state as domain events. CQRS read models are *built from* domain events. Choreographed sagas are *coordinated by* domain events. So getting your domain events right (granularity, naming, payload) underpins everything.

## Sagas

**Problem.** With Database per Service, a business transaction spanning services can't be a single ACID transaction, and **2PC is not an option** (poor availability, not supported by many modern data stores/brokers).

**Solution.** Implement the transaction as a **sequence of local transactions**. Each local transaction updates one service's database and publishes a message/event that triggers the next. If a step fails a business rule, run **compensating transactions** to undo the prior steps.

### Choreography vs Orchestration

**Choreography** — decentralized; each service's local transaction **publishes domain events** that trigger the next participant's local transaction.
- *Pros:* simple, loosely coupled, no central component; good for a few participants.
- *Cons:* the flow is implicit/scattered (hard to understand and monitor); risk of cyclic dependencies; harder to test as it grows.

**Orchestration** — centralized; a **saga orchestrator** sends command messages to participants telling them which local transaction to run, and receives replies to decide the next step.
- *Pros:* the flow is explicit in one place (understandable, testable, easier for complex sagas); participants don't need to know about each other; avoids cyclic dependencies.
- *Cons:* extra component; risk of centralizing too much business logic in the orchestrator.

Rule of thumb: **choreography for simple, few-step sagas; orchestration once there are many steps/participants or complex conditional flow.**

### Example (create order, Richardson's)
- *Choreography:* Order Service creates `Order(PENDING)` → emits `OrderCreated` → Customer Service reserves credit → emits `CreditReserved`/`CreditLimitExceeded` → Order Service approves or rejects the order.
- *Orchestration:* Order Service creates the `CreateOrder` saga orchestrator → orchestrator creates `Order(PENDING)` → sends `ReserveCredit` command → Customer Service replies → orchestrator approves/rejects.

### The hard parts
- **No automatic rollback.** You must **design compensating transactions** that semantically undo each step (cancel order, release credit). Steps classify as **compensatable**, **pivot** (point of no return), or **retriable** (after the pivot, must succeed — retry until they do).
- **Lack of isolation (ACD, not ACID).** Concurrent sagas can observe each other's intermediate state → anomalies (lost updates, dirty reads, fuzzy reads). Apply **countermeasures**: *semantic lock* (a `*_PENDING` status flag), *commutative updates* (order-independent ops), *pessimistic view* (reorder steps to reduce risk), *reread value* (detect changes before overwriting), *version file* (record ops to reorder), *by value* (choose strategy by business risk).
- **Reliable publishing.** Each local transaction must atomically update its DB and publish — use **event sourcing** or the **transactional outbox** (never a raw dual write).
- **Answering a synchronous client** of an async saga: (a) respond when the saga completes (e.g. on `OrderApproved`); (b) return an id immediately and let the client **poll** (`GET /orders/{id}`); (c) return an id and **notify** later (websocket/webhook). Trade-offs in latency vs coupling.

### Related patterns
- **Database per Service** creates the need for sagas.
- **Event Sourcing** / **Transactional Outbox** = the reliable atomic-update-and-publish mechanisms a saga step needs.
- **Aggregates + Domain Events** = how a choreography-based saga publishes its triggers.
- **Command-side replica** can replace a saga step that merely queries another service's data.

## The connective tissue (why it's one topic)

```
Database per Service
  ├─ business txn spans services ──> SAGA (choreography via domain events | orchestration via commands)
  └─ query spans services        ──> CQRS (read model built from domain events) | API Composition
Aggregate state change ──> DOMAIN EVENT ──> consumed by sagas, CQRS projections, integrations
EVENT SOURCING stores state AS domain events and makes publishing atomic
Throughout: EVENTUAL CONSISTENCY (the cost of giving up cross-service ACID)
```

Pick the subset the problem demands: a service might use **event sourcing + CQRS** internally and participate in an **orchestrated saga** externally — or use none of them if it's a simple CRUD service. The patterns are a toolkit, not a mandate ([[software-architecture]]: choose the least-worst trade-off).
