---
name: gcp-compute-engine
description: "Google Compute Engine — GCP's IaaS VMs: machine families and the type-naming grammar (e2/n2/c3/m3/a3 …), Persistent Disk vs Hyperdisk vs local SSD, images and snapshots, instance templates + managed instance groups (autoscaling, autohealing, rolling updates), Spot VMs and preemption, committed/sustained-use discounts, quotas, metadata server and SSH via OS Login/IAP. Use when creating or sizing VMs, choosing machine types or disks, building MIG-based fleets, cutting compute cost with Spot/CUDs, debugging VM access, or deciding raw VMs vs GKE/Cloud Run."
license: MIT
---

# gcp-compute-engine

Compute Engine is Google Cloud's virtual machine service: create and run VMs on Google's
infrastructure, from a single `e2-micro` to thousands of vCPUs. It is the substrate every
higher-level GCP compute product (GKE, Dataflow, Dataproc, even Cloud Run's underlying pool)
is built on — when you need full OS control, custom kernels, GPUs, or lift-and-shift, this
is the layer you work at.

## The mental model

A VM **instance** is zonal, and is the product of three choices:

- **Machine type** — CPU/memory shape, drawn from a family/series catalog.
- **Image** — what the boot disk is stamped from (public or custom OS image).
- **Disks** — one boot disk plus optional data disks (durable PD/Hyperdisk, ephemeral local SSD).

**Machine-type naming grammar**: `SERIES-TYPE-vCPUS`, e.g. `n2-standard-4`, `c3-highmem-22`,
`e2-micro`. The series token encodes family letter + generation (+ CPU-vendor suffix:
`d` = AMD, `a` = Arm — `n2d`, `c4a`, `t2a`):

| Letter | Family | Series (examples) |
|---|---|---|
| E | General purpose, cost-optimized | e2 |
| N | General purpose, balanced/flexible | n1, n2, n2d, n4, n4a/n4d |
| C | General/compute, consistently high perf | c2, c2d, c3, c3d, c4, c4a/c4d, c4n |
| T | Tau scale-out | t2d (AMD), t2a (Arm) |
| H | HPC/compute-optimized | h3, h4d |
| M / X | Memory-optimized (to ~12 TB) | m1, m2, m3, m4, x4 |
| Z | Storage-optimized (Titanium SSD dense) | z3 |
| A / G | Accelerator-optimized (GPU) | a2, a3, a4, g2, g4 |

The TYPE segment fixes the memory ratio: `highcpu` ≈ 2 GB/vCPU, `standard` ≈ 4, `highmem` ≈ 8,
`megamem`/`ultramem` 12–31. N- and E-series also allow `custom-VCPUS-MEM` types (~5% premium).
Never invent a series — check `gcloud compute machine-types list --zones=ZONE`.

**Fleets**: an **instance template** freezes a full VM config; a **managed instance group (MIG)**
stamps identical VMs from it and owns their lifecycle (autoscale, autoheal, rolling update).
Zonal MIG = one zone (up to ~1,000 VMs); regional MIG spreads across zones (up to ~2,000)
and survives zone failure — default to regional for anything serving traffic.

**Identity on the VM**: every instance can run as a service account; workloads fetch tokens
from the **metadata server** at `http://metadata.google.internal/computeMetadata/v1/` (header
`Metadata-Flavor: Google` required). Startup/shutdown scripts, instance attributes, and the
Spot `preempted` flag all live there — it is how a VM knows about itself without credentials.

## Lifecycle: verified command shapes

```bash
# Create — the flags that matter
gcloud compute instances create web-1 \
  --zone=us-central1-a --machine-type=e2-medium \
  --image-family=debian-12 --image-project=debian-cloud \
  --boot-disk-size=20GB --boot-disk-type=pd-balanced \
  --network=default --subnet=default \
  --service-account=SA_EMAIL --scopes=cloud-platform \
  --metadata-from-file=startup-script=./startup.sh

# SSH — gcloud manages keys; prefer OS Login (IAM-governed, no authorized_keys sprawl)
gcloud compute ssh web-1 --zone=us-central1-a
gcloud compute ssh web-1 --tunnel-through-iap     # no external IP needed

# Fleet: template -> MIG -> rolling update
gcloud compute instance-templates create tpl-v2 --machine-type=e2-medium ...
gcloud compute instance-groups managed rolling-action start-update my-mig \
  --version=template=tpl-v2 --max-surge=3 --max-unavailable=0
```

IAP SSH needs a firewall rule allowing tcp:22 from `35.235.240.0/20` plus the IAP tunnel IAM
role. Image *families* (`--image-family=debian-12`) always resolve to the newest non-deprecated
image — reference families in templates/IaC, never pinned image names, and use deprecation of
your own custom images to roll back.

## Storage decisions

- **pd-balanced is the sane default boot/data disk**; pd-ssd for latency-sensitive, pd-standard
  only for cold/sequential, pd-extreme for provisioned-IOPS legacy needs.
- **Hyperdisk is the current generation** (Balanced/Extreme/Throughput/ML): performance is
  provisioned *independently of size*, unlike PD where performance scales with capacity. Newer
  series (C3 onward, C4, M4, Z3…) increasingly support only Hyperdisk — check series support.
- **Local SSD is ephemeral**: data is lost if the VM stops, is preempted, or fails, for any
  reason. Scratch, caches, flash-native databases with their own replication — never boot
  volumes, never sole copies.
- Snapshots are point-in-time disk backups (incremental); a *machine image* captures the whole
  instance (all disks + config); a custom *image* is a bootable template for one disk.
- Billing is for provisioned capacity from create to delete — detached disks still bill.

## Fleet mechanics

- **Autohealing**: attach an application health check to the MIG; failed VMs are recreated from
  the template. This is distinct from the load balancer's health check — configure both, and
  make the autohealing check more lenient to avoid recreate-storms during deploys.
- **Autoscaling**: on CPU, LB serving capacity, Cloud Monitoring metrics, or schedules.
- **Rolling updates**: `max-surge` (extra VMs above target during update) and `max-unavailable`
  control velocity; `--max-unavailable=0` with surge > 0 gives zero-downtime replacement.
  Canary by giving the new template a partial `target-size`. Proactive updates roll now;
  opportunistic ones apply only as instances are naturally recreated. Stateful MIGs (preserved
  names, disks, metadata) require the `recreate` replacement method, which keeps instance names.

## Cost levers

- **Spot VMs**: up to ~91% off; no SLA, no live migration; can be preempted any time via ACPI
  soft-off with up to 30 s to shut down (metadata `preempted` flips to TRUE; optional 120 s
  notice in preview). Termination action is STOP (default) or DELETE. Prices float but change
  at most ~daily. Run them in a MIG so preempted capacity is recreated; handle cleanup in a
  shutdown script. Successor to "preemptible VMs" (which had a 24 h max runtime).
- **Committed use discounts**: resource-based (commit to vCPU/RAM/GPU/local-SSD in a region;
  up to ~55% general / ~70% memory-optimized, 3-yr > 1-yr) vs Compute Flexible (spend-based,
  covers Compute Engine + GKE + Cloud Run, no region/shape lock-in, smaller %).
- **Sustained use discounts**: automatic, scale with fraction of the month used; only older
  series (N1/N2/N2D, C2, M1/M2 — up to 20–30%). E2 and current-gen series (N4, C3, C4 …) get
  no SUDs — their lower list price is the substitute. SUDs don't stack with CUDs.

## Gotchas and quotas

- Quotas are per-region and per-family (`CPUS`, `N2_CPUS`, GPU, disk-TB, in-use IPs). Check with
  `gcloud compute regions describe REGION`; new projects have small defaults — request increases
  *before* the launch, and remember Spot/GPU/local-SSD each have their own quota lines.
- Instances are zonal; a zone outage takes every single-zone VM with it. Regional MIGs or
  multi-zone placement are your HA story, not the VM itself.
- Stopping a VM stops compute billing but not disk/IP billing; a reserved static external IP
  attached to a stopped VM still costs.
- Default service account with broad scopes is a classic over-privilege trap — set a dedicated
  SA per workload and `--scopes=cloud-platform`, letting IAM do the limiting.
- **Sole-tenant nodes** exist for BYOL licensing and physical isolation (your VMs alone on a
  host) — niche, priced per node, CUD-eligible.

## vs siblings

Raw Compute Engine wins when you need OS/kernel control, GPUs/TPUs with custom drivers,
lift-and-shift of legacy or licensed software (sole-tenancy, BYOL), stateful singletons, or
maximum cost tuning (Spot + CUD arithmetic). If your unit is a container and you want managed
orchestration, use [[gcp-gke]]; if it's a stateless request-driven container, [[gcp-cloud-run]]
is less ops for less control. MIGs + templates are the poor man's orchestrator — fine for
homogeneous fleets, wrong for microservice sprawl.

## Related

[[gcp-gke]], [[gcp-cloud-run]], [[gcp-app-engine]], [[gcp-cloud-functions]], [[gcp-vpc]],
[[gcp-load-balancing]], [[gcp-cloud-nat]], [[gcp-iam]], [[gcp-iap]], [[gcp-cloud-storage]],
[[gcp-cloud-monitoring]], [[gcp-cloud-logging]], [[gcp-secret-manager]], [[gcp-cloud-sql]],
[[gcp-cloud-sdk]], [[terraform]], [[ansible]], [[devops]]

Sources: https://docs.cloud.google.com/compute/docs, https://docs.cloud.google.com/compute/docs/machine-resource, https://docs.cloud.google.com/compute/docs/disks, https://docs.cloud.google.com/compute/docs/images, https://docs.cloud.google.com/compute/docs/instance-groups, https://docs.cloud.google.com/compute/docs/instances/spot, https://docs.cloud.google.com/compute/docs/instances/create-start-instance, https://docs.cloud.google.com/compute/docs/instances/ssh, https://docs.cloud.google.com/compute/docs/metadata/overview, https://docs.cloud.google.com/compute/docs/instances/committed-use-discounts-overview, https://docs.cloud.google.com/compute/docs/sustained-use-discounts, https://docs.cloud.google.com/compute/quotas-limits, https://docs.cloud.google.com/compute/docs/instance-groups/rolling-out-updates-to-managed-instance-groups (fetched 2026-07).
