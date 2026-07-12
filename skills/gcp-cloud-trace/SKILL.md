---
name: gcp-cloud-trace
description: "Google Cloud Trace — distributed tracing for GCP: a trace is a tree of spans sharing a trace ID across services; context propagates via W3C traceparent (recommended) or legacy X-Cloud-Trace-Context headers; instrument with OpenTelemetry (vendor-neutral, the docs' recommended path) exporting OTLP to the Telemetry API — directly or via an OTel Collector — while the legacy Cloud Trace API and Google-specific Trace exporters are being migrated away from; some GCP front doors (Cloud Load Balancing, App Engine, Cloud Run, Apigee, Endpoints) participate in propagation and Cloud Run / App Engine standard auto-send request latency spans; head-based sampling (ParentBased + TraceIdRatioBased) controls cost at $0.20/million spans after 2.5M free; Trace explorer gives heatmaps, percentile latency, waterfall/DAG views, and log correlation. Use when adding distributed tracing to GCP services, wiring OpenTelemetry export, choosing sampling rates, debugging broken/missing traces across queues, or analyzing latency in Trace explorer."
license: MIT
---

# GCP Cloud Trace

Google Cloud's distributed tracing system: collects latency data from applications and
displays it in near real-time in the console. You send spans (via OpenTelemetry), GCP
stitches them into traces, and the Trace explorer turns them into latency analysis.
Stored span data is retained for 30 days.

## The mental model

- **A trace is one end-to-end operation; a span is one timed step inside it.** All spans in
  a trace share a 128-bit trace ID. Each span has its own span ID, a parent span ID (null
  for the root span), start/end timestamps, a name, and key-value attributes — use
  OpenTelemetry Semantic Conventions for attribute names. The result is a tree: root span
  = the inbound request, children = RPC calls, DB queries, handlers.
- **Traces only connect if context propagates.** The trace ID + parent span ID + sampling
  decision must travel with every hop. Two header formats:
  - `traceparent` — the W3C Trace Context standard, hyphen-separated, hex IDs. Recommended.
  - `X-Cloud-Trace-Context` — Google's legacy format: `TRACE_ID/SPAN_ID;o=OPTIONS` (32-hex
    trace ID, *decimal* span ID, `o=1` sampled / `o=0` not).
- **Two ingestion APIs.** The **Telemetry API** (OTLP-shaped, recommended) has no span-count
  cap (regional bandwidth quotas instead) and much more generous span limits. The **Cloud
  Trace API** is the legacy proprietary path with daily span quotas and tight limits. New
  instrumentation should land on the Telemetry API.
