---
name: gcp-cloud-router
description: "Google Cloud Router: the managed BGP speaker (control plane only — never a data-plane hop) that exchanges routes between a VPC and on-prem/multicloud over HA VPN tunnels and Interconnect VLAN attachments. Covers dynamic routing mode (regional vs global) and what each BGP session advertises/learns, default vs custom route advertisements, MED/base priority for path steering, BFD fast failure detection, ASN rules (16550 for Partner Interconnect), and the quota cliffs (peers per router, learned-route prefixes). Use when wiring BGP for hybrid connectivity, steering traffic with MED/priorities, debugging why on-prem routes aren't in the VPC (or vice versa), or hitting dynamic-route quotas."
license: MIT
---

# Google Cloud Router

Managed, regional BGP control plane for a VPC network. It runs BGP sessions over HA VPN tunnels, Interconnect VLAN attachments, and NCC Router appliance links, advertises VPC routes to the peer, and installs learned routes into the VPC as dynamic routes. Required for HA VPN and all Interconnect flavors (Dedicated, Partner, Cross-Cloud); optional for Classic VPN.

## The mental model

Cloud Router is **not a router in the data path**. Docs verbatim: Cloud Routers don't provide packet routing or forwarding capability — Andromeda (Google's SDN) forwards packets; Cloud Router only *decides* the routes and programs them. Consequences:

- No bandwidth through it, no failover of "the router" affecting traffic — a control-plane outage leaves existing routes forwarding (pair with graceful restart on the on-prem device so routes survive BGP re-establishment).
- One Cloud Router lives in one **region + VPC network** and uses **one ASN for all its BGP sessions**.
- **Learned routes become VPC dynamic routes.** Who can use them is decided not by the router but by the VPC's **dynamic routing mode**: `regional` (default) installs learned routes only in the router's own region and advertises only same-region subnets; `global` installs them in every region and advertises subnets from all regions (with an inter-region cost added to MED).
- The reverse direction mirrors it: in regional mode a VM in another region has **no route** to on-prem via that router — the classic "VPN works from us-east1 but not europe-west1" bug.
- IPv6: BGP over IPv6 sessions or MP-BGP over IPv4 exchanging both address families (IPv6 sessions unsupported on Classic VPN, Router appliance, Cross-Cloud Interconnect attachments).

## Shapes

```bash
# Router (one per region+network pair as needed; ASN must be private — except Partner Interconnect: exactly 16550)
gcloud compute routers create cr-use1 \
  --network=my-vpc --region=us-east1 --asn=65001

# Interface bound to an HA VPN tunnel + BGP peer (link-local 169.254.0.0/16 peering IPs)
gcloud compute routers add-interface cr-use1 --region=us-east1 \
  --interface-name=if-tun0 --vpn-tunnel=tunnel0 \
  --ip-address=169.254.10.1 --mask-length=30
gcloud compute routers add-bgp-peer cr-use1 --region=us-east1 \
  --peer-name=peer0 --interface=if-tun0 \
  --peer-ip-address=169.254.10.2 --peer-asn=65010 \
  --advertised-route-priority=100

# Custom advertisements on one session (subnets + extra ranges, e.g. restricted.googleapis.com VIP)
gcloud compute routers update-bgp-peer cr-use1 --region=us-east1 --peer-name=peer0 \
  --advertisement-mode=custom --set-advertisement-groups=all_subnets \
  --set-advertisement-ranges=199.36.153.4/30

# BFD on an Interconnect BGP session
gcloud compute routers update-bgp-peer cr-use1 --region=us-east1 --peer-name=peer0 \
  --bfd-session-initialization-mode=active \
  --bfd-min-transmit-interval=1000 --bfd-min-receive-interval=1000 --bfd-multiplier=5

gcloud compute routers get-status cr-use1 --region=us-east1   # BGP state + learned routes
```

## Advertisements and path steering

- **Default mode**: advertises subnet ranges only — same-region subnets (regional mode) or all-region subnets (global mode). Tracks subnet lifecycle automatically.
- **Custom mode**: set at router level (all sessions) or per BGP session (overrides router). Two variants: custom prefixes *only*, or custom *in addition to* subnets (`--set-advertisement-groups=all_subnets`). Default routes (`0.0.0.0/0`, `::/0`) are allowed — how you make on-prem egress via Google.
- **MED = base advertised route priority (default 100)**; in global mode cross-region subnet routes get `base + inter-region cost` added, so same-region paths naturally win. Custom ranges always use the base priority alone. Lower MED = preferred.
- Steering: give the preferred tunnel/attachment's session a lower `--advertised-route-priority` for active/passive; equal priorities give ECMP.
- Inbound tie-break: among learned routes to the same prefix, the VPC picks by the peer's MED (becomes the dynamic route priority).

