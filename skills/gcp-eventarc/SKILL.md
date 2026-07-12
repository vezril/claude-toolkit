---
name: gcp-eventarc
description: "Google Cloud Eventarc — managed event routing for event-driven architectures: providers emit events, triggers (Standard) or bus/pipeline/enrollments (Advanced) filter them, destinations (Cloud Run, Workflows, GKE, internal HTTP endpoints) receive them as CloudEvents over Pub/Sub transport. Covers direct events vs Cloud Audit Logs events, gcloud trigger shapes, at-least-once delivery, retries/dead-lettering via the underlying Pub/Sub subscription, Standard vs Advanced editions, quotas, and pricing shape. Use when wiring 'when X happens in GCP, run Y', choosing Eventarc vs raw Pub/Sub vs Cloud Tasks vs Cloud Scheduler, debugging missing/duplicate event deliveries, or designing a central event bus with filtering and CEL transformation."
license: MIT
---

# GCP Eventarc

Eventarc is Google Cloud's managed eventing layer: it routes state-change events from
Google services, custom apps, and third parties to your compute, handling delivery,
auth, retries, and observability. As of 2026-07 it ships as **two editions**: **Eventarc
Standard** (the original trigger model, one source → one destination) and **Eventarc
Advanced** (introduced 2025: a central bus with many-to-many pipelines, CEL
transformation, larger events). Same CloudEvents contract on the wire for both.

## The mental model

**Providers emit events → triggers filter → destinations receive CloudEvents.**

- **Providers**: Google services emit either **direct events** (first-class, e.g.
  `google.cloud.storage.object.v1.finalized`) or the **long tail via Cloud Audit Logs**
  (`google.cloud.audit.log.v1.written` filtered by `serviceName` + `methodName` — this is
  how you react to almost any admin/data operation on ~any GCP API). Plus Pub/Sub
  messages and third-party providers (Datadog, Check Point, etc., preview). Docs' rule:
  when both a direct and an audit-log event exist, **prefer the direct event**.
- **Triggers (Standard)**: exact-match filters on event type + attributes; each trigger
  binds one filter set to one destination. Under the hood every Standard trigger is
  **Pub/Sub transport** — Eventarc creates a topic + push subscription
  (`eventarc-REGION-…`) for you; retry and dead-letter behavior live on that subscription.
