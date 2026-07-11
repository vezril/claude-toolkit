---
name: akka-cluster
description: "Akka Cluster (Akka Core 2.10.x, Typed API) in Scala and Java — building elastic, resilient, distributed systems from multiple ActorSystems. Covers cluster membership (gossip, phi-accrual failure detector, leader, member lifecycle), forming a cluster (seed nodes, Cluster Bootstrap, roles), and the higher-level tools: Cluster Sharding (distributing stateful entities), Cluster Singleton, Distributed Data (CRDTs), Distributed Pub-Sub, Sharded Daemon Process, Reliable Delivery, Artery remoting + TLS, the Split Brain Resolver, and Coordination/Lease. Use whenever designing or operating an Akka cluster, distributing actors/entities across nodes, sharding aggregates, needing a cluster-wide singleton, replicating state with CRDTs, handling network partitions/split brain, configuring remoting/seed-nodes/downing, or doing cluster-aware pub-sub or routing — even if \"cluster\" isn't named but multi-node Akka, sharding, entities, or partition-tolerance are involved. Builds on the akka-actors skill."
---

# Akka Cluster

A decentralized, peer-to-peer membership service that lets multiple `ActorSystem`s (nodes) form a single elastic, fault-tolerant cluster — no single point of failure, no master. Built on Artery remoting and gossip; the substrate for sharding, singletons, distributed data, and [[akka-persistence]] at scale. Builds on [[akka-actors]].

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-actors]], [[akka-persistence]], [[akka-serialization]], [[akka-discovery]].

Dependencies (per feature): `akka-cluster-typed`, `akka-cluster-sharding-typed`, `akka-coordination`; SBR is in `akka-cluster`.

## How a cluster works (concepts)

- **Gossip + vector clocks.** Cluster state is a single versioned value gossiped randomly (biased to nodes that haven't seen the latest), reconciled with vector clocks. **Convergence** = every node has seen the current version; it **cannot occur while any node is `unreachable`**, which blocks leader actions (but not the running app).
- **Failure detector.** A **phi-accrual** detector; each node is heartbeat-monitored by up to 5 others on a hashed ring. One node marking another unreachable propagates to all; reachability is restored only when *all* monitors agree.
- **Leader.** Deterministically recognized after convergence (no election); performs membership transitions (joining→up, exiting→removed).
- **Member lifecycle:** `joining` → (`weakly up`) → `up` → `leaving` → `exiting` → `removed`, plus the orthogonal **unreachable** flag and `down`. A node id is `host:port:uid`; the **same ActorSystem can never rejoin** once removed (must restart with a new uid).

## Forming a cluster

Minimum config — **all nodes must share the ActorSystem name**, enable a serializer, and set a downing provider:

```hocon
akka {
  actor.provider = "cluster"
  remote.artery.canonical { hostname = "127.0.0.1", port = 2551 }
  cluster {
    seed-nodes = ["akka://MySystem@127.0.0.1:2551", "akka://MySystem@127.0.0.1:2552"]
    downing-provider-class = "akka.cluster.sbr.SplitBrainResolverProvider"   # enable SBR!
  }
}
```

Three ways to join: **Cluster Bootstrap** (automatic discovery via [[akka-discovery]] — preferred in k8s/cloud), **configured seed-nodes** (the first in the list must be up to form a new cluster), or programmatic `JoinSeedNodes`. Use **roles** (`akka.cluster.roles`) to run different actors on different nodes: `if (Cluster(ctx.system).selfMember.hasRole("backend")) ctx.spawn(...)`. Gate startup with `akka.cluster.min-nr-of-members`.

```scala
val cluster = Cluster(system)               // Java: Cluster.get(system)
cluster.manager ! Join(cluster.selfMember.address)
cluster.subscriptions ! Subscribe(subscriber, classOf[MemberEvent])
```

Leaving should be **graceful** (Coordinated Shutdown, triggered on `ActorSystem` termination/SIGTERM — it hands off singletons & shards). Abrupt termination → unreachable → must be **downed** (let SBR do it).

## The higher-level tools — pick the right one

Detail lives in three references:

- **`references/sharding.md`** — **Cluster Sharding** (distribute many stateful entities across nodes; the standard home for [[akka-persistence]] aggregates), `EntityTypeKey`/`init`/`EntityRef`, passivation, remember-entities, shard allocation & `number-of-shards`, and **Sharded Daemon Process** (N balanced workers). *Use when you have more stateful actors than fit on one node, or need single-active-entity guarantees.*
- **`references/singleton-ddata-pubsub.md`** — **Cluster Singleton** (exactly one instance cluster-wide), **Distributed Data** (eventually-consistent CRDTs with tunable read/write consistency), and **Distributed Pub-Sub** (`Topic`). *Singleton: one coordinator; DData: shared replicated state; Pub-Sub: broadcast.*
- **`references/remoting-sbr-coordination-reliable.md`** — **Artery remoting** + TLS, the **Split Brain Resolver** (required! strategies: keep-majority, static-quorum, keep-oldest, lease-majority, down-all), **Coordination/Lease**, and **Reliable Delivery** (at-least-once + flow control). *Read for partition handling, security, and guaranteed delivery.*

## Always-apply defaults

1. **Enable the Split Brain Resolver** (`downing-provider-class = akka.cluster.sbr.SplitBrainResolverProvider`) and auto-restart downed nodes. A wrong/missing downing strategy yields duplicate singletons / duplicate sharded entities writing the same event stream — corruption. Set `akka.coordinated-shutdown.exit-jvm = on`.
2. **Enable serialization** (Jackson — see [[akka-serialization]]); all cross-node messages, entity commands, and `EntityRef`s must be serializable.
3. **Pin `number-of-shards`** (identical on all nodes; ~10× max node count) and never change it without a full cluster stop.
4. **Prefer graceful leave** (Coordinated Shutdown) over killing nodes; size SBR `stable-after`/`down-removal-margin` to your cluster.
5. **Use sharding for stateful entities, singleton sparingly** (it's a bottleneck + SPOF), and reference other aggregates by **id**, not direct ref.

## Anti-patterns (flag in review)

- No SBR / naive auto-down → split brain → duplicate singletons & sharded entities (catastrophic with persistence).
- Mismatched `number-of-shards` or ActorSystem name across nodes; relying on a node rejoining with the same uid.
- Treating Cluster Singleton as a workhorse; large aggregates loaded as one shard entity; holding direct `ActorRef`s to entities on other nodes (use `EntityRef`).
- Assuming Distributed Data is strongly consistent by default, or using it for big data (≤ ~100k entries, all in memory).
- Plain remoting/Distributed Data over untrusted networks without TLS.

## Related

- [[akka]] — meta skill and module map.
- [[akka-actors]] — the actor foundation (cluster distributes actors).
- [[akka-persistence]] — event-sourced/durable entities live inside Cluster Sharding (single-writer).
- [[akka-serialization]] — required for any cross-node message.
- [[akka-discovery]] — powers Cluster Bootstrap (automatic seed discovery).
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/typed/index-cluster.html (v2.10.x).
