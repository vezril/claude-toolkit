---
name: gcp-error-reporting
description: "Google Cloud Error Reporting — the error-triage layer over Cloud Logging: automatically recognizes, deduplicates, and groups error events from log entries (stack traces in textPayload/jsonPayload) or the report API, tracks counts and first/last seen per group, and notifies on new or reopened groups. Covers the log-entry formats that trigger recognition, supported stack-trace languages, grouping rules (exception type + top 5 frames), group statuses and muting, notification channels/throttling, and the regional/CMEK constraints that silently break it. Use when errors aren't showing up in Error Reporting, when formatting exceptions/logs so they get grouped, when wiring error notifications, or when deciding between Error Reporting and plain log-based alerting."
license: MIT
---

# GCP Error Reporting

The error-triage layer over Cloud Logging. It watches your logs, recognizes error
events (mostly by spotting stack traces), deduplicates them into **error groups**,
and gives each group a count, first-seen/last-seen timestamps, affected
service/version breakdown, recent samples with links back to the source log
entries, and a resolution status. Notifications fire on *new* groups — not on
every occurrence — which is the whole point: one bad deploy throwing 50k identical
exceptions is one row, not 50k alerts. For mobile client apps (Android/iOS),
Google points you to Firebase Crashlytics instead.

## The mental model

- **Errors arrive as log entries.** Either your platform/logger writes an
  exception with a stack trace to Cloud Logging, or you call the Error Reporting
  API's `report` method (`ReportedErrorEvent`), which itself generates a properly
  formatted log entry. There is no separate error datastore pipeline — it is a
  global service built on Cloud Logging.
- **Grouping is by stack signature.** Rules applied in order: (1) certain
  environment-specific exceptions group by exception type alone; (2) errors with
  a stack trace group by exception type + the 5 top-most frames (for nested
  exceptions, the innermost one decides); (3) errors without a stack trace group
  by message (first 3 literal tokens) + function name if present.
- **A group has a status**: open, acknowledged, resolved, or muted. An error
  landing in a *resolved* group reopens it and re-notifies; a *muted* group never
  notifies.

## How errors get in

- **Automatic on serverless/managed platforms**: App Engine (standard + flex),
  Cloud Functions, Cloud Run (exceptions on `stderr`), GKE, Compute Engine — no
  setup needed if exceptions reach Cloud Logging. Amazon EC2 works with config.
- **Recognized log shapes** (severity `ERROR`+, supported monitored resource
  types like `global`, `gce_instance`, `k8s_container`):
  - multi-line `textPayload` containing a stack trace;
  - `jsonPayload` with a stack trace in `stack_trace`, `exception`, or `message`
    (evaluated in that order);
  - a `ReportedErrorEvent`-shaped payload (`message` + `serviceContext`); for
    text-only messages with no stack trace, set
    `"@type": "type.googleapis.com/google.devtools.clouderrorreporting.v1beta1.ReportedErrorEvent"`
    and supply `context.reportLocation` (`filePath`, `lineNumber`, `functionName`).
- **Stack-trace parsing** supports the major language formats; client libraries
  exist for Go, Java, .NET, Node.js, Python, PHP, and Ruby.
- **Anything else**: call the API's `report` method directly (works even with an
  API key) — the catch-all for languages/formats the parser doesn't know.

## Operations

- **Notifications**: sent when an event can't be grouped with previous errors
  (new group) or when a resolved group reopens. Channels are Cloud Monitoring
  notification channels: email, Google Cloud Mobile App, Slack, webhooks.
  Configure from the Error Reporting console page ("Configure notifications";
  creating channels needs Monitoring Editor).
- **Triage**: set status per group (acknowledge/resolve/mute), filter by
  resource, text, and time range; each recent sample links via **View Logs** to
  Logs Explorer filtered on the error group ID.
- **Throttling**: max 5 notifications per group per 60 minutes, then a 6-hour
  silence; 5-minute notification suspension after manually resolving a group.

## Gotchas

- **Unparseable stack traces vanish silently** — an unsupported format isn't
  captured at all; the entry just sits in Cloud Logging as a plain error log.
  If errors "don't show up", suspect the format first (or force recognition with
  the `@type` field).
- **Sampling**: up to 1,000 errors/hour are sampled; beyond that, displayed
  counts are estimates.
- **CMEK breaks it**: Error Reporting can't analyze log buckets with
  customer-managed encryption keys enabled — on *any* bucket storing the entry.
- **Cross-project routing breaks it**: log entries routed to a bucket in a
  different project than where they originated aren't analyzed (bucket must be
  in the originating or receiving project per the routing rules).
- **Regional buckets limit notifications**: the error-event message is only
  included in a notification when the group comes from a `global`-region bucket.
- **Cost**: no separate Error Reporting SKU on the observability pricing page —
  you pay normal Cloud Logging ingestion/storage for the underlying log entries
  (and API-reported errors become log entries too).

## Related

- [[gcp-cloud-logging]] — the substrate: every error event is a log entry; recognition, buckets, CMEK, and routing all happen there.
- [[gcp-cloud-monitoring]] — supplies the notification channels; use it for threshold/rate alerting beyond "new group" events.
- [[gcp-cloud-trace]] — latency-side counterpart in the observability suite.
- [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-gke]] — platforms with automatic error capture.

Sources: https://docs.cloud.google.com/error-reporting/docs, https://docs.cloud.google.com/error-reporting/docs/setup, https://docs.cloud.google.com/error-reporting/docs/formatting-error-messages, https://docs.cloud.google.com/error-reporting/docs/grouping-errors, https://docs.cloud.google.com/error-reporting/docs/notifications, https://docs.cloud.google.com/error-reporting/docs/viewing-errors, https://docs.cloud.google.com/error-reporting/docs/regionalization, https://cloud.google.com/products/observability/pricing (fetched 2026-07).
