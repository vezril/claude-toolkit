---
name: gcp-cloud-monitoring
description: "Google Cloud Monitoring (formerly Stackdriver): the metrics/dashboards/alerting/uptime/SLO backbone of Google Cloud observability. Covers the time-series model (metric type x monitored resource x labels), metrics scopes for multi-project views, alerting policy anatomy (alignment, aggregation, retest windows, notification channels, snooze), uptime checks and burn-rate SLO alerts, PromQL as the query language (MQL console support ended July 22, 2025), Managed Service for Prometheus on the same Monarch backend, the Ops Agent for VM telemetry, and the pricing shape (per-MiB ingestion vs per-sample Prometheus metering, alerting charges from 2026). Use when designing dashboards or alert policies, debugging flapping alerts, defining SLOs/error budgets, wiring Prometheus or Ops Agent ingestion, controlling metric cardinality or monitoring spend, or choosing between Cloud Monitoring native and Prometheus-style workflows."
license: MIT
---

# Google Cloud Monitoring

Cloud Monitoring collects metric data from Google Cloud, AWS, on-prem, and application sources, then lets you chart it (dashboards), watch it (alerting policies), probe it from outside (uptime checks, synthetic monitors), and manage reliability against targets (SLO monitoring). It is one product family with Cloud Logging, Cloud Trace, and Error Reporting under "Google Cloud Observability." Everything below is docs-truth as of July 2026.

## The mental model

**A time series is: metric type × monitored resource × one combination of label values.**

- **Metric type** — a named measurement, e.g. `compute.googleapis.com/instance/cpu/utilization`. ~6,500 built-in types. Each has a *kind* (`GAUGE` = point-in-time, `DELTA` = change over an interval, `CUMULATIVE` = running total that resets) and a *value type* (int64, double, bool, string, distribution).
- **Monitored resource** — where the data came from: VM instance, GKE container, Cloud SQL database, etc. (~270 types). Every point belongs to exactly one resource.
- **Labels** — key-value dimensions on both the metric and the resource. Cardinality = the number of unique label-value combinations; **total time series = metric cardinality × resource cardinality**. Monitoring only stores series that actually receive data, but the multiplication is what you must control (see Gotchas).
- **User-defined metrics** live under `custom.googleapis.com/*` (Monitoring API, OpenTelemetry) or `prometheus.googleapis.com/*` (Prometheus-format ingestion). The Metrics Management page shows per-metric volume and which metrics nobody reads — your first stop for cost cleanup.

**Metrics scopes make monitoring multi-project.**

- Every project hosts a metrics scope; by default it sees only itself.
- Add other projects as monitored resource containers (up to 375 officially supported). The *scoping project*'s dashboards, alerting policies, uptime checks, and synthetic monitors then see all of them, filterable by `project_id`.
- Pattern: one `prod-monitoring` scoping project watching all prod projects — alerts and dashboards defined once, centrally. Viewing needs only Monitoring Viewer; changing a scope needs Monitoring Admin on both sides.

**Alerting = a condition evaluated against time series + notification channels.** A policy watches data; when its condition is met, Monitoring opens an *incident* and notifies the channels. When the condition clears, the incident auto-closes and a closure notification is sent.

**Managed Service for Prometheus is not a separate database.** It is Prometheus-compatible ingestion — managed collection on GKE (recommended), self-deployed collectors (drop-in Prometheus binary replacement), the OpenTelemetry Collector, or the Ops Agent's Prometheus receiver — writing into **Monarch, the same backend as Cloud Monitoring**. Both metric families are queryable together, from the console or from Grafana pointed at the Monitoring API; existing Grafana dashboards work unchanged. Minimum scrape interval 5 s; 24-month retention at no extra storage cost.

**PromQL is the query lingua franca.** It queries Google Cloud system metrics, custom metrics, and Prometheus metrics alike — in Metrics Explorer (Code tab), dashboards, and alerting policies. Cloud Monitoring metric names map to PromQL by replacing the first `/` with `:` and other specials with `_`:

```
compute.googleapis.com/instance/cpu/utilization
→ compute_googleapis_com:instance_cpu_utilization
```

**MQL is deprecated.** As of **July 22, 2025**, Google Cloud customer support for MQL ended and MQL is gone from the console for new charts, dashboards, and alerting policies. Existing MQL artifacts keep working and can still be created via the API, but new work should use PromQL (or the builder UI / filter-based API conditions).

