---
name: gcp-gke
description: "Google Kubernetes Engine (GKE) — GCP's managed Kubernetes: Google runs the control plane, you choose between Autopilot mode (Google manages nodes, you're billed per-pod resource requests — the recommended default) and Standard mode (you own node pools and pay for the Compute Engine VMs). Covers the Autopilot vs Standard fork and Autopilot's security constraints (no privileged containers, no host namespaces, no node SSH, dropped NET_RAW/NET_ADMIN), cluster architecture (zonal vs regional control plane), node pools (per-pool machine type/image/taints/spot, independent upgrades), release channels (Rapid/Regular/Stable/Extended) driving auto-upgrades with maintenance windows and exclusions, surge vs blue-green node upgrades and the 1-hour PDB respect limit, Workload Identity Federation as THE way pods reach Google Cloud APIs (PROJECT_ID.svc.id.goog pool, direct principal grants vs SA impersonation), VPC-native networking (node/pod/service CIDRs, /24 per node, IP exhaustion), Gateway API as Ingress's successor, storage CSI drivers (PD, Hyperdisk, Filestore, GCS FUSE), quotas and the pricing shape ($0.10/cluster/hour fee, free tier credit, Autopilot pod-resources vs Standard nodes). Use when creating or configuring GKE clusters or node pools, choosing Autopilot vs Standard or GKE vs Cloud Run, writing gcloud container commands, wiring Workload Identity, planning CIDR ranges, tuning upgrade strategy/release channels, debugging Autopilot admission rejections, or estimating GKE costs. Assumes Kubernetes literacy — this is about GKE-the-managed-service, not k8s itself."
license: MIT
---

# GCP Google Kubernetes Engine (GKE)

Google's managed Kubernetes. Google runs and scales the control plane (API server, scheduler, controllers, etcd — or Spanner-backed state) behind a single endpoint; your workloads run on Compute Engine VMs. The big fork is who manages those VMs: **Autopilot** (Google does; you pay per pod) or **Standard** (you do; you pay per node). Everything below assumes you already know Kubernetes — this is the GKE-specific layer.

## The mental model

**The control plane is Google's problem.** You never see the control-plane VMs, never SSH to them, never patch them. Zonal clusters have one control-plane replica (API unavailable during its upgrade); regional clusters replicate it across three zones and upgrade one at a time — production wants regional. GKE auto-upgrades control planes regardless of settings (honoring maintenance exclusions when possible); node auto-upgrade is on by default.

**Autopilot = pods are the API.** You submit workloads; GKE provisions, scales, repairs, and upgrades the nodes underneath — you can't delete its node pools or SSH in. Billing follows your pod **resource requests** (vCPU/memory/ephemeral-storage rates) for general-purpose pods, or falls back to node-based billing when you pin specific hardware/accelerators via compute classes. Missing requests get preconfigured defaults. Autopilot is the docs' recommended default mode, and clusters are always regional.

**Standard = you own node pools.** A node pool is a set of identical VMs (machine type, image, labels, taints, spot-ness); you can't configure a single node, only a pool. Default pool: 3 nodes/zone, `e2-medium`, `cos_containerd`. Multi-zonal clusters replicate every pool per zone — quota multiplies accordingly. Pools upgrade and autoscale independently and may run different versions (nodes may lag the control plane by at most two minor versions). Pods land on the right pool via `nodeSelector` on `cloud.google.com/gke-nodepool` (every node carries that label) or via your own labels/taints.

**Compute classes shape Autopilot hardware.** By default pods run on the general-purpose container-optimized compute platform (per-pod billing). Selecting a compute class — built-ins like Balanced or Scale-Out, `autopilot-arm`, `autopilot-spot`, or a custom ComputeClass that pins machine families/accelerators — is how you request specific hardware without managing node pools; hardware-specific selections flip that workload to node-based billing.

**Release channels drive upgrades.** Enrolling a cluster in a channel determines when auto-upgrades of control plane and nodes happen; critical security patches ship to all channels without delay. You steer timing, not whether: **maintenance windows** say when, **maintenance exclusions** block upgrades for up to 90 days ("no upgrades") or indefinitely ("no minor upgrades"). Running with no channel is deprecated (removal June 14, 2027).

