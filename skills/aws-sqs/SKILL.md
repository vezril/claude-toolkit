---
name: aws-sqs
description: "Designing, securing, and operating Amazon SQS queues, distilled from docs.aws.amazon.com and AWS's own messaging/serverless agent skills (fetched 2026-09). Covers the messaging-vs-streaming distinction (messages are consumed once then deleted, no replay — contrast Kinesis/MSK), the message lifecycle (send → receive → in-flight/visibility timeout → delete, at-least-once and possibly out-of-order delivery on Standard queues), Standard vs FIFO queues (MessageGroupId ordering and parallelism, MessageDeduplicationId and content-based deduplication, high-throughput FIFO mode via DeduplicationScope/FifoThroughputLimit), polling (short vs 20s-max long polling), batching (SendMessageBatch/DeleteMessageBatch/ChangeMessageVisibilityBatch, 10 messages per batch), dead-letter queues and redrive policy (maxReceiveCount, the DLQ-must-match-queue-type rule, the queue-policy step that's easy to skip for EventBridge/SNS-fed DLQs), the Lambda event source mapping (batch size/window, ReportBatchItemFailures, the 5→300/min→1,250-default scaling ramp, FIFO ESM concurrency), large messages via the Extended Client Library (256 KB message cap, S3-backed payloads up to 2 GB), encryption (SSE-SQS default vs SSE-KMS) and the confused-deputy queue-policy pattern for service-principal senders, and service quotas. Use when creating or configuring an SQS queue, choosing Standard vs FIFO, wiring a Lambda or EventBridge/SNS trigger, setting up a dead-letter queue, debugging duplicate/out-of-order/stuck messages, or sending payloads near or over the 256 KB limit."
license: MIT
---

# Amazon SQS

How to design SQS queues that actually deliver what they promise — at-least-once (or exactly-once-in-order for FIFO), buffered, decoupled messaging — without the silent failure modes that show up under load. Distilled from `docs.aws.amazon.com` and AWS's own messaging/serverless agent skills, fetched 2026-09. Cross-links: [[aws-lambda]] for the event-source-mapping half of this, [[secure-coding]] for the confused-deputy queue-policy pattern, [[cqrs-event-sourcing]] for where SQS fits relative to true event streams.

## The mental model

SQS is **messaging**, not streaming: a producer sends a message, a consumer receives and processes it, and once it's deleted **it's gone** — no replay, no multiple independent readers picking up the same message at different offsets. (That's what Kinesis/MSK are for.) SQS's job is to **decouple and buffer** — absorb bursty producer traffic, distribute work across a pool of competing consumers, and hold messages safely until something is ready to process them.

```
Producer ──SendMessage──▶ Queue ──ReceiveMessage──▶ Consumer
                             │         (message becomes invisible
                             │          for the visibility timeout)
                             │
                     DeleteMessage (success) ──▶ gone, for good
                             │
                  visibility timeout expires,
                  no delete received ──▶ visible again, redelivered
                             │
                  received maxReceiveCount times ──▶ moved to DLQ (if configured)
```

Two queue types, chosen once at creation and not changeable after:

| | Standard | FIFO |
|---|---|---|
| Ordering | Best-effort | Strict, per `MessageGroupId` |
| Delivery | At-least-once (duplicates possible) | Exactly-once processing per message (within the dedup window) |
| Throughput | Effectively unlimited | 300 TPS per API action by default; up to 3,000 batched; much higher with high-throughput mode |
| Name | Any | Must end in `.fifo` |

## Non-negotiables

1. **Visibility timeout ≥ your actual processing time**, with real margin — Lambda specifically: **≥ 6× the function timeout**. Too short, and a message that's still being processed becomes visible again and gets picked up a second time.
2. **Always configure a DLQ with a redrive policy** (`maxReceiveCount`), and **the DLQ must be the same queue type as the source** — a FIFO source needs a FIFO DLQ.
3. **A DLQ attached alone is not enough for cross-service senders.** EventBridge rule targets and SNS subscriptions that redrive to an SQS DLQ also need an explicit **queue policy** granting that service principal `sqs:SendMessage`, scoped with `aws:SourceArn` — without it, the DLQ silently drops the failure record instead of receiving it. See `dlq-and-lambda-integration.md`.
4. **Every consumer is idempotent.** Standard queues guarantee at-least-once, not exactly-once — duplicates are expected, not a bug.
5. **Long polling in production** (`ReceiveMessageWaitTimeSeconds=20`) — new queues default to **short polling (0)**, which burns more requests (and cost) checking empty queues.
6. **Customer-managed KMS key for anything sensitive** — new queues default to `alias/aws/sqs` (SSE-SQS, AWS-owned key); `SetQueueAttributes` with a specific `KmsMasterKeyId` for compliance-sensitive payloads.
7. **256 KB is the hard message-size ceiling** — reach for the Extended Client Library (S3-backed, up to 2 GB) rather than truncating or splitting payloads awkwardly.
8. **Service-principal queue policies need `aws:SourceArn`/`aws:SourceAccount` conditions** — omitting them opens a confused-deputy hole where *any* rule/topic/bucket in *any* account can write to your queue.
9. **Request `MessageSystemAttributeNames` separately from `MessageAttributeNames`.** System attributes (`SentTimestamp`, `SenderId`, `AWSTraceHeader`) are never returned by a bare `ReceiveMessage` call — request them explicitly. This matters most on DLQs, where the trace header rides on the system-attribute slot and the *service's* failure metadata (e.g. EventBridge's `ERROR_CODE`, `RULE_ARN`) rides on the user-attribute slot.
10. **Broker/queue credentials never inline** — Secrets Manager, referenced by ARN, not embedded in connection strings or IaC.

## Quick reference (defaults you should usually override)

| Setting | New-queue default | Production default |
|---|---|---|
| `ReceiveMessageWaitTimeSeconds` (polling) | 0 (short) | 20 (long) |
| `KmsMasterKeyId` (encryption) | `alias/aws/sqs` | Customer-managed key for sensitive data |
| Visibility timeout | 30s | ≥ 6× consumer processing time |
| Message size | 256 KB max | Extended Client Library beyond that |
| DLQ | none | Always, with a matched-type queue and `maxReceiveCount` set intentionally |

## References

- `references/queue-mechanics.md` — the message lifecycle, Standard vs FIFO in depth (MessageGroupId, deduplication, high-throughput mode), polling, batching, and the quota table.
- `references/dlq-and-lambda-integration.md` — dead-letter queues and redrive policy, the queue-policy trap for EventBridge/SNS-fed DLQs, and the Lambda event source mapping (batching, scaling, partial batch failures).
- `references/security-and-ops.md` — encryption, the confused-deputy queue-policy pattern, large messages via the Extended Client Library, and cost/quota notes.
