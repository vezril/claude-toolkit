---
name: gcp-apigee
description: "Google Cloud Apigee — full-lifecycle API management platform: API proxies (ProxyEndpoint/TargetEndpoint, PreFlow/conditional/PostFlow), XML policies (SpikeArrest, Quota, OAuthV2, VerifyAPIKey, ServiceCallout), the org → environment → env-group → proxy → API product → developer app → key hierarchy, analytics, developer portals, monetization, Advanced API Security. Variants: Apigee (formerly Apigee X, SaaS), Apigee hybrid (runtime on your Kubernetes), legacy Apigee Edge. Use when designing/building/debugging Apigee proxies or policies, provisioning an org (VPC peering vs non-peering), packaging API products, setting quotas/rate limits, choosing Apigee vs API Gateway vs Cloud Endpoints, or estimating Apigee cost shape."
license: MIT
---

# Apigee (Google Cloud API Management)

Google Cloud's heavyweight, full-lifecycle API management platform: you put an **API proxy** in front of backend services and get security, rate limiting, transformation, caching, analytics, developer onboarding, and monetization as configuration (XML policies), not code. Three shapes: **Apigee** (the SaaS product, historically "Apigee X" — docs now mostly just say "Apigee"), **Apigee hybrid** (Google-hosted control plane + runtime plane you run on GKE/AKS/EKS via Helm charts or the older `apigeectl`; v1.16 current as of 2026-07), and **Apigee Edge** (the legacy pre-GCP platform, still documented separately). One Apigee org binds to one Google Cloud project.

## The mental model

The hierarchy, top down — memorize this, everything else hangs off it:

