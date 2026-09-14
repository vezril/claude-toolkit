# Pipes vs Rules, retries, and dead-letter queues

Source: docs.aws.amazon.com (eventbridge/latest) + AWS's serverless agent skill. Fetched 2026-09.

## Pipes vs Rules

| Dimension | EventBridge Pipes | EventBridge Rules |
|---|---|---|
| Topology | Point-to-point (1 source → 1 target) | Fan-out (1 event → N targets across matching rules) |
| Flow | Source → Filter → Enrichment → Transform → Target, all built in | Pattern-match on a bus, route to targets |
| Sources | SQS, Kinesis Data Streams, DynamoDB Streams, MSK, Amazon MQ | Any event already on a bus |
| Enrichment | Built in (Lambda, API Gateway, API Destinations, synchronous Express Step Functions) | Not built in — add a target that does it |
| Billing | You pay only for events that **pass the filter** — filtering happens at the source | You pay for rule evaluation regardless of match |
| Retry + DLQ | Built in, per pipe | Configured per rule target |

**Use Pipes to replace "glue Lambda" for a source→target hookup** — e.g. SQS → (filter/transform) → Step Functions, with no intermediary function to write, deploy, or pay cold-start latency on. **Use Rules** when you need to fan one event out to multiple independent targets, or when the source is something already landing on a bus (not one of the five Pipes source types).

## Target retry policy

Every rule target (and every Pipe) has a retry policy:

```json
{ "MaximumRetryAttempts": 3, "MaximumEventAgeInSeconds": 3600 }
```

- `MaximumRetryAttempts`: 0–185. Default (unset) behavior is **185 attempts**.
- `MaximumEventAgeInSeconds`: 60–86,400. Default (unset) behavior is **24 hours (86,400s)**.
- Retries stop at whichever limit is hit first, with exponential backoff and jitter.
- **If both limits are exhausted with no DLQ configured, the event is silently dropped.** EventBridge does not surface this anywhere by default — it just stops trying.

Tune these down from the generous defaults when a target's failure should fail fast (e.g. a time-sensitive action where a retry an hour later is worse than useless) — leaving 185 attempts / 24 hours on a target where staleness matters is a common oversight, not a safe default.

## Dead-letter queues

Attach a DLQ (an SQS queue) to a rule target's `DeadLetterConfig`, or to a Pipe's error handling config. This is **not sufficient by itself**:

**The destination queue needs an explicit queue policy** granting the sending service principal permission to write to it:

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "events.amazonaws.com" },
  "Action": "sqs:SendMessage",
  "Resource": "<dlq-arn>",
  "Condition": {
    "ArnEquals": { "aws:SourceArn": "<rule-or-pipe-arn>" },
    "StringEquals": { "aws:SourceAccount": "<account-id>" }
  }
}
```

Without this, the DLQ attachment succeeds at configuration time and then **silently receives nothing** when a target actually fails — this is one of the most common EventBridge production surprises, and it's identical in shape to the SNS/SQS DLQ trap covered in [[aws-sqs]]'s `dlq-and-lambda-integration.md`.

Reading a DLQ message: the originating service's failure metadata (e.g. `RULE_ARN`, `ERROR_CODE` from EventBridge) rides on the SQS **user** message attributes; the propagated `AWSTraceHeader` rides on the **system** attributes — request both explicitly (`MessageAttributeNames` and `AttributeNames`/`MessageSystemAttributeNames` respectively) or you'll only see half the picture.

## Input transformer

A rule target can rewrite the event payload before it reaches the target, using **input paths** (extract fields via a JSON-path-like syntax) and an **input template** (a string template referencing those extracted values). Use it to reshape an event into exactly the payload a target expects, without an intermediary Lambda — the same "skip the glue function" motivation as Pipes' transform step, but available on plain rule targets too.

## Pitfalls

- Reaching for Pipes when you actually need one-event-to-many-targets fan-out (that's Rules) — or reaching for a rule + Lambda glue function when a Pipe would do the filter/enrich/transform natively and more cheaply.
- Leaving retry policy at its generous defaults on a target where a stale retry is actively harmful.
- Configuring `DeadLetterConfig` and considering the job done, without writing the destination's queue policy.
- Not requesting SQS system attributes when reading a DLQ message, and missing the trace header as a result.
