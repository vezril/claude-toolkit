---
name: akka-distributed-cluster
description: Akka Distributed Cluster (Scala+Java) — connect Akka services across geographically distributed locations (cloud regions, providers) for active-active, lower latency, and higher availability. NOT one stretched cluster — each region is a separate autonomous Akka Cluster linked by reliable asynchronous event replication over gRPC, built on Projections over gRPC (brokerless service-to-service eventing) and Replicated Event Sourcing over gRPC (active-active entities). Covers the architecture and why not a single stretched cluster, the two building blocks, dynamic filters, the exactly-once/eventual-consistency model, and when to use it. Use when designing multi-region/active-active Akka systems, brokerless cross-service or cross-region eventing, hot standby, or geo-distributed microservices. Builds on akka-persistence (Replicated Event Sourcing) and akka-projections (gRPC).
---

# Akka Distributed Cluster

Features (shipped within Akka Projection) for building stateful systems across **geographically distributed locations** — multiple cloud regions or providers — for higher availability and lower latency, plus **brokerless** asynchronous service-to-service communication. Builds on [[akka-persistence]] (Replicated Event Sourcing) and [[akka-projections]] (Projection gRPC).

Cross-links: [[akka]] (meta), [[akka-persistence]], [[akka-projections]], [[akka-edge]] (the edge counterpart), [[akka-grpc]]. Group `com.lightbend.akka`, BSL 1.1.

## The key architectural decision: many clusters, not one

It is **not** one Akka Cluster stretched across regions. Each location is a **separate, fully autonomous Akka Cluster** (typically its own Kubernetes cluster), linked by **reliable event replication over gRPC**. A single stretched cluster across regions is impractical: cross-region peer-to-peer security, address translation between separate k8s clusters, reliable cross-cluster bootstrap, and failure detection over mixed-latency links all break down. The gRPC replication transport instead gives **TLS/mTLS**, ingress/load-balancer-friendly networking, **exactly-once or at-least-once** processing, and **brokerless** async communication (no Kafka).

## The two building blocks

1. **Projections over gRPC** — brokerless **service-to-service eventing** (one-way producer→consumer). The producer side streams from its **event journal**; the consumer side uses [[akka-projections]] with offset tracking (offsets drive dedup → **exactly-once**). Multiple consumers can attach, each at its own pace, each from its last offset. Producer and consumer are usually different microservices / Bounded Contexts ([[domain-driven-design]]); each keeps its **own database** — no direct cross-service DB access. Replaces a message broker without the broker.
2. **Replicated Event Sourcing over gRPC** — **active-active entities** updatable in more than one location (hot standby, serve-from-nearest, multi-location writes). Replicas run in separate clusters connected by gRPC event replication, belong to the **same logical service / Bounded Context**, and each has its **own DB** (products may differ). See [[akka-persistence]] Replicated Event Sourcing for the conflict-resolution model (CRDTs / LWW).

## How replication works

The **event journal is the source of truth** and the publication source. Events stream directly from journal to consumers with **full backpressure** based on demand; sequence numbers + consumer offsets give at-least-once + automatic dedup → exactly-once. Entities are assigned to **slices** for partitioning; different consumers take different slice ranges, **scalable at runtime**. Once a consumer catches up it receives **live events immediately** (very low latency), with the journal as the reliable fallback. **Dynamic filters** (by event tag or entity id, on producer and/or consumer side, **changeable at runtime**) select which entities replicate where; newly-included entities have their preceding events **automatically replayed**.

## Always-apply defaults

1. **Keep each region a separate autonomous cluster**; never try to stretch one Akka Cluster across regions. Connect them via Projection gRPC / Replicated Event Sourcing gRPC.
2. **Choose the building block by need:** one-way cross-service/region eventing → Projections over gRPC; multi-location writes / hot standby → Replicated Event Sourcing over gRPC.
3. **Each service/replica owns its database**; integrate only through replicated events, never direct cross-DB access.
4. **Expect eventual consistency** (async replication); for active-active, design state to merge concurrent updates ([[akka-persistence]] RES — CRDT/LWW).
5. **Use dynamic filters** to replicate only what each region needs (cost/regulatory), tuning at runtime.

## When to use it (vs alternatives)

Use it for a **small number of services across a few cloud regions** needing active-active/HA or brokerless eventing. For **many, more constrained, more distributed** locations (single-node edge sites, intermittent connectivity), use [[akka-edge]] — the two share the same primitives and are designed to be combined (cloud-region mesh + edge fan-out). If you just need one resilient cluster in one region, plain [[akka-cluster]] suffices.

## Anti-patterns (flag in review)

- Trying to run one Akka Cluster spanning regions; sharing a database across services/replicas; assuming synchronous/strong consistency across regions.
- Reaching for it when a single-region [[akka-cluster]] would do; replicating everything everywhere instead of using filters.

## Related

- [[akka-persistence]] (Replicated Event Sourcing, the active-active engine) · [[akka-projections]] (Projection gRPC) · [[akka-edge]] (edge counterpart) · [[akka-grpc]] (transport) · [[akka]] (meta) · [[domain-driven-design]] (bounded contexts).
- Source: https://doc.akka.io/libraries/akka-distributed-cluster/current/
