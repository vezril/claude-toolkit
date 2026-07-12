---
name: gcp-spanner
description: "Google Cloud Spanner — globally distributed, strongly consistent relational database: external consistency via TrueTime, horizontally sharded storage with Paxos replication, compute in nodes/processing units (1 node = 1000 PUs) decoupled from storage, GoogleSQL + PostgreSQL dialects, interleaved tables and hotspot-aware primary-key design, RW/RO transactions with bounded/exact staleness, regional (99.99%) vs dual/multi-region (99.999%) configs, Data Boost for analytics. Use when designing schemas or keys for Spanner, choosing Spanner vs Cloud SQL/AlloyDB/Bigtable, sizing instances/autoscaling, tuning transactions or stale reads, or debugging hotspots and mutation-limit errors."
license: MIT
---

# gcp-spanner

Spanner is Google Cloud's fully managed, horizontally scalable relational database with
**external consistency at global scale** — the only mainstream managed database that gives you
strict serializability across regions with an SLA of up to 99.999%. It speaks two SQL dialects
(GoogleSQL and PostgreSQL, chosen per database at creation) and has grown multi-model:
key-value, graph (Spanner Graph), full-text and vector search, depending on edition.

## The mental model

- **Horizontally sharded relational storage.** Tables are ordered by primary key and cut into
  **splits** (contiguous key ranges). Splits are moved and re-cut automatically based on size
  *and load* — Spanner rebalances for you, but only along key boundaries. Your primary-key
  design therefore *is* your load-distribution strategy.
- **Paxos replication.** Every split is replicated across zones/regions; writes commit via a
  Paxos quorum (regional: 3 read-write replicas across zones; multi-region: read-write, read-only,
  and witness replicas, with a default **leader region** that serializes writes).
- **External consistency via TrueTime.** TrueTime is Google's globally synchronized clock with
  bounded uncertainty. Every commit gets a TrueTime timestamp; if Txn1 completes before Txn2
  starts committing, Txn1's timestamp is earlier — no client can ever observe Txn2's effects
  without Txn1's. This is serializability *plus* real-time ordering, and it holds across regions.
- **Compute is decoupled from storage.** You provision compute as **nodes or processing units**
  (1 node = 1000 PUs; granularity 100 PUs up to 1000, then whole nodes). Storage is billed and
  scaled separately: ~1024 GiB per 100 PUs below 1 node, 10 TiB per node at 1+ nodes. Enterprise+
  editions add a managed autoscaler (min/max PUs, CPU and storage targets).
- **Keep CPU headroom for Paxos.** Target < 65% high-priority CPU on regional instances,
  < 45% per region on multi-region — beyond that, tail latencies degrade.

## Schema doctrine

- **Never use a monotonically increasing value as the first key part** of a high-write table
  (timestamps, auto-increment IDs). All inserts land on the last split → one server takes every
  write. Fixes, per the docs:
  - **UUIDv4** (`GENERATE_UUID()` / `gen_random_uuid()`) — random bits spread writes. Avoid
    UUIDv1 (timestamp in high-order bits).
  - **Bit-reversed sequences** — `CREATE SEQUENCE ... bit_reversed_positive` gives unique
    integers whose bit-reversal scatters them across the keyspace.
  - **Swap key order** — `(LastAccess, UserId)` → `(UserId, LastAccess)`.
  - **Logical sharding** — prepend `ShardId = hash(...) % N` with N ≈ expected node count;
    more shards than servers buys nothing.
- **Interleaved tables** co-locate child rows physically under their parent row
  (`INTERLEAVE IN PARENT Parent ON DELETE CASCADE`; child PK must start with the full parent PK
  in order). Use for parent-child data you always read together; locality holds as long as a
  parent row + descendants stays under the split size limit. Max interleave depth: 7.
  Interleaving is permanent — undoing it means recreating the table. Use interleaving *or*
  foreign keys for a relationship, not both.
- **Indexes hotspot too**: never create a non-interleaved index on a monotonically increasing
  column of a high-write table — the index is itself a table with that column as its key.
  Interleave the index in the parent when the per-parent write rate is modest.
- **History tables**: store timestamps `DESC` in the key when you mostly read the most recent
  entries.

## Transaction model

- **Read-write transactions**: pessimistic locking, serializable by default (external
  consistency). Aborted transactions are retried automatically by the client libraries with
  escalating lock priority — always write retry-safe (idempotent) transaction bodies.
  A repeatable-read (snapshot) isolation option exists for lower contention.
- **Read-only transactions**: lock-free, never block or abort writers, give a consistent
  snapshot across any number of reads. Default: **strong** (sees everything committed before
  the read).
