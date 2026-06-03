---
name: akka-management
description: Akka Management (Scala+Java) — the suite of operational tools for running Akka Clusters, exposing a central HTTP management endpoint plus extensions for Cluster Bootstrap (automatic cluster formation via Akka Discovery, replacing static seed-nodes), health checks (Kubernetes readiness/liveness probes), Cluster HTTP Management (inspect/manage membership over REST), and Kubernetes rolling-update helpers (Pod Deletion Cost, AppVersionRevision). Use when deploying an Akka Cluster to Kubernetes or the cloud, forming a cluster automatically instead of hardcoding seed nodes, wiring readiness/liveness probes, doing graceful rolling updates, or inspecting cluster membership over HTTP — even if "management" isn't named but cluster bootstrap, health checks, or k8s cluster ops are involved. Complements akka-cluster and akka-discovery.
---

# Akka Management

A suite of **operational tools for Akka Clusters**. The core `akka-management` module provides a single central **HTTP management endpoint** to which extensions register routes; you add only the extensions you need. The most important are **Cluster Bootstrap** (form a cluster automatically via [[akka-discovery]]) and **health checks** (Kubernetes probes). This is what makes [[akka-cluster]] practical to run on Kubernetes/cloud.

Cross-links: [[akka]] (meta), [[akka-cluster]], [[akka-discovery]]. Dependencies under `com.lightbend.akka.management`; pin all `akka-*` to one Akka version.

## Starting it

Management does **not** auto-start (so you can prepare before exposing routes):

```scala
import akka.management.scaladsl.AkkaManagement
AkkaManagement(system).start()       // Future[Done]; HTTP endpoint on akka.management.http.port (default 8558)
```
```java
AkkaManagement.get(system).start();
```
```hocon
akka.management.http {
  hostname = "127.0.0.1"            # bind-hostname/bind-port for NAT/Docker
  port = 8558
  route-providers-read-only = true # set false to expose mutating cluster endpoints
}
```
No security by default — don't expose management publicly; add HTTPS/basic-auth via `start(_.withHttpsConnectionContext(...).withAuth(...))`.

## Cluster Bootstrap — automatic cluster formation

Replaces static `akka.cluster.seed-nodes` in dynamic environments (Kubernetes, AWS) by using [[akka-discovery]] to find peers. Start **both** Akka Management and Bootstrap on every node:

```scala
AkkaManagement(system).start()
ClusterBootstrap(system).start()
```
```hocon
akka.management.cluster.bootstrap.contact-point-discovery {
  service-name     = "my-service"
  discovery-method = kubernetes-api          # or akka-dns, aws-api, consul; falls back to akka.discovery.method
  required-contact-point-nr = 3              # ideally the exact initial node count
}
```
**How it works:** each node exposes `/bootstrap/seed-nodes`; nodes query discovery until they find the required contact points, then probe them — if a cluster exists they join it, otherwise the node with the lowest address self-joins and forms a new cluster, and the rest join it. Don't set `seed-nodes` (it takes precedence and disables bootstrap). For deploy safety, flip `new-cluster-enabled = off` after the first formation, and add `akka.cluster.shutdown-after-unsuccessful-join-seed-nodes = 30s` + `akka.coordinated-shutdown.exit-jvm = on` so a pod that can't join is restarted. Enable the [[akka-cluster]] **Split Brain Resolver** for hard failures.

## Health checks (Kubernetes probes)

Two kinds, mirroring k8s probes: **readiness** (`/ready`, should receive traffic — e.g. joined the cluster) and **liveness** (`/alive`, should keep running). Returns 200 only when all checks of that kind pass. A cluster-membership readiness check ships by default; add custom checks (a `() => Future[Boolean]` / `Supplier<CompletionStage<Boolean>>`) under `akka.management.health-checks.{readiness-checks,liveness-checks}`.

## Cluster HTTP Management & rolling updates

Detail in **`references/bootstrap-healthchecks-k8s.md`** — the discovery methods (kubernetes-api RBAC, DNS, AWS), the full health-check config and custom checks, **Cluster HTTP Management** REST endpoints (`/cluster/members`, domain-events SSE, shard info; GETs by default, mutations only when `route-providers-read-only = false`), graceful shutdown via SIGTERM + Coordinated Shutdown, and the Kubernetes rolling-update helpers — **start rolling redeploys from the newest node** (singletons run on the oldest), plus `akka-rolling-update-kubernetes` extensions **Pod Deletion Cost** (keep the oldest pod alive longest) and **AppVersionRevision** (correct app-version on rollback).

## Always-apply defaults

1. **Use Cluster Bootstrap, not static seed-nodes**, in Kubernetes/cloud; start both Management and Bootstrap on every node; don't set `seed-nodes`.
2. **Wire `/ready` and `/alive` to k8s probes** (management port, commonly named `management`/8558); keep the default cluster-membership readiness check.
3. **Don't expose the management endpoint publicly**; keep `route-providers-read-only = true` unless you specifically need mutating endpoints, and secure with HTTPS/auth if exposed.
4. **Shut down with SIGTERM** (not SIGKILL) so Coordinated Shutdown leaves the cluster gracefully (fast singleton/shard handover); **start rolling updates from the newest node**.
5. **Pair with [[akka-cluster]] SBR** and set `required-contact-point-nr` to the initial node count for safe formation.

## Anti-patterns (flag in review)

- Mixing `seed-nodes` with Bootstrap (Bootstrap silently won't run); exposing management to the internet; leaving mutating endpoints on.
- SIGKILL instead of SIGTERM (crash-style exit blocks graceful handover); rolling updates from the oldest node (singletons thrash); no SBR.

## Related

- [[akka-cluster]] (the cluster being formed/operated) · [[akka-discovery]] (powers Bootstrap) · [[akka]] (meta).
- Source: https://doc.akka.io/libraries/akka-management/current/
