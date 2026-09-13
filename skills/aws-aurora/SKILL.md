---
name: aws-aurora
description: "Provisioning and operating Amazon Aurora (MySQL- and PostgreSQL-compatible clusters, distinct from standalone RDS), distilled from docs.aws.amazon.com and AWS's own Aurora MySQL/PostgreSQL advisor agent skills (fetched 2026-09). Covers the shared-storage architecture (a cluster volume auto-replicated six ways across three AZs in 10 GiB segments, tolerating the loss of two copies with no write impact and three with no read impact, decoupled from compute so adding a reader copies no data), the cluster topology (one writer + up to 15 readers, promotion-tier failover 0-15 with largest-instance tiebreak, cluster/reader/instance endpoints), Aurora Serverless v2 (ACU capacity units in 0.5 increments up to 128, scale-to-zero on supporting versions, reader promotion-tier coupling to writer capacity, mixed provisioned+serverless clusters), cloning (copy-on-write, minimal initial storage, cross-account via RAM), Backtrack (MySQL-only, in-place rewind, incompatible with Global Database) and Aurora Global Database (up to five secondary regions, <1s typical storage-based replication, <1 minute promotion on regional outage), I/O-Optimized vs Standard storage (the 25%-of-spend threshold rule, once-per-30-days switch-back limit), the RDS Data API (HTTP/IAM-authenticated, connectionless), Aurora PostgreSQL express configuration (single-call, no-VPC, IAM-only quick start) vs full VPC-based configuration, commitment pricing (RI for provisioned, Database Savings Plans for both provisioned and serverless), and the operational safety tiers AWS's own skills apply (never public accessibility; confirm-then-execute for routine changes; block-and-redirect for deletes, failovers, credential changes, and purchases). Use when provisioning an Aurora cluster, choosing Aurora Serverless v2 vs provisioned, sizing ACUs, evaluating I/O-Optimized storage, setting up Global Database or cloning, deciding RDS vs Aurora, or reviewing an Aurora architecture for production readiness."
license: MIT
---

# Amazon Aurora

How Aurora's architecture actually works, and how to operate it without the safety mistakes AWS's own advisor skills specifically guard against. Distilled from `docs.aws.amazon.com` and AWS's Aurora MySQL/PostgreSQL agent skills, fetched 2026-09. Cross-links: [[aws-rds]] for the RDS-vs-Aurora distinction and for standalone RDS (Aurora is a different product, not a superset), [[aws-lambda]] for Data API / RDS Proxy from Lambda, [[secure-coding]] for the credential/network hardening below.

## Aurora is not "RDS but faster" — the architecture is genuinely different

RDS attaches an EBS volume you size yourself, per instance. Aurora decouples storage from compute entirely: every instance in a cluster — writer and every reader — reads and writes the **same distributed storage volume**, not its own copy.

```
Aurora cluster
├── Writer instance ──┐
├── Reader instance ──┼──▶ shared cluster volume (10 GiB segments, 6 copies, 3 AZs)
├── Reader instance ──┘        - lose 2 copies → writes still fine
└── (up to 15 readers total)   - lose 3 copies → reads still fine
                                 - self-healing: blocks/disks continuously scanned and repaired
```

This shared-storage design is *why* Aurora behaves differently from RDS in ways that matter operationally: adding a reader is fast because it attaches to existing storage rather than copying data; cloning is fast and cheap because it's copy-on-write at the storage layer; there's no separate "Multi-AZ" toggle the way RDS has one — the storage layer's cross-AZ replication is inherent to every Aurora cluster.

For the full point-by-point contrast (instance-based vs cluster-based topology, LTS, Serverless, Data API, `describe-db-instances` vs `describe-db-clusters`), see the table in [[aws-rds]]'s `SKILL.md`.

## Two engines, mostly-shared operations

Aurora MySQL and Aurora PostgreSQL share the cluster/storage architecture, Serverless v2, cloning, Backtrack (MySQL only), and Global Database. They diverge on:

