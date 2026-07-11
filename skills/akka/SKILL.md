---
name: akka
description: "Akka — the meta/overview skill for the whole Akka toolkit (Akka Core 2.10.x + ecosystem) in Scala and Java. Explains the actor model and Akka's philosophy (message-driven, location-transparent, resilient, elastic), maps every module to what it does and when to reach for it, and routes to the per-module skills: akka-actors, akka-cluster, akka-persistence, akka-streams, akka-discovery, akka-serialization, akka-utilities, and the ecosystem (akka-http, akka-grpc, alpakka, akka-projections, akka-persistence-plugins). Also covers version/dependency alignment and the BSL license. Use as the entry point for any Akka question to pick the right module, when designing an Akka-based system end to end, when unsure which Akka library solves a problem, or when a task spans several Akka modules. From any Akka task, defer to the specific module skill for detail."
---

# Akka (overview / meta)

Akka is a toolkit for building **concurrent, distributed, resilient, message-driven** applications on the JVM (Scala and Java). Everything is built on the **actor model**: stateful units that communicate only by asynchronous messages, process one message at a time, and are **location-transparent** (a local and a remote actor are addressed identically). This skill is the map — for any non-trivial Akka work, **read the specific module skill** linked below.

Cross-links: [[akka-actors]], [[akka-cluster]], [[akka-persistence]], [[akka-streams]], [[akka-discovery]], [[akka-serialization]], [[akka-utilities]], [[akka-http]], [[akka-grpc]], [[alpakka]], [[akka-projections]], [[akka-persistence-plugins]]; and [[functional-programming]], [[scala]], [[domain-driven-design]], [[event-storming]].

## Philosophy (the through-line of every module)

- **Message-driven, share-nothing.** Actors don't share mutable state; they pass immutable messages. No locks; one message at a time. Pairs naturally with [[functional-programming]] (immutability, ADTs) and [[scala]].
- **Let it crash.** Model *expected* failures (validation) as messages; supervise *unexpected* failures and recover (restart) rather than defensively coding every error path.
- **Location transparency.** The same actor API works locally or across a cluster — distribution is a deployment concern, not a rewrite.
- **Back-pressure everywhere.** [[akka-streams]] (and HTTP/gRPC/Alpakka on top) never let a fast producer overwhelm a slow consumer.
- **Typed by default.** Akka Typed (`akka.actor.typed`) enforces each actor's message protocol at compile time. Akka Classic is legacy; prefer Typed.

## Module map — what to reach for

**Core (`akka-core`):**
- **[[akka-actors]]** — the foundation: Behaviors, lifecycle, interaction patterns, supervision, routers, stash, FSM, testing. *Start here for anything actor-based.*
- **[[akka-streams]]** — bounded-memory, back-pressured stream processing (Source/Flow/Sink, graphs, operators). *Use for data pipelines, IO, and as the substrate for HTTP/gRPC/Alpakka.*
- **[[akka-cluster]]** — multiple nodes as one elastic, fault-tolerant system: sharding (distribute stateful entities), singleton, distributed data (CRDTs), pub-sub, split-brain resolver, remoting. *Use to scale out and survive partitions.*
- **[[akka-persistence]]** — durable stateful actors via event sourcing or durable state, CQRS, snapshots, replicated event sourcing. *Use for aggregates that must not lose state; pairs with [[domain-driven-design]] / [[event-storming]].*
- **[[akka-serialization]]** — turn messages/events into bytes (Jackson recommended; Java serialization off by default). *Required by cluster & persistence; plan schema evolution.*
- **[[akka-discovery]]** — pluggable service discovery (DNS/config/k8s); powers Cluster Bootstrap. *Use to find services/seed nodes without hardcoding.*
- **[[akka-utilities]]** — EventStream/dead letters, logging, circuit breaker, Futures patterns, extensions. *Cross-cutting helpers.*

