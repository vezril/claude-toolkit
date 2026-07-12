---
name: gcp-cloud-dns
description: "Google Cloud DNS — the managed, anycast-served authoritative DNS service. Covers public zones (internet-facing) vs private zones (bound to VPC networks via --networks), the VPC name resolution order (metadata server 169.254.169.254 → outbound server policy → response policies → private/forwarding/peering zones by longest suffix → Compute Engine internal DNS → public DNS), record-set management (gcloud dns record-sets create/update and the transaction flow), DNSSEC (--dnssec-state and the DS-record chain to the registrar), hybrid DNS (inbound/outbound server policies, forwarding zones, the 35.199.192.0/19 source range), peering zones and cross-project binding, routing policies (geolocation, weighted round robin, failover with health checks), split-horizon patterns, and pricing shape (per zone-month + per million queries). Also answers 'gcloud dns', 'managed zone', 'Cloud DNS private zone'. Use when designing or debugging DNS on Google Cloud, wiring hybrid on-prem↔cloud resolution, choosing forwarding vs peering zones, enabling DNSSEC, steering traffic with geo/weighted/failover records, or deciding between Cloud DNS and Cloud Domains."
license: MIT
---

# GCP Cloud DNS

Cloud DNS is Google Cloud's managed authoritative DNS: it publishes your zones from Google's global anycast name-server fleet (public zones) or answers only inside VPC networks you authorize (private zones), with no name servers for you to run. It is *hosting and resolution*, not registration — you buy the domain elsewhere (Cloud Domains or any registrar) and delegate it here. Beyond plain record serving it is also the control plane for hybrid DNS (forwarding to on-prem, inbound resolution from on-prem) and for DNS-level traffic steering (geo, weighted, failover routing policies).

## The mental model

- **Two kinds of zones, one API.** A **public zone** is visible to the internet and served over anycast from the nearest edge. A **private zone** is visible only from the VPC networks listed in `--networks`, and only for queries originating inside them. Same record model, opposite audiences — split-horizon DNS is literally a public zone and a private zone with the same `--dns-name`.
- **Inside a VPC, the metadata server is the resolver.** VMs point at `169.254.169.254`; Cloud DNS resolves in a fixed order: (1) if an **outbound server policy** exists, *every* query goes to its alternate name servers — full stop; otherwise (2) **response policies** (RPZ-style overrides), (3) private, forwarding, and peering zones by **longest suffix match**, (4) Compute Engine internal DNS, (5) public DNS. A matching private zone is authoritative: if the zone matches but the record doesn't exist, you get NXDOMAIN even if the public internet has an answer. That shadowing is the #1 "why can't my VM resolve X" cause.
- **Forwarding and peering zones stitch hybrid DNS.** A **forwarding zone** holds no records — it names forwarding targets (on-prem or in-VPC resolvers) for a suffix. A **peering zone** delegates a suffix to *another VPC network's* resolution order (one-way, consumer → producer, at most one transitive hop). Server policies are the network-wide counterpart: **inbound** policies create entry-point IPs in each subnet so on-prem can query your private zones; **outbound** policies redirect the whole VPC to alternate name servers.
- **Records are rrsets; changes are atomic.** You manage record *sets* (name + type → rrdatas + TTL). The modern `record-sets create/update/delete` verbs handle single sets; the `transaction start/add/remove/execute` flow batches multiple changes into one atomic change set.
- **Routing policies replace static rrdatas with logic.** A record set can carry a geolocation, weighted-round-robin, or failover policy instead of fixed data — evaluated per query, optionally health-checked against internal load balancers.

## Core how-to

```sh
gcloud services enable dns.googleapis.com

# Public zone (internet-facing; note the trailing dot on --dns-name)
gcloud dns managed-zones create prod-public \
    --description="public example.com" --dns-name=example.com. --visibility=public

# Private zone bound to VPCs
gcloud dns managed-zones create prod-private \
    --description="internal example.com" --dns-name=example.com. \
    --visibility=private --networks=vpc-prod,vpc-shared
```

Record sets, modern verbs:

```sh
gcloud dns record-sets create test.example.com. \
    --zone=prod-public --type=A --ttl=300 --rrdatas=198.51.100.5
gcloud dns record-sets update test.example.com. \
    --zone=prod-public --type=A --ttl=30 --rrdatas=198.51.100.6
gcloud dns record-sets list --zone=prod-public
gcloud dns record-sets delete test.example.com. --type=A --zone=prod-public
```

Atomic multi-record change (older transaction flow, still supported):

```sh
gcloud dns record-sets transaction start --zone=prod-public
gcloud dns record-sets transaction add 198.51.100.7 \
    --name=www.example.com. --ttl=300 --type=A --zone=prod-public
gcloud dns record-sets transaction execute --zone=prod-public
```

DNSSEC on/off is a zone property: `gcloud dns managed-zones update prod-public --dnssec-state=on` (states: `off`, `on`, `transfer`). After enabling, fetch the DS record and publish it at your **registrar** — signing without the DS chain does nothing for validators.

## Hybrid DNS (on-prem ↔ cloud)

