---
name: akka-projections
description: Akka Projections (current, 1.6.x) in Scala and Java — process a stream of events/changes into a read-side/projection with durable offset tracking; the read side of CQRS for Akka Persistence. Covers the building blocks (SourceProvider via EventSourcedProvider.eventsByTag/eventsBySlices and DurableStateSourceProvider, Projection, ProjectionId, Handler, the offset store), delivery semantics (exactly-once, at-least-once, grouped, at-most-once), the concrete projection types (R2dbcProjection, JdbcProjection, SlickProjection, CassandraProjection, DynamoDBProjection, Kafka, gRPC), error/recovery strategies, and distributing projections across a cluster via ShardedDaemonProcess. Use whenever building a CQRS read model, projecting event-sourced or durable-state events into a database/Kafka/another service, tracking stream offsets, choosing exactly-once vs at-least-once, or running service-to-service event replication — even if "Projections" isn't named but read-side views, event handlers with offset storage, or CQRS read models are involved. Builds on akka-persistence and akka-cluster.
---

# Akka Projections

Process a stream of events or state-changes from a `SourceProvider` into a **read-side projection** (a query-optimized view, another service, Kafka, …), with **durable offset tracking** so it resumes where it left off. This is the **read side of CQRS** for [[akka-persistence]], and the standard way to do service-to-service event replication. Current version **1.6.x** (group `com.lightbend.akka`).

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-persistence]], [[akka-cluster]], [[akka-persistence-plugins]], [[alpakka]], [[akka-grpc]].

## The three building blocks

1. **SourceProvider** — the source of *envelopes* and how offsets are tracked. From [[akka-persistence]]: `EventSourcedProvider.eventsByTag` (Cassandra/JDBC) or `EventSourcedProvider.eventsBySlices` (R2DBC/DynamoDB — preferred, dynamically rescalable); `DurableStateSourceProvider.changesBySlices`. Also Kafka (`akka-projection-kafka`), gRPC (`akka-projection-grpc`), custom.
2. **Handler** — your per-envelope (or per-group) processing; receives a store session for transactional projections.
3. **Offset store** — durable storage of the last processed offset (R2DBC / JDBC / Slick / Cassandra / DynamoDB).

```scala
val sourceProvider = EventSourcedProvider.eventsBySlices[ShoppingCart.Event](
  system, R2dbcReadJournal.Identifier, entityType = "ShoppingCart", minSlice, maxSlice)
val projection = R2dbcProjection.exactlyOnce(
  ProjectionId("ShoppingCarts", s"carts-$minSlice-$maxSlice"), settings = None,
  sourceProvider, handler = () => new ShoppingCartHandler())
```
```java
SourceProvider<Offset, EventEnvelope<ShoppingCart.Event>> sp =
  EventSourcedProvider.eventsBySlices(system, R2dbcReadJournal.Identifier(), "ShoppingCart", minSlice, maxSlice);
Projection<EventEnvelope<ShoppingCart.Event>> projection = R2dbcProjection.exactlyOnce(
  ProjectionId.of("ShoppingCarts", "carts-" + minSlice + "-" + maxSlice), Optional.empty(), sp, ShoppingCartHandler::new, system);
```

## Always-apply defaults

1. **Never run two instances with the same `ProjectionId` concurrently** — they overwrite each other's offset. Distribute disjoint subsets (tags / slice ranges) instead.
2. **Prefer `eventsBySlices` + R2DBC/DynamoDB** for new systems (slice ranges rebalance dynamically) over tag-based; if using tags, choose tag count ≈ 10× max nodes up front (can't rescale).
3. **Choose semantics deliberately:** `exactlyOnce` (offset committed in the **same transaction** as the side effect — JDBC/R2DBC/Slick only); `atLeastOnce` (idempotent handler required; tune `.withSaveOffset`); `groupedWithin` (batch + same-txn offset → effectively exactly-once); `atLeastOnceAsync`/`groupedWithinAsync` (non-DB side effects, e.g. Kafka/HTTP); `atMostOnce` (rare).
4. **Distribute across the cluster with ShardedDaemonProcess** (one instance per tag / slice range), wrapping each in a `ProjectionBehavior`.
5. **Handlers must not be shared across Projection instances** (each gets a fresh one); a stateful handler is fine (invoked one envelope at a time).
6. **Use the matching Projection for slice queries** — `eventsBySlices` returns duplicates by design (backtracking); the Projection deduplicates and enforces per-pid order.

## Delivery semantics & handlers

```scala
class ShoppingCartHandler(repo: OrderRepository)
    extends JdbcHandler[EventEnvelope[ShoppingCart.Event], PlainJdbcSession] {
  override def process(session: PlainJdbcSession, env: EventEnvelope[ShoppingCart.Event]): Unit =
    env.event match {
      case ShoppingCart.CheckedOut(cartId, time) => session.withConnection(c => repo.save(c, Order(cartId, time)))
      case _ => ()
    }
}
// at-least-once tuning: .withSaveOffset(afterEnvelopes = 100, afterDuration = 500.millis)
// grouped:             JdbcProjection.groupedWithin(...).withGroup(20, 500.millis)
```

Recovery: `.withRecoveryStrategy(HandlerRecoveryStrategy.retryAndFail(retries, delay))` (also `retryAndSkip`, `skip`, default `fail` → restart from last saved offset); restart backoff via `.withRestartBackoff(...)` (config `akka.projection.restart-backoff`).

## Distributing across the cluster

```scala
ShardedDaemonProcess(system).init[ProjectionBehavior.Command](
  name = "ShoppingCarts",
  numberOfInstances = ranges.size,
  behaviorFactory = i => ProjectionBehavior(projectionFor(ranges(i))),
  stopMessage = ProjectionBehavior.Stop)
```
```java
ShardedDaemonProcess.get(system).init(
  ProjectionBehavior.Command.class, "ShoppingCarts", ranges.size(),
  i -> ProjectionBehavior.create(projectionFor(ranges.get(i))), ProjectionBehavior.stopMessage());
```

See **`references/sources-stores-grpc.md`** for: the source providers in detail (eventsByTag vs eventsBySlices vs durable-state changes, the two `EventEnvelope` types), the per-store projection types and their offset stores (R2DBC/JDBC/Cassandra/DynamoDB schema & config), grouped/async handler variants, and **Projection gRPC** (service-to-service event replication).

## Related

- [[akka-persistence]] — produces the events/changes; projections are the CQRS read side.
- [[akka-cluster]] — ShardedDaemonProcess distributes projection instances; tag/slice partitioning.
- [[akka-persistence-plugins]] — the offset store and read journal come from the same backend (R2DBC recommended).
- [[alpakka]] — Kafka as a projection source/sink (`akka-projection-kafka`).
- [[akka-grpc]] — transport for Projection gRPC (service-to-service replication).
- Source: Akka Projection docs, https://doc.akka.io/libraries/akka-projection/current/ (v1.6.x).
