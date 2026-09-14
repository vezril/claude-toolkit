---
name: aws-s3
description: "Storing, securing, and operating data in Amazon S3, distilled from docs.aws.amazon.com and AWS's own S3 security agent skill (fetched 2026-09). Covers storage classes (Standard, Express One Zone for single-digit-ms latency, Standard-IA/One Zone-IA, Intelligent-Tiering's four automatic access tiers, the three Glacier tiers), strong read-after-write consistency (since December 2020 — no longer eventually consistent), versioning and lifecycle rules (noncurrent-version transitions/expiration, the precedence order when multiple actions apply the same day: deletion > transition > delete-marker creation, the eventually-consistent interaction between lifecycle expiration and restoring a noncurrent version), multipart upload (100 MB practical threshold, concurrent-upload precedence rules, AbortIncompleteMultipartUpload lifecycle cleanup), conditional writes (If-Match/If-None-Match, 412/409 responses, their exact interaction with in-flight multipart uploads and concurrent deletes), presigned URLs, S3 security defaults and hardening (Block Public Access and BucketOwnerEnforced ACLs are on by default and should stay on, the mandatory DenyInsecureTransport bucket policy, SSE-S3 with Bucket Keys as the default encryption with SSE-C blocked, why a customer-managed KMS key is required — never the aws/s3 managed key — when using SSE-KMS, the put-bucket-policy full-replace danger and the read-modify-write-and-back-up discipline it demands), event notifications (native S3 notifications to SQS/SNS/Lambda vs. routing through EventBridge for advanced filtering and a standardized event format), and monitoring (Server Access Logs vs CloudTrail data events, GuardDuty S3 protection, Config rules). Use when creating or securing an S3 bucket, choosing a storage class, writing a lifecycle policy, debugging a bucket policy or encryption issue, handling large-object uploads, reacting to object events, or auditing an existing bucket's configuration."
license: MIT
---

# Amazon S3

How to store data in S3 without the two failure modes that matter most: an object that's more exposed than you think, and a `put-bucket-policy` call that silently deletes the security you already had. Distilled from `docs.aws.amazon.com` and AWS's own S3 security agent skill, fetched 2026-09. Cross-links: [[aws-cloudfront]] for the "serve S3 through CloudFront, not directly" pattern, [[aws-lambda]] for S3-triggered functions, [[aws-eventbridge]] for advanced S3 event routing, [[secure-coding]] for the general encryption/least-privilege posture this builds on.

## The mental model

A **bucket** is a region-scoped namespace; an **object** is a key + its bytes + metadata, stored redundantly across multiple facilities within the bucket's Region (or a single AZ for the Express One Zone class). There's no real directory structure — keys with `/` in them are a UI convention, not a filesystem.

**Consistency**: since December 2020, S3 provides **strong read-after-write consistency** for all operations (PUTs of new objects, overwrites, deletes, GETs, LISTs) — a `GET` immediately following a successful `PUT` is guaranteed to see the new data. This wasn't always true; older documentation, blog posts, and tutorials describing "eventual consistency" for overwrite PUTs predate this change and are stale.

## Non-negotiables

1. **Never turn off Block Public Access or switch ACLs away from `BucketOwnerEnforced`.** Both are on by default for new buckets specifically to prevent accidental public exposure — there's essentially never a legitimate reason to disable either.
2. **Enforce HTTPS with a `DenyInsecureTransport` bucket policy** on every bucket — deny `s3:*` when `aws:SecureTransport` is `false`. This isn't automatic; you write it.
3. **`put-bucket-policy` replaces the entire policy — it is not a merge.** Before ever calling it: fetch the existing policy (`get-bucket-policy`), back it up if one exists, merge your new statement(s) into its `Statement` array, validate the merged JSON, then apply. Skipping the read step silently deletes every existing statement.
4. **Default encryption is SSE-S3 with S3 Bucket Keys enabled, SSE-C blocked.** If you need SSE-KMS, use a **customer-managed key by full ARN** — never the `aws/s3` AWS-managed key (the API accepts it without error, so this has to be enforced by policy/process, not caught by the API).
5. **Every object exceeding ~100 MB should use multipart upload**; every object *must* if it exceeds 5 GB (S3's single-PUT limit). Set a lifecycle rule to `AbortIncompleteMultipartUpload` after ~7 days, or abandoned upload parts accumulate storage cost silently.
6. **Serve public content through CloudFront with Origin Access Control, not a public bucket or a website endpoint you also expose directly.** See [[aws-cloudfront]]'s `protecting-origins.md`.
7. **Presigned URLs inherit the signer's permissions and expire on a clock you set — pick that expiry deliberately**, and never generate one with credentials broader than the specific object access being granted.

## Quick reference — storage classes

| Class | Best for | Notes |
|---|---|---|
| **S3 Standard** | Frequently accessed, general purpose | Default |
| **S3 Express One Zone** | Latency-critical workloads | Single AZ (co-locatable with compute), directory buckets, up to ~10× faster access, ~80% lower request cost than Standard |
| **S3 Standard-IA** | Infrequent access, still needs millisecond retrieval | Lower storage cost, per-GB retrieval fee |
| **S3 One Zone-IA** | Infrequent, re-creatable data | Single AZ — lower durability guarantee than multi-AZ classes |
| **S3 Intelligent-Tiering** | Unknown or changing access patterns | Auto-moves objects across 2 low-latency tiers (frequent/infrequent) + 2 opt-in archive tiers, no retrieval fees |
| **S3 Glacier Instant Retrieval** | Rarely accessed, millisecond retrieval needed | Archive pricing, instant access |
| **S3 Glacier Flexible Retrieval** | Archival, retrieval in minutes–hours acceptable | Lower cost than Instant Retrieval |
| **S3 Glacier Deep Archive** | Long-term archival, retrieval in hours acceptable | Lowest-cost S3 storage class |

## References

- `references/storage-classes-and-lifecycle.md` — the storage class table in depth, lifecycle rule mechanics, versioning interaction, and the multi-action-same-day precedence order.
- `references/security-and-access.md` — the default-secure bucket recipe (Block Public Access, `BucketOwnerEnforced`, `DenyInsecureTransport`, encryption), the `put-bucket-policy` safety discipline, and monitoring.
- `references/data-operations.md` — multipart upload mechanics and concurrency gotchas, conditional writes, presigned URLs, and event notifications (native vs. via EventBridge).