## Gotchas

- **Regional vs global routing mode is the #1 surprise** — switching the VPC to global changes what every Cloud Router in it advertises and where learned routes apply, network-wide, instantly.
- **On-prem may ignore your MED**: BGP attributes (local-pref, AS path) are evaluated before MED, and Google's inter-region costs can change over time — don't build invariants on exact MED values.
- **Quota cliffs**: 5 Cloud Routers per region+network; 128 BGP peers per router; a peer sending > 5,000 prefixes gets its **session reset**; unique learned-route prefixes per region per VPC default 250 (same-region) + 250 (cross-region, adjustable); 200 custom advertised ranges per session. Alert on the learned-routes metrics before hitting them — overflow routes are silently dropped.
- **BFD is Interconnect-only**: Dedicated/Partner VLAN attachments on Dataplane v2. Explicitly *not* supported on HA VPN tunnels or Router appliance. Asynchronous control-only mode (no echo, no demand); intervals 1000–30000 ms, multiplier 5–16; cuts detection from ~60 s (BGP hold) to ~5 s.
- **Partner Interconnect hard-requires ASN 16550** on the Cloud Router; everything else wants a private ASN. One router = one ASN, so a router can't mix Partner Interconnect and a differently-numbered peering scheme.
- BGP sessions are **unauthenticated by default** — enable MD5 where the peer supports it.
- Custom learned routes (static "pretend the peer advertised this" entries, max 10/session) behave exactly like BGP-learned routes — useful when the peer can't advertise a prefix.

## Debugging "the route isn't there"

1. `get-status` on the router: is the BGP session `Established`? If not, it's peering IPs/ASN/MD5/firewall on the underlying tunnel or attachment — not routing policy.
2. Session up but on-prem lacks a VPC prefix → check advertisement mode (custom-only mode silently drops subnets unless `all_subnets` group is set) and, in regional mode, whether the subnet is in another region.
3. Session up but VPC lacks an on-prem prefix → check the peer actually advertises it (`get-status` lists learned routes), then the learned-route quota (silent drop past the regional limit), then dynamic routing mode if the consumer VM sits in another region.
4. Asymmetric or flapping paths across two tunnels → compare advertised priorities on both sessions (unequal = active/passive, equal = ECMP) and confirm the on-prem side isn't overriding MED with local-pref.

## Role in the stack

Never standalone. Cloud Router only exists attached to something: HA VPN tunnels ([[gcp-cloud-vpn]]), Interconnect VLAN attachments ([[gcp-interconnect]]), NCC Router appliances — and as the non-BGP config anchor for Cloud NAT gateways ([[gcp-cloud-nat]]). Design sequence: choose the VPC dynamic routing mode first, then one router (or an HA pair of sessions on one router) per region per hybrid path, then advertisement policy per session.

## Related

- [[gcp-vpc]] — dynamic routing mode lives on the network; learned routes join its routing table
- [[gcp-cloud-vpn]] — HA VPN's 99.99% SLA assumes BGP via Cloud Router on both tunnels
- [[gcp-interconnect]] — every VLAN attachment needs a Cloud Router; BFD lives here
- [[gcp-cloud-nat]] — uses a Cloud Router as regional config anchor, no BGP involved
- [[gcp-cloud-dns]] — hybrid forwarding zones ride the routes Cloud Router learns
- [[gcp-vpc-service-controls]] — advertise restricted VIP ranges to on-prem via custom mode
- [[gcp-cloud-monitoring]] — quota/learned-route metrics and BGP session alerting
- [[network-engineering]] — BGP fundamentals: MED, ASN, ECMP, graceful restart, BFD

Sources: https://docs.cloud.google.com/network-connectivity/docs/router, https://docs.cloud.google.com/network-connectivity/docs/router/concepts/overview, https://docs.cloud.google.com/network-connectivity/docs/router/concepts/advertised-routes, https://docs.cloud.google.com/network-connectivity/docs/router/concepts/bfd, https://docs.cloud.google.com/network-connectivity/docs/router/quotas, https://docs.cloud.google.com/network-connectivity/docs/router/concepts/best-practices (fetched 2026-07).