- **Rapid** — new minors 1–2 weeks after upstream Kubernetes GA; auto-upgrades ~1–2 months later. Pre-prod canaries.
- **Regular** (default) — features ~2 months behind Rapid; the stability/freshness balance.
- **Stable** — 3–4 months behind Regular; maturity first.
- **Extended** — park on one minor for up to 24 months (10-month extended support tail with security patches) when you need to stop the treadmill.

**Everything is VPC-native.** All new clusters use alias IP ranges: node IPs from the subnet's primary range, pod IPs from a secondary range (a `/24` — 256 IPs — per node for the default 110 max pods/node), service IPs from a third range (newer versions default to the Google-managed `34.118.224.0/20`). Pod IPs are natively routable in the VPC. Plan the pod CIDR before you create the cluster — undersizing it caps your node count, and clusters sharing a secondary range can starve each other.

## Cluster and node-pool shapes

```bash
# Autopilot (recommended default) — regional, nodes fully managed
gcloud container clusters create-auto my-cluster \
    --location=us-central1 --release-channel=regular

# Standard zonal — you pick machine shape and count
gcloud container clusters create my-cluster \
    --location=us-central1-a --num-nodes=3 \
    --machine-type=e2-standard-4 --release-channel=regular

# Add a specialized node pool (taints/labels/spot per pool)
gcloud container node-pools create batch-pool \
    --cluster=my-cluster --location=us-central1-a \
    --machine-type=n2-highmem-8 --spot

# Kubeconfig credentials
gcloud container clusters get-credentials my-cluster --location=us-central1

# Enable Workload Identity Federation (Standard; Autopilot has it always on)
gcloud container clusters update my-cluster --location=us-central1-a \
    --workload-pool=PROJECT_ID.svc.id.goog
gcloud container node-pools update default-pool --cluster=my-cluster \
    --location=us-central1-a --workload-metadata=GKE_METADATA
```

## Autoscaling in Standard (Autopilot does all of this for you)

Two distinct machines, both driven by pod resource *requests*, not utilization:

- **Cluster autoscaler** resizes *existing* pools when pods are unschedulable or nodes sit underutilized. Per-zone bounds via `--enable-autoscaling --min-nodes/--max-nodes`, or cluster-wide bounds via `--total-min-nodes/--total-max-nodes` (1.24+).
- **Node auto-provisioning (NAP)** (`--enable-autoprovisioning`) goes further: it *creates and deletes whole node pools*, picking machine types to fit pending pods — Standard's halfway house toward Autopilot.
- **Autoscaling profiles:** `balanced` (default — keeps headroom for fast scheduling) vs `optimize-utilization` (aggressive scale-down, cost over readiness).

Under-requested pods defeat all of it: the autoscalers believe your requests, so requests that lie produce nodes that thrash. Rightsize requests first, tune autoscaling second.

## Workload Identity Federation — how pods reach GCP APIs

The one blessed path; it replaces exported service-account keys and shared node-SA scopes. A GKE metadata-server DaemonSet intercepts calls to `metadata.google.internal`, swaps the pod's Kubernetes ServiceAccount JWT for a short-lived federated token via STS. Enabling creates the fixed pool `PROJECT_ID.svc.id.goog` (never deleted, even if all clusters go).

Preferred: grant IAM roles **directly to the principal** — no Google service account at all:

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --role=roles/storage.objectViewer \
    --member="principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/NAMESPACE/sa/KSA_NAME"
```

Fallback (for the few services that reject federated tokens): impersonate an IAM service account — bind `roles/iam.workloadIdentityUser` to member `serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/KSA_NAME]` **and** annotate the KSA with `iam.gke.io/gcp-service-account=GSA_EMAIL`. Both halves are required. `principalSet://` grants can target a whole namespace or cluster.

Caveats: the GKE metadata server caches access tokens (they live one hour) and only serves a subset of Compute Engine metadata endpoints — code probing node-level attributes gets `404`s, which is by design.

## L7: Gateway API over Ingress

