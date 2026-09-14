# Video analysis: stored and streaming

Source: docs.aws.amazon.com (rekognition/latest/dg). Fetched 2026-09.

## Stored video (the API to build on)

Every stored-video operation follows the same asynchronous shape: `Start<X>` kicks off a job against a video already sitting in S3 and returns a `JobId`; you learn it's done via an SNS notification, then call `Get<X>` with that `JobId` to retrieve results.

```json
// StartLabelDetection request
{
  "Video": { "S3Object": { "Bucket": "my-bucket", "Name": "video.mp4" } },
  "ClientRequestToken": "LabelDetectionToken",
  "MinConfidence": 50,
  "NotificationChannel": {
    "SNSTopicArn": "arn:aws:sns:us-east-1:111122223333:topic",
    "RoleArn": "arn:aws:iam::111122223333:role/rekognition-sns-publish-role"
  },
  "JobTag": "DetectingLabels"
}
```

- **`NotificationChannel` is how you find out the job is done** — no other polling-free mechanism exists. It needs an SNS topic in the **same Region** as the Rekognition Video endpoint you're calling, plus an **IAM role that lets Rekognition publish to that topic**. Skipping this means you have no way to know completion short of polling `Get<X>` yourself on a timer.
- Once the SNS message reports `SUCCEEDED`, call the matching `Get<X>` with the `JobId` from the `Start<X>` response.
- **`ClientRequestToken`** is an idempotency key with a **7-day lifetime**: reusing it with the *same* operation and *same* parameters within that window returns the same `JobId` without re-running the job (protects against accidental duplicate submission, e.g. a retried request); reuse with *different* parameters is rejected; after 7 days the token can be reused fresh.
- `StartLabelDetection` applies the `GENERAL_LABELS` feature by default and supports inclusive/exclusive label or category filters via `Settings` — the same filtering concept as image label detection, applied to video.

**The full Start/Get family**: `StartLabelDetection`, `StartFaceDetection`, `StartPersonTracking`, `StartCelebrityRecognition`, `StartContentModeration`, `StartSegmentDetection` — each with a matching `Get*`. Face-related video operations (`GetFaceSearch`, `GetCelebrityRecognition`, `GetPersonTracking`) return only the **default** facial attribute set regardless of request — `GetFaceDetection` (paired with `StartFaceDetection`'s `FaceAttributes` parameter) is the only stored-video operation that can return the full attribute set, matching `DetectFaces`' behavior.

## Segment detection

`StartSegmentDetection` finds structural boundaries in a video rather than content within frames:

- **`TECHNICAL_CUES`** — frame-accurate start/end/duration of black frames, color bars, opening/end credits, studio logos, and primary program content. Useful for e.g. finding exactly where end credits begin.
- **`SHOT`** — start/end/duration of individual shots (camera cuts) — useful for identifying edit points.

```json
{
  "Video": { "S3Object": { "Bucket": "test_files", "Name": "test_file.mp4" } },
  "SegmentTypes": ["TECHNICAL_CUES", "SHOT"],
  "Filters": {
    "TechnicalCueFilter": { "MinSegmentConfidence": 90, "BlackFrame": { "MaxPixelThreshold": 0.1, "MinCoveragePercentage": 95 } },
    "ShotFilter": { "MinSegmentConfidence": 60 }
  }
}
```
Different confidence filters can be set independently per segment type in the same request.

## Streaming video — availability has changed

> **Streaming Video and Bulk Image Analysis is no longer available to new customers.** Existing customers can continue using it; this does not affect any other Rekognition feature.

For context (relevant if maintaining an existing integration, not for new design): streaming video used **Amazon Kinesis Video Streams** as input and a **stream processor** (`CreateStreamProcessor`) to manage analysis, with two distinct processor shapes:

- **Face search stream processor** — `FaceSearchSettings` pointing at a collection; outputs match results to a **Kinesis data stream** you consume yourself.
- **Label detection stream processor** — `ConnectedHomeSettings` (`PERSON`, `PET`, `PACKAGE`, or `ALL`) with optional `RegionsOfInterest`; outputs go to **S3 + SNS notification** instead of a Kinesis data stream, and can optionally be KMS-encrypted.

**For new real-time/near-real-time video analysis needs, design around the stored-video API against short S3-uploaded clips, or evaluate a different service** — don't architect a new system assuming stream processor access, since it isn't available to accounts that don't already have it.

## Pitfalls

- Omitting `NotificationChannel`/the IAM publish role and then having no way to learn when a video job finishes.
- Reusing a `ClientRequestToken` with different parameters, expecting a new job — it's rejected, not silently accepted.
- Expecting `GetFaceSearch`/`GetCelebrityRecognition`/`GetPersonTracking` to return full facial attributes the way `GetFaceDetection` or image `DetectFaces` can — they can't.
- Designing a new architecture around Kinesis Video Streams + stream processors without checking current account eligibility first.
