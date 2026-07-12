---
name: gcp-datastore
description: "Firestore in Datastore mode (the product formerly named Google Cloud Datastore) — serverless schemaless NoSQL for server workloads: entities under kinds with hierarchical keys (namespace/kind/ID + ancestor path), every indexed property auto-indexed, queries answer only what an index can serve (no joins), composite indexes declared in index.yaml, GQL, serializable transactions, strong consistency everywhere since the Firestore-backend upgrade. Use when working with legacy Datastore / Datastore-mode databases (classic App Engine stacks), writing GQL or index.yaml, debugging needs-index or exploding-index errors, tuning entity-group and transaction limits, or choosing between Datastore mode, Firestore Native, Bigtable, and Cloud SQL."
license: MIT
---

# Firestore in Datastore mode (Cloud Datastore)

**The naming story.** "Cloud Datastore" no longer exists as a separate product. Its successor is
**Firestore in Datastore mode**: the Datastore API and data model running on Firestore's storage
layer. Google automatically upgraded all legacy Datastore databases (rollout began 2021; the docs
as of 2026-07 only say legacy databases "were upgraded" — no action was required). The upgrade
made every query **strongly consistent** and removed the old 1-write/sec-per-entity-group and
25-entity-group-per-transaction limits — *except* for upgraded databases still running the legacy
"Optimistic With Entity Groups" concurrency mode (see Gotchas). Docs, console, and `gcloud
datastore` still use the Datastore name; billing and locations are Firestore's.

**For new projects** the docs now say: "Use Firestore in Native mode for all new applications
(server, mobile, and web)" (guidance as of 2026-07 — earlier docs, roughly 2019–2023, steered new
*server* projects to Datastore mode). Pick Datastore mode today only for compatibility: existing
Datastore codebases, App Engine `ndb`/client-library stacks, or GQL dependence. A database is
permanently one mode or the other — Native rejects Datastore API calls and vice versa.

## The mental model

- **Schemaless entities under kinds.** An entity = named properties (int, float, string, dates,
  blobs, arrays...). A kind is a query namespace, not a schema: "Entities of the same kind don't
  need to have the same properties," and the same property can hold different types in different
  entities. Type discipline is your application's job.
- **Keys are hierarchical.** Key = namespace (multitenancy) + kind + identifier (string name or
  auto-allocated numeric ID) + optional **ancestor path**, e.g.
  `[User:alice, TaskList:default, Task:sampleTask]`. A parent set at creation is permanent. A root
  entity plus all descendants = an **entity group**. Auto IDs are random and roughly uniformly
  distributed (up to 16 digits) — never use `0` as a manual numeric ID (it triggers allocation).
- **Everything queryable is indexed.** Built-in single-property indexes are predefined for every
  property of every kind. "Every query computes its results using one or more indexes" — a query
  never scans entities. Corollary: a query can only answer what some index can serve. No joins
  ("non-scaling queries"), one property per query with inequality filters, projections only over
  indexed properties. Aggregations exist but are index-served too: `COUNT(*)`, `COUNT_UP_TO(n)`,
  `SUM()`, `AVG()`.
- **Composite indexes are declared, not inferred.** Multi-property queries (filter + other-property
  sort, multiple sorts, some projections) need a composite index defined in `index.yaml` and
  deployed before the query works. The inequality-filter property must be ordered first.
- **Consistency is strong.** Since the Firestore-backend upgrade, all queries — including
  non-ancestor queries, which were *eventually* consistent in legacy Datastore — are strongly
  consistent. Ancestor queries are no longer needed for consistency, only for scoping to a subtree.

## Shapes (verified against docs)

```sql
-- GQL: SELECT * | property-list (projection) | __key__ FROM kind ...
SELECT * FROM Task WHERE done = FALSE
SELECT * FROM Person WHERE age >= 18 AND age <= 35     -- inequalities: one property only
SELECT * WHERE __key__ HAS ANCESTOR KEY(Person, 'Amy') -- ancestor scoping (kindless here)
SELECT COUNT(*) FROM Task WHERE done = FALSE           -- aggregation, index-served
-- Operators: =, IN, CONTAINS, IS NULL, HAS ANCESTOR/DESCENDANT, <, <=, >, >=, !=, NOT IN
-- Plus: DISTINCT ON (props), LIMIT/OFFSET (counts or @cursor bindings)
```

```yaml
# index.yaml — composite indexes (built-in single-property indexes need no config)
indexes:
- kind: Task
  properties:
  - name: priority
  - name: percent_complete   # direction defaults to asc; add `direction: desc` to sort desc
```

