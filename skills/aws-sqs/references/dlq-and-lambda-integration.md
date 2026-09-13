# Dead-letter queues and Lambda integration

Source: docs.aws.amazon.com (SQS dead-letter queues, Lambda event source mappings) + AWS's messaging/serverless agent skills. Fetched 2026-09.

## Dead-letter queues and redrive policy

A DLQ is an ordinary SQS queue that other queues redirect failed messages to. Configure it via a **redrive policy** on the *source* queue:

```json
{ "deadLetterTargetArn": "<dlq-arn>", "maxReceiveCount": 5 }
```

`maxReceiveCount` is how many times a message can be received (not necessarily *failed* — received without being deleted) before it moves to the DLQ. Set it too low (e.g. 1) and a single transient failure exiles a message; set it generously enough to absorb real transient errors while still catching genuinely poison messages.

**The DLQ must be the same queue type as the source** — a FIFO source needs a FIFO DLQ, a Standard source needs a Standard DLQ. Mixing types is rejected at configuration time.

For Standard queues specifically, once `maxReceiveCount > 3` and a message has been received 3+ times without deletion, SQS moves it to the **back of the queue** rather than leaving it at the front blocking younger messages — `ApproximateAgeOfOldestMessage` then reflects the next message that hasn't crossed that threshold, not the stuck one.

**Redrive allow policy** (on the DLQ itself) controls which source queues may use it: allow all (default), allow a specific list (up to 10 source ARNs), or deny all.

## The queue-policy trap for service-driven DLQs

Attaching a DLQ to an **EventBridge rule target** or an **SNS subscription** is not enough by itself — **the DLQ also needs a queue policy** granting the sending service principal `sqs:SendMessage`, or the DLQ silently drops the failure with no error and no message:

- **EventBridge:** `PutTargets` with `DeadLetterConfig.Arn=<dlq-arn>`, **plus** an SQS queue policy statement allowing `Service: events.amazonaws.com` to `sqs:SendMessage`, scoped with `aws:SourceArn` = the specific rule ARN.
- **SNS:** `SetSubscriptionAttributes` with `RedrivePolicy={"deadLetterTargetArn":"<dlq-arn>"}`, **plus** an SQS queue policy allowing `Service: sns.amazonaws.com`, scoped by the topic ARN.

Both follow the same shape as the general confused-deputy pattern in `security-and-ops.md` — always pair a service-principal grant with `aws:SourceArn`/`aws:SourceAccount`.

## Lambda event source mapping (SQS as a trigger)

Lambda long-polls the queue and invokes your function **synchronously** with a batch — this is a pull-based integration, distinct from SNS pushing directly and asynchronously.

| Parameter | Default | Notes |
|---|---|---|
| `BatchSize` | 10 | Standard: up to 10,000. FIFO: up to 10 |
| `MaximumBatchingWindowInSeconds` | 0 | 0–300; not usable with FIFO; requires ≥1s if `BatchSize` > 10 |
| `MaximumConcurrency` | — | 2–1,000, per-mapping cap; reserves nothing else on the function |
| `FilterCriteria` | — | Filters on the message `body` only; **unmatched messages are automatically, permanently deleted** — not retried, not DLQ'd |
| `FunctionResponseTypes` | — | Set to `ReportBatchItemFailures` |

Invocation triggers on **any** of: batching window expires, batch size reached, or payload hits 6 MB.

**Scaling (Standard queues):** starts at **5** concurrent invocations, ramps ~**300/minute**, defaults to a ceiling of **1,250**. A sudden backlog is *not* absorbed instantly — it takes several minutes to ramp up. For workloads that can't tolerate that delay, Lambda's Provisioned (Poller) Mode starts higher and scales much faster (see the aws-lambda skill's `event-sources.md`).

**Scaling (FIFO queues):** concurrency is the *lower* of (distinct `MessageGroupId` count, `MaximumConcurrency`) — more groups is the lever for more parallelism, same as with any FIFO consumer.

**Partial batch failures:** set `FunctionResponseTypes: [ReportBatchItemFailures]` and return failed `messageId`s in `batchItemFailures`; an empty/null response means full success. Returning a malformed response (bad key name, null identifier) or throwing an unhandled exception causes the **entire batch** to retry, not just the genuinely failed messages.

```yaml
# SAM
Events:
  SQSEvent:
    Type: SQS
    Properties:
      Queue: !GetAtt MyQueue.Arn
      BatchSize: 10
      FunctionResponseTypes: [ReportBatchItemFailures]
      ScalingConfig: { MaximumConcurrency: 50 }
```

Always pair the source queue with a redrive policy — a message that keeps failing eventually needs to leave the queue via the DLQ, not retry forever.

## Pitfalls

- DLQ configured on an EventBridge rule or SNS subscription with no matching queue policy — failures vanish with no trace.
- `maxReceiveCount` set to 1 — a single transient blip exiles otherwise-fine messages.
- FIFO source queue paired with a Standard DLQ (or vice versa) — rejected, but worth knowing why.
- Expecting an SQS-triggered Lambda to instantly absorb a backlog spike — the ramp takes minutes on Standard scaling.
- `ReportBatchItemFailures` configured but the handler throws instead of returning identifiers — full batch retry regardless of the config.
