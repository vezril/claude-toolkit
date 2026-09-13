# Compute, cold starts, and networking

Source: docs.aws.amazon.com (lambda/latest/dg) + AWS's Lambda/serverless agent skill. Fetched 2026-09. Assumes packaging/layer basics; focused on the numbers and edge cases.

## Cold-start strategy

**SnapStart** — snapshots the initialized execution environment (Firecracker microVM memory + disk) and restores from that cache instead of cold-booting.
- Supported: Java 11+, Python 3.12+, .NET 8+.
- Mutually exclusive with **Provisioned Concurrency** and with EFS. Ephemeral storage must be ≤ 512 MB. Only works on **published versions**, not `$LATEST`.
- Java: no extra charge. Python/.NET: a caching charge (by memory, min 3h) plus a per-restore charge.
- **Restoration gotchas** — the snapshot is reused across restores, so: generate unique IDs/secrets in the handler (not init), re-establish network connections in the handler (they're stale post-restore), refresh cached timestamps/credentials in the handler.

**Provisioned Concurrency** — pre-initializes environments that stay warm permanently.
- Scoped to a **published version or alias**, never `$LATEST`.
- One instance handles one concurrent request at a time; per-instance throughput = 1 / function duration. Spills to on-demand (cold starts) beyond the provisioned count.
- Supports Application Auto Scaling (target ~70% utilization).
- **Paid even when idle** — disable it in dev/staging.

| Scenario | Pick |
|---|---|
| Java/Python 3.12+/.NET 8+, heavy init | SnapStart first |
| Strict <50ms cold start on every request, or need EFS/>512MB ephemeral | Provisioned Concurrency |
| Tolerant of occasional cold starts | On-demand + minimize package size |
| Predictable traffic shape | Provisioned Concurrency + auto scaling |
| General cost/perf improvement | arm64 (Graviton), ~34% better price-performance |

They cannot coexist on one function — if SnapStart's P99 is still too high, switch to Provisioned Concurrency rather than trying to combine them.

## Memory, CPU, and timeout

CPU scales linearly with memory; **1 vCPU at 1,769 MB**. Over-provisioning memory often *lowers* cost, because faster execution means less billed duration. Start at 256–512 MB and tune against `Max Memory Used` in REPORT log lines (or the AWS Lambda Power Tuning tool) rather than guessing.

Timeout defaults to 3s — always set it explicitly, to P99 + buffer. Watch the ceilings above you:
- API Gateway REST API: 29s default (adjustable for Regional/private APIs; **edge-optimized stays capped at 29s**)
- API Gateway HTTP API: 30s hard limit, not adjustable
- SQS visibility timeout should be **≥ 6× the function timeout**

Ephemeral storage (`/tmp`): 512 MB default/min, up to 10,240 MB (extra cost above 512 MB). It's a transient cache across warm invocations — **not cleared after a failed invoke** — and SnapStart requires ≤ 512 MB.

## VPC connectivity

Lambda uses **Hyperplane ENIs**, shared across every function using the same subnet + security group combination (not one ENI per function; each supports ~65,000 connections).
- First-time ENI creation can take **several minutes** (function sits `Pending`).
- ENIs are reclaimed after **14 days of inactivity**; removing VPC config from a function can take up to 20 minutes to fully unwind.
- Reuse subnet + security group combos across functions to share ENIs and avoid cold-creation delays.
- **Prefer VPC endpoints** (gateway: S3, DynamoDB; interface: STS, Secrets Manager, SQS, …) over a NAT Gateway for reaching AWS services from inside a VPC — lower latency, traffic never leaves the AWS backbone.
- Only attach a VPC when you actually need a private resource (RDS, ElastiCache). VPC-attached functions need the `AWSLambdaVPCAccessExecutionRole` managed policy (or equivalent).

## Runtime lifecycle timeouts

- **On-demand init: 10s.** Exceed it and Lambda retries at the first invocation, against the function's configured timeout.
- **Provisioned/SnapStart init: up to 15 minutes.**
- **Shutdown**: 0ms with no extensions, 500ms internal-only, 2,000ms with external extensions — then SIGKILL.
- **SnapStart restore**: 10s for restore + after-restore hooks combined.

## Function URLs

A dedicated HTTPS endpoint on a single function, no API Gateway involved. Good for internal service-to-service calls (IAM auth), a Lambdalith behind CloudFront, response streaming, or webhook receivers. **No built-in rate limiting, WAF, or request validation** — front it with CloudFront/API Gateway if you need those. Reach for API Gateway instead when you need a public API with rate limiting, JWT/Cognito auth, multi-function routing, or WAF without a CDN in front.

Invoking a Function URL **always requires both** `lambda:InvokeFunctionUrl` and `lambda:InvokeFunction` — granting only the URL-invoke action returns HTTP 403 even under `AuthType=NONE`.

- **`AuthType=AWS_IAM`** (prefer for production): only SigV4-signed callers succeed; unauthenticated requests get 403. Same-account callers can be granted via either the caller's identity policy *or* the function's resource policy (only one is required); cross-account callers need **both**. CloudFront in front should use Origin Access Control to sign requests.
- **`AuthType=NONE`** (public): Lambda does no auth at all — the resource policy alone gates access and must explicitly grant public access via two separate statements (the console/SAM add both automatically; by CLI, two `add-permission` calls are required):
```bash
aws lambda add-permission --function-name my-function \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl --principal '*' --function-url-auth-type NONE
aws lambda add-permission --function-name my-function \
  --statement-id FunctionURLInvokeAllowPublicAccess \
  --action lambda:InvokeFunction --principal '*' --invoked-via-function-url
```
The second statement's `lambda:InvokedViaFunctionUrl` condition scopes that grant to Function URL calls only — it does not open direct `Invoke` access.

## Packaging

- 50 MB zipped / 250 MB unzipped including layers → switch to a container image (10 GB limit) past that.
- Max 5 layers per function; layers are incompatible with container images.
- Use `uv pip install` (10–100× faster than pip) with `--platform manylinux2014_{x86_64,aarch64} --only-binary=:all:` for cross-platform Python builds, or let `sam build` handle it.
- **Powertools for AWS Lambda** (Python/TypeScript/Java/.NET) gives structured logging, X-Ray tracing, EMF metrics, idempotency, and batch processing out of the box — adds some cold-start overhead, so use selective imports when that matters. Useful env vars: `POWERTOOLS_SERVICE_NAME`, `POWERTOOLS_METRICS_NAMESPACE`, `POWERTOOLS_LOG_LEVEL`, `POWERTOOLS_TRACE_DISABLED` (tests), `POWERTOOLS_DEV` (pretty-print).
