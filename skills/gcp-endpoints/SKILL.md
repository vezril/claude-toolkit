---
name: gcp-endpoints
description: "Google Cloud Endpoints — self-deployed API management: you write an OpenAPI (2.0/3.0.x) or gRPC service config, deploy it to Service Management with gcloud endpoints services deploy, and run the Extensible Service Proxy (ESPv2, Envoy-based; legacy ESP is NGINX-based and maintenance-only) as a sidecar or Cloud Run remote proxy in front of your backend; Service Control enforces API keys, JWT auth, quotas, and emits logs/metrics. Covers the three flavors (OpenAPI, gRPC with HTTP/JSON transcoding, legacy Endpoints Frameworks), ESPv2-on-Cloud-Run setup, x-google-* extensions, pricing shape ($/million calls), and limits. Use when securing/monitoring an API on Cloud Run, GKE, Compute Engine, or App Engine with API keys or JWTs, doing gRPC transcoding, choosing Endpoints vs API Gateway vs Apigee, or debugging ESP/ESPv2, service-config, or Service Control issues."
license: MIT
---

# Cloud Endpoints

API management you run yourself: a declarative **service config** (OpenAPI or gRPC
service definition) deployed to Google's Service Management, enforced at runtime by
the **Extensible Service Proxy** (ESP/ESPv2) container that *you* deploy in front of
your backend. Gives you API keys, JWT auth, quotas, monitoring, logging, and tracing
without writing gateway code. Mature and GA, but quiet: Google's managed alternatives
(API Gateway, Apigee) are where new investment goes — see "vs siblings" below.

## The mental model

Two halves, control plane and data plane:

1. **Control plane — the service config.** Your OpenAPI 2.0/3.0.x spec (or gRPC
   `api_config.yaml` + compiled `.pb` descriptor) *is* the API product definition:
   surface, auth rules, API-key requirements, quotas, backend addresses (via
   `x-google-*` extensions). `gcloud endpoints services deploy` uploads it to
   **Service Management**, which versions it as a config ID. The service *name* comes
   from the spec's `host` (2.0) / `servers.url` (3.x) — conventionally
   `NAME.endpoints.PROJECT_ID.cloud.goog`.
2. **Data plane — ESP/ESPv2.** A proxy container running the config:
   - **ESPv2** (Envoy-based) — what new deployments should use.
   - **ESP** (NGINX-based) — docs warning, verbatim: "ESP is maintained for
     preexisting users. New users are encouraged to follow the tutorials for ESPv2.
     Both products are generally available and production-ready." (as of 2026-07)
   Deployed either as a **sidecar** next to your backend (GKE, Compute Engine — no
   extra network hop) or as a **remote proxy**: a standalone Cloud Run service
   fronting serverless backends, wired via `x-google-backend`.
3. **Runtime — Service Control.** On each request the proxy checks/reports against
   the Service Control API: API key validation, JWT verification, quota accounting,
   then forwards to the backend and ships logs/metrics/trace data. The proxy caches
   aggressively, so most API calls never hit Service Control synchronously.

State lives in the deployed config, not the proxy — redeploy the config, restart or
rebuild the proxy image, and behavior changes. Nothing here edits your backend code.

## Three flavors

- **Endpoints for OpenAPI** — REST APIs, any language/framework, spec in OpenAPI
  2.0 or 3.0.x (3.x uses `servers:` + `x-google-endpoint`/`x-google-api-management`).
- **Endpoints for gRPC** — protobuf APIs; ESP/ESPv2 can also **transcode HTTP/JSON
  to gRPC** so browsers/curl can call gRPC backends. Needs HTTP/2 end to end, so no
  gRPC on Cloud Run functions (and legacy App Engine constraints apply).
- **Endpoints Frameworks** — App Engine standard **gen 1 only** (Java 8, Python 2.7),
  built-in gateway instead of ESP. Effectively legacy; don't start anything new here.

## How-to: ESPv2 on Cloud Run (the canonical serverless shape)

