---
name: aws-rekognition
description: "Adding image and video analysis with Amazon Rekognition, distilled from docs.aws.amazon.com (fetched 2026-09). Covers Rekognition Image's synchronous API surface (DetectLabels, DetectModerationLabels — the 3-level L1/L2/L3 content-moderation taxonomy, currently version 7, with a breaking label-name change from v6.1 — DetectFaces and its DEFAULT vs ALL facial attributes, DetectText, DetectProtectiveEquipment, RecognizeCelebrities), image format/size constraints (PNG/JPEG only, 5 MB as raw bytes vs 15 MB as an S3 object, per-operation pixel-dimension and minimum-face-size limits), face collections (CreateCollection/IndexFaces/SearchFaces/SearchFacesByImage/CompareFaces, the 80% default FaceMatchThreshold, the 20-million-face-vector collection ceiling, the identity-verification CompareFaces-then-SearchFacesByImage pattern), Rekognition Video's always-asynchronous stored-video API (Start*/Get* job pairs, the SNS notification + IAM service role wiring, the 7-day ClientRequestToken idempotency window, segment detection for technical cues and shots), streaming video via Kinesis Video Streams and stream processors (flagged: no longer available to new customers), Rekognition Custom Labels for training a custom detection model on a small labeled dataset, and — because this is a facial recognition/analysis service — AWS's own published guidance on responsible use: mandatory human review, a 99%+ confidence bar, and specific AWS Service Terms requirements for law-enforcement/public-safety use. Use when adding image or video analysis to an app, choosing between Rekognition Image and Video operations, building face search/verification against a collection, moderating user-generated content, processing video asynchronously, or evaluating whether a face-recognition use case needs human review."
license: MIT
---

# Amazon Rekognition

How to use AWS's image/video analysis service without hitting its two sharpest edges: the sync/async split that trips up anyone expecting one calling pattern for both images and video, and the fact that this is a facial recognition service — which comes with real technical constraints on how face-matching results may be used, not just engineering ones. Distilled from `docs.aws.amazon.com`, fetched 2026-09. Cross-links: [[aws-s3]] for the bucket an image/video is typically read from, [[aws-lambda]] for handling the SNS completion notification on a video job, [[aws-eventbridge]]/[[aws-sqs]] for wiring that notification into a broader pipeline, [[aws-amplify]]'s `advanced-and-ops.md` for Face Liveness (a distinct, session-based Rekognition capability for identity verification, not covered here), [[secure-coding]] for the IAM least-privilege posture below.

## The mental model

**Rekognition Image is synchronous; Rekognition Video is always asynchronous.** This single fact explains most of the API surface's shape:

```
Rekognition Image (single image, one request/response)
  DetectLabels · DetectModerationLabels · DetectFaces · DetectText
  · DetectProtectiveEquipment · RecognizeCelebrities · CompareFaces
  · IndexFaces / SearchFaces / SearchFacesByImage (collections)

Rekognition Video — stored video (S3-hosted file, job-based)
  StartLabelDetection → GetLabelDetection    (same Start/Get pairing for
  StartFaceDetection → GetFaceDetection       faces, celebrities, person
  StartPersonTracking → GetPersonTracking     tracking, content moderation,
  StartCelebrityRecognition → Get...          and segment/technical-cue
  StartContentModeration → Get...             detection)
  StartSegmentDetection → GetSegmentDetection
  → completion published to an SNS topic; call the matching Get* once SUCCEEDED

Rekognition Video — streaming (Kinesis Video Streams, stream processors)
  ⚠️ No longer available to new customers — see references/video-analysis.md
```

A **face collection** (`CreateCollection`, `IndexFaces`, `SearchFaces`/`SearchFacesByImage`) is a separate, persistent concept layered on top of both — a searchable index of face vectors you build up over time, distinct from the one-shot `DetectFaces`/`CompareFaces` calls.

## Non-negotiables

1. **Images must be PNG or JPEG.** No other format is accepted by any image operation.
2. **Know which size limit applies.** Raw bytes passed directly: **5 MB** (4 MB for `DetectProtectiveEquipment`, 4 MB for `DetectCustomLabels`). An object referenced in S3: up to **15 MB**. Passing image bytes isn't supported through the AWS CLI at all — use an SDK or reference an S3 object.
3. **Video must be stored in S3** for the stored-video API — Rekognition Video doesn't accept inline video bytes the way image operations accept inline image bytes.
4. **Set `MinConfidence` deliberately, per operation.** Defaults differ: `DetectLabels`/`DetectModerationLabels` default to ~50–55%; face-matching (`SearchFaces`) defaults to 80% (`FaceMatchThreshold`). A default that's fine for a general label isn't necessarily fine for a moderation or identity decision.
5. **Pin and test against a specific content-moderation taxonomy version.** Version 7 changed label names and structure from 6.1 (e.g. `Suggestive` split into two new L1 categories) — a hardcoded label string from an older integration silently stops matching after a version change. See `references/image-analysis.md`.
6. **Face-matching output requires human review before any consequential action**, and for public-safety/law-enforcement use, AWS's own Service Terms impose specific obligations (99%+ confidence threshold, trained human reviewers, no sustained surveillance without independent review, public disclosure). This isn't optional guidance for that use case — see `references/face-collections-and-matching.md`.
7. **Streaming video (Kinesis Video Streams + stream processors) is closed to new customers.** Existing customers can keep using it; don't design a new architecture around it — use the stored-video API against short S3-uploaded clips instead, or a different real-time approach.
8. **Every video job needs an IAM service role that can publish to the SNS topic you specify** — `StartLabelDetection` (and its siblings) fail to notify you of completion without it, and there's no way to poll status other than through that notification or manual `Get*` calls.

## Quick reference — image limits

| Constraint | Value |
|---|---|
| Formats | PNG, JPEG only |
| Max size, raw bytes | 5 MB (4 MB for `DetectProtectiveEquipment`/`DetectCustomLabels`) |
| Max size, S3 object | 15 MB |
| Max pixel dimensions (`DetectLabels`/`DetectModerationLabels`) | 10,000 × 10,000 |
| Min face size to detect | 40×40 px in a 1920×1080 image (scales proportionally) |
| `DetectText` word limit | 100 words per image |
| `DetectProtectiveEquipment` person limit | 15 people per image |
| Max face vectors per collection | 20 million |
| Max user vectors per collection | 10 million (default) |
| Max matches returned by a search | 4,096 |

## References

- `references/image-analysis.md` — `DetectLabels`, `DetectModerationLabels` and the taxonomy (with the v6.1→v7 migration), `DetectFaces` attributes, `DetectText`, `DetectProtectiveEquipment`, and the image format/size constraint table in depth.
- `references/face-collections-and-matching.md` — collections, `IndexFaces`/`SearchFaces`/`SearchFacesByImage`/`CompareFaces`, the identity-verification pattern, and AWS's responsible-use guidance for face matching (public safety, human review, Service Terms obligations).
- `references/video-analysis.md` — the stored-video async pattern (SNS/IAM wiring, idempotency), segment/technical-cue detection, and streaming video's new-customer availability change.
- `references/custom-labels-and-ops.md` — Rekognition Custom Labels (training your own detector), IAM least-privilege practices, and human review via Amazon A2I (also flagged as closed to new customers).
