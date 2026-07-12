---
name: gcp-secure-web-proxy
description: "Google Cloud Secure Web Proxy (SWP): managed egress filtering proxy for HTTP/S web traffic — Gateway Security Policies with CEL rules (SessionMatcher/ApplicationMatcher) matching source identity (secure tags, service accounts, IPs) and destinations (hostnames, URL lists), optional TLS inspection via Certificate Authority Service, explicit-proxy / next-hop / Private Service Connect deployment modes. Use when controlling or auditing outbound web traffic from VMs/GKE, allowlisting egress destinations by hostname or URL, choosing SWP vs Cloud NAT vs firewall FQDN rules, setting up TLS inspection, or debugging blocked egress through a proxy gateway."
license: MIT
---

# GCP Secure Web Proxy

Controlled egress for web traffic — the complement to Cloud NAT's open egress. Cloud NAT gets
your private VMs *to* the internet; Secure Web Proxy (SWP) decides *which* web destinations
they may reach, logs every transaction, and can crack open TLS to inspect it. Default posture
is deny-all: nothing egresses through the gateway until a rule allows it.

## The mental model

A managed Envoy proxy instance (a **gateway**) deployed in your VPC region, fronted by an
internal IP:port. Attached to it: a **GatewaySecurityPolicy** containing ordered
**GatewaySecurityPolicyRules**, each with a priority, an ALLOW/DENY action, and CEL matchers:

- **`sessionMatcher`** — evaluated per connection, pre-decryption: `host()` (from SNI/CONNECT),
  `source.ip`, `destination.port`, `source.matchTag('tagValues/…')`,
  `source.matchServiceAccount('sa@…')`, `inIpRange(...)`, `inUrlList(host(), 'projects/…/urlLists/…')`.
- **`applicationMatcher`** — evaluated per HTTP request: `request.method`, `request.path`,
  `request.url()`, `request.headers['…']` (lowercase keys), plus everything sessionMatcher sees.
  For HTTPS, request-level attributes are only visible when TLS inspection is enabled on the rule.

So: *policy → rules → (who = tags/service accounts/IP) + (where = hostnames/URLs via CEL)*.
Optionally a **TlsInspectionPolicy** hangs off the security policy, minting short-lived
server certs from a Certificate Authority Service (CAS) CA pool so the proxy can MITM and
inspect HTTPS. Everything is regional; traffic is logged to Cloud Logging.

## Deployment modes

1. **Explicit proxy** (default, `EXPLICIT_ROUTING_MODE`) — clients set `http_proxy`/`https_proxy`
   (or app-level proxy config) to the gateway's IP:port; HTTPS goes through `CONNECT`.
2. **Next hop** (`NEXT_HOP_ROUTING_MODE`, "SWP as next hop") — no client config; a static route
   with `--next-hop-ilb` pointing at the gateway IP (priority lower than the default internet
   route, scoped by network tags) steers traffic in. Gateway can listen on all ports (1–65535).
   One SWPaNH instance per VPC per region; same-region traffic only, cross-region is dropped.
3. **Private Service Connect service attachment** — publish one central SWP to many consumer
   VPCs in a multi-VPC/host-project hub.

## Setup shape (explicit proxy)

1. Enable APIs: `compute`, `certificatemanager`, `networkservices`, `networksecurity`
   (+ `privateca` for TLS inspection).
2. Create a **proxy-only subnet** (purpose `REGIONAL_MANAGED_PROXY`, /23 recommended) in each
   region — Envoy needs it even though the gateway resource never references it.
3. Optional: a Certificate Manager cert if clients will speak HTTPS *to the proxy itself*.
4. Create the `GatewaySecurityPolicy`, add rules (`gcloud network-security gateway-security-policies
   rules create … --session-matcher="host() == 'github.com'" --basic-profile=ALLOW --priority=…`).
5. Create the gateway: `gcloud network-services gateways create --type=SECURE_WEB_GATEWAY
   --addresses=… --ports=443 --gateway-security-policy=…`.
6. Point clients at it; watch decisions in Cloud Logging.

### TLS inspection add-on

CAS CA pool (DevOps tier) → subordinate CA signed by your root → grant
`service-PROJECT_NUMBER@gcp-sa-networksecurity.iam.gserviceaccount.com` the
`roles/privateca.certificateManager` role on the pool → create `TlsInspectionPolicy`
referencing the pool → attach it to the gateway security policy → set
`--tls-inspection-enable` on the specific rules to decrypt. Inspection applies only to traffic
matching that rule's sessionMatcher. Leaf certs are short-lived and can't be revoked via CAS.

## Gotchas

- **Explicit proxy needs client cooperation.** Env vars don't cover everything — static
  binaries, distroless containers, and SDKs with their own proxy handling each need explicit
  config. Next-hop mode exists precisely to avoid this, at the cost of one-per-VPC-region.
- **TLS inspection = trust distribution.** Every client must trust the issuing CA chain or
  every HTTPS call fails certificate validation. Plan OS/container trust-store rollout first.
- **Idle gateways bill.** ~$1.25/gateway-hour runs 24/7 whether or not traffic flows
  (~$900/month/gateway), plus ~$0.018/GB processed; TLS inspection adds CAS per-certificate
  fees. Delete gateways you're not using. (Shape, not gospel — check current pricing.)
- **Next hop grabs everything the route matches** — including OS updates and background
  agent traffic. Non-HTTP(S)/TCP traffic and cross-region flows are dropped, not passed.
- IPv4 only; no HTTP/3. Regional service — deploy per region.
- Limits shape: 10 policies and 10 URL lists per project-region, 500 rules/policy,
  2,500 entries/URL list, regexes are RE2 and capped (5 regex matchers per policy).

## vs siblings

- **Cloud NAT** — open egress plumbing: address translation, no filtering, no L7 visibility.
  SWP is the filtered path; many architectures run SWP *instead of* NAT for web traffic so
  the proxy is the only way out.
- **Firewall FQDN rules / policies** — L3/L4 allow/deny at connection level with DNS-based
  FQDN matching; no URL paths, methods, headers, or TLS inspection, but covers non-HTTP too.
- **Cloud IDS** — detection, not control: mirrors traffic and alerts; SWP sits inline and blocks.
- **VPC Service Controls** — perimeter for *Google API* access; SWP governs general internet
  egress. Complementary, not overlapping.

## Related

[[gcp-vpc]], [[gcp-cloud-nat]], [[gcp-cloud-ids]], [[gcp-vpc-service-controls]],
[[gcp-certificate-manager]], [[gcp-load-balancing]], [[gcp-cloud-dns]], [[gcp-iam]],
[[gcp-cloud-logging]], [[gcp-compute-engine]], [[gcp-gke]], [[network-security]]

Sources: https://docs.cloud.google.com/secure-web-proxy/docs, /overview, /initial-setup-steps,
/enable-tls-inspection, /cel-matcher-language-reference, /deploy-next-hop, /quotas,
https://cloud.google.com/secure-web-proxy/pricing (fetched 2026-07).