- **Cloud → on-prem:** create a forwarding zone for the corporate suffix; targets get queried from **35.199.192.0/19** (standard routing, internal targets) — allow that range through on-prem firewalls, make the DNS servers accept it, and advertise a return route via Cloud Router. **Private routing** forces target traffic through the VPC (VPN/Interconnect) regardless of IP class; standard routing sends RFC 1918 targets through the VPC and internet-routable targets over the internet.
- **On-prem → cloud:** create an **inbound server policy** on the VPC; Cloud DNS allocates an entry-point address in each subnet, and on-prem resolvers forward the cloud suffix there, gaining access to private zones and internal DNS names.
- **Multi-VPC:** outbound forwarding **cannot traverse VPC Network Peering** — use DNS **peering zones** to let a consumer VPC resolve through a hub/producer VPC (which may itself hold the forwarding zone). One transitive hop max.
- **Shared VPC:** either create zones in the host project, or use **cross-project binding** — a service project owns its zone but binds it to the host project's VPC, keeping team autonomy without burning the peering hop.
- **Naming strategy (docs-recommended):** keep two authoritative systems with disjoint suffixes — e.g. `corp.example.com` on-prem, `gcp.example.com` in Cloud DNS — rather than one domain mastered in both places.

## Specialized zone and policy types

- **Reverse lookup zones** — managed private zones that serve PTR records for non-RFC-1918 address space inside the VPC.
- **Service Directory zones** — expose a Service Directory namespace over DNS so VPC clients discover registered services with plain lookups.
- **Response policies** — not zones; RPZ-style rule sets attached to a VPC that rewrite or block answers by query name before any zone is consulted. Managed separately from managed zones.
- **DNS64** — synthesizes IPv6 answers from IPv4-only destinations using the well-known prefix `64:ff9b::/96`, for IPv6-only workloads reaching IPv4 services.
- All three policy families — server, response, routing — can be active on the same network simultaneously; they hook into different steps of the resolution order.

## Routing policies (geo / wrr / failover)

- **Weighted round robin (WRR):** each policy item has a weight 0–1000; answers are returned proportionally. Canarying and traffic splitting.
- **Geolocation (GEO):** answers by nearest Google Cloud region to the query source (public zones use resolver IP / EDNS Client Subnet; private zones use the querying VM's region). Optional **geofencing** pins answers to the matched region instead of failing over to the next-closest when endpoints are unhealthy.
- **Failover:** an active set and a backup set; backups are served only "when all IP addresses in the active set become unhealthy."
- **Health checks** integrate with internal passthrough/proxy Network Load Balancers and internal Application Load Balancers, plus direct external endpoints in public zones. Health-checkable types are A/AAAA; CNAME, MX, SRV, TXT can carry routing policies but without health checks.
- **Restrictions:** you cannot combine WRR and GEO in one record set; with DNSSEC enabled, a health-checked policy item may contain only a single IP address.

## Gotchas

- **DNSSEC is a chain, not a switch.** Enable in Cloud DNS *and* publish the DS at the registrar (registrar and TLD must both support it). Reverse order to tear down: remove/deactivate DS at the registrar first, *then* `--dnssec-state=off` — dropping signing while the DS is live makes the whole zone bogus for validating resolvers.
- **Private-zone shadowing:** a private zone matching the suffix answers authoritatively — missing records return NXDOMAIN, never falling through to public DNS. Check the resolution order before blaming the record.
- **The trailing dot matters:** `--dns-name=example.com.` — zone and record names are FQDNs.
- **Forgetting 35.199.192.0/19** on the on-prem firewall (or the return route in Cloud Router) is the classic silent-timeout of outbound forwarding.
- **Peering ≠ VPC peering:** DNS peering zones are a Cloud DNS construct, work without VPC Network Peering, and are the only way DNS resolution crosses VPC boundaries (outbound forwarding won't ride a VPC peering link).
- **Pricing shape:** per managed zone per month (tiered — cheaper per zone as the count grows) plus per million queries (tiered by volume); queries answered by routing policies or forwarded to on-prem bill at higher per-million rates. Zones are cheap; query volume and policy-evaluated queries are what scale the bill.

## When to use vs siblings

- **Cloud DNS** — hosting and serving zones (public or VPC-private), hybrid resolution, DNS traffic steering. It never registers domains.
- **Cloud Domains** — registration and renewal of the domain name itself; typically configured to delegate to a Cloud DNS public zone. Registration vs hosting — most production setups use both.
- **Google Public DNS (8.8.8.8)** — a public *recursive* resolver for anyone; unrelated to hosting your zones.
- **Load balancing vs DNS routing policies:** a global external Application Load Balancer gives one anycast IP with instant, connection-aware failover; DNS-level geo/failover steering is coarser (TTL-bound, resolver-dependent) but works for non-HTTP protocols and multi-entry-point topologies.

## Related

[[gcp-cloud-domains]] — registration vs hosting split above. Network fabric: [[gcp-vpc]] (private zone binding, Shared VPC), [[gcp-cloud-vpn]], [[gcp-interconnect]], [[gcp-cloud-router]] (hybrid forwarding path and return routes), [[gcp-cloud-nat]]. Traffic: [[gcp-load-balancing]] (health-checked routing-policy targets and the steering alternative), [[gcp-cloud-cdn]], [[gcp-certificate-manager]]. Control plane: [[gcp-iam]], [[gcp-cloud-logging]] (DNS query logging), [[gcp-cloud-monitoring]]. Practice: [[terraform]], [[network-engineering]].

Sources: https://docs.cloud.google.com/dns/docs/overview, https://docs.cloud.google.com/dns/docs/zones, https://docs.cloud.google.com/dns/docs/zones/zones-overview, https://docs.cloud.google.com/dns/docs/records, https://docs.cloud.google.com/dns/docs/dnssec, https://docs.cloud.google.com/dns/docs/best-practices, https://docs.cloud.google.com/dns/docs/policies-overview, https://docs.cloud.google.com/dns/docs/routing-policies-overview, https://docs.cloud.google.com/dns/docs/vpc-name-res-order, https://cloud.google.com/dns/pricing (fetched 2026-07).
