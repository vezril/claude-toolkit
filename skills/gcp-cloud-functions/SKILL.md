---
name: gcp-cloud-functions
description: "Google Cloud Run functions (formerly Cloud Functions; also 'Cloud Functions 1st/2nd gen', 'Cloud Run functions'): single-purpose HTTP and event-driven (CloudEvents/Eventarc) functions built from source with buildpacks and run as Cloud Run services — signatures via the Functions Framework, gcloud run deploy --function vs legacy gcloud functions deploy, generations, retries, concurrency, scaling, limits, pricing. Use when writing/deploying/debugging a GCP function, choosing 1st gen vs 2nd gen vs Cloud Run, wiring Pub/Sub or Storage triggers, or migrating off gcloud functions."
license: MIT
---

# Cloud Run functions (formerly Cloud Functions)

Google's function-as-a-service: you write a single-purpose function, Google builds it
from source and runs it on Cloud Run infrastructure. The naming story matters
(date-stamped, verified 2026-07):

- **Pre-Aug 2024**: "Cloud Functions", with **1st gen** (original, isolated infra) and
  **2nd gen** (rebuilt on Cloud Run + Eventarc, GA 2022).
- **Aug 2024**: renamed **Cloud Run functions**; 2nd gen became the default meaning,
  1st gen lives on as "Cloud Run functions (1st gen)" (now deprecated-tier, limited
  triggers/configurability).
- **Today**: the docs say it plainly — *"a function is a Cloud Run service that is
  deployed from source code."* Function metadata is stored in the Cloud Run service
  definition. Three management surfaces coexist: Cloud Run Admin API (recommended),
  the Cloud Functions v2 API (`gcloud functions`, still supported), and 1st gen
  (legacy). A v2-API function can be **detached** to become a plain Cloud Run
  service; the reverse is not possible, and "functions created with the Cloud Run
  Admin API cannot be modified with the Cloud Functions API."

## The mental model

**Source → buildpack → container → Cloud Run service.** You give gcloud a source
directory; Cloud Build applies Google's buildpacks (base images like `nodejs24`,
`python314`, `go126`, `java25`, `dotnet10`, `ruby40`, `php85`), produces a container
in Artifact Registry, and deploys it as a Cloud Run service. Automatic base-image
security updates are on by default (`--no-enable-automatic-updates` to opt out).

**Two function shapes**, one per trigger type (a function binds to at most ONE trigger):
- **HTTP functions** — get a URL, receive HTTP(S) requests. Signature: an HTTP
  handler (Flask request in Python, Express req/res in Node, `http.HandlerFunc` in
  Go, `HttpFunction` in Java).
- **Event-driven (CloudEvent) functions** — receive CloudEvents delivered by
  **Eventarc** (all event delivery goes through Eventarc now: Pub/Sub, Cloud
  Storage, Firestore, plus 90+ sources via Cloud Audit Logs). Signature: a
  CloudEvent handler (`CloudEventsFunction` in Java, `ICloudEventFunction<T>` in
  .NET, decorator/registration in the scripting runtimes).

**The Functions Framework** is the open-source per-language library that turns your
function into an HTTP server and unmarshals CloudEvents. It is what runs inside the
container — and it runs on your laptop too, so local dev is just `functions-framework
--target=my_fn` and curl; no emulator needed. Declare it as a normal dependency
(`package.json`, `requirements.txt`, etc.). Entry-point files are conventional:
`index.js`, `main.py`, `app.rb`, `index.php`; Go/Java/.NET use their standard layouts.

## Deploy shapes (current command surface)

Recommended — Cloud Run Admin API, the `--function` flag is what makes it a function
rather than a plain service:

```bash
gcloud run deploy FUNCTION \
  --source . \
  --function FUNCTION_ENTRYPOINT \
  --base-image nodejs24 \
  --region REGION \
  [--allow-unauthenticated]
```

Event wiring is a separate step (triggers are attached after deploy on this surface):

```bash
gcloud eventarc triggers create TRIGGER_NAME \
  --location=LOCATION \
  --destination-run-service=FUNCTION \
  --destination-run-region=REGION \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=MY_BUCKET" \
  --service-account=TRIGGER_SA
```

Legacy-but-supported — Cloud Functions v2 API, trigger flags inline:

