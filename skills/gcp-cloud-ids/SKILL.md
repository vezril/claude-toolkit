---
name: gcp-cloud-ids
description: "Google Cloud IDS: managed network intrusion DETECTION powered by Palo Alto Networks signatures — zonal IDS endpoints receive traffic copied by Packet Mirroring policies, classify threats (malware, spyware, C2, vulnerability exploits) at five severities, and write alerts to Cloud Logging. Detection only: it never blocks; response is on you (Cloud NGFW Enterprise IPS is the inline-prevention sibling). Use when setting up threat detection for a VPC, wiring IDS endpoints + mirroring policies, tuning severity/threat exceptions, routing threat logs, meeting PCI 11.4 / HIPAA IDS requirements, or choosing between Cloud IDS and Cloud NGFW."
license: MIT
---

# Cloud IDS

Managed intrusion *detection* for VPC traffic, powered by Palo Alto Networks threat
technologies (App-ID, vulnerability and anti-spyware signatures, updated daily). You
deploy **IDS endpoints**, point **Packet Mirroring policies** at them, and threat
alerts land in Cloud Logging. Status (as of 2026-07): GA, no deprecation notice —
but Cloud NGFW Enterprise now offers *inline* intrusion prevention built on the same
Palo Alto signature stack, so new designs should consciously pick detect-only vs prevent.

## The mental model

- **IDS endpoint** — a zonal resource (Google-managed Palo Alto VMs behind private
  services access peering) that can inspect mirrored traffic from *any zone in its
  region*. ~5 Gbps sustained inspection capacity each (spikes to ~17 Gbps); size one
  endpoint per 5 Gbps of throughput.
- **Packet Mirroring is the feed.** Cloud IDS sees only what your mirroring policies
  copy to it — by subnet, network tag, or instance list, optionally filtered by
  protocol/CIDR. No policy, no visibility. This covers both north-south and
  east-west (VM-to-VM lateral movement) if you scope the policies that way.
- **Out-of-band, therefore detection-only.** The endpoint inspects a *copy*; the real
  packets were already delivered. Cloud IDS alerts — it never drops, resets, or
  quarantines. Response (firewall rule, NGFW policy, incident workflow) is on you.
- **Alerts are logs.** Threats write to Cloud Logging as
  `ids.googleapis.com%2Fthreat` (resource type `ids.googleapis.com/Endpoint`), with
  fields like threat_id, alert_severity, source/destination IP:port, application,
  cves. Traffic logs (session metadata) also available. Console has an "IDS Threats"
  page; anything else (SIEM, Pub/Sub, alerting) is standard log routing.
- **Five severities** — CRITICAL / HIGH / MEDIUM / LOW / INFORMATIONAL. The endpoint's
  minimum severity is its alert threshold; per-threat-ID exceptions (max 99/endpoint)
  suppress noisy signatures.

## Setup shape

One-time per VPC: private services access (the endpoint VMs live in a peered producer network).

```bash
gcloud services enable servicenetworking.googleapis.com ids.googleapis.com
gcloud compute addresses create ids-range --global --purpose=VPC_PEERING \
    --addresses=192.168.0.0 --prefix-length=16 --network=VPC_NETWORK
gcloud services vpc-peerings connect --service=servicenetworking.googleapis.com \
    --ranges=ids-range --network=VPC_NETWORK
```

Then endpoint + mirroring policy (the pair is the unit of coverage):

```bash
gcloud ids endpoints create my-endpoint --network=VPC_NETWORK \
    --zone=ZONE --severity=MEDIUM   # threshold: MEDIUM and up alert
gcloud ids endpoints describe my-endpoint   # grab endpointForwardingRule
gcloud compute packet-mirrorings create my-policy --region=REGION \
    --collector-ilb=ENDPOINT_FORWARDING_RULE --network=VPC_NETWORK \
    --mirrored-subnets=SUBNET   # or --mirrored-tags / --mirrored-instances
```

Tune later: `gcloud ids endpoints update my-endpoint --threat-exceptions=ID1,ID2`.
IAM: `roles/ids.admin` / `ids.viewer`, plus `roles/compute.packetMirroringUser` to
attach policies and `roles/logging.viewer` to read alerts.

## Gotchas

- **Pricing shape: endpoint-hours + inspected GB.** ~$1.50/hr per endpoint (burns
  whether or not traffic flows — ~$1,100/mo idle) plus ~$0.07/GB inspected. The
  per-GB rate *includes* Packet Mirroring (no separate mirroring charge), but
  cross-zone data transfer for mirrored traffic is priced under VPC network rates.
- **Coverage is only what you mirror.** A forgotten subnet or an instance without the
  mirrored tag is invisible. Audit mirroring policies alongside firewall rules.
- **Endpoint is zonal, policies are regional.** One endpoint can collect from the
  whole region, but multi-region coverage means endpoints (and cost) per region.
- **Cloud NGFW L7 inspection wins conflicts.** Where an NGFW firewall-endpoint L7
  inspection policy overlaps a mirroring policy, NGFW takes priority and traffic is
  *not* mirrored to Cloud IDS — running both on the same paths silently blinds IDS.
- **Encrypted payloads limit signature depth.** Cloud IDS inspects mirrored packets
  as-is; it has no TLS interception (Cloud NGFW Enterprise does).
- **C2 detection is egress-based** — anti-spyware signatures flag infected hosts when
  traffic *leaves* toward known C2 infrastructure, so don't scope mirroring to
  ingress only.
- Multiple endpoints in one VPC reuse the peering connection but each consumes a new
  subnet from your reserved range — size the /16 allocation accordingly.

## vs siblings

- **Cloud NGFW (firewall rules / Enterprise IPS)** — enforcement, inline. NGFW
  Enterprise adds prevention (block/alert per security profile) using the same Palo
  Alto signatures, plus TLS inspection, via zonal *firewall endpoints* with packet
  intercept. Cloud IDS = passive copy + alert. As of 2026-07 both are GA; pick IDS
  for zero-risk-to-traffic monitoring/compliance, NGFW Enterprise to actually block.
- **Secure Web Proxy** — explicit egress proxy for web traffic policy; a control
  point, not a detector.
- **VPC Service Controls** — perimeter against data exfiltration via Google APIs;
  orthogonal to packet-level threat detection.

## Related

[[gcp-vpc]] (Packet Mirroring, private services access), [[gcp-cloud-logging]]
(threat/traffic logs, routing to SIEM), [[gcp-cloud-monitoring]] (alerting on threat
log entries), [[gcp-vpc-service-controls]], [[gcp-secure-web-proxy]],
[[gcp-load-balancing]] (collector ILB mechanics), [[gcp-iam]], [[network-security]]

Sources: https://docs.cloud.google.com/intrusion-detection-system/docs,
https://docs.cloud.google.com/intrusion-detection-system/docs/overview,
https://docs.cloud.google.com/intrusion-detection-system/docs/configuring-ids,
https://docs.cloud.google.com/intrusion-detection-system/docs/logging,
https://cloud.google.com/intrusion-detection-system/pricing,
https://docs.cloud.google.com/firewall/docs/about-intrusion-prevention (fetched 2026-07).
