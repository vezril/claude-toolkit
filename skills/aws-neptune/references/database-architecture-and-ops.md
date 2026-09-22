# Neptune Database: architecture and operations

## Cluster anatomy

- **Primary instance**: the only writer. Handles all loads and mutations.
- **Neptune replicas**: up to **15**, read-only, attached to the **same cluster volume**, so a replica doesn't replay a log to catch up. Put them in separate AZs. On primary failure, Neptune fails over to a replica automatically.
- **Cluster volume**: a single virtual volume on NVMe SSDs, replicated across **3 AZs**, growing automatically to **128 TiB** (64 TiB in China and GovCloud). Storage self-heals. It's the same shape as [[aws-aurora]].
- Neptune stores data as quads in three indexes (`SPOG`, `POGS`, `GPSO`), even for property graphs. This is why lock ranges and query plans are described in quad terms.
- AWS states a design target of **> 99.99% availability**.

### Endpoints

| Endpoint | Routes to | Use for |
|---|---|---|
| Cluster endpoint | current primary | writes, read-your-writes |
| Reader endpoint | load-balanced across replicas | general reads |
| Instance endpoint | one specific instance | diagnostics, pinning a workload |
| Custom endpoint | a chosen subset of instances | isolating analytics or batch readers from app readers |

All endpoints use **port 8182** over HTTPS/WSS. The API paths are `/gremlin`, `/openCypher`, `/sparql`, `/loader`, `/status`, and the stream paths (`/propertygraph/stream`, `/sparql/stream`). The `neptunedata` API (`aws neptunedata …`, `boto3.client('neptunedata', endpoint_url=…)`) wraps these data-plane calls. Management runs through the `neptune` API (`aws neptune create-db-cluster …`), which shares account limits with RDS.

## Compute: provisioned vs Serverless

- **Provisioned** memory-optimized classes: r5, r5d, r6g, r6gd, r6i, r7g, r7i, r8g, x2g, x2gd, x2iedn, x2iezn, plus t3/t4g.medium for dev. Availability varies by region, so check the pricing page. R4 is no longer supported.
- **r5d/r6gd with the lookup cache:** on `R5d` instances the local NVMe holds a lookup cache for property values, which speeds up read-heavy workloads that return many properties. `neptune_lookup_cache` turns on automatically when an R5d is added. It doesn't work on Serverless.
- **Serverless** (engine ≥ 1.2.0.1):
  - Capacity is in **NCUs**, which scale in 0.5-NCU steps up to **128 NCU (256 GB)**, roughly an r6g.8xlarge.
  - Compute scales; storage doesn't change.
  - Serverless and provisioned instances can be mixed in one cluster, and an instance can be switched between them without a new cluster.
  - It fits spiky or idle workloads, dev and test, and one-cluster-per-tenant setups.
  - Watch it with query timeouts. A runaway query scales the bill.
- **Auto-scaling** adds or removes read replicas on a CloudWatch target. `neptune_autoscaling_config` sets the class, maintenance window and tags for the replicas it creates. It isn't supported on Global Database secondaries.

## Storage billing

- Storage is billed on the **high-water mark** of allocated space.
- **Standard**: pay per I/O. Good for moderate or low I/O.
- **I/O-Optimized** (`--storage-type iopt1`, engine ≥ 1.3.0.0): **no I/O charges**, but higher instance and storage rates. Choose it when I/O is a large share of the bill. You can switch **at most once every 30 days**, on create, modify or restore. `describe-*` calls report the storage type.
- Streams, audit logs and snapshots add I/O and storage cost.

## Global Database

