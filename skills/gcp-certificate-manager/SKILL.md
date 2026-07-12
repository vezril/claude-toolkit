---
name: gcp-certificate-manager
description: "Google Cloud Certificate Manager: TLS certificate lifecycle for Google's edge — Google-managed certs (auto-issued/renewed) vs self-managed uploads, domain authorization via load balancer authz (simple, max 5 SANs, needs traffic already routed) vs DNS authorization (CNAME to authorize.certificatemanager.goog, works pre-cutover, required for wildcards, up to 100 SANs), certificate maps + entries for SNI-based cert selection at scale (exact > wildcard > primary entry), trust configs for mTLS client validation, attach to target HTTPS/SSL proxies, Secure Web Proxy, Media CDN. Use when provisioning HTTPS certs for Cloud Load Balancing, migrating domains without downtime, needing wildcard or >15 certs per proxy, setting up mTLS, or deciding Certificate Manager vs classic compute ssl-certificates."
license: MIT
---

# GCP Certificate Manager

Certificate Manager acquires, deploys, and renews TLS certificates for Google Cloud's edge
products — the successor to classic `compute ssl-certificates` when you need scale (thousands
of certs), wildcards, pre-cutover provisioning, mTLS, or per-hostname cert selection. It serves
Application Load Balancers (global external, classic, regional external/internal, cross-region
internal), proxy Network Load Balancers (target SSL proxies), Secure Web Proxy, and Media CDN.
A 2nd-gen version of the product exists with its own features and pricing; the model below is
1st gen, which is what the deploy guides describe.

## The mental model

```
domain authz (LB authz | DNS authz) ──> certificate (Google-managed | self-managed)
certificate ──> certificate map ENTRY (hostname ──> up to 4 certs)
entries ──> certificate MAP ──> target proxy (--certificate-map)   [or direct attach]
trust config (trust anchors + intermediates + allowlist) ──> ServerTlsPolicy ──> mTLS
```

- **Certificate** is the leaf resource. Google-managed: issued and renewed automatically
  (Google Trust Services, Let's Encrypt, or a private CA via Certificate Authority Service
  through a certificate issuance config). Self-managed: you upload PEM cert + key and own renewal.
- **Domain authorization** proves you control the domain before Google issues a managed cert:
  - **Load balancer authorization** — Google validates via the LB itself. Zero DNS work, but the
    cert only provisions once the domain's traffic already reaches the LB (A/AAAA pointed at its
    IP, ports open). Max 5 SANs, no wildcards, not supported for `ALL_REGIONS` scope certs.
  - **DNS authorization** — you add one CNAME per domain
    (`_acme-challenge.example.com -> <token>.authorize.certificatemanager.goog`). Provisions
    *before* any traffic cutover and is the only route to wildcards: authorize the parent domain,
    then request `example.com,*.example.com`. Up to 100 SANs. Two flavors: `FIXED_RECORD`
    (same CNAME reusable across projects) and `PER_PROJECT_RECORD` (project-scoped record name,
    Google Trust Services only).
- **Certificate map + entries** decouple certs from proxies. Each entry binds a hostname to up
  to 4 certificates; the map attaches to a target HTTPS/SSL proxy. At handshake, SNI selects:
  exact hostname match, else wildcard entry (`*.example.com` matches one label only), else the
  **primary entry** (`--set-primary`); no SNI and no primary = handshake failure. Once a map is
  attached, any directly-attached certificates on the proxy are ignored.
- **Trust config** is the mTLS half: trust stores holding trust anchors (roots), intermediate
  CAs, and allowlisted certificates (always accepted if parseable — even expired). Referenced by
  a `ServerTlsPolicy` on the load balancer to validate *client* certs.

## Canonical shape: managed wildcard cert via DNS authz + map

```bash
gcloud certificate-manager dns-authorizations create example-authz \
    --domain="example.com" --type=FIXED_RECORD
# describe it, then publish the returned CNAME in your DNS zone (Cloud DNS or elsewhere)
gcloud certificate-manager certificates create example-cert \
    --domains="example.com,*.example.com" --dns-authorizations="example-authz"
gcloud certificate-manager maps create example-map
gcloud certificate-manager maps entries create example-entry \
    --map="example-map" --certificates="example-cert" --hostname="example.com"
# (repeat entries per hostname; mark one --set-primary as the no-match fallback)
gcloud compute target-https-proxies create example-proxy \
    --certificate-map="example-map" --url-map="example-um" --global
```

Verify with `certificates describe`: the managed section shows the domain reaching `AUTHORIZED`
and the cert `ACTIVE`. Trust configs import from YAML:
`gcloud certificate-manager trust-configs import CFG --source=file.yaml --location=global`.

## Gotchas

- **Provisioning is asynchronous.** A managed cert must reach `ACTIVE` before the LB can serve
  it — typically minutes after the CNAME is live, but DNS propagation gates it. Stuck for hours
  usually means a wrong/missing CNAME, or (for LB authz) traffic not yet reaching the LB.
- The `_acme-challenge` CNAME must be the **only** record at that DNS name.
- Wildcards match a single subdomain level; `*.example.com` does not cover `a.b.example.com`
  and does not cover the apex — list both `example.com` and `*.example.com` as domains.
- Deleting a DNS authorization requires deleting the certificates that reference it first;
  detach a trust config from its `ServerTlsPolicy` before deleting it.
- Quotas (per project): 1000 Google-managed + 1000 self-managed certs, 100 maps, 5000 map
  entries, 1000 DNS authorizations, 4 certs per entry, 1 map per proxy, 100 certs per proxy,
  100 domains per DNS-authorized cert vs 5 per LB-authorized cert; regional variants are lower
  (100 certs/region). API rate quotas ~300 requests/min.
- Docs note possible slightly higher TLS latency vs classic Compute Engine SSL certs in some
  scenarios — measure if handshake latency is critical.
- **Pricing shape:** billed per certificate per month with a free tier for the first block of
  certificates, then tiered per-cert rates that decrease with volume; check the pricing page
  for current numbers before quoting them.

## vs siblings

- **Classic `compute ssl-certificates`:** fine for a handful of certs on one LB with traffic
  already flowing; no maps, no wildcards on managed certs, no pre-cutover issuance, ~15-cert
  per-proxy ceiling. Certificate Manager is the answer for scale, wildcards, zero-downtime
  migrations, per-hostname selection, and mTLS.
- **Certificate Authority Service (CAS):** a different product — runs your *private* CA and
  signs certs. Certificate Manager can consume CAS as issuer (via a certificate issuance
  config) and can trust private CAs in trust configs, but CAS does not deploy certs to LBs.

## Related

[[gcp-load-balancing]], [[gcp-cloud-dns]], [[gcp-media-cdn]], [[gcp-secure-web-proxy]],
[[gcp-cloud-domains]], [[gcp-cloud-cdn]], [[gcp-iam]], [[cryptography]], [[network-security]]

Sources: https://docs.cloud.google.com/certificate-manager/docs, https://docs.cloud.google.com/certificate-manager/docs/overview, https://docs.cloud.google.com/certificate-manager/docs/dns-authorizations, https://docs.cloud.google.com/certificate-manager/docs/maps, https://docs.cloud.google.com/certificate-manager/docs/certificate-selection-logic, https://docs.cloud.google.com/certificate-manager/docs/quotas, https://docs.cloud.google.com/certificate-manager/docs/deploy-google-managed-dns-auth, https://docs.cloud.google.com/certificate-manager/docs/trust-configs (fetched 2026-07).
