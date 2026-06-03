---
name: akka-persistence-plugins
description: Akka Persistence storage plugins (current) in Scala and Java — the journal / snapshot / durable-state / read-journal backends for Akka Persistence: R2DBC (Postgres/Yugabyte, the recommended modern default, eventsBySlices + durable state + Projection gRPC), JDBC (any JDBC DB via Slick, eventsByTag), Cassandra (high write throughput, eventsByTag, no durable state), and DynamoDB (AWS-native, eventsBySlices). Covers the HOCON to wire each as journal/snapshot/durable-state store, the read-journal identifiers, schema/table creation, slices vs tags, and how to choose a backend. Use whenever picking or configuring a persistence backend, wiring akka.persistence.journal.plugin / snapshot-store.plugin / state.plugin, setting up a read journal for queries/projections, deciding R2DBC vs JDBC vs Cassandra vs DynamoDB, or debugging persistence plugin/schema/connection issues — even if a plugin isn't named but an event-sourcing database backend is involved. Pairs with akka-persistence and akka-projections.
---

# Akka Persistence Plugins

[[akka-persistence]] needs a **storage plugin** to actually persist events, snapshots, and durable state, and to expose a **read journal** for queries/[[akka-projections]]. All are enabled via the three standard keys: `akka.persistence.journal.plugin`, `akka.persistence.snapshot-store.plugin`, `akka.persistence.state.plugin` (durable state), each overridable per-behavior (`journalPluginId`/`snapshotPluginId`/`durableStateStorePluginId`).

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-persistence]], [[akka-projections]], [[akka-serialization]].

## Choosing a backend

| Plugin | Backends | Query model | Durable state | Choose when |
|---|---|---|---|---|
| **R2DBC** (recommended default) | Postgres, Yugabyte, H2, SQLServer (exp.) | **eventsBySlices** + changesBySlices | **Yes** | New projects; reactive SQL; needed for Projection gRPC / Replicated ES |
| **JDBC** | any JDBC DB via Slick | **eventsByTag** | Yes | Existing/legacy JDBC infra, blocking driver only |
| **Cassandra** | Cassandra, Keyspaces, Astra, Scylla | **eventsByTag** | **No** | Very high write throughput, log-oriented workloads |
| **DynamoDB** | Amazon DynamoDB | **eventsBySlices** | No | AWS-native / serverless |

**The key divide: slices vs tags.** R2DBC and DynamoDB partition the event stream into **1024 slices** (deterministic hash of `persistenceId`), so [[akka-projections]] instances can be **rebalanced dynamically** across more workers reusing offsets. JDBC and Cassandra use **tags**, which require deciding the tag count up front (≈10× max nodes) and can't be rescaled. **Prefer slices (R2DBC/DynamoDB) for new event-sourced systems.** Durable state is only on R2DBC and JDBC. All publish under `com.lightbend.akka`, license BSL 1.1, served from `https://repo.akka.io/maven`.

## R2DBC — the recommended modern plugin

`com.lightbend.akka %% akka-persistence-r2dbc`. Postgres driver transitive; H2/SQLServer drivers `provided`.

