---
name: gcp-load-balancing
description: "Google Cloud Load Balancing — the map of the confusing LB family: Application LB (L7, HTTP/HTTPS; external global/regional, internal regional/cross-region) vs Network LB (L4; proxy for TCP±SSL, passthrough for TCP/UDP/ESP/GRE/ICMP), each external or internal, proxy terminates connections while passthrough preserves client IP with direct-return responses. Component chain: forwarding rule → target proxy → URL map (L7) → backend service → backends (MIGs, zonal/serverless/internet/hybrid/PSC NEGs). Use when choosing a GCP load balancer, wiring gcloud forwarding rules/URL maps/backend services, exposing Cloud Run or GKE behind an ALB, debugging health checks or firewall probe ranges, or attaching Cloud Armor/CDN/certificates."
license: MIT
---

# GCP Cloud Load Balancing

One product family, many SKUs. Every Google Cloud load balancer is a combination of four
axes: **layer** (Application = L7 HTTP(S), Network = L4), **exposure** (external vs internal),
**scope** (global/cross-region vs regional), and **plumbing** (proxy vs passthrough). Learn the
axes and the component chain below, and every docs page slots into place. The whole family was
renamed in 2023 — old tutorials say "HTTP(S) Load Balancing" (now Application LB), "TCP/SSL
Proxy" (now external proxy Network LB), and "Network Load Balancing" (now external passthrough
Network LB). Translate on sight.

## The family map

| Load balancer | Deployment | Traffic | Scheme | Pick this when |
|---|---|---|---|---|
| **Application LB** (L7, always proxy) | Global external | HTTP/HTTPS | `EXTERNAL_MANAGED` | Internet-facing web/API, multi-region backends, one anycast IP (Premium tier) |
| | Regional external | HTTP/HTTPS | `EXTERNAL_MANAGED` | Internet-facing but traffic must stay in-region, or Standard tier |
| | Regional internal | HTTP/HTTPS | `INTERNAL_MANAGED` | Private L7 routing inside the VPC, single region |
| | Cross-region internal | HTTP/HTTPS | `INTERNAL_MANAGED` | Private L7 across regions (global access from VPC/hybrid) |
| **Proxy Network LB** (L4, terminates TCP) | Global external | TCP ± SSL offload | `EXTERNAL_MANAGED` | Non-HTTP TCP from the internet, global anycast, optional TLS termination |
| | Regional external | TCP | `EXTERNAL_MANAGED` | Non-HTTP TCP, regional, Standard tier OK |
| | Regional / cross-region internal | TCP | `INTERNAL_MANAGED` | Private TCP proxying, incl. to hybrid backends |
| **Passthrough Network LB** (L4, no proxy) | External (regional only) | TCP, UDP, ESP, GRE, ICMP(v6) | `EXTERNAL` | UDP/exotic protocols, or client source IP must reach the VM unchanged |
| | Internal (regional only) | TCP, UDP, ICMP, SCTP, ESP, AH, GRE | `INTERNAL` | Classic internal L4 VIP; also next-hop for routes/NVAs |

Decision order from the docs: traffic type first (HTTP(S) → Application; TCP-with-proxying →
proxy NLB; anything else or IP-preservation → passthrough NLB), then external/internal, then
global/regional. Global external LBs require **Premium** Network Service Tier; regional
external ones work in Standard. Passthrough LBs are regional, period. The **classic**
Application LB is the pre-Envoy generation (`EXTERNAL` scheme, global only in Premium) — still
supported, but new builds should use the global external ALB.

## The component chain

Every LB is the same Lego chain; this vocabulary unlocks every docs page:

```
forwarding rule (IP:port, scheme) → target proxy (HTTP/HTTPS/TCP/SSL; L7 terminates TLS here)
  → URL map (L7 only: host/path/header routing) → backend service (protocol, health check,
    affinity, timeouts, balancing mode) → backends
```

- **Backends**: instance groups (MIGs/unmanaged), zonal NEGs (`GCE_VM_IP_PORT`/`GCE_VM_IP`),
  **serverless NEGs** (Cloud Run, App Engine, Cloud Functions gen1, API Gateway preview),
  internet NEGs (external origins), hybrid NEGs (on-prem), Private Service Connect NEGs.
  You cannot mix instance groups and zonal NEGs in one backend service.
- **Balancing modes** on the backend service: `UTILIZATION`, `RATE`, `CONNECTION` (plus
  custom-metrics variants). Ignored for serverless NEGs.
- Passthrough NLBs skip the proxy/URL-map stages: forwarding rule → regional backend service →
  backends, and responses go **directly from VM to client** (direct server return).
- Envoy-based regional/internal LBs additionally need a **proxy-only subnet** per region.

## Minimal global external ALB (gcloud shape)

Order matters — build back-to-front:

