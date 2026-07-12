---
name: gcp-firestore
description: "Firestore in Native mode — Google's serverless NoSQL document database: schemaless documents in collections and subcollections addressed by hierarchical slash paths, shallow index-backed queries (every field auto-indexed, composite indexes declared in firestore.indexes.json), real-time listeners and offline persistence as the mobile/web differentiator, and Firestore Security Rules enforcing per-request access at the edge for client SDKs while server libraries authenticate via IAM. Use when modeling documents/collections, writing queries or composite indexes, wiring real-time or offline sync, authoring Security Rules, choosing Native vs Datastore mode, tuning hotspots/limits, or picking between Firestore, Bigtable, Spanner, AlloyDB, and Cloud SQL."
license: MIT
---

# Firestore in Native mode

**Identity.** Firestore in Native mode is Google Cloud's serverless, autoscaling NoSQL **document
database** — the same storage engine as [[gcp-datastore]] but exposing a document/collection API plus
two features Datastore mode lacks: **real-time listeners** and **offline persistence** via mobile/web
SDKs, gated by **Firestore Security Rules**. It is Google's recommended default: "Use Firestore in
Native mode for all new applications (server, mobile, and web)." Reach for it when a phone/browser
client needs to read and write the database directly, sync live, and work offline.

## The mental model

- **Schemaless documents in collections.** A *document* is a JSON-like record of key→value fields
  (boolean, number, string, timestamp, geo point, binary blob, array, and nested `map` objects); it
  is identified by a name (document ID) unique within its collection. A *collection* is just a
  container for documents — created implicitly on first write, gone when empty. There is no schema:
  documents in a collection need not share fields.
- **Hierarchy is paths, not joins.** Nest a *subcollection* under a document, alternating
  collection/document/collection/document up to 100 levels deep. References are forward-slash paths:
  `users/alovelace/messages/msg1`. A reference is a lightweight pointer — creating one does no I/O
  and the target need not exist. Deleting a document does **not** delete its subcollections.
- **Queries are shallow and index-backed.** A query reads documents from **one** collection (or,
  with a *collection group query*, every collection of the same ID across the tree) and never
  descends into subcollections. "Every query computes its results using one or more indexes" — no
  scans, no joins. Corollary: a query can only answer what an index serves.
- **Real-time + offline are the point.** Attach a listener (`onSnapshot`) and clients are pushed the
  new result set on every change; the mobile/web SDKs cache locally so reads/writes keep working
  offline and reconcile on reconnect. Server client libraries also listen but do not cache/offline.
