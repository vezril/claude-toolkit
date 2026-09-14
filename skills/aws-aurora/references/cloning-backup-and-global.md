# Cloning, Backtrack, backups, and Global Database

Source: docs.aws.amazon.com (AmazonRDS/latest/AuroraUserGuide) + AWS's Aurora advisor agent skills. Fetched 2026-09.

## Cloning (copy-on-write)

Aurora cloning creates a new cluster that shares the source cluster's data at the storage layer via a **copy-on-write** protocol — not a data copy.

- At creation, the clone and the source share a **single copy** of the underlying data. Additional storage is only allocated once either the source or the clone **changes** data that diverges from the shared copy.
- Practically instant to create, and cheap until divergence — this is *why* cloning is the recommended way to spin up a realistic test/dev/analytics environment from production data, rather than a snapshot-restore.
- You can create **multiple clones from the same cluster**, and **clones from other clones** — clone chains are supported.
- A clone can be configured **differently from its source** — e.g. a single-instance clone from a multi-instance production cluster, if the clone doesn't need the same HA posture. A clone created with a different deployment configuration than its source uses the source engine's **latest minor version**.
- Clones are created in the **same AWS account** as the source by default; sharing serverless or provisioned clusters/clones **across accounts** is supported via AWS RAM.
- Cross-VPC cloning needs the destination VPC to have subnets covering the AZs the source's storage actually uses (storage always spans exactly three AZs regardless of instance count) — check `describe-db-clusters` for the source's AZ list before creating a cross-VPC clone.
- Delete a clone when done with it; it doesn't clean itself up.

Good uses: schema-change or parameter-group experiments, workload-intensive exports/analytics without touching production, spinning up a dev/test copy of real data — all without any corruption risk to the source.

## Backtrack (Aurora MySQL only)

Rewinds a cluster to an earlier point in time **in place**, without the restore-to-a-new-instance step a snapshot/PITR restore requires. Useful for quickly undoing an unintended write/DDL on MySQL specifically.

**Incompatible with Aurora Global Database** — a cluster that's part of a Global Database cannot use Backtrack. If both matter for a given cluster, you have to choose one; there is no combined configuration.

## How Aurora backups differ from RDS's

The mechanics *look* similar to standalone RDS (see [[aws-rds]]'s `storage-and-backups.md`) — automated backups with a retention window, manual snapshots, PITR — but the underlying implementation differs: Aurora backups are **continuous and incremental at the storage layer**, so unlike traditional volume snapshots, taking a backup **doesn't suspend I/O or degrade performance** on the running cluster. You still configure a retention period and can still take manual snapshots on top of that, exactly as you would on RDS — the operational commands are the same, only the "how" underneath changes.

## Aurora Global Database

Spans a single Aurora database across **multiple AWS Regions** — a primary cluster (all writes) plus **up to five secondary, read-only clusters** in other Regions.

- Replication uses **storage-level block replication**, not the database engine's own replication — Aurora replicates the underlying storage changes directly, which is both faster and lower-overhead than logical/binlog-style replication.
- Replication is **asynchronous**: primary-region writes don't wait for secondary regions to apply them. **Typical replication latency is under 1 second.**
- On a regional degradation or outage, a secondary cluster can be **promoted to full read/write in under 1 minute** — this is the disaster-recovery value proposition; a secondary is not just a read replica, it's a standby region.
- Recent engine updates improved cross-region resiliency further: secondary reader instances can now restart and keep serving reads through unplanned regional events instead of going fully unavailable, and planned cross-region switchovers typically complete with under a minute of writer downtime.
- **Global Database and Backtrack are mutually exclusive** on the same cluster (see above).
- Use for: low-latency local reads for a geographically distributed user base, and/or a genuine regional-outage disaster-recovery posture that goes beyond a single-region Multi-AZ setup.

## Pitfalls

- Reaching for a snapshot-restore workflow to spin up a dev/test copy when cloning would be faster and cheaper.
- Forgetting to delete clones once done with them — they don't expire.
- Trying to combine Backtrack with Global Database on the same cluster — not supported, pick one.
- Assuming Aurora backups have the same performance-impact profile as traditional volume-snapshot backups — they don't; the continuous storage-layer design specifically avoids that.
- Treating a Global Database secondary as read-only-forever — it's specifically designed to be promotable to full read/write during a regional event.
