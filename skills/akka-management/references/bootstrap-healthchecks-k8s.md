# Akka Management: discovery, health checks, cluster HTTP, k8s rolling updates

Scala+Java. Source: doc.akka.io/libraries/akka-management/current/{bootstrap/index,bootstrap/kubernetes-api,healthchecks,cluster-http-management,rolling-updates}.html

## Discovery methods for Bootstrap

`akka.management.cluster.bootstrap.contact-point-discovery.discovery-method` (falls back to `akka.discovery.method`). Shipped: **kubernetes-api**, **aws-api**, **azure-api**, **consul**; DNS (`akka-dns`) is core. Kubernetes and DNS are the well-tested ones.

**Kubernetes API** (`discovery-method = kubernetes-api`): queries the API server for pods matching a label selector.
```hocon
akka.discovery.kubernetes-api.pod-label-selector = "app=%s"   # default
```
- Namespace auto-detected from the service-account file (or `KUBERNETES_NAMESPACE`). Pods set `AKKA_CLUSTER_BOOTSTRAP_SERVICE_NAME` from label `app`.
- Needs RBAC: a `Role` with `get/watch/list` on `pods` + a `RoleBinding` to the pod's service account.
- Don't use `kubernetes-api` as the default `akka.discovery.method` (use `akka-dns` for consuming other services).
- Probes point at the management port (8558, commonly named `management`): liveness `/alive`, readiness `/ready`.

## Health checks

```hocon
akka.management.health-checks {
  readiness-checks {
    cluster-membership = "akka.management.cluster.scaladsl.ClusterMembershipCheck"  # default; "" to disable
    my-readiness = "com.example.MyReadinessCheck"
  }
  liveness-checks { my-liveness = "com.example.MyLivenessCheck" }
  readiness-path = "ready"   # default; liveness-path = "alive"
}
```
A check extends `() => Future[Boolean]` (Scala) / `Supplier<CompletionStage<Boolean>>` (Java); constructor is no-arg or takes a single `ActorSystem`. Endpoint returns 200 only if all checks of that kind pass, 500 otherwise. The cluster-membership readiness check is healthy when the node is `Up`/`WeaklyUp` (configurable via `akka.management.cluster.health-checks.ready-states`). Disable all health routes with `akka.management.http.routes.health-checks = ""`.

## Cluster HTTP Management (`akka-management-cluster-http`)

Auto-loads its routes on `AkkaManagement(system).start()`. GETs exposed by default; POST/PUT/DELETE only when `akka.management.http.route-providers-read-only = false`.

| Path | Method | Action |
|---|---|---|
| `/cluster/members/` | GET | Cluster status (members, status, roles, leader, oldest, unreachable) |
| `/cluster/members/` | POST `address` | Join |
| `/cluster/members/{address}` | DELETE / PUT `operation=Down\|Leave` | Leave / Down |
| `/cluster/domain-events` | GET (SSE) | Stream of cluster events, optional `?type=` filter |
| `/cluster/shards/{name}` | GET | Shard region info |
| `/cluster/` | PUT `operation=Prepare-for-full-shutdown` | Prepare full shutdown |

Host these in your own Akka HTTP server via `ClusterHttpManagementRoutes(Cluster(system))` / `.readOnly(...)`. Disable just these with `akka.management.http.routes.cluster-management = ""`.

## Graceful shutdown & rolling updates

- **Send SIGTERM** (not SIGKILL; forward the signal if the JVM is wrapped). Coordinated Shutdown calls `Cluster.leave` on self → Exiting → removed, so shards shut down gracefully and singletons migrate quickly (node is known shut down, not crashed).
- **Start rolling redeploys from the newest node** — singletons run on the **oldest** node, so removing oldest-last means singletons move only once (matters even with just Cluster Sharding, which uses an internal singleton). Wait for each node to finish joining (a stable discovery period) before churning more.
- **`akka-rolling-update-kubernetes`** extensions:
  - **Pod Deletion Cost** (`akka.extensions += "akka.rollingupdate.kubernetes.PodDeletionCost"`) — annotates older pods with `controller.kubernetes.io/pod-deletion-cost` so K8s ≥1.22 removes them last (avoids churning the oldest/singleton node). Needs RBAC `patch` on `pods`; a CRD-based variant exists for security-averse setups.
  - **AppVersionRevision** (`akka.extensions += "akka.rollingupdate.kubernetes.AppVersionRevision"`) — reads the Deployment annotation `deployment.kubernetes.io/revision` so `akka.cluster.app-version` stays correct even on `kubectl rollout undo`. Needs RBAC `get/list` on `pods` and `replicasets`.
- Recommended cluster robustness with Bootstrap: `akka.cluster.shutdown-after-unsuccessful-join-seed-nodes = 30s`, `akka.coordinated-shutdown.exit-jvm = on`, and enable the SBR.

Other Management modules (in nav): JMX management, Dynamic Log Levels (`loglevels`), Kubernetes Lease, Native Image support.
