---
name: gcp-pubsub
description: "Google Cloud Pub/Sub — global asynchronous messaging: topics fan out to independent pull/push/export (BigQuery, Cloud Storage, Bigtable) subscriptions; at-least-once delivery by default with ordering keys, exactly-once (pull-only, regional), dead-letter topics, filters, retention/seek/replay, and Avro/proto schemas. Use when designing service-to-service eventing or streaming ingestion on GCP, creating topics/subscriptions with gcloud, tuning ack deadlines and redelivery, wiring DLQs and push OIDC auth, replaying backlogs, or choosing between Pub/Sub, Cloud Tasks, and Eventarc."
license: MIT
---

# Google Cloud Pub/Sub

Global, serverless pub/sub messaging: publishers broadcast to **topics**, consumers receive via
**subscriptions**. Decouples producers from consumers with ~100 ms typical latency, per-message
parallelism (no partitions to manage), and throughput quotas measured in GB/s per region.

## The mental model

- **Topics fan out to independent subscriptions.** A message published to a topic is delivered to
  *every* attached subscription (up to 10,000 per topic). Each subscription is its own cursor plus
  its own delivery config: type (pull/push/export), ack deadline, retry policy, DLQ, filter,
  ordering, retention. Subscribers attached to the *same* subscription share the message load.
- **Ack deadlines drive redelivery.** A delivered message is leased; if not acked before the ack
  deadline (default 10 s, max 600 s), Pub/Sub redelivers it — to any subscriber on that
  subscription. Delivery is at-least-once: idempotent handlers are the baseline design assumption.
- **Global service, per-message routing.** One topic name worldwide; messages are stored in the
  region where they were published (restrictable via message storage policy). Publishers do not
  know who consumes ("implicit invocation") — that is the core contrast with Cloud Tasks.
- **Artifacts drive state**: the subscription's backlog, not your app, is the source of truth for
  what's unprocessed. Retention + seek let you rewind that cursor.

## Shapes (verified gcloud)

```sh
# Topic — optionally with schema validation, topic-level retention, CMEK, region pinning
gcloud pubsub topics create orders \
  --message-retention-duration=7d \
  --schema=order-schema --message-encoding=json \
  --message-storage-policy-allowed-regions=europe-west1

# Pull subscription with DLQ, exactly-once, and a retry-backoff policy
gcloud pubsub subscriptions create orders-worker --topic=orders \
  --ack-deadline=60 \
  --enable-exactly-once-delivery \
  --dead-letter-topic=orders-dlq --max-delivery-attempts=5 \
  --min-retry-delay=10s --max-retry-delay=600s

# Ordered subscription (publisher must also set an ordering key per message)
gcloud pubsub subscriptions create orders-ordered --topic=orders \
  --enable-message-ordering

# Push subscription with OIDC auth (endpoint must be HTTPS)
gcloud pubsub subscriptions create orders-push --topic=orders \
  --push-endpoint=https://svc.example.run.app/handler \
  --push-auth-service-account=pusher@PROJECT.iam.gserviceaccount.com \
  --push-no-wrapper   # optional: raw body instead of JSON envelope

# Export subscriptions — no worker fleet at all
gcloud pubsub subscriptions create orders-bq  --topic=orders --bigquery-table=proj:ds.orders
gcloud pubsub subscriptions create orders-gcs --topic=orders \
  --cloud-storage-bucket=my-archive --cloud-storage-max-duration=5m

# Replay: snapshot the ack state, later rewind to it (or to a timestamp)
gcloud pubsub snapshots create pre-deploy --subscription=orders-worker
gcloud pubsub subscriptions seek orders-worker --snapshot=pre-deploy
gcloud pubsub subscriptions seek orders-worker --time=2026-07-01T00:00:00Z
```

DLQ wiring needs IAM: the Pub/Sub service agent
(`service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com`) needs Publisher on the DLQ topic
and Subscriber on the source subscription — without both, attempts aren't even counted.

## Delivery semantics

- **At-least-once is the default.** Duplicates come from ack-deadline expiry, publisher retries
  (client retries mint new message IDs; service-side retries keep the same ID), and cross-region
  consumption. Design handlers idempotent first; reach for exactly-once second.
- **Ordering keys** serialize delivery per key, at a price: publish throughput is capped at
  **1 MBps per ordering key** (topic-wide throughput unaffected), all messages for a key must be
  published in the same region, and a nack/timeout redelivers the whole subsequent block for that
  key. Keys ≤ 1 KB.
- **Exactly-once delivery** (`--enable-exactly-once-delivery`): pull subscriptions only — push and
  export don't support it — and the guarantee is **within one region**. You get reliable ack
  results (acks can be confirmed, stale ack IDs fail with `INVALID_ARGUMENT`) and no redelivery
  after a successful ack. Cost: significantly higher publish-to-subscribe latency; use
  StreamingPull for throughput. It does not deduplicate publisher-side retries.
- **Push acks are HTTP status codes**: 102/200/201/202/204 = ack; anything else = nack and
  redelivery after the deadline. Pub/Sub ramps push rate with a slow-start algorithm (window grows
  on success, shrinks on failure). OIDC JWT lands in the `Authorization` header — validate audience
  and service account in the handler.

## Operational knobs

