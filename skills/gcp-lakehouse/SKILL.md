---
name: gcp-lakehouse
description: "Google Cloud Lakehouse for Apache Iceberg (the product formerly named BigLake, renamed 2026-04-20; APIs/CLI/IAM still say biglake) — the open-lakehouse storage layer: Apache Iceberg tables on Cloud Storage, the serverless Lakehouse runtime catalog (ex BigLake metastore) with its Iceberg REST catalog endpoint, credential vending, BigQuery catalog federation, and multi-engine access from Spark/Flink/Trino/Hive/BigQuery. Use when building or debugging a lakehouse on GCP, wiring Spark or Dataproc to the Iceberg REST catalog, choosing between runtime-catalog Iceberg tables vs BigQuery managed Iceberg tables vs native BigQuery storage vs plain external tables, or reasoning about BigLake pricing, table maintenance, and format/engine support."
license: MIT
---

# GCP Lakehouse for Apache Iceberg (BigLake)

**Lakehouse for Apache Iceberg** is Google Cloud's lakehouse storage engine. It is the product previously sold as **BigLake**: as of **2026-04-20** Google renamed BigLake → "Lakehouse for Apache Iceberg" and BigLake metastore → the **Lakehouse runtime catalog**. Only the *branding* changed — the API (`biglake.googleapis.com`), client libraries, `gcloud biglake` commands, and IAM roles (`roles/biglake.admin`, `roles/biglake.serviceAgent`) all still say BigLake. Expect docs, blogs, and Terraform to mix both names for years; treat "BigLake", "BigLake metastore", "Lakehouse", and "Lakehouse runtime catalog" as the same product line.

## The mental model

One copy of data, many engines:

```
Spark / Flink / Trino / Hive          BigQuery (SQL, Preview r/w)
        \                                   /
         Iceberg REST catalog endpoint (biglake.googleapis.com/iceberg/v1/restcatalog)
                        |
         Lakehouse runtime catalog  — serverless, regional metastore
           catalogs > namespaces (≈ datasets) > Iceberg tables
                        |
         Cloud Storage bucket(s) — Parquet data files + Iceberg metadata
```

- **Storage** is your GCS bucket (Autoclass and CMEK work). **Metadata** (Iceberg snapshots, manifests, pointers) is generated and managed by the runtime catalog and persisted in the warehouse location. **Compute** is whatever engine you attach — the catalog is the shared source of truth, so there is no copy/sync between Spark and BigQuery.
- The catalog speaks the **open-source Apache Iceberg REST Catalog API** plus Google extensions; it handles transaction commits, pointer management, and **credential vending** (the catalog hands engines short-lived, table-scoped storage credentials instead of you granting every engine broad bucket IAM).
- **Iceberg V2 is GA, V3 is Preview, V1 is unsupported** (must be upgraded). Data files via the REST catalog endpoint are **Parquet only**.
- Where this sits vs BigQuery native storage: native BigQuery tables live in BigQuery's proprietary storage with the richest feature set; lakehouse tables live in *your* bucket in an open format so non-Google engines get first-class read/write. You trade some BigQuery performance/features for openness.

## Table types — pick the right one

| Type | Metastore | Writes | Reads | Use for |
|---|---|---|---|---|
| **Iceberg tables (runtime catalog)** | Lakehouse runtime catalog, Iceberg REST endpoint | Spark/Flink/Trino r/w; BigQuery r/w (Preview) | all listed engines | The default for new open lakehouses — full multi-engine interop |
| **Hive tables (runtime catalog)** | Hive metastore endpoint | Spark/Hive | BigQuery read-only | Migrating existing Spark/Hive workloads to a serverless metastore |
| **BigQuery managed Iceberg tables** | BigQuery-managed | BigQuery only | OSS engines limited read | Iceberg-on-GCS but BigQuery-first: streaming, CDC, multi-statement txns |
| **Native BigQuery tables** | BigQuery | BigQuery | BigQuery | Non-Iceberg workloads wanting max features/perf |
| **External tables** | self-managed (GCS/S3/Azure) | external systems | BigQuery read-only | Third-party catalogs, data you don't let Google manage |

## How-to shapes (verified against docs 2026-07)

**Create a catalog** (needs `roles/biglake.admin` on the project + `roles/storage.admin` on buckets; BigLake API enabled):

```bash
gcloud biglake iceberg catalogs create CATALOG \
  --project PROJECT_ID --catalog-type biglake \
  --default-location gs://my-bucket \
  --credential-mode end-user        # or vended-credentials
```

Optional: `--restricted-locations` (extra allowed bucket paths), `--primary-location US|EU` for BigQuery interop.

**Connect Spark** — easiest on Dataproc / Managed Spark: add `--optional-components=ICEBERG` and `--properties="dataproc.lakehouse.catalog.CATALOG=projects/PROJECT_ID/catalogs/CATALOG_ID"` at cluster create, then a plain `SparkSession.builder.getOrCreate()` just works. Manual configuration (any Spark, anywhere):

```python
spark = (SparkSession.builder.appName("app")
  .config('spark.sql.defaultCatalog', 'CATALOG')
  .config('spark.sql.catalog.CATALOG', 'org.apache.iceberg.spark.SparkCatalog')
  .config('spark.sql.catalog.CATALOG.type', 'rest')
  .config('spark.sql.catalog.CATALOG.uri',
          'https://biglake.googleapis.com/iceberg/v1/restcatalog')
  .config('spark.sql.catalog.CATALOG.warehouse',
          'bl://projects/PROJECT_ID/catalogs/CATALOG_ID')   # or gs://BUCKET single-bucket
  .config('spark.sql.catalog.CATALOG.header.x-goog-user-project', 'PROJECT_ID')
  .config('spark.sql.catalog.CATALOG.rest.auth.type',
          'org.apache.iceberg.gcp.auth.GoogleAuthManager')
  .config('spark.sql.catalog.CATALOG.io-impl', 'org.apache.iceberg.gcp.gcs.GCSFileIO')
  .config('spark.sql.extensions',
          'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions')
  .getOrCreate())
```

