---
name: gcp-cloud-domains
description: "Google Cloud Domains — the domain-registrar surface inside GCP: search, register, renew, and transfer-out domains via console/gcloud/API, with Squarespace as the registrar of record since its September 7, 2023 acquisition of Google Domains (status as documented 2026-07: still operational for new registrations and management, but transfers INTO Cloud Domains, Google Domains import/export, domain/email forwarding, and dynamic DNS were shut down January 22, 2024, and Google Domains free DNS is retired). Covers the registrar-vs-DNS-host split (Cloud DNS or custom name servers do the hosting), contact-privacy tiers (REDACTED_CONTACT_DATA replacing PRIVATE_CONTACT_DATA), DNSSEC, transfer locks and EPP auth codes (.uk push transfers), auto-renew rules (enable 15 days pre-expiry), the 30-day post-expiration renewal window (72 h wait for ccTLDs), and yearly billing to the Cloud Billing account. Use when registering or managing a domain from a GCP project, wiring a Cloud Domains registration to a Cloud DNS zone, transferring a domain out, recovering an expired registration, untangling the Squarespace/Google Domains situation, or deciding whether Cloud Domains is still the right registrar."
license: MIT
---

# GCP Cloud Domains

Cloud Domains is the domain **registrar** built into Google Cloud: search availability, register, renew, and manage domains from the console, `gcloud domains`, or the Cloud Domains API, with the registration billed yearly to your Cloud Billing account and owned by your project like any other resource. Honesty first, because this product's history is its biggest gotcha: **on September 7, 2023 Squarespace acquired all domain registrations and customer accounts from Google Domains**. As of the docs in July 2026, Cloud Domains itself is *still operational* — you can register new domains and keep managing existing ones through GCP — but Squarespace is the registrar of record (new registrations require accepting Squarespace's ToS), the Google Domains UI is gone, and a slab of Google-Domains-backed features was deprecated October 19, 2023 and shut down **January 22, 2024**: transfers **into** Cloud Domains, import/export to and from Google Domains, domain and email forwarding, and dynamic DNS. Google Domains as a free DNS provider is retired. If someone asks "should I move my registrar into GCP?" — you can, but only by *registering new* domains there; you cannot transfer an existing domain in.

## The mental model

- **Registrar and DNS host are two different jobs, split across two products.** Cloud Domains holds the *registration* — ownership, contacts, name-server delegation, renewal, transfer lock. Actually *answering DNS queries* is Cloud DNS's job (or any third-party provider's). At registration you pick one of two DNS configurations: a **Cloud DNS zone** (recommended; billed separately per Cloud DNS pricing) or **custom name servers** pointing at an external provider. The formerly free Google Domains DNS option is retired and unavailable to new registrations.
- **A registration is a GCP resource.** It lives in a project, is guarded by IAM (`roles/domains.admin`, or fine-grained permissions like `domains.registrations.configureManagement`), appears in `gcloud domains registrations list`, and the slow actions (register, renew, transfer) are long-running operations you poll.
- **Squarespace is underneath.** The acquisition made Squarespace the registrar of record; GCP remains your management plane. During migration the old `PRIVATE_CONTACT_DATA` privacy setting was converted to `REDACTED_CONTACT_DATA`.
- **The pipes flow one way now.** Out: transferring to another registrar is fully supported. In: shut down January 22, 2024. A plan like "we'll consolidate all our domains into GCP" is unfixable except by registering fresh names.

## Core how-to

Enable the API, then search and register:

```sh
gcloud services enable domains.googleapis.com

gcloud domains registrations search-domains example        # availability + price
gcloud domains registrations get-register-parameters example.com
gcloud domains registrations register example.com \
  --contact-data-from-file=contacts.yaml \
  --contact-privacy=redacted-contact-data \
  --cloud-dns-zone=example-zone \
  --yearly-price="12.00 USD"
```

Registration prerequisites: a project with billing enabled, the Cloud Domains API on, and acceptance of the Squarespace ToS. Choose the DNS config (`--cloud-dns-zone` or custom name servers) and privacy tier at register time. Then **verify the registrant email within 15 days or the domain goes inactive**. Premium domains are not supported. Since August 2025, per ICANN's Registration Data Policy, gTLDs no longer require separate admin/technical contacts.

Renewal and transfer-out management:

```sh
gcloud domains registrations configure management example.com \
  --transfer-lock-state=unlocked                            # step 1 of transfer-out
gcloud domains registrations get-authorization-code example.com   # EPP code
gcloud domains registrations renew-domain example.com \
  --yearly-price="12.00 USD"                                # within 30 days of expiry
```

