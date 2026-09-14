# Protecting origins

Source: AWS's CloudFront agent skill (`protecting-your-origins.md`) + docs.aws.amazon.com. Fetched 2026-09. Every mechanism here answers the same question: how do we make CloudFront the *only* way to reach this origin?

## Choose by origin type

| Origin | Mechanism |
|---|---|
| Private Amazon S3 bucket | **Origin access control (OAC)** + scoped bucket policy + Block Public Access left on |
| ALB, NLB, or EC2 in a private subnet | **VPC origin** + a security group allowing the CloudFront managed prefix list |
| Public, on-premises, or other-cloud HTTP origin | **Origin mutual TLS** (origin mTLS) |

These are chosen by origin type, not interchangeable — though an origin can combine more than one (e.g. a VPC origin *and* origin mTLS).

## S3 origin: OAC

**Default to OAC over origin access identity (OAI) for anything new** — OAI doesn't cover every Region, doesn't support SSE-KMS, and doesn't support write requests. Reserve OAI purely for migrating an older setup that already uses it.

```bash
aws cloudfront create-origin-access-control --origin-access-control-config '{
  "Name": "my-bucket-oac", "OriginAccessControlOriginType": "s3",
  "SigningBehavior": "always", "SigningProtocol": "sigv4"
}'
```

Bucket policy — scoped to the **specific distribution**, with both conditions:
```json
{
  "Effect": "Allow",
  "Principal": { "Service": "cloudfront.amazonaws.com" },
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::my-bucket/*",
  "Condition": {
    "StringEquals": {
      "AWS:SourceArn": "arn:aws:cloudfront::<account-id>:distribution/<distribution-id>",
      "AWS:SourceAccount": "<account-id>"
    }
  }
}
```
Both conditions together are what prevent a confused-deputy request from a different distribution or account. Keep S3 Block Public Access **fully on** the whole time — OAC doesn't need it disabled.

**If the bucket uses SSE-KMS**, the key policy must separately grant `kms:Decrypt` (and `kms:GenerateDataKey*` for write paths) to `cloudfront.amazonaws.com`, scoped the same way with both `SourceArn` and `SourceAccount` — otherwise CloudFront gets `AccessDenied` reaching an encrypted object even with a correct bucket policy.

**OAC only works on a standard S3 bucket origin, not a website endpoint** — if OAC "doesn't work," check the origin isn't accidentally configured as a website endpoint.

## Private ALB/NLB/EC2: VPC origins

Recommend a VPC origin over moving the resource to a public subnet, every time.

- Add an inbound security group rule allowing the **CloudFront managed prefix list** (or the service-managed security group) — **missing this rule causes requests to fail silently**, with nothing informative in the logs.
- Confirm the specific resource type is currently supported before proceeding — support has historically excluded some configurations (Gateway Load Balancers, dual-stack NLBs, NLBs with TLS listeners have all been unsupported at various points; an NLB needs a security group attached; gRPC and Lambda@Edge origin-facing triggers haven't been supported on VPC origins) — check current docs rather than assuming.
- **VPC origin deployment takes several minutes** — confirm it reaches a deployed state before relying on it.

**Lighter fallback**: for an ALB/NLB that must stay in a public subnet, restrict its security group to the CloudFront managed prefix list instead of using VPC origins. Simpler, but less secure — the origin still has a public IP, just filtered.

## Public/hybrid origin: origin mutual TLS

CloudFront presents a client certificate; **the origin server — not CloudFront — is the one that validates it**. This is the piece people get backwards.

- The origin must be independently configured to request client certificates and hold the issuing CA in its own trust store, before enabling origin mTLS does anything.
- Import the client certificate into ACM (in `us-east-1`, like every other CloudFront-related certificate) and enable origin mTLS per origin — different origins can use different certificates.
- Prefer this over IP allowlists or custom-header "secrets" for hybrid/multi-cloud origins — both of those are easier to accidentally leak or bypass.

## Troubleshooting

| Symptom | Cause |
|---|---|
| VPC origin requests fail with nothing in the logs | Missing security group rule for the CloudFront managed prefix list |
| Can't add a Gateway Load Balancer as a VPC origin | Unsupported resource type — check current docs, don't assume |
| `AccessDenied` reaching an S3 origin | Missing or misscoped bucket policy for `cloudfront.amazonaws.com` |
| OAC "doesn't work" | Origin is a website endpoint, not a standard bucket — OAC doesn't support website endpoints |
| Origin rejects CloudFront with origin mTLS enabled | Origin isn't actually configured to request/validate the client certificate — CloudFront only presents it |

## Pitfalls

- Scoping the S3 bucket policy or KMS key policy with only `SourceArn` or only `SourceAccount`, not both.
- Assuming origin mTLS is validated by CloudFront — it's validated by the origin.
- Not rotating origin mTLS certificates ahead of expiry — connections break (or silently fall back to a weaker path) when they lapse.
- Manually maintained CIDR-range security group rules instead of the CloudFront managed prefix list — they drift.
