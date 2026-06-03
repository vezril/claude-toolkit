# SLOs, monitoring & incidents — concrete practice

Google *Site Reliability Engineering* + *The Site Reliability Workbook*. Practical detail behind the SKILL.

## Defining SLIs & SLOs

1. **Choose SLIs that reflect user happiness**, usually as a **ratio of good events / valid events** (e.g. proportion of HTTP requests served < 300 ms; proportion of requests that are non-5xx). Common categories: **availability**, **latency**, **throughput**, **correctness/quality**, **durability** (storage), **freshness** (data pipelines).
2. **Specify precisely**: which events count, measured **where** (load balancer vs server vs client), which **percentile** (p50/p95/p99 — tail latency matters), over which **window**.
3. **Set the SLO** as a target + window: "99.9% of valid requests succeed over a rolling 28 days." Start from current performance and what users actually need; **don't pick a number you can't sustain** and don't promise 100%.
4. **SLA** (if any) is looser than the SLO and carries business consequences; the SLO is your internal early-warning line.

**Error budget** = `1 − SLO` over the window (99.9% → 0.1% ≈ 43 min/month of unavailability). Write an **error-budget policy** agreed by dev + SRE + product: while budget remains, ship; when it's spent, **halt feature launches and prioritize reliability**. This makes the velocity/reliability trade-off automatic and unemotional.

## Monitoring & alerting

- **Four golden signals** per service: **Latency** (split successful vs failed — fast errors can hide slow successes), **Traffic** (demand: req/s, sessions), **Errors** (rate of failed requests, by type), **Saturation** (how full the most-constrained resource is: CPU/mem/IO/queue — and headroom).
- **Symptom vs cause**: page on **symptoms** that mean users are hurting (SLO burning), not on every internal cause. Diagnose causes from dashboards/traces after the page.
- **Burn-rate alerting**: alert when you're consuming the error budget too fast (e.g. multi-window multi-burn-rate: a fast-burn page for acute outages, a slow-burn ticket for gradual degradation). Tune to balance precision/recall and avoid noise.
- **White-box** (instrument the app: metrics/logs/traces) + **black-box** (probe externally like a user). Every **page must be actionable, novel, and urgent** — otherwise it's a ticket or a dashboard. Alert fatigue is a reliability risk itself.

## On-call

- Rotations sized so on-call is sustainable (Google targets a cap on incidents/shift so responders have time to do it well and to do engineering). Compensate/time-off-in-lieu; follow-the-sun across regions to avoid night pages.
- On-call engineers need **playbooks/runbooks**, good dashboards, and the authority to act. Time spent on-call is engineering time, not overhead.

## Incident management

- Declare an incident with a clear **severity**; assign an **Incident Commander (IC)** who coordinates (not necessarily the person debugging), plus **Ops** (hands-on-keyboard) and **Communications** leads for larger incidents.
- Maintain a **single source of truth** (incident doc/channel); communicate status to stakeholders on a cadence.
- Optimize for **MTTR**: mitigate first (roll back, failover, shed load, flip a feature flag), root-cause later. Practice with **drills/game days** so the process is muscle memory.

## Blameless postmortems

Trigger one for any incident meeting a threshold (user impact, data loss, prolonged outage, manual intervention). Structure:
- **Summary** · **Impact** (user-facing + duration + scope) · **Timeline** (UTC, detection → mitigation → resolution) · **Root cause(s)** (systemic — the "5 whys" land on process/design, never a person) · **What went well / what went poorly / where we got lucky** · **Action items** (concrete, owned, dated, tracked to completion — prevention > recurrence).
- **Blameless** is non-negotiable: assume everyone acted reasonably with the information they had; fix the **system** (missing guardrail, bad alert, fragile design), not the human. Psychological safety ([[devops]] Five Ideals) is what makes honest postmortems possible. Publish and share them widely (the Third Way's learning culture).

## Reliability engineering patterns

- Design against **cascading failures**: timeouts everywhere, **retries with exponential backoff + jitter** and a retry budget (never retry-storm), **circuit breakers** ([[akka-utilities]]), load shedding, graceful degradation, bulkheads.
- **Capacity**: forecast demand, provision with headroom, load-test to find the saturation point, and autoscale on real signals.
- **Reduce toil** by automating the top recurring manual tasks first; track toil as a metric.
- Prefer **simplicity** ([[software-design]]) — every bit of complexity is future unreliability. For clustered services, lean on [[akka-cluster]] (split-brain resolver, reliable delivery), [[akka-management]] (health checks, graceful rolling updates), and [[akka-insights]] (telemetry).
