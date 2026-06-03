---
name: site-reliability-engineering
description: Site Reliability Engineering (SRE) — running production systems reliably by treating operations as a software problem, distilled from Google's *Site Reliability Engineering*. Covers embracing risk (reliability targets, not 100%), SLIs/SLOs/SLAs and error budgets, eliminating toil, monitoring (the four golden signals, symptom-based alerting), release engineering (canarying, progressive rollouts), on-call and incident management, blameless postmortems, simplicity, and capacity planning / addressing cascading failures. Use when defining reliability targets or SLOs, setting up monitoring/alerting, designing on-call or incident response, writing postmortems, reducing operational toil, or balancing feature velocity against reliability. The reliability/operations skill in the DevOps set; see devops for principles and ansible for infrastructure as code.
---

# Site Reliability Engineering

SRE is **what you get when you treat operations as a software engineering problem**: engineers build automation, set measurable reliability targets, and keep systems healthy at scale. The operations/reliability arm of [[devops]]. Source: Google's *Site Reliability Engineering: How Google Runs Production Systems* (free at sre.google/books).

Cross-links: [[devops]] (principles, CI/CD), [[ansible]] (provisioning/IaC), [[akka-insights]] (telemetry), [[akka-management]] (health checks, rolling updates), [[akka-cluster]] (cascading failure / split-brain), [[secure-coding]].

## Embracing risk — reliability is a feature, with a target

**100% reliability is the wrong target** — it's infeasible, ruinously expensive, and users can't tell the difference past a point (their ISP/phone is less reliable than your "four nines" already). So you choose an explicit reliability *target* and engineer to it, spending the difference on **feature velocity**. This reframing — reliability as a quantified, budgeted property — is the core of SRE.

## SLIs, SLOs, SLAs & the error budget

- **SLI (Service Level Indicator)** — a *measured* quantity about the service: request latency, availability (success rate), error rate, throughput, durability. Define it precisely (which events, which percentile).
- **SLO (Service Level Objective)** — a *target* for an SLI over a window (e.g. "99.9% of requests < 300 ms over 28 days"). The internal goal you engineer to. Pick SLOs from the **user's** perspective; don't over-promise.
- **SLA (Service Level Agreement)** — an external *contract* with consequences (credits/penalties) if missed. SLAs should be looser than SLOs.
- **Error budget** = `1 − SLO` (e.g. 0.1% unavailability). It's a **currency**: as long as budget remains, the team ships features freely; when it's **exhausted**, the policy is to **freeze risky launches and focus on reliability** until you're back in budget. This turns "dev vs ops" tension into a shared, data-driven decision and is the single most important SRE practice.

## Eliminate toil

**Toil** = work that is manual, repetitive, automatable, tactical, devoid of enduring value, and **scales linearly with the service**. SRE caps toil (Google's rule: **≤ 50%** of an SRE's time) so the rest goes to **engineering** that reduces future toil. The mandate is to **automate toil away**, not to do it faster by hand.

## Monitoring & alerting

- **The four golden signals** — monitor every user-facing system for **Latency**, **Traffic**, **Errors**, and **Saturation**. If you can measure only four things, measure these.
- **Alert on symptoms, not causes** — page on user-visible problems (SLO at risk), not on every internal metric. **Avoid alert fatigue**: every page should be **actionable** and urgent; route non-urgent issues to tickets/dashboards.
- **White-box** (internal metrics/traces) + **black-box** (probing like a user) monitoring. Burn-rate alerting off the error budget. Telemetry tooling: [[akka-insights]].

## Release engineering, simplicity & capacity

- **Release engineering** — hermetic, reproducible builds; CI/CD ([[devops]]); **progressive rollouts / canarying** (ship to a small slice, watch the golden signals, then expand); easy rollback. Make releases routine and low-risk.
- **Simplicity** — SRE actively fights complexity; reliable systems are simple systems ([[software-design]]). Boring is good.
- **Capacity planning** — forecast demand, provision with headroom, load-test; handle **cascading failures** with timeouts, retries-with-jitter+budgets, **circuit breakers**, load shedding, and graceful degradation (see [[akka-cluster]] reliable delivery / split-brain, [[akka-utilities]] circuit breaker).

## On-call & incident management

- **Sustainable on-call** — balanced rotations, bounded load, follow-the-sun where possible; on-call time is engineering time, not punishment.
- **Incident response** — a clear structure (an **Incident Commander**, ops/comms leads), defined severities, a single source of truth; optimize for **mean time to recovery (MTTR)** over blame.
- **Blameless postmortems** — after any significant incident, write a postmortem that focuses on **systemic causes and fixes, not individuals**. The culture must make it safe to be honest (psychological safety — [[devops]] Five Ideals); the goal is learning so the same failure can't recur. Track action items to completion.

## Always-apply defaults

1. **Set SLOs from the user's perspective and manage an error budget** — let it govern the velocity-vs-reliability trade-off rather than arguing.
2. **Measure the four golden signals; alert only on actionable, user-impacting symptoms.** Kill noisy alerts.
3. **Treat toil as a bug** — automate it; cap manual ops time so engineering compounds.
4. **Make releases small, canaried, and reversible**; keep systems simple.
5. **Run blameless postmortems** and design for failure (timeouts, retries-with-jitter, circuit breakers, graceful degradation) — assume things will break.
6. **Don't chase 100%** — pick the right number and stop gold-plating beyond it.

## How to use this skill

- **`references/slos-monitoring-incidents.md`** — defining SLIs/SLOs and error-budget policy concretely, the golden signals and burn-rate alerting, on-call structure, the incident-command model, and a postmortem template.

## Related

- [[devops]] — the principles, CI/CD, and culture SRE operationalizes (DORA's MTTR/change-failure-rate ↔ SRE reliability).
- [[ansible]] — infrastructure as code for reproducible provisioning.
- [[akka-insights]] (telemetry/metrics), [[akka-management]] (health checks, rolling updates), [[akka-cluster]] / [[akka-utilities]] (cascading-failure defenses: SBR, reliable delivery, circuit breaker), [[software-design]] (simplicity), [[secure-coding]].
- Source: *Site Reliability Engineering* (Beyer, Jones, Petoff, Murphy — Google), and *The Site Reliability Workbook*.
