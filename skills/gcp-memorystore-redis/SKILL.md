---
name: gcp-memorystore-redis
description: "Google Cloud Memorystore: managed in-VPC Redis-compatible caching/key-value — three variants (standalone Memorystore for Redis with Basic/Standard tiers, horizontally-sharded Memorystore for Redis Cluster, and Memorystore for Valkey, the OSS-engine successor covering both cluster and single-shard modes). Private-IP only: direct peering or private services access for standalone, Private Service Connect for Cluster/Valkey. Use when choosing or operating a managed Redis/Valkey cache on GCP, picking a variant/tier, wiring VPC connectivity from GKE/Cloud Run/GCE, configuring persistence (RDB/AOF), tuning eviction/maxmemory, or estimating capacity-based pricing."
license: MIT
---

# Memorystore (Redis / Redis Cluster / Valkey) — GCP's managed in-memory store

Fully managed, Redis-protocol-compatible in-memory service living inside your VPC.
The family map as the docs present it (as of 2026-07):

| Variant | Shape | Engine | Connectivity |
|---|---|---|---|
| **Memorystore for Redis** (standalone) | 1 vertically-scaled instance, Basic/Standard tiers, max 300 GB | OSS Redis ≤ 7.2 (subset of commands) | VPC peering (direct) or private services access |
| **Memorystore for Redis Cluster** | Horizontally sharded; each shard = 1 primary + 0–5 replicas spread across zones | OSS Redis 7.x (subset) | Private Service Connect (PSC), discovery endpoint |
| **Memorystore for Valkey** | Same sharded architecture; Cluster Mode Enabled (multi-shard) or Disabled (single shard) | Valkey 7.2 / 8.0 / 9.0 | PSC; discovery endpoint (CME) or primary/reader endpoints (CMD) |

Steer for new workloads (2026-07): Valkey is the actively-versioned engine (up to 9.0,
open BSD license) and covers both the clustered and single-node shapes; Redis variants
are pinned at OSS Redis ≤ 7.2. Prefer Valkey unless you need Redis-specific behavior;
prefer the standalone product only when you want its simpler single-endpoint,
GB-sized shape and its peering-based networking.

## The mental model

- **It is a cache/store *inside* your VPC — connectivity is THE gotcha.** Private IP
  only, no public endpoint, no IP allowlists. You reach it from workloads whose
  traffic can route into the VPC (GCE, GKE, Cloud Run/Functions via VPC access,
  App Engine). Standalone uses VPC peering; Cluster/Valkey use PSC endpoints created
  via service connection policies.
- **Tier/variant choice = durability & HA posture, not features.** Basic = one node,
  ephemeral, gone during maintenance. Standard = cross-zone replica + auto failover.
  Cluster/Valkey = shards with 0–5 replicas each and optional AOF/RDB persistence.
- **It is still Redis under the hood**: eviction policies, TTLs, fragmentation, and
  client reconnect behavior are your problem; Google manages the nodes, patching,
  and failover.

## Provisioning & connecting

```bash
# Standalone: capacity in GB, tier picks HA
gcloud redis instances create my-cache --size=5 --region=us-central1 \
  --tier=standard --network=projects/PROJ/global/networks/my-vpc
gcloud redis instances describe my-cache --region=us-central1   # host/port (6379)

# Cluster: shard count x replica count; networking (PSC policy) must exist first
gcloud redis clusters create my-cluster --region=us-central1 \
  --shard-count=3 --replica-count=1 --network=projects/PROJ/global/networks/my-vpc
```

- Standalone connection modes: **direct peering** (default; Memorystore peers a
  Google-managed VPC to yours, needs a free /29–/28 range) or **private services
  access** (recommended: shared PSA range, required for Shared VPC and reaching the
  instance over VPN/Interconnect from on-prem). **You cannot switch the connection
  mode of an existing instance** — recreate, and the IP changes.
- No PUPI (privately-used public IP) ranges; legacy networks unsupported.
- Clients: any Redis client; Cluster/Valkey CME need a cluster-aware client pointed
  at the discovery endpoint. In-transit encryption (TLS) and AUTH are opt-in.

## Per-variant capability matrix

