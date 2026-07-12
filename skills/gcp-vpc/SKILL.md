---
name: gcp-vpc
description: "Google Cloud VPC — software-defined networking where the VPC is a GLOBAL resource and subnets are REGIONAL. Covers auto vs custom mode, stateful firewall rules (implied deny-ingress/allow-egress, priority 0-65535, tag/service-account targeting) vs hierarchical/global/regional network firewall policies, system + custom routes, non-transitive VPC peering, Shared VPC (host/service projects), the private-access menu (Private Google Access, Private Service Connect, private services access), alias IP ranges, and flow logs. Use when designing GCP network topology, writing firewall rules or Terraform for networks/subnets, debugging cross-VPC or private-API connectivity, choosing between peering/Shared VPC/PSC, or planning CIDR space."
license: MIT
---

# GCP Virtual Private Cloud (VPC)

The networking foundation of Google Cloud: a virtualized network layer providing IP allocation,
routing, firewalling, and private connectivity for Compute Engine, GKE, Cloud Run, and every
service that touches an internal IP. Everything else in the gcp networking set (NAT, VPN,
Interconnect, load balancing, DNS) hangs off a VPC.

## The mental model

The inversion newcomers from AWS miss: **a GCP VPC is global; subnets are regional.**
There is no per-region VPC. One network spans every region over Google's backbone; you place
regional subnets inside it, and VMs in different regions on the same network reach each other
on internal IPs with zero extra wiring. Consequences:

- No inter-region peering, transit VPCs, or region-pair meshes just to get cross-region traffic.
- A subnet is not an AZ-level object either — it spans all zones in its region.
- "Multi-region" in GCP usually means *more subnets in the same VPC*, not more VPCs.

The rest of the model:

- **Routing is implicit + custom.** Every subnet's primary/secondary range gets an automatic
  *subnet route* visible network-wide; a system default route (`0.0.0.0/0` → `default-internet-gateway`)
  handles egress. You add custom static routes (next hop: instance, internal passthrough NLB,
  VPN tunnel, gateway) or dynamic routes via Cloud Router/BGP. Evaluation: subnet routes always
  win, then most-specific destination, then priority. Dynamic routing mode (`regional` | `global`)
  on the network controls whether Cloud Router advertises/learns across all regions.
- **Firewalls are stateful and attach to the network, not to instances.** Rules select targets by
  network tag or service account (mutually exclusive in one rule). Allowed connections get return
  traffic automatically (idle TCP tracked ~10 min). Two *implied* rules exist on every network:
  deny all ingress, allow all egress — both at lowest precedence, both overridable.
- **Peering is non-transitive by design.** A↔B and B↔C never gives A→C. Full-mesh or hub via
  Network Connectivity Center — never assume transit through a peer.
- **Shared VPC = host project owns the network; service projects attach workloads.** Centralized
  network/firewall administration in the host, delegated subnet use (`compute.networkUser` at
  subnet granularity) to application teams. Same organization required.

Two network modes: **auto mode** (one `/20` per region auto-carved from `10.128.0.0/9`, grows as
regions launch) and **custom mode** (starts empty; you define every subnet). Production guidance
is unambiguous: custom mode. Conversion is one-way, auto → custom only.

Firewall management has two generations: classic **VPC firewall rules** (per-network, tags/SAs)
and **network firewall policies** (hierarchical at org/folder, global, or regional; rules use
IAM-governed secure tags; policies can be attached across networks). Hierarchical policies
evaluate *before* network-level rules and can `goto_next` to delegate downward.

## Private access decision map

| Need | Use |
|---|---|
| VMs without external IPs calling Google APIs (Storage, BigQuery…) | **Private Google Access** — a per-subnet boolean; traffic exits via the default internet gateway route but never leaves Google |
| Same, but a fixed internal IP / no default-route dependency / VPC-SC control | **Private Service Connect endpoint for Google APIs** |
| Consuming a service published by another org/team's VPC | **PSC endpoint (published services)** — no route exchange, no CIDR coordination, no transitivity worries |
| Google-managed instances that live in a producer VPC (Cloud SQL private IP, Memorystore, older AlloyDB) | **Private services access** — VPC peering to the producer network; you allocate a reserved range; inherits peering's non-transitivity |
| On-prem hosts calling Google APIs privately | Private Google Access for on-prem via VPN/Interconnect + `private.googleapis.com` / `restricted.googleapis.com` VIPs |
| Two of *your* VPCs, full subnet-route exchange acceptable | **VPC peering** (or NCC hub-and-spoke at scale) |
| Cloud Run / Functions / App Engine reaching VPC-internal IPs | Serverless VPC access connector or Direct VPC egress |

Default to PSC for service-to-service across trust boundaries; peering only when you genuinely
want flat mutual IP reachability.

## Shapes (verified 2026-07)

