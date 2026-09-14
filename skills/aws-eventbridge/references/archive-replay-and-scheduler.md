# Archive, replay, Scheduler, and schema registry

Source: docs.aws.amazon.com (eventbridge/latest/userguide, scheduler/latest/UserGuide). Fetched 2026-09.

## Archive and replay

An **archive** captures a filtered copy of the events flowing through a **single source event bus** (you cannot change the source bus after creating the archive, but you can have multiple archives per bus with different filters).

- Optionally filter what's archived with an event pattern (same syntax as rules); unfiltered captures everything on the bus.
- Retention: configurable in days, or **indefinite by default**.
- Encrypted at rest with AES-256 under an AWS-owned key by default.
- **Delivery isn't instant** — there can be a delay between an event landing on the bus and it appearing in the archive. Wait roughly **10 minutes** before replaying recently-archived events, to be confident everything you expect has actually arrived.
- `DescribeArchive`'s `EventCount`/`SizeBytes` fields reconcile on a **24-hour** cycle — don't treat a just-archived event as reflected in those counters immediately.

**Replay** re-sends archived events back onto the source bus (optionally scoped to specific rule ARNs via `FilterArns`), as if they'd just arrived. To prevent a replay from being captured by the same archive again (which would create a growing loop of replayed data), EventBridge automatically adds a managed rule to the source bus that excludes any event carrying a `replay-name` field (the marker EventBridge stamps on replayed events) — you don't have to build this exclusion yourself.

## EventBridge Scheduler (prefer this over legacy scheduled rules)

Legacy **scheduled rules** (a rule with a `schedule` pattern instead of an event pattern) still work, but AWS explicitly recommends **EventBridge Scheduler** for new work — it's more scalable, supports a wider range of target API operations and AWS services, and (unlike scheduled rules) **works on custom and partner buses**, not just the default.

Three schedule types:

| Type | Shape |
|---|---|
| Rate-based | `rate(5 minutes)` — recurring, fixed interval |
| Cron-based | `cron(0 12 * * ? *)` — recurring, calendar-based |
| One-time | A specific date/time/timezone — fires exactly once |

- **All schedule types invoke with ~60-second precision** — a schedule set for `1:00` fires somewhere in `1:00:00`–`1:00:59` (absent a flexible time window). Don't rely on sub-minute scheduling accuracy.
- **Flexible time windows** let you spread invocation over a window instead of a fixed instant — useful for smoothing a fleet of schedules that would otherwise all fire in the same second.
- Retry limits and maximum retention for failed invocations are configurable per schedule, same spirit as a rule's target retry policy.
- Time zone and daylight-saving handling is explicit per schedule — set the time zone you actually mean, not an assumption of UTC.

## Schema registry (brief)

EventBridge can auto-discover the JSON schema of events flowing through a bus (a **discoverer**, `CreateDiscoverer`), including optionally from **cross-account** senders (`CrossAccount: true`, the default). This generates downloadable schema artifacts (and code bindings in several languages) you can use to strongly type event producers/consumers, rather than hand-writing pattern matches against an unknown event shape. Reach for it when building or maintaining event contracts across teams, not for a single-team, single-bus setup where you already know every event shape.

## Pitfalls

- Replaying archived events immediately after they're generated, before the ~10-minute delivery window has elapsed — some may not have landed in the archive yet.
- Reading `EventCount`/`SizeBytes` on a very recent archive and treating them as current — they reconcile daily.
- Building a new scheduled task with legacy scheduled rules instead of Scheduler, then discovering it can't target a custom bus.
- Assuming sub-minute precision from any EventBridge-based schedule.