| Capability | Standalone Basic | Standalone Standard | Cluster / Valkey |
|---|---|---|---|
| HA / failover | none (cache loss on failure) | cross-zone replica, auto failover (~seconds; clients must reconnect) | replicas per shard, multi-zone by default |
| Read scaling | no | up to 5 read replicas (read endpoint) | replicas per shard serve reads |
| Write scaling | vertical (resize GB) | vertical (resize GB) | horizontal — add shards (many small nodes beat few big ones) |
| Persistence | RDB snapshots (1h–24h interval; recovery-only, **no manual restore**) | RDB (used only if replica also lost) | RDB **and** AOF |
| Max size | 300 GB, 16 Gbps | 300 GB, 16 Gbps | grows with shard count |

## Gotchas the docs warn about

- **Default eviction is `volatile-lru`** — it only evicts keys *with TTLs*. A cache
  full of TTL-less keys hits `maxmemory` and writes fail with
  `-OOM command not allowed under OOM prevention`. Set TTLs or switch to
  `allkeys-lru`.
- **Leave memory headroom.** `maxmemory-gb` defaults to full instance capacity; the
  docs say system memory usage ratio > 80% = memory pressure. Fragmentation can OOM
  the node even when used-memory looks fine — enable `activedefrag` (Redis ≥ 4.0,
  costs CPU). For exports, drop `maxmemory-gb` to ~50% of capacity first.
- **Maintenance is real downtime.** 1-hour weekly window you should set; Basic tier
  is unavailable ~5 minutes, Standard fails over (~15 s) and **clients must
  reconnect** — build reconnect-with-exponential-backoff into every client. Email
  notice ≥ 7 days ahead (opt-in); deferrable at most twice, 7 days each. Keep memory
  ≤ 50% going into a window.
- **No cross-region anything by default** — an instance/cluster lives in one region;
  DR across regions is on you (client-side dual writes or export/import).
- Command surface is a *subset* of OSS Redis (no `CONFIG` etc.); RDB snapshots are
  for automatic recovery only; snapshots/recovery slow past ~200M keys.

**Pricing shape**: capacity-based. Standalone bills per **GB-hour**, rate set by
capacity band (M1–M5) and tier (Standard > Basic); each read replica adds its GB.
Cluster/Valkey bill per node (node-type × count × hours). Network egress extra;
RDB snapshots on standalone add no charge. Committed-use discounts available.

## vs siblings

- **vs self-managed Redis on GKE/GCE**: Memorystore trades `CONFIG`-level control,
  modules, and newest-engine access for managed patching, HA/failover, and zero node
  ops. Run it yourself only if you need modules, cross-region replication topologies,
  or exotic versions.
- **vs Cloud SQL / AlloyDB / Firestore**: Memorystore is not a system of record —
  Basic tier is explicitly ephemeral and even persistent variants recover, not
  restore. Keep durable truth in a database; Memorystore is the low-latency cache,
  session store, leaderboard, or queue in front of it.
- **vs Bigtable**: Bigtable for huge durable wide-column datasets at ms latency;
  Memorystore for sub-ms in-memory data structures.

## Related

[[gcp-vpc]], [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-bigtable]], [[gcp-datastore]],
[[gcp-gke]], [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-compute-engine]],
[[gcp-cloud-vpn]], [[gcp-interconnect]], [[gcp-cloud-monitoring]], [[gcp-iam]]

Sources: https://docs.cloud.google.com/memorystore/docs/redis,
https://docs.cloud.google.com/memorystore/docs/redis/redis-tiers,
https://docs.cloud.google.com/memorystore/docs/redis/networking,
https://docs.cloud.google.com/memorystore/docs/redis/rdb-snapshots,
https://docs.cloud.google.com/memorystore/docs/redis/memory-management-best-practices,
https://docs.cloud.google.com/memorystore/docs/redis/about-maintenance,
https://docs.cloud.google.com/memorystore/docs/cluster,
https://docs.cloud.google.com/memorystore/docs/cluster/memorystore-for-redis-cluster-overview,
https://docs.cloud.google.com/memorystore/docs/valkey/product-overview,
https://cloud.google.com/memorystore/docs/redis/pricing (fetched 2026-07).
