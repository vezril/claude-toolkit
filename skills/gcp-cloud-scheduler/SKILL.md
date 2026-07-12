---
name: gcp-cloud-scheduler
description: "Google Cloud Scheduler — fully managed cron: unix-cron schedules firing HTTP/S endpoints, Pub/Sub topics, or App Engine handlers, with OIDC/OAuth service-account auth for HTTP targets, at-least-once delivery, and configurable exponential-backoff retries. Use when scheduling recurring jobs on GCP (nightly batch kicks, periodic Cloud Run/Functions invocations, cron-to-Pub/Sub fan-out), wiring --oidc-service-account-email auth, debugging 403s/duplicate runs/DST drift, or choosing Scheduler vs Cloud Tasks vs Workflows vs Eventarc."
license: MIT
---

# Cloud Scheduler

Fully managed cron on GCP: you define a schedule and a target, Google runs the clock. No
instances to keep alive, nothing to patch — each job is a row of config that fires at
minute granularity and retries on failure.

## The mental model

A **job** = schedule + time zone + target + retry policy. Three target types:

1. **HTTP/S** — any reachable endpoint; the workhorse for Cloud Run, Cloud Run functions,
   GKE ingress, or external URLs. Available in all supported regions.
2. **Pub/Sub** — publish a message body to a topic on schedule; decouples the clock from
   however many subscribers care.
3. **App Engine HTTP** — hits a relative URL on an App Engine service; jobs must live in
   the project's (fixed) App Engine region.

Schedules use standard five-field **unix-cron**: `minute hour day-of-month month day-of-week`,
with `*`, ranges (`1-5`), lists (`0,12`), steps (`*/2`), and `JAN-DEC`/`SUN-SAT` names.
`0 1 * * 0` = 01:00 every Sunday. Default time zone is `Etc/UTC`; override per job with
`--time-zone` (tz-database names). Jobs are serialized per job: execution *n+1* does not
start until execution *n* finishes.

## Creating jobs (gcloud)

HTTP target with OIDC service-account auth (the standard shape for Cloud Run/Functions):

```sh
gcloud scheduler jobs create http nightly-report \
  --location=us-central1 \
  --schedule="0 2 * * *" --time-zone="Etc/UTC" \
  --uri="https://report-svc-xyz.a.run.app/run" \
  --http-method=POST --message-body='{"scope":"daily"}' \
  --oidc-service-account-email=scheduler-invoker@PROJECT_ID.iam.gserviceaccount.com \
  --attempt-deadline=180s
```

Pub/Sub and App Engine targets:

```sh
gcloud scheduler jobs create pubsub tick --location=us-central1 \
  --schedule="*/5 * * * *" --topic=cron-topic --message-body="tick"

gcloud scheduler jobs create app-engine warmup --location=us-central1 \
  --schedule="0 0 * * 1-5" --relative-url="/cron-handler" --service=default
```

`gcloud scheduler jobs update http|pubsub|app-engine` takes the same flags; also
`pause`, `resume`, `run` (force an execution now), `list`, `describe`, `delete`.

**HTTP auth**: OIDC (`--oidc-service-account-email`) for your own services and anything
checking ID tokens (Cloud Run needs `roles/run.invoker` on that SA; 1st-gen functions
`roles/cloudfunctions.invoker`). OAuth (`--oauth-service-account-email`, default scope
`cloud-platform`) only for `*.googleapis.com` APIs, which expect access tokens. OIDC
audience defaults to the full target URI **including query params** — if your handler
validates audience, pin `--oidc-token-audience` to the bare URL. The Cloud Scheduler
service agent (`service-PROJECT_NUMBER@gcp-sa-cloudscheduler.iam.gserviceaccount.com`)
must keep `roles/cloudscheduler.serviceAgent`; revoking it turns authenticated targets
into mystery 403s (projects created before 2019-03-19 may need it granted manually).

## Gotchas, quotas, pricing

- **At-least-once**: rare duplicate executions happen; handlers must be idempotent. The
  `X-CloudScheduler-ScheduleTime` header carries the original slot time across retries —
  use it as a dedup key.
- **Failure = no acknowledgement** from the handler (non-2xx or deadline exceeded).
  Retries use exponential backoff: `--max-retry-attempts` (0-5, default 0),
  `--max-retry-duration` (default 0 = unlimited), `--min-backoff` (5s), `--max-backoff`
  (1h), `--max-doublings` (5). With retry settings at 0, a failed run just waits for the
  next slot. Retries can run **through** the next scheduled time, which is then skipped.
- **Deadlines**: `--attempt-deadline` bounds each attempt; HTTP executions hard-cap at
  30 minutes — longer work belongs behind Pub/Sub or Cloud Tasks.
- **DST**: schedules follow wall-clock time in the job's zone, so spring-forward/fall-back
  can skip or double-fire jobs. Schedule in `Etc/UTC` unless users genuinely need local time.
- **Quotas**: 1,000 jobs/region default (raisable to 5,000); payload ≤ 1 MB; admin API
  ~1,250 reads and 500 writes/min per project.
- **Pricing shape**: per job-month (~$0.10, prorated daily), executions free, 3 free jobs
  per **billing account** (not per project) — and paused jobs still bill.

## vs siblings

Scheduler answers exactly one question: "run this at these times." Cloud Tasks is the
inverse trigger — code enqueues work on demand, and you get per-queue rate limiting,
dispatch control, and task-level dedup that Scheduler lacks (a classic combo: Scheduler
fires one endpoint that fans out into a Tasks queue). Workflows is for *what happens
after* the trigger — multi-step orchestration with state, branching, and error handling;
a Scheduler job invoking a workflow is the standard "scheduled pipeline" shape. Eventarc
triggers on *events* (audit logs, Pub/Sub, direct events) rather than the clock. If the
trigger is time, start here; if it's demand, Tasks; if it's an event, Eventarc; if the
work itself is multi-step, put Workflows behind whichever trigger fits.

## Related

- [[gcp-cloud-tasks]] — demand-driven queues with rate/dispatch control
- [[gcp-workflows]] — multi-step orchestration Scheduler often triggers
- [[gcp-eventarc]] — event-driven (not clock-driven) triggering
- [[gcp-pubsub]] — the Pub/Sub target's other half
- [[gcp-cloud-run]] / [[gcp-cloud-functions]] / [[gcp-app-engine]] — common targets
- [[gcp-iam]] — service accounts and invoker roles for OIDC auth

Sources: https://docs.cloud.google.com/scheduler/docs, https://docs.cloud.google.com/scheduler/docs/overview, https://docs.cloud.google.com/scheduler/docs/creating, https://docs.cloud.google.com/scheduler/docs/http-target-auth, https://docs.cloud.google.com/scheduler/docs/configuring/cron-job-schedules, https://docs.cloud.google.com/scheduler/docs/configuring/retry-jobs, https://docs.cloud.google.com/scheduler/quotas, https://cloud.google.com/scheduler/pricing, https://docs.cloud.google.com/sdk/gcloud/reference/scheduler/jobs/create/http (fetched 2026-07).
