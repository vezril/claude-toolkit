# Architecture and availability

Source: docs.aws.amazon.com (AmazonRDS/latest/AuroraUserGuide) + AWS's Aurora MySQL/PostgreSQL agent skills. Fetched 2026-09.

## The shared cluster volume

Aurora automatically divides the database volume into **10 GiB segments** spread across many disks, and replicates each segment **six ways across three Availability Zones** — two copies per AZ. This isn't a backup mechanism; it's the live storage layer every instance in the cluster reads and writes.

Durability/availability math that falls out of the 6-copies-3-AZs design:
- **Lose up to 2 copies** (of 6) → write availability unaffected.
- **Lose up to 3 copies** → read availability unaffected.
- Storage is **self-healing** — blocks and disks are continuously scanned for errors and repaired automatically, with no operator action.

**All instances in a cluster share this one volume** — this is the core architectural difference from RDS's per-instance EBS storage, and it's why several Aurora behaviors are fast in ways RDS isn't:
- **Adding a reader instance is quick** because Aurora doesn't copy data — the new instance just attaches to the existing shared volume.
- **Removing an instance doesn't touch the underlying data** — only deleting the entire cluster removes data.
- **Cloning is fast and cheap** (see `cloning-backup-and-global.md`) because it's copy-on-write against the same storage layer.

**Sizing ceiling:** cluster volume — and therefore max table size — is **64 TiB**. The volume auto-grows as your data grows; you don't pre-provision storage size the way you do on RDS.

**There's no separate "Multi-AZ" toggle on Aurora the way there is on RDS.** The 3-AZ storage replication is inherent to every cluster; what you configure instead is *how many readable instances* you run and *where*.

## Failover and promotion tiers

Every instance in a cluster (writer and readers) has a **promotion tier**, 0–15. On a writer failure, Aurora promotes the reader with the **highest priority** (lowest tier number); ties are broken by **the largest instance**. You can change promotion tiers at any time without triggering a failover.

- Tiers can be set per-instance in the console (Failover priority) or via CLI/API (`PromotionTier` on `DBClusterMember`).
- For **Aurora Serverless v2 readers** specifically, the promotion tier does double duty: it also controls whether that reader scales up to match the writer's capacity or scales independently. Readers in **tier 0 or 1** are kept at a minimum capacity at least as high as the writer, so they're immediately ready to take over on failover. Readers in **tiers 2–15** have no such floor and can scale down to the cluster's configured minimum ACU when idle. If the writer is a provisioned instance, Aurora estimates the equivalent serverless capacity to use as that floor.
- `aurora-postgresql` cluster cache management: a single designated reader (same instance class as the writer, tier set to **0**) can pre-warm its buffer cache to match the writer, specifically to minimize cold-cache impact right after a failover promotes it.

## Endpoints

- **Cluster (writer) endpoint** — always points at the current writer; use for all writes.
- **Reader endpoint** — load-balances across all available readers; use for read scaling. If there are no readers, it falls back to the writer.
- **Instance endpoint** — points at one specific instance; use when you need to pin to a particular reader (e.g. the cache-management reader above), not for general application traffic.

## Pitfalls

- Treating Aurora storage like RDS's per-instance EBS volume — sizing/provisioning it explicitly is unnecessary and the mental model is wrong.
- Assuming a tier-2+ Serverless v2 reader is always warm and ready for failover — only tier 0/1 readers carry that guarantee.
- Pinning application traffic to an instance endpoint by habit (from an RDS mindset) instead of the reader endpoint, and losing automatic load balancing across readers as a result.
- Forgetting that changing promotion tiers doesn't cause a failover, but changing an instance class *does* — different operations, different blast radius.
