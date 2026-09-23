# SessionManager: graph over the data lake

The workflow is **create → import → analyze → export → destroy**. Your tables stay the source of truth. Neptune Analytics exists only while you analyze, and each import is a full fresh projection, so there's no sync pipeline to maintain. `from nx_neptune.session_manager import SessionManager, CleanupTask`.

The API is **async** (`await`). It runs as-is in Jupyter. In a script, wrap it in `asyncio.run(main())`. The docs say it can also run in Lambda, but graph provisioning takes minutes, so watch the 15-minute limit.

## Constructing

```python
session = SessionManager.session(session_name="fraud-ring", cleanup_task=CleanupTask.DESTROY)
# same as SessionManager("fraud-ring", CleanupTask.DESTROY)
```

- The constructor is `SessionManager(session_name=None, cleanup_task=None)`. Region and credentials come from the standard boto3 chain (`AWS_REGION`, profile, role). The docs' `SessionManager(graph_id=..., region=..., iam_role_arn=..., s3_import_path=..., s3_export_path=...)` example **doesn't match the code**.
- Constructing calls STS `GetCallerIdentity`. The **caller's own ARN** is used as the role for S3 import/export, so that identity needs the S3/KMS permissions and must be assumable by Neptune for import tasks. See the IAM notes in `data-sources-and-deployment.md`.
- `session_name` is a **name prefix**. New graphs are named `{session_name}-{uuid}`, and every list, get or destroy method filters to graphs whose name *starts with* the prefix. `None` means every graph in the account and region.
- `CleanupTask`: `NONE`, `DESTROY`, `RESET`, `STOP`. Only `DESTROY` does anything, only in a `with` block, and only reliably in Jupyter. See SKILL.md non-negotiable 6. Use `try/finally: await session.destroy_all_graphs()`.

## Methods

| Method | Async | Does |
|---|---|---|
| `list_graphs()` | no | `NeptuneAnalyticsClient` objects in the session (`.graph_id`, `.name`, `.status`, `.details`) |
| `get_graph(graph_id)` | no | one graph by id, restricted to the session. Raises if it's not found |
| `get_or_create_graph(config=None)` | yes | first **AVAILABLE** graph in the session, otherwise creates one. `config` = boto3 `create_graph` kwargs |
| `create_from_csv(s3_arn, config=None)` | yes | new graph loaded from S3 CSV in one step |
| `create_from_snapshot(snapshot_id, config=None)` | yes | new graph from a snapshot |
| `create_multiple_instances(count, config=None)` | yes | parallel creates. Returns graph **ids** |
| `import_from_table(graph, s3_location, sql_queries, sql_parameters=None, catalog=None, database=None, remove_buckets=True)` | yes | runs the Athena projections to CSV in `s3_location`, imports them, deletes the CSVs. Returns the **import task id** (the docstring says graph id) |
| `import_from_csv(graph, s3_location, reset_graph_ahead=False, max_size=None)` | yes | loads CSV already in S3. On `InsufficientMemory`, **doubles provisioned memory** up to `max_size` GB and retries |
| `export_to_csv(graph, s3_location, export_filter=None)` | yes | export task to S3. Returns the task id |
| `export_to_table(graph, s3_location, csv_table_name, csv_catalog, csv_database, iceberg_vertices_table_name, iceberg_edges_table_name, iceberg_catalog, iceberg_database, remove_resources=True)` | yes | graph → CSV → Athena CSV tables (`{csv_table_name}_vertices` / `_edges`) → two Iceberg tables, then cleans up the intermediates |
| `create_snapshot(graph, snapshot_name)` / `delete_snapshot(snapshot_id)` | yes | snapshots (`neptune-graph:CreateGraphSnapshot` etc.) |
| `start_graph(name)` / `stop_graph(name)` / `reset_graph(name)` / `destroy_graph(name)` | returns a future | accepts a **graph name** (or list of names), not an id. Acts only on graphs in the right state: start needs STOPPED, the others need AVAILABLE. Anything else is skipped with a warning |
| `start_all_graphs()` / `stop_all_graphs()` / `reset_all_graphs()` / `destroy_all_graphs()` | returns a future | the same, for every graph matching the prefix |
| `validate_permissions()` | no | checks the caller's IAM against the import/export buckets and their KMS keys |

The graph object you pass around is `NeptuneAnalyticsClient`. It has `graph.execute_query(opencypher)` and `graph.execute_generic_query(query, parameter_map)`, which return the raw boto3 `ExecuteQuery` response.

## Projection SQL

You write one Athena `SELECT` per node set and one per edge set, and pass them as a list. Each query becomes one CSV in Neptune's openCypher CSV format.

| Projection | Required columns | Optional |
|---|---|---|
| Node | `"~id"` | `"~label"`; any other column becomes a property |
| Edge | `"~from"`, `"~to"` | `"~label"` (the relationship type); other columns become properties |

- Type a property with a `"name:Type"` alias: `"amount" AS "amount:Float"`. Types follow the Neptune Analytics openCypher CSV data formats. Check that page for the exact type names.
- Put a vector in a node column aliased exactly `"embedding:vector"`. Any other `*:vector` or `embedding:*` name fails validation. The graph's vector index dimension must match. See [[aws-neptune]].
- **Double-quote the tilde aliases.** Athena treats `~id` without quotes as a syntax error.
- Deduplicate node ids (`SELECT DISTINCT`). Filter `NULL`s on both endpoints so you don't create dangling edges.
- Edges whose `~from`/`~to` have no matching node row: Neptune's import behaviour applies. Project nodes from the **union of both endpoint columns** so every edge has its endpoints.
- `SELECT *` bypasses validation (warning only).
- `sql_parameters` is a list of parameter lists, one per query, for Athena `?` placeholders.
- `catalog` / `database` select the Athena namespace. For S3 Tables, use `s3tablescatalog/<table-bucket>` and your namespace. For federated sources, use the connector's catalog name.