- **Retention & replay**: subscriptions keep unacked messages 7 days by default (max 31 d with
  `--message-retention-duration`); add `--retain-acked-messages` to keep acked ones replayable.
  Topic-level retention (max 31 d) covers all current *and future* subscriptions. Snapshots live
  max **7 days** (and must be ≥ 1 h from expiry at creation); `seek --time` needs retention on,
  `seek --snapshot` doesn't.
- **Filters** (`--message-filter`): attribute-based only (never the payload), ≤ 256 bytes, syntax
  `attributes.k = "v"`, `hasPrefix(...)`, `AND/OR/NOT`. **Immutable after creation.** Filtered-out
  messages are auto-acked — you skip outbound delivery fees but still pay delivery/seek-storage.
- **Export subscriptions** replace trivial "read → write to warehouse" workers: BigQuery
  (`--use-table-schema` to map fields), Cloud Storage (batched by `--cloud-storage-max-duration` /
  file prefix+suffix), Bigtable (Preview as of 2026-07). No exactly-once, no code, autoscaled.
- **Schemas**: Avro 1.11 or proto2/proto3, attached at topic creation with
  `--schema --message-encoding=json|binary`; non-conforming publishes are rejected. Up to 20
  revisions per schema, definition ≤ 300 KB, 10,000 schemas/project.
- **Subscription expiry**: idle subscriptions are deleted after 31 days by default — set
  `--expiration-period=never` for anything that matters.

## Gotchas

- An unconsumed subscription silently accrues backlog for 7 days, then messages age out — and an
  *idle* subscription is deleted at 31 days. Both losses look like "Pub/Sub dropped my messages."
- `--max-delivery-attempts` (5–100) is approximate: forwarding can happen a bit before or after,
  and the counter can reset to zero if pull subscribers go inactive.
- Ordering + heavy keys = throttling at 1 MBps/key; don't use one ordering key as a global FIFO.
- Filters can't be edited — plan them, or budget a new-subscription + snapshot-seek migration.
- Exactly-once ≠ exactly-once *processing* across regions or through push endpoints.
- **Pub/Sub Lite is gone**: deprecated 2024, turned down **June 30, 2026**. Migrate to standard
  Pub/Sub or Managed Service for Apache Kafka; never propose Lite in new designs.

## Quotas & pricing shape

- Limits: message ≤ **10 MB**; ≤ 100 attributes (key ≤ 256 B, value ≤ 1024 B); publish request
  ≤ 10 MB / 1,000 messages; StreamingPull ≤ 10 MBps per stream; 10,000 topics, subscriptions, and
  attached-subscriptions-per-topic per project. Regional throughput quotas: up to 4 GB/s publish
  and pull in large regions (push far lower: ~440 MB/s) — quotas, so raisable.
- Pricing is **throughput-based**: Message Delivery Basic at **$40/TiB** (publish + pull + push all
  count), first **10 GiB/month free**. Export subscriptions bill **$50/TiB** (BigQuery, Cloud
  Storage — no free tier there). Storage for retained/snapshot/topic-retained messages:
  **$0.27/GiB-month**. Small messages bill as 1 KB minimum — batch tiny messages.

## vs siblings

- **Cloud Tasks**: explicit invocation — the *producer* picks the endpoint, schedules delivery,
  rate-limits (queues, 500 QPS/queue), 1 MB payloads, one handler per task. Pub/Sub is implicit
  invocation: publisher ignorant of consumers, many subscriptions per event, 10 MB, no scheduled
  delivery, no per-queue rate cap. Task = "do this, then"; event = "this happened."
- **Eventarc**: routing layer for *Google-and-provider-emitted* events (Cloud Storage, audit logs,
  SaaS) into Cloud Run/GKE/Workflows, built on Pub/Sub under the hood. Use Eventarc to consume
  GCP events with filtering/CloudEvents format; use Pub/Sub directly for your own app-to-app
  messaging and firehose ingestion.
- **Cloud Scheduler → Pub/Sub** is the standard cron-fan-out trigger; **Dataflow** is the standard
  heavy-transform consumer when export subscriptions are too dumb.

## Related

[[gcp-cloud-tasks]], [[gcp-eventarc]], [[gcp-cloud-scheduler]], [[gcp-workflows]],
[[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-bigquery]], [[gcp-cloud-storage]],
[[gcp-dataflow]], [[gcp-bigtable]], [[gcp-iam]], [[gcp-cloud-monitoring]], [[cqrs-event-sourcing]]

Sources: https://docs.cloud.google.com/pubsub/docs/overview, https://docs.cloud.google.com/pubsub/docs/subscriber, https://docs.cloud.google.com/pubsub/docs/create-topic, https://docs.cloud.google.com/pubsub/docs/create-subscription, https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery, https://docs.cloud.google.com/pubsub/docs/ordering, https://docs.cloud.google.com/pubsub/docs/handling-failures, https://docs.cloud.google.com/pubsub/docs/replay-overview, https://docs.cloud.google.com/pubsub/docs/schemas, https://docs.cloud.google.com/pubsub/docs/push, https://docs.cloud.google.com/pubsub/docs/subscription-message-filter, https://docs.cloud.google.com/pubsub/docs/choosing-pubsub-or-cloud-tasks, https://docs.cloud.google.com/pubsub/quotas, https://cloud.google.com/pubsub/pricing, https://docs.cloud.google.com/pubsub/lite/docs, https://docs.cloud.google.com/sdk/gcloud/reference/pubsub/topics/create, https://docs.cloud.google.com/sdk/gcloud/reference/pubsub/subscriptions/create (fetched 2026-07).
