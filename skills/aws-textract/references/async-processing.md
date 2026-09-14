# Asynchronous processing

Source: docs.aws.amazon.com (textract/latest/dg, textract/latest/APIReference, AWS code examples). Fetched 2026-09. This is the API to reach for whenever a document is multi-page (PDF/TIFF beyond 1 page) or you don't want to block on Textract's response time.

## The Start/Get pattern

Identical shape to Rekognition Video's stored-video API (see [[aws-rekognition]]'s `video-analysis.md` if you've used that): `Start<X>` kicks off a job against a document already in S3 and returns a `JobId`; completion is published to an SNS topic; call `Get<X>` with the `JobId` once the notification reports success.

```python
response = textract_client.start_document_text_detection(
    DocumentLocation={"S3Object": {"Bucket": bucket_name, "Name": document_file_name}},
    NotificationChannel={"SNSTopicArn": sns_topic_arn, "RoleArn": sns_role_arn},
)
job_id = response["JobId"]
```

**The family**: `StartDocumentTextDetection`/`GetDocumentTextDetection` (plain OCR, mirrors `DetectDocumentText`), `StartDocumentAnalysis`/`GetDocumentAnalysis` (structured extraction with the same `FeatureTypes` as `AnalyzeDocument`), `StartExpenseAnalysis`/`GetExpenseAnalysis` (mirrors `AnalyzeExpense`). **There is no async equivalent of `AnalyzeID`** — identity document analysis is synchronous-only.

## Notification wiring

- **`NotificationChannel`** needs an **SNS topic ARN** and a **`RoleArn`** for an IAM role that Textract can assume to publish to that topic. Without this, you have no push-based way to learn the job finished — only manual polling of `Get<X>` on your own schedule.
- The SNS topic must be reachable by the IAM role you provide — scope that role tightly to just this topic, not broad SNS publish access.

## Idempotency

**`ClientRequestToken`** (1–64 chars, alphanumeric/hyphen/underscore) works exactly like Rekognition's equivalent: reusing the same token with the same operation and same input returns the **same `JobId`** without starting a new job — protects against accidental duplicate submission (e.g. a retried request after a timeout). Reusing it with different parameters produces different behavior than a fresh call — don't rely on token reuse across genuinely different requests.

**`JobId` is valid for 7 days** — after that window, a stored `JobId` you haven't yet called `Get<X>` on becomes unusable; retrieve results within the window or re-run the job.

## Retrieving and paginating results

`Get<X>` results are paginated: **up to 1,000 results per call** via `MaxResults`, with a `NextToken` returned when more remain. For a large multi-page document, expect to page through several `Get<X>` calls to collect the full `Blocks` array — don't assume one call returns everything.

**`JobTag`** is an optional free-text identifier you set on the `Start<X>` call and get back in the completion notification — use it to correlate a notification back to what you were actually processing (e.g. "tax-form" vs "receipt") when a single SNS topic serves multiple job types.

## Output destination and encryption

By default, Textract stores async results internally, retrievable only via `Get<X>`. **`OutputConfig`** lets you instead have results written to a bucket you own — useful when you want the raw output durably stored alongside the source document rather than only reachable through the API. **`KMSKeyId`** encrypts those results with a customer-managed key; omitted, results are encrypted server-side with SSE-S3 by default.

## Bulk Document Uploader

A console-based batch-processing tool, distinct from calling the async API yourself:
- Same format/size limits as the general async limits (JPEG/PNG 10 MB; PDF/TIFF up to 500 MB, 3,000 pages).
- **Up to 150 documents per bulk request** — submit multiple batches of ≤150 for larger volumes.
- **Does not support `AnalyzeLending` or `AnalyzeID`** — those document types need direct API calls.
- Billed the same as regular Textract usage — it's a convenience wrapper, not a separate pricing tier.

## Pitfalls

- Omitting `NotificationChannel`/the IAM role and having no way to learn a job completed.
- Retrieving only the first page of `Get<X>` results on a large document and silently losing the rest — always follow `NextToken` until it's absent.
- Letting a `JobId` sit unused past its 7-day validity window.
- Expecting an async equivalent of `AnalyzeID` — it doesn't exist; identity documents are synchronous-only regardless of page count.
- Trying to bulk-upload expense or identity documents through the console uploader — it silently excludes those types.
