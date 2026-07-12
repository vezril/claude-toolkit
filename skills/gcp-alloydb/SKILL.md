---
name: gcp-alloydb
description: "Google AlloyDB for PostgreSQL — fully managed, 100% PostgreSQL-compatible database for demanding OLTP: clusters with a primary instance + read pool instances (up to 20 nodes) over a shared, auto-scaling regional storage layer; in-memory columnar engine for in-place analytics; index advisor and adaptive autovacuum; AlloyDB AI (pgvector-compatible vector, ScaNN index, in-SQL model calls, NL-to-SQL); AlloyDB Omni to run the same engine in containers/Kubernetes anywhere; Auth Proxy and language connectors for IAM-authenticated connections. Use when choosing or operating AlloyDB, sizing clusters/read pools, enabling the columnar engine or vector search, wiring PSC/private-IP connectivity, planning HA/backups/PITR, or deciding AlloyDB vs Cloud SQL for PostgreSQL vs Spanner."
license: MIT
---

# GCP AlloyDB for PostgreSQL

Fully managed, PostgreSQL-compatible database for demanding transactional workloads. It is
real PostgreSQL to your app — psql, pgAdmin, drivers, and extensions work unmodified — but
the engine underneath is Google-built: disaggregated compute/storage, an intelligent regional
storage layer, and an in-memory columnar engine for analytics on live operational data.

## The mental model

- **Cluster → instances → nodes.** A *cluster* is the regional container holding all storage
  and compute for a workload. *Instances* are connection points: exactly one **primary**
  (read/write) and zero or more **read pool** instances (read-only, each 1–20 nodes behind a
  single endpoint). *Nodes* are the VMs actually running the engine.
- **Compute and storage are separate and scale independently.** All instances in a cluster
  share one horizontally scalable regional storage layer. Adding read pool nodes adds zero
  storage cost — replicas read the same shared storage rather than keeping full copies.
- **HA is a node count, not a second cluster.** A high-availability primary uses two nodes in
  different zones with automatic failover; a "basic" (zonal) primary is one node. Cross-region
  replication exists on top of that for DR.
- **The columnar engine is the differentiator.** It keeps selected columns in an in-memory
  column-oriented store with its own planner/execution paths, accelerating scans, joins, and
  aggregates on the same data your OLTP writes touch — HTAP without an ETL pipeline.
- **Machine-learning-driven self-management.** Index advisor recommends indexes from your
  actual query load; adaptive autovacuum tunes maintenance automatically; auto-columnarization
  picks which columns to populate into the column store.

## Provisioning and connecting

Prereqs: enable the AlloyDB API; set up private services access **or** Private Service Connect
on your VPC; have `roles/alloydb.admin` (plus `compute.networks.list`).

```bash
gcloud alloydb clusters create my-cluster \
    --database-version=POSTGRES_16 --region=us-central1 \
    --password=SECRET --network=my-vpc

gcloud alloydb instances create my-primary \
    --instance-type=PRIMARY --cluster=my-cluster \
    --region=us-central1 --cpu-count=4        # N2: 2–128 vCPU; also C4, C4A (from 1 vCPU), Z3

gcloud alloydb instances create my-reads \
    --instance-type=READ_POOL --read-pool-node-count=2 \
    --cluster=my-cluster --region=us-central1 --cpu-count=4
```

Connecting, in order of recommendation:

- **AlloyDB Auth Proxy** — sidecar/daemon giving IAM-based access control and end-to-end
  encryption; the production default.
- **Language connectors** (Java/Python/Go) — in-process libraries with automated mTLS
  (TLS 1.3) and IAM authorization; no external proxy process. Docs recommend these if you
  must use public IP.
- **Direct private IP** inside the VPC (PSA or PSC endpoint); lowest latency, plain PG wire.
- **IAM database authentication** — OAuth 2.0 tokens instead of PostgreSQL passwords.

## The differentiators

- **Columnar engine** — set the `google_columnar_engine.enabled` flag (one-time, restarts the
  instance); by default it takes ~30% of instance memory (configurable). Auto-columnarization
  analyzes the workload and populates/evicts columns; you can also add columns manually.
  Wins on selective scans over few columns, SUM/MIN/MAX/AVG/COUNT aggregates, hash joins,
  JSON-expression filters, ORDER BY/LIMIT over columnar scans.
