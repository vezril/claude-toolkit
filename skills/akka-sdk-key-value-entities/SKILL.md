---
name: akka-sdk-key-value-entities
description: Akka SDK Key Value Entities (Java) — durable, stateful components that persist the full latest state on every change (CRUD-style, no event log), the simpler alternative to Event Sourced Entities. Covers defining one (extend KeyValueEntity<State>, @Component(id), emptyState), command handlers returning Effect<T>, the Effect API (updateState/reply/error/deleteEntity/expireAfter, ReadOnlyEffect), the single-writer/sharding guarantee, when to use vs event sourced, multi-region replication & filters, calling via ComponentClient.forKeyValueEntity, and testing with KeyValueEntityTestKit. Use when you only need current state (no history/audit/event consumers) for a stateful entity in an Akka SDK service. Part of the Akka SDK (Java); see akka-sdk for the model and akka-sdk-event-sourced-entities for the event-log alternative.
---

# Akka SDK — Key Value Entities

A durable, stateful component that stores the **full current state** on every change (like CRUD) — **no event history**, unlike [[akka-sdk-event-sourced-entities]]. Simpler and cheaper when you don't need an audit trail, event replay, or downstream event consumers. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-event-sourced-entities]] (event-log alternative), [[akka-sdk-views]] (read side).

## The model

```java
public record Counter(int value) { public Counter increment(int d) { return new Counter(value + d); } }

@Component(id = "counter")
public class CounterEntity extends KeyValueEntity<Counter> {           // <State> only — no event type
  public CounterEntity(KeyValueEntityContext ctx) { /* ctx.entityId() */ }
  @Override public Counter emptyState() { return new Counter(0); }     // ALWAYS override

  public Effect<Counter> plusOne() {
    var next = currentState().increment(1);
    return effects().updateState(next).thenReply(next);                // the ONLY way to change state
  }
  public ReadOnlyEffect<Counter> get() { return effects().reply(currentState()); }
  public Effect<Done> delete() { return effects().deleteEntity().thenReply(Done.getInstance()); }
}
```

## Key rules

- **The only way to change state is `effects().updateState(newState)`** — never mutate `currentState()` fields directly (lost on reload). Effect API: `updateState(s).thenReply(...)`, `reply(v)`, `error("msg")`, `deleteEntity()`, `.expireAfter(Duration)`, `ReadOnlyEffect<T>` for reads.
- **Single-writer / sharding** and **stable, unique `@Component(id)`** work exactly as in [[akka-sdk-event-sourced-entities]]; capture the id via `ctx.entityId()` / `commandContext().entityId()`. Override `emptyState()`.
- **Persist a private/internal model**, not public API types.

## When to use vs Event Sourced

Use a **Key Value Entity** when you only need the current state and don't need history, audit, temporal queries, or event-driven projections/replication of *changes* — it's simpler and cheaper. Use an **Event Sourced Entity** when those matter. Note: a [[akka-sdk-consumers]] consumer / [[akka-sdk-views]] view sourced from a KV entity is guaranteed to see the *most recent* state but **not necessarily every intermediate change** (changes can be coalesced).

## Multi-region, calling, testing

- **Multi-region:** same model as ESE but the replicated unit is the **state change**; primary handles writes, async eventual replication, `ReadOnlyEffect` may be stale, write `Effect` routes to primary. `@EnableReplicationFilter` + `updateReplicationFilter(...)` scope regions.
- **Call:** `componentClient.forKeyValueEntity(id).method(CounterEntity::plusOne).invoke()`.
- **Deletion:** `effects().deleteEntity()` leaves an empty state briefly; fully removed ~1 week later; `isDeleted()`; avoid id reuse. `.expireAfter(Duration)` TTL (canceled by a later update without it). Alternatively reset via `updateState(emptyState)`.
- **Unit test** with `KeyValueEntityTestKit`:
  ```java
  var tk = KeyValueEntityTestKit.of(CounterEntity::new);
  assertEquals(11, tk.method(CounterEntity::plusOne).invoke().getReply().value());
  assertEquals(11, tk.getState().value());
  ```
  **Integration**: extend `TestKitSupport`, drive via `componentClient.forKeyValueEntity(id)`.

## Always-apply defaults / anti-patterns

- Override `emptyState()`; change state only via `updateState`; keep logic in `domain/` records; stable `@Component(id)`.
- For read-by-attribute/cross-instance queries build a [[akka-sdk-views]] view, not entity scans.
- **Anti-patterns:** mutating state in place; choosing KV when you actually need event history/projections (use ESE); relying on a KV-sourced consumer to observe every change; reusing ids after deletion.

## Related

- [[akka-sdk]] · [[akka-sdk-event-sourced-entities]] · [[akka-sdk-views]] · [[akka-sdk-consumers]]
- Source: https://doc.akka.io/sdk/key-value-entities.html
