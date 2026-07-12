---
name: gcp-api-gateway
description: "Google Cloud API Gateway — the fully managed, Envoy-based gateway that fronts serverless backends (Cloud Run, Cloud Run functions, App Engine) with an OpenAPI-defined REST facade. Covers the API → immutable API config → regional gateway deployment model, the *.apigateway.PROJECT.cloud.goog managed service, x-google-backend routing (path translation, deadlines, jwt_audience), consumer auth (API keys, JWT, Firebase/Auth0/Okta, Google ID tokens), OpenAPI 2.0 vs 3.x (x-google-api-management), quotas, pricing shape, and custom domains via external load balancing. Also answers 'GCP API Gateway', 'gcloud api-gateway', 'gateway.dev'. Use when designing, deploying, securing, or debugging an API Gateway setup, choosing between API Gateway, Apigee, and Cloud Endpoints/ESPv2, writing an OpenAPI spec with x-google-* extensions, or wiring a gateway behind a load balancer for custom domains or multi-region."
license: MIT
---

# GCP API Gateway

API Gateway is Google Cloud's fully managed, pay-per-call API front door for serverless backends. You hand it an OpenAPI spec annotated with `x-google-*` extensions; it gives you a hosted, Envoy-based proxy at a `gateway.dev` URL that authenticates consumers, meters calls through Service Control, and forwards requests to Cloud Run, Cloud Run functions, App Engine, or any HTTP(S) backend. It is the lightweight sibling of Apigee and the managed successor niche of Cloud Endpoints — same auth syntax as Endpoints, but Google runs the proxy for you.

## The mental model

- **Three resources, strictly layered.** An **API** is the logical container. An **API config** is an immutable snapshot of an OpenAPI spec (or gRPC service definition) plus settings — you can never edit one, only upload a new one. A **gateway** is a regional Envoy proxy that serves exactly one config at a time. Updating an API = create new config, point the gateway at it (zero-downtime swap).
- **Every API is a managed service.** Creating an API registers a Service Management service named `API_ID.apigateway.PROJECT_ID.cloud.goog`. Each call flows through Service Control — that is what gets billed, logged, and rate-limited, and it is why API keys only work after you `gcloud services enable` that managed service in the consumer project.
- **The gateway does auth twice.** Inbound, it validates the consumer (API key, JWT, Google ID token). Outbound, it signs a Google ID token with the service account you gave `--backend-auth-service-account` and attaches it — so your Cloud Run backend can require authentication and accept only the gateway.
- **Serverless economics.** Scale-to-zero proxy, no instances to size, billed per million calls plus premium-tier egress. Nothing to patch, but also nothing to tune.
- **Config is the artifact.** Because configs are immutable and versioned, your OpenAPI file in git *is* the deployment history. Treat it like source; promote by re-pointing gateways.

## Core how-to

Enable the three services once per project:

```sh
gcloud services enable apigateway.googleapis.com servicemanagement.googleapis.com servicecontrol.googleapis.com
```

Define the API in OpenAPI 2.0 with backend routing and (optionally) API-key security:

```yaml
swagger: "2.0"
info: {title: hello-api, version: "1.0.0"}
schemes: [https]
paths:
  /hello:
    get:
      operationId: hello
      x-google-backend:
        address: https://hello-abc1def2gh-uc.a.run.app
      security:
        - api_key: []
      responses:
        "200": {description: OK}
securityDefinitions:
  api_key:
    type: "apiKey"
    name: "key"
    in: "query"
```

Create, configure, deploy:

```sh
gcloud api-gateway apis create API_ID
gcloud api-gateway api-configs create CONFIG_ID \
  --api=API_ID --openapi-spec=openapi.yaml \
  --backend-auth-service-account=SA_EMAIL
gcloud api-gateway gateways create GATEWAY_ID \
  --api=API_ID --api-config=CONFIG_ID --location=GCP_REGION
```

The gateway answers at `https://GATEWAY_ID-HASH.REGION_CODE.gateway.dev`. To roll a new config onto a live gateway: `gcloud api-gateway gateways update GATEWAY_ID --api=API_ID --api-config=NEW_CONFIG_ID --location=GCP_REGION`.

**`x-google-backend` knobs** (per-operation or top-level): `address` (required), `path_translation` — `APPEND_PATH_TO_ADDRESS` (default at top level; `/hello/Dave` → `address/hello/Dave`) vs `CONSTANT_ADDRESS` (default at operation level; path params become query params), `deadline` (seconds; default 15, max 600 — the silent killer of slow backends), `jwt_audience` (set it explicitly for Cloud Run deterministic URLs; defaults to `address`), `disable_auth` to skip the outbound ID token.

**Consumer auth:** API keys identify the calling project for quota/billing; JWTs (service accounts, Firebase, Auth0, Okta, Google ID tokens) authenticate callers — declared in `securityDefinitions` with the same `x-google-issuer` / `x-google-jwks_uri` / `x-google-audiences` syntax as Cloud Endpoints. The gateway forwards the request body and headers unchanged.

