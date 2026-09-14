---
name: aws-textract
description: "Extracting text, forms, tables, and structured data from documents with Amazon Textract, distilled from docs.aws.amazon.com (fetched 2026-09). Covers the four synchronous, single-page APIs (DetectDocumentText for plain OCR; AnalyzeDocument with FeatureTypes TABLES/FORMS/QUERIES/SIGNATURES/LAYOUT; AnalyzeExpense for invoices/receipts, returning SummaryFields and LineItemGroups; AnalyzeID for US driver's licenses and passports, returning normalized IdentityDocumentFields) versus the always-asynchronous Start*/Get* stored-document family (StartDocumentTextDetection/StartDocumentAnalysis/StartExpenseAnalysis, the same SNS-topic-plus-IAM-role notification wiring as Rekognition Video, ClientRequestToken idempotency, JobId's 7-day validity, and paginated Get* results), the Block-object response model (Page/Line/Word, TABLE/CELL, KEY_VALUE_SET, SELECTION_ELEMENT, SIGNATURE, QUERY/QUERY_RESULT, and the LAYOUT_* block types, all connected by Relationships), the Queries feature (natural-language questions with an Alias, 15 per page synchronous vs 30 asynchronous, English-only), document limits (JPEG/PNG/PDF/TIFF only, no XFA or password-protected PDFs, the 5 MB-vs-10 MB size-limit discrepancy across Textract's own docs worth verifying before relying on either figure, PDF/TIFF's 1-page synchronous cap vs 3,000-page asynchronous cap, minimum 15px text height, English-only handwriting recognition, six supported languages for printed text), the Bulk Document Uploader, and human review via Amazon A2I (flagged, as in Rekognition, closed to new customers). Use when extracting text or structured data from scanned documents, PDFs, or images, parsing invoices/receipts or ID documents, processing multi-page documents asynchronously, building a document-Q&A pipeline with Queries, or reviewing Textract output confidence for a downstream decision."
license: MIT
---

# Amazon Textract

Textract's API surface makes the most sense once you see it as **four synchronous, single-document specialists plus one asynchronous, S3-and-SNS-driven pattern that mirrors Rekognition Video almost exactly.** If you've used [[aws-rekognition]]'s stored-video API, the async half of this skill will feel immediately familiar — same `Start*`/`Get*` shape, same notification wiring, same idempotency token. Distilled from `docs.aws.amazon.com`, fetched 2026-09. Cross-links: [[aws-rekognition]] for the parallel async pattern and the shared Amazon A2I human-review caveat, [[aws-s3]] for where documents live for both sync and async calls, [[aws-lambda]] for handling the SNS completion notification, [[aws-eventbridge]]/[[aws-sqs]] for wiring that notification into a pipeline, [[secure-coding]] for the IAM/KMS posture below.

## The mental model

```
Synchronous (single document, one request/response, no JobId)
  DetectDocumentText          plain OCR — Lines and Words only
  AnalyzeDocument              OCR + FeatureTypes: TABLES · FORMS · QUERIES · SIGNATURES · LAYOUT
  AnalyzeExpense                invoices/receipts → SummaryFields + LineItemGroups
  AnalyzeID                     US driver's licenses/passports → normalized IdentityDocumentFields

Asynchronous (document in S3, job-based — for multi-page PDFs/TIFFs)
  StartDocumentTextDetection → GetDocumentTextDetection
  StartDocumentAnalysis      → GetDocumentAnalysis        (same FeatureTypes as AnalyzeDocument)
  StartExpenseAnalysis       → GetExpenseAnalysis
  → completion published to an SNS topic; call the matching Get* once SUCCEEDED
```

Every operation's output — sync or async — is a flat list of **`Block` objects** (`PAGE`, `LINE`, `WORD`, `TABLE`, `CELL`, `KEY_VALUE_SET`, `SELECTION_ELEMENT`, `SIGNATURE`, `QUERY`, `QUERY_RESULT`, and the `LAYOUT_*` family), connected by `Relationships` rather than nested JSON — expect to walk a graph, not parse a tree.