- **Bus/pipeline/enrollment (Advanced)**: sources publish to one **message bus** per
  project/region; **enrollments** (CEL filter on any attribute) bind bus messages to
  **pipelines**, which can transform (CEL), convert schemas, and deliver — including to
  Pub/Sub topics, other buses, and cross-project destinations (Standard can't).
- **Destinations**: Cloud Run services/functions (Advanced adds jobs), Workflows, public
  GKE endpoints, internal HTTP endpoints in a VPC. Delivery is an HTTP POST in
  **CloudEvents** format (binary content mode; body = payload, `ce-*` headers = context).
- **Delivery contract**: **at-least-once, unordered**, 24 h retention, exponential
  backoff retries. Your handler must be idempotent and return 2xx to ack.

## Trigger creation shapes (Standard, gcloud)

Direct event (Cloud Storage → Cloud Run):

```bash
gcloud eventarc triggers create storage-trigger \
    --location=us-central1 \
    --destination-run-service=my-service \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=MY_BUCKET" \
    --service-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

Audit-log event (the long tail — here: BigQuery, or any service/method pair):

```bash
gcloud eventarc triggers create auditlog-trigger \
    --location=us-central1 \
    --destination-run-service=my-service \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.audit.log.v1.written" \
    --event-filters="serviceName=storage.googleapis.com" \
    --event-filters="methodName=storage.objects.create" \
    --event-filters-path-pattern="resourceName=/projects/_/buckets/MY_BUCKET/objects/*" \
    --service-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

Pub/Sub message (new topic auto-created, or bring your own with `--transport-topic`):

```bash
gcloud eventarc triggers create pubsub-trigger \
    --location=us-central1 \
    --destination-run-service=my-service \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
    --transport-topic=projects/PROJECT_ID/topics/MY_TOPIC \
    --service-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

Useful extras: `--destination-run-path` (non-root endpoint),
`--event-data-content-type=application/json|application/protobuf`. Workflows and GKE
destinations use analogous destination flags — check `gcloud eventarc triggers create --help`
rather than guessing. Setup invariants: enable `eventarc.googleapis.com` (+
`eventarcpublishing`, `pubsub`, Cloud Logging for audit triggers); trigger SA needs
`roles/eventarc.eventReceiver` and, for Cloud Run, `roles/run.invoker`; for
Storage direct events the Storage service agent needs `roles/pubsub.publisher`.

## Gotchas

- **Propagation lag**: a trigger is created instantly but takes **up to ~2 minutes** to
  start filtering; audit-log triggers are the slowest to initialize. Events fired in
  that window are lost. Audit-log events also add end-to-end latency vs direct events.
- **Audit-log triggers need the logs on**: for many `serviceName`/`methodName` pairs you
  must enable **Data Access audit logs** for that service in IAM & Admin → Audit Logs,
  or nothing ever fires. Known quirk: Compute Engine audit events are emitted from
  `us-central1` regardless of resource location. Audit-log triggers aren't available in
  dual-/multi-region locations.
- **Filters are exact-match and immutable**: no wildcards/regex in `--event-filters`
  (path patterns only via `--event-filters-path-pattern` on `resourceName`); you cannot
  edit a trigger's source filters — create a new trigger, delete the old.
- **At-least-once, unordered**: expect duplicates and out-of-order delivery; design
  idempotent handlers keyed on the CloudEvents `id`.
- **Dead-lettering is a Pub/Sub feature** (Standard only): find the Eventarc-created
  subscription (`eventarc-REGION-…`), attach a dead-letter topic and tune retry backoff
  (default 10 s → 600 s exponential) **on the subscription**. Undelivered events are
  discarded after the 24 h retention window if no DLQ. Advanced has no Pub/Sub DLQ.
- **Deleting a trigger deletes topics it created** — don't hang other consumers off an
  Eventarc-managed topic; use `--transport-topic` with a topic you own instead.
- **Size limits**: 512 KB/event Standard, 1 MB Advanced; 500 triggers per project per
  location (Standard); Advanced: 1 bus per project/region, 100 pipelines, 100 enrollments.
- **Pricing shape**: Standard — Google-source and Pub/Sub-source events are **$0** at the
  Eventarc layer (first 50 k events/month free; third-party sources $1/M; events metered
  per 64 KiB chunk), but you pay normal **Pub/Sub transport** rates (10 GiB/month free)
  plus destination compute. Advanced — ~$1.00/M messages published to the bus +
  $0.50/M per pipeline delivery + $0.40/M transformations, metered per 16 KiB chunk.

## vs siblings

- **Raw Pub/Sub**: you own topics/subscriptions and message shape; no CloudEvents
  envelope, no Google-service event catalog. Eventarc = Pub/Sub + provider integration +
  filtering + IAM plumbing. If services publish to each other and you control both ends,
  plain Pub/Sub is simpler and cheaper to reason about.
- **Cloud Tasks**: explicit task queues you enqueue into — rate limits, scheduled
  delivery, per-task control. Push-style "something happened" fan-out is Eventarc;
  "do this specific unit of work later, throttled" is Tasks.
- **Cloud Scheduler**: time-driven (cron), not event-driven. Scheduler often *feeds*
  Eventarc/Pub/Sub pipelines.
- **Workflows**: an orchestrator, not a router — Eventarc triggers commonly *start* a
  workflow, which then makes ordered, stateful calls.

## Related

[[gcp-pubsub]], [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-workflows]],
[[gcp-cloud-tasks]], [[gcp-cloud-scheduler]], [[gcp-gke]], [[gcp-cloud-storage]],
[[gcp-cloud-logging]], [[gcp-application-integration]], [[gcp-iam]]

Sources: https://docs.cloud.google.com/eventarc/docs, https://docs.cloud.google.com/eventarc/docs/overview, https://docs.cloud.google.com/eventarc/advanced/docs/choose-product-edition, https://docs.cloud.google.com/eventarc/docs/run/create-trigger-storage-gcloud, https://docs.cloud.google.com/eventarc/standard/docs/run/route-trigger-cloud-audit-logs, https://docs.cloud.google.com/eventarc/standard/docs/run/route-trigger-cloud-pubsub, https://docs.cloud.google.com/eventarc/standard/docs/event-providers-targets, https://docs.cloud.google.com/eventarc/docs/retry-events, https://docs.cloud.google.com/eventarc/docs/quotas, https://cloud.google.com/eventarc/pricing (fetched 2026-07).
