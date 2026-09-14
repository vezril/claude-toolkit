---
name: aws-lambda
description: "Building, scaling, and operating AWS Lambda functions, distilled from docs.aws.amazon.com and AWS's own Lambda/serverless agent skills (fetched 2026-09). Covers the execution model (init/invoke/shutdown phases, execution environment reuse and recycling, Hyperplane ENIs for VPC), cold-start mitigation (SnapStart vs Provisioned Concurrency — mutually exclusive, with restoration gotchas for SnapStart), memory/CPU/timeout tuning (CPU scales linearly with memory; 1 vCPU at 1,769 MB; default 3s timeout that should never ship), the four concurrency controls (Reserved, Provisioned, ESM Maximum Concurrency, ESM Provisioned Mode) and their numeric interactions, event source mappings (SQS batching/scaling/FIFO concurrency, DynamoDB Streams shards/parallelization/poison-record handling, event filtering, partial batch failure reporting via ReportBatchItemFailures), Function URLs and the AuthType=NONE vs AWS_IAM permission model, packaging/layers/container images, and a production-readiness checklist (observability/alarms, idempotency by event source, response streaming, Lambdalith vs micro-Lambda, anti-patterns). Use when writing or configuring a Lambda function, tuning memory/timeout/concurrency, wiring an SQS/DynamoDB/Kinesis trigger, debugging cold starts/throttles/timeouts, setting up a Function URL, or reviewing a Lambda-based architecture for production readiness."
license: MIT
---

# AWS Lambda

How to build Lambda functions that scale predictably, fail safely, and don't surprise you in production. Distilled from `docs.aws.amazon.com` and AWS's own Lambda/serverless agent skills, fetched 2026-09. Cross-links: [[aws-sqs]], [[aws-eventbridge]], and [[aws-amplify]] for common trigger sources, [[aws-api-gateway]] for the proxy-integration contract Lambda must honor, [[nodejs]] / [[python]] for handler code, [[cqrs-event-sourcing]] for the event-driven patterns Lambda usually sits inside, [[secure-coding]] for the IAM/secrets hardening below.

> **Freshness.** Quotas, pricing, and supported-runtime lists change; treat exact numbers here as a 2026-09 snapshot and re-verify anything a production decision hinges on.

## The mental model

A Lambda function is stateless application code that AWS runs inside a managed, single-tenant **execution environment** on demand. You never see the environment directly, but its lifecycle explains almost every non-obvious Lambda behavior:

```
INIT (once per environment) ──▶ INVOKE (repeated, one at a time per environment) ──▶ SHUTDOWN
   extension init → runtime init → function init         handler runs                environment reclaimed
```

- **Code outside the handler runs once per environment**, not once per request — this is *why* you initialize SDK clients and DB connections at module scope, and *why* stale connections/credentials from a long-lived environment are a real bug class (refresh them inside the handler, not just at init).
- **Environments are recycled periodically even under continuous load** — never assume warm state survives indefinitely.
- **Invocation type changes the failure contract**: synchronous callers (API Gateway, Function URLs, SDK `Invoke`) get the error back directly; asynchronous invokes (S3, SNS, EventBridge) retry automatically then go to a configured failure destination/DLQ; **event source mappings** (Lambda polling SQS/DynamoDB Streams/Kinesis/MSK on your behalf) invoke synchronously against a *batch*, with retry/failure semantics owned by the source, not by Lambda's async retry path.

## Non-negotiables

1. **Set the timeout explicitly.** The default is 3 seconds — always too short or accidentally too long. Set it to P99 + a buffer, and remember the ceilings above you: API Gateway REST (29s, non-adjustable for edge-optimized), HTTP API (30s hard limit).
2. **SQS visibility timeout ≥ 6× the function timeout.** Too short, and a still-processing message becomes visible again and gets double-processed.
3. **Every handler is idempotent.** All Lambda event sources deliver **at-least-once** — duplicates are not an edge case, they're guaranteed eventually. See `production-readiness.md` for the idempotency key per source.
4. **DLQ or failure destination on every async invocation and every event source mapping.** Without one, failed messages are silently discarded.
5. **`ReportBatchItemFailures` on SQS/Kinesis/DynamoDB Streams triggers**, and return failure identifiers correctly — an empty/malformed response silently retries the *entire* batch, not just the failed items.
6. **One IAM role per function, scoped to exact resource ARNs.** Least privilege isn't optional here — a shared broad role is the most common Lambda security mistake.
7. **No secrets in plain environment variables** (visible in console/API, 4 KB total cap anyway) — Secrets Manager or SSM `SecureString`, cached with Powertools.
8. **`Provisioned Concurrency` and `SnapStart` are mutually exclusive on the same function** — decide, don't assume you can layer them.
9. **Only attach a VPC when you need private resources** (RDS, ElastiCache). It adds cold-start latency for no benefit when calling AWS services — use VPC endpoints for those instead.
10. **Function URLs default to `NONE` (public) only when you mean it.** Production should default to `AuthType=AWS_IAM`; either way, invoking one always needs **both** `lambda:InvokeFunctionUrl` and `lambda:InvokeFunction` — granting only the first returns a 403.

## Quick reference

| Parameter | Value |
|---|---|
| Memory | 128 MB – 10,240 MB, 1 MB increments, default 128 MB. **1 vCPU at 1,769 MB**, ~5.8 vCPUs at max. CPU scales linearly with memory. |
| Timeout | 1s – 900s (15 min), default 3s |
| Ephemeral storage (`/tmp`) | 512 MB (default/min) – 10,240 MB; persists across warm invokes, not cleared on failure |
| Env vars | 4 KB total |
| Sync payload | 6 MB request/response |
| Async payload | 1 MB |
| Streamed response | 200 MB, 2 MBps after the first 6 MB |
| Deployment package | 50 MB zipped / 250 MB unzipped (incl. layers) → container image (10 GB) beyond that |
| Layers | Max 5 per function; incompatible with container images |
| Default concurrency | 1,000 per region (soft, raisable); scales at 1,000 new environments/10s per function |
| Account RPS quota | 10 × account concurrency |

## References

- `references/compute-and-scaling.md` — cold-start strategy (SnapStart vs Provisioned Concurrency), memory/timeout tuning, VPC/ENI behavior, Function URLs and their permission model, packaging/layers/Powertools.
- `references/concurrency.md` — the four concurrency controls, how they interact (and where they conflict), decision table, SAM/CDK property reference.
- `references/event-sources.md` — SQS and DynamoDB Streams event source mappings, event filtering, partial batch failure reporting, scaling formulas.
- `references/production-readiness.md` — the pre-deploy checklist, Lambdalith vs micro-Lambda, observability/alarms, idempotency by source, response streaming, anti-patterns.
