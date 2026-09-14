# Security, large messages, and cost

Source: docs.aws.amazon.com (SQS Developer Guide, endpoints and quotas) + AWS's messaging agent skill. Fetched 2026-09.

## Encryption

- **At rest:** SSE-SQS (AWS-owned key, `alias/aws/sqs`) is on by default for new queues. For compliance-sensitive payloads, switch to **SSE-KMS** with a customer-managed key: `SetQueueAttributes` with `KmsMasterKeyId=<key-id-or-arn>`.
- **In transit:** enforce HTTPS-only access with an explicit `Deny` statement on `"aws:SecureTransport": "false"` in the queue policy — not assumed by default.

## The confused-deputy pattern (read this before granting any service principal access)

Whenever a queue policy grants a **service principal** (`events.amazonaws.com`, `sns.amazonaws.com`, `s3.amazonaws.com`, etc.) permission to `sqs:SendMessage`, omitting a source condition means **any** resource of that type, in **any** AWS account, could write to your queue — not just yours. Always scope the statement:

- `aws:SourceArn` — the specific rule/topic/bucket/pipe ARN (use `ArnLike` with a wildcard suffix if the exact ARN isn't fully known up front).
- `aws:SourceAccount` — your account ID.

**S3 event notifications need both conditions** — S3 bucket ARNs don't carry the account ID, so `aws:SourceArn` alone doesn't constrain which account's bucket can write. The identical pattern applies to IAM role trust policies used by EventBridge rules and EventBridge Pipes (principal `events.amazonaws.com` / `pipes.amazonaws.com`, `aws:SourceArn` = the rule or pipe ARN) — not just the DLQ-specific case in `dlq-and-lambda-integration.md`.

## Large messages: the Extended Client Library

Hard message-size ceiling is **256 KB**. To send larger payloads (up to 2 GB), use the **Amazon SQS Extended Client Library**: the actual payload goes to S3, and the SQS message carries a reference to it. The library handles both sides transparently — sending stores to S3 first, then enqueues the pointer; receiving fetches the S3 object automatically.

- Available for Java natively (`amazon-sqs-java-extended-client-lib`); equivalent patterns exist for other languages via the same S3-pointer approach.
- Clean up the S3 object after successful processing — the library can do this automatically once the SQS message is deleted, but confirm that's wired up, or S3 storage accumulates silently.
- Don't try to work around the 256 KB limit by compressing or splitting a payload across multiple messages unless you have a strong reason not to use the Extended Client Library — it solves the ordering/reassembly problem for you.

## Credentials

Broker and queue-adjacent credentials (for Amazon MQ bridges, cross-account access patterns, etc.) belong in **Secrets Manager**, referenced by ARN — never hardcoded in application config, environment variables, connection strings, or IaC templates. Scope `secretsmanager:GetSecretValue` IAM access to only the consuming role, and enable rotation where the credential type supports it.

## System vs user message attributes

`ReceiveMessage` does **not** return system attributes (`SenderId`, `SentTimestamp`, `AWSTraceHeader`, etc.) by default — request them explicitly via `AttributeNames`/`MessageSystemAttributeNames`, separately from `MessageAttributeNames` (which fetches attributes *you* set). This distinction matters most when debugging via a DLQ: the X-Ray trace header (set by X-Ray/EventBridge/Pipes when a message lands in a DLQ) rides on the **system** attribute slot, while the originating service's own failure metadata (EventBridge's `RULE_ARN`, `ERROR_CODE`, etc.) rides on the **user** attribute slot — you need to request both to get the full picture of why a message ended up there.

## SNS → Firehose → S3 note

If you have SNS fanning out to Firehose (protocol `firehose`) landing in S3, SNS already newline-delimits records (NDJSON) by default. Don't also enable Firehose's `AppendDelimiterToRecord` — you'll get double newlines.

## Cost shape

SQS is priced per request (`SendMessage`, `ReceiveMessage`, `DeleteMessage`, and each batch action counts as fewer billed requests than the equivalent number of single calls). The practical cost levers are: **long polling** (fewer empty `ReceiveMessage` calls), **batching** (fewer total requests for the same message volume), and **not over-polling** idle queues. Extended Client Library payloads add S3 storage/request cost on top of SQS's own pricing.

## Pitfalls

- Granting a service principal `sqs:SendMessage` with no `aws:SourceArn`/`aws:SourceAccount` — a real confused-deputy exposure, not a theoretical one.
- S3 event notifications scoped with `aws:SourceArn` alone — always needs `aws:SourceAccount` too.
- Forgetting to clean up S3 objects behind Extended Client Library messages.
- Reading a DLQ message and only checking user attributes — the trace header you need is in the system attributes.
- Assuming SSE-SQS is sufficient for compliance workloads that specifically require customer-managed key control.
