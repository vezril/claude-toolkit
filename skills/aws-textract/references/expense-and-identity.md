# Expense and identity document analysis

Source: docs.aws.amazon.com (textract/latest/dg, textract/latest/APIReference). Fetched 2026-09. Both operations here are synchronous, purpose-built extractors — not `AnalyzeDocument` with different `FeatureTypes`.

## `AnalyzeExpense`

Purpose-built for invoices and receipts — financially related relationships between pieces of text, not generic forms/tables.

Response is split into:
- **`SummaryFields`** — everything that isn't a line item: vendor name, invoice number, dates, totals, tax, header-level information.
- **`LineItemGroups`** — a set of `LineItems`, each describing one purchased item/service and its associated data (description, price, quantity).

Each field carries both a **detected `Type`** (a normalized category Textract assigns, e.g. `TOTAL`, `VENDOR_NAME`, `INVOICE_RECEIPT_DATE`) and the raw detected text, each with its own confidence score — similar in spirit to `AnalyzeID`'s normalized-field pattern below. Treat the normalized `Type` as Textract's best guess at what the field *means*, and the raw text as what was actually printed — reconcile discrepancies (e.g. an ambiguous date format) rather than trusting the normalization blindly for anything consequential.

Not supported by the **Bulk Document Uploader** — if you're batch-processing expense documents, call `AnalyzeExpense` (or its async counterpart, `StartExpenseAnalysis`/`GetExpenseAnalysis`) directly rather than routing through the bulk uploader.

## `AnalyzeID`

Purpose-built for **US-issued driver's licenses and passports only** — not a general international identity-document parser. Verify this scope before building a KYC/identity-verification flow that assumes broader coverage.

Returns three things:
1. **Standardized key-value pairs** for explicit fields (Date of Birth, Date of Issue, ID #, Class, Restrictions, ...).
2. **Implied fields** without explicit on-document labels (Name, Address, Issued By) that Textract infers from document layout/context.
3. **Full document text**, the same as plain text detection would return.

**Key names are normalized across document types** — a driver's license's `LIC#` and a passport's `Passport No` both come back under the same standardized key, `DOCUMENT_NUMBER` — specifically so you can combine data across ID types without per-document-type parsing logic.

```json
{
  "IdentityDocumentFields": [
    { "Type": { "Text": "first name" }, "ValueDetection": { "Text": "jennifer", "Confidence": 99.999 } },
    { "Type": { "Text": "last name" }, "ValueDetection": { "Text": "sample", "Confidence": 99.998 } }
  ]
}
```
If a detected field doesn't map to a known normalized type, it comes back labeled `"other"` rather than being dropped — don't assume every field in the response is one of the standardized types.

**Normalized fields, driver's licenses**: `FIRST_NAME`, `LAST_NAME`, `MIDDLE_NAME`, `SUFFIX`, `CITY_IN_ADDRESS`, `ZIP_CODE_IN_ADDRESS`, `STATE_IN_ADDRESS`, `COUNTY`, `DOCUMENT_NUMBER`, `EXPIRATION_DATE`, `DATE_OF_BIRTH`, `STATE_NAME`, `DATE_OF_ISSUE`, `CLASS`, `RESTRICTIONS`, `ENDORSEMENTS`, `ID_TYPE`, `VETERAN`, `ADDRESS`.

**Passports** have a similar but distinct normalized field set (starting with the same `FIRST_NAME`/`LAST_NAME` pattern) — check current docs for the full passport-specific list rather than assuming full overlap with the driver's-license set.

**Two-sided documents** (most driver's licenses): pass the front and back images as **separate images within the same `AnalyzeID` request** — don't call it twice per document; a single call handles both sides together.

Not supported by the **Bulk Document Uploader**, same as `AnalyzeExpense`.

## Pitfalls

- Assuming `AnalyzeID` handles non-US identity documents — it doesn't; verify coverage before designing around it.
- Treating a normalized `Type` on `AnalyzeExpense`/`AnalyzeID` output as infallible — it's Textract's classification of the field, with its own confidence score, not a guarantee.
- Calling `AnalyzeID` twice for a two-sided document instead of passing both images in one request.
- Routing expense or ID documents through the Bulk Document Uploader and being surprised it silently doesn't apply to them — call the dedicated APIs directly for these document types.
- Ignoring `"other"`-labeled fields entirely — they may still carry useful text even though Textract couldn't map them to a standardized type.
