---
name: akka-persistence
description: Akka Persistence (Akka Core 2.10.x, Typed API) in Scala and Java — durable, stateful actors via event sourcing and durable state. Covers EventSourcedBehavior (PersistenceId, command/event handlers, the Effect API, replies & StatusReply, recovery, tagging), snapshotting & retention, schema evolution (serializers, event adapters), CQRS read-sides, Replicated Event Sourcing (active-active/multi-DC with CRDTs), DurableStateBehavior (CRUD-style latest-state persistence), Persistence Query (read journals, EventsByTag/Slice, offsets), and testing (EventSourcedBehaviorTestKit, persistence-testkit). Use whenever building event-sourced or durable stateful entities, designing aggregates with persisted state, choosing event sourcing vs durable state, handling snapshots/retention/schema evolution, building a CQRS read-side, doing active-active replication, or testing persistent behaviors — even if "persistence" isn't named but durable actor state, event sourcing, aggregates, or CQRS are involved. Builds on akka-actors and is typically combined with akka-cluster sharding.
---

# Akka Persistence

Durable, stateful actors. Two models: **Event Sourcing** (persist *events*, rebuild state by replay — the default, gives a full audit log and high write throughput) and **Durable State** (persist the *latest state*, CRUD-style). Built on [[akka-actors]]; persistent entities almost always live inside [[akka-cluster]] sharding for the single-writer guarantee.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-actors]], [[akka-cluster]], [[akka-serialization]], [[akka-projections]], [[akka-persistence-plugins]], [[domain-driven-design]], [[event-storming]].

Dependencies: `akka-persistence-typed` (+ `akka-persistence-testkit % Test`, `akka-persistence-query` for read-sides). A journal (and optional snapshot store) plugin is required — see [[akka-persistence-plugins]].

## Event sourcing in one breath

An `EventSourcedBehavior[Command, Event, State]` receives a non-persistent **Command** → validates → emits **Event(s)** → events are appended to the journal → the **event handler** applies events to produce the new **State**. State is rebuilt on start by replaying events (optionally from a snapshot). This maps directly onto [[domain-driven-design]] aggregates and the output of an [[event-storming]] session (commands → events → state; the wall *is* the design).

```scala
EventSourcedBehavior[Command, Event, State](
  persistenceId = PersistenceId(entityTypeHint, entityId),
  emptyState    = State.empty,
  commandHandler = (state, cmd) => cmd match {
    case Add(d) => Effect.persist(Added(d)).thenReply(...)(_ => StatusReply.Ack)
  },
  eventHandler = (state, evt) => evt match {
    case Added(d) => state.withItem(d)
  })
```
```java
public class Cart extends EventSourcedBehavior<Command, Event, State> {
  @Override public State emptyState() { return State.empty(); }
  @Override public CommandHandler<Command, Event, State> commandHandler() {
    return newCommandHandlerBuilder().forAnyState()
      .onCommand(Add.class, c -> Effect().persist(new Added(c.data))).build();
  }
  @Override public EventHandler<State, Event> eventHandler() {
    return newEventHandlerBuilder().forAnyState()
      .onEvent(Added.class, (s, e) -> s.withItem(e.data)).build();
  }
}
```

## Always-apply defaults

1. **Events are facts in the past tense** (`Added`, `Withdrawn`); commands are imperatives (`Add`, `Withdraw`). Model them as `sealed`/`interface` ADTs.
2. **No side effects in the event handler** — it runs during recovery (and on replicated-event consumption). Side effects go in `.thenRun`/`.thenReply` or on the `RecoveryCompleted` signal.
3. **All state lives in `State`** (never in instance fields); prefer immutable state. Use `withMutableState(factory)` only if state must be mutable.
4. **Single-writer:** put the entity in [[akka-cluster]] Cluster Sharding so exactly one instance per `PersistenceId` is active. Compose the id from an entity-type hint + entityId.
5. **Use `withEnforcedReplies` + `StatusReply`** so the compiler guarantees every command replies, and success/validation-error is modeled uniformly.
6. **Pick a real serializer (Jackson) and plan schema evolution from day one** — events are immutable and long-lived (see [[akka-serialization]]). Never rely on Java serialization.
7. **Snapshot for long event streams** (`RetentionCriteria.snapshotEvery(n, keepN)`); avoid deleting events.

## Anti-patterns (flag in review)

- Side effects / IO in the event handler; state stored in actor fields instead of `State`.
- Multiple active writers for one `PersistenceId` (no sharding) → interleaved events → corrupt replay.
- Throwing on validation instead of replying with a `StatusReply.Error`; events that can fail on replay.
- Default Java serialization for events; no schema-evolution plan; renaming event classes without a migration/event-adapter.
- Deleting events (especially with Projections active, or under Replicated Event Sourcing where it's disallowed); using event sourcing where CRUD ([[akka-persistence-plugins]] durable state) is enough.
- Assuming `EventsByTag` gives a globally ordered stream across persistence ids (it doesn't — use offsets and slices).

## How to use this skill

Detail lives in three references:

- **`references/event-sourcing.md`** — `EventSourcedBehavior` in full: components, the **Effect API** (`persist`/`none`/`reply`/`thenRun`/`stop`/`stash`), replies & `StatusReply` & `withEnforcedReplies`, recovery & `RecoveryCompleted`, state-dependent (FSM-style) handlers, tagging, and **CQRS**.
- **`references/snapshots-schema-testing.md`** — snapshotting & `RetentionCriteria`, event/snapshot deletion caveats, **schema evolution** (serializers, `EventAdapter`, versioned manifests, split/rename/remove events), and **testing** (`EventSourcedBehaviorTestKit`, `UnpersistentBehavior`, `PersistenceTestKit`).
- **`references/durable-state-query-replicated.md`** — **DurableStateBehavior** (CRUD-style), **Persistence Query** (read journals, `EventsByPersistenceId`/`ByTag`/`BySlice`, offsets — the CQRS read-side feeding [[akka-projections]]), and **Replicated Event Sourcing** (active-active, multi-DC, CRDT/LWW conflict resolution).

## Related

- [[akka-actors]] — persistent behaviors are typed actors.
- [[akka-cluster]] — Cluster Sharding hosts entities and enforces single-writer; Sharded Daemon Process runs projection workers.
- [[akka-persistence-plugins]] — journal/snapshot/durable-state backends (Cassandra, JDBC, R2DBC, DynamoDB).
- [[akka-projections]] — builds CQRS read-sides from the event stream.
- [[akka-serialization]] — event serialization & schema evolution.
- [[domain-driven-design]], [[event-storming]] — aggregates, events, and the modeling that precedes the code.
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/typed/index-persistence.html (v2.10.x).
