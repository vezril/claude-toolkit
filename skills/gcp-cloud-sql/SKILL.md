---
name: gcp-cloud-sql
description: "Google Cloud SQL — fully managed MySQL, PostgreSQL, and SQL Server: a VM-shaped instance you size vertically (vCPU/memory tiers, up to 64 TB storage) with read replicas for scale-out reads; Enterprise vs Enterprise Plus editions (99.95% vs 99.99% SLA, <60s vs <1s maintenance, 7 vs 35-day PITR, data cache); connectivity via Cloud SQL Auth Proxy / language connectors (IAM-authorized, TLS 1.3) > private IP (PSA peering or PSC) > public IP + authorized networks; regional HA = synchronous standby + automatic failover on the same connection string, PITR via binlog/WAL, IAM database authentication. Use when creating/sizing/connecting a Cloud SQL instance, wiring the Auth Proxy or private IP, designing HA/replica/backup/PITR topology, tuning maintenance windows, estimating cost, or choosing Cloud SQL vs AlloyDB vs Spanner vs self-managed."
license: MIT
---

# gcp-cloud-sql

Cloud SQL is Google Cloud's fully managed relational database service for **MySQL, PostgreSQL, and SQL Server** — Google runs the VM, OS patching, replication, backups, and failover; you get a normal database endpoint with the stock engine and (almost all of) its flags.

Engines and versions (per docs at fetch time):
- **MySQL** — 8.0 and 8.4 on both editions; 5.6/5.7 linger on Enterprise only (5.6 lacks IAM auth).
- **PostgreSQL** — current majors on both editions; Enterprise Plus unlocks data cache and the bigger machine series.
- **SQL Server** — Enterprise edition instances with Microsoft licensing folded into pricing (or BYOL).
- Engine behavior is stock: you tune with the engine's own flags via `gcloud sql instances patch --database-flags=...`; a handful of flags and superuser are restricted because Google operates the box.

## The mental model

