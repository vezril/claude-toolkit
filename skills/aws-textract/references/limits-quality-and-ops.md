# Limits, document quality, and operations

Source: docs.aws.amazon.com (textract/latest/dg — quotas, limits, bulk uploader best practices). Fetched 2026-09.

## Format, size, and page limits (the authoritative table)

| Constraint | Value |
|---|---|
| Accepted formats | JPEG, PNG, PDF, TIFF (JPEG 2000-encoded images embedded in PDF are fine) |
| Unsupported | XFA-based PDFs; password-protected PDFs |
| Sync: JPEG/PNG/PDF/TIFF size | 10 MB "in memory" (the quotas page's figure — cross-check against the `Document` object reference's 5 MB figure for your specific SDK/call; see `SKILL.md`) |
| Sync: PDF/TIFF pages | **1 page only** |
| Async: JPEG/PNG size | 10 MB |
| Async: PDF/TIFF size | 500 MB |
| Async: PDF/TIFF pages | 3,000 pages |
| PDF max dimensions | 40 inches × 9,000 points |
| Max image resolution (any side) | 10,000 px |
| Minimum text height | 15 px (≈8pt font at 150 DPI) |
| Rotation | All in-plane rotations supported (e.g. 45°) |
| Vertical text | **Not supported** (e.g. traditional vertical Japanese/Chinese layout) |
| Queries per page | 15 sync / 30 async |
| Handwriting recognition | English only |
| Printed-text languages | English, French, German, Italian, Portuguese, Spanish (the API doesn't report which language it detected) |

## TPS quotas (default, adjustable per Region)

Distinct quotas apply per operation family:
- **Synchronous**: `AnalyzeDocument`, `DetectDocumentText`, `AnalyzeExpense`, `AnalyzeID` each have their own default transactions-per-second ceiling.
- **Asynchronous — Start**: `StartDocumentAnalysis`, `StartDocumentTextDetection`, `StartExpenseAnalysis`.
- **Asynchronous — Get**: `GetDocumentAnalysis`, `GetDocumentTextDetection`, `GetExpenseAnalysis`.

Both Start and Get quotas are measured independently — a burst of `Get<X>` polling can be throttled separately from your `Start<X>` submission rate. Request quota increases per-operation-family, per-Region, if steady-state volume approaches the default.

## Document quality guidance

- Prefer higher-resolution scans over lower ones, within the 10,000px max — text below the 15px minimum height simply won't be reliably detected, not gracefully degraded.
- Skewed/rotated pages are handled automatically for in-plane rotation; heavily distorted or non-planar images (e.g. a photo of a curled receipt) degrade accuracy more than a straightforward rotation does.
- For forms/tables specifically, a clean, high-contrast scan matters more than for plain OCR — `FORMS`/`TABLES` structure detection is more sensitive to noise than `LINE`/`WORD` detection alone.

## IAM

Standard least-privilege practice applies, with the same Rekognition-shaped specifics:
- The **SNS-publishing service role** for async jobs should be scoped to the one topic the job actually notifies, not broad SNS access.
- If writing async results to your own bucket via `OutputConfig`, the calling principal (or Textract's role, depending on how you've wired it) needs scoped `s3:PutObject` to that specific bucket/prefix, not account-wide S3 write access.
- Start with an AWS managed policy for common cases, then narrow to a customer-managed policy scoped to your actual operations and resources for production use.

## Human review via Amazon A2I

`AnalyzeExpense` and other Textract operations can integrate with **Amazon Augmented AI (A2I)** to route low-confidence extractions to human reviewers, the same pattern as Rekognition's `DetectModerationLabels` integration (see [[aws-rekognition]]'s `custom-labels-and-ops.md`).

> **A2I is no longer open to new customers** — existing customers can continue using it, but AWS isn't adding new features. **Don't design a new document-processing pipeline assuming A2I availability.** Build a custom review queue instead (e.g. route extractions below a confidence threshold to SQS/EventBridge for manual review) unless the account already has A2I access.

## Pricing shape (brief)

Textract bills per document/page processed, with **`AnalyzeDocument`'s `FeatureTypes` billed as separate line items** on top of the base detection cost — this is the practical reason to request only the features you need (see `SKILL.md`'s non-negotiable #4), not just an API-design nicety.

## Pitfalls

- Assuming a single account-wide TPS quota — Start and Get operations, and each sync operation, have independent limits.
- Treating a low-quality scan as "good enough" because it displays fine visually — text below the minimum detectable height or under heavy noise degrades extraction accuracy in ways that aren't obvious from a quick visual check.
- Designing a new pipeline around Amazon A2I without checking current account eligibility first.
- Granting a Textract service role broad S3/SNS access instead of scoping it to the specific bucket/topic the job actually needs.