**Credential vending**: add header config `X-Iceberg-Access-Delegation=vended-credentials`, and grant the catalog's auto-provisioned service agent `roles/storage.objectUser` on every bucket. Vending requires `GCSFileIO`.

**Then**: `CREATE NAMESPACE IF NOT EXISTS ns; USE ns;` and normal Iceberg DDL/DML from Spark/Trino, `gcloud`, the REST API, the console, or BigQuery (Preview).

**BigQuery catalog federation** (the other direction — expose *BigQuery-managed* tables to OSS engines): point the engine's warehouse at `bq://projects/PROJECT_ID`; the REST endpoint proxies straight into BigQuery's catalog, tables appear in BigQuery as ordinary `dataset.table`. Asymmetric: **read-write through BigQuery, read-only from Spark/Trino**, and credential vending is unsupported for federated catalogs.

**Table maintenance**: automatic table management (compaction/adaptive file sizing, clustering, garbage collection, snapshot cleanup) exists as an **opt-in, per-table Preview** — it is not on by default; until you enable it (or run your own Spark maintenance jobs), small files and dead snapshots accumulate.

## Gotchas

- **Support matrix is where projects die.** V1 Iceberg unsupported; V3 still Preview; REST-endpoint tables are Parquet-only; metadata file size capped at 1 MB; no table rename, no views, no clustering, no flexible column names via the REST catalog endpoint.
- **BigQuery's write path to runtime-catalog tables is Preview**, and you *cannot* use BigQuery DDL/DML on tables served through the Apache Iceberg REST catalog endpoint in all configurations — check the current matrix per endpoint type before promising SQL writes.
- **Query semantics differ from native BigQuery**: queries can be slower than native tables, dry runs may report 0 bytes (so cost estimation lies), `tabledata.list` and storage statistics aren't supported.
- **Two catalog generations coexist**: the older "custom Apache Iceberg catalog for BigQuery" endpoint predates the REST endpoint; its tables stay visible via BigQuery catalog federation, but new work should use the Iceberg REST catalog endpoint (also the interop path for BigQuery and AlloyDB).
- **Governance boundary**: the runtime catalog does authn/authz + credential vending; *cataloging/governance* (semantic search, lineage, data quality, policies) comes from **Dataplex Knowledge Catalog** integration, and fine-grained/row-column controls depend on the engine path — don't assume a Spark-vended credential honors BigQuery-side policies.
- **Credential-vending setup has two halves** and fails opaquely if you do only one: catalog created with `--credential-mode vended-credentials` *and* the auto-provisioned service agent granted `roles/storage.objectUser` on each bucket. In end-user mode, every engine principal needs its own GCS access instead.
- **Everything is regional.** Catalogs live in a region; namespaces carry a `gcp-region` property in federation; multi-region `--primary-location US|EU` exists mainly for BigQuery interop. Cross-region Spark ↔ catalog traffic adds latency and egress. Cross-cloud lakehouse (S3/Azure data) and managed disaster recovery are separate, documented features — not defaults.
- **Pricing shape** (own meter, small but nonzero): catalog **metadata storage** (free tier 1 GiB/month), **Class A operations** (writes/list/create/config; 5,000 free/month), **Class B operations** (reads/get/delete; 50,000 free/month), and **table management compute** for the automatic optimization jobs (file sizing, clustering, GC, BigQuery CMETA generation). The big money stays elsewhere: GCS data storage, and BigQuery/Dataproc/Spark compute, each billed by that product. Watch Class A ops with chatty streaming writers — every commit is metadata traffic.

## vs siblings

- **vs native BigQuery tables** ([[gcp-bigquery]]): native = closed format, best performance, full feature set (fine-grained DML, time travel, BI Engine). Lakehouse = open Iceberg in your bucket, multi-engine writes, some BigQuery features lost. If only BigQuery will ever touch the data, native wins.
- **vs BigQuery managed Iceberg tables**: same open files on GCS, but BigQuery owns the write path (gets you streaming/CDC/transactions); pick these when you want Iceberg output but BigQuery-centric ingestion. Runtime-catalog tables win when Spark/Flink/Trino must write too.
- **vs plain external tables over GCS** ([[gcp-cloud-storage]]): external tables are read-only from BigQuery, no managed metastore, no transactions, no credential vending — fine for occasional reads over files you don't govern; a lakehouse once multiple engines need consistent read-write.

## Related

[[gcp-bigquery]], [[gcp-cloud-storage]], [[gcp-dataflow]], [[gcp-pubsub]], [[gcp-looker]], [[gcp-iam]], [[gcp-vpc-service-controls]], [[gcp-cloud-monitoring]], [[gcp-cloud-logging]]

Sources: https://docs.cloud.google.com/lakehouse/docs, https://docs.cloud.google.com/lakehouse/docs/introduction, https://docs.cloud.google.com/lakehouse/docs/about-lakehouse-catalogs, https://docs.cloud.google.com/lakehouse/docs/lakehouse-tables, https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog, https://docs.cloud.google.com/lakehouse/docs/manage-lakehouse-iceberg-tables, https://docs.cloud.google.com/lakehouse/docs/use-catalog-federation, https://docs.cloud.google.com/lakehouse/docs/iam-and-access-control, https://cloud.google.com/products/lakehouse/pricing (fetched 2026-07).
