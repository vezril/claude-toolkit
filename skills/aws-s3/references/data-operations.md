# Multipart upload, conditional writes, presigned URLs, and events

Source: docs.aws.amazon.com (AmazonS3/latest/userguide). Fetched 2026-09.

## Multipart upload

Splits one object into independently-uploadable parts, reassembled by S3 on completion.

- **Use it once an object reaches roughly 100 MB** — S3's own general guidance threshold. **Required**, not optional, past S3's single-PUT object size limit.
- Parts can upload **in parallel** and **out of order**; a failed part can be retransmitted without redoing the others — this is the actual benefit, not just "upload big files."
- **Checksums**: S3 supports SHA-1, SHA-256, CRC32, and CRC32C as additional integrity checks stored with object metadata — use one as a durability best practice to confirm every byte transferred intact, beyond S3's own internal integrity checks.
- **Always add a lifecycle rule**: `AbortIncompleteMultipartUpload` after a set number of days (7 is a reasonable starting point) — otherwise abandoned upload parts sit in the bucket, unusable and billed, indefinitely. S3 Storage Lens can surface how much incomplete-multipart-upload storage exists across an account.

### Concurrency behavior worth knowing

- **In a versioning-enabled bucket**, if two `CreateMultipartUpload` calls target the same key concurrently, **the current version is determined by whichever upload *started* most recently** (by `createdDate`) — not whichever *completes* first. A first upload that started at 10:00 and completes at 10:30 can still lose current-version status to a second upload that started at 11:00 and completed earlier.
- **In a non-versioned bucket**, any other request landing between a multipart upload's initiation and completion can take precedence — including another operation deleting the same key mid-upload, which can result in the multipart upload reporting success without the object actually existing afterward.
- **Conditional writes do not consider in-progress multipart uploads** — they're not "fully written objects" yet. If another client completes a conditional `PutObject` on the same key while your multipart upload is in progress, your `CompleteMultipartUpload` call fails with `412 Precondition Failed`.

## Conditional writes

`If-Match` / `If-None-Match` headers let you write only if an object's current ETag matches (or, for `If-None-Match: *`, only if the key doesn't exist yet) — S3's mechanism for optimistic concurrency control without a separate locking system.

| Scenario | Response |
|---|---|
| Conditional write races a competing multipart upload that completes first | `412 Precondition Failed` (both `If-Match` and `If-None-Match` cases) |
| Conditional write races a delete that completes first | `409 Conflict` (`If-None-Match`) or `404 Not Found` (`If-Match`) — the earlier delete takes precedence |

In either race, the fix is the same: retry as a fresh operation (a new multipart upload, or a fresh conditional write against current state) — don't try to "resume" against stale assumptions about the object's existence.

## Presigned URLs

A presigned URL grants time-limited access to a specific S3 action, signed with the credentials of whoever generated it — the bearer needs no AWS credentials of their own.

- The URL inherits **exactly the permissions of the signer** — generate it with a principal scoped to only what should be delegated (a specific `GetObject` on a specific key, not broad bucket access), never with broader credentials "because it's convenient."
- **Set the expiry deliberately.** Short-lived for one-off access (minutes); longer only with a specific reason, since a leaked presigned URL is valid for anyone until it expires — there's no revocation short of rotating the underlying credentials or, for bucket-owner-generated URLs, changing the bucket policy to explicitly deny.

## Event notifications

Two ways to react to object events (`ObjectCreated`, `ObjectRemoved`, etc.):

- **Native S3 event notifications** — direct to SQS, SNS, or Lambda. Simple, low-latency, no extra hop.
- **Via EventBridge** (`S3 EventBridge Notification`) — routes the same events through EventBridge first, gaining **advanced content-based filtering** (EventBridge's full pattern language, not just S3's simpler prefix/suffix filters), **multiple simultaneous destinations** without configuring each natively, and a **standardized event envelope** (`detail-type: "Object Created"`, `source: "aws.s3"`) that's easier to handle generically alongside events from other services.

```json
{
  "detail-type": "Object Created",
  "source": "aws.s3",
  "detail": { "bucket": { "name": "example-bucket" }, "object": { "key": "IMG_1234.jpg", "size": 184662 } }
}
```

Choose native notifications for a simple, single-destination reaction; choose the EventBridge path the moment you need filtering beyond prefix/suffix, multiple destinations, or want S3 events to flow through the same event-driven architecture as everything else (see [[aws-eventbridge]]).

## Pitfalls

- Not setting `AbortIncompleteMultipartUpload`, letting failed uploads accumulate cost forever.
- Assuming multipart-upload "current version wins by completion time" in a versioned bucket — it's actually by *start* time.
- Treating a `412`/`409` from a conditional write as a bug instead of the expected outcome of a real race — retry fresh rather than assuming corruption.
- Generating a presigned URL with broader permissions or a longer expiry than the specific delegation actually needs.
- Reaching for native S3 notifications when the real need (multi-destination, rich filtering) calls for routing through EventBridge instead.
