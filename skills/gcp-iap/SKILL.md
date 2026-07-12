---
name: gcp-iap
description: "Google Cloud Identity-Aware Proxy (IAP): BeyondCorp zero-trust access to apps and VMs WITHOUT a VPN. An identity checkpoint at the edge that checks IAM (roles/iap.httpsResourceAccessor) + optional context-aware access levels BEFORE traffic reaches the app, and injects a signed JWT (x-goog-iap-jwt-assertion, ES256) the app MUST verify. Two modes: HTTPS resource protection on a load-balancer backend (App Engine/Cloud Run/GKE/GCE), and TCP forwarding for SSH/RDP to private VMs (gcloud compute ssh --tunnel-through-iap). Use when protecting an internal web app, gating SSH/RDP to no-public-IP instances, verifying the IAP JWT, wiring context-aware/device-based access, or supporting external identities."
license: MIT
---

# Google Cloud Identity-Aware Proxy (IAP)

IAP is an **identity checkpoint at the edge**: application-level authentication and
authorization without a VPN or bastion. It is Google's implementation of the
**BeyondCorp** zero-trust model — trust is established per-request from *identity +
context*, not from being inside a network perimeter. Every request to a protected
resource is evaluated in real time; only authenticated, authorized principals get through.

## The mental model

IAP sits **on the load-balancer backend service** (HTTPS mode) or **in front of the
instance** (TCP mode), between the caller and your resource. For each request it:

1. **Authenticates** the caller — redirects unsigned browser users to sign in (Google
   Account, Workforce Identity Federation, or Identity Platform), storing tokens in cookies.
2. **Authorizes** against **IAM** — the principal needs the resource-type role
   (`roles/iap.httpsResourceAccessor` for web apps, `roles/iap.tunnelResourceAccessor`
   for TCP). Optionally an IAM **conditional binding** requires an **access level**
   (context-aware access) — device posture, IP range, geo.
3. **Injects a signed JWT** into the upstream request. Only *after* all checks pass does
   traffic reach your app.

The checks happen **before** your code runs. Your app's job is to *trust IAP and nothing
else*: verify the JWT and refuse any request that didn't come through IAP.

## Two modes

**HTTPS resource protection** — a central authz layer for browser/HTTPS apps, replacing
network firewalls with an app-level access model. Fronts App Engine, Cloud Run, GKE, and
Compute Engine (the latter three via a Cloud Load Balancing **backend service**; Cloud Run
directly or via LB). Requires an external Application Load Balancer with an HTTPS frontend.

**TCP forwarding** — wraps SSH/RDP (or any TCP) to VMs that have **no public IP**,
tunneling over an IAP-authenticated connection. Eliminates jump hosts and open SSH ports.

## Shapes (verified against docs)

Enable IAP on a load-balancer backend service:
```bash
gcloud compute backend-services update BACKEND_SERVICE --global --iap=enabled
# regional LB: --region REGION instead of --global. Prompts for OAuth consent screen
# (brand) config on first enable. Frontend must have an HTTPS protocol.
```

Grant a user access to the protected app (HTTPS mode):
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:alice@example.com --role=roles/iap.httpsResourceAccessor
# (grant on the resource, not just the project, to scope tightly)
```

SSH / RDP over the IAP TCP tunnel (no public IP needed):
```bash
gcloud compute ssh INSTANCE --tunnel-through-iap --zone=ZONE       # SSH (port 22)
gcloud compute start-iap-tunnel INSTANCE 3389 \
  --local-host-port=localhost:13389 --zone=ZONE                    # RDP → local port
```
Firewall + IAM the tunnel needs:
```bash
gcloud compute firewall-rules create allow-ingress-from-iap \
  --direction=INGRESS --action=allow --rules=tcp:22,tcp:3389 \
  --source-ranges=35.235.240.0/20      # ALL IAP TCP-forwarding source IPs
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:alice@example.com --role=roles/iap.tunnelResourceAccessor
```

Verify the signed JWT in your app (**mandatory** — see gotchas):
- Read the header **`x-goog-iap-jwt-assertion`**.
- Verify the signature: algorithm **`ES256`**, match the JWT `kid` to a key from
  `https://www.gstatic.com/iap/verify/public_key-jwk` (JWK) or `.../public_key` (PEM map).
- Check `iss` == `https://cloud.google.com/iap`.
- Check `aud` matches your resource exactly:
  - GCE/GKE backend: `/projects/PROJECT_NUMBER/global/backendServices/SERVICE_ID`
  - Cloud Run: `/projects/PROJECT_NUMBER/locations/REGION/services/SERVICE_NAME`
  - App Engine: `/projects/PROJECT_NUMBER/apps/PROJECT_ID`
