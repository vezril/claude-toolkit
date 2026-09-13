# Queue mechanics

Source: docs.aws.amazon.com (AWSSimpleQueueService/latest/SQSDeveloperGuide) + AWS's messaging agent skill. Fetched 2026-09.

## Message lifecycle

1. **`SendMessage`** — producer enqueues. Message becomes visible to consumers.
2. **`ReceiveMessage`** — a consumer reads it. The message doesn't leave the queue; it becomes **invisible** to other consumers for the **visibility timeout** duration.
3. **`DeleteMessage`** — consumer finishes processing and explicitly deletes it. This is the only way a message actually leaves the queue.
4. If the visibility timeout expires **before** delete, the message becomes visible again and can be redelivered — to the same or a different consumer. Extend it mid-processing with `ChangeMessageVisibility` if a job is running long.
5. If a message is received `maxReceiveCount` times without being deleted, and a redrive policy is configured, it moves to the DLQ (see `dlq-and-lambda-integration.md`).

**In-flight limit:** up to 120,000 messages in flight (received, not yet deleted) per Standard queue, and per FIFO queue — the Standard limit is raisable via AWS Support, the FIFO one is not.

## Standard vs FIFO

**Standard** — at-least-once delivery, best-effort ordering (usually roughly ordered, not guaranteed), effectively unlimited throughput. Default choice unless you specifically need strict ordering or exactly-once processing.

**FIFO** — strict ordering *within* a `MessageGroupId`, exactly-once processing (dedup window applies), queue name must end `.fifo`.

### MessageGroupId (FIFO)

Every FIFO message carries a `MessageGroupId`. Messages in the **same** group are always processed one at a time, in strict order — no two messages from the same group process concurrently. Messages in **different** groups can be processed in parallel.

- For strict ordering across the *entire* queue, use a single `MessageGroupId` for everything — but this serializes all processing, so throughput is bounded by how fast one consumer can work through one group.
- For parallelism, design multiple independent `MessageGroupId`s (e.g. one per customer, per order, per tenant) — this is the standard way to get both ordering *and* throughput out of FIFO.
- While a message from a group is in flight (received, not yet deleted), **no other message from that same group is returned** — this is the ordering guarantee's mechanism, and it's also why one slow consumer can stall an entire group's backlog.
- Standard queues can also *set* `MessageGroupId`, but there it enables **fair queues** (preventing one noisy group from starving others), not ordering.

### Deduplication (FIFO)

Every FIFO message needs a `MessageDeduplicationId` — either supplied explicitly, or derived automatically via **content-based deduplication** (a SHA-256 hash of the message body) if you enable that option instead. Within the 5-minute deduplication window, a duplicate ID is silently dropped rather than enqueued twice.

### High-throughput FIFO mode

Default FIFO throughput is 300 TPS per API action (`SendMessage`/`ReceiveMessage`/`DeleteMessage`), or up to 3,000 TPS using the batch actions. To go materially higher, enable **high throughput**, which requires setting both:
- `DeduplicationScope = messageGroup` (dedup happens per group, not queue-wide)
- `FifoThroughputLimit = perMessageGroupId` (the throughput quota applies per group, not to the whole queue)

Changing either setting away from those values silently reverts the queue to normal throughput. High-throughput quotas scale with the number of distinct message group IDs — more groups spreads load across more partitions. Exceeding the per-action TPS limit (even with messages available) returns `ThrottlingException`; the fixes are the same as above plus batching and increasing group-ID cardinality.

## Polling

- **Short polling** (`WaitTimeSeconds=0`, the default on a new queue) — queries a subset of servers, returns immediately, may miss messages that exist but weren't in the sampled subset.
- **Long polling** (`WaitTimeSeconds` > 0, max **20**) — waits up to that many seconds for a message to arrive before returning, reducing both empty polls and "false empty" responses. Nearly always what you want in production — it cuts request count (and therefore cost) for anything but a saturated queue.
- With multiple queues, use **one polling thread per queue**, not one shared thread — a shared thread can end up blocked (up to 20s) waiting on an empty queue while a different queue has messages ready.
- Set the client's HTTP response timeout **longer** than `WaitTimeSeconds`, or you'll see spurious timeout errors on a perfectly healthy long poll.

## Batching

`SendMessageBatch`, `DeleteMessageBatch`, `ChangeMessageVisibilityBatch` — up to **10 messages per batch**. Use these instead of one-at-a-time calls whenever you control both sides of the exchange; it materially raises effective throughput (especially relevant for hitting FIFO's per-action TPS limits) and cuts request cost. For `ReceiveMessage`, set `MaxNumberOfMessages` up to 10 to pull a batch in one call. For FIFO high-throughput queues specifically, batch operations on messages sharing the same group ID together where possible — it's the documented way to get the best partition utilization.

## Key quotas

| Quota | Value |
|---|---|
| Message size | 256 KB (use the Extended Client Library beyond this) |
| Message attributes | 10 per message |
| Messages per batch | 10 |
| Batched TPS, FIFO (standard) | 3,000 |
| Batched TPS, FIFO (high-throughput, most regions) | 700,000 in us-east-1/us-west-2/eu-west-1; lower in other regions |
| In-flight messages, Standard | 120,000 (raisable) |
| In-flight messages, FIFO | 120,000 (not raisable) |
| Visibility timeout max | 12 hours |
| Long-poll wait time max | 20 seconds |
| Actions per queue policy | 7 |

## Pitfalls

- Assuming Standard-queue ordering is guaranteed — it's best-effort only; use FIFO if order actually matters.
- One `MessageGroupId` for everything on a FIFO queue when you actually need parallelism — instant throughput ceiling.
- Enabling high-throughput mode without setting *both* `DeduplicationScope` and `FifoThroughputLimit` correctly — a partial config silently falls back to normal throughput.
- Leaving a queue at short-polling defaults in production — needless empty-poll cost.
- Sending near the 256 KB ceiling without a plan for what happens when a payload eventually exceeds it.