## Dashboards

- Custom dashboards are JSON documents (`dashboards.create` API) — keep them in git and deploy with Terraform (`google_monitoring_dashboard`); the console builder is fine for exploration but drifts.
- Chart widgets take either builder-style (filter + alignment + aggregation) or PromQL queries; out-of-the-box dashboards exist for VMs, GKE, and most Google Cloud services.
- Charts in a scoping project span every monitored project — group or filter by `project_id` to split environments.

## Alerting policies: the part everyone gets wrong

Policy anatomy: 1–6 **conditions** (AND/OR combiner), **notification channels** (email, Slack, PagerDuty, SMS, webhooks, Pub/Sub; up to 16 per policy), and a **documentation** block (Markdown + variables) that lands in the notification — put the runbook link there. Up to 2,000 policies per metrics scope.

Condition types:

- **Metric threshold** — value above/below a threshold for the retest window.
- **Metric absence** — no data arrives for the retest window (max 24 h). This is your "the thing silently died" detector.
- **Forecast** — predicted to cross the threshold within a 1 h–7 d forecast window (disk-full predictions).
- **PromQL-based** — arbitrary PromQL: ratios, metric math, dynamic thresholds. Avoid filtering on system metadata labels in these.
- **Log-match** and **SQL-based** conditions also exist (single-condition policies).

The three knobs that actually determine behavior:

1. **Alignment period + per-series aligner** — raw points are regularized into buckets (e.g. `rate`, `mean`, `max` over 5 min). DELTA/CUMULATIVE metrics *must* be aligned to be comparable. Longer alignment period = smoother data = slower detection (worse MTTD) but fewer false alarms.
2. **Cross-series aggregation (reducer + group-by)** — collapses many series into the ones you alert on. No group-by = one giant aggregate that hides a single bad instance; group-by everything = one incident per series, alert storms.
3. **Retest window (duration)** — how long the condition must hold before the incident opens. `0s` fires on a single aligned point; `5m`+ requires sustained violation.

**The classic flapping alert**: alignment period too short (noisy aligned values) + duration `0s` + threshold sitting inside the metric's normal oscillation band. Fixes, in order:

- Lengthen the alignment period or use a smoothing aligner (`mean` over a longer window).
- Add a nonzero retest window.
- Move the threshold out of the noise band.
- Switch to a ratio or burn-rate style condition instead of a raw gauge.

Every smoothing step adds detection latency — the trade-off is explicit, pick per severity.

**Snooze, not disable**: for maintenance windows, snooze the policy (scheduled, scoped). There is no "only alert during business hours" setting.

## Uptime checks and SLO monitoring

**Uptime checks** probe HTTP/HTTPS/TCP endpoints from external checkers (redirects followed; HTTPS checks also compute SSL cert expiry). Public checks run from at least 3 checker locations worldwide; private checks reach resources behind your VPC. Alert with an uptime-check condition — the sensible default is "at least two regions failing for at least one minute," which keeps one flaky checker location from paging you. **Synthetic monitors** are the heavier sibling: scripted browser/API journeys backed by Cloud Run functions, billed per execution.

**SLO monitoring**, per the docs:

- Define a *service* (auto-detected for GKE, App Engine, Cloud Service Mesh/Istio; or custom).
- Pick an **SLI**: availability (good responses / all responses) or latency (calls under threshold / all calls); request-based or windows-based.
- Set an **SLO**: e.g. 99.9% over a rolling 1–30-day or calendar week/month period; up to 500 SLOs per service. Don't set it higher than users need — tighter targets cost real money.
- **Error budget** = (1 − goal) × eligible events. 99% over 100,000 requests = 1,000 allowed failures.

