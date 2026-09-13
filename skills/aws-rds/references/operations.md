# Operations: proxying, Blue/Green, monitoring, and cost

Source: AWS's RDS advisor agent skill (rds-oss) + docs.aws.amazon.com. Fetched 2026-09. Scoped to the open-source engines (MySQL/MariaDB/PostgreSQL); Oracle/SQL Server/Db2 have their own engine-specific quirks not covered here.

## RDS Proxy vs PgBouncer / connection pooling

RDS Proxy is a managed connection pooler sitting in front of your instance. Before reaching for it, know what it actually adds over a self-managed pooler already doing connection multiplexing (e.g. PgBouncer in transaction mode):

- If PgBouncer in transaction mode is already deployed and working, the **multiplexing** benefit of switching to RDS Proxy is marginal — that's the primary thing both provide.
- What RDS Proxy adds on top: **no EC2 to operate or patch** (fully managed), **built-in IAM authentication** (PgBouncer doesn't have this natively), **automatic failover integrated with RDS failover events** (reacts in seconds; PgBouncer needs external health checks and manual reconfiguration), and **Secrets Manager integration** for credential rotation without downtime.
- **Recommendation:** if none of those four specific features (managed infra, IAM auth, managed failover, Secrets-Manager-rotated credentials) are actually needed and PgBouncer is working, stay on PgBouncer. Switch only when one of them is a real requirement.
- Common driver for reaching for a proxy at all: Lambda functions opening too many direct connections to RDS — the proxy pools connections across concurrent Lambda invocations instead of each one opening its own.

## Blue/Green deployments

For low-downtime major-version upgrades or schema changes: creates a full replica environment ("green") kept in sync with production ("blue") via the engine's native replication (binlog for MySQL/MariaDB), lets you apply changes to green, then switches traffic over.

**The type-change trap:** a column type change (e.g. `VARCHAR(10)` → `INT`) applied directly on a Blue/Green source **breaks replication**, not because of a vague "row format" issue but because Blue/Green replicates blue → green by **replaying binlog events**, and a type change produces a **different binary representation** on each side — events recorded against the old `VARCHAR` column can't be applied to the new `INT` column on green.

Correct sequence:
1. Validate prerequisites: `binlog_format=ROW`, automated backups enabled (retention > 0), instance `available`.
2. `aws rds create-blue-green-deployment` to stand up green.
3. Let green fully catch up via replication **before** touching schema.
4. Apply the schema change **on green only**, once caught up.
5. `aws rds switchover-blue-green-deployment` **immediately** after the DDL — don't let green run in parallel with blue post-DDL, since the schema divergence breaks further replication from that point.
6. Verify the change against the production endpoint after switchover.

**Switchover is destructive and traffic-moving — always a confirmed, explicit step**, never an automatic "next step" in a sequence you run without a pause. Treat any switchover, purchase, or destructive modification the same way: propose it, then execute only after explicit confirmation.

## Monitoring: Performance Insights vs Enhanced Monitoring

Both exist and answer different questions — don't reach for one when you mean the other:

- **Performance Insights** — database-load-centric: which SQL, which waits, which sessions are driving load right now (`db.load.avg`, sampled active-session data via `DescribeDimensionKeys`). This is "what's the database doing."
- **Enhanced Monitoring** — OS-level metrics from the underlying host (CPU, memory, file system, processes) at up to 1-second granularity. This is "what's the host doing."

Enable both for production; they're complementary, not overlapping. Performance Insights retention of 7 days is free; longer retention costs more and should be a deliberate choice.

## Commitment pricing: Reserved Instances vs Database Savings Plans

For steady-state (24/7, multi-month-plus-confidence) workloads, On-Demand pricing is rarely the cheapest option:

- **Reserved Instances (RI)** — locked to a specific instance type and Region; 1yr or 3yr terms; No/Partial/All Upfront payment options.
- **Database Savings Plans (DSP)** — coverage is scoped to an **instance family** (e.g. `r7g`), not a specific instance type, which is the key advantage if you might resize within the family over the commitment term; **1yr term only** for RDS (unlike RIs' 1yr/3yr choice).
- Both are **region-locked** — moving the workload cross-region forfeits the commitment's benefit.
- A 3yr commitment is a real lock-in: if the workload changes materially or the instance family gets superseded, it's not recoverable in full.
- This is advisory analysis, not a purchase to automate — present the On-Demand/1yr-RI/3yr-RI/1yr-DSP comparison (dollars and percentage savings for each) and let the human decide when to actually buy.

## Upgrade workflow (open-source engines)

1. **Identify the instance and engine** via `describe-db-instances` (never `describe-db-clusters` for standalone RDS — that's Aurora).
2. **Enumerate valid targets** with `describe-db-engine-versions`, filtered to the current engine and major version — don't hand-maintain a version list.
3. **RDS has no LTS concept** — if upgrade advice starts talking about LTS tracks, that's a sign of RDS/Aurora confusion; back up and re-check which product you're actually looking at.
4. **MariaDB reuses MySQL's precheck set** (it's a MySQL fork) but **does not support the RDS Data API** — that's an Aurora Serverless-only feature; don't recommend it for MariaDB.
5. Precheck via SSM Run Command from a client host, or a direct engine-client connection, before committing to a target version.
6. Treat the actual `modify-db-instance --engine-version` call the same way as a switchover: propose it, get explicit confirmation, then run it — never as an unattended step in a longer automated sequence. A snapshot-and-restore dry run in a non-production environment first is the safer default.

## Pitfalls

- Adding RDS Proxy on top of an already-adequate PgBouncer setup for no concrete reason.
- Letting a Blue/Green green environment sit alongside blue after an incompatible schema change instead of switching over immediately.
- Confusing Performance Insights (query/session load) with Enhanced Monitoring (host OS metrics) when diagnosing a performance issue.
- Buying a 3yr RI for a workload whose instance family is likely to change — a DSP would have covered that better.
- Recommending the RDS Data API for anything other than Aurora Serverless.
