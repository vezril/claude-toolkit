# Storage classes, versioning, and lifecycle

Source: docs.aws.amazon.com (AmazonS3/latest/userguide). Fetched 2026-09.

## Storage classes in depth

- **S3 Standard** — the default: frequent access, millisecond first-byte latency, data resilient across multiple Availability Zones.
- **S3 Express One Zone** — purpose-built for the most latency-sensitive workloads: single-digit-millisecond consistent access, up to ~10× faster than Standard, ~80% lower request cost. Lives in a **single Availability Zone** you choose (so you can co-locate it with compute for the shortest possible path), and uses a distinct bucket type — a **directory bucket** — rather than the general-purpose bucket type everything else uses.
- **S3 Standard-IA / S3 One Zone-IA** — infrequent access with millisecond retrieval still available; lower storage price, a per-GB retrieval fee. One Zone-IA trades multi-AZ resilience for an even lower price — use only for data you can re-create or that's already replicated elsewhere.
- **S3 Intelligent-Tiering** — for data whose access pattern is unknown or changes over time. Automatically moves objects between **four** access tiers: two low-latency tiers (frequent, infrequent) with no retrieval fees, plus two **opt-in** archive tiers for rarely-accessed data. This is the "stop guessing, let S3 optimize" class.
- **Glacier family** — three tiers trading retrieval speed for storage cost: **Instant Retrieval** (archive pricing, millisecond access — the closest Glacier gets to "just works"), **Flexible Retrieval** (minutes to hours, cheaper), **Deep Archive** (hours, the cheapest storage S3 offers).

Choosing: known-frequent → Standard; known-infrequent-but-fast-retrieval → Standard-IA; unpredictable → Intelligent-Tiering; genuinely archival → the Glacier tier matching your acceptable retrieval latency.

## Versioning

A versioning-enabled bucket keeps **one current version** and **zero or more noncurrent versions** per key. Each new upload to an existing key demotes the prior current version to noncurrent rather than overwriting it.

- **"Noncurrent age"** (used by lifecycle rules targeting noncurrent versions) is measured from when the object's **successor was created**, not from when the object itself was created.
- Deleting the current version doesn't erase data in a versioned bucket — it either creates a **delete marker** (if you send an unversioned delete) or removes one specific version (if you delete by version ID).

## Lifecycle rules

Rules can target current objects, noncurrent versions, or both, with actions:
- **Transition** — move to a cheaper storage class after N days.
- **Expiration** — delete the current version after N days.
- **NoncurrentVersionTransition** / **NoncurrentVersionExpiration** — same, scoped to noncurrent versions in a versioned bucket.
- **AbortIncompleteMultipartUpload** — clean up abandoned multipart uploads after N days (see `data-operations.md`) — a good default is **7 days**.

**When multiple rules make an object eligible for multiple actions on the same day, S3 resolves the conflict in this order:**
1. **Permanent deletion** takes precedence over transition.
2. **Transition** takes precedence over delete-marker creation.
3. If eligible for both a Glacier Flexible Retrieval transition and a Standard-IA/One Zone-IA transition simultaneously, S3 **chooses the Glacier Flexible Retrieval transition**.

## Restoring a previous version safely

Two ways to bring back a noncurrent version, with different safety profiles:
- **Method 1 (recommended)**: **copy** the noncurrent version into the bucket as a new object — it becomes the new current version, and every existing version is preserved.
- **Method 2**: permanently delete the current version, which promotes the most recent noncurrent version to current.

**Why Method 1 is safer**: S3 Lifecycle expiration operates under an **eventually consistent model** for this specific interaction. If you delete the current version (Method 2) intending to "restore" the previous one, and a lifecycle rule is concurrently expiring noncurrent versions, there's a real window where the version you wanted to restore gets permanently removed by the lifecycle rule before your restore completes — because S3 may be temporarily unaware of your deletion when evaluating the lifecycle expiration. Copying (Method 1) avoids this race entirely.

## Pitfalls

- Assuming a single-AZ storage class (One Zone-IA, Express One Zone) is a drop-in replacement for Standard — it isn't, for data you can't afford to lose in an AZ failure.
- Writing overlapping lifecycle rules without knowing the precedence order, then being surprised an object transitioned instead of expired (or vice versa).
- Restoring a "previous version" via Method 2 (delete current) on a bucket with active lifecycle expiration rules — use Method 1.
- Forgetting `AbortIncompleteMultipartUpload` entirely, letting failed/abandoned multipart uploads accumulate storage cost forever.
