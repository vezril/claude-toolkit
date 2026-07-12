---
name: gcp-interconnect
description: "Google Cloud Interconnect — private physical connectivity into a VPC: Dedicated (your 10/100/400 Gbps circuits into a Google colocation edge, LOA-CFA provisioning), Partner (50 Mbps–50 Gbps VLAN attachments via a service provider, pairing-key flow), and Cross-Cloud (Google-provisioned links to AWS/Azure/OCI/Alibaba). VLAN attachments + Cloud Router BGP carry the traffic; redundancy topology (edge availability domains, metros) determines the 99.9% vs 99.99% SLA; not encrypted by default (MACsec or HA VPN over Interconnect). Use when connecting on-prem or another cloud to Google at bandwidths beyond VPN, designing SLA-grade hybrid topologies, sizing attachments, or weighing Interconnect vs HA VPN."
license: MIT
---

# Google Cloud Interconnect

Private, high-bandwidth, low-latency physical connectivity between your network and
your VPC — traffic bypasses the public internet entirely. Three flavors: **Dedicated**
(your fiber into Google's edge), **Partner** (a service provider's fiber, you buy a
slice), and **Cross-Cloud** (Google-run links to AWS, Azure, OCI, Alibaba Cloud).
Internal VPC IPs become directly reachable from on-prem, no NAT.

## The mental model

**Physical circuit → VLAN attachment → Cloud Router BGP session → VPC routes. The SLA
is a property of your redundancy topology, not of any single circuit.**

- The **circuit** is layer 1/2: for Dedicated, one or more 10/100/400 Gbps Ethernet
  links (bundled with LACP — required even for a single link) landed in a Google
  colocation facility. For Partner, the provider owns the circuit; for Cross-Cloud,
  Google owns it end to end up to the other cloud's demarcation.
- A **VLAN attachment** is the layer 2 unit of consumption: an 802.1Q tag on the
  circuit that connects one Cloud Router to one VPC network, with a capacity ceiling
  you choose. Multiple attachments per circuit = multiple VPCs or redundancy legs.
- **BGP on a Cloud Router is the control plane** — it advertises VPC subnets to your
  router and learns on-prem routes dynamically. No static-route Interconnect. Route
  reach follows the router's VPC dynamic routing mode (regional vs global).
- **Edge availability domains** are Google's maintenance-isolation zones within a
  metro. The SLA recipes are topology recipes:
  - **99.9% (non-critical)**: 2 connections in the same metro, different edge
    availability domains (Partner: 2 VLAN attachments in different domains).
  - **99.99% (critical)**: 4 connections across **2 metros**, 2 per metro in different
    edge domains, ≥2 Cloud Routers, **global dynamic routing enabled** — so a region
    can fail over to the surviving metro's attachments.
- **Nothing is encrypted by default.** Options: **MACsec** (IEEE 802.1AE, GCM-AES-256
  pre-shared CAK/CKN, hitless rotation up to 5 keys) encrypts only your-router↔Google-edge,
  or **HA VPN over Cloud Interconnect** for IPsec across the private link.

## Choosing a flavor

- **Dedicated**: you're in (or can reach) a colocation facility with Google's edge;
  need 10 Gbps+; want the lowest per-bit cost at scale. Link types: 10, 100, or
  400 Gbps, up to 8 circuits per bundle (80 G / 800 G / 3.2 T). Link type is
  **immutable after creation**. Provisioning: order → Google issues an **LOA-CFA** →
  vendor runs the cross-connect → test → create attachments. Think weeks, not hours.
- **Partner**: no colo presence, or you need sub-10G. You create a VLAN attachment,
  get a **pairing key**, hand it to a supported provider who provisions their side.
  Attachment capacities **50 Mbps–50 Gbps**. Layer 2 partners: you run BGP to Cloud
  Router yourself; layer 3 partners: the provider runs BGP for you.
- **Cross-Cloud**: multi-cloud backbone without managing your own circuits. Google
  provisions the physical link to the remote cloud's demarcation; **you still buy the
  remote side's port** (Direct Connect / ExpressRoute / FastConnect / Express Connect)
  and hand Google the authorization. 10/100 Gbps everywhere, 400 Gbps for AWS and OCI.
  Lead time 1–4 weeks.

