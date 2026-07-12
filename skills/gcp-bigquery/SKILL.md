---
name: gcp-bigquery
description: "Google BigQuery — serverless, columnar analytics data warehouse: Dremel compute decoupled from Colossus storage, datasets/tables, partitioning + clustering as the cost levers, on-demand ($/TiB scanned) vs capacity (editions/slots) pricing, logical vs physical storage billing, batch loads (free) vs Storage Write API vs legacy streaming, external/BigLake tables, scheduled queries, bq CLI and GoogleSQL DDL. Use when designing, querying, loading, or cost-tuning a BigQuery warehouse, choosing partition/cluster keys, picking on-demand vs editions, or deciding BigQuery vs Bigtable/Spanner/AlloyDB."
license: MIT
---

# GCP BigQuery

Petabyte-scale, fully managed analytics data warehouse. You write GoogleSQL (or Python);
Google runs it on a massively parallel engine. No servers, no indexes, no vacuuming —
your job is schema design and cost discipline, not operations.

## The mental model

- **Storage and compute are separate systems.** Data lives in Capacitor (columnar) files on
  Colossus, Google's distributed filesystem; queries run on Dremel, a fleet of workers whose
  unit of capacity is the **slot**. They scale independently — you never size a cluster.
- **Columnar means you pay per column touched.** A query reads only the columns it references,
  across every row it can't prune. `SELECT *` on a wide table is the canonical money fire.
- **Datasets are regional containers.** Tables, views, and routines live in datasets; a dataset
  is pinned to a location (region or US/EU multi-region) at creation and queries can't join
  across locations. Access control and default expirations hang off the dataset.
- **Two meters, pick one per workload.** On-demand bills **bytes scanned** ($6.25/TiB, US;
  first 1 TiB/month free). Capacity billing (editions) bills **slot-hours** regardless of bytes.
  Flat-rate slots were retired **July 2023**, replaced by editions with autoscaling.
- **Partitioning prunes, clustering sorts.** Partitioning splits a table into segments BigQuery
  can skip entirely when the filter names the partition column; clustering sorts data within
  storage blocks so filters/aggregations on clustered columns read fewer blocks. These two are
  the levers that make on-demand cost sane. Partition pruning gives an exact pre-run estimate;
  clustering savings only show up after the query runs.

## How-to shapes

Query and inspect (bq CLI):

```bash
bq query --use_legacy_sql=false 'SELECT ... FROM `proj.ds.t` WHERE d = "2026-07-01"'
bq query --dry_run --use_legacy_sql=false 'SELECT ...'   # bytes estimate, no charge
bq head -n 20 proj:ds.t          # preview rows — free; a SELECT * LIMIT 20 is not
bq show --schema proj:ds.t
```

Batch load (free, shared slot pool):

```bash
bq load --source_format=PARQUET mydataset.mytable gs://bucket/part-*.parquet
bq load --source_format=CSV --autodetect mydataset.t gs://bucket/file.csv
```

Partitioned + clustered table DDL (verified against docs):

```sql
CREATE TABLE mydataset.events (
  event_ts TIMESTAMP, user_id INT64, action STRING
)
PARTITION BY TIMESTAMP_TRUNC(event_ts, DAY)
CLUSTER BY user_id, action
OPTIONS (partition_expiration_days = 90, require_partition_filter = TRUE);
```

Variants: `PARTITION BY date_col` (DATE), `PARTITION BY DATE_TRUNC(d, MONTH)`,
`PARTITION BY _PARTITIONDATE` (ingestion time), integer ranges via
`PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 100, 10))`.
One partition column only; up to four clustering columns, and **column order matters** —
filters must hit a prefix of the cluster key to prune blocks.

Scheduled queries (run by the Data Transfer Service):

```bash
bq query --display_name=nightly --destination_table=ds.t_{run_date} \
  --schedule='every 24 hours' --use_legacy_sql=false 'SELECT ...'
```

`@run_date` / `@run_time` parameters and `{run_date}` table templating are built in; use
`--service_account_name` for production so schedules don't die with an employee's account.

## Cost control (the section that pays for itself)

- **`maximum_bytes_billed`** — per-query hard cap; the query fails instead of overspending.
  Set it in job config, `bq query --maximum_bytes_billed=…`, or as a project/user custom quota.
- **Dry-run everything programmatic** (`--dry_run`); the console validator shows the same estimate.
- **Never `SELECT *`** — name columns. To eyeball data use the console preview or `bq head`, which are free.
- **`LIMIT` does not reduce on-demand cost** on non-clustered tables — you still scan everything.
  (Clustered tables are the exception.)
