# Concurrency controls

Source: docs.aws.amazon.com (lambda-concurrency) + AWS's serverless agent skill. Fetched 2026-09. Four controls operate at different levels — the interactions are where mistakes happen.

## The four controls

1. **Reserved Concurrency** (function-scoped) — sets the function's **max** concurrent instances *and* reserves that capacity out of the account pool. Setting it to **0** fully throttles the function — an emergency kill switch. Use to protect a critical function, cap load on a downstream dependency, or shut something off fast.
2. **Provisioned Concurrency** (scoped to a published version or alias — **never `$LATEST`**) — pre-warms environments. Spills to on-demand (with cold starts) beyond the provisioned count. Combine with Application Auto Scaling at ~70% target utilization. Paid even when idle.
3. **Maximum Concurrency** (per SQS event source mapping, 2–1,000) — caps how many concurrent instances *that ESM* can drive. Reserves nothing — other triggers on the same function can still consume the function's total concurrency.
4. **Provisioned (Poller) Mode** (SQS and Kafka/MSK event source mappings) — dedicated event pollers with configurable min/max, for throughput standard ramp-up can't absorb fast enough. Per-poller capacity is an OR envelope: **SQS = 1 MB/s or 10 concurrent invokes**; **Kafka/MSK = 5 MB/s or 5 concurrent invokes**.

## Numbers and interactions

- **Account RPS quota = 10 × account concurrency** — an account-wide quota, not per-instance. Per-instance throughput is 1 / function duration, so a fast function can be RPS-limited well before it's concurrency-limited (a 50ms function at 20,000 RPS needs only 1,000 concurrency, but the account's 10× RPS quota throttles it at 10,000 RPS — request more account concurrency, not more reserved concurrency, to fix this).
- **Max reservable = account limit − 100.** Lambda always holds back 100 unreserved.
- Scaling rate: 1,000 new environments / 10s, per function.
- If both Reserved and Provisioned are set, **Provisioned ≤ Reserved**.
- Provisioned counts against the account limit **even while idle** — watch `ClaimedAccountConcurrency`.

| Combination | Allowed? |
|---|---|
| Reserved + Provisioned | Yes (Provisioned ≤ Reserved) |
| Reserved + ESM Maximum Concurrency | Yes (Reserved should be ≥ Σ Maximum Concurrency across ESMs) |
| Provisioned + ESM Maximum Concurrency / Provisioned Mode | Yes — different layers |
| **ESM Maximum Concurrency + ESM Provisioned Mode, same ESM** | **No — mutually exclusive** |
| **Provisioned Concurrency + SnapStart** | **No — mutually exclusive** |

At the limit: synchronous invokes get `429`; async invokes retry up to 6h then go to the DLQ/failure destination; event-source-mapping polling is throttled and messages simply stay at the source.

```bash
aws service-quotas request-service-quota-increase \
  --service-code lambda --quota-code L-B99A9384 --desired-value 5000
```

## Decision table

| Scenario | Reserved | Provisioned | ESM Maximum Concurrency | ESM Provisioned Mode |
|---|:---:|:---:|:---:|:---:|
| Protect a critical API / cap a downstream dependency | Yes | — | — | — |
| Eliminate cold starts, user-facing API | Optional | Yes | — | — |
| Multiple SQS queues, prevent one from hogging capacity | Yes | — | Yes | — |
| High-throughput SQS, low-latency | Optional | Optional | — | Yes |
| Kafka/SQS with spiky traffic | — | — | — | Yes |
| Predictable daily traffic curve | — | Yes + AutoScale | — | — |
| Emergency shutoff | Yes (= 0) | — | — | — |

## Common mistakes

1. **Reserved concurrency left at 0** from a past incident — blocks *all* invocations. First thing to check when a function throttles at low traffic.
2. **Reserved set too low** — reserve 50, actual need 80 → throttled at 51, even with spare account capacity.
3. **Reserved starves other functions** — it's subtracted from the account pool even while unused; be conservative.
4. **Provisioned with no auto scaling** — paying for idle off-peak, still spilling to cold starts on-peak.
5. **Provisioned on `$LATEST`** — silently doesn't work. Publish a version, create an alias, provision the alias.
6. **ESM Maximum Concurrency set higher than Reserved** — the ESM tries to scale to 100, the function caps at 50 anyway. Keep Reserved ≥ Σ Maximum Concurrency across all ESMs on that function.
7. **Confusing ESM Maximum Concurrency with a reservation** — it reserves nothing; an unrelated trigger (API Gateway, another ESM) can still consume all of the function's concurrency out from under it.
8. **Forgetting the 100-unit account buffer** when calculating max reservable.

## SAM / CDK property reference

| Control | SAM | CDK |
|---|---|---|
| Reserved | `ReservedConcurrentExecutions` | `reservedConcurrentExecutions` |
| Provisioned | `AutoPublishAlias` + `ProvisionedConcurrencyConfig.ProvisionedConcurrentExecutions` | `new lambda.Alias({ provisionedConcurrentExecutions })` — on the alias, not `$LATEST` |
| ESM Maximum Concurrency | `ScalingConfig.MaximumConcurrency` | `maxConcurrency` on `EventSourceMapping` |
| ESM Provisioned Mode | `ProvisionedPollerConfig.MinimumPollers`/`MaximumPollers` | `provisionedPollerConfig: { minimumPollers, maximumPollers }` |
| SnapStart | `SnapStart.ApplyOn: PublishedVersions` + `AutoPublishAlias` | `snapStart: lambda.SnapStartConf.ON_PUBLISHED_VERSIONS` |

Auto scaling: `alias.addAutoScaling({ minCapacity, maxCapacity })` then `.scaleOnUtilization({ utilizationTarget: 0.7 })`.
