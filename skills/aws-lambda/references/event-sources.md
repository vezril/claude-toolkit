# Event source mappings

Source: docs.aws.amazon.com (lambda/latest/dg) + AWS's serverless agent skill. Fetched 2026-09. Assumes the basics (SNS is a direct async push, not an ESM; unmatched SQS filter messages are permanently deleted; SQS visibility ≥ 6× function timeout).

## SQS

Lambda long-polls SQS and invokes the function **synchronously** with a batch.

| Parameter | Default | Range / notes |
|---|---|---|
| `BatchSize` | 10 | Standard: up to 10,000. FIFO: up to 10 |
| `MaximumBatchingWindowInSeconds` | 0 | 0–300; not for FIFO; requires ≥1s when `BatchSize` > 10 |
| `MaximumConcurrency` | — | 2–1,000, per-ESM cap |
| `ProvisionedPollerConfig.MinimumPollers` / `MaximumPollers` | 2 / 200 | 2–200 / 1–2,000 |
| `FilterCriteria` | — | Filters on the `body` key only |
| `FunctionResponseTypes` | — | Set to `ReportBatchItemFailures` |

`MaximumConcurrency` and Provisioned (Poller) Mode are mutually exclusive on the same ESM (see `concurrency.md`). Lambda invokes when **any** of these trips: batching window expires, batch size reached, or the payload hits 6 MB.

**Scaling — standard queues:** concurrency starts at **5** concurrent invocations and ramps by **~300/minute** to a default max of **1,250** — a sudden backlog (say, 10,000 queued messages) takes several minutes to fully absorb, not seconds. For workloads that can't tolerate that ramp, use Provisioned (Poller) Mode instead, which starts higher and scales much faster.

**Scaling — FIFO queues:** concurrency is capped by the *lower* of (number of distinct message group IDs, `MaximumConcurrency`); order is preserved per group ID.

```yaml
# SAM
Events:
  SQSEvent:
    Type: SQS
    Properties:
      Queue: !GetAtt MyQueue.Arn
      BatchSize: 10
      MaximumBatchingWindowInSeconds: 5
      FunctionResponseTypes: [ReportBatchItemFailures]
      ScalingConfig: { MaximumConcurrency: 50 }
      FilterCriteria:
        Filters: [{ Pattern: '{"body": {"status": ["PENDING"]}}' }]
```
CDK: `fn.addEventSource(new SqsEventSource(queue, { batchSize, maxBatchingWindow, reportBatchItemFailures: true, maxConcurrency }))`.

## DynamoDB Streams

Lambda polls stream shards **4×/second**, invoking synchronously, in order per partition key.

| Parameter | Default | Range / notes |
|---|---|---|
| `BatchSize` | 100 | Up to 10,000 |
| `StartingPosition` | — | `TRIM_HORIZON` (recommended) or `LATEST` — `LATEST` can miss events created during ESM setup |
| `ParallelizationFactor` | 1 | 1–10, concurrent batches per shard |
| `BisectBatchOnFunctionError` | false | Splits a failed batch in half; doesn't consume the retry quota |
| `MaximumRetryAttempts` | -1 (infinite) | 0–10,000 |
| `MaximumRecordAgeInSeconds` | -1 (infinite) | -1, or 60–604,800 (7 days) |
| `DestinationConfig.OnFailure` | — | SQS, SNS, S3, or a Kafka topic |
| `TumblingWindowInSeconds` | — | 0–900, for stateful aggregation |

Key behaviors:
- **Max 2 Lambda readers per shard** on a single-region table; **1** for global tables.
- 100 shards × `ParallelizationFactor` 10 = up to **1,000 concurrent invocations**, order still preserved at the partition-key level.
- **Stream retention is 24 hours** — a poison record can block an entire shard for that whole window if retries aren't bounded. Always set `MaximumRetryAttempts`, `MaximumRecordAgeInSeconds`, or `BisectBatchOnFunctionError` — leaving all three at their infinite/off defaults is the trap.

## Event filtering

`FilterCriteria` applies only to event source mappings, not push triggers like SNS.

| Source | Filter key | Notes |
|---|---|---|
| SQS | `body` | Unmatched messages are **automatically, permanently deleted** — not retried, not DLQ'd |
| DynamoDB Streams | `dynamodb` + metadata (e.g. `eventName`) | **No numeric operators** — stream values are strings; match `{"N": ["123"]}`, not `{"numeric": [...]}` |
| Kinesis | `data` | Base64-decoded before filtering |
| MSK / Kafka | `value` | — |

Up to 5 filters per ESM (raisable to 10); multiple filters are OR'd, fields within one filter are AND'd. A format mismatch (plain string body vs a JSON filter, or vice versa) silently drops the record.

## Partial batch failure reporting

Set `FunctionResponseTypes: [ReportBatchItemFailures]` and return the failed identifiers, or a batch failure retries the **whole batch**:

- SQS → return failed `messageId`s in `batchItemFailures`.
- Streams (DynamoDB/Kinesis) → return the failed `SequenceNumber`; Lambda checkpoints at the **lowest** returned sequence number and retries everything after it.
- FIFO → stops at the first failure, returning it plus every unprocessed message after it, to preserve order.

An empty/null `batchItemFailures` means complete success. A bad `itemIdentifier`, wrong key name, or any unhandled exception in the handler causes a **complete batch retry** instead of a partial one. For streams, an unhandled exception triggers `BisectBatchOnFunctionError` (no response is returned, so `ReportBatchItemFailures` has no effect that invocation); a successful return *with* `batchItemFailures` checkpoints at the lowest failed sequence number as described above.

Prefer a maintained batch processor (e.g. Powertools' `process_partial_response`) over hand-rolling this — the edge cases above are easy to get subtly wrong.

## Concurrency formulas

```
SQS (standard scaling):     min(1250, MaximumConcurrency, ReservedConcurrency)
SQS (Provisioned Mode):      MaximumPollers × 10
DynamoDB / Kinesis:          number_of_shards × ParallelizationFactor
```

## Idempotency

Every event source here is **at-least-once**. See `production-readiness.md` for the idempotency key to use per source and the Powertools Idempotency utility.