For new HTTP(S) routing, use the **Gateway API** — Google's investment path, with Ingress resources "directly convertible" to Gateway + HTTPRoute. GKE ships Google-managed GatewayClasses that program real load balancers out of band from traffic: external (`gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, legacy `gke-l7-gxlb`), internal (`gke-l7-rilb`), multi-cluster variants of each, and service-mesh classes (`gke-td`, `asm-l7-gxlb`). The single-cluster controller is enabled by default; multi-cluster gateways require Fleet registration. Cross-namespace routing needs explicit `ReferenceGrant`s.

## Upgrades, PDBs, and maintenance

- Node upgrade strategies: **surge** (default; rolling with temporary extra nodes, `maxSurge`) and **blue-green** (parallel node environments, easy rollback, more quota; configurable soak time).
- During upgrades and node drains GKE respects PodDisruptionBudgets and graceful termination **for up to one hour**, then proceeds anyway. A zero-disruption PDB doesn't block an upgrade forever — it delays it an hour per node and slows everything down. Autopilot can protect fault-intolerant pods from eviction for up to 7 days.
- Upgrades pause when a maintenance window closes mid-flight and resume in the next window; manual upgrades ignore windows.

## Autopilot constraints (what gets rejected)

- No privileged containers (partner-allowlisted workloads excepted), no host network/PID namespaces, no hostPort binding, no SSH to nodes.
- `hostPath`: read-only `/var/log/*` only; no writes.
- `CAP_NET_RAW` and `CAP_NET_ADMIN` dropped by default (ping breaks unless you add NET_RAW back in the securityContext); only a baseline capability set is allowed.
- No workloads in GKE-managed namespaces (`kube-system` etc.); mutating webhooks are rewritten to exclude managed namespaces and can't target nodes/PVs/CSRs/TokenReviews; `spec.externalIPs` Services blocked (CVE-2020-8554).
- DaemonSets work, but anything needing node-level privilege is out — that class of agent is the classic reason teams stay on Standard.
- For workloads that need *stronger* isolation instead, GKE Sandbox (gVisor) adds a second kernel boundary around high-risk containers.

## Gotchas, quotas, pricing shape

- **IP exhaustion is a create-time decision.** The pod secondary range is nearly immutable; a too-small range silently caps cluster growth. Do the math: nodes × /24. Mitigations exist (additional pod CIDRs, expanding primary ranges) but planning beats patching. Newer versions manage secondary ranges for you (Autopilot 1.27+, Standard 1.29+) unless you take control.
- **Zonal control plane = API downtime during upgrades.** You can't `kubectl apply` while a zonal control plane upgrades. Running workloads keep serving, but CI/CD and autoscaler actions stall. Regional clusters dodge this entirely.
- **PDBs slow upgrades; they don't stop them.** The one-hour respect window per node is the contract — design PDBs for availability during churn, not as an upgrade veto. Long `terminationGracePeriodSeconds`, tight PDBs, and node affinity all stretch upgrade duration.
- **Regional vs zonal is forever** — you can't convert a cluster in place; location, VPC-native-ness, and (on Autopilot) the node service account are create-time choices.
- **Node pool deletes drain gracefully** — GKE cordons and drains respecting PDBs up to the same one-hour cap; essential `kube-system` pods must remain schedulable somewhere or the cluster degrades.
- **Storage:** PD CSI is the default (Balanced PD default class since 1.24); zonal PDs pin pods to a zone — regional clusters with zonal PVs get scheduling surprises; use regional PDs or rethink. Hyperdisk for tunable IOPS/throughput (its ML variant does ReadOnlyMany for shared model weights), Filestore CSI for RWX NFS, GCS FUSE CSI for object-storage-as-files (ML data), local SSD for fast ephemeral. Don't containerize your database reflexively — Cloud SQL/AlloyDB/Spanner exist.
- **Quotas/limits (2026-07):** Standard up to 65,000 nodes/cluster (large counts need review), 1,000 nodes per node-pool zone, 256 max pods/node (110 default); Autopilot 5,000 nodes; both: 200,000 pods, 400,000 containers, 6 GB etcd per cluster.
- **Pricing shape:** flat **$0.10/cluster/hour management fee** in both modes, then Autopilot bills pod resource requests (vCPU/GiB/ephemeral rates — over-requesting is pure waste) while Standard bills the Compute Engine nodes whether pods use them or not. Free tier: **$74.40/month credit per billing account**, effectively covering one zonal or Autopilot cluster's fee. Enterprise edition adds a per-vCPU fee. Check cloud.google.com/kubernetes-engine/pricing for current rates.
- **Autopilot cost intuition flips:** on Standard you optimize bin-packing and node utilization; on Autopilot you optimize *requests* — rightsizing requests is the whole cost game, and idle node capacity is Google's problem, not yours.
- **Cost tools:** `--enable-cost-allocation` (Standard) breaks cluster spend down by namespace and Kubernetes label in Cloud Billing and its BigQuery export — note it's based on *requests*, not consumption, so it inherits the rightsizing problem. The console's workload rightsizing recommendations and cluster utilization metrics flag over/under-provisioned workloads and idle clusters; Spot VMs (Standard pools) and Spot pods (Autopilot) are the standard discount levers for interruption-tolerant work.

