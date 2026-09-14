# Image analysis operations

Source: docs.aws.amazon.com (rekognition/latest/dg, rekognition/latest/APIReference). Fetched 2026-09. All operations here are synchronous — one request, one response, no job ID.

## Passing an image

```json
{ "Bytes": "<raw bytes, up to 5 MB>" }
// or
{ "S3Object": { "Bucket": "my-bucket", "Name": "photo.jpg", "Version": "optional-version-id" } }
```
Raw `Bytes` is capped at 5 MB (4 MB for `DetectProtectiveEquipment` and `DetectCustomLabels`); an S3-referenced object can be up to 15 MB. **The AWS CLI doesn't support passing raw image bytes at all** — use `--image-bytes <local-file>` (which the CLI reads and encodes for you) or reference an S3 object; SDKs generally don't require you to base64-encode `Bytes` yourself.

## `DetectLabels`

Detects objects, scenes, activities, and concepts — "flower," "wedding," "person skiing."
- `Features`: `GENERAL_LABELS` (the object/scene detection you'd expect) and/or `IMAGE_PROPERTIES` (dominant colors, quality metrics).
- `MaxLabels` and `MinConfidence` are only meaningful with `GENERAL_LABELS`. Default confidence floor: **55%** if unspecified.
- Max image dimensions: 10,000 × 10,000 px.
- Can use a custom adapter (`ProjectVersionArn`) to blend in a Custom Labels model's predictions alongside the built-in labels.

## `DetectModerationLabels`

Detects unsafe/inappropriate content for moderation workflows.
- Default confidence floor: **50%** if `MinConfidence` unspecified.
- Max image dimensions: 10,000 × 10,000 px.
- **Three-level hierarchical taxonomy**: L1 (top, e.g. `Explicit`) → L2 (e.g. `Explicit Nudity`) → L3 (e.g. `Exposed Female Genitalia`). Every returned label carries a `TaxonomyLevel`.
- **AWS's own recommendation: moderate using L1 or L2**; use L3 only to carve out specific exceptions from your moderation policy, not as the primary filtering level.
- **Taxonomy version matters and has changed.** Version 7 restructured labels from version 6.1 — e.g. v6.1's single `Suggestive` L1 category split into two new v7 L1 categories (`Non-Explicit Nudity of Intimate parts and Kissing` and `Swimwear or Underwear`). **If your integration filters or branches on specific label strings, pin the taxonomy version you tested against and re-verify after any migration** — a hardcoded label check against the old taxonomy silently stops matching once the account moves to a newer version.
- Can be routed to human review via Amazon A2I (see `custom-labels-and-ops.md` — also flagged there as closed to new customers).

## `DetectFaces`

Analyzes facial attributes — not identity. (Identity/matching is `CompareFaces`/`SearchFaces*`, a different API family — see `face-collections-and-matching.md`.)

- **`DEFAULT` attributes** (always returned): `BoundingBox`, `Confidence`, `Pose`, `Quality`, `Landmarks`.
- **Full attribute list** (request via `Attributes: ["ALL"]` or name specific ones alongside `DEFAULT`): `AGE_RANGE`, `BEARD`, `EMOTIONS`, `EYE_DIRECTION`, `EYEGLASSES`, `EYES_OPEN`, `GENDER`, `MOUTH_OPEN`, `MUSTACHE`, `FACE_OCCLUDED`, `SMILE`, `SUNGLASSES`.
- Requesting more attributes increases response time — don't request `ALL` by default if you only need a couple.
- **`FaceOccluded` and `EyeDirection` are DetectFaces/GetFaceDetection-only** — not supported when analyzing video with `StartFaceDetection`/`GetFaceDetection`'s sibling operations `GetCelebrityRecognition`, `GetPersonTracking`, or `GetFaceSearch`, which return only the default attribute set regardless of what you ask for.
- **Treat attribute values (age range, gender, emotion) as model estimates, not ground truth** — they're probabilistic outputs with their own confidence scores, not verified facts about the person.

## `DetectText`

OCR — detects and returns both individual words and full lines, with bounding boxes and confidence. **Caps at 100 words per image.** Rotated/skewed text is supported but degrades detection quality — see the general image-quality guidance (`security-and-access` equivalent concept: better input, better output) in AWS's best-practices docs for sensors/input images.

## `DetectProtectiveEquipment`

Detects PPE (hard hats, face masks, hand covers) on people in an image, and whether it's worn correctly relative to a body part.
- **Caps at 15 people per image.**
- Minimum person size to detect: 100×100 px in an 800×1300 image (scales proportionally for larger images).
- Minimum image dimensions: 64×64 px (this one differs from the general 80×80 px minimum for other operations).
- Maximum image dimensions: 4096 × 4096 px.
- Raw-bytes cap is **4 MB**, tighter than the general 5 MB.

## `RecognizeCelebrities`

Identifies well-known individuals against Rekognition's built-in celebrity database (not your own face collection). Returns identity, confidence, and face details for recognized celebrities plus `UnrecognizedFaces` for faces detected but not matched. Distinct from — and not a substitute for — your own `CompareFaces`/collection-based matching against people you've enrolled yourself.

## Pitfalls

- Passing raw image bytes through the AWS CLI — it isn't supported; use `--image-bytes` or an S3 reference.
- Hardcoding a moderation label string against an old taxonomy version and having it silently stop matching after a version bump.
- Requesting `Attributes: ["ALL"]` on `DetectFaces` by default when only one or two attributes are actually needed — needless latency.
- Treating `DetectFaces`' `Gender`/`AgeRange`/`Emotions` outputs as authoritative facts rather than confidence-scored model estimates.
- Assuming `DetectText`/`DetectProtectiveEquipment` share the same size/dimension limits as `DetectLabels` — several operations have their own tighter constraints (see `SKILL.md`'s quick reference).
