---
name: gcp-bigtable
description: "Google Cloud Bigtable — petabyte-scale wide-column NoSQL: a single sorted key-to-wide-row map where the ROW KEY is the schema (range scans + hotspot avoidance drive all design), column families as locality/GC groups, timestamped cell versions, instances→clusters→nodes with replication + app profiles for isolation/failover, SSD/HDD tiers, HBase-compatible Java API plus read-only GoogleSQL. Use when designing Bigtable row keys/schemas, sizing or autoscaling clusters, wiring app profiles and replication, debugging hotspots or per-node throughput, comparing Bigtable vs Spanner/Firestore/BigQuery, or using cbt/gcloud bigtable."
license: MIT
---

# gcp-bigtable

Bigtable is Google Cloud's managed wide-column NoSQL store: sparsely populated tables scaling to billions of rows and thousands of columns, built for large volumes of single-keyed data at low latency. It backs time-series, IoT, financial, ad-tech, and graph workloads, and speaks the open-source HBase API.

## The mental model

**One giant map, sorted by key.** A table is a single lexicographically sorted map from row key → wide row. There is exactly one index: the row key. Every read is either a point lookup or a contiguous range scan over that sort order. Consequences:

- **The row key IS the schema.** Design it from your queries backward ("design your row key based on the queries you will use to retrieve the data"). Data you want to read together must sort together.
- **Hotspots are the failure mode.** Rows are sharded into tablets by contiguous key ranges and spread across nodes; keys that sort adjacently at write time (timestamps, sequential IDs) funnel all writes to one node.
- **Column families are locality + retention groups.** Related columns share a family; garbage collection (max versions / max age) is set per family, not per column. Keep families to ~100 per table.
- **Cells are versioned.** Each row×column intersection holds multiple timestamped cells — a built-in history. Unused columns cost nothing (sparse storage).
- Tablets live in SSTables on Colossus; nodes are stateless compute pointing at them, so rebalancing moves pointers, not data.

## Row-key design doctrine

Do:
- Pack multiple **delimited values** into the key (`continent#country#city`), low-cardinality first, most-granular last — enables prefix range scans at every level.
- **Field promotion**: move the fields you filter on out of the value and into the key. This is the primary tool; prefer it over salting.
- Keep keys short (4 KB hard limit; short keys cut memory and storage) and human-readable (Key Visualizer debugging).
- Pad integers with leading zeros so lexicographic order matches numeric order.
- If you need time in the key, put a high-cardinality prefix (user ID, device ID) **before** the timestamp; use a reversed timestamp (`MAX - ts`) when you want newest-first scans.
- Multi-tenancy: one table with a tenant prefix per row key, not a table per tenant (1,000-table instance cap, connection overhead).

Avoid:
- **Timestamp or sequential ID at the front of the key** — the canonical hotspot.
- **Hashed keys** — they fix hotspots but destroy range scans and debuggability; salting is a trade-off of scan fan-out for write spread, take it only when field promotion can't work.
- **Frequently rewriting the same row key** — overloads the node and bloats the row; write new rows with a timestamp suffix instead.
- Related data scattered into non-contiguous keys — forces full scans.

Tall vs wide: tall tables (one event per row, time in the key) suit time-series scans; wide rows (column qualifiers as data, e.g. friend-IDs-as-qualifiers) suit "fetch the whole entity in one read". Both are idiomatic; a row must stay well under the size limits below.

## Operational model

- **Instance → clusters → nodes.** An instance is the container; each cluster lives in one zone (max one cluster per zone per instance) and instances can span up to 8 regions. Nodes are the compute: each owns a set of tablets, serves its reads/writes, and does maintenance. Throughput scales linearly with node count.
- **Replication** copies all data and schema changes between clusters, eventually consistent (typically seconds to minutes). Single-cluster = strong consistency; multi-cluster defaults to eventual.
- **App profiles** are the routing + isolation mechanism: single-cluster routing (isolation, strong consistency, required for single-row read-modify-write/conditional mutations), multi-cluster any-cluster (nearest cluster, automatic failover), cluster-group routing, and row-affinity routing. Classic pattern: one profile pinning batch/analytics to cluster B, another serving user traffic from cluster A.
- **Storage type is per instance, chosen at creation, permanent**: SSD or HDD for every cluster.
- **Autoscaling**: recommended default; Bigtable adds/removes nodes against CPU and storage utilization targets. Manual node counts are for the rare workload autoscaling handles badly (spiky batch bursts faster than scale-up).
- **Failover**: automatic with multi-cluster routing profiles, manual with single-cluster routing (the near-real-time-backup pattern: standby cluster + manual failover).

Monitoring — watch these per cluster:
- CPU utilization (average AND hottest node — a hot key shows up as one pegged node while the average looks fine).
- Storage utilization per node (performance degrades past the 60–70% targets).
- Replication latency between clusters when using multi-cluster profiles.
- **Key Visualizer** heatmaps: the dedicated tool for spotting hotspots and lopsided key ranges; human-readable row keys make its output legible.

## Shapes

```sh
# one-time cbt setup
gcloud components install cbt
echo project = PROJECT_ID > ~/.cbtrc
echo instance = INSTANCE_ID >> ~/.cbtrc

cbt listinstances
cbt createtable my-table
cbt createfamily my-table cf1
cbt set my-table r1 cf1:col1=value
cbt read my-table          # scan
cbt lookup my-table r1     # point read
cbt deleterow my-table r1
cbt count my-table
```

