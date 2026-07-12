---
name: gcp-cloud-nat
description: "Google Cloud NAT: managed egress NAT so VMs, GKE nodes, and serverless (Direct VPC egress) without external IPs can reach the internet — distributed SNAT programmed into the VPC data plane (no appliance, no choke point), configured on a Cloud Router per region+network. Covers Public vs Private NAT, auto vs manual NAT IPs, static vs dynamic port allocation and the port-exhaustion math, NAT rules, drain, logging/metrics, pricing shape. Use when giving private instances outbound access, debugging SNAT port exhaustion or dropped egress packets, pinning stable source IPs for allowlists, or choosing Cloud NAT vs public IPs vs Secure Web Proxy."
license: MIT
---

# Google Cloud NAT

Managed source-NAT for resources that have no external IP: Compute Engine VMs, GKE nodes/pods (private clusters), Cloud Run / Cloud Run functions via Direct VPC egress or Serverless VPC Access, and App Engine standard via Serverless VPC Access. Egress only — it never accepts unsolicited inbound connections (DNAT exists solely for response packets of established flows).

## The mental model

Cloud NAT is **not a box**. There is no proxy VM, no appliance, no single path traffic funnels through. Andromeda (Google's SDN) programs the SNAT mappings directly into the virtual network stack of each VM's host machine. Consequences:

- **No bandwidth penalty, no choke point, no single point of failure** — each VM does its own translation at line rate.
- **No inbound** — it can't be misused as an entry point; pair with IAP or a load balancer for ingress.
- **Control plane rides on a Cloud Router**: one NAT gateway config attaches to a Cloud Router and serves subnets of one VPC network in one region. The router is just the config anchor — NAT traffic doesn't "pass through" it, and it doesn't need BGP.
- Two flavors: **Public NAT** (private VMs → internet, the common case) and **Private NAT** (private-to-private translation across NCC spokes / hybrid connections, for overlapping IPv4 ranges).

## Shapes

```bash
# Anchor router (no BGP needed)
gcloud compute routers create nat-router --network=my-vpc --region=us-central1

# Gateway, auto-allocated IPs, all subnets in the region
gcloud compute routers nats create my-nat \
  --router=nat-router --region=us-central1 \
  --nat-all-subnet-ip-ranges --auto-allocate-nat-external-ips

# Manual (reserved static) IPs — needed for stable allowlist source IPs
gcloud compute routers nats create my-nat \
  --router=nat-router --region=us-central1 \
  --nat-custom-subnet-ip-ranges=app-subnet \
  --nat-external-ip-pool=nat-ip-1,nat-ip-2

# Dynamic port allocation
gcloud compute routers nats update my-nat --router=nat-router --region=us-central1 \
  --enable-dynamic-port-allocation --min-ports-per-vm=64 --max-ports-per-vm=4096

# Drain an IP gracefully (existing connections live on; no new ones use it)
gcloud compute routers nats update my-nat --router=nat-router --region=us-central1 \
  --nat-external-ip-pool=nat-ip-1 --nat-external-drain-ip-pool=nat-ip-2
```

## Port math — where Cloud NAT bites

Each NAT IP has **64,512 usable ports per protocol** (65,536 minus well-known 0–1023).

- **Static allocation** (Public NAT default): every VM gets a fixed block, default **64 ports/VM**. Capacity: `⌊(NAT IPs × 64,512) / ports-per-VM⌋` VMs — one IP at 64 ports serves 1,008 VMs.
- **Dynamic allocation**: starts at a minimum (default 32), **doubles** as a VM nears exhaustion up to your `--max-ports-per-vm`, shrinks when idle. Incompatible with endpoint-independent mapping.
- A port maps one *concurrent connection per destination 3-tuple* (dest IP, dest port, protocol); the same NAT IP:port pair supports up to 1,024 connections to a single destination 3-tuple.

**SNAT exhaustion**: a VM opening many concurrent connections (crawlers, high-fanout pods on one GKE node) burns its block; with manual IPs and no headroom, packets are **silently dropped** — apps see timeouts, not errors. Symptoms in metrics: `nat/dropped_sent_packets_count` with `reason=OUT_OF_RESOURCES` (or `ENDPOINT_INDEPENDENCE_CONFLICT`), `nat/nat_allocation_failed=true`, high `nat/port_usage` vs `nat/allocated_ports`. Fixes, in order: dynamic port allocation, more NAT IPs, raise ports/VM, cut idle timeouts, reduce fanout.

Timeout defaults (tunable): TCP established idle 1200s, TCP transitory 30s, TCP TIME_WAIT 120s, UDP 30s, ICMP 30s.

## Gotchas

- **Logging is off by default.** Enable it (translation, errors, or both) or you'll debug exhaustion blind. Error logs only capture egress TCP/UDP drops, capped ~50–100 entries/s per vCPU.
- **Removing a NAT IP without draining resets its connections.** Use `--nat-external-drain-ip-pool` to retire an IP gracefully.
- **Endpoint-independent mapping (EIM)** helps some P2P/STUN cases but can cause `ENDPOINT_INDEPENDENCE_CONFLICT` drops and is mutually exclusive with dynamic port allocation *and* NAT rules.
- **NAT rules** (CEL match on `destination.ip`/`source.ip`, `inIpRange()`): present a specific source IP to a specific destination. Ranges must not overlap across rules; each rule allocates ports independently — an extra exhaustion axis.
- **VMs with an external IP bypass Cloud NAT** for that interface — the external IP always wins.
- Auto-allocated NAT IPs can change as the gateway scales; use manual IPs whenever a partner allowlists you.
- **Pricing shape**: hourly charge per VM using the gateway **capped at 32 VMs** (a busy gateway costs the same as a 32-VM one), plus a per-GB data-processing charge on all NATed traffic, plus normal external IP and internet egress charges.

## Debugging egress timeouts through NAT

1. Confirm the flow actually uses NAT: VM has no external IP, subnet is covered by the gateway (`--nat-all-subnet-ip-ranges` or listed in custom ranges), destination is external.
2. Check `nat/dropped_sent_packets_count` by `reason`; `OUT_OF_RESOURCES` = port exhaustion, `ENDPOINT_INDEPENDENCE_CONFLICT` = EIM collision.
3. Compare `nat/port_usage` (peak concurrent connections to one endpoint) against `nat/allocated_ports` per VM — size against ~30 days of peaks, not averages.
4. Enable error logging if it wasn't on (it isn't, by default) and look for drop entries.
5. Remember long-idle TCP flows: NAT forgets an established connection after 1200s idle — enable TCP keepalives under that threshold on long-lived connections (DB pools).