```bash
# 1. Deploy the service config (spec title/host name the service)
gcloud endpoints services deploy openapi-run.yaml --project ESPV2_PROJECT_ID

# 2. Enable the machinery + your new managed service
gcloud services enable servicemanagement.googleapis.com servicecontrol.googleapis.com
gcloud services enable ENDPOINTS_SERVICE_NAME

# 3. Bake the config INTO an ESPv2 image (Google's gcloud_build_image script)
./gcloud_build_image   # -> gcr.io/PROJECT/endpoints-runtime-serverless:VERSION-HOST-CONFIG_ID

# 4. Run that image as the public Cloud Run service
gcloud run deploy ESPV2_SERVICE --image=gcr.io/PROJECT/endpoints-runtime-serverless:... \
  --allow-unauthenticated --platform managed

# 5. Let ESPv2 invoke the (private) backend
gcloud run services add-iam-policy-binding BACKEND_SERVICE \
  --member serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role roles/run.invoker
```

In the spec, `x-google-backend: {address: BACKEND_URL, protocol: h2}` routes to the
backend. On GKE/GCE the shape is simpler: run `espv2` as a sidecar with
`--service=NAME --rollout_strategy=managed` flags instead of baking an image.

## Gotchas and limits

- **Config changes are not live**: serverless ESPv2 bakes the config ID into the
  image — redeploying the spec requires rebuilding/redeploying the proxy image
  (sidecars can use `--rollout_strategy=managed` to auto-pull latest).
- **Service Control quota**: 10,000,000 quota units per 100 seconds per producer
  project (one unit per check/report call); proxy caching means real API throughput
  is far higher, but bursty cold-cache traffic can bump it.
- **OpenAPI subset**: not every OpenAPI feature is supported (see the "unsupported
  OpenAPI features" page); the spec doubles as Google service config, so lint against
  what `gcloud endpoints services deploy` accepts, not just swagger validators.
- **You own the proxy**: patching, scaling, and paying for the ESPv2 container is on
  you — that's the core trade against API Gateway.
- **DNS/TLS**: `*.cloud.goog` names are convenience; custom domains need your own
  DNS + certs (on Cloud Run, the ESPv2 service's domain mapping).
- **Pricing shape** (per billing account, per month): first 2M API calls **free**,
  then **$3.00/million** up to 1B calls, **$1.50/million** beyond — plus normal
  compute/network cost of wherever ESP runs.

## When to use vs siblings

- **[[gcp-api-gateway]]** — fully managed gateway built on the same ESPv2/Envoy tech
  and "the same authentication mechanism and syntax as used by Cloud Endpoints," but
  Google runs the proxy. For new serverless APIs (Cloud Run, Cloud Functions, App
  Engine) with OpenAPI 2.0, prefer API Gateway: no proxy image to build, rebuild, or
  scale. Choose Endpoints instead when you need sidecar-level latency on GKE/GCE,
  gRPC transcoding, or OpenAPI 3.x support.
- **[[gcp-apigee]]** — full enterprise API management: monetization, developer
  portals, advanced analytics, hybrid/multicloud. Endpoints/API Gateway are
  lightweight enforcement; Apigee is a product platform with a price tag to match.
- **Status honestly stated** (2026-07): Endpoints itself carries no deprecation
  banner and is GA, but ESP (v1) is maintenance-only, Endpoints Frameworks targets
  dead runtimes, and the docs' newest patterns funnel serverless users toward API
  Gateway. Treat Endpoints as stable-but-static: fine to keep running, choose
  deliberately for greenfield.

## Related

- [[gcp-api-gateway]], [[gcp-apigee]] — the sibling API-management tiers (above)
- [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]] — serverless backends behind ESPv2 remote proxy
- [[gcp-gke]], [[gcp-compute-engine]] — sidecar deployment homes
- [[gcp-iam]] — `roles/run.invoker` wiring and the proxy's service account
- [[gcp-cloud-logging]], [[gcp-cloud-monitoring]], [[gcp-cloud-trace]] — where Service Control's telemetry lands
- [[gcp-load-balancing]], [[gcp-cloud-dns]] — fronting ESP with your own domain
- [[docker]] — ESP/ESPv2 are containers you build and run
- [[terraform]], [[devops]] — codifying service-config deploys and proxy rollouts

Sources: https://docs.cloud.google.com/endpoints/docs, https://docs.cloud.google.com/endpoints/docs/openapi/about-cloud-endpoints, https://docs.cloud.google.com/endpoints/docs/choose-endpoints-option, https://docs.cloud.google.com/endpoints/docs/openapi/architecture-overview, https://docs.cloud.google.com/endpoints/docs/openapi/get-started-cloud-run, https://docs.cloud.google.com/endpoints/docs/openapi/openapi-overview, https://docs.cloud.google.com/endpoints/quotas, https://cloud.google.com/endpoints/pricing (fetched 2026-07).
