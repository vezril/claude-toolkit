# Sources, offset stores & Projection gRPC

Akka Projections 1.6.x. Source: doc.akka.io/libraries/akka-projection/current/{eventsourced,durable-state,jdbc,r2dbc,running,error,grpc}.html

## Source providers

**Events from Akka Persistence** (`akka-projection-eventsourced`):
- `EventSourcedProvider.eventsByTag[E](system, readJournalId, tag)` — tag-partitioned (Cassandra/JDBC). Envelope type `akka.projection.eventsourced.EventEnvelope[E]`.
- `EventSourcedProvider.eventsBySlices[E](system, readJournalId, entityType, minSlice, maxSlice)` — slice-partitioned (R2DBC/DynamoDB, **preferred**; slice ranges rebalance dynamically). Use `EventSourcedProvider.sliceRanges(system, readJournalId, n)` to split. Envelope type `akka.persistence.query.typed.EventEnvelope[E]` (note: **different** type than eventsByTag). Variants: `eventsBySlicesStartingFromSnapshots` (reduce cold-start load), `EventsBySliceFirehoseQuery` (share one DB stream across many consumers).

**Durable state changes** (`akka-projection-durable-state`): `DurableStateSourceProvider.changesByTag` / `changesBySlices` → `DurableStateChange[State]` (`UpdatedDurableState`/`DeletedDurableState`). Only the *latest* change per object is eventually emitted (rapid updates coalesce). For all individual changes, use a `ChangeEventHandler` on the `DurableStateBehavior` to emit delta change-events and consume them with `eventsBySlices`.

The read journal id and offset store backend should match your [[akka-persistence-plugins]] choice.

## Projection types & semantics

`ProjectionId(name, key)` identifies a projection + its offset row. Factories per store: **`R2dbcProjection`**, **`JdbcProjection`**, **`SlickProjection`**, **`CassandraProjection`**, **`DynamoDBProjection`**, plus Kafka. Each offers:

- `exactlyOnce` — offset written in the **same transaction** as the handler side effect (transactional stores only: JDBC/R2DBC/Slick).
- `atLeastOnce` — offset saved after processing; **handler must be idempotent**; tune `.withSaveOffset(afterEnvelopes, afterDuration)`.
- `groupedWithin` — batch envelopes, offset in same txn as the grouped handler (effectively exactly-once); `.withGroup(groupAfterEnvelopes, groupAfterDuration)`.
- `atLeastOnceAsync` / `groupedWithinAsync` — handler not bound to a DB session, for non-DB side effects (Kafka, HTTP). Cassandra is effectively at-least-once only.
- `atMostOnce` — offset saved before processing (rare).

Handler variants: `JdbcHandler`/`R2dbcHandler` (receive a session), grouped handler (process a `Seq`/`List`), plain `Handler` (async side effects), stateful handler, actor handler.

## Offset stores (config highlights)

- **JDBC** (`akka-projection-jdbc`) — implement `JdbcSession` (for `exactlyOnce` set `autoCommit=false`). **Required config:** `akka.projection.jdbc.dialect` (`postgres-dialect`/`mysql-dialect`/…) and `blocking-jdbc-dispatcher.thread-pool-executor.fixed-pool-size` (JDBC is blocking → dedicated dispatcher). Tables `akka_projection_offset_store` + `akka_projection_management`; create via `JdbcProjection.createTablesIfNotExists` (tests; create schema before deploy in prod).
- **R2DBC** (`akka-projection-r2dbc`) — reactive, non-blocking; **recommended pairing for `eventsBySlices`** and the **only** offset store for Projection gRPC. Handlers use `R2dbcSession`; offset written in the same connection/txn for `exactlyOnce`/`groupedWithin`. 1024 slices; slice-range count is dynamically rescalable.
- **Cassandra** (`akka-projection-cassandra`) — `atLeastOnce`/`groupedWithin` only (no cross-row txn → no true exactly-once); tag-based.
- **DynamoDB** / **Slick** — analogous.

## Distributing & error handling (recap)

Wrap each projection instance in a `ProjectionBehavior` and start `numberOfInstances` (= number of tags or slice ranges) via `ShardedDaemonProcess` (see SKILL.md). Run locally with `context.spawn(ProjectionBehavior(p), id)` or as a Cluster Singleton for one/few instances. Recovery: `HandlerRecoveryStrategy.{fail, skip, retryAndFail, retryAndSkip}` per envelope; projection restart-backoff on unrecoverable failure (resumes from last saved offset).

## Projection gRPC — service-to-service replication

`akka-projection-grpc` streams events from a producer service to a consumer service over [[akka-grpc]] (R2DBC required on both sides). The **producer** exposes events via an `EventProducer` gRPC service (`EventProducerSource` with entityType, transformation, optional filters). The **consumer** builds a `GrpcReadJournal` and feeds it to `EventSourcedProvider.eventsBySlices` like any read journal, then runs it via `R2dbcProjection` + `ShardedDaemonProcess`. Variants: **producer push** (producer initiates the connection — for edge/firewalled producers) and **Replicated Event Sourcing over gRPC** (active-active, see [[akka-persistence]]). This is the idiomatic way to cross a Bounded Context boundary ([[domain-driven-design]]) with events.
