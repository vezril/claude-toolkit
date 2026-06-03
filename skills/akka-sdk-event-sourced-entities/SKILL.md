---
name: akka-sdk-event-sourced-entities
description: Akka SDK Event Sourced Entities (Java) — durable, stateful components whose state is derived from a persisted append-only sequence of domain events (the CQRS source of truth with a full audit trail). Covers defining one (extend EventSourcedEntity<State, Event>, @Component(id), emptyState), the state/command/event model (records + a sealed event interface with @TypeName), command handlers returning Effect<T>, the Effect API (persist/reply/error/none/deleteEntity/expireAfter, ReadOnlyEffect), the applyEvent event handler, automatic snapshots, deletion & TTL, the single-writer/sharding guarantee, multi-region replication & replication filters, calling via ComponentClient.forEventSourcedEntity, and testing with EventSourcedTestKit. Use when modeling stateful domain aggregates that need history/audit/event-driven projections in an Akka SDK service. Part of the Akka SDK (Java); see akka-sdk for the model and akka-sdk-key-value-entities for the simpler latest-state alternative.
---

# Akka SDK — Event Sourced Entities

A durable, stateful component that persists the **sequence of events** that produced its state (an append-only journal), not the state itself; state is rebuilt by replaying events. This is the CQRS **source of truth** with a full audit trail. Part of the [[akka-sdk]] (Java); the SDK's version of [[akka-persistence]] event sourcing, but the runtime handles the journal, sharding, and replication.

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-key-value-entities]] (latest-state alternative), [[akka-sdk-views]] / [[akka-sdk-consumers]] (read sides), [[domain-driven-design]], [[event-storming]].

## The model

```java
// domain/ — plain records + a sealed event interface
public record ShoppingCart(String cartId, List<LineItem> items, boolean checkedOut) {
  public ShoppingCart addItem(LineItem i) { /* return a new immutable instance */ }
}
public sealed interface ShoppingCartEvent {
  @TypeName("item-added")  record ItemAdded(ShoppingCart.LineItem item) implements ShoppingCartEvent {}
  @TypeName("checked-out") record CheckedOut()                          implements ShoppingCartEvent {}
}

// application/
@Component(id = "shopping-cart")
public class ShoppingCartEntity extends EventSourcedEntity<ShoppingCart, ShoppingCartEvent> {
  private final String entityId;
  public ShoppingCartEntity(EventSourcedEntityContext ctx) { this.entityId = ctx.entityId(); }

  @Override public ShoppingCart emptyState() {           // ALWAYS override (else currentState() is null)
    return new ShoppingCart(entityId, List.of(), false);
  }

  public Effect<Done> addItem(ShoppingCart.LineItem item) {           // command handler
    if (currentState().checkedOut()) return effects().error("Cart already checked out");
    return effects().persist(new ShoppingCartEvent.ItemAdded(item))  // persist event(s)
                    .thenReply(newState -> Done.getInstance());      // reply with post-apply state
  }

  public ReadOnlyEffect<ShoppingCart> getCart() { return effects().reply(currentState()); }

  @Override public ShoppingCart applyEvent(ShoppingCartEvent event) {  // THE event handler — derives new state
    return switch (event) {
      case ShoppingCartEvent.ItemAdded e  -> currentState().addItem(e.item());
      case ShoppingCartEvent.CheckedOut e -> currentState().onCheckedOut();
    };
  }
}
```

## Key rules

