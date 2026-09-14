# Synchronous analysis and the Block model

Source: docs.aws.amazon.com (textract/latest/dg, textract/latest/APIReference). Fetched 2026-09. All operations here are synchronous — single document, one request/response, no `JobId`.

## `DetectDocumentText` vs `AnalyzeDocument`

- **`DetectDocumentText`** — plain OCR. Returns `LINE` and `WORD` blocks only. Use this when you need raw text and nothing else — it's cheaper and simpler than `AnalyzeDocument` with no `FeatureTypes` requested.
- **`AnalyzeDocument`** — OCR plus structured extraction, gated by `FeatureTypes`. Lines and words are **always** returned regardless of which features you request — `FeatureTypes` only controls what *additional* structure comes back.

## `FeatureTypes`

| Feature | Adds | Response shape |
|---|---|---|
| `TABLES` | Detected tables and cells | `TABLE` blocks, each with child `CELL` blocks (including `MERGED_CELL` for spanned cells) |
| `FORMS` | Key-value pairs | Two `KEY_VALUE_SET` blocks per pair — one `EntityType: KEY`, one `EntityType: VALUE` — linked via `Relationships` |
| `QUERIES` | Answers to natural-language questions you supply | `QUERY` block (your question + alias) linked to a `QUERY_RESULT` block (the answer text + confidence) |
| `SIGNATURES` | Signature locations | `SIGNATURE` blocks — can appear standalone, inside a form key-value pair, or inside a table cell |
| `LAYOUT` | Document structural layout | `LAYOUT_TEXT`, `LAYOUT_TITLE`, `LAYOUT_HEADER`, `LAYOUT_FOOTER`, `LAYOUT_SECTION_HEADER`, `LAYOUT_PAGE_NUMBER`, `LAYOUT_LIST`, `LAYOUT_FIGURE`, `LAYOUT_TABLE`, `LAYOUT_KEY_VALUE` blocks |

Selection elements (checkboxes, radio buttons) are detected as part of `FORMS`/`TABLES` analysis — a `SELECTION_ELEMENT` block carries a `SelectionStatus` (`SELECTED`/`NOT_SELECTED`), nested wherever the checkbox actually appears (inside a form value, inside a table cell).

**Each requested feature is billed separately** — requesting `["TABLES", "FORMS", "QUERIES", "SIGNATURES", "LAYOUT"]` on every call regardless of need is the single easiest way to overpay for Textract. Request only the features a given document type actually requires.

## The Block object model

Every response — sync or async — is a **flat array of `Block` objects**, not nested JSON. Each block has a `BlockType`, a `Confidence`, geometric data (`BoundingBox`/`Polygon`), and a `Relationships` array pointing to related blocks by ID (typically `Type: CHILD` for containment — a `LINE`'s child `WORD`s, a `TABLE`'s child `CELL`s — and `Type: ANSWER`/`VALUE` for cross-references like a `QUERY` to its `QUERY_RESULT`, or a `KEY_VALUE_SET` key to its value).

```
PAGE
 └─ LINE (Relationships: CHILD → WORD, WORD, ...)
 └─ TABLE (Relationships: CHILD → CELL, CELL, ...)
 └─ KEY_VALUE_SET (EntityType: KEY)   (Relationships: VALUE → KEY_VALUE_SET (EntityType: VALUE))
 └─ QUERY (Relationships: ANSWER → QUERY_RESULT)
```
To reconstruct anything useful (a table as rows/columns, a form as key→value pairs), you traverse this relationship graph yourself — Textract doesn't hand you a pre-assembled table or form structure. This is the most common source of "my extraction code is more complex than expected" surprise for a first Textract integration; budget for writing (or using a maintained library for) the graph-walking step.

## Queries

Ask natural-language questions against a document instead of (or alongside) structural extraction — useful when you know exactly what fields you need and don't want to hand-write form-key matching:

```json
{
  "Queries": [
    { "Text": "What is the patient first name?", "Alias": "PATIENT_FIRST_NAME" },
    { "Text": "What is the invoice total?", "Alias": "INVOICE_TOTAL" }
  ]
}
```
```json
{
  "BlockType": "QUERY",
  "Query": { "Text": "What is the patient first name?", "Alias": "PATIENT_FIRST_NAME" },
  "Relationships": [{ "Type": "ANSWER", "Ids": ["<query-result-block-id>"] }]
}
{ "BlockType": "QUERY_RESULT", "Confidence": 1.0, "Text": "ALEJANDRO", "Id": "<query-result-block-id>" }
```
- If no answer is found, the response element is simply blank — check for an empty/missing `QUERY_RESULT`, don't assume every query returns something.
- **Query limits**: **15 per page synchronous, 30 per page asynchronous.**
- **English-only** — Textract doesn't support Queries against non-English documents.
- Add `QUERIES` to `FeatureTypes` alongside your `Queries` list — it's just another feature type, composable with `TABLES`/`FORMS`/`SIGNATURES`/`LAYOUT` in the same call.

## Pitfalls

- Requesting every `FeatureTypes` value on every call "just in case" — each is billed independently.
- Expecting `AnalyzeDocument` to hand back an assembled table/form structure — you get blocks and relationships, and building the structure is your code's job.
- Assuming a `QUERY` always has an answer — check for an empty result before using it downstream.
- Sending a non-English document through Queries or expecting handwriting recognition on a non-English handwritten form — neither is supported.