## GKE vs siblings

- **vs Cloud Run:** workload-shaped decision. Request-driven stateless containers → Cloud Run (no cluster fee, scale to zero, less to run). You need Kubernetes itself — CRDs/operators, DaemonSets, StatefulSets, sidecar-heavy pods, node control, arbitrary L4 protocols → GKE. Default to Cloud Run; graduate when its constraints bite. Autopilot narrows the gap (managed nodes, pod-shaped billing) but you still own the Kubernetes objects, upgrades cadence, and the cluster fee. See [[gcp-cloud-run]].
- **vs Compute Engine:** if it's one VM-shaped thing with no orchestration need, GKE is overhead — see [[gcp-compute-engine]].
- **Autopilot vs Standard:** Autopilot unless you need what it forbids — privileged/node-level agents, custom node images (COS is fixed; Standard offers Ubuntu/Windows), single-node tuning, or Marketplace apps requiring elevated node access. Autopilot is the recommended, security-hardened, less-ops default; Standard is the escape hatch with full control.
- **Companions:** images from [[gcp-cloud-build]] + [[gcp-artifact-registry]] (scan via [[gcp-artifact-analysis]]); L7 via [[gcp-load-balancing]] and [[gcp-cloud-cdn]]; networking on [[gcp-vpc]] with [[gcp-cloud-nat]] for private-node egress and [[gcp-cloud-dns]]; auth via [[gcp-iam]]; secrets in [[gcp-secret-manager]]; observability through [[gcp-cloud-logging]] and [[gcp-cloud-monitoring]]; state in [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-spanner]], [[gcp-memorystore-redis]], [[gcp-cloud-storage]].

## Related

[[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-compute-engine]], [[gcp-cloud-build]], [[gcp-artifact-registry]], [[gcp-artifact-analysis]], [[gcp-buildpacks]], [[gcp-cloud-sdk]], [[gcp-vpc]], [[gcp-cloud-nat]], [[gcp-cloud-dns]], [[gcp-load-balancing]], [[gcp-cloud-cdn]], [[gcp-vpc-service-controls]], [[gcp-iam]], [[gcp-iap]], [[gcp-secret-manager]], [[gcp-certificate-manager]], [[gcp-cloud-logging]], [[gcp-cloud-monitoring]], [[gcp-cloud-trace]], [[gcp-pubsub]], [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-spanner]], [[gcp-memorystore-redis]], [[gcp-cloud-storage]], [[docker]], [[devops]], [[terraform]], [[site-reliability-engineering]]

Sources: https://docs.cloud.google.com/kubernetes-engine/docs, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-security, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/cluster-architecture, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/node-pools, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/release-channels, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/cluster-upgrades, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/workload-identity, https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/alias-ips, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/gateway-api, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/storage-overview, https://docs.cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster, https://docs.cloud.google.com/kubernetes-engine/docs/how-to/creating-a-zonal-cluster, https://docs.cloud.google.com/kubernetes-engine/docs/resources/autopilot-standard-feature-comparison, https://docs.cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler, https://docs.cloud.google.com/kubernetes-engine/docs/how-to/cost-allocations, https://docs.cloud.google.com/kubernetes-engine/quotas, https://cloud.google.com/kubernetes-engine/pricing (fetched 2026-07).