- **The only way to change state is to persist an event** — never mutate `currentState()` fields directly (lost on reload). The command handler validates and persists; **`applyEvent` is the sole place state is derived** and must be free of side effects (it runs on every replay).
- **Single-writer / sharding:** each entity instance (`@Component(id)` + instance id) lives on exactly one node; commands are routed to it and handled **one at a time** (sequential, no concurrency control needed). Inactive instances are passivated and recovered from the journal on next use.
- **`@Component(id)` must be unique and stable**; capture the instance id via the constructor `ctx.entityId()` or `commandContext().entityId()`. Persist a **private/internal** event model (not your public API types) so storage can evolve; tag each subtype with a stable `@TypeName`.
- **Effect API:** `effects().persist(event...).thenReply(state -> reply)`, `.reply(v)`, `.error("msg")`, `.none()`; `.deleteEntity()` and `.expireAfter(Duration)` chain onto a persist; `ReadOnlyEffect<T>` is compile-time read-only (and servable from any region).

## Always-apply defaults

1. **Override `emptyState()`** to avoid null state everywhere.
2. **Events are facts in the past tense** (`ItemAdded`, `CheckedOut`), modeled as a `sealed interface` with `@TypeName` per case; keep domain logic in the `domain/` records, the entity thin.
3. **No side effects in `applyEvent`** (it replays); validate and decide in the command handler.
4. **Don't delete events casually** — the history has business value; if you must, persist a final event then `.deleteEntity()` (events are physically removed ~1 week later to let consumers process the final event).
5. **Pair with a [[akka-sdk-views]] view or [[akka-sdk-consumers]] consumer** for read-side queries / projections rather than querying entities by non-id attributes.
6. **In multi-region, use a write `Effect` (routes to the primary) when a read must see the latest**; `ReadOnlyEffect` may be served stale from any region.

## Snapshots, deletion, multi-region

- **Snapshots** are automatic (no code): `akka.javasdk.event-sourced-entity.snapshot-every = 100`. On reload the snapshot loads, then later events replay.
- **Deletion:** `effects().persist(finalEvent).deleteEntity().thenReply(...)`. Entity exists briefly after; events/snapshots fully removed ~1 week later. `isDeleted()` checks status; avoid reusing ids. **TTL:** `.expireAfter(Duration.ofDays(30))` on a persist auto-deletes if no further events (a persist without `expireAfter` cancels it).
- **Multi-region:** each instance has a **primary region** (handles writes); events replicate **asynchronously** (eventually consistent). `@EnableReplicationFilter` + `effects().updateReplicationFilter(ReplicationFilter.includeRegion/excludeRegion)` restrict which regions replicate an instance.

## Calling & testing

```java
componentClient.forEventSourcedEntity(cartId).method(ShoppingCartEntity::addItem).invoke(item);
```
**Unit test** with `EventSourcedTestKit` (one in-memory instance):
```java
var tk = EventSourcedTestKit.of(ShoppingCartEntity::new);
var result = tk.method(ShoppingCartEntity::addItem).invoke(item);
assertEquals(Done.getInstance(), result.getReply());
var added = result.getNextEventOfType(ShoppingCartEvent.ItemAdded.class);
assertEquals(item, tk.getState().items().get(0));
```
`EventSourcedResult`: `getReply()`, `getAllEvents()`, `getState()`, `getNextEventOfType(X.class)`. **Integration**: extend `TestKitSupport`, drive via the injected `componentClient`.

## Anti-patterns (flag in review)

- Mutating `currentState()` directly instead of persisting an event; side effects in `applyEvent`.
- Not overriding `emptyState()`; persisting public API types instead of an internal event model; missing/duplicate `@TypeName`.
- Deleting events while a projection/consumer still needs them; reusing an entity id after deletion; changing `@Component(id)`.
- Querying entities by non-id fields instead of building a [[akka-sdk-views]] view; using event sourcing where latest-state ([[akka-sdk-key-value-entities]]) suffices.

## Related

- [[akka-sdk]] · [[akka-sdk-key-value-entities]] · [[akka-sdk-views]] · [[akka-sdk-consumers]] · [[akka-sdk-workflows]] (orchestrate entity calls)
- [[akka-persistence]] — the Core-library equivalent; [[domain-driven-design]] / [[event-storming]] for modeling aggregates and events.
- Source: https://doc.akka.io/sdk/event-sourced-entities.html