## vs siblings

- **Public IPs per VM**: free of NAT charges but every VM is internet-addressable — larger attack surface, IP sprawl, org policies often forbid it. Cloud NAT is the default posture: private VMs, shared egress IPs.
- **Secure Web Proxy**: an explicit L7 proxy that filters egress by URL/hostname/identity. Cloud NAT translates but never inspects — if you need *controlled* or audited egress, SWP (or a firewall + FQDN objects) sits in front; NAT just provides the address.
- **Private Google Access** (VPC feature) covers Google APIs without any NAT; don't size NAT capacity for traffic that never needed it.

## Related

- [[gcp-vpc]] — subnets Cloud NAT serves; Private Google Access for Google APIs
- [[gcp-cloud-router]] — the required control-plane anchor per region/network
- [[gcp-compute-engine]], [[gcp-gke]] — the workloads that egress through it
- [[gcp-cloud-run]] — Direct VPC egress routes serverless traffic through NAT
- [[gcp-secure-web-proxy]] — filtered/audited egress, vs NAT's plain translation
- [[gcp-load-balancing]], [[gcp-iap]] — the inbound story NAT deliberately lacks
- [[gcp-cloud-logging]], [[gcp-cloud-monitoring]] — NAT logs and exhaustion metrics
- [[gcp-cloud-vpn]], [[gcp-interconnect]] — hybrid paths Private NAT translates across

Sources: https://docs.cloud.google.com/nat/docs/overview, https://docs.cloud.google.com/nat/docs/ports-and-addresses, https://docs.cloud.google.com/nat/docs/set-up-manage-network-address-translation, https://docs.cloud.google.com/nat/docs/monitoring, https://docs.cloud.google.com/nat/docs/nat-rules-overview, https://docs.cloud.google.com/nat/docs/tune-nat-configuration, https://cloud.google.com/nat/pricing (fetched 2026-07).