**OpenAPI 3.x:** supported alongside 2.0, with a different shape — a required root-level `x-google-api-management` extension holds a `backends` map (`address`, `jwtAudience`, `disableAuth`, `pathTranslation`, `deadline`, `protocol`) that operations reference by name via `x-google-backend`; JWT auth moves into `securitySchemes` via `x-google-auth` (`issuer`, `jwksUri`, `audiences`, `jwtLocations`). Update the gcloud CLI before uploading 3.x specs, and check the separate 3.x feature-limitations page — parity with 2.0 is not complete.

## Gotchas, limits, pricing shape

- **Configs are immutable; one config per gateway.** No in-place edits, no fan-in of multiple configs to a single gateway. Design your spec as one file (or merge before upload).
- **Quotas:** 50 APIs per project, 100 configs per API, 50 gateways per region. Default Service Control rate: 10,000,000 quota units per 100 s per producer project (caching means real throughput can exceed it).
- **Hard limits:** 32 MB request/response payloads, 60 KB request headers, 1 MB gRPC-transcoding payloads, **no streaming**. Big uploads and SSE/WebSockets do not belong behind API Gateway.
- **Custom domains are not native.** Default is only the `gateway.dev` URL; a custom domain means putting a global external HTTP(S) load balancer with a serverless NEG in front (documented as Preview). Multi-region = one gateway per region behind that same LB.
- **API keys 403 until you enable the managed service** (`MANAGED_SERVICE_NAME` from `gcloud api-gateway apis describe`) in the project. Most common first-deploy failure.
- **Propagation lag:** new configs and key enablements take minutes to become active; don't debug a 404/403 in the first few minutes.
- **Pricing shape:** billed as Service Control operations, per million API calls per billing account — a free tier for the first couple million calls each month, a flat per-million rate up to a very large monthly volume, then a cheaper rate beyond it. Data transfer out is standard premium-tier internet egress, tiered by volume and continent; ingress is free. No per-gateway or idle charge.

## Debugging and observability

Everything routes through the managed service, so the usual Google Cloud observability stack applies without extra wiring:

- **Inspect state first.** `gcloud api-gateway apis describe API_ID` (shows the managed service name), `gcloud api-gateway api-configs list --api=API_ID`, `gcloud api-gateway gateways describe GATEWAY_ID --location=REGION` (shows `defaultHostname` and which config is live). Artifacts drive state — the answer to "what is deployed?" is always in these, not in memory.
- **Monitoring and tracing** come per-API via Cloud Monitoring metrics and Cloud Trace; **platform logs** and **audit logs** land in Cloud Logging under the managed service, which is where consumer 401/403s and backend 5xxs show up with the gateway's view of the request.
- **Classic failure triage:** 403 with a valid key → managed service not enabled in the caller's project; 401 from the *backend* → the gateway's ID token audience is wrong (`jwt_audience`) or the backend SA lacks invoker rights; 504 at ~15 s → default `deadline` too low; 404 right after deploy → propagation lag or `path_translation` sending the path somewhere you didn't expect.

## When to use vs siblings

- **API Gateway** — you want a managed facade over serverless backends with API keys/JWT auth, metering, and OpenAPI-driven config, and you don't want to run a proxy. Cheapest and simplest; no API monetization, developer portal, or traffic-shaping policies.
- **Apigee** — full API-management platform: developer portals, monetization, advanced policies (transformations, quotas per product, threat protection), hybrid/on-prem deployment, analytics. Substantially more cost and operational surface. Choose it when APIs are a *product*, not just an ingress.
- **Cloud Endpoints (ESPv2)** — the same OpenAPI/`x-google-*` model, but *you* deploy and run the ESPv2 Envoy container (e.g., as a sidecar or Cloud Run service). Pick it when you need proxy-level control, gRPC-first workloads, or deployment topologies API Gateway can't reach; pick API Gateway when you'd rather Google host the proxy. Auth syntax is interchangeable, so migrating specs between the two is cheap.

## Related

[[gcp-apigee]], [[gcp-endpoints]] — the sibling decision above. Backends: [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]]. Custom domains/multi-region: [[gcp-load-balancing]], [[gcp-cloud-dns]], [[gcp-certificate-manager]]. Auth plumbing: [[gcp-iam]], [[gcp-secret-manager]]. Observability: [[gcp-cloud-logging]], [[gcp-cloud-monitoring]], [[gcp-cloud-trace]]. Practice: [[terraform]] (configs-as-artifacts fit IaC naturally), [[network-engineering]], [[secure-coding]].

Sources: https://docs.cloud.google.com/api-gateway/docs, https://docs.cloud.google.com/api-gateway/docs/about-api-gateway, https://docs.cloud.google.com/api-gateway/docs/secure-traffic-gcloud, https://docs.cloud.google.com/api-gateway/docs/quotas, https://docs.cloud.google.com/api-gateway/docs/authentication-method, https://docs.cloud.google.com/api-gateway/docs/openapi-overview, https://docs.cloud.google.com/api-gateway/docs/how-to, https://docs.cloud.google.com/api-gateway/docs/passing-data, https://docs.cloud.google.com/api-gateway/docs/deployment-model, https://docs.cloud.google.com/api-gateway/docs/oasv3-extensions, https://docs.cloud.google.com/api-gateway/docs/using-custom-domains, https://cloud.google.com/api-gateway/pricing (fetched 2026-07).
