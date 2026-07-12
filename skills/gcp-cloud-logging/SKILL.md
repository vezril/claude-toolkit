---
name: gcp-cloud-logging
description: "Google Cloud Logging — centralized log management: every entry hits the Log Router, sinks (inclusion + exclusion filters) route copies to log buckets (_Required immutable 400d, _Default 30d configurable), BigQuery, Cloud Storage, or Pub/Sub; log views scope read access; the Logging query language (=, :, =~, severity>=, resource.type/logName anchors); log-based metrics feeding Cloud Monitoring alerts; Log Analytics (SQL over buckets via BigQuery); and Cloud Audit Logs — the four types (Admin Activity always-on/free, Data Access off-by-default except BigQuery, System Event, Policy Denied) with org-level aggregated sinks for SIEM export. Use when designing log routing/retention, writing Logging queries, enabling Data Access audit logs, building log-based alerts, cost-tuning ingestion, or setting up centralized audit/forensics pipelines."
license: MIT
---

# GCP Cloud Logging

Fully managed log storage, search, analysis, and alerting for Google Cloud (plus AWS and
80+ other sources via Bindplane). Two products in one skin: operational logging for your
workloads, and Cloud Audit Logs — the tamper-evident record of who did what to your cloud.

## The mental model

- **Every log entry hits the Log Router.** Each project, folder, org, and billing account has
  its own router. Sinks evaluate every incoming entry independently; each matching sink sends
  a *copy* to its destination. Routing is fan-out, not pipeline — one entry can land in five
  places. The router buffers against transient outages but is not storage.
- **A sink = inclusion filter + optional exclusion filters + destination.** Entry must match
  the inclusion filter AND no exclusion filter. Destinations: log buckets, BigQuery datasets,
  Cloud Storage buckets (JSON files, long-term archive), Pub/Sub topics (Splunk/Datadog/SIEM
  bridge), or another Google Cloud project (one-hop limit).
- **Two system buckets exist in every project.** `_Required` holds Admin Activity, System
  Event, and Access Transparency audit logs: 400-day retention, immutable, undeletable, and
  free. `_Default` catches everything else via an empty-filter sink: 30-day default retention,
  configurable 1–3650 days, and its sink can be edited or disabled. You can add up to 100
  user-defined buckets per project (region is fixed at creation).
- **Log views scope read access.** Every bucket has views; grant users a view instead of the
  whole bucket to show only a subset (e.g., one app's logs). Field-level access controls can
  redact sensitive fields like PII.
- **Exclusion filters are the cost lever — but not a quota lever.** Excluded entries are never
  stored (never billed for ingestion), yet they're applied *after* the Logging API receives
  the entry, so API quota is still consumed and user-defined log-based metrics still count them.
- **Sinks are prospective only.** No sink ever routes entries received before it existed, and
  entries older than the retention period (or >24h in the future) are discarded on arrival.

## The Logging query language

Boolean expressions over log-entry fields; case-insensitive except regexes and the operators
`AND`/`OR`/`NOT` (which must be uppercase; `-` works as `NOT`, `AND` is implicit between terms).

- **Operators:** `=` `!=` `<` `<=` `>` `>=` (comparison), `:` (substring, the workhorse),
  `=~` / `!~` (RE2 regex). `severity >= ERROR` works because severities are ordered.
- **Anchor on indexed fields first** — `resource.type`, `logName`, `severity`, `timestamp`,
  `insertId`, `trace`, `labels`, `httpRequest.status` — then narrow into `textPayload` /
  `jsonPayload.*`. Payload keys are case- and format-sensitive (`jsonPayload.endTime` is not
  `jsonPayload.end_time`).
- **Functions:** `SEARCH("hello world")` (tokenized full-text), `log_id("stdout")` (log name
  without URL-encoding), `sample(insertId, 0.01)`, `ip_in_net(jsonPayload.ip, "10.0.0.0/8")`,
  `regexp_extract(...)`, `cast(...)`.

```text
resource.type = "gce_instance" AND severity >= ERROR
resource.type = "cloud_run_revision" AND jsonPayload.message =~ "^timeout"
logName = "projects/my-proj/logs/cloudaudit.googleapis.com%2Factivity"
log_id("cloudaudit.googleapis.com/data_access") AND protoPayload.methodName : "Get"
timestamp >= "2026-07-01T00:00:00Z" AND httpRequest.status >= 500
```

Gotchas: log names embed URL-encoded slashes (`%2F`) — or use `log_id()` to skip encoding;
mixing `AND`/`OR` needs explicit parentheses; a missing payload field silently fails every
comparison (`NOT missingField=x` is TRUE, `missingField!=x` is FALSE); JSON null is
`NULL_VALUE`; array fields compare element-wise with OR semantics.

## Log-based metrics and alerting

- **Counter** (entries matching a filter) or **distribution** (histogram of a numeric field,
  e.g., latency) metrics, surfaced in Cloud Monitoring as
  `logging.googleapis.com/user/METRIC_NAME` — chart them, alert on them.
- Project-scoped metrics see all logs the API receives (even excluded ones); bucket-scoped
  metrics see only what lands in that bucket — use these to meter cross-project aggregation.
- Data starts at metric creation — never retroactive. Extract labels from fields to split
  time series. User-defined log-based metrics bill as Monitoring custom metrics.
- The fast path from "bad log line" to "page": counter metric on the filter, then an alerting
  policy in Cloud Monitoring.

## Log Analytics

- Upgrade a bucket to Log Analytics (a.k.a. Observability Analytics) and query it with SQL —
  grouping, aggregation, joins with trace data — powered by BigQuery. Upgrade is irreversible;
  pre-upgrade entries backfill over days.
- Optionally create a **linked BigQuery dataset**: read-only access to the same data, no
  BigQuery storage or ingestion cost — you pay only BigQuery analysis charges per query.
  This replaces the old pattern of sinking everything into your own BigQuery dataset when
  all you wanted was SQL.
- Limits: buckets with field-level access controls can't be queried via Log Analytics (linked
  datasets and Logs Explorer still work); duplicates aren't auto-collapsed as in Logs Explorer.