- **Some GCP front doors participate for free.** Services known to propagate or create
  context: Apigee, App Engine, Cloud Endpoints, Cloud Load Balancing, Cloud Run, Cloud
  Scheduler, Cloud Tasks, Pub/Sub (support varies — "Cloud Trace isn't responsible for
  context propagation"). Cloud Run and Cloud Run functions auto-send request latency spans;
  App Engine standard did so on legacy runtimes (Java 8, Python 2, PHP 5). These
  auto-generated spans give you front-door latency even with zero instrumentation — but
  they are shallow one-span traces until your code joins in.

## Instrumentation

- **OpenTelemetry is the path** (docs: prefer "an open-source, vendor-neutral instrumentation
  framework, such as OpenTelemetry" over vendor APIs). Instrumentation samples exist for Go,
  Java, Node.js, Python, and C++.
- **Preferred shape:** app SDK → OTLP exporter → **OpenTelemetry Collector** (sidecar/agent)
  → Telemetry API. Direct OTLP export from the app to the Telemetry API also works; the
  collector buys batching, retries, and tail-sampling options.
- **Legacy status (as of 2026-07):** the Google-specific Cloud Trace exporters and client
  libraries are superseded — docs actively steer to "Migrate from Trace exporter to OTLP
  endpoints"; no hard shutdown date is published, but treat the old exporters as
  maintenance-only and start new work on OTLP.
- **Auth:** default scopes cover Compute Engine, Cloud Run, and App Engine automatically.
  GKE needs the `trace.append` scope if you narrowed scopes (Autopilot: Workload Identity
  Federation). Off-GCP, use a service account with `roles/cloudtrace.agent`.

## Sampling

- **Head-based is the model:** the decision is made when the request arrives and rides the
  context (`o=` flag / traceparent flags) so children honor it. In OTel, combine
  `ParentBased` (respect upstream's decision) with `TraceIdRatioBased` (probabilistic rate
  for new roots).
- **Each GCP service makes its own sampling decision** for auto-generated spans — typically
  a small default rate plus honoring the parent's decision as a hint. Don't expect every
  request through a load balancer or Cloud Run to be traced.
- **Always-sample is a cost/quota decision, not a default.** Full sampling on high-QPS
  services can blow through quotas and storage cost limits fast.
- **Tail-based sampling isn't native.** Cloud Trace decides nothing after the fact; run the
  OpenTelemetry Collector's tail-sampling processor in front if you want "keep all errors,
  1% of the rest".

## Analysis

- **Trace explorer** is the main console surface: span filters (service name, span name,
  status, duration, span kind, App Hub attributes), an attribute filter bar
  (e.g. `/http/status_code: 200`), and direct trace-ID lookup.
- **Heatmap + percentiles:** span density heatmap for spotting latency outliers; p50/p90/
  p95/p99 breakdowns; a Spans table sortable by duration and a Grouped table aggregated by
  service + span name.
- **Waterfall and DAG:** a selected trace renders as a timeline (default) or directed
  acyclic graph of the call hierarchy, with latency bars and log indicators per span.
- **Log correlation:** span flyout shows attributes, events, stack traces, and logs matched
  by `trace_id`/`span_id`, with jump-through to Logs Explorer. Write those fields into your
  structured logs to get it.
- **SQL analytics:** query trace data with SQL via the Observability Analytics page or
  BigQuery for questions the explorer can't answer.

## Gotchas

- **Broken traces almost always mean broken propagation.** Anything that drops headers —
  proxies, hand-rolled HTTP clients, and especially async hops — orphans the downstream
  spans into separate traces. Queues are the classic case: carry trace context in message
  attributes (Pub/Sub, Cloud Tasks) and restore it in the consumer; the docs only cover
  synchronous HTTP/gRPC propagation, so the queue leg is on you.
- **Span limits differ wildly by API.** Cloud Trace API: 32 attributes/span, 256-byte
  values, 128 events, 3M–5B spans/day quota. Telemetry API: 1,024 attributes, 64 KiB
  values, 256 events, no span-count cap. Oversized attributes get truncated silently —
  another reason to be on the Telemetry API.
- **Cost is per span ingested:** $0.20/million spans after the first 2.5 million per
  billing account per month (charges on ingestion, not storage). Your bill is
  traffic × sampling rate × spans-per-request — a chatty auto-instrumentation stack can
  10x spans-per-request overnight. Spans auto-generated by App Engine standard, Cloud Run,
  and Cloud Run functions are non-chargeable and don't consume API quota.
- **Retention is 30 days, not configurable.** Export to BigQuery (via the SQL analytics
  path) if you need longer-horizon latency analysis.

## Related

[[gcp-cloud-monitoring]], [[gcp-cloud-logging]], [[gcp-error-reporting]] — the rest of the
observability suite (metrics/alerts, logs + correlation, exception grouping).
[[gcp-cloud-run]], [[gcp-app-engine]], [[gcp-load-balancing]], [[gcp-apigee]],
[[gcp-endpoints]] — front doors that create or propagate trace context.
[[gcp-pubsub]], [[gcp-cloud-tasks]], [[gcp-cloud-scheduler]] — async hops where you must
propagate context manually. [[gcp-bigquery]] — SQL over trace data.
[[site-reliability-engineering]] — latency SLOs that tracing debugs.

Sources: https://docs.cloud.google.com/trace/docs, https://docs.cloud.google.com/trace/docs/overview, https://docs.cloud.google.com/trace/docs/setup, https://docs.cloud.google.com/trace/docs/traces-and-spans, https://docs.cloud.google.com/trace/docs/trace-context, https://docs.cloud.google.com/trace/docs/trace-sampling, https://docs.cloud.google.com/trace/docs/finding-traces, https://docs.cloud.google.com/trace/docs/quotas, https://cloud.google.com/stackdriver/pricing (fetched 2026-07).