**A managed VM-shaped database, not a distributed one.** One instance = one primary VM with a persistent disk. You scale it **vertically** (bigger machine tier) and add **read replicas** for read scale-out. It is NOT horizontally sharded and writes never scale beyond the primary — that's Spanner's (or AlloyDB's, partially) territory. Consequences:

- **Region is forever.** The region you pick at create time can't be changed; moving means replica-promote or dump/restore.
- **Replicas ≠ HA.** Read replicas are *asynchronous* copies for read traffic and DR; HA is a *synchronous* standby in another zone of the same region. Different mechanisms, different problems solved.
- **The connectivity decision tree is where everyone stumbles**, not SQL. Learn it first (below).
- **Editions are a real fork.** Enterprise Plus is not just a bigger tier — different machine series (N2/C4A vs N4/shared-core), data cache, near-zero-downtime maintenance, longer PITR, better SLA.

## Connectivity — the decision tree

Preference order: **Auth Proxy / language connectors > private IP (direct) > public IP + authorized networks.**

1. **Cloud SQL Auth Proxy** (`cloud-sql-proxy` binary) — client-side sidecar/daemon. Authorizes connections with **IAM** (caller needs the **Cloud SQL Client** role, `cloudsql.instances.connect`), auto-refreshes OAuth 2.0 tokens, and encrypts with **TLS 1.3** with automatic cert rotation. No authorized-network config, no manual SSL certs. It does **not** pool connections (pair with pgbouncer/HikariCP) and does not encrypt the app→proxy hop (keep them co-located).
2. **Language connectors** (Java, Python, Go, Node.js libraries) — same IAM+TLS story as the proxy, embedded in your app; no separate process.
3. **Private IP** — instance gets an RFC 1918 address inside a VPC, via **private services access** (VPC peering to Google's producer network, single-VPC) or **Private Service Connect** (endpoint-based, works across VPCs/projects/orgs). Docs recommend direct connections over private IP, with SSL/TLS enforced. Requires the VPC plumbing to exist first.
4. **Public IP + authorized networks** — CIDR allowlist on an internet-facing address. Last resort; ephemeral client IPs (home ISPs, serverless) make the allowlist churn constantly — use the proxy instead.

**IAM database authentication** (MySQL, PostgreSQL; not MySQL 5.6): database users are IAM principals or groups; the "password" is a short-lived (1 h) OAuth token. With the proxy/connectors' **automatic IAM authn** (`--auto-iam-authn`), token handling disappears entirely. Users need **Cloud SQL Instance User** (`cloudsql.instances.login`); usernames are lowercase; login quota 12,000/min/instance; up to 200 IAM groups per instance. Prefer this over built-in passwords.

## Reliability

**Regional HA (the instance-level checkbox):**
- An HA instance is a *regional instance*: primary + standby in two zones, with every write **synchronously replicated** to persistent disks in both zones before commit is acknowledged.
- Heartbeat failure triggers **automatic failover**; expect ~60 seconds of unavailability; the standby takes over the **same IP / connection string** — no app change. The old primary is recreated as the new standby.
- The standby is **not readable** — it's insurance, not capacity. An HA instance costs **2× a standalone** (compute doubles; that's the SLA's price).

**Editions (Enterprise vs Enterprise Plus):**
- SLA: **99.95% excluding maintenance** vs **99.99% including maintenance**.
- Maintenance connectivity loss: **<60 s** vs **<1 s** (near-zero-downtime planned maintenance).
- PITR window: up to **7 days** vs up to **35 days**.
- Enterprise Plus adds **data cache** (local SSD read cache), write optimization, advanced DR with write endpoints, N2/C4A machine series, and longer Query Insights retention (30 d vs 7 d).

**Read replicas:**
- Asynchronous, read-only copies; in-region, **cross-region**, or **cascading** (up to 4 levels including the primary; ~10 direct replicas per primary recommended). External (off-GCP) MySQL replicas are supported.
- Any replica can be **promoted** to a standalone primary (the manual DR lever; a promoted cascade keeps its sub-tree).
- No backups configured on replicas; they follow the primary's maintenance schedule (replicas update first).

**Backups & PITR:**
- Automated backups on a schedule + retention you set (classic default 7, up to 365 days; enhanced backups via the Backup and DR service reach 10 years); on-demand backups kept until deleted. Backups are stored separately from the instance.
- **PITR** replays **binary logs (MySQL) / write-ahead logs (PostgreSQL)** on top of a backup to any instant in the window — requires binlog/PITR enabled, and a restore **creates a new instance** (never in-place).
- Don't hand-prune automated backups: PITR depends on the backup + log chain being intact.

**DR shape:** HA covers a zone failure inside one region; a **cross-region replica** (promotable) covers a region failure. Enterprise Plus adds advanced DR with write endpoints so the promoted topology keeps a stable write address. Rehearse the promotion path — it is the part that fails when untested.

## Shapes (verify flags with `gcloud sql ... --help`; never invent)

```bash
# Create (MySQL example; --edition=ENTERPRISE_PLUS for Plus; --no-assign-ip + --network for private-only)
gcloud sql instances create my-instance \
  --database-version=MYSQL_8_4 --region=us-central1 \
  --tier=db-custom-4-16384 --edition=ENTERPRISE \
  --enable-bin-log --backup-start-time=03:00 --root-password=...

# Quick connect (opens temporary access, uses the proxy under the hood)
gcloud sql connect my-instance --user=root

# Auth Proxy: instance connection name is PROJECT:REGION:INSTANCE
./cloud-sql-proxy --port 5432 my-project:us-central1:my-instance
./cloud-sql-proxy --private-ip --auto-iam-authn my-project:us-central1:my-instance
```

Then point your app at `127.0.0.1:<port>` as if the database were local.

Other everyday shapes: `gcloud sql instances patch` (flags, tier resize — resizes restart the instance),
`gcloud sql backups create --instance=...`, `gcloud sql instances promote-replica REPLICA`,
`gcloud sql users create ... --type=cloud_iam_user` for IAM-auth users. In Kubernetes, run the
proxy as a sidecar container; on Cloud Run, prefer the built-in Cloud SQL connection or a connector.

## Gotchas

- **Maintenance restarts the instance.** Set a maintenance window (else Google picks from defaults); notifications ≥1 week ahead; reschedule up to 24 h before; deny-maintenance periods block up to 90 days but can't be chained forever. Enterprise Plus shrinks the blip to <1 s.
- **Storage auto-grow is one-way.** Automatic storage increases are permanent — you can never shrink an instance's disk. Recovering space means migrating to a new smaller instance.
- **Connection limits scale with tier.** `max_connections` defaults track machine size (flag-overridable); serverless callers are capped too (e.g. 100 connections per Cloud Run/App Engine instance). Pool aggressively — the proxy won't do it for you.
- **Ephemeral/public IP churn:** authorized-network allowlists rot as client IPs change; every hour spent curating them is an argument for the proxy.
- **Region immutability + zonal default:** HA is opt-in; a default (zonal) instance has no standby and a zone outage takes it down.
- **Limits shape:** up to 64 TB storage (dedicated-core), ~1,000 instances/project on the new network architecture, MySQL ~50k tables by default.
- **Pricing shape:** per-second billing of **vCPU + memory** (by tier/region) + **provisioned storage GB-month** + **network egress** + **backup storage**; **HA doubles compute**; Enterprise Plus rates > Enterprise; committed-use discounts (1/3-year) cut compute; SQL Server adds per-core license fees (or BYOL).

## vs siblings

- **AlloyDB** — PostgreSQL-compatible but re-architected (separated compute/storage, columnar engine, read pools). Pick for demanding Postgres (analytics-on-OLTP, higher write throughput); Cloud SQL for stock-engine fidelity, SQL Server/MySQL, lower entry cost.
- **Spanner** — horizontally scalable, globally consistent, but not wire-compatible with any stock engine. Pick when a single-primary write ceiling or multi-region synchronous consistency is the actual problem.
- **Self-managed on GCE** — full control (any engine version, superuser, OS access) and full toil (patching, replication, backups, failover are your pager). Cloud SQL trades a few restricted flags/superuser bits for all of that ops work.
- **Memorystore (Redis)** — cache in front of Cloud SQL, not a durability peer.

## Related

[[gcp-alloydb]], [[gcp-spanner]], [[gcp-bigquery]], [[gcp-memorystore-redis]], [[gcp-compute-engine]], [[gcp-vpc]], [[gcp-iam]], [[gcp-secret-manager]], [[gcp-cloud-run]], [[gcp-gke]], [[gcp-cloud-monitoring]]

Sources: https://docs.cloud.google.com/sql/docs, https://docs.cloud.google.com/sql/docs/editions-intro, https://docs.cloud.google.com/sql/docs/mysql/connect-overview, https://docs.cloud.google.com/sql/docs/mysql/sql-proxy, https://docs.cloud.google.com/sql/docs/mysql/high-availability, https://docs.cloud.google.com/sql/docs/mysql/replication, https://docs.cloud.google.com/sql/docs/mysql/backup-recovery/backups, https://docs.cloud.google.com/sql/docs/mysql/iam-authentication, https://docs.cloud.google.com/sql/docs/mysql/maintenance, https://docs.cloud.google.com/sql/docs/mysql/quotas, https://cloud.google.com/sql/pricing (fetched 2026-07).