## Cloud Audit Logs

Four log types, written per project/folder/org, under `cloudaudit.googleapis.com/`:

| Type | Log id | Default | Cost posture |
|---|---|---|---|
| Admin Activity | `activity` | Always on — cannot be disabled or excluded | Free |
| Data Access | `data_access` | **Off** by default (exception: BigQuery — on) | Billable and voluminous |
| System Event | `system_event` | Always on (Google-initiated changes, e.g., autoscaling) | Free |
| Policy Denied | `policy` | On; can't be disabled, but *can* be excluded via filters | Billable |

- **Enabling Data Access logs** is IAM-policy configuration (`auditConfigs`), not a Logging
  API call: per service or `allServices`, choosing `ADMIN_READ` / `DATA_READ` / `DATA_WRITE`,
  with optional exempted principals. Config inherits org → folder → project and is cumulative —
  a child can add log types but never switch off what a parent enabled. Editing via
  `setIamPolicy` must preserve `bindings` and `etag`, or you can wipe access to the project.
- Reading Data Access logs in the `_Default` bucket requires **Private Logs Viewer**
  (`roles/logging.privateLogViewer`); plain `roles/logging.viewer` doesn't see them.
- **Org-wide SIEM export:** create an org-level **aggregated sink** matching
  `logName : "cloudaudit.googleapis.com"` routing to a central bucket, BigQuery, or Pub/Sub.
  Non-intercepting sinks copy and let child sinks run too; **intercepting** sinks swallow
  matching entries (they still reach `_Required`) — use those to stop teams from re-routing
  or paying for audit logs project-by-project.
- **Doctrine: audit logs are your forensics.** `_Required` is the backstop — immutable,
  400 days, free, unbypassable even by intercepting sinks. For longer retention or legal
  hold, route to Cloud Storage *before* the incident; sinks can't reach back in time. Lock
  down who holds `logging.privateLogViewer`, and use CMEK on buckets if compliance demands it.

## Gotchas and pricing shape

- **You pay per GiB ingested into billable buckets** (list ~$0.50/GiB) past a free allotment
  (~50 GiB/project/month). `_Required` is free. Extended retention beyond the default adds a
  small per-GiB-month charge (~$0.01). Routing to BigQuery/GCS/Pub/Sub is billed by the
  destination service, not by Logging. Verify current numbers — the shape is stable, the
  digits move.
- The classic cost blowups: enabling `DATA_READ` on a chatty service org-wide, verbose debug
  logging from GKE/Cloud Run flowing into `_Default`, and load-balancer request logs. Fix with
  exclusion filters on the `_Default` sink — but remember metrics/quota still see the traffic.
- **Sink writer identity:** each sink gets a service account (writer identity); the destination
  owner must grant it write access (e.g., `roles/bigquery.dataEditor` on the dataset,
  `roles/storage.objectCreator` on the GCS bucket). Aggregated sinks in orgs fail silently-ish
  without this — misconfigured sinks emit error logs and alert Essential Contacts.
- Shortening a bucket's retention gives a 7-day grace period before deletion; a bucket's
  region can never change after creation.
- GCS-destination sinks can take hours to start delivering; BigQuery destinations must be
  writable datasets (linked datasets are read-only and can't be sink targets).

## Related

[[gcp-cloud-monitoring]], [[gcp-cloud-trace]], [[gcp-error-reporting]], [[gcp-bigquery]],
[[gcp-pubsub]], [[gcp-cloud-storage]], [[gcp-iam]], [[gcp-vpc-service-controls]],
[[gcp-gke]], [[gcp-cloud-run]], [[gcp-cloud-sdk]], [[site-reliability-engineering]]

Sources: https://docs.cloud.google.com/logging/docs, https://docs.cloud.google.com/logging/docs/routing/overview, https://docs.cloud.google.com/logging/docs/buckets, https://docs.cloud.google.com/logging/docs/view/logging-query-language, https://docs.cloud.google.com/logging/docs/logs-based-metrics, https://docs.cloud.google.com/logging/docs/log-analytics, https://docs.cloud.google.com/logging/docs/audit, https://docs.cloud.google.com/logging/docs/audit/configure-data-access, https://docs.cloud.google.com/logging/docs/audit/best-practices, https://cloud.google.com/stackdriver/pricing (fetched 2026-07).
