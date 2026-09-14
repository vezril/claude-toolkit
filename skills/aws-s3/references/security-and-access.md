# Security and access

Source: AWS's S3 security agent skill (`securing-s3-buckets`) + docs.aws.amazon.com. Fetched 2026-09.

## The default-secure bucket recipe

In order, for a new production bucket:

1. **Create the bucket.** Newer accounts should use account-regional bucket namespacing (`--bucket-namespace account-regional`) where available.
2. **Enable versioning.**
3. **Enable encryption**: SSE-S3 + S3 Bucket Keys enabled + SSE-C explicitly blocked (see Encryption below).
4. **Enable logging** — pick one: Server Access Logs to CloudWatch (the general recommendation), Server Access Logs to a separate general-purpose bucket, or CloudTrail data events. Any one of the three is sufficient; having none is a finding.
5. **Enforce HTTPS-only** via a `DenyInsecureTransport` bucket policy (below) — required, not optional.
6. **Leave Block Public Access and ACL ownership controls at their defaults** — new buckets ship with Block Public Access **fully on** and ACLs **disabled** (`BucketOwnerEnforced`). Don't change either.

## The `DenyInsecureTransport` policy (apply to every bucket)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyInsecureTransport",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": ["arn:aws:s3:::<bucket>/*", "arn:aws:s3:::<bucket>"],
    "Condition": { "Bool": { "aws:SecureTransport": "false" } }
  }]
}
```

## The `put-bucket-policy` safety rules (apply every time, no exceptions)

`put-bucket-policy` **replaces the entire policy document** — it is not additive.

1. **Fetch the existing policy first**: `aws s3api get-bucket-policy --bucket <name>`.
2. **If one exists, back it up**: `... --output text > backup-policy-$(date +%s).json`.
3. **If `NoSuchBucketPolicy` is returned**, there's nothing to back up — proceed to write the new policy directly.
4. **Merge your new statement(s) into the existing policy's `Statement` array** — don't just write a fresh policy with only your new statement.
5. **Validate the merged JSON** before applying (e.g. pipe through a JSON validator).
6. **Display the final command and get confirmation before executing** it against a production bucket.

Skipping step 1 is the single most common way a well-intentioned policy change quietly deletes every prior grant on the bucket.

## Encryption

- **Default**: SSE-S3, **S3 Bucket Keys enabled** (reduces KMS request cost/volume when using KMS, and is a good default even for SSE-S3), **SSE-C blocked** (customer-provided keys bypass AWS-side key management entirely — block it unless there's a specific reason to allow it).
- **SSE-KMS**: if used, **must be a customer-managed key**, referenced by **full ARN**, never by alias, and never the AWS-managed `aws/s3` key. The S3 API will silently accept `aws/s3` or an alias without erroring — this constraint has to be enforced by policy or process, not caught at the API layer. Always verify with `get-bucket-encryption` after applying.
- For a CloudFront-fronted bucket using SSE-KMS, the KMS key policy must separately grant `kms:Decrypt` (and `kms:GenerateDataKey*` for writes) to the CloudFront service principal, scoped to the distribution — see [[aws-cloudfront]]'s `protecting-origins.md`.

## Monitoring

- **GuardDuty** — check for an existing detector before creating one (`list-detectors`); `create-detector` on an account that already has one throws `BadRequestException: detector already exists`.
- **CloudTrail** — commands operate against the trail's **home region**, not the bucket's region. Find it: `aws cloudtrail describe-trails --query 'trailList[*].[Name,HomeRegion]'`. Using the bucket's region instead of the trail's home region is a common source of "my CloudTrail change didn't take effect."
- **AWS Config** — enable the core recommended S3-related managed rules (public-access checks, encryption checks, SSL-enforcement checks) for continuous drift detection rather than relying only on point-in-time audits.
- **S3 Storage Lens** — account/org-wide visibility into storage patterns, including finding incomplete multipart uploads across the estate (see `data-operations.md`).

## Auditing an existing bucket (read-only)

When auditing rather than provisioning: run every check as a **read-only** command, never a write/modify call during the audit itself. Report each control as **PASS / FAIL / NOT CONFIGURED** with a severity, and treat any one of the three logging options (SAL-to-CloudWatch, SAL-to-bucket, CloudTrail data events) as sufficient — mark logging `NOT CONFIGURED` only if none of the three are active. `ObjectLockConfigurationNotFoundError` means Object Lock simply isn't enabled — that's `NOT CONFIGURED`, not a failed call.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `AccessDenied` on read/audit calls | Check IAM policy, bucket policy, Block Public Access, VPC endpoint policy, and SCPs/RCPs in that order; `aws iam simulate-principal-policy` helps isolate which layer is denying |
| `put-bucket-policy` appears to have "lost" statements | The safety rules above weren't followed — restore from the backup and redo the merge |
| GuardDuty `detector already exists` | A detector already exists on the account; use it instead of creating a new one |
| CloudTrail changes don't take effect | Commands were run against the bucket's region instead of the trail's home region |

## Pitfalls

- Disabling Block Public Access "temporarily" for a debugging session and not re-enabling it.
- Writing a bucket policy from scratch instead of merging into the existing one.
- Using an alias or the `aws/s3` managed key for SSE-KMS instead of a customer-managed key's full ARN.
- Auditing a bucket and executing a "quick fix" write call mid-audit instead of keeping the audit strictly read-only.