- **`require_partition_filter = TRUE`** on big partitioned tables makes accidental full scans a
  hard error instead of a bill.
- **Storage billing is per-dataset, logical or physical.** Logical = uncompressed bytes, time
  travel and fail-safe included. Physical = compressed bytes (often several times cheaper for
  compressible data) but time-travel/fail-safe storage is billed separately. US ballpark:
  logical $0.02/GiB/mo active, physical $0.04/GiB/mo active; anything untouched 90 days drops
  to long-term rates at half price automatically. First 10 GiB/month free.
- **Editions when spend is steady:** Standard $0.04/slot-hour (autoscale only, project-level),
  Enterprise $0.06 with baselines + 1-yr (~20% off) / 3-yr (~40% off) commitments, Enterprise
  Plus adds managed DR and compliance. Rule of thumb: heavy, predictable scanning → slots;
  spiky/exploratory → on-demand with caps. (US rates as of 2026-07.)

## The loading spectrum

| Path | Cost | Semantics | Use for |
|---|---|---|---|
| Batch load jobs (`bq load`, GCS) | Free (shared slots) | Atomic per job | The default. CSV/JSON/Avro/Parquet/ORC |
| Storage Write API | $0.025/GiB after 2 TiB/mo free | Exactly-once (offsets), gRPC + protobuf/Arrow | Real streaming; also batch via pending streams |
| Legacy streaming (`insertAll`) | ~2x Write API | At-least-once, dedupe best-effort | Don't start new work here — migrate |

Write API stream types: **default** (at-least-once, easiest), **committed** (exactly-once,
immediate visibility), **pending** (atomic batch commit). Loads are free but not instant;
streaming is instant but never free.

## Gotchas and quotas

- Query timeout 6 hours; 1,500 load jobs per table per day; local-file loads capped at 100 MB
  (route through GCS); STRING clustering uses only the first 1,024 characters.
- You can't `ALTER` a table into a different partitioning scheme — recreate and backfill.
- Scheduled queries firing exactly on the hour can double-run; make them idempotent
  (`WRITE_TRUNCATE` or MERGE, not blind INSERT).
- Cross-region queries fail confusingly ("dataset not found") — check locations first.
- On-demand projects get a default per-project slot ceiling; a "slow" query at 2 PM may just
  be slot contention, not a bad plan.
- Edition feature lists shift over time — don't encode "Enterprise has X" into policy; check docs.

## vs siblings

- **Bigtable** — wide-column NoSQL for millions of point reads/writes per second at
  single-digit-ms latency. BigQuery is the opposite: scan a billion rows in seconds, but a
  single-row lookup is slow and costs a scan. Analytical vs operational — be honest about which
  you are.
- **Spanner / AlloyDB / Cloud SQL** — transactional SQL (OLTP). They serve your app;
  BigQuery analyzes what they produced (federated queries and Datastream can bridge).
- **BigLake / lakehouse** — when data must stay in GCS/S3/Azure as Parquet or Iceberg,
  BigLake tables give BigQuery (and Spark) governed access without ingestion. Native storage
  still queries faster; see [[gcp-lakehouse]].

## Related

[[gcp-bigtable]], [[gcp-spanner]], [[gcp-alloydb]], [[gcp-cloud-sql]], [[gcp-lakehouse]],
[[gcp-looker]], [[gcp-dataflow]], [[gcp-pubsub]], [[gcp-cloud-storage]],
[[gcp-cloud-scheduler]], [[gcp-iam]], [[gcp-cloud-monitoring]], [[gcp-cloud-sdk]]

Sources: https://docs.cloud.google.com/bigquery/docs, https://docs.cloud.google.com/bigquery/docs/partitioned-tables, https://docs.cloud.google.com/bigquery/docs/clustered-tables, https://docs.cloud.google.com/bigquery/docs/creating-partitioned-tables, https://docs.cloud.google.com/bigquery/docs/editions-intro, https://docs.cloud.google.com/bigquery/docs/storage_overview, https://docs.cloud.google.com/bigquery/docs/write-api, https://docs.cloud.google.com/bigquery/docs/batch-loading-data, https://docs.cloud.google.com/bigquery/docs/external-data-sources, https://docs.cloud.google.com/bigquery/docs/scheduling-queries, https://docs.cloud.google.com/bigquery/docs/best-practices-costs, https://cloud.google.com/bigquery/pricing (fetched 2026-07).