```hocon
akka.persistence.journal.plugin        = "akka.persistence.r2dbc.journal"
akka.persistence.snapshot-store.plugin = "akka.persistence.r2dbc.snapshot"
akka.persistence.state.plugin          = "akka.persistence.r2dbc.state"
akka.persistence.r2dbc.connection-factory = ${akka.persistence.r2dbc.postgres}   # or .yugabyte / .h2 / .sqlserver
akka.persistence.r2dbc.connection-factory {
  host = "localhost", database = "postgres", user = "postgres", password = "postgres"
  initial-size = 10, max-size = 30, acquire-retry = 1   # set acquire-retry = max-size to survive DB restarts
}
```
Read journal id: `R2dbcReadJournal.Identifier`; durable state via `DurableStateStoreRegistry`. Tables `event_journal`, `snapshot`, `durable_state` (DDL scripts under `ddl-scripts/`; slice indexes only needed for slice queries). Implements `eventsBySlices`/`currentEventsBySlices` (+ start-from-snapshot). **Slice queries return duplicates by design** (offset is a `TimestampOffset` + backtracking to catch late/out-of-order events) — always consume through an [[akka-projections]] `R2dbcProjection`, which deduplicates and enforces per-pid order. Low-latency pub-sub over the cluster reduces poll latency. Durable state extras: `additional-columns`, `custom-table`, `change-handler` (same-txn query-representation update). Deletes are **hard** (don't delete events still needed by projections). The connection pool is shared across all `akka.persistence.r2dbc` plugins. H2/file-based R2DBC can't be shared across JVMs (no cluster use).

## JDBC — any JDBC DB via Slick

`com.lightbend.akka %% akka-persistence-jdbc` (uses Slick 3.6 + HikariCP internally). Plugin ids are **unprefixed**:
```hocon
akka.persistence.journal.plugin        = "jdbc-journal"
akka.persistence.snapshot-store.plugin = "jdbc-snapshot-store"
jdbc-journal { slick = ${slick} }
jdbc-snapshot-store { slick = ${slick} }
jdbc-read-journal { slick = ${slick} }
slick {
  profile = "slick.jdbc.PostgresProfile$"   # or MySQL/H2/Oracle/SQLServer Profile$
  db { url = "jdbc:postgresql://localhost:5432/db?reWriteBatchedInserts=true", user = "u", password = "p",
       driver = "org.postgresql.Driver", numThreads = 5, maxConnections = 5, minConnections = 1 }
}
```
Read journal id `JdbcReadJournal.Identifier`; query is **tag-based** (`eventsByTag`/`currentEventsByTag` — add a `CREATE INDEX ... ON event_tag (tag)` for performance). Default = one pool per journal type; share via `akka-persistence-jdbc.shared-databases` + `use-shared-db`. Schema scripts per DB; `SchemaUtils.createIfNotExists()` for tests. Lower `journal-sequence-retrieval.query-delay` **and** `refresh-interval` for latency.

## Cassandra — high write throughput

`com.lightbend.akka %% akka-persistence-cassandra` (DataStax driver 4.x via Alpakka Cassandra).
```hocon
akka.persistence.journal.plugin        = "akka.persistence.cassandra.journal"
akka.persistence.snapshot-store.plugin = "akka.persistence.cassandra.snapshot"
datastax-java-driver.advanced.reconnect-on-init = true   # strongly recommended
# No durable state store.
```
Read journal id `CassandraReadJournal.Identifier`; **eventsByTag** only. Create keyspace/tables before use (**never auto-create in production** — concurrent migrations corrupt schema; use RF ≥ 3, `NetworkTopologyStrategy`). `target-partition-size` and `events-by-tag.bucket-size` are **immutable once data exists** — choose before production. **Biggest gotcha: eventsByTag is eventually consistent** with a backtracking blind spot if a query restarts from a later offset — events delayed beyond `eventual-consistency-delay` (default 5s) may never be delivered. Keep tags < 10 (each tag copies the event). Default consistency QUORUM (LOCAL_QUORUM multi-DC).

## DynamoDB — AWS-native

`com.lightbend.akka %% akka-persistence-dynamodb` (AWS SDK v2).
```hocon
akka.persistence.journal.plugin        = "akka.persistence.dynamodb.journal"
akka.persistence.snapshot-store.plugin = "akka.persistence.dynamodb.snapshot"
# Journal + snapshot only — no durable state.
```
Read journal id `DynamoDBReadJournal.Identifier`; **eventsBySlices** only (no eventsByTag, no eventsByPersistenceId). Tables created via the `CreateTables` utility; the journal table needs a **GSI for slice indexing**. Same `TimestampOffset` + backtracking + dedup-via-Projection model as R2DBC. TTL on journal items supported.

## Always-apply defaults

1. **Default to R2DBC** for new event-sourced systems (slices, durable state, Projection gRPC); use Cassandra only for very high write throughput, JDBC for existing infra, DynamoDB for AWS-native.
2. **Always run slice queries through the matching [[akka-projections]] Projection** (it deduplicates backtracking duplicates and enforces per-pid order).
3. **Create schemas explicitly before deploy** (never rely on auto-create in production, especially Cassandra).
4. **Pin all `akka-*` to one version** and configure a real serializer ([[akka-serialization]] — Jackson) with a schema-evolution plan.
5. **Don't delete events still needed by projections** (R2DBC/DynamoDB hard-delete).

## Related

- [[akka-persistence]] — these back its journal/snapshot/durable-state and read journals.
- [[akka-projections]] — the offset store and read journal come from the same backend; R2DBC is the recommended pairing.
- [[akka-serialization]] — payload serialization & schema evolution.
- Sources: akka-persistence-r2dbc / -jdbc / -cassandra / -dynamodb docs at doc.akka.io/libraries/.
