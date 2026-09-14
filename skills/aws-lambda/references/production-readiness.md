# Production readiness

Source: AWS's serverless agent skill + docs.aws.amazon.com (Lambda best practices, Serverless Applications Lens). Fetched 2026-09. Deliberately concise — the value is the checklist and the opinionated defaults, not API syntax.

## Pre-deploy checklist

**Compute**
- [ ] Memory right-sized (Power Tuning / load test, not guessed)
- [ ] Timeout set explicitly — never the 3s default
- [ ] Reserved concurrency set where a downstream dependency needs protecting
- [ ] DLQ / on-failure destination on every async invocation and every event source mapping
- [ ] Config via env vars; SDK clients initialized outside the handler
- [ ] Deployment package minimized (no tests/docs/unused deps)

**Observability**
- [ ] Structured JSON logging (Powertools Logger) with correlation IDs propagated
- [ ] X-Ray active tracing
- [ ] Custom metrics via EMF, not synchronous `PutMetricData` in hot paths
- [ ] Alarms on Errors, Throttles, Duration P99, IteratorAge, ConcurrentExecutions, DLQ depth (table below)
- [ ] Log retention set explicitly — the default is "never expire"
- [ ] Log group encrypted with a customer-managed KMS key when compliance requires it
- [ ] Lambda Insights enabled

**Security**
- [ ] One IAM role per function, scoped to exact resource ARNs
- [ ] No secrets in env vars — Secrets Manager / SSM `SecureString`, cached via Powertools
- [ ] Input validation at the handler boundary (Zod / Pydantic / Powertools Validation)
- [ ] VPC only where actually required (RDS, ElastiCache); VPC endpoints for AWS service calls
- [ ] GuardDuty Lambda Protection, Security Hub Lambda controls, Inspector Lambda scanning, CI dependency scanning
- [ ] Function URLs use `AWS_IAM` auth in production, not `NONE`
- [ ] SSE-KMS on SQS queues when compliance requires customer-managed keys (SSE-SQS is on by default)
- [ ] Customer-managed KMS on DynamoDB tables when key control is required (AWS-owned encryption is on by default)
- [ ] `aws:SecureTransport` enforced in resource policies (S3, SQS)

**Reliability**
- [ ] Every handler idempotent
- [ ] Partial batch failure reporting wired for SQS/Kinesis/DynamoDB Streams
- [ ] `BisectBatchOnFunctionError` set for stream sources
- [ ] Retry config tuned (`MaximumRetryAttempts`, `MaximumEventAgeInSeconds`)
- [ ] Reserved concurrency = 0 documented as the emergency kill switch, and someone knows it exists
- [ ] No unhandled exceptions swallowed silently — catch, log, return a meaningful error

**Deployment**
- [ ] Aliases + weighted traffic shifting (or CodeDeploy canary/linear) with rollback alarms
- [ ] All infra as code (CDK/SAM/CloudFormation)
- [ ] Separate accounts for dev/staging/prod
- [ ] Post-deploy smoke tests and pre-traffic hooks before a full shift

## Architecture decisions

**Lambdalith vs micro-Lambda.** Default to **micro-Lambda** (one function per route) on greenfield work: per-function least-privilege IAM, independent scaling and reserved concurrency, granular observability, smaller/faster cold starts. Reach for a **Lambdalith** when migrating an existing Express/FastAPI app wholesale, or when a small team genuinely values deployment simplicity over per-route granularity.

**Reserved vs Provisioned Concurrency.** Reserved guarantees capacity and protects downstream systems (cold starts are still possible; the function throttles once the limit is hit). Provisioned eliminates cold starts (and spills to on-demand beyond the provisioned count). Needing both: Provisioned ≤ Reserved. Try SnapStart before Provisioned for eligible runtimes — no cost for Java.

## Observability

Powertools **Logger** (structured JSON, automatic correlation IDs), **Tracer** (wraps X-Ray, auto-captures SDK/HTTP calls, annotate with business keys), **Metrics** (EMF — near-zero latency, writes to stdout; avoid synchronous `PutMetricData` in hot paths, ~5–20ms per call).

**Minimum alarm set, every production function:**

| Alarm | Metric | Threshold | Why |
|---|---|---|---|
| Error rate | `Errors / Invocations` | > 1% | Bugs or upstream failures |
| Throttles | `Throttles` | > 0 | Concurrency limit hit |
| Duration P99 | `Duration` P99 | > 80% of timeout | Catch slow functions before they start timing out |
| Iterator age | `IteratorAge` | > 60s | Stream processing falling behind |
| Concurrent executions | `ConcurrentExecutions` | > 80% of reserved | Approaching a throttle |
| DLQ depth | SQS `ApproximateNumberOfMessagesVisible` | > 0 | Failed messages accumulating unseen |

**Testing.** Serverless apps are mostly service integrations, not complex business logic — the integration layer (tested against the real cloud) carries the most value; keep unit tests to pure logic and E2E tests light. Structure handlers as thin adapters around pure functions. Don't rely on LocalStack/DynamoDB Local as primary test infrastructure — they diverge from real IAM, quotas, and error codes. Don't mock AWS SDK calls for integration tests. `sam sync` / `cdk watch` plus a per-developer isolated stack keeps the iteration loop fast.

## Idempotency

At-least-once delivery is guaranteed — duplicates arrive from async retries, SQS visibility-timeout expiry, stream replays, client retries, and Step Functions task retries. Use the Powertools **Idempotency** utility (Python/TS/Java/.NET), backed by a DynamoDB table with TTL: `id` (hash of the idempotency key), `status` (`INPROGRESS`/`COMPLETED`/`EXPIRED`), `data` (cached response), `expiration` (TTL).

| Source | Idempotency key |
|---|---|
| SQS | `messageId` |
| EventBridge | `detail.id` or a composite |
| DynamoDB Streams | `eventID` |
| API Gateway / Function URL | `Idempotency-Key` header, or a body hash |
| Step Functions | Execution ID + task token |

Set TTL to roughly how long duplicates can plausibly arrive: API retries ~1h; SQS ≈ `maxReceiveCount` × visibility timeout; stream replays ~24h (the stream retention window).

## Response streaming

Use for payloads > 6 MB (the buffered limit), TTFB-sensitive responses, SSE, LLM token streaming, or large generated files. Function URLs are simplest; REST API also supports it (proxy, `STREAM` mode); **HTTP API does not**. Limits: 200 MB response, 2 MBps after the first 6 MB; billed for the full duration even if the client disconnects early. Node.js has native support (`awslambda.streamifyResponse` + `awslambda.HttpResponseStream.from`); other runtimes need a custom runtime or the Lambda Web Adapter. Not supported for VPC-attached functions via Function URL — use `InvokeWithResponseStream` instead. Don't bother streaming small JSON payloads — buffered is simpler and fine under 6 MB.

## Anti-patterns

- **Lambda calling Lambda synchronously** — doubles latency, tight coupling, fragile error handling. Decouple through SQS, or use Step Functions when you actually need the result back.
- **An accidental monolith handler** — routing stuffed into one function without weighing the trade-off blocks independent scaling and widens the IAM blast radius. Choose Lambdalith vs micro-Lambda on purpose.
- **Secrets in env vars.**
- **Skipping idempotency** — guaranteed duplicate processing, eventually.
- **VPC attachment "just in case"** — pure cold-start tax when nothing private is being called.
- **Shipping the default 3s timeout** — legitimate slow requests fail with no signal as to why.
- **Missing DLQ** — failed async invocations and ESM messages vanish with no trace.
- **Log retention left at "never expire."**