## Flows and policies

**Contact privacy** — three tiers where the TLD allows:

- **Privacy protection / redacted** (`REDACTED_CONTACT_DATA`): proxy or redacted contact data in WHOIS/RDAP — the default posture, free.
- **Limited public data**: only non-identifying information published (`.com`/`.net` style).
- **Full public disclosure**: everything in WHOIS/RDAP.
- Many ccTLDs impose their own rules and still require admin/tech contacts. One-click **DNSSEC** is available when Cloud DNS hosts the zone.

**Renewal** — auto-renewal is **on by default** after registration and charges the yearly price to your billing account:

- Turned it off and changed your mind? **Enable auto-renew at least 15 days before expiration** or it won't apply to that cycle.
- Lapsed anyway? Manual renewal works **within 30 days after expiration** (`renew-domain` with an explicit `--yearly-price`, or `registrations.renewDomain`).
- **ccTLDs force a 72-hour wait after expiration** before that renewal is possible.
- The docs promise nothing past the 30-day window — assume redemption/deletion at the registry's mercy and treat day 30 as the real deadline.

**Transfer out** — three steps:

1. **Unlock**: set `transferLockState` to `UNLOCKED` (most TLDs lock by default against hijacking).
2. **Get the authorization (EPP) code** via console/gcloud/API.
3. **Hand it to the gaining registrar**, which initiates the transfer.

Exceptions: `.uk`/`.co.uk` have no auth codes — instead you issue a **push transfer** to the gaining registrar's Nominet tag via gcloud/API. Some gaining registrars require your WHOIS contact info to be public before accepting, so you may need to drop privacy temporarily.

## Gotchas

- **You cannot transfer a domain INTO Cloud Domains** (shut down 2024-01-22). New registrations only. The most common wrong assumption about the product post-acquisition.
- **Forwarding and dynamic DNS are gone** (same shutdown date). A legacy Google Domains setup that relied on domain/email forwarding must replicate it with Cloud DNS records plus its own redirect service/mail provider.
- **The 15-day email verification** after registration is a silent killer: no click, no domain.
- **Auto-renew timing trap:** re-enabling auto-renew inside the last 15 days before expiration doesn't save you; renew manually instead.
- **Expired-domain recovery is a 30-day sprint**, and for ccTLDs the first 72 hours are a forced wait. Don't design a "we'll notice eventually" process around it.
- **Two bills:** the registration renews yearly through Cloud Domains, and the Cloud DNS zone serving it bills separately. Killing the project's billing endangers the registration itself.
- **Transfer lock and privacy interact with transfers out:** unlock first, and expect some registrars to demand public contact data before accepting.
- **`PRIVATE_CONTACT_DATA` is dead** — code or Terraform still setting it will fail; use `REDACTED_CONTACT_DATA`.
- **Docs truth over memory:** this product's status has shifted repeatedly since 2023. The feature-deprecations page is the authority; re-check it before recommending Cloud Domains for anything new.

## When to use vs siblings

- **[[gcp-cloud-dns]] hosts, Cloud Domains registers.** Cloud DNS is the authoritative name-serving product (zones, records, DNSSEC signing); Cloud Domains is the registrar that points the world at those name servers. You almost always use them together — but either works without the other.
- **Certificate provisioning is neither product's job** — that's [[gcp-certificate-manager]], which uses DNS-authorization records you place in the Cloud DNS zone.
- **Need a registrar you can transfer existing domains into?** Cloud Domains is not it anymore — use Squarespace or any third-party registrar, and still point the name servers at Cloud DNS if you want GCP-hosted DNS.

## Related

[[gcp-cloud-dns]] — the DNS host this registrar delegates to. Downstream consumers of a domain: [[gcp-load-balancing]], [[gcp-cloud-cdn]], [[gcp-media-cdn]], [[gcp-certificate-manager]] (TLS for the names you register), [[gcp-cloud-run]], [[gcp-app-engine]] (custom domains). Access control on registrations: [[gcp-iam]]. Practice: [[network-engineering]], [[terraform]] (`google_clouddomains_registration`).

Sources: https://docs.cloud.google.com/domains/docs, https://docs.cloud.google.com/domains/docs/overview, https://docs.cloud.google.com/domains/docs/register-domain, https://docs.cloud.google.com/domains/docs/transfer-domain-to-another-registrar, https://docs.cloud.google.com/domains/docs/renew-expired-domain, https://docs.cloud.google.com/domains/docs/deprecations/feature-deprecations (fetched 2026-07).