## Gotchas

- **Provisioning lead time is the schedule risk**: LOA-CFA + vendor cross-connect for
  Dedicated, partner turn-up for Partner, 1–4 weeks for Cross-Cloud. Plan hybrid
  cutovers around it; bring up HA VPN first if you need connectivity now.
- **Attachment capacity is a ceiling you pick, and Partner tops out at 50 Gbps per
  attachment** — above that you scale out with more attachments (ECMP via BGP), not up.
- **The Partner SLA covers Google↔provider only.** Your last mile to the provider is
  your contract with them. Budget availability accordingly.
- **The SLA is void without the full recipe** — same-domain "redundant" circuits, one
  Cloud Router, or regional-only routing in a two-metro design all silently disqualify
  you from 99.99%.
- **MACsec caveats**: standard on 100/400 Gbps; 10 Gbps only at select facilities
  (allowlist via your account team). It stops at Google's edge — no encryption in
  transit inside Google, so regulated workloads often still layer IPsec/TLS.
- **MTU**: attachments support 1440/1460/1500/8896 bytes; jumbo (8896) only on
  unencrypted attachments. Mismatched MTU with on-prem = fragmentation or blackholes.
- **Cross-region interplay**: data transfer bills to the *attachment's* project, and if
  the VM's region differs from the attachment's region you pay inter-region rates on
  top of Interconnect egress.
- **Pricing shape**: (1) per-circuit hourly for Dedicated/Cross-Cloud (order of
  $2.33/hr per 10 G, $23/hr per 100 G Dedicated; Cross-Cloud higher); (2) per-VLAN-
  attachment hourly — flat ~$0.10/hr for Dedicated attachments up to 10 G, capacity-
  tiered for Partner (≈$0.05/hr at 50 Mbps → ≈$9/hr at 50 Gbps), plus the partner's own
  separate bill; (3) **data transfer out per GiB** (~$0.02 NA/EU) — several times
  cheaper than internet egress, which is a big part of the TCO case; ingress free.

## vs siblings

- **[[gcp-cloud-vpn]]**: HA VPN = ~1–3 Gbps per tunnel over the internet, encrypted,
  live in hours, cheap. Interconnect = 10 Gbps–3.2 Tbps private capacity, consistent
  latency, cheaper egress, weeks of lead time, unencrypted by default. Rule of thumb:
  sustained multi-Gbps or latency-sensitive hybrid traffic → Interconnect; bursty,
  modest, or urgent → HA VPN. Need both capacity *and* encryption → HA VPN over
  Interconnect or MACsec.
- **[[gcp-cloud-router]]** is mandatory — every attachment's BGP session lives on one,
  and its global-vs-regional mode is part of the 99.99% recipe.
- Egress to the internet is [[gcp-cloud-nat]]/VPC territory; Interconnect only carries
  traffic to *your* networks.

## Related

- [[gcp-cloud-router]] — the BGP control plane for every VLAN attachment
- [[gcp-cloud-vpn]] — the internet-based sibling; also rides Interconnect as HA VPN over Interconnect
- [[gcp-vpc]] — the network attachments terminate in; dynamic routing mode shapes SLA eligibility
- [[gcp-cloud-nat]] — internet egress for the same private VMs
- [[network-engineering]] — BGP, LACP, ECMP, and edge-redundancy fundamentals

Sources: https://docs.cloud.google.com/network-connectivity/docs/interconnect,
https://docs.cloud.google.com/network-connectivity/docs/interconnect/concepts/overview,
https://docs.cloud.google.com/network-connectivity/docs/interconnect/concepts/dedicated-overview,
https://docs.cloud.google.com/network-connectivity/docs/interconnect/concepts/partner-overview,
https://docs.cloud.google.com/network-connectivity/docs/interconnect/concepts/cci-overview,
https://docs.cloud.google.com/network-connectivity/docs/interconnect/concepts/macsec-overview,
https://cloud.google.com/network-connectivity/docs/interconnect/pricing (fetched 2026-07).
