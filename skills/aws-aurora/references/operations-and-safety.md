# Operations, cost, and safety tiers

Source: AWS's Aurora MySQL/PostgreSQL advisor agent skills + docs.aws.amazon.com. Fetched 2026-09.

## I/O-Optimized vs Standard storage

Two storage configurations, chosen per cluster:

- **Aurora Standard** — pay per instance/storage plus **per I/O request**. Cost-effective for workloads with moderate, predictable I/O.
- **Aurora I/O-Optimized** (`aurora-iopt1`) — higher instance/storage price, but **no separate charge per I/O request**. Wins once I/O volume is high enough that the per-request charges under Standard would exceed the I/O-Optimized premium.

**Rule of thumb:** if I/O costs are running above roughly **25% of total Aurora spend** on Standard storage, it's worth evaluating a switch to I/O-Optimized — that's the threshold AWS's own advisor skills use to trigger the analysis (run the actual numbers for your instance mix and monthly I/O volume rather than switching on the heuristic alone).

**Switching constraints:**
- Aurora Standard → I/O-Optimized: **once every 30 days**.
- I/O-Optimized → Aurora Standard: **anytime**, no cooldown.
- **No downtime** for most instance classes; a **restart is required** for NVMe/Optimized Reads instance classes (`r6gd`, `r6id`, `r8gd`).

Treat a storage-type switch as a Tier-2 "state the risk, then confirm" change (downtime possibility on some instance classes, and the 30-day one-way cooldown) — not a routine toggle.

## The RDS Data API

An HTTP-based, **connectionless** way to run SQL against an Aurora cluster — no persistent database connection, no connection pool to manage, authenticated via IAM. Enable with:

```bash
aws rds modify-db-cluster --db-cluster-identifier my-cluster --enable-http-endpoint
```

Particularly useful from Lambda or other bursty/serverless callers where opening a real database connection per invocation would exhaust the cluster's connection limit — the Data API sidesteps that problem entirely by not holding a connection open. Trade-off: it's an HTTP round-trip per call, with its own latency and payload-size characteristics — not a drop-in replacement for every connection-pooled workload, but a strong fit for exactly the "many short-lived serverless callers" case.

## Aurora PostgreSQL express configuration

Aurora PostgreSQL's default creation path is **express configuration**: a single API call, AWS-managed connectivity via an **Internet Access Gateway** (no customer VPC required), and **IAM-only authentication — no master password exists on an express cluster**.

```bash
aws rds create-db-cluster --with-express-configuration ...
```
Don't separately pass `--engine-mode`, `--serverless-v2-scaling-configuration`, `--master-username`, or `--manage-master-user-password` — the express flag sets all of that for you.

**Use express by default** for a quick PostgreSQL start; route to **full (VPC-based) configuration** only when any of these apply: a specific customer VPC/subnet group/security group, a customer-managed KMS key, a custom cluster parameter group **at creation time**, or a specific pinned engine version. Express clusters remain customizable after creation (e.g. you can attach a custom parameter group post-create), so "might need that later" isn't itself a reason to start with full configuration.

**Aurora MySQL has no express path** — it's full (VPC-based) configuration only.

Connect to an express cluster the same way as any IAM-authenticated database: `aws rds generate-db-auth-token` for a short-lived (15-minute) token.

## Commitment pricing

- **Reserved Instances (RI)** — provisioned clusters only, 1yr or 3yr terms.
- **Database Savings Plans (DSP)** — available for **both** provisioned and Aurora Serverless v2 clusters; for serverless, DSP is the **only** commitment option (no RI equivalent for serverless capacity).
- Same trade-offs as standalone RDS commitment pricing apply (family-scoped flexibility, region-lock, multi-year lock-in) — see [[aws-rds]]'s `operations.md` for the general RI-vs-DSP reasoning.
- This is advisory analysis — present the comparison with real dollar/percentage figures, never execute a purchase automatically.

## Operational safety tiers (apply this framework to any Aurora change)

**Tier 1 — routine, confirm and proceed:** creating a cluster/instance, adjusting Serverless v2 min/max ACU, changing backup retention period, toggling deletion protection, enabling CloudWatch Logs export, changing the preferred backup window, enabling the Data API (`--enable-http-endpoint`), tagging.

**Tier 2 — state the specific risk, then confirm:** switching storage type (downtime on NVMe/Optimized Reads classes, 30-day one-way cooldown), changing an instance class (**causes a failover**), a **minor** engine-version upgrade (brief restart/failover; `--apply-immediately` bypasses the maintenance window and needs its own explicit confirmation).

**Tier 3 — block and redirect, don't execute even with confirmation:** deleting a cluster or instance (irreversible — offer to help with a final snapshot first instead), manual failover or Blue/Green switchover, a **major** engine-version upgrade (needs prechecks and a rollback plan — offer an upgrade assessment instead), any credential/password modification (redirect to Secrets Manager rotation or the console), changing VPC security groups (network security posture — redirect to change-control), changing the DB cluster parameter group (can break the application — offer a diff/comparison instead), making an instance publicly accessible (never — offer the Data API, express configuration, or a bastion instead), purchasing an RI or Savings Plan (redirect to a cost analysis instead), and rebooting an instance or cluster (offer to check for pending modifications and recommend a maintenance window instead).

The shape that matters across all of Tier 3: **explain why, then offer the safe alternative** — never a bare refusal, and never proceed on confirmation alone for something on this list.

## Version-upgrade gotchas

- **Aurora MySQL major vs minor:** version format is `major.minor.patch`. `3.06` → `3.08` is a **minor** upgrade (leading digit `3` unchanged). A leading-digit change (`2.x` → `3.x`, i.e. MySQL 5.7-compatible → 8.0-compatible) is **major**. When genuinely unsure, treat it as major — the safer default given Tier 3's block on major upgrades.
- **Aurora has LTS versions** — unlike standalone RDS, which has no LTS concept at all (see [[aws-rds]]). Don't apply RDS's "no LTS" fact to Aurora, or vice versa.

## Pitfalls

- Switching storage type back and forth without accounting for the 30-day one-way cooldown on Standard→I/O-Optimized.
- Enabling the Data API and still maintaining a large connection-pooled fleet of callers that didn't need one — pick the right tool per caller shape.
- Treating a minor-version bump as risk-free because "minor" sounds small — it still causes a brief restart.
- Executing any Tier 3 action because the user said "yes" once, without having stated the specific risk first (or, for the genuinely irreversible ones, executing at all).