### Worked example: fraud rings (from the project walkthrough)

```python
import asyncio, os
from nx_neptune.session_manager import SessionManager

ACCOUNTS = """
SELECT DISTINCT "~id", 'account' AS "~label"
FROM (
  SELECT "nameOrig" AS "~id" FROM transactions_iceberg WHERE "nameOrig" IS NOT NULL
  UNION ALL
  SELECT "nameDest" AS "~id" FROM transactions_iceberg WHERE "nameDest" IS NOT NULL
)"""

TRANSACTIONS = """
SELECT "nameOrig" AS "~from", "nameDest" AS "~to", "type" AS "~label",
       "amount" AS "amount:Float"
FROM transactions_iceberg
WHERE "nameOrig" IS NOT NULL AND "nameDest" IS NOT NULL"""

async def main():
    session = SessionManager.session("fraud-ring")
    graph = await session.get_or_create_graph(
        config={"provisionedMemory": 32, "publicConnectivity": False})
    try:
        await session.import_from_table(
            graph, os.environ["NETWORKX_S3_IMPORT_BUCKET_PATH"],
            [ACCOUNTS, TRANSACTIONS],
            catalog=os.environ["NETWORKX_S3_TABLES_CATALOG"],
            database=os.environ["NETWORKX_S3_TABLES_DATABASE"])

        graph.execute_query(
            'CALL neptune.algo.louvain.mutate({iterationTolerance:1e-07, '
            'writeProperty:"community"}) YIELD success RETURN success')

        await session.export_to_table(
            graph, os.environ["NETWORKX_S3_EXPORT_BUCKET_PATH"],
            csv_table_name="transactions_csv", csv_catalog="AwsDataCatalog", csv_database="graph_demo",
            iceberg_vertices_table_name="accounts_updated",
            iceberg_edges_table_name="transactions_updated",
            iceberg_catalog="s3tablescatalog/nx-neptune-data", iceberg_database="graph_demo")
    finally:
        await session.destroy_all_graphs()

asyncio.run(main())
```

- `louvain.mutate` with `writeProperty` returns only `success`. Drop `.mutate` and `writeProperty` to get assignments back in the query result.
- To inspect the biggest communities, query or use Graph Explorer (Neptune → Notebooks → Actions → Open Graph Explorer):
  ```cypher
  MATCH (n) WITH n.community AS c, count(n) AS size ORDER BY size DESC LIMIT 100
  MATCH (n) WHERE n.community = c MATCH p=(n)-[*1..3]-() RETURN p
  ```
  Bound variable-length paths like this. `[*1..3]` over hub accounts still fans out fast.
- `export_to_table` result: `accounts_updated` (every vertex, now with `community`) and `transactions_updated` (every edge), registered in the catalog for BI and ML.

### Preparing CSV sources as Iceberg (walkthrough step)

Keep the raw CSV in its **own S3 prefix**. An Athena external table reads *every* file under `LOCATION`, so mixing it with the import, export or staging prefixes corrupts the table.

```sql
CREATE EXTERNAL TABLE transactions (...) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LOCATION 's3://bucket/paysim/' TBLPROPERTIES ('skip.header.line.count'='1');
CREATE TABLE transactions_iceberg WITH (table_type='ICEBERG', is_external=false)
AS SELECT * FROM transactions;
```

## Lifecycle and cost

- A graph bills while it's **AVAILABLE**. You can stop it (cheaper, keeps data) or snapshot and destroy it. Provisioning or restoring takes minutes.
- Prefer snapshots for re-analysis across days. `create_snapshot` → `destroy_graph` → later `create_from_snapshot`.
- Size memory to the projection. 16 m-NCU is the default. `import_from_csv(max_size=...)` can grow it automatically. `import_from_table` has no such retry, so an undersized graph fails the import.
- The Athena scan cost is per projection query, every import. Project only the columns you need.
- Things you clean up yourself: the staging, import and export buckets, logs under `s3_location` (Athena writes query output there), source tables, and any graph created without a session prefix.

## Gotchas

| Symptom | Cause |
|---|---|
| `get_or_create_graph` returns an unexpected graph | Prefix match. Another graph whose name starts with your session name was AVAILABLE |
| New graph created although one exists | The existing one is STOPPED or still CREATING. Only AVAILABLE graphs are reused |
| `AttributeError` / `TypeError` passing `graph["id"]` | Pass the `NeptuneAnalyticsClient` object itself |
| `Exception: Projections not created.` | All Athena queries failed validation or execution. Check the `~id`/`~from`/`~to` aliases, quoting, and catalog/database |
| Import fails `InsufficientMemory` | Undersized graph. Recreate larger, or stage to CSV and use `import_from_csv(max_size=…)` |
| `destroy_graph("g-…")` does nothing | It takes graph **names**, not ids |
| Graphs still running after the script exits | `CleanupTask` didn't fire. Always `await` destroy in `finally` |
