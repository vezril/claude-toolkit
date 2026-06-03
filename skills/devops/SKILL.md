---
name: devops
description: DevOps principles and practice — the culture and methods for fast, reliable software delivery, distilled from Gene Kim's *The Phoenix Project* (the Three Ways) and *The Unicorn Project* (the Five Ideals), framed for practice. Covers the CALMS model (Culture, Automation, Lean, Measurement, Sharing), flow / feedback / continual learning, value-stream thinking and the Theory of Constraints, the core practices (version-control-everything, CI/CD and deployment pipelines, infrastructure as code, automated testing, observability, small frequent releases, blameless postmortems), and the DORA delivery metrics. Use when reasoning about delivery flow, CI/CD pipelines, release process, team/ops culture, reducing lead time or unplanned work, or deciding how to organize for fast and safe delivery — the meta/entry skill that routes to ansible (infrastructure as code) and site-reliability-engineering (reliability/operations).
---

# DevOps (principles / meta)

DevOps is the **culture and set of practices** that let an organization deliver software **quickly, frequently, and reliably** by breaking down the wall between development and operations. This is the meta/principles skill — it captures the *why* (from Gene Kim's novels) and the practice map, then routes to the concrete skills: **[[ansible]]** (infrastructure as code / config management) and **[[site-reliability-engineering]]** (reliability and operations).

Cross-links: [[tdd]] (automated testing in the pipeline), [[secure-coding]] (DevSecOps), [[clean-code]]/[[software-design]] (the code that flows through it), [[akka-management]] (deploying/operating clustered services), [[os-virtualization]] (containers/k8s).

## CALMS — the five dimensions

A useful checklist for "are we actually doing DevOps?":
- **Culture** — shared ownership, collaboration, blamelessness; dev and ops (and security) on the same team toward the same goal.
- **Automation** — automate the repetitive: builds, tests, deploys, infrastructure, config (see [[ansible]]).
- **Lean** — small batches, limit work-in-progress, eliminate waste, optimize the whole flow.
- **Measurement** — instrument everything; decide with data (telemetry, the DORA metrics below).
- **Sharing** — knowledge, tooling, and responsibility flow across teams; no silos.

## The Three Ways (The Phoenix Project)

The novel's core model — the principles all DevOps practices derive from:

1. **Flow / Systems Thinking** (left → right) — optimize the **whole** value stream from dev to operations to the customer, not local silos. Make work **visible** (kanban), **reduce batch sizes and WIP**, and **never pass a known defect downstream**. The book frames work as **four types** (business projects, internal IT projects, changes, and the killer: **unplanned work**) and uses the **Theory of Constraints** — improvements anywhere but the **bottleneck** are an illusion; find and elevate the constraint.
2. **Amplify Feedback Loops** (right → left) — create **fast feedback** at every step so problems are seen and fixed immediately: pervasive telemetry, automated tests, **swarming** problems when they occur, and pushing **quality toward the source** (catch defects where they're created, not in production).
3. **Continual Experimentation and Learning** — a culture that rewards **experimentation, risk-taking, and learning from failure** (blameless), plus the discipline of **improving daily work** (improvement of daily work is more important than daily work itself) and deliberate **practice** to build mastery and resilience.

## The Five Ideals (The Unicorn Project)

The developer-centric companion to the Three Ways:
1. **Locality and Simplicity** — design systems and teams so a change can be made in one place by one team, without coordinating across many (loose coupling, [[software-design]] deep modules, bounded contexts — [[domain-driven-design]]).
2. **Focus, Flow, and Joy** — developers in flow, with fast feedback and minimal interruptions, doing meaningful work.
3. **Improvement of Daily Work** — pay down technical debt and improve the system continuously, not just feature work.
4. **Psychological Safety** — people can speak up, surface problems, and fail safely; the precondition for learning.
5. **Customer Focus** — relentlessly distinguish **core** (what customers value, your differentiator) from **context** (everything else); invest accordingly.

## Core practices (what to actually do)

- **Version-control everything** — code, config, infrastructure definitions, pipelines.
- **Continuous Integration / Continuous Delivery** — automated build + test on every commit; a **deployment pipeline** that promotes a tested artifact through environments; trunk-based development, small frequent merges. Pair with [[tdd]] for the test layer.
- **Infrastructure as Code** — define servers/config/infra declaratively and idempotently in version control → reproducible environments. The hands-on skill is **[[ansible]]** (also Terraform/containers/k8s — [[os-virtualization]]).
- **Small, frequent, reversible releases** — feature flags, canaries, blue-green/rolling deploys to make releases low-risk and routine (rolling updates for clustered apps: [[akka-management]]).
- **Observability** — logs, metrics, traces; alert on symptoms. Deep treatment in **[[site-reliability-engineering]]** (golden signals, SLOs).
- **Blameless postmortems & continuous learning** — every incident is a learning opportunity (see [[site-reliability-engineering]]).
- **Shift left on security** — DevSecOps; bake [[secure-coding]] and dependency scanning into the pipeline.

## DORA delivery metrics (how to measure)

The four research-backed indicators of delivery performance — track these to know if you're improving:
- **Deployment frequency** (how often you ship), **Lead time for changes** (commit → production), **Change failure rate** (% of deploys causing incidents), **Mean time to restore (MTTR)**. Elite teams ship frequently *and* reliably — speed and stability rise together, they don't trade off. (A fifth, **reliability**, ties into [[site-reliability-engineering]] SLOs.)

## How to use this skill

- **`references/principles.md`** — the Three Ways and the Five Ideals in depth (with the Theory-of-Constraints / four-types-of-work / unplanned-work framing), as a diagnostic lens for delivery problems.
- For **infrastructure as code / configuration management**, go to **[[ansible]]**.
- For **reliability, SLOs, monitoring, on-call, and incidents**, go to **[[site-reliability-engineering]]**.

## Always-apply notes

- Optimize **flow through the whole value stream**, not local efficiency; attack the **constraint** and **unplanned work** first.
- Make work and system state **visible**; decide with the **DORA metrics**, not opinion.
- Automate ruthlessly and keep everything in version control; small batches beat big-bang.
- Culture (psychological safety, blamelessness) is the foundation — practices fail without it.

## Related

- [[ansible]] — infrastructure as code / configuration management (the automation pillar).
- [[site-reliability-engineering]] — reliability, SLOs, observability, incident response (the operations pillar).
- [[tdd]] · [[clean-code]] · [[software-design]] · [[domain-driven-design]] — the engineering that produces flowable, reliable change.
- [[secure-coding]] — DevSecOps; [[akka-management]] / [[os-virtualization]] — deploying & operating services (k8s, rolling updates, containers).
- Sources: *The Phoenix Project* (Kim, Behr, Spafford) — the Three Ways; *The Unicorn Project* (Gene Kim) — the Five Ideals; plus the DevOps Handbook / DORA *Accelerate* research for the metrics.