- **Index advisor** — periodic analysis of query patterns yields concrete CREATE INDEX
  recommendations; pairs with Query Insights for diagnosis.
- **AlloyDB AI** — `vector` (customized pgvector: HNSW, IVF/IVFFlat, scalar quantization),
  `alloydb_scann` (ScaNN nearest-neighbor index, can load into the columnar engine),
  `google_ml_integration` (embeddings, ranking, prediction calls to Vertex AI or registered
  OpenAI/Anthropic endpoints from SQL), `alloydb_ai_nl` (natural-language questions over your
  schema). AlloyDB AI itself is free; model calls bill through the model provider.
- **AlloyDB Omni** — downloadable, streamlined edition of the same engine for your own
  environment: container on a VM, Kubernetes operator, or Linux RPM; distributed via Docker
  Hub, Artifact Registry, Cloud Marketplace, and AWS Marketplace. Follows PostgreSQL
  versioning. This is the "run it on-prem/another cloud/your laptop" answer.

## Gotchas

- **Networking is a prerequisite, not an afterthought.** Cluster creation wants private
  services access or PSC configured on the VPC first; choose per cluster. Public IP exists but
  docs steer you to connectors + authorized networks if you use it.
- **Columnar engine is not free lunch:** enabling requires a restart; it consumes instance
  memory; frequently updated rows invalidate columnar data; tiny tables (<5,000 rows) and
  already-indexed columns may stay on the row store anyway. Verify with EXPLAIN.
- **PITR restores create a new cluster** (same region), then you must create a primary
  instance on it — it is not an in-place rewind. Continuous backup default retention is
  14 days (1–35 configurable); on-demand/automated backups keep up to a year and survive
  cluster deletion. On-demand backups can be stored cross-region for DR.
- **Read pools are eventually consistent reads** off shared storage — route only
  staleness-tolerant traffic there.
- **Pricing shape:** per-vCPU + per-GiB-memory per node-hour (HA primary = 2 nodes = 2x
  compute; read pool nodes billed like any node), regional storage billed only for what you
  use (shared across all instances), backup storage, and networking — no license fee, no I/O
  charges. 1- and 3-year committed use discounts on CPU/memory. 30-day free trial cluster
  (up to 1 TB, 8 vCPU primary + 8 vCPU read pool) on top of the $300 new-customer credit.

## vs siblings

- **Cloud SQL for PostgreSQL** — managed *vanilla* Postgres on a VM with attached disk;
  cheaper and simpler for ordinary workloads. AlloyDB is for demanding OLTP: shared-storage
  read scaling, columnar HTAP, and the AI/vector stack. Same wire protocol either way.
- **Spanner** — global, horizontally scalable, synchronously replicated SQL with a different
  surface (PostgreSQL *interface*, not full compatibility). Pick Spanner for multi-region
  writes and effectively unlimited scale; pick AlloyDB when you need actual PostgreSQL.
- **BigQuery** — the columnar engine accelerates analytics *on operational data in place*;
  it does not replace a warehouse for petabyte scans, cross-source joins, or BI serving.

## Related

[[gcp-cloud-sql]], [[gcp-spanner]], [[gcp-bigquery]], [[gcp-bigtable]],
[[gcp-memorystore-redis]], [[gcp-vpc]], [[gcp-iam]], [[gcp-secret-manager]],
[[gcp-cloud-run]], [[gcp-gke]], [[gcp-compute-engine]], [[gcp-cloud-monitoring]],
[[gcp-cloud-logging]], [[gcp-cloud-sdk]]

Sources: https://docs.cloud.google.com/alloydb/docs, https://docs.cloud.google.com/alloydb/docs/overview, https://docs.cloud.google.com/alloydb/docs/cluster-create, https://docs.cloud.google.com/alloydb/docs/connection-overview, https://docs.cloud.google.com/alloydb/docs/columnar-engine/about, https://docs.cloud.google.com/alloydb/docs/ai, https://docs.cloud.google.com/alloydb/docs/backup/overview, https://docs.cloud.google.com/alloydb/omni/docs, https://cloud.google.com/alloydb/pricing (fetched 2026-07).