- Check `exp` in the future / `iat` in the past (allow ~30s skew). The `email`/`sub`
  claims identify the authenticated user.

## Gotchas

- **You MUST verify the JWT AND lock the app to IAP-only traffic — otherwise IAP is
  bypassable.** IAP does not protect against activity *inside* the project (e.g. another
  VM hitting the backend directly). Restrict the backend so it only accepts LB/IAP traffic
  (firewall rules, VPC design) and reject any request lacking a valid
  `x-goog-iap-jwt-assertion`. Enforcement is defense-in-depth: network lockdown *plus*
  JWT verification.
- **Signed header ≠ bearer token.** `x-goog-iap-jwt-assertion` is an IAP-signed assertion
  about the already-authenticated user; it is not the user's OAuth bearer token. Verify it
  as a JWT with IAP's ES256 public keys — do not treat it as an access token.
- **`aud` is resource-specific.** A JWT minted for one backend service must be rejected by
  another. Hardcode/validate the exact `aud` string for *this* resource; a wrong or absent
  `aud` check lets a token from a different app slide through.
- **Context-aware access needs Access Context Manager.** Access levels (device, IP, geo)
  are defined in Access Context Manager and attached via IAM **conditions** on
  `iap.httpsResourceAccessor`. **Device-based** attributes require a **Chrome Enterprise
  Premium** license.
- **External identities are opt-in and per-resource.** Default is Google identities. To
  admit non-Google users, wire **Identity Platform** (email/password, social, SAML, OIDC,
  multi-tenant) with a FirebaseUI or custom sign-in page (often hosted on Cloud Run);
  enterprise SSO can instead use **Workforce Identity Federation**. Programmatic clients
  authenticate with an OIDC ID token whose `aud` is the IAP OAuth client ID.
- **Cost.** IAP itself carries no per-request charge — you pay for the underlying load
  balancer/compute; device-based access levels require the Chrome Enterprise Premium
  license noted above.

## vs siblings

- **IAP vs a plain load balancer** — a bare LB routes traffic; IAP adds the *identity +
  authz gate* in front of the backend and the signed-identity JWT. Use IAP when "who is
  this and are they allowed" must be answered before the app.
- **IAP vs a bastion / jump host** — IAP TCP forwarding replaces the bastion: no public
  IP, no standing SSH port, access gated by IAM instead of host credentials.
- **IAP (ingress) vs Secure Web Proxy (egress)** — IAP controls *inbound* access to your
  resources; **Secure Web Proxy** controls and inspects *outbound* traffic from your
  workloads to the internet. Opposite directions.
- **IAP vs API Gateway / Apigee** — those manage/authenticate API traffic and quotas; IAP
  is a broad app- and VM-level access gate for browser apps and SSH/RDP, not an API manager.

## Related

- [[gcp-iam]] — the roles/conditions IAP authorizes against (`iap.httpsResourceAccessor`,
  `iap.tunnelResourceAccessor`).
- [[gcp-load-balancing]] — the backend service IAP attaches to in HTTPS mode.
- [[gcp-compute-engine]] — VMs protected by TCP forwarding (SSH/RDP without public IPs).
- [[gcp-cloud-run]] — serverless backend protected directly or via LB.
- [[gcp-app-engine]] — App Engine apps fronted by IAP.
- [[gcp-gke]] — GKE workloads exposed via an IAP-enabled ingress/LB.
- [[gcp-secure-web-proxy]] — the egress counterpart (outbound control).
- [[gcp-vpc]] / [[gcp-vpc-service-controls]] — network lockdown that makes IAP non-bypassable.
- [[gcp-certificate-manager]] — certs for the required HTTPS frontend.
- [[network-security]], [[secure-coding]] — zero-trust patterns and verifying the JWT in-app.

Sources: https://docs.cloud.google.com/iap/docs, https://docs.cloud.google.com/iap/docs/concepts-overview, https://docs.cloud.google.com/iap/docs/signed-headers-howto, https://docs.cloud.google.com/iap/docs/using-tcp-forwarding, https://docs.cloud.google.com/iap/docs/enabling-compute-howto, https://docs.cloud.google.com/iap/docs/cloud-iap-context-aware-access-howto, https://docs.cloud.google.com/iap/docs/external-identities, https://docs.cloud.google.com/iap/docs/faq (fetched 2026-07).