cbt has no smart retries or error handling — use a client library (or HBase client for Java) in production. `gcloud bigtable ...` manages the control plane:

```sh
gcloud bigtable instances create INSTANCE --display-name=NAME \
  --cluster-config=id=CLUSTER,zone=us-central1-a,nodes=3
gcloud bigtable app-profiles list --instances=INSTANCE
```

**HBase compatibility**: a customized HBase client for Java (HBase API 1.x and 2.x, Java 8+, Hadoop 2.4+) talks to Bigtable through the open-source HBase API — no HBase server to run. Intended for HBase migrations; the APIs are close but "not identical" (minor documented differences). Greenfield Java code should use the native Cloud Bigtable client instead.

**GoogleSQL for Bigtable**: ANSI-style read-only SQL — `SELECT` only, no DML/DDL, no JOINs/subqueries/CTEs. Row key surfaces as `_key`; each column family is a `MAP<key, value>` (with `with_history => TRUE`, `MAP<key, ARRAY<STRUCT<timestamp, value>>>`); temporal args (`as_of`, `latest_n`, ...) query cell history. Continuous materialized views precompute continuously running queries.

## Gotchas and limits (per docs)

- **Per-node throughput expectations** (1 KB rows): SSD ~17,000 row reads/s, ~14,000 writes/s, ~220 MBps scans per node; HDD ~500 reads/s (the killer), ~10,000 writes/s. Size clusters from these, then load-test ≥10 min with ≥100 GB/node of data.
- **Keep CPU under ~60% for latency-sensitive work** (90% ceiling for pure throughput); storage under 60–70% per node. Storage per node caps: 5 TB SSD, 16 TB HDD (higher with tiered storage on Enterprise tiers).
- **Size limits**: row key 4 KB hard; keep a row under 100 MB (256 MB hard); cell 10 MB recommended (100 MB hard); qualifier 16 KB; ~100 families/table; 1,000 tables/instance; 100,000 mutations per batch.
- Rebalancing is automatic but balances both data volume and traffic — a single hot tablet can't be fixed by adding nodes; only key design fixes it.
- Values over ~1 MiB aren't compressed by Bigtable — pre-compress large blobs.
- Strong consistency reverts to eventual after a failover; row-affinity routing improves but does not guarantee read-your-writes.
- Single-row transactions (read-modify-write, conditional mutations) require a compatible routing policy — with multi-cluster routing two clusters could commit conflicting writes, so those calls are restricted.
- Atomicity is single-row only. There are no multi-row transactions; design entities so that what must change together lives in one row.
- Separate columns with different retention needs into different families — GC policy is family-level, and keeping unneeded versions inflates storage cost and read latency.
- **Pricing shape**: nodes (per node-hour, billed whether idle or busy, per cluster — replication multiplies node AND storage cost), storage (SSD ≫ HDD per GB-month), backup storage, and network egress (cross-region replication traffic counts). Autoscaling is the main cost lever.

## Vs siblings

- **vs Spanner**: Spanner is relational — SQL writes, secondary indexes, global strong consistency and cross-row transactions. Bigtable is cheaper per throughput at massive scale and lower latency for keyed access, but gives you one index and single-row atomicity only.
- **vs Datastore/Firestore**: Firestore offers documents, automatic indexes, queries, and mobile sync with zero capacity management — better for app entities at modest throughput. Bigtable wins for sustained very high write rates and huge flat datasets.
- **vs BigQuery**: BigQuery is analytical scan-everything SQL (seconds, columnar, serverless); Bigtable is operational point/range access (single-digit ms, provisioned nodes). Common pattern: stream into Bigtable for serving, mirror to BigQuery for analytics.
- **vs Memorystore**: Redis for sub-ms ephemeral caching of small hot sets; Bigtable for persistent, petabyte-scale keyed data (its in-memory tier, in preview, narrows the latency gap).

Quick heuristic: need SQL joins or multi-row transactions → Spanner; need ad-hoc analytics over everything → BigQuery; need flexible entity queries at app scale → Firestore; need millions of keyed reads/writes per second over terabytes with known access patterns → Bigtable.

## Related

[[gcp-spanner]], [[gcp-datastore]], [[gcp-bigquery]], [[gcp-memorystore-redis]], [[gcp-dataflow]], [[gcp-pubsub]], [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-gke]], [[gcp-cloud-monitoring]], [[gcp-iam]]

Sources: https://docs.cloud.google.com/bigtable/docs/overview, https://docs.cloud.google.com/bigtable/docs/schema-design, https://docs.cloud.google.com/bigtable/docs/instances-clusters-nodes, https://docs.cloud.google.com/bigtable/docs/performance, https://docs.cloud.google.com/bigtable/docs/replication-overview, https://docs.cloud.google.com/bigtable/quotas, https://docs.cloud.google.com/bigtable/docs/googlesql-overview, https://docs.cloud.google.com/bigtable/docs/cbt-overview, https://docs.cloud.google.com/bigtable/docs/hbase-bigtable, https://cloud.google.com/bigtable/pricing (fetched 2026-07).