```sh
gcloud firestore databases create --location=nam5 --type=datastore-mode  # new DB (mode is permanent)
gcloud datastore indexes create index.yaml --database=DATABASE_ID       # deploy composites (async build)
gcloud datastore indexes cleanup index.yaml                             # delete indexes not in the file
gcloud firestore databases update --concurrency-mode=OPTIMISTIC ...     # shed legacy entity-group limits
```

## Transactions

Serializable isolation, atomic ("all of the operations... are applied, or none"). New Datastore
mode databases default to **pessimistic** concurrency (reader/writer locks); upgraded legacy
databases got **optimistic** or **Optimistic With Entity Groups**. Limits: 10 MiB per transaction,
expiry at 270 s (or 60 s idle), 500 property transformations per commit, 1,000 keys per lookup.
Two sharp edges: reads inside a transaction do **not** see that transaction's earlier writes, and
nothing auto-retries — write idempotent transactions and retry contention failures yourself.
Read-only transactions dodge contention entirely and give a consistent snapshot.

## Gotchas

- **Exploding indexes.** A composite index over multiple array-valued properties gets one entry per
  value *combination*: 3 tags × 3 collaborators = 9 entries in one index, vs 6 across two separate
  indexes. Cap: 20,000 indexed property values + composite entries per entity, 2 MiB of composite
  entries — writes fail with "Index entries too large" / "Too many indexed properties."
- **Index hygiene is manual.** Composite indexes: 200 per database (1,000 with billing). Excluding
  a property from indexing also disables it in any composite index that references it, and
  re-including requires rewriting every existing entity. Indexed strings cap at 1,500 bytes —
  store long text with exclude-from-indexes (unindexed properties go up to ~1 MiB).
- **Legacy limits linger by concurrency mode, not by product.** Databases left in "Optimistic With
  Entity Groups" still have: 1 write/sec per entity group, 25 entity groups per transaction, and
  ancestor-only queries inside transactions. Switching to OPTIMISTIC/PESSIMISTIC via
  `gcloud firestore databases update` removes them — it is not automatic.
- **Entity size**: max 1,048,572 bytes (1 MiB − 4 B); key ≤ 6 KiB; API request ≤ 10 MiB.
- **Kindless queries** (no kind, no ancestor) sweep the whole database and cannot filter or sort on
  property values. **No real-time listeners and no offline persistence** — those are Native-mode
  features; polling or Pub/Sub is your change-feed here.

## Pricing shape

Identical structure (and SLA/locations) to Firestore Native: you pay **per entity operation** —
reads, writes, deletes metered per 100K ops, with small operations (keys-only queries, aggregation
results) cheaper than full entity reads — plus **storage per GiB/month** (entities *and their index
entries*, so exploding indexes cost storage too) and network egress. A perpetual free daily quota
covers small workloads. Cost lever #1 is index count: every write fans out to every index entry.

## vs siblings

- **Firestore (Native mode)**: same infrastructure, different API and model — documents/collections,
  real-time listeners, offline sync, mobile/web SDKs (12 client libraries vs Datastore mode's 8,
  which exclude mobile/web). Google's pick for all new apps. No migration path in place: modes are
  mutually exclusive per database.
- **Bigtable**: wide-column NoSQL for massive throughput/low-latency at TB–PB scale; node-based
  pricing, no per-op billing, no GQL/serializable-transaction surface. Datastore mode is serverless
  and per-op — better for spiky, modest-scale server state.
- **Cloud SQL / AlloyDB / Spanner**: relational — joins, SQL, schemas, constraints. If your access
  patterns aren't key-lookups plus pre-indexable filters, Datastore mode's no-join model will fight
  you; go relational (Spanner when you need horizontal scale *and* SQL).

## Related

[[gcp-bigtable]], [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-spanner]], [[gcp-bigquery]],
[[gcp-memorystore-redis]], [[gcp-app-engine]], [[gcp-cloud-run]], [[gcp-cloud-functions]],
[[gcp-pubsub]], [[gcp-cloud-sdk]], [[gcp-iam]], [[gcp-cloud-monitoring]]

Sources: https://docs.cloud.google.com/datastore/docs, https://docs.cloud.google.com/datastore/docs/firestore-or-datastore, https://docs.cloud.google.com/datastore/docs/concepts/entities, https://docs.cloud.google.com/datastore/docs/concepts/queries, https://docs.cloud.google.com/datastore/docs/concepts/indexes, https://docs.cloud.google.com/datastore/docs/concepts/transactions, https://docs.cloud.google.com/datastore/docs/concepts/limits, https://docs.cloud.google.com/datastore/docs/upgrade-to-firestore, https://docs.cloud.google.com/datastore/docs/reference/gql_reference, https://cloud.google.com/datastore/pricing (fetched 2026-07).
