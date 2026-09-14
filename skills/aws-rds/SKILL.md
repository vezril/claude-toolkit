---
name: aws-rds
description: "Provisioning, scaling, and operating Amazon RDS (the managed relational database service for MySQL, MariaDB, PostgreSQL, Oracle, SQL Server, and Db2 — distinct from Aurora), distilled from docs.aws.amazon.com and AWS's own RDS advisor agent skill (fetched 2026-09). Covers the RDS-vs-Aurora distinction (instance-based topology and describe-db-instances vs cluster-based and describe-db-clusters; RDS has no LTS versions, no Serverless mode, no I/O-Optimized storage, no Data API), high availability (Multi-AZ DB instance — a synchronous, read-only-standby failover target — vs Multi-AZ DB cluster — two readable reader instances, semisynchronous replication, ~35s failover — vs asynchronous, promotable read replicas, including cross-region and cascading replicas), storage (General Purpose SSD gp2/gp3 vs Provisioned IOPS io1/io2, per-engine size ceilings), backups (automated backups with 1-35 day retention, point-in-time recovery to any second in that window, manual snapshots up to 100/region independent of automated-backup deletion, cross-region snapshot copy), security (KMS encryption at rest, TLS enforcement per engine, IAM database authentication, Secrets Manager-managed master passwords, private-subnet/security-group placement, parameter groups vs option groups, audit logging to CloudWatch Logs), and operations (RDS Proxy vs PgBouncer, Blue/Green deployments and why a column type change breaks binlog replication, Performance Insights vs Enhanced Monitoring, Reserved Instances vs Database Savings Plans, a production instance-creation checklist with the exact CLI flags). Use when provisioning an RDS instance, choosing an HA/read-scaling topology, sizing storage, setting up backups or PITR, hardening RDS security, evaluating RDS Proxy or Blue/Green, or deciding between RDS and Aurora."
license: MIT
---

# Amazon RDS

How to provision and operate Amazon RDS — the managed relational database service for **MySQL, MariaDB, PostgreSQL, Oracle, SQL Server, and Db2**. Distilled from `docs.aws.amazon.com` and AWS's own RDS advisor agent skill, fetched 2026-09. Cross-links: [[aws-lambda]] for RDS Proxy + Lambda connection patterns, [[secure-coding]] for the encryption/credential hardening below, [[python]]/[[nodejs]] for application-side connection handling.

> **Freshness.** Engine version numbers, quotas, and pricing here are a 2026-09 snapshot — always confirm the current latest version with `describe-db-engine-versions` rather than hardcoding one.

## RDS is not Aurora — check this first

RDS (this skill) and Aurora are different products with different semantics, even though both live under "Amazon RDS" in the console. Applying Aurora concepts to standalone RDS (or vice versa) is the single most common mistake:

| Concept | RDS (MySQL/MariaDB/PostgreSQL/Oracle/SQL Server/Db2) | Aurora |
|---|---|---|
| Topology | **Instance-based** — `describe-db-instances` | **Cluster-based** — `describe-db-clusters` |
| LTS releases | Don't exist | Exist |
| Serverless mode | Doesn't exist | Aurora Serverless v2 |
| I/O-Optimized storage | Doesn't exist | `aurora-iopt1` |
| Data API | Not available | Available on Aurora Serverless clusters |
| Upgrade scope | Per-instance | Per-cluster (writer + readers together) |
| Storage | EBS-backed, you choose the type/size | Distributed cluster storage, auto-scales |

If an identifier turns out to be `aurora-mysql` or `aurora-postgresql`, you're looking at Aurora — different tooling, different mental model, out of scope for this skill. See [[aws-aurora]] for that product.

## The mental model

An RDS **DB instance** is a managed VM running your chosen engine, backed by an **EBS volume** you size and type explicitly (unlike Aurora's auto-scaling cluster storage). Everything else — Multi-AZ, read replicas, backups, Performance Insights — layers on top of that one instance concept.

```
DB instance (engine + instance class + EBS storage)
├── Multi-AZ DB instance  → 1 synchronous standby, failover target, NOT readable
├── Multi-AZ DB cluster   → 2 readable readers, semisynchronous, ~35s failover
├── Read replica(s)       → async, readable, promotable to standalone, optionally cross-region
├── Automated backups     → daily snapshot + transaction logs, 1–35 day retention, PITR to any second
├── Manual snapshots      → point-in-time, kept until you delete them (up to 100/region)
├── Parameter group       → engine config (my.cnf/postgresql.conf-style settings)
└── Option group          → engine features that need extra IAM/network wiring (MySQL/Oracle/SQL Server only)
```

## Non-negotiables (production defaults — apply unless told otherwise)

Straight from AWS's own RDS advisor skill's production checklist:

1. **Check the latest engine version with `describe-db-engine-versions`** — never hardcode one. For MySQL specifically, prefer 8.4.x over 8.0.x (earlier end-of-standard-support date).
2. **Multi-AZ on** for anything production — `--multi-az`.
3. **Storage encrypted with a customer-managed KMS key** — `--storage-encrypted --kms-key-id <arn>`, not the default AWS-owned key, so you control rotation and cross-account sharing.
4. **`--no-publicly-accessible`.** No production database should be reachable from the internet.
5. **7-day backup retention minimum** — `--backup-retention-period 7`.
6. **Performance Insights on, 7-day retention** — `--enable-performance-insights --performance-insights-retention-period 7`; add `--performance-insights-kms-key-id` if captured queries might contain sensitive literals.
7. **Deletion protection on** — `--deletion-protection`.
8. **Never a default master username** (`admin`, `root`, `postgres`, `master`) — pick something custom; default names make credential-guessing attacks easier.
9. **`--manage-master-user-password`, never a plaintext `--master-user-password`** — this provisions and rotates the password in Secrets Manager automatically.
10. **`gp3` storage**, not `gp2` — cheaper, faster, no minimum-IOPS purchase requirement.
11. **TLS enforced at the parameter-group level**: `require_secure_transport=ON` (MySQL/MariaDB) or `rds.force_ssl=1` (PostgreSQL) — the client flag alone isn't enough.
12. **Database logs exported to CloudWatch Logs, encrypted with KMS** — `--enable-cloudwatch-logs-exports '["error","slowquery","audit"]'` (MySQL/MariaDB) or `'["postgresql"]'` (PostgreSQL); logs can carry SQL literals and usernames.

See `references/security-and-access.md` for the full CLI example and `references/operations.md` for what *not* to auto-execute (upgrades, purchases, switchovers are advisory-only, not fire-and-forget).

## References

- `references/high-availability.md` — Multi-AZ DB instance vs Multi-AZ DB cluster vs read replicas: the differences that actually matter (readability, replication mode, failover time, promotion).
- `references/storage-and-backups.md` — storage types and sizing ceilings, automated backups and PITR mechanics, manual snapshots, cross-region copy.
- `references/security-and-access.md` — encryption at rest/in transit, IAM auth, Secrets Manager password management, network placement, parameter vs option groups, audit logging, the full production `create-db-instance` example.
- `references/operations.md` — RDS Proxy vs PgBouncer, Blue/Green deployments (and the binlog-replication trap), Performance Insights vs Enhanced Monitoring, Reserved Instances vs Database Savings Plans, the upgrade workflow.
