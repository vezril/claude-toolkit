# Loading, change streams and integration

## The bulk loader

`POST https://<endpoint>:8182/loader`, with body type `application/json`. You can also call `aws neptunedata start-loader-job` or boto3 `neptunedata.start_loader_job`. It's the right way to get large volumes in. Remember that **the loader is not ACID**: data loaded before a failure stays loaded.

**Prerequisites**
- An IAM role that can read the S3 objects (plus KMS decrypt for SSE-KMS), **attached to the cluster**, passed as `iamRoleArn`. Comma-separated **role chaining** works for cross-account buckets (≥ 1.2.1.0.R3).
- An **S3 gateway VPC endpoint** in the cluster's VPC.
- The bucket must be in the **same region** as the cluster. SSE-S3 and SSE-KMS are supported. **SSE-C isn't**.

**Formats** (UTF-8 only; individual files may be `.gz` or `.bz2`; no tar archives):

| `format` | Model | Notes |
|---|---|---|
| `csv` | property graph (Gremlin CSV) | queryable by Gremlin *and* openCypher |
| `opencypher` | property graph (openCypher CSV) | queryable by both |
| `ntriples`, `nquads`, `rdfxml`, `turtle` | RDF | SPARQL only |

**Gremlin CSV**: vertices and edges go in separate files.
```
~id,name:String,age:Int,interests:String[],~label
v1,"marko",29,"sailing;graphs",person
v2,"lop",,,software

~id,~from,~to,~label,weight:Double
e1,v1,v2,created,0.4
```
- `~id` is required in both. Edges also need `~from` and `~to`. Multiple vertex labels go in `~label` separated by `;`, and an edge has one label.
- Property headers are `name:Type`, with types `Bool`, `Byte`, `Short`, `Int`, `Long`, `Float`, `Double`, `String`, `Date`, `Datetime`.
- Cardinality: `name:Type(single)`, `name:Type(set)` (the default), and `[]` for multiple values separated by `;`. Edge properties are always single.
- Empty fields are "no value". Set `parserConfiguration.allowEmptyStrings: true` to load `""` as a real empty string.

**openCypher CSV** uses the `:ID`, `:LABEL`, `:START_ID`, `:END_ID`, `:TYPE` headers. **Supply relationship IDs** (`userProvidedEdgeIds: TRUE`). Without them the loader can't resume a failed relationship load and can't detect duplicate relationships. All openCypher properties are single-cardinality. When node IDs repeat, the rows are merged (labels are unioned, and **one property value wins non-deterministically**).

**Key request parameters**

| Parameter | Default | Meaning |
|---|---|---|
| `source` | — | an S3 URI prefix: a file, a folder, or everything under the prefix |
| `mode` | `AUTO` | `NEW` reloads everything. `RESUME` retries only failed files of the previous load from this source. `AUTO` resumes if possible, otherwise NEW |
| `failOnError` | `TRUE` | `FALSE` skips bad records and continues |
| `parallelism` | `HIGH` | `LOW` (vCPU/8), `MEDIUM` (/2), `HIGH` (= vCPU), `OVERSUBSCRIBE` (×2). On `LOAD_DATA_DEADLOCK` (openCypher), lower it and retry |
| `updateSingleCardinalityProperties` | `FALSE` | `TRUE` replaces existing single values instead of raising an error |
| `queueRequest` | `FALSE` | `TRUE` queues the job FIFO (up to **64** queued). Otherwise the request fails if a load is running |
| `dependencies` | — | load IDs that must succeed first, otherwise `LOAD_FAILED_BECAUSE_DEPENDENCY_NOT_SATISFIED` |
| `edgeOnlyLoad` | `FALSE` | `TRUE` skips the vertex-first scan and loads files in listed order |

Check progress with `GET /loader/<loadId>?details=true&errors=true`. Neptune keeps the **last 1,024 jobs** and **10,000 errors per job**. To load faster, use a bigger writer for the duration of the load (scale it down afterwards) and many similar-sized files.

**Other ways in:** batched Gremlin, openCypher or SPARQL writes (idempotent, small transactions); AWS DMS with Neptune as the target (relational to graph via a mapping); AWS Glue with `neptune-python-utils`; `g.io(url).read()` for GraphML/GraphSON from a presigned URL; the GraphML2CSV converter.

**Getting data out:** the `neptune-export` utility (CSV, JSON, RDF, to S3), Streams (below), or queries.

## Neptune Streams (change data capture)

- Turn it on with the cluster parameter `neptune_streams=1` (static, so reboot).
- Retention is **7 days** by default, **1–90 days** via `neptune_streams_expiry_days` (≥ 1.2.0.0).
- Reading: `GET https://<endpoint>:8182/propertygraph/stream` (Gremlin/openCypher data; the older path `/gremlin/stream`) or `/sparql/stream`, with an iterator type and `commitNum`/`opNum` to resume. The API is also available as `neptunedata get-propertygraph-stream`.

Guarantees:
- Every committed change is logged **exactly once**, **in order** (including within a transaction), **with nothing missing**.
- The log is written **synchronously** in the same transaction.
- It's readable from the writer and the replicas.

Costs and constraints:
- A small write-performance penalty, plus I/O and storage charges.
- Stream reads compete with queries for the same instance resources.
- **Disabling streams makes the log unreadable immediately**, so drain it first.
- **No native Lambda trigger.** Consumers poll. AWS provides a streams **polling framework** (a Lambda on a schedule, with a DynamoDB checkpoint table, deployed via CloudFormation). See [[aws-lambda]].

Typical uses:
- **full-text search**: sync to Amazon OpenSearch, then query it through Neptune's OpenSearch integration
- a cache (ElastiCache) or S3 data lake sync
- notifications
- **Neptune-to-Neptune replication** for cross-region DR, as an alternative to Global Database

## Full-text search

Neptune doesn't do full-text search itself. The pattern is: Streams → the AWS-provided replication consumer → **Amazon OpenSearch Service** index. Queries then call OpenSearch from Gremlin (`g.withSideEffect('Neptune#fts.endpoint', …)` with `Neptune#fts.*` predicates) or from SPARQL (`SERVICE neptune-fts:search`). Geospatial search uses the same OpenSearch pairing.

## Neptune ML

Neptune ML uses graph neural networks (via Deep Graph Library on Amazon SageMaker AI) for node classification or regression, link prediction and edge classification, with predictions queried inline from Gremlin or SPARQL. It's configured with `neptune_ml_iam_role` and `neptune_ml_endpoint`. The pipeline is export → data processing → training → endpoint. It's a substantial SageMaker setup, so confirm the current workflow and region support in the docs before committing. For simpler "score and use" needs, compute features in **Neptune Analytics** and write them back.

## Tooling

- **graph-notebook**: Jupyter with `%%gremlin`, `%%oc`, `%%sparql` magics and visualization. Managed notebooks run via SageMaker AI. Free to learn on without a production cluster.
- **Graph Explorer**: an open-source visual explorer for property-graph and RDF data.
- Third-party visualization: Tom Sawyer, Cambridge Intelligence (KeyLines/ReGraph), Graphistry, metaphacts, G.V(), Linkurious.
- GraphQL: through AWS AppSync resolvers (a custom integration). There's no built-in GraphQL endpoint.
