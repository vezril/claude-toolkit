---
name: akka-edge
description: Akka Edge (Scala+Java, plus Akka Edge Rust) — extend Akka services to the edge of the cloud for lower latency, higher availability, and local-first operation. Shares its implementation with Akka Distributed Cluster (Projections over gRPC + Replicated Event Sourcing over gRPC) but targets many more, more resource-constrained, more distributed locations — an edge site can be a single autonomous node connected to the cloud, with all gRPC connections initiated FROM the edge. Covers the edge↔cloud topology, edge-as-consumer/producer (Projection gRPC with producer push), active-active edge↔cloud, H2 storage, lightweight deployments (K3s, GraalVM native image, autoscaling), and Akka Edge Rust for constrained devices. Use when pushing endpoints/state to edge locations, building local-first systems with intermittent connectivity, or running Akka on constrained hardware. Builds on akka-distributed-cluster, akka-persistence, and akka-projections.
---

# Akka Edge

Run Akka **at the edge of the cloud** for lower latency, higher availability, and **local-first** operation. Akka Edge **shares features and implementation with [[akka-distributed-cluster]]** (Projections over gRPC, Replicated Event Sourcing over gRPC) but targets **many more, more distributed, more resource-constrained** locations — and the two are designed to be used together. Builds on [[akka-persistence]] and [[akka-projections]].

Cross-links: [[akka]] (meta), [[akka-distributed-cluster]] (the cloud-region counterpart), [[akka-persistence]], [[akka-projections]], [[akka-grpc]].

## How it differs from Distributed Cluster

- **Scale/constraints:** Distributed Cluster connects *few* services across *cloud regions*; Edge connects *many* services, possibly very resource-constrained, where an edge location can be a **single standalone Akka node** (not a cluster).
- **Connection direction:** **all gRPC connections are established from the edge** (regardless of whether the edge is producer or consumer), because the cloud usually can't reach into edge networks (NAT/firewall) and shouldn't have to track every edge node.
- **Topology:** edge services connect to cloud services in a **star** (edge↔edge is possible, an app concern). Edge services are **fully autonomous** — they keep working during disconnection and **catch up on pending events when reconnected**. Devices reach the nearest edge via HTTP/MQTT/etc.

## The same two building blocks

1. **Projections over gRPC** in both directions:
   - **Edge as consumer** — edge connects to a cloud producer, processing from its stored offset; the offset store on the edge can be an **embeddable H2** database (file mode). Optimizations: start from snapshots, start from a custom offset, and the "many consumers" firehose.
   - **Edge as producer** — edge connects to a cloud consumer and **pushes** events (**Akka Projection gRPC with producer push**); the cloud writes them to its journal, acks, and the edge advances its offset.
2. **Replicated Event Sourcing over gRPC** — active-active entities across cloud regions and edge **Points-of-Presence**; connection established from the edge; each replica has its own DB (e.g. **Postgres in cloud, H2 at the edge**).

Replication mechanics, slices, dynamic filters, and exactly-once-via-offset-dedup are identical to [[akka-distributed-cluster]].

## Lightweight deployments & Akka Edge Rust

- **Constrained edge:** lightweight Kubernetes (**K3s**, MicroK8s); cloud-optimized JVMs (OpenJ9); **GraalVM Native Image** (AOT to a native executable — smaller, faster start, lower footprint; Akka ships reachability metadata and auto-registers messages via Akka Serialization Jackson; use the tracing agent for unsupported libs). Edge apps can't scale to zero but can scale to **near zero**; combine k8s HPA (on custom metrics like active-entity count) + VPA, keeping ≥2 replicas + a PodDisruptionBudget.
- **Akka Edge Rust** — a **subset of Akka reimplemented in Rust** to run on **resource-constrained devices** (demonstrated on MIPS32, 500MHz, 128MiB RAM). Provides event-sourced entities (with compaction, a file-log adapter, entity manager), projections (offset store + gRPC source provider/handler) to consume/produce events to the cloud, HTTP event production incl. **SSE**, and **UDP** ingestion; connects to a JVM/cloud counterpart over **gRPC**, remembering its offset across restarts. Event-driven browser UI via **WebAssembly** (Yew). Needs Rust ≥1.70, `wasm32-unknown-unknown` target, Trunk, protobuf ≥v23.

## Always-apply defaults

1. **Initiate all edge↔cloud gRPC from the edge**; treat edge nodes as autonomous (operate offline, reconcile on reconnect).
2. **Pick the right replication direction:** edge-consumes (cloud→edge data) via Projection gRPC; edge-produces (edge→cloud telemetry) via Projection gRPC **with producer push**; multi-location writes via Replicated Event Sourcing gRPC.
3. **Use H2 (file mode) for edge storage** where a full DB is impractical; expect each replica to have its own (possibly different) database.
4. **Design for intermittent connectivity** — local-first behavior, store-and-forward, automatic catch-up; use dynamic filters so only relevant data flows to each edge.
5. **For very constrained devices, use Akka Edge Rust**; for cloud-region meshes use [[akka-distributed-cluster]] (combine the two).

## Anti-patterns (flag in review)

- Expecting the cloud to dial into edge nodes; edge designs that fail when disconnected (not autonomous); replicating everything to every edge instead of filtering.
- Running a heavy JVM stack on hardware that calls for Akka Edge Rust / native image; assuming strong consistency edge↔cloud.

## Related

- [[akka-distributed-cluster]] (shared primitives, cloud-region side) · [[akka-persistence]] (Replicated Event Sourcing) · [[akka-projections]] (Projection gRPC + producer push) · [[akka-grpc]] · [[akka]] (meta).
- Source: https://doc.akka.io/libraries/akka-edge/current/
