---
name: gcp-cloud-vpn
description: "Google Cloud VPN — IPsec tunnels over the public internet between a VPC and a peer network. HA VPN (two-interface gateway, BGP via Cloud Router, 99.99% SLA when both interfaces have tunnels to a redundant peer) vs deprecated-for-BGP Classic VPN; per-tunnel ~250k pps ceiling scaled with ECMP; IKE cipher, MTU/MSS, and rekey gotchas. Use when connecting on-prem or another cloud to a VPC over the internet, designing SLA-grade VPN topologies, debugging tunnel throughput or BGP sessions, or choosing between Cloud VPN and Interconnect."
license: MIT
---

# Google Cloud VPN

Managed IPsec VPN connecting your VPC to a peer network (on-prem, AWS, Azure, another
VPC) over the public internet. Two products: **HA VPN** (the current one — regional,
two interfaces, dynamic routing, 99.99% SLA) and **Classic VPN** (legacy — single
interface, static routing only, 99.9% SLA). Everything new should be HA VPN.

## The mental model

**An HA VPN gateway is two interfaces, and the SLA is a topology property.**

- An HA VPN gateway gets **two interfaces**, each with its own external IP drawn
  automatically from Google's pool (no forwarding rules to manage, unlike Classic).
- The **99.99% SLA requires tunnels from *both* interfaces** to a peer that is itself
  redundant: two peer gateways, one peer gateway with two IPs, or one peer device that
  is internally redundant behind one IP. Interface 0 pairs with peer interface 0,
  interface 1 with peer interface 1. One tunnel from one interface = no 99.99% SLA.
- **Dynamic routing via BGP on a Cloud Router is mandatory for HA VPN.** There is no
  static-route HA VPN. Each tunnel carries a BGP session; failover is BGP reconvergence,
  not gateway magic. Route scope follows the Cloud Router's VPC dynamic routing mode
  (regional vs global).
- **Each tunnel has a hard ceiling: ~250,000 pps** (ingress + egress summed), roughly
  1–3 Gbps depending on packet size. You do not scale a tunnel; you **add tunnels and
  ECMP across them** (active/active). Active/passive keeps failover capacity honest —
  throughput never exceeds what one tunnel can carry, so failover doesn't degrade.
  Rule of thumb from the docs: active/passive for a single gateway pair, active/active
  when spreading across multiple gateways.
- Traffic crosses the public internet — encrypted, but with internet latency and jitter.
  For guaranteed bandwidth/latency you want Interconnect (see below).

## Setup shape (HA VPN to a peer network)

1. **Create the HA VPN gateway** in a region — it materializes with two interfaces and
   two external IPs.
2. **Create an external peer VPN gateway resource** describing the peer side (1, 2, or
   4 interfaces/IPs to model its redundancy).
3. **Create (or reuse) a Cloud Router** in the same region, with an ASN for BGP.
4. **Create two tunnels** — interface 0 → peer, interface 1 → peer — each with an IKE
   pre-shared key. IKEv2 preferred (required for IPv6).
5. **Configure a BGP session per tunnel** on the Cloud Router (link-local /30 peering
   addresses), and mirror the config on the peer device.
6. **Open firewall rules** for the peer ranges; verify both tunnels are `ESTABLISHED`
   and both BGP sessions are up — only then does the topology qualify for the SLA.

For VPC-to-VPC across regions, put an HA VPN gateway on each side (gateway pairs peer
directly, no external gateway resource needed).

## Gotchas

- **Classic VPN's BGP support is deprecated (date-stamped): as of August 1, 2025,
  creating Classic VPN tunnels with dynamic routing/BGP is no longer supported.**
  Existing BGP Classic tunnels run SLA-less and can't be recreated once deleted.
  Classic VPN survives only for static-routing cases (including to VM-based VPN
  gateways). HA VPN is the only BGP path — migrate.
- **Cipher drift on rekey**: if you propose multiple ciphers per role, the selected
  cipher can *change* when new SAs are created during key rotation — silently shifting
  MTU and performance. Docs' fix: propose/accept exactly **one cipher per role**, and
  give both tunnels of an HA pair identical ciphers and IKE Phase 2 lifetimes
  (Cloud VPN defaults: Phase 1 36,000 s, Phase 2 10,800 s).
- **MTU/MSS**: IPsec encapsulation eats headroom — set tunnel MTU appropriately and
  clamp TCP MSS, or large packets fragment/blackhole. Enable IKEv2 fragmentation
  (RFC 7383) on the peer so large IKE messages survive.
- **Per-tunnel pps is the real limit**, not Gbps: 250k pps total both directions.
  Small-packet workloads hit it long before "3 Gbps". ECMP spreads *flows*, not
  packets — one elephant flow stays on one tunnel.
- IKEv1 and IKEv2 both supported (pre-shared keys only, no certificates); **IPv6
  requires IKEv2**, and modp_8192 is unsupported on IPv6-enabled HA VPN gateways.
- Tunnel/gateway counts are regional quotas (adjustable) — check the console Quotas
  page before designing a many-tunnel ECMP fan-out.
- **Pricing shape**: per **tunnel-hour** charge plus standard **internet egress** rates
  on traffic leaving Google; ingress free. Two-tunnel HA topologies cost two tunnels.

## vs siblings

- **[[gcp-interconnect]]**: VPN = encrypted over internet, ~1–3 Gbps/tunnel, cheap,
  hours to set up. Interconnect = private physical link, 10/100 Gbps (Dedicated) or
  50 Mbps–50 Gbps (Partner), higher cost + lead time, traffic *not* encrypted by
  default. Need both encryption and capacity? **HA VPN over Cloud Interconnect** runs
  IPsec tunnels across the private link.
- **[[gcp-cloud-router]]** is not optional here — it's the BGP speaker for every HA VPN
  tunnel and controls advertised routes and failover behavior.
- For private access to Google APIs rather than to your own network, that's
  [[gcp-vpc]] Private Google Access territory, not a VPN problem.

## Related

- [[gcp-cloud-router]] — mandatory BGP control plane for HA VPN tunnels
- [[gcp-interconnect]] — the higher-bandwidth, SLA-heavier sibling; also the substrate for HA VPN over Interconnect
- [[gcp-vpc]] — the network the gateway attaches to; dynamic routing mode shapes route propagation
- [[gcp-cloud-nat]] — egress for private VMs; unrelated data path but often co-designed
- [[network-engineering]] — BGP, ECMP, and failover fundamentals
- [[tcp-ip]] — MTU, MSS clamping, and fragmentation mechanics

Sources: https://docs.cloud.google.com/network-connectivity/docs/vpn,
https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/overview,
https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/topologies,
https://docs.cloud.google.com/network-connectivity/docs/vpn/deprecations/classic-vpn-deprecation,
https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/supported-ike-ciphers,
https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/best-practices,
https://docs.cloud.google.com/network-connectivity/docs/vpn/quotas (fetched 2026-07).