| | Aurora MySQL | Aurora PostgreSQL |
|---|---|---|
| Creation flow | Full (VPC-based) only | **Express** (single API call, no VPC, IAM-only auth) is the default; full config for custom VPC/KMS/parameter group/pinned version |
| Distinctive feature | Parallel Query (push scan-heavy analytical queries down to the storage layer, bypassing the buffer pool) | Babelfish (SQL Server wire-protocol compatibility), pgvector (vector similarity search) |
| Version numbering | `major.minor.patch`, e.g. `3.06`→`3.08` is a **minor** upgrade (leading digit unchanged); `2.x`→`3.x` (5.7→8.0 compatibility) is **major** | Standard PostgreSQL major.minor versioning |

**Aurora has LTS versions — RDS (standalone) does not.** Don't carry RDS's "no LTS" fact over to Aurora, and don't carry Aurora's LTS guidance back onto standalone RDS.

## Non-negotiables

1. **Never `--publicly-accessible`.** AWS's own Aurora skills treat this as an outright block, not a warning — there is no legitimate reason, even for a prototype. Use the RDS Data API (HTTPS + IAM auth, no network path needed), Aurora PostgreSQL express configuration (IAM-only via the Internet Access Gateway, no VPC needed), an EC2 bastion with an SSH tunnel, or a workload inside the same VPC.
2. **Destructive and credential operations are confirm-then-execute at best, block-and-redirect at worst.** `delete-db-cluster`/`delete-db-instance`, `failover-db-cluster`, `switchover-blue-green-deployment`, a major-version `--engine-version` change, `--master-user-password`/`--manage-master-user-password`, `--vpc-security-group-ids`, `--db-cluster-parameter-group-name`, and any RI/Savings Plan purchase should never be executed unattended — treat these the way AWS's own advisor skills do: explain the risk, get explicit confirmation, or redirect to console/change-control entirely for the irreversible ones. See `references/operations-and-safety.md` for the full tiering.
3. **Credentials:** rotate via Secrets Manager or the console, never a direct password-modify API call. `aws rds generate-db-auth-token` (a 15-minute IAM token) is the approved way to get a short-lived credential when IAM database authentication is enabled.
4. **Storage-type switches are rate-limited in one direction.** Aurora Standard → I/O-Optimized is allowed **once per 30 days**; I/O-Optimized → Standard can happen anytime. Factor that asymmetry into the decision, not just the cost comparison.
5. **A minor engine-version bump still causes a brief restart/failover** (applied in the maintenance window, or immediately with `--apply-immediately`, which itself bypasses the maintenance window and needs its own confirmation). Don't treat "minor" as "no impact."
6. **`modify-db-instance --db-instance-class` triggers a failover** in a Multi-instance cluster — size changes are not free even when they sound routine.

## Quick reference

| Parameter | Value |
|---|---|
| Storage segment size | 10 GiB, replicated 6× across 3 AZs |
| Max cluster volume | 64 TiB |
| Max readers per cluster | 15 |
| Promotion tier range | 0 (first) – 15 (last); ties broken by largest instance |
| Serverless v2 ACU range | 0.5 – 128, half-step increments; **0** on versions supporting auto-pause |
| Global Database secondary regions | Up to 5 |
| Global Database replication latency | Typically < 1 second |
| Global Database secondary promotion time | Typically < 1 minute |
| Standard → I/O-Optimized switch frequency | Once per 30 days |
| I/O-Optimized → Standard | Anytime |

## References

- `references/architecture-and-availability.md` — the shared storage layer, quorum durability math, promotion tiers and failover, cluster/reader/instance endpoints.
- `references/serverless-and-scaling.md` — Aurora Serverless v2 ACUs, scale-to-zero, mixed provisioned+serverless clusters, Parallel Query, sizing approach.
- `references/cloning-backup-and-global.md` — copy-on-write cloning, Backtrack, Aurora Global Database, how Aurora backups differ operationally from RDS's.
- `references/operations-and-safety.md` — I/O-Optimized vs Standard (the 25% rule), the Data API, Aurora PostgreSQL express configuration, commitment pricing, and the full confirm/block operational safety tiers.
