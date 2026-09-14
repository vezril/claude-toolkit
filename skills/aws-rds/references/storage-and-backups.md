# Storage, backups, and recovery

Source: docs.aws.amazon.com (AmazonRDS/latest/UserGuide, Storage & Backup sections). Fetched 2026-09.

## Storage types

RDS storage is EBS-backed; you choose the type explicitly (this is a key difference from Aurora's auto-scaling cluster storage).

| Type | Best for | Notes |
|---|---|---|
| **General Purpose SSD — gp3** | Most workloads, dev/test through moderate production | Performance (IOPS/throughput) is provisioned **independently of volume size** — the current default recommendation over gp2 |
| General Purpose SSD — gp2 | Legacy | Baseline performance is **determined by volume size** — bigger volume, more baseline IOPS, less flexible than gp3 |
| **Provisioned IOPS SSD — io1 / io2 (Block Express)** | I/O-intensive production workloads needing low, consistent latency | Best suited for production database workloads with demanding IOPS/throughput requirements |
| Magnetic (standard) | None — deprecated | No longer offered for new instances; from **2026-07-01** you can no longer restore a snapshot to magnetic storage either |

**Sizing ceilings:** MySQL, MariaDB, PostgreSQL, and Db2 support up to **64 TiB**. Oracle and SQL Server support up to **256 TiB** using additional storage volumes. Db2 doesn't support the gp2 storage type.

Choose `gp3` by default for anything new; reach for `io1`/`io2` when a workload's IOPS/latency requirements are consistently demanding rather than bursty.

## Automated backups

On by default when you create a DB instance. RDS takes a storage-level snapshot daily and continuously captures transaction logs, letting you restore to **almost any second** within the retention window.

- **Retention: 1–35 days**, your choice. Longer retention = more recovery options, more S3 storage cost (billed separately from instance usage).
- Backups live in S3, region-scoped.
- **Point-in-time recovery (PITR):** restore to any specific second within the retention window. This always creates a **new instance** — the original is left untouched. You can add additional storage volumes with custom configuration (type/size/IOPS/throughput) as part of the same restore call:
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier my-source-instance \
  --target-db-instance-identifier my-pitr-instance \
  --use-latest-restorable-time \
  --additional-storage-volumes '[{"VolumeName":"rdsdbdata","StorageType":"gp3","AllocatedStorage":5000,"IOPS":5000,"StorageThroughput":200}]'
```
- Deleting an instance: choosing to **retain automated backups** keeps them for the rest of the retention period even after the instance is gone; declining deletes them with the instance. A **final manual snapshot** on deletion (recommended) and any pre-existing manual snapshots are unaffected either way.

## Manual snapshots

Point-in-time, user-triggered, and kept **until you explicitly delete them** — independent of the automated-backup retention window and unaffected by instance deletion.

- Up to **100 manual snapshots per Region**.
- Copy a snapshot to another Region to extend backup storage (and cost) into that Region, or as a DR strategy.
- Restoring a manual snapshot, like PITR, always produces a **new instance**.

## Practical guidance

- 7 days is the production floor (see `SKILL.md`'s non-negotiables); go longer for compliance-driven retention needs.
- Automated backups + PITR cover "oops, five minutes ago" scenarios; manual snapshots cover "before this risky migration" and long-term retention scenarios — use both, they're not substitutes for each other.
- Cross-region snapshot copy is the simple DR primitive when cross-region read replicas are more than you need.

## Pitfalls

- Assuming PITR restores in place — it always creates a new instance; you still need to redirect your application afterward.
- Treating manual snapshots as expiring — they don't; a stale collection of forgotten manual snapshots is a real (if minor) cost leak worth periodically auditing.
- Using magnetic/standard storage on anything new — deprecated, and its snapshot-restore path is closing entirely from mid-2026.
