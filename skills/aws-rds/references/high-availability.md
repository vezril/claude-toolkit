# High availability and read scaling

Source: docs.aws.amazon.com (AmazonRDS/latest/UserGuide) + AWS's RDS advisor agent skill. Fetched 2026-09. Three distinct topologies get conflated constantly — they have different read behavior, replication mode, and failover time.

## Multi-AZ DB instance (the classic HA option)

One primary, one **synchronous** standby in a different AZ. The standby is a **failover target only** — you cannot read from it, and it has no separate endpoint. On failure, RDS flips the instance's DNS endpoint to the standby; your application reconnects to the same endpoint.

- Replication to the standby is synchronous — a committed write is durable on both before the client gets the ack.
- If you also have read replicas off a Multi-AZ instance, and the primary fails over, those replicas **automatically re-point to the new primary** (the promoted standby) as their replication source.
- You can additionally make a **read replica itself** a Multi-AZ DB instance — RDS creates a standby of the replica for the replica's own failover support, independent of whether the source is Multi-AZ.

## Multi-AZ DB cluster (higher-availability, lower-latency option)

One writer, **two reader instances**, each in a different AZ, using the engine's native replication. This is a genuinely different architecture from a Multi-AZ *instance*:

- Replication is **semisynchronous** — a write commits once **at least one** reader has acknowledged it, not all of them. Lower write latency than a Multi-AZ instance as a result.
- **Both readers are readable** — they serve real read traffic (via a dedicated reader endpoint) *and* act as automatic failover targets, unlike a Multi-AZ instance's non-readable standby.
- On a writer outage, RDS fails over to whichever reader has the most recent change record. **Failover typically completes in well under 35 seconds** (both readers must apply outstanding transactions from the failed writer first).
- For RDS for MySQL Multi-AZ DB clusters specifically, **every table should have a primary key** — its absence is a documented cause of replication errors.
- Introspect with `describe-db-clusters` (cluster-based, like Aurora — not `describe-db-instances`).

## Read replicas (async, for read scaling — not primarily HA)

Asynchronous, engine-native replication to one or more separate, independently addressable, readable instances.

- Can be created from either a single-AZ or Multi-AZ source instance.
- MySQL/MariaDB/PostgreSQL support cascading (second-tier) replicas — a replica of a replica — to spread replication load.
- Cross-region replicas are supported for disaster-recovery or latency-driven read placement.
- A replica can be **promoted** to a standalone, independent read/write instance — this breaks the replication link permanently.
- Lag is real and unbounded in the worst case — read replicas are eventually consistent; don't route read-after-write-sensitive queries to them without accounting for that.

## Choosing between them

| Need | Use |
|---|---|
| Simple automatic failover, no read scaling need | Multi-AZ DB instance |
| Lower write latency than a Multi-AZ instance, AND want to scale reads on the same topology | Multi-AZ DB cluster |
| Scale read throughput across many replicas, don't need sub-minute failover | Read replica(s) |
| Cross-region DR or geographically local reads | Cross-region read replica |
| None of the above is enough (need auto-scaling storage, Serverless, sub-second failover) | Reconsider Aurora — different product, see `SKILL.md` |

## Pitfalls

- Assuming a Multi-AZ **instance**'s standby is readable — it isn't; that's the Multi-AZ **cluster** feature.
- Using `describe-db-instances` to look for a Multi-AZ cluster's topology — clusters need `describe-db-clusters`.
- Treating read replica lag as negligible — it isn't guaranteed bounded.
- Forgetting that promoting a read replica is one-way — you can't easily undo it back into a replication relationship.