## Non-negotiables

1. **Know which size limit actually applies before you rely on one.** Textract's own documentation is inconsistent here: the `Document` object reference (the `Bytes`/`S3Object` input) states a **5 MB** limit for both; the quotas/limits page states synchronous operations support up to **10 MB "in memory."** Treat **5 MB as the safe conservative bound for inline `Bytes`**, and verify the current figure for your specific call shape before assuming 10 MB elsewhere.
2. **PDF and TIFF are single-page only for synchronous operations.** Multi-page PDFs/TIFFs **require the asynchronous API** (up to 3,000 pages, 500 MB). Sending a multi-page PDF to a sync operation doesn't degrade gracefully — use the right API for the document from the start.
3. **No password-protected PDFs, no XFA-based PDFs.** Neither is supported by any Textract operation, sync or async — flatten/export before ingestion if your source produces either.
4. **`AnalyzeDocument`'s `FeatureTypes` costs money per feature requested** — `TABLES`, `FORMS`, `QUERIES`, `SIGNATURES`, and `LAYOUT` are billed individually. Request only what you'll actually consume; `DetectDocumentText` is the cheaper choice when all you need is plain OCR.
5. **Handwriting recognition is English-only**, as is the **Queries** feature. Printed-text detection supports six languages (English, French, German, Italian, Portuguese, Spanish) — verify language support before routing non-English documents through Textract at all.
6. **The async job's SNS notification needs an IAM service role that can publish to your topic** — exactly like Rekognition Video. Without it, there's no way to learn a job completed short of polling `Get*` yourself.
7. **`AnalyzeID` only covers US-issued driver's licenses and passports.** It is not a general international ID parser — verify document coverage before building a KYC flow that assumes broader support.
8. **Confidence scores are not ground truth**, especially on `AnalyzeExpense`/`AnalyzeID` output feeding a financial or identity decision — route low-confidence extractions to human review rather than acting on them automatically. See `references/limits-quality-and-ops.md` for the same Amazon A2I availability caveat that applies to Rekognition.

## Quick reference

| Constraint | Value |
|---|---|
| Accepted formats | JPEG, PNG, PDF, TIFF (JPEG 2000 inside PDF is fine) |
| Sync PDF/TIFF page limit | **1 page** — use async for more |
| Async PDF/TIFF page limit | 3,000 pages |
| Async PDF/TIFF size limit | 500 MB |
| Sync JPEG/PNG/PDF/TIFF size | 10 MB "in memory" per the quotas page (5 MB per the `Document` object reference — verify which applies to your call) |
| Async JPEG/PNG size | 10 MB |
| Queries per page, sync | 15 |
| Queries per page, async | 30 |
| `JobId` validity | 7 days |
| `Get*` pagination | up to 1,000 results per page (`NextToken`) |
| Minimum text height | 15 px (≈8pt font at 150 DPI) |
| Handwriting recognition | English only |
| Printed-text languages | English, French, German, Italian, Portuguese, Spanish |
| Bulk Document Uploader | Up to 150 documents/request; doesn't support `AnalyzeLending` or `AnalyzeID` |

## References

- `references/sync-analysis-and-features.md` — `DetectDocumentText` vs `AnalyzeDocument`, every `FeatureTypes` option, the `Block` object model and `Relationships`, and the `Queries` feature in depth.
- `references/expense-and-identity.md` — `AnalyzeExpense` (`SummaryFields`/`LineItemGroups`) and `AnalyzeID` (normalized `IdentityDocumentFields`, two-sided documents, US-only coverage).
- `references/async-processing.md` — the `Start*`/`Get*` pattern, SNS/IAM wiring, `ClientRequestToken` idempotency, `OutputConfig` and KMS, and the Bulk Document Uploader.
- `references/limits-quality-and-ops.md` — the full format/size/page/language quota table, image-quality guidance, IAM least privilege, and human review via Amazon A2I.
