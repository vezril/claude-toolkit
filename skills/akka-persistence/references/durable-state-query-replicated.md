# Durable State, Persistence Query & Replicated Event Sourcing

Akka Persistence (2.10.x). Source: doc.akka.io/libraries/akka-core/current/typed/durable-state/persistence.html, persistence-query.html, typed/replicated-eventsourcing.html

## Durable State — CRUD-style persistence

`DurableStateBehavior[Command, State]` persists the **latest state** (not events) — simpler when you don't need an event log/audit trail. Same structure as event sourcing minus the event handler: `persistenceId`, `emptyState`, `commandHandler: (State, Command) => Effect[State]`.

```scala
DurableStateBehavior[Command, State](
  persistenceId = PersistenceId(entityType, entityId),
  emptyState    = State.empty,
  commandHandler = (state, cmd) => cmd match {
    case Update(v, replyTo) => Effect.persist(state.updated(v)).thenReply(replyTo)(_ => Done)
    case Get(replyTo)       => Effect.none.thenReply(replyTo)(s => s.value)
  })
```
```java
public class MyEntity extends DurableStateBehavior<Command, State> {
  @Override public State emptyState() { return State.empty(); }
  @Override public CommandHandler<Command, State> commandHandler() {
    return newCommandHandlerBuilder().forAnyState()
      .onCommand(Update.class, (s, c) -> Effect().persist(s.updated(c.value)).thenReply(c.replyTo, ns -> Done.getInstance()))
      .build();
  }
}
```

Effects: `persist(newState)` (insert, or update only if revision is exactly +1 — optimistic concurrency / single-writer check), `delete()` (reset to empty, bump revision), `none`, `unhandled`, plus `.thenRun`/`.thenReply`/`.thenStop`. Needs a Durable State store plugin (e.g. R2DBC — see [[akka-persistence-plugins]]). Tag with `.withTagger`/`tagsFor` for the read-side.

## Persistence Query — the CQRS read-side

`akka-persistence-query` exposes the journal as Akka Streams `Source`s for building read models. Read journals are plugin-specific.

```scala
val readJournal = PersistenceQuery(system).readJournalFor[MyReadJournal]("akka.persistence.query.my-journal")
val src: Source[EventEnvelope, NotUsed] = readJournal.eventsByTag("orders", Offset.noOffset)
```
```java
MyReadJournal rj = PersistenceQuery.get(system).getReadJournalFor(MyReadJournal.class, "akka.persistence.query.my-journal");
Source<EventEnvelope, NotUsed> src = rj.eventsByTag("orders", Offset.noOffset());
```

Queries (each has a live and a finite `current...` variant): `persistenceIds`, `eventsByPersistenceId(id, from, to)` (replay one entity), `eventsByTag(tag, offset)` (across entities — order across persistence ids is **not** globally guaranteed; use offsets for resumability), and typed `eventsBySlice` (entity type + slice range — deterministically distributes ids; used at scale by [[akka-projections]]). `EventEnvelope` carries the event + persistenceId/seqNr/offset/timestamp. Store the offset to make a projection resumable. **Prefer [[akka-projections]]** over hand-rolling read-sides with `mapAsync`. Durable State has its own tag-based `changes(tag, offset)` query yielding `UpdatedDurableState`/`DeletedDurableState`.

## Replicated Event Sourcing — active-active / multi-DC

Runs **multiple replicas** of an entity (one per region/DC), auto-replicating events between them. Relaxes single-writer for availability (tolerates partitions, rolling redeploys) → state is **eventually consistent** and the event handler **must handle concurrent events** (the single-writer guarantee is gone). Needs a plugin with metadata support (e.g. R2DBC over gRPC).

```scala
ReplicatedEventSourcing.commonJournalConfig(
  ReplicationId("Movie", entityId, replicaId), allReplicaIds, queryPluginId) { replicationContext =>
    EventSourcedBehavior[Command, Event, State](…)
}
```

**Conflict resolution — design state as a CRDT or with explicit timestamps:**
- **Operation-based CRDTs** — events are commutative operations applied once with causal delivery. Built-in: `Counter`, `ORSet` (add-wins), `LwwTime`.
- **Last-writer-wins** — use `LwwTime` (timestamp + replicaId; greater wins, ties broken by replicaId). Relies on synced clocks; carry the full state (or per-field timestamps) to avoid divergence.

`ReplicationContext` gives `replicaId`, `entityId`, `currentTimeMillis()`, the event's origin replica, recovery flag, and a `concurrent` check. Causality is tracked with version vectors. A Projection per replica sees all events from all replicas (filter by origin replica id to process only local events). Event deletion via retention is **disallowed** here.
