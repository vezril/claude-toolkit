---
name: aws-eventbridge
description: "Building event-driven architectures with Amazon EventBridge, distilled from docs.aws.amazon.com and AWS's own serverless/messaging agent skills (fetched 2026-09). Covers event buses (default for AWS service events, custom per application domain, partner, cross-account), event pattern matching (exact/prefix/suffix/anything-but/numeric/exists/wildcard operators, AND across fields, OR within an array), rules vs Pipes (fan-out routing on a bus vs point-to-point source-to-target with built-in filter/enrich/transform and per-record retry+DLQ), target retry policy (24h/185 attempts default, MaximumEventAgeInSeconds 60-86400, MaximumRetryAttempts 0-185) and dead-letter queues (including the destination queue-policy step that's easy to skip), archive and replay (single source bus per archive, AES-256 encryption, ~10-minute delivery delay, the anti-replay-loop managed rule), EventBridge Scheduler (rate/cron/one-time schedules, 60-second invocation precision, flexible time windows — the recommended replacement for legacy scheduled rules, which don't work on custom/partner buses), and the schema registry. Use when designing an event-driven architecture, writing an EventBridge rule or event pattern, choosing Pipes vs Rules, wiring a Lambda/SQS/Step Functions target, setting up a DLQ on a rule or Pipe, debugging events that never reach their target, or scheduling a recurring or one-time task."
license: MIT
---

# Amazon EventBridge

How to route events reliably on AWS — the failure mode to design against is a rule that silently never fires, or a target that silently drops events with no trace. Distilled from `docs.aws.amazon.com` and AWS's serverless/messaging agent skills, fetched 2026-09. Cross-links: [[aws-sqs]] for the DLQ queue-policy pattern this skill also needs, [[aws-lambda]] for Lambda as an EventBridge target, [[secure-coding]] for the confused-deputy pattern behind every service-principal grant here.

## The mental model

An **event bus** receives events; **rules** on that bus match an **event pattern** and route matching events to one or more **targets**. This is *fan-out routing*, distinct from SQS/SNS point-to-point/pub-sub and distinct from Kinesis/MSK streaming (no replay window on the live bus — that's what Archive exists for).

```
Event source (AWS service, your app via PutEvents, a partner, another account)
        │
        ▼
   Event bus (default | custom | partner)
        │
        ▼  rule matches an event pattern (AND across fields, OR within one field's array)
        ▼
   Target(s): Lambda, SQS, SNS, Step Functions, Kinesis, API destination, another bus, …
```

**Pipes are the other primitive**, and answer a different question: not "route this event to N places on a bus" but "get events from *this one* stream/queue source to *that one* target, with filtering/enrichment/transformation in between, at lower cost because filtering happens before you're billed." See `pipes-targets-retries-and-dlq.md` for when to reach for which.

## Non-negotiables

1. **One dedicated event bus per application domain**, not the default bus. Reserve the default bus for AWS service events; mixing your application's events onto it makes pattern management and blast-radius control harder than it needs to be.
2. **Be precise with event patterns.** A broad pattern (or a rule whose target re-emits an event matching its own trigger pattern) risks an infinite loop — patterns are the actual access control here, not a suggestion.
3. **One target per rule** where practical — it keeps debugging and IAM scoping tractable. Multiple loosely-related targets on one rule make partial-failure debugging much harder.
4. **A DLQ on every target, always.** Without one, a target that keeps failing simply drops the event after retries exhaust — no error surfaces anywhere.
5. **The DLQ needs its own queue policy, not just a `DeadLetterConfig` pointer.** Attaching a DLQ to a rule target is not sufficient by itself — the destination SQS queue must have a policy granting `events.amazonaws.com` (or `pipes.amazonaws.com`) `sqs:SendMessage`, scoped with `aws:SourceArn` (the rule or pipe ARN) and `aws:SourceAccount`. Skip this and the DLQ silently receives nothing. See [[aws-sqs]]'s `dlq-and-lambda-integration.md` for the exact policy shape.
6. **Prefer EventBridge Scheduler over legacy scheduled rules** for anything new — better scalability, a wider target surface, flexible time windows, and (unlike scheduled rules) it works on custom and partner buses too.
7. **Test patterns before deploying them** — the EventBridge Sandbox exists specifically so a bad pattern doesn't surprise you in production.
8. **Service-principal bus/queue policies always need `aws:SourceArn`/`aws:SourceAccount`** — the same confused-deputy pattern applies here as everywhere else a service principal gets a grant.

## Quick reference

| Setting | Default | Range |
|---|---|---|
| Target retry duration | 24 hours | Configurable via `MaximumEventAgeInSeconds`: 60 – 86,400 |
| Target retry attempts | 185 | Configurable via `MaximumRetryAttempts`: 0 – 185 |
| Scheduler invocation precision | ±59 seconds of the scheduled time | Tighten with a flexible time window setting |
| Archive delivery delay | Not instant | Wait ~10 minutes before replaying, to be sure all events landed |
| Archive `EventCount`/`SizeBytes` accuracy | Reconciled every 24 hours | Recent archive activity may lag in these fields |
| Archive retention | Indefinite by default | Configurable per archive |

## References

- `references/rules-and-buses.md` — event bus types, event pattern syntax and operators, rule design best practices.
- `references/pipes-targets-retries-and-dlq.md` — Pipes vs Rules decision table, the target retry policy, DLQ setup and the queue-policy trap.
- `references/archive-replay-and-scheduler.md` — archiving and replaying events, EventBridge Scheduler's three schedule types, and the schema registry.