```sh
gcloud compute health-checks create http http-basic-check --port 80
gcloud compute backend-services create web-backend-service \
    --load-balancing-scheme=EXTERNAL_MANAGED --protocol=HTTP \
    --port-name=http --health-checks=http-basic-check --global
gcloud compute backend-services add-backend web-backend-service \
    --instance-group=lb-backend-example --instance-group-zone=ZONE --global
gcloud compute url-maps create web-map-http --default-service web-backend-service
gcloud compute target-http-proxies create http-lb-proxy --url-map=web-map-http
gcloud compute addresses create lb-ipv4-1 --ip-version=IPV4 --network-tier=PREMIUM --global
gcloud compute forwarding-rules create http-content-rule \
    --load-balancing-scheme=EXTERNAL_MANAGED --address=lb-ipv4-1 \
    --target-http-proxy=http-lb-proxy --ports=80 --global
```

HTTPS swaps in `target-https-proxies` with `--ssl-certificates` (or a Certificate Manager
map). Classic ALB uses `--load-balancing-scheme=EXTERNAL` instead of `EXTERNAL_MANAGED` —
mismatched schemes between forwarding rule and backend service is a classic wiring error.
Cloud Run backend = create a serverless NEG in the service's region, add it as the backend.

## Traffic management (URL maps)

- **Host rules → path matcher → path rules / route rules.** Route rules are priority-ordered
  (0 = highest) and match on path, headers (`user-agent:Mobile`), and query params.
- **Actions**: weighted traffic splitting across backend services (weights 0–1000; canaries),
  URL rewrites (host and path), 3xx redirects, request/response header transforms, retries,
  per-route timeouts, fault injection (delay/abort), CORS policy, traffic mirroring (MIG and
  zonal/hybrid NEG backends only).
- **Backend-service level**: session affinity (client-IP, generated cookie, header), locality
  policies (`ROUND_ROBIN`, `LEAST_REQUEST`, `RING_HASH`, `MAGLEV`), connection draining,
  outlier detection. Feature support varies by LB mode — the docs matrix per feature is
  authoritative; classic ALB has the thinnest set.

## Gotchas

- **Health-check firewall rules are on you.** Probes come from Google ranges that must be
  allowed by ingress firewall: `35.191.0.0/16` + `130.211.0.0/22` for GFE/Envoy-based LBs
  (ALBs, proxy NLBs); external passthrough NLBs also use `209.85.152.0/22` and
  `209.85.204.0/22`. "Backend unhealthy but serves fine directly" is almost always this.
- **Proxy LBs replace the client IP.** Backends see the proxy; recover the caller from
  `X-Forwarded-For` (format: `client-IP, LB-IP`, appended after any inbound values, which are
  spoofable). Passthrough NLBs deliver the original packet — client IP intact, no header
  games — which is exactly why UDP/ESP/GRE and NVA patterns live there.
- **Serverless NEG limits**: one per region on a global backend service (one total on
  regional), same region/project as the Cloud Run service, no health checks (use outlier
  detection), no mixing with other backend types, backend timeout ignored.
- **Global = Premium tier.** Dropping to Standard tier silently forces you into regional
  variants; classic ALB in Standard becomes effectively regional.
- **Scheme mismatches** (`EXTERNAL` vs `EXTERNAL_MANAGED`) and missing **proxy-only subnets**
  (regional Envoy LBs) are the two most common gcloud setup failures.
- **Pricing shape**: hourly charge per forwarding rule (first five billed as a bundle, then
  per-rule) + per-GB data processed (inbound and outbound), plus normal egress at your
  network tier. Global anycast itself isn't a separate SKU — data processing is where cost
  scales.

## Related

[[gcp-cloud-cdn]] and Cloud Armor attach at the backend service of external ALBs;
[[gcp-certificate-manager]] supplies certs to target HTTPS proxies. [[gcp-vpc]] for subnets,
proxy-only subnets, and firewall rules; [[gcp-cloud-run]] via serverless NEGs; [[gcp-gke]]
Gateway/Ingress provisions these LBs under the hood; [[gcp-compute-engine]] MIGs are the
canonical backend; [[gcp-cloud-dns]] for pointing names at the VIP; [[gcp-media-cdn]] and
[[gcp-iap]] for the delivery/auth layers; [[network-engineering]] for the L4/L7 fundamentals.

Sources: https://docs.cloud.google.com/load-balancing/docs,
https://docs.cloud.google.com/load-balancing/docs/choosing-load-balancer,
https://docs.cloud.google.com/load-balancing/docs/https,
https://docs.cloud.google.com/load-balancing/docs/backend-service,
https://docs.cloud.google.com/load-balancing/docs/health-check-concepts,
https://docs.cloud.google.com/load-balancing/docs/negs/serverless-neg-concepts,
https://docs.cloud.google.com/load-balancing/docs/https/ext-http-lb-simple,
https://docs.cloud.google.com/load-balancing/docs/https/traffic-management-global,
https://cloud.google.com/vpc/network-pricing (fetched 2026-07).