**Alert on burn rate, not on the SLI.** Burn rate = how fast you consume error budget relative to the compliance period (rate 1 = exactly exhausting budget at period end). The standard pattern is two policies: a **fast-burn** alert (high burn-rate threshold, short lookback — pages a human, something is on fire) and a **slow-burn** alert (low threshold, long lookback — files a ticket, you'll miss the SLO in days). This catches both outages and slow rot without threshold-flapping.

## Ops Agent

The **Ops Agent** is the single agent for Compute Engine VMs: Fluent Bit for logs + the OpenTelemetry Collector for metrics and traces, replacing the legacy Monitoring and Logging agents. Unified YAML config; Linux (RHEL/Rocky, Debian, Ubuntu, SLES) and Windows Server; Arm supported. It ships curated third-party integrations (MySQL, PostgreSQL, MongoDB, nginx, Apache, Kafka, Redis, …) and a **Prometheus receiver**, so VM-local exporters flow into Managed Service for Prometheus without running a Prometheus server. Agent-collected metrics are chargeable (below); GKE has its own built-in collection — the Ops Agent is a VM story.

## Gotchas

- **Cardinality is the cost and quota multiplier.** Never use user IDs, IP addresses, timestamps, or raw URLs as label values — each combination is a new time series counted against active-series limits (200k custom / 1M Prometheus per resource) and, for Prometheus, billed as samples per series per scrape.
- **Pricing has two meters — know which you're on.** Non-Prometheus chargeable metrics (custom, agent, workload) bill **per MiB ingested**, tiered: $0.2580/MiB after the free 150 MiB/month, dropping at 100k and 250k MiB. Prometheus-format metrics bill **per million samples**: $0.06/M tapering to $0.024/M above 500B samples. Sample-based cost scales with scrape interval × series count, not payload size — halving scrape frequency halves the bill. Google Cloud system metrics are free.
- **Alerting stops being free.** Effective August 2026 (enforcement no sooner than Sept 1, 2026): **$0.35/month per metric reference in a policy** plus **$0.50 per million points returned by condition queries**. A PromQL condition touching many metrics, or a fine-alignment condition over thousands of series, now has a bill. Audit policy count and query breadth before then.
- **Read API calls bill by time series returned** ($0.50/M beyond 1M free, since Oct 2, 2025) — a wide `timeSeries.list` from a dashboard-as-code tool or exporter gets expensive. Writes are free.
- **Retention has downsampling cliffs.** 24-month retention for most metrics, but custom/workload data keeps full resolution only 6 weeks (then 10-min buckets); Prometheus data keeps raw resolution 1 week, 1-min for 5 weeks, then 10-min. Fine-grained forensics older than that are gone — export to BigQuery if you need them.
- **Metric-absence beats threshold for dead emitters.** A threshold condition on a metric that stops arriving never fires. Pair critical thresholds with an absence condition or an uptime check.
- **Uptime checks bill per execution** ($0.30/1,000 past 1M/project/month) and each selected region is a separate execution — a 1-minute global check costs ~6× a single-region one.
- **Write limits**: one point per 5 seconds per time series, 200 time series per write call — batch custom-metric writers accordingly.

## Related

- [[gcp-cloud-logging]] — log-based metrics feed Monitoring; log-match alert conditions; shared Observability pricing page.
- [[gcp-cloud-trace]] — latency traces; Ops Agent/OTel export traces alongside metrics.
- [[gcp-error-reporting]] — error aggregation; its notifications complement metric alerts.
- [[site-reliability-engineering]] — SLI/SLO/error-budget theory that SLO monitoring and burn-rate alerts implement.
- [[gcp-gke]] — managed Prometheus collection, GKE control-plane metrics, built-in observability.
- [[gcp-compute-engine]] — the Ops Agent's home; VM dashboards.
- [[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]] — serverless system metrics and SLO-eligible services; synthetic monitors run on Cloud Run functions.
- [[gcp-bigquery]] — long-term metric export target; SQL-based alert conditions.
- [[gcp-pubsub]] — notification-channel type for programmatic incident handling.
- [[gcp-iam]] — Monitoring Viewer/Editor/Admin roles; metrics-scope changes need Admin on both sides.

Sources: https://docs.cloud.google.com/monitoring/docs, https://docs.cloud.google.com/monitoring/api/v3/metric-model, https://docs.cloud.google.com/monitoring/alerts, https://docs.cloud.google.com/monitoring/settings, https://docs.cloud.google.com/monitoring/uptime-checks, https://docs.cloud.google.com/stackdriver/docs/solutions/slo-monitoring, https://docs.cloud.google.com/monitoring/promql, https://docs.cloud.google.com/monitoring/mql, https://docs.cloud.google.com/stackdriver/docs/managed-prometheus, https://docs.cloud.google.com/monitoring/agent/ops-agent, https://docs.cloud.google.com/monitoring/quotas, https://cloud.google.com/stackdriver/pricing (fetched 2026-07).
