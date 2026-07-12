---
name: gcp-cloud-tasks
description: "Google Cloud Tasks — managed task queues that dispatch individually-addressed HTTP tasks with per-queue rate limiting, configurable retries/backoff, scheduled delivery, and named-task dedup. Covers queue creation and tuning (max-dispatches-per-second, max-concurrent-dispatches, retry knobs), HTTP-target tasks with OIDC/OAuth service-account auth, the at-least-once + no-ordering contract, limits (1 MiB task, 30-day schedule horizon, 24h dedup window, 500/s per queue), pricing shape, and Tasks vs Pub/Sub vs Scheduler vs Eventarc. Use when queuing async work to an HTTP endpoint, throttling calls to a rate-limited backend, deferring/scheduling one-off work, smoothing traffic spikes, or choosing between Cloud Tasks and Pub/Sub."
license: MIT
---

# Google Cloud Tasks

Fully managed task queues: your code enqueues a task (an HTTP request description),
Cloud Tasks persists it and dispatches it to a worker endpoint at a controlled rate,
retrying with backoff until the worker returns 2xx or retry config is exhausted.

## The mental model

**Explicit invocation.** Unlike Pub/Sub (publish an event, whoever is subscribed reacts),
the Cloud Tasks *creator* decides exactly which endpoint runs each task, with what payload,
when, and under what rate/retry policy. A queue is a throttle + retry policy wrapped around
a bag of individually-addressed HTTP requests.

- **Task** = one unit of async work: URL + method + headers + body (+ optional name, schedule time, auth token config).
- **Queue** = dispatch policy: `max_dispatches_per_second`, `max_concurrent_dispatches`, retry/backoff config. System computes `max_burst_size` from the dispatch rate.
- **Target**: any HTTP endpoint (Cloud Run, Cloud Functions, GKE, Compute Engine, on-prem) or a legacy App Engine handler. Success = HTTP 200–299 before the deadline (10 min default, 30 min max for HTTP targets).
- **Contract**: at-least-once delivery, so handlers must be idempotent. Ordering is NOT guaranteed — never assume FIFO.

## Creating queues and tasks

```bash
# Queue (HTTP targets need no App Engine app; pick any supported region)
gcloud tasks queues create my-queue --location=us-central1

# Tune dispatch + retry
gcloud tasks queues update my-queue --location=us-central1 \
  --max-dispatches-per-second=10 --max-concurrent-dispatches=5 \
  --max-attempts=5 --max-retry-duration=4h \
  --min-backoff=1s --max-backoff=300s --max-doublings=5

# Enqueue an HTTP task with OIDC auth (task ID positional is optional; named tasks dedup)
gcloud tasks create-http-task my-task-id \
  --queue=my-queue --location=us-central1 \
  --url=https://worker-abc.a.run.app/handle \
  --method=POST --header=Content-Type:application/json \
  --body-content='{"job":42}' \
  --schedule-time=2026-08-01T00:00:00Z \
  --oidc-service-account-email=invoker@PROJECT.iam.gserviceaccount.com \
  --oidc-token-audience=https://worker-abc.a.run.app
```

Python client shape (Node/Go/Java analogous):

```python
task = tasks_v2.Task(
    http_request=tasks_v2.HttpRequest(
        http_method=tasks_v2.HttpMethod.POST,
        url=url,
        headers={"Content-type": "application/json"},
        body=json.dumps(payload).encode(),
        oidc_token=tasks_v2.OidcToken(
            service_account_email=sa_email, audience=audience),
    ),
)
client.create_task(parent=client.queue_path(project, location, queue), task=task)
```

**Auth**: use **OIDC** tokens (`oidc_token`) for handlers on Google Cloud (Cloud Run,
Cloud Functions); use **OAuth** access tokens (`--oauth-service-account-email`) only for
`*.googleapis.com` APIs. IAM needed: enqueuer has `roles/cloudtasks.enqueuer`;
Cloud Tasks needs `roles/iam.serviceAccountUser` on the token SA; the token SA needs the
handler's invoke role (e.g. `roles/run.invoker`).

## Dispatch and retry knobs

- **Rate**: `--max-dispatches-per-second` (hard ceiling 500/queue), `--max-concurrent-dispatches`. To go past 500/s, shard across multiple queues.
- **Retry**: interval starts at `min-backoff`, doubles `max-doublings` times, then grows linearly, then holds at `max-backoff`; stops at `max-attempts` (-1 = unlimited) or `max-retry-duration` (0 = unlimited), whichever hits first.
- **Scheduling**: `schedule_time` defers a task up to the 30-day horizon — good for one-off delayed work without a cron.

## Gotchas

- **Dedup is create-time only**: a named task can't be re-created for up to **24 hours** after completion/deletion — this dedupes enqueues, not deliveries (still at-least-once). Named-task creation also has higher latency; prefer auto-generated IDs unless you need dedup.
- **No ordering**, no FIFO, no exactly-once. Design handlers idempotent.
- **Limits**: task ≤ **1 MiB**; schedule horizon **30 days** ahead; task retention 31 days; 1,000 queues/region (quota); deleted queue name unusable for **7 days**; queues idle 30 days may go inactive.
- **Handler deadline**: 10 min default / 30 min max (HTTP). Long jobs should ack fast and run elsewhere.
- **queue.yaml vs API**: pick one queue-management method; mixing gcloud/API config with a deployed `queue.yaml` silently overwrites settings.
- **Pricing shape**: per billable operation = any API call or push delivery attempt, chunked at 32 KB (a 96 KB task = 3 ops; each retry attempt bills again). First 1M ops/month free, then ~$0.40/million; network egress extra.

## vs siblings

- **Pub/Sub**: implicit invocation / fan-out, subscriber controls consumption, ordering keys, 10 MB messages, global. **Tasks**: explicit endpoint per task, creator controls rate/retry/schedule, individual task management + dedup, regional. Event notification → Pub/Sub; controlled work execution → Tasks.
- **Cloud Scheduler**: cron — the *same* call fires on a recurring schedule. Tasks schedules *individual, distinct* payloads once each. Scheduler often enqueues into a Tasks queue.
- **Eventarc**: routes *provider* events (Cloud Storage, Audit Logs) to services; you don't enqueue explicit work items.
- **Workflows**: multi-step orchestration with state; a Tasks task is one fire-and-retry HTTP call.

## Related

[[gcp-pubsub]], [[gcp-cloud-scheduler]], [[gcp-eventarc]], [[gcp-workflows]],
[[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-iam]]

Sources: https://docs.cloud.google.com/tasks/docs, https://docs.cloud.google.com/tasks/docs/dual-overview, https://docs.cloud.google.com/tasks/docs/creating-queues, https://docs.cloud.google.com/tasks/docs/configuring-queues, https://docs.cloud.google.com/tasks/docs/creating-http-target-tasks, https://docs.cloud.google.com/tasks/docs/comp-pub-sub, https://docs.cloud.google.com/tasks/docs/quotas, https://cloud.google.com/tasks/pricing, https://docs.cloud.google.com/sdk/gcloud/reference/tasks/create-http-task (fetched 2026-07).