```bash
gcloud functions deploy FUNCTION \
  --region=REGION --runtime=RUNTIME \
  --source=. --entry-point=ENTRYPOINT \
  TRIGGER_FLAGS   # e.g. --trigger-http, --trigger-topic=T; add --retry for events
```

Runtimes (GA, mid-2026): Node.js 18–24, Python 3.10–3.14, Go 1.24–1.26, Java 21/25,
.NET 8/10, Ruby 3.2–4.0, PHP 8.3–8.5. Lifecycle: GA → deprecated (90-day notice) →
decommissioned (no new deploys/updates).

## Gotchas

- **Generation gap is huge**: 1st gen = 1 request per instance, 9 min max timeout,
  8 GB/2 vCPU, 7 event sources. Current = up to 1000 concurrent requests per
  instance, 60 min HTTP timeout (event functions still 540 s; scheduled/task-queue
  1800 s), 16–32 GiB / 4+ vCPU, 90+ Eventarc sources, traffic splitting.
- **Retry semantics differ by management surface** — the classic footgun:
  Cloud Run Admin API functions retry **by default** (exponential backoff 10–600 s,
  24-hour window); Cloud Functions v2 API functions **drop failed events by
  default** unless deployed with `--retry`. Either way the window is 24 h and your
  function MUST be idempotent (use the CloudEvent ID as an idempotency key). A
  function stuck in a retry loop must be redeployed or deleted to stop it. For
  poison messages, put a dead-letter topic on the underlying Pub/Sub subscription.
- **Cold starts**: scale-to-zero means first-request latency; mitigate with
  min-instances (billed while idle) and by keeping global scope light.
- **Concurrency default**: current-gen functions default to concurrent request
  handling — your code must be thread/async-safe, unlike 1st gen's
  one-request-per-instance world. Set concurrency to 1 if your code isn't.
- **Eventarc payload limit is 512 KB** for event functions (HTTP functions get
  32 MB req/resp); trigger binding is asynchronous — allow minutes after creating
  a trigger before events flow.
- **Quotas**: 1000 functions+services per region; default max instances 100
  (raisable to 1000); 60 API writes per 60 s deploy rate (fixed).
- **Pricing shape** = Cloud Run pricing: per-request fee + vCPU-seconds +
  GiB-seconds, rounded up to 100 ms, in request-based (CPU only during requests —
  default, right for bursty/event work) or instance-based (CPU always on, no
  per-request fee) billing. Free tier ~2 M requests, 360 K GiB-s, 180 K vCPU-s
  monthly. Builds (Cloud Build) and image storage (Artifact Registry) bill
  separately. 1st gen keeps its own legacy pricing page.

## vs siblings

- **vs plain Cloud Run services**: same infra, same pricing, same YAML underneath.
  The function abstraction earns its keep when you want source-based deploys with
  managed base images, a per-language signature instead of a web server, and
  automatic CloudEvent unmarshalling. Choose a plain service when you need your own
  Dockerfile, sidecars, custom servers/protocols, or anything the buildpack path
  can't express. Detaching converts function → service one way, so starting as a
  function is low-risk.
- **vs App Engine**: App Engine is app-shaped (versions, services, app.yaml) and
  legacy-leaning; functions are event-shaped glue. New event-driven work belongs
  here; new web apps generally belong on Cloud Run proper.

## Related

[[gcp-cloud-run]], [[gcp-eventarc]], [[gcp-pubsub]], [[gcp-cloud-build]],
[[gcp-buildpacks]], [[gcp-artifact-registry]], [[gcp-cloud-scheduler]],
[[gcp-cloud-tasks]], [[gcp-cloud-storage]], [[gcp-workflows]], [[gcp-app-engine]],
[[gcp-iam]], [[gcp-secret-manager]], [[gcp-cloud-logging]]

Sources: https://docs.cloud.google.com/functions/docs, https://docs.cloud.google.com/functions/docs/concepts/version-comparison, https://docs.cloud.google.com/functions/docs/runtime-support, https://docs.cloud.google.com/functions/docs/writing, https://docs.cloud.google.com/functions/docs/deploy, https://docs.cloud.google.com/functions/docs/calling, https://docs.cloud.google.com/run/docs/deploy-functions, https://docs.cloud.google.com/functions/docs/bestpractices/retries, https://docs.cloud.google.com/functions/quotas, https://cloud.google.com/run/pricing (fetched 2026-07).