- **Organization** — top-level container, 1:1 with a GCP project. Holds everything below.
- **Environment** — a runtime deploy target (`dev`, `staging`, `prod`). Isolated: KVMs, caches, target servers, and deployed proxy revisions are per-environment. Up to 85 per org.
- **Environment group** — maps hostnames to a set of environments; routing of `api.example.com` into the right env happens here (this replaced Edge's "virtual hosts").
- **API proxy** — the unit of deployment. Two halves: **ProxyEndpoint** (faces the client: base path, flows, client-side policies) and **TargetEndpoint** (faces the backend). Each half has a **PreFlow** (always runs first), **conditional flows** (match on path/verb, e.g. `GET /pets`), and a **PostFlow** (always runs last). Policies attach as steps in those flows. Edits create **revisions**; you deploy a specific revision to an environment. Max 10 endpoints and 200 flows per proxy; bundle ≤ 15 MB.
- **Shared flow** — a reusable policy sequence (auth, logging, CORS) invoked via FlowCallout or attached org-wide via **flow hooks**.
- **API product** — the publishing unit: bundles operations (proxy + resource paths + verbs) with a quota, OAuth scopes, and custom attributes. Developers never consume proxies directly; they consume products.
- **Developer → App → Key** — a registered developer creates an app, the app subscribes to products and gets a consumer key/secret; `VerifyAPIKey` or `OAuthV2` policies resolve the key back to product entitlements at runtime. Key approval is auto or manual per product.

**Policies** are the verbs. Main families (all XML `<PolicyName>` elements attached to flow steps):

- **Traffic**: `SpikeArrest`, `Quota`, `ResponseCache` / `LookupCache` / `PopulateCache` / `InvalidateCache`.
- **Security**: `VerifyAPIKey`, `OAuthV2` (+ Get/Set/Delete/RevokeOAuthV2Info), `VerifyJWT` / `DecodeJWT` / `GenerateJWT`, `BasicAuthentication`, `HMAC`, `AccessControl`, `CORS`, SAML generate/validate; threat protection — `JSONThreatProtection`, `XMLThreatProtection`, `RegularExpressionProtection`, `OASValidation`.
- **Mediation**: `AssignMessage`, `ExtractVariables`, `JSONToXML` / `XMLToJSON`, `XSLTransform`, `RaiseFault`, `KeyValueMapOperations`, `DataCapture`, `MessageLogging`.
- **Extension**: `JavaScript`, `PythonScript`, `JavaCallout`, `ServiceCallout` (HTTP call-out mid-flow), `ExternalCallout` (gRPC), `FlowCallout` (invoke a shared flow).

A policy is a standalone XML file referenced from a flow step, optionally gated by a **condition**:

```xml
<!-- apiproxy/proxies/default.xml (ProxyEndpoint) -->
<PreFlow>
  <Request>
    <Step><Name>Verify-API-Key</Name></Step>
    <Step><Name>Spike-Arrest</Name></Step>
  </Request>
</PreFlow>
<Flows>
  <Flow name="getPet">
    <Condition>(proxy.pathsuffix MatchesPath "/pets/*") and (request.verb = "GET")</Condition>
    <Request><Step><Name>Lookup-Cache</Name></Step></Request>
  </Flow>
</Flows>
```

State moves between policies via **flow variables** — the ones you'll use constantly: `request.verb`, `request.header.NAME`, `proxy.pathsuffix`, `request.queryparam.NAME`, `response.status.code`, `target.url`, plus everything `VerifyAPIKey`/`OAuthV2` populate (`apiproduct.name`, `developer.email`, `client_id`) and whatever you `ExtractVariables` into. Conditions use the same variables (`MatchesPath`, `=`, `!=`, `JavaRegex`).

**Backends**: a TargetEndpoint points at a URL or, better, at named **target servers** defined per environment (host/port/TLS config), so the same proxy revision hits different backends per env and can load-balance across several with health checks — never hardcode backend URLs in the bundle.

## How-to shapes

**Provision an org** (one-time, slow — plan for tens of minutes): Console wizard or CLI, choosing subscription vs pay-as-you-go, and **VPC peering vs non-peering** networking. Non-peering is the modern default; peering carves a /22 (+ /28) from your VPC. Northbound traffic normally enters through a global external LB + PSC to the Apigee instance; southbound to private backends also rides PSC in non-peering setups.

**Everything is the management API** (`apigee.googleapis.com/v1`) under the hood; the Console, `gcloud apigee`, and the community-standard `apigeecli` all wrap it:

```bash
gcloud apigee apis list --organization=$ORG
gcloud apigee apis deploy REVISION --api=my-proxy --environment=prod --organization=$ORG
gcloud apigee products list --organization=$ORG
# raw management API — the escape hatch for anything gcloud doesn't cover:
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://apigee.googleapis.com/v1/organizations/$ORG/environments/prod/deployments"
```

**Proxy source layout** (what's in the bundle zip you import): `apiproxy/<name>.xml`, `apiproxy/proxies/default.xml` (ProxyEndpoint), `apiproxy/targets/default.xml` (TargetEndpoint), `apiproxy/policies/*.xml`, `apiproxy/resources/{jsc,java,py,...}`. CI/CD shape: keep this tree in git, lint/test locally (Apigee has local development via Apigee Emulator + VS Code integration), zip → import (creates revision N) → deploy N to env → smoke test → promote the same revision through envs. Terraform's `google_apigee_*` resources cover org/env/instance plumbing; proxy bundles usually ship via `apigeecli apis create bundle` in a pipeline.

**Debugging**: the Debug (Trace) tool records per-policy execution with variable values — first stop for "why did this policy not fire" (check the flow condition and which endpoint's Pre/PostFlow it's on). Limits: sessions capped (15 transactions/session).

**Secure an API, minimal viable shape**:

1. `VerifyAPIKey` (or `OAuthV2` with `Operation=VerifyAccessToken`) in the ProxyEndpoint request PreFlow — this also binds the call to an API product.
2. `SpikeArrest` immediately after (protect the backend before doing expensive work).
3. `Quota` referencing the product's quota settings (`<Interval ref="verifyapikey.Verify-API-Key.apiproduct.developer.quota.interval"/>` pattern) so limits live on the product, not the proxy.
4. `CORS` policy if browsers call it; threat-protection policies on any endpoint accepting bodies.
5. The **Advanced API Security** add-on layers on top: risk scoring of proxy config, abuse/bot detection from traffic analysis, and security actions — an add-on cost, not default behavior.

## Gotchas and limits

- **Quota is not a rate limiter.** Distributed quota counters sync no faster than every 10 s, so short bursts can exceed the nominal quota. Use `SpikeArrest` (per-second/minute smoothing, ~4,000/s ceiling) for protection and `Quota` for business entitlements — the classic pairing is both.
- **Payloads**: 30 MB buffered request/response (enforced); streaming mode lifts buffering with a 10 MB soft threshold — beyond that it works but Apigee stops being the right place for bulk transfer. Headers ≤ 60 KB, URL ≤ 10 KB.
- **Config ceilings** you'll actually hit: 15 MB proxy bundle, 5,000 API products/org, 75 deployed shared flows/env, KVM values ~10 KB (KVMs are config storage, not a database), cache values ≤ 256 KB with 30-day max TTL.
- **One org per project, orgs are near-permanent** — provisioning choices (region, network mode, billing type) are hard to unwind; get networking right before you provision.
- Revisions deployed to any env can't be edited meaningfully — save-as-new-revision is the loop; undeploying the only revision takes the API down, deploy-before-undeploy (seamless redeploy) is default behavior on Apigee.
- Analytics data is minutes delayed — don't build synchronous logic on it; use `DataCapture` for custom dimensions.
- Fault handling is its own subsystem: `FaultRules`/`DefaultFaultRule` per endpoint, evaluated on error with their own (surprising, bottom-up) ordering. Always define a DefaultFaultRule that normalizes error responses or clients see raw gateway errors.

**Pricing shape** (no exact numbers — check current page): two models. **Subscription** — Standard / Enterprise / Enterprise Plus tiers, annual commitment, bundled API-call volume and entitlements. **Pay-as-you-go** — billed on API calls (per-million), environment type + gateway-node uptime, and analytics; add-ons (Advanced API Security, monetization) bill separately. A time-boxed **eval/trial** org is free. The cost floor is meaningful even at zero traffic on PAYG (environments/nodes are always-on) — Apigee is priced like the enterprise platform it is.

## When to use vs siblings

- **Apigee**: full API *program* management — external/partner APIs, developer portal and self-service keys, monetization, per-consumer quotas, transformation/mediation, analytics, security scanning. Any backend (on-prem, multi-cloud, GCP). Heaviest and most expensive; overkill for a couple of internal services.
- **API Gateway** ([[gcp-api-gateway]]): fully managed, lightweight, OpenAPI-2.0-configured front door for **serverless GCP backends** (Cloud Run, Cloud Functions, App Engine). Auth (API keys, JWT/IAM) and basic management, per-call pricing, no portal/monetization/policy engine. Default choice for simple internal or single-product APIs.
- **Cloud Endpoints** ([[gcp-endpoints]]): same ESP/ESPv2 (Envoy) proxy tech but **you deploy and run the proxy** alongside your workload; gRPC transcoding support. Older option; for new work Google steers serverless cases to API Gateway.

Rule of thumb: products + developers + quotas + portal → Apigee; "put auth and a key in front of my Cloud Run service" → API Gateway; you need to own the proxy container or gRPC transcoding → Endpoints.

## Related

- [[gcp-api-gateway]], [[gcp-endpoints]] — the lighter-weight siblings above
- [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-gke]] — common backends; hybrid's runtime plane runs on GKE
- [[gcp-load-balancing]], [[gcp-vpc]], [[gcp-cloud-dns]], [[gcp-certificate-manager]] — northbound path: external LB + PSC, env-group hostnames, TLS
- [[gcp-iam]], [[gcp-secret-manager]], [[gcp-vpc-service-controls]] — control-plane access, credential hygiene, perimeter
- [[gcp-cloud-logging]], [[gcp-cloud-monitoring]], [[gcp-cloud-trace]] — MessageLogging targets, ops dashboards, distributed tracing
- [[terraform]], [[github-actions]], [[devops]] — org/env plumbing as code and the proxy-bundle CI/CD loop
- [[site-reliability-engineering]], [[secure-coding]], [[network-engineering]] — rate-limit design, threat-protection policies, peering/PSC topology

Sources: https://docs.cloud.google.com/apigee/docs, https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee, https://docs.cloud.google.com/apigee/docs/api-platform/get-started/get-started, https://docs.cloud.google.com/apigee/docs/api-platform/fundamentals/understanding-apis-and-api-proxies, https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy, https://docs.cloud.google.com/apigee/docs/api-platform/reference/limits, https://docs.cloud.google.com/apigee/docs/api-platform/fundamentals/best-practices-api-proxy-design-and-development, https://docs.cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid, https://cloud.google.com/apigee/pricing, https://docs.cloud.google.com/api-gateway/docs (fetched 2026-07).