**Ecosystem libraries:**
- **[[akka-http]]** — HTTP/1.1+HTTP/2 server & client, Routing DSL, JSON, WebSocket. *Use for REST APIs and HTTP clients.*
- **[[akka-grpc]]** — protobuf-first, code-generated gRPC on HTTP/2 + streams. *Use for typed service-to-service RPC.*
- **[[alpakka]]** — stream connectors (Kafka, S3, JDBC, Cassandra, …). *Use to integrate external systems as streams; Alpakka Kafka for Kafka.*
- **[[akka-projections]]** — build CQRS read-sides from event/durable-state streams with offset tracking; service-to-service event replication. *The read side of [[akka-persistence]].*
- **[[akka-persistence-plugins]]** — the storage backends (R2DBC recommended, JDBC, Cassandra, DynamoDB). *Choose where events/state actually live.*

**Operations & architecture libraries:**
- **[[akka-management]]** — HTTP management, Cluster Bootstrap (form a cluster via discovery instead of static seed-nodes), health checks, k8s rolling-update helpers. *Use to run a cluster on Kubernetes/cloud.*
- **[[akka-diagnostics]]** — config checker + thread-starvation detector. *Catch config mistakes and blocking-on-the-wrong-dispatcher.*
- **[[akka-distributed-cluster]]** — active-active across cloud regions via Replicated Event Sourcing + Projection gRPC (separate clusters, brokerless). *Multi-region HA.*
- **[[akka-edge]]** — push services to the edge / constrained devices (incl. Akka Edge Rust), edge↔cloud replication. *Local-first, low latency.*
- **[[akka-insights]]** — commercial telemetry/observability (Cinnamon) for actors/cluster/sharding/persistence/streams. *Production monitoring.*

## The Akka SDK (a higher-level alternative)

Separately from these Core libraries, the **[[akka-sdk]]** is an opinionated, component-based **Java** framework (the evolution of Kalix) where you write components (**[[akka-sdk-agents]]**, **[[akka-sdk-event-sourced-entities]]**, **[[akka-sdk-key-value-entities]]**, **[[akka-sdk-views]]**, **[[akka-sdk-workflows]]**, **[[akka-sdk-endpoints]]**, **[[akka-sdk-consumers]]**, **[[akka-sdk-timed-actions]]**) and the Akka runtime handles persistence, sharding, replication, and scaling for you — no database or service mesh to manage. **Use the SDK** to build event-driven/agentic services fast with less infrastructure code; **use these Core libraries** when you need low-level control. Start at [[akka-sdk]].

## How the pieces fit (a typical system)

A reactive microservice often looks like: **[[akka-http]]/[[akka-grpc]]** at the edge → commands to **[[akka-cluster]]** sharded **[[akka-persistence]]** event-sourced aggregates (single-writer per entity) → events stored via an **[[akka-persistence-plugins]]** backend (R2DBC) → **[[akka-projections]]** build read models and publish to other services (Projection gRPC) → **[[alpakka]]** integrates Kafka/external systems → all serialized with **[[akka-serialization]]** (Jackson), discovered via **[[akka-discovery]]**, and resilient via the **[[akka-cluster]]** split-brain resolver. Design the aggregates and bounded contexts with [[domain-driven-design]] and [[event-storming]] first.

## Always-apply defaults (across modules)

1. **Prefer Akka Typed** over Classic; model protocols as `sealed`/`interface` ADTs ([[functional-programming]], [[scala]]).
2. **Pin all `akka-*` artifacts to one Akka version**; keep `akka-http`/`akka-grpc`/Alpakka/Projections versions compatible. Akka is licensed under **BSL 1.1** (commercial license required above usage thresholds; artifacts come from Akka's tokenized repo) — flag this for the user when relevant.
3. **In a cluster, always enable the Split Brain Resolver and a real serializer** ([[akka-cluster]], [[akka-serialization]]).
4. **Keep effects at the edges** — pure domain logic in actors/behaviors, IO in streams/repositories at the boundary ([[functional-programming]] pure-core/effectful-shell).
5. **Don't reach for clustering/persistence/streams until the problem needs it** — match the tool to real complexity.

## Related

- Per-module skills (all linked above) for concrete APIs, config, and code.
- [[functional-programming]], [[scala]] — immutability/ADTs and the language the examples use.
- [[domain-driven-design]], [[event-storming]] — model the domain before wiring aggregates, sharding, and projections.
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/index.html (v2.10.x), and the ecosystem library docs under https://doc.akka.io/libraries/.