- **Staleness reads** are the deliberate tool, not a compromise: **bounded staleness**
  ("at most N seconds old", docs commonly suggest 15s) lets the nearest replica — including
  read-only replicas in other regions — serve without contacting the leader; **exact staleness**
  reads at a fixed timestamp. Use stale reads for geo-distributed read latency and for taking
  load off the leader when freshness within seconds is acceptable.
- **Partitioned DML** for large-scale backfills/updates: executes per-partition, must be
  idempotent, avoids the single-transaction mutation limit.

## Shapes (verified against docs)

```bash
gcloud spanner instances create my-instance \
  --config=regional-us-central1 --description="prod" \
  --edition=ENTERPRISE --processing-units=300      # or --nodes=3
# autoscaling (Enterprise+): --autoscaling-min-processing-units / -max-processing-units \
#   --autoscaling-high-priority-cpu-target --autoscaling-storage-target
gcloud spanner databases create my-db --instance=my-instance \
  --database-dialect=GOOGLE_STANDARD_SQL   # or POSTGRESQL
```

```sql
CREATE TABLE Singers ( SingerId INT64 NOT NULL, Name STRING(MAX) ) PRIMARY KEY (SingerId);
CREATE TABLE Albums (
  SingerId INT64 NOT NULL, AlbumId INT64 NOT NULL, AlbumTitle STRING(MAX)
) PRIMARY KEY (SingerId, AlbumId), INTERLEAVE IN PARENT Singers ON DELETE CASCADE;
```

## Gotchas

- **Mutation limits**: 80,000 mutations per commit (index entries count!), 100 MiB commit size.
  Batch large writes or use Partitioned DML.
- **Key/table limits**: 8 KiB max key size, 16 key columns, 1,024 columns/table, 5,000
  tables/database, 128 indexes/table, 10,000 indexes/database.
- **Editions gate features**: Standard = regional only; Enterprise adds autoscaler, graph,
  full-text/vector search, columnar engine, incremental backups; Enterprise Plus is required
  for dual-region/multi-region (99.999%) and geo-partitioning. Edition upgrade is ~10 min,
  zero downtime.
- **Multi-region costs latency on writes** (cross-region quorum) and money (more replicas);
  it buys 99.999% and low-latency reads near users. Moving the leader region is cheap and fast;
  choose it near your write traffic.
- **Data Boost** (serverless, pay-per-PU-used) runs analytics/exports — BigQuery federated
  queries, Dataflow — on independent compute with near-zero impact on the provisioned instance.
- **Pricing shape**: compute (nodes/PUs per hour, rate varies by edition and by
  regional vs multi-region config) + database storage (GB/month) + backup storage + network
  egress/replication + Data Boost usage. CUDs: ~20% (1yr) / ~40% (3yr). The floor is real:
  even 100 PUs runs continuously — Spanner is not a scale-to-zero database.

## vs siblings

- **Cloud SQL**: managed MySQL/Postgres/SQL Server on a single VM primary — cheaper, familiar,
  fine until you hit vertical-scaling or regional-failover ceilings. Pick Spanner when you need
  horizontal write scaling, > 99.99% availability, or multi-region strong consistency.
- **AlloyDB**: high-performance PostgreSQL-compatible; better than Cloud SQL for demanding
  Postgres workloads, but still a scale-up architecture with read pools — not globally
  horizontally scalable writes.
- **Bigtable**: NoSQL wide-column, massive throughput at lower cost per node, but no SQL joins,
  no multi-row ACID transactions, eventual cross-cluster replication. Spanner when you need
  relational semantics and strong consistency; Bigtable for time-series/high-volume KV.
- Honest read: Spanner's premium is justified by *consistency at scale*. A single-region app
  that fits in one Postgres box is cheaper and simpler on Cloud SQL or AlloyDB.

## Related

- [[gcp-cloud-sql]], [[gcp-alloydb]] — the scale-up relational siblings
- [[gcp-bigtable]], [[gcp-datastore]] — the NoSQL siblings
- [[gcp-bigquery]] — analytics target (federated queries + Data Boost)
- [[gcp-dataflow]] — bulk import/export and change-stream processing
- [[gcp-iam]], [[gcp-cloud-monitoring]] — access control and CPU/latency observability

Sources: https://docs.cloud.google.com/spanner/docs, https://docs.cloud.google.com/spanner/docs/schema-design, https://docs.cloud.google.com/spanner/docs/compute-capacity, https://docs.cloud.google.com/spanner/docs/transactions, https://docs.cloud.google.com/spanner/docs/limits, https://docs.cloud.google.com/spanner/docs/instance-configurations, https://docs.cloud.google.com/spanner/docs/schema-and-data-model, https://docs.cloud.google.com/spanner/docs/editions-overview, https://docs.cloud.google.com/spanner/docs/create-manage-instances, https://docs.cloud.google.com/spanner/docs/databoost/databoost-overview, https://docs.cloud.google.com/spanner/docs/true-time-external-consistency (fetched 2026-07).