- One primary cluster plus **up to 5 secondary regions**, each read-only with up to **16 replicas**. Replication runs at the **storage layer** with lag typically **under 1 second**.
- Writes go only to the primary cluster endpoint.
- **Planned relocation**: *managed planned failover*, with no data loss. **Region outage**: *detach and promote* a secondary, done manually.
- Limits:
  - no t3/t4g.medium instances
  - no auto-scaling on secondaries
  - clusters can't be stopped or started individually
  - custom parameter groups are re-applied manually after a major upgrade
  - before 1.4.0.0, a primary writer restart also restarted every secondary reader (1.4.0.0+ has "survivable replicas")
- Only available in a subset of regions, so check before designing around it.
- The alternative for cross-region DR is **Streams-based replication** (a streams consumer app writing to a second cluster).

## Backups

Neptune has continuous backup to S3 with point-in-time restore, manual snapshots, and restore-to-new-cluster (you can change the storage type on restore). Encryption at rest carries through to backups, snapshots and replicas.

## Parameters worth knowing

These are cluster-level unless noted. **Static** ones need a reboot.

| Parameter | Default | Notes |
|---|---|---|
| `neptune_query_timeout` (cluster and instance) | 120000 ms | 10 ms – 2³¹-1 ms. A lower per-query hint wins. Static |
| `neptune_enable_slow_query_log` | `disabled` | `info` or `debug`. Dynamic. `debug` adds lock-wait counters (≥ 1.4.5.0) |
| `neptune_slow_query_log_threshold` | 5000 ms | Dynamic |
| `neptune_enable_audit_log` | 0 | Publish to CloudWatch Logs. Static |
| `neptune_streams` / `neptune_streams_expiry_days` | 0 / 7 | Retention 1–90 days. Static |
| `neptune_dfe_query_engine` (instance) | `viaQueryHint` | `enabled` uses DFE wherever possible. **openCypher always runs on DFE** |
| `neptune_result_cache` (instance) | 0 | Gremlin results cache |
| `neptune_lab_mode` | — | Experimental features, `feature=enabled,…` |
| `neptune_lookup_cache` | 0 (auto 1 on R5d) | |
| `neptune_enable_inline_server_generated_edge_id` | 0 | |
| `UndoLogPurgeConfig` (instance) | `default` | `aggressive` for heavy delete or update churn |

`neptune_enforce_ssl` is deprecated because HTTPS is always enforced.

## Engine versions and upgrades

- Versions are `1.MAJOR.MINOR.PATCH` from 1.3.0.0. `AutoMinorVersionUpgrade` follows the minor number.
- Minor versions stay available at least 6 months, and majors at least 12 months. End-of-life notices arrive at least 3 months ahead (email and Health Dashboard). At end of life, you can't create clusters on that version, and running clusters are **auto-upgraded in a maintenance window**.
- **As of 2026-09:** the latest is **1.4.8.0** (2026-07-27, EOL 2027-10-27). All **1.2.0.0–1.2.1.2 and 1.1.1.0 reach EOL on 2026-12-04**. 1.3.x and early 1.4.x reach EOL on 2027-03-06.
- A major upgrade (1.2 → 1.3/1.4) changes the TinkerPop client version. Test your driver version, serializers and query behaviour on a clone first.

## Observability

- CloudWatch metrics include CPU, memory, `BufferCacheHitRatio`, request counts and errors, replica lag, and main-request-queue depth.
- Slow-query log and audit log go to CloudWatch Logs.
- `/status` shows the engine version, and whether lab mode, DFE and streams are on.
- Query-level analysis uses Gremlin `explain`/`profile`, SPARQL explain, and openCypher explain.

## Cost levers, roughly by impact

1. Right-size the writer and scale **reads with replicas**, not with a bigger writer.
2. **Serverless** for spiky or idle clusters (with a sane `MaxCapacity` and query timeout). Provisioned for steady load.
3. **I/O-Optimized** when I/O is a large share of the bill.
4. Stop dev clusters (not possible inside a Global Database).
5. Keep Streams retention and snapshot counts deliberate.
6. Offload whole-graph analytics to **Neptune Analytics**, sized for the job and deleted afterwards (see `neptune-analytics.md`).