```bash
# Custom mode network
gcloud compute networks create prod-net \
    --subnet-mode=custom \
    --bgp-routing-mode=regional \        # or global; default regional
    --mtu=1460                           # 1300–8896; 1460 default, 8896 for jumbo

# Regional subnet with a secondary range (GKE pods/services) and PGA
gcloud compute networks subnets create prod-us-central1 \
    --network=prod-net --region=us-central1 \
    --range=10.10.0.0/20 \
    --secondary-range=pods=10.16.0.0/14 \
    --enable-private-ip-google-access

# Firewall rule: allow SSH from IAP range to tagged VMs
gcloud compute firewall-rules create allow-iap-ssh \
    --network=prod-net --direction=INGRESS --action=ALLOW \
    --rules=tcp:22 --source-ranges=35.235.240.0/20 \
    --target-tags=ssh-enabled --priority=1000 --enable-logging

# One-way conversion
gcloud compute networks update legacy-net --switch-to-custom-subnet-mode
```

Terraform equivalents: `google_compute_network` (`auto_create_subnetworks = false`),
`google_compute_subnetwork` (with `secondary_ip_range` blocks, `private_ip_google_access`),
`google_compute_firewall`, `google_compute_network_firewall_policy(_rule/_association)`.

## Gotchas

- **Auto-mode CIDR collisions.** Every auto-mode network uses the same `10.128.0.0/9` carve-up,
  so two auto-mode networks can never peer, and peering/VPN to on-prem 10.x space collides.
  This alone justifies custom mode everywhere.
- **Peering non-transitivity traps.** Private services access is itself a peering — so a VPC
  peered to yours cannot reach your Cloud SQL private IP, and on-prem over VPN can't either
  unless you export/import custom routes (`--export-custom-routes` / `--import-custom-routes`).
- **Peering is quota-coupled.** A network plus all its peers form a *peering group* sharing
  limits (peers per network, subnet ranges, instances, dynamic routes per region). Exceeding the
  dynamic-route limit silently drops peering dynamic routes. Full-mesh grows O(n²) — plan NCC early.
- **Firewall priority semantics.** 0–65535, lower number wins, default 1000. Priorities need not
  be unique; at *equal* priority deny beats allow, but evaluation order of same-priority rules is
  otherwise indeterminate. Hierarchical policy rules evaluate before your network rules entirely.
- **The implied rules bite in both directions.** New network + no rules = nothing can reach your
  VMs (implied deny ingress) but they can exfiltrate anywhere (implied allow egress). Egress
  lockdown must be explicit (`--action=DENY --direction=EGRESS` at a strong priority).
- **Network tags are not security boundaries.** Anyone with instance edit rights can add a tag
  and inherit its firewall exposure. Prefer service-account targeting (tied to IAM, requires
  instance stop to change) or secure tags in firewall policies.
- **Subnet ranges: 4 IPs reserved** per primary range (network, gateway, second-to-last,
  broadcast); primary ranges can expand but never shrink; up to 170 secondary ranges per subnet;
  alias ranges cap at 150 per NIC.
- **Alias IPs over static routes to instances.** Alias ranges get automatic routes and pass
  anti-spoofing; hand-rolled routes to a VM's extra IPs need IP forwarding and lose those checks.
  VPC-native GKE = pods on alias IPs from a secondary range.
- **Flow logs are sampled 5-tuple flows, not pcap** — per-subnet toggle, 5s default aggregation,
  configurable sampling ≤1.0, into Cloud Logging. Costs scale with traffic; filter and lower
  sampling before enabling fleet-wide.
- **MTU is fixed per network** (1300–8896, default 1460); mismatched MTUs across VPN/peering
  cause blackholed large packets, not clean errors.

## Related

Networking set: [[gcp-cloud-nat]], [[gcp-cloud-vpn]], [[gcp-interconnect]], [[gcp-cloud-router]],
[[gcp-cloud-dns]], [[gcp-load-balancing]], [[gcp-cloud-cdn]], [[gcp-media-cdn]],
[[gcp-secure-web-proxy]], [[gcp-vpc-service-controls]], [[gcp-cloud-ids]], [[gcp-cloud-domains]].
Consumers: [[gcp-compute-engine]], [[gcp-gke]], [[gcp-cloud-run]], [[gcp-cloud-sql]],
[[gcp-memorystore-redis]], [[gcp-alloydb]]. Governance: [[gcp-iam]], [[gcp-iap]].
General: [[network-engineering]], [[network-security]], [[terraform]].

Sources: https://docs.cloud.google.com/vpc/docs/overview, https://docs.cloud.google.com/vpc/docs/subnets, https://docs.cloud.google.com/firewall/docs/firewalls, https://docs.cloud.google.com/firewall/docs/firewall-policies-overview, https://docs.cloud.google.com/firewall/docs/using-firewalls, https://docs.cloud.google.com/vpc/docs/routes, https://docs.cloud.google.com/vpc/docs/vpc-peering, https://docs.cloud.google.com/vpc/docs/shared-vpc, https://docs.cloud.google.com/vpc/docs/private-access-options, https://docs.cloud.google.com/vpc/docs/alias-ip, https://docs.cloud.google.com/vpc/docs/create-modify-vpc-networks, https://docs.cloud.google.com/vpc/docs/using-flow-logs, https://docs.cloud.google.com/vpc/docs/quota (fetched 2026-07).