- **Two client families, two auth models.** *Mobile/web SDKs* (Android, iOS, Web, Flutter, C++,
  Unity) run in untrusted clients and every request is evaluated against **Security Rules** first.
  *Server client libraries* (Node, Python, Go, Java, C#, PHP, Ruby) run in trusted backends, **bypass
  all Security Rules**, and authorize through Application Default Credentials + [[gcp-iam]].

## Shapes (verified against docs)

```sh
gcloud firestore databases create --location=nam5 --type=firestore-native   # mode is set here
gcloud firestore indexes composite create --collection-group=cities \
  --field-config=field-path=state,order=ascending \
  --field-config=field-path=population,order=descending                     # or deploy the JSON below
firebase deploy --only firestore:indexes,firestore:rules                    # Firebase CLI path
```

```js
// Compound query: multiple where() clauses AND together.
// Range/inequality (<, <=, >, >=, !=) plus an order-by on another field ⇒ needs a composite index.
db.collection("cities")
  .where("state", "==", "CA")
  .where("population", "<", 1_000_000)
  .orderBy("population", "desc");
// in / array-contains-any / OR: up to 30 disjunctions; not-in up to 10 values.
db.collectionGroup("landmarks").where("type", "==", "museum");  // across all `landmarks` subcollections
```

```json
// firestore.indexes.json — single-field indexes are automatic; composites are declared.
{ "indexes": [
  { "collectionGroup": "cities", "queryScope": "COLLECTION", "fields": [
    { "fieldPath": "state", "order": "ASCENDING" },
    { "fieldPath": "population", "order": "DESCENDING" } ] } ] }
```

```
// Security Rules — evaluated on every mobile/web request; server libs skip them.
rules_version = '2';                                   // v2 required for collection group queries
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid} {
      allow read: if request.auth != null;             // any signed-in user
      allow write: if request.auth.uid == uid          // owner only, and shape-validate the write
                   && request.resource.data.email is string;
    }
  }
}
```

## The Native-vs-Datastore-mode decision (CRITICAL)

Both modes are the same engine and both are strongly consistent. **Mode is a per-database property
set at creation** (`--type=firestore-native` vs `--type=datastore-mode`). Changing it requires the
database to be **completely empty** and the switch takes a few minutes during which the database
rejects writes — so for any database holding data it is effectively **permanent**. A single project
may hold multiple databases in different modes. What differs:

- **Native mode** = mobile/web client libraries, real-time listeners, offline persistence, and
  Security Rules; strongly consistent queries across the whole database. Pick it for anything
  client-facing and for all new apps.
- **Datastore mode** = server-side only (no mobile/web SDKs, no listeners, no offline, **no Security
  Rules** — IAM only), the Datastore/GQL API, and the option to request eventual consistency. Pick
  it only if your app depends on the Datastore API. Full treatment in [[gcp-datastore]].

There is no live migration between modes; they are mutually exclusive per database.

## Gotchas

- **Index explosion / exemptions.** Every field is auto-indexed both ascending and descending, plus
  an array-contains index — great for ad-hoc queries, but large arrays/maps burn index entries and
  write cost (a document nearing ~40,000 index entries needs a **single-field index exemption**).
  Exempt fields you never filter/sort on, and exempt TTL and large-blob fields.
- **Hotspotting.** Monotonically increasing document IDs (`Customer1, Customer2, …`) or sequential
  indexed values (e.g. timestamps) concentrate writes on one lexicographic range and throttle
  latency — prefer the SDK's random auto-IDs. Follow the **500/50/5 rule**: ramp a new collection at
  ≤500 ops/sec, then +50% every 5 minutes, letting Firestore split the range.
- **Query limits.** No joins; a query hits one collection (or one collection-group). Disjunction
  (`or`, `in`, `array-contains-any`) is capped at **30** values, `not-in` at 10; you can't mix
  `array-contains` and `array-contains-any` in one OR group. Compound range + order-by needs a
  composite index — the error message links a one-click console builder.
- **Aggregations are `count()`, `sum()`, `average()` only.** Server-side, billed 1 read per up to
  1,000 index entries scanned, and subject to a **60-second** `DEADLINE_EXCEEDED` timeout; they
  can't be used with listeners or offline. Anything richer means reading documents or exporting to
  [[gcp-bigquery]].
- **Hard limits.** **1 MiB per document**; transactions 10 MiB / 270 s timeout (20 s lock, 60 s
  idle); a **batched write** or transaction commits at most **500** operations atomically; 100
  levels of subcollection nesting. Reads inside a transaction must precede writes, and transactions
  auto-retry on contention (batched writes do not).

## Pricing shape

Same structure as [[gcp-datastore]]: pay **per document operation** — reads, writes, deletes metered
per operation — plus **stored data per GiB/month** (documents *and* their index entries) and network
egress. **Queries bill one read per document returned** regardless of query complexity, so cost
tracks result-set size and listener churn, not query count. A perpetual free daily quota covers small
workloads. Two editions exist — **Standard** (pay-as-you-go) and **Enterprise** (adds MongoDB API
compatibility). Cost lever #1 is read volume; #2 is index fan-out on writes.

## vs siblings

- **[[gcp-datastore]]** — same engine, server-only API; no real-time, offline, or Security Rules.
  Choose Firestore Native unless locked to the Datastore/GQL API.
- **[[gcp-bigtable]]** — wide-column NoSQL for massive, low-latency throughput at TB–PB scale, node
  priced. Firestore is serverless/per-op and adds documents + real-time; Bigtable wins on raw
  sustained write/scan volume with no per-op billing.
- **[[gcp-spanner]]** — globally-distributed relational: SQL, joins, schemas, horizontal scale, and
  strong consistency. Pick it when you need SQL *and* scale; Firestore's no-join shallow-query model
  will fight relational access patterns.
- **[[gcp-alloydb]] / [[gcp-cloud-sql]]** — managed PostgreSQL/MySQL for relational workloads with
  joins, constraints, and transactions across tables. Reach for these when the data is relational and
  you don't need mobile-direct/offline/real-time.

Firestore's honest niche: **unstructured/semi-structured documents that mobile and web clients read
and write directly, synced live and offline, with access enforced by declarative rules** — not
analytics, not relational joins, not the highest-throughput key-value tier.

## Related

[[gcp-datastore]], [[gcp-bigtable]], [[gcp-spanner]], [[gcp-alloydb]], [[gcp-cloud-sql]], [[gcp-iam]],
[[gcp-bigquery]], [[gcp-cloud-functions]], [[gcp-cloud-run]], [[gcp-app-engine]], [[gcp-pubsub]],
[[gcp-secret-manager]], [[gcp-cloud-sdk]], [[gcp-cloud-monitoring]], [[secure-coding]]

Sources: https://docs.cloud.google.com/firestore/docs, https://docs.cloud.google.com/firestore/docs/firestore-or-datastore, https://docs.cloud.google.com/firestore/docs/data-model, https://docs.cloud.google.com/firestore/docs/query-data/queries, https://docs.cloud.google.com/firestore/docs/query-data/indexing, https://docs.cloud.google.com/firestore/docs/query-data/aggregation-queries, https://docs.cloud.google.com/firestore/docs/security/get-started, https://docs.cloud.google.com/firestore/docs/manage-data/transactions, https://docs.cloud.google.com/firestore/docs/best-practices, https://cloud.google.com/firestore/pricing (fetched 2026-07).
