# Face collections, matching, and responsible use

Source: docs.aws.amazon.com (rekognition/latest/dg, including the identity-verification tutorial and the public-safety use-case guidance) + AWS Service Terms references. Fetched 2026-09.

## Two different questions: "are these the same face?" vs "is this face in my collection?"

- **`CompareFaces`** — one-shot, no persistent state: compares a source face image against a target face image, returns a similarity score. Good for "does this selfie match this ID photo," a single pairwise comparison.
- **Face collections** — a persistent, searchable index of face vectors you build over time (`CreateCollection`, then `IndexFaces` to add faces to it). Good for "does this face belong to anyone we already know," a one-to-many search.

## Building and searching a collection

```bash
aws rekognition create-collection --collection-id my-collection
aws rekognition index-faces --collection-id my-collection --image '{"S3Object":{"Bucket":"b","Name":"face.jpg"}}'
```
`IndexFaces` extracts facial features and stores them as a **face vector** in the collection, returning a `FaceId`. It can also return full facial attributes (via `DetectAttributes`, mirroring `DetectFaces`' `Attributes` parameter).

**Two ways to search the collection:**
- **`SearchFaces`** — search by an existing `FaceId` already in the collection (found a match, want other faces similar to it).
- **`SearchFacesByImage`** — search by a *new* image not yet indexed (the common case: "does this incoming photo match anyone in the collection").

Both default to returning matches with similarity **greater than 80%** (`FaceMatchThreshold`) — tune this explicitly for your use case rather than accepting the default silently. Results are ordered highest-similarity first and **capped at 4,096 matches**.

**Collection capacity**: up to **20 million** face vectors per collection, and (in newer collections) up to **10 million** user vectors by default — a "user" being an association of multiple faces to one identity (someone enrolled with several photos), distinct from individual `FaceId`s.

Managing the collection: `ListFaces` (enumerate what's indexed), `DeleteFaces` (remove specific face vectors), `DeleteCollection`.

## The identity-verification pattern

A common flow (e.g. "prevent duplicate account registration," "verify this is the same person who enrolled"):
1. `CompareFaces` the new photo against the photo just captured at this session (liveness/session-level check).
2. If similarity clears your threshold, `SearchFacesByImage` against your collection.
3. A match → this person is likely already registered, don't create a duplicate identity. No match → safe to `IndexFaces` and register them as new.

```python
response = client.search_faces_by_image(
    CollectionId="collection-id-name",
    Image={"Bytes": open(photo, "rb").read()},
    FaceMatchThreshold=99,   # tune per risk tolerance — identity use cases often run much higher than the 80% default
    MaxFaces=1,
)
```
Note the higher threshold (99) in identity-verification contexts versus the 80% general default — this is deliberate, not a typo; identity decisions warrant a much stricter bar than a general "similar faces" search.

## Responsible use — this is AWS's own published guidance, not an external add-on

Because face comparison/detection results feed decisions about real people, AWS publishes specific operational guidance, and for one category of use case, contractual requirements:

**General best practice, all face-comparison use cases:**
- Use appropriate confidence thresholds for the stakes involved — general "similar photos" search is not the same risk tier as an identity or access decision.
- Involve human reviewers to verify results before acting on them; don't make consequential decisions on system output alone.
- Face detection/comparison should **narrow the field for human review**, not make the final call itself.

**Public-safety and law-enforcement use specifically — a higher, non-optional bar:**
- Use a **confidence threshold of 99% or higher** to minimize false positives.
- **Trained human reviewers must verify every decision** that could affect someone's civil liberties or equivalent human rights — no autonomous action on a match.
- Be **transparent** about the system's use: inform affected end users/subjects where possible, obtain consent, and provide a feedback mechanism.
- **If you are a law enforcement agency using face comparison in connection with criminal investigations, the AWS Service Terms impose specific contractual requirements**, including: appropriately trained human review of every decision with civil-liberties impact, personnel training on responsible use, public disclosure of the system's use, and a prohibition on sustained surveillance of a person absent independent review or exigent circumstances.
- A facial-comparison match should be **one input among other compelling evidence**, never the sole basis for action.

**Where this bar doesn't apply the same way**: AWS's own docs note that non-law-enforcement identity scenarios — unlocking a phone, authenticating an employee at a building entrance — don't carry the same civil-liberties stakes and don't require the same manual-audit obligations. Match the rigor to the actual stakes of the decision, but default toward more human review, not less, whenever a match result could meaningfully affect someone.

## Pitfalls

- Using the default 80% `FaceMatchThreshold` for an identity-verification or access-control decision without deliberately raising it.
- Treating a `CompareFaces`/`SearchFaces*` match as sufficient justification for an automated action with real consequences for the person involved.
- Building a public-safety-adjacent application without checking the AWS Service Terms obligations that specifically apply to that use case.
- Confusing `RecognizeCelebrities` (built-in celebrity database) with your own collection-based matching — they're unrelated data sources.
- Conflating a "face," a "user" (multiple faces linked to one identity), and a "FaceId" — collection capacity limits and search behavior differ across the three.
