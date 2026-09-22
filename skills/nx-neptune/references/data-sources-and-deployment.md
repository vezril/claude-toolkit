# Data sources, IAM, deployment, and doc discrepancies

## Data sources

Every source except native S3 CSV/Parquet import goes through **Amazon Athena**. nx-neptune runs your projection SQL in Athena, writes the results to S3 as CSV, and Neptune Analytics imports that CSV. A source works if Athena can query it.

| Source | Connector | Setup you own | Notes |
|---|---|---|---|
| **Amazon S3 Tables** (Iceberg) | native Athena | table bucket + namespace; catalog `s3tablescatalog/<bucket>` | Also the **export target** (`export_to_table`). Needs `athena:StartQueryExecution`, `athena:GetQueryExecution`, `s3:GetObject` |
| **Amazon S3 Vectors** | custom `athena-s3vector-connector` (Lambda, in the repo's `connectors/`) | build and deploy it to your account | Projects embeddings as `"embedding:vector"` for graph + similarity search |
| **Databricks Unity Catalog** | custom JDBC `athena-databricks-connector` (in `connectors/`) | build and deploy it to your account | Federated query into UC tables |
| **Snowflake** | AWS-provided Athena Snowflake connector | deploy from the Serverless Application Repository; IAM for Athena + the connector Lambda | |
| **Amazon OpenSearch** | AWS-provided Athena OpenSearch connector | deploy connector | A **VPC** domain needs the connector Lambda configured with VPC access to reach it |
| Any other Athena source | 25+ federated connectors | per connector | Use the connector's catalog name as `catalog=` |
| CSV/Parquet already in S3 | none (Neptune native import) | — | `create_from_csv` / `import_from_csv`; no Athena |

Federated queries run in a Lambda, so large projections hit Lambda time and spill limits before Athena's own. Push filters into the projection SQL.

## IAM

The identity running nx-neptune (the SessionManager uses the STS caller ARN for S3 tasks) needs the following:

| Purpose | Actions |
|---|---|
| Query / algorithms / backend sync | `neptune-graph:ReadDataViaQuery`, `WriteDataViaQuery`, `DeleteDataViaQuery` |
| Lifecycle | `neptune-graph:StartGraph`, `StopGraph`, plus create, delete and get/list graph and import/export task actions for SessionManager creates |
| Snapshots | `neptune-graph:CreateGraphSnapshot`, `RestoreGraphFromSnapshot`, `DeleteGraphSnapshot`, `TagResource` |
| S3 import/export | `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `kms:Decrypt`, `kms:GenerateDataKey`, `kms:DescribeKey` |
| Data lake | `athena:StartQueryExecution`, `athena:GetQueryExecution`, plus Glue catalog read/write for table creation on export |

- The docs' S3 list includes **`s3:DeleteBucket`**. The library deletes *objects* (staged CSVs), so check whether you really need to grant bucket deletion. Grant `s3:DeleteObject` on the staging prefix, and add `DeleteBucket` only if your own teardown needs it.
- Neptune import/export tasks run under a **role Neptune assumes** (`neptune-graph.amazonaws.com` in its trust policy). For the backend, that role is `s3_iam_role` / `NETWORKX_S3_IAM_ROLE_ARN`. For SessionManager, it's the caller's own ARN, which works when the caller is a role (for example the SageMaker notebook role) whose trust policy allows Neptune.
- If the buckets use SSE-KMS, the key policy must allow that role. The library looks up each bucket's encryption key for you.
- Scope the `neptune-graph` data actions to the session's graphs. ARNs are `arn:aws:neptune-graph:<region>:<acct>:graph/<graph-id>`. Graph ids are random, so scope by tag (`agent=nx-neptune`, plus your own tags passed in `config["tags"]`).

## Environment variables

| Variable | Read by | Purpose |
|---|---|---|
| `NETWORKX_GRAPH_ID` | backend | target graph id |
| `NETWORKX_S3_IAM_ROLE_ARN` | backend | role for S3 import/export. The docs call it `NETWORKX_ARN_IAM_ROLE`, but the code reads this name |
| `NETWORKX_S3_IMPORT_BUCKET_PATH` | notebooks, `validate_permissions` | import staging path (`s3://bucket/import/`) |
| `NETWORKX_S3_EXPORT_BUCKET_PATH` | notebooks, `validate_permissions` | export path |
| `NETWORKX_STAGING_BUCKET` | notebooks | staging root |
| `NETWORKX_S3_TABLES_CATALOG` / `NETWORKX_S3_TABLES_DATABASE` | notebooks | Athena namespace for S3 Tables |
| `AWS_REGION` | boto3 | region |

The SessionManager methods take paths as **arguments**. Apart from `validate_permissions`, the env vars are a notebook convention the library doesn't read. In Jupyter, set them with `%env NAME=value`. A kernel doesn't see `export`s made after it started.

## CloudFormation demo stack

`cloudformation-templates/nx-neptune-sagemaker.json` creates the following:
- a Neptune Analytics graph (`ProvisionedMemory` 16/32/64 m-NCU, default 16)
- a SageMaker notebook (`ml.t3.medium`) with nx_neptune installed
- a versioned, KMS-encrypted S3 staging bucket plus its key
- an IAM role with Neptune, S3, KMS, Athena, Glue and SageMaker permissions

```bash
./cloudformation-templates/deploy.sh                          # nx-neptune-demo, us-west-1, PyPI
./cloudformation-templates/deploy.sh my-stack us-east-1       # custom
./cloudformation-templates/deploy.sh my-stack us-east-1 true  # build + ship local wheel
./cloudformation-templates/teardown.sh my-stack us-east-1     # empties ALL bucket versions, deletes stack
```

- The stack name and `ApplicationId` are **16 characters max**.
- `PublicConnectivity` defaults to **true**. Override it for anything beyond a demo.
- For a manual deploy: build the wheel, zip `notebooks/`, upload both under `AssetsS3Prefix`, then `aws cloudformation deploy --capabilities CAPABILITY_NAMED_IAM --parameter-overrides AssetsS3Prefix=s3://…`.
- Outputs: `GraphId`, `NotebookURL`, `StagingBucketName`.
- The notebook shows up under Neptune → Notebooks as `aws-neptune-nx-neptune` by default. Open JupyterLab and use the `conda_python3` kernel. `notebooks/import_s3_table_demo.ipynb` is the walkthrough.
- The notebook's env vars are set by the stack. **Changing them needs a notebook stop and start.** Every start reinstalls nx_neptune (the wheel if one was provided, otherwise PyPI latest), so pin the version via the wheel if you need reproducibility.
- The notebook's session name must match `ApplicationId` (default `nx-neptune-graph` in the walkthrough) so `get_or_create_graph` finds the stack's graph instead of creating a second one.
- The bucket is versioned, so a plain `aws s3 rm --recursive` leaves old versions behind and blocks stack deletion. Use `teardown.sh`.

## Development

- `make install`, `make test` (unit, pytest), `make integ-test` (needs `NETWORKX_GRAPH_ID` of a live graph; backend calls clear it, so use a scratch graph).
- `make lock` regenerates the pip-tools lock files and must run under **Python 3.11** to match CI.
- Layout: `nx_neptune/` (algorithms, session manager, instance management, clients), `nx_plugin/` (backend registration + `NeptuneConfig`), `connectors/` (Databricks, S3 Vectors), `notebooks/`, `cloudformation-templates/`, `tests/`, `integ_test/`.
- A new algorithm follows the pattern `@configure_if_nx_active()` → build openCypher → execute → convert. Register it in the list in `nx_neptune/interface.py`.

## Doc vs source discrepancies (0.6.0)

| Docs say | Code does |
|---|---|
| `SessionManager(graph_id=, region=, iam_role_arn=, s3_import_path=, s3_export_path=)` | `SessionManager(session_name=None, cleanup_task=None)`. Everything else is a method argument or boto3 config |
| Blog: `import_from_table(graph["id"], …)` | takes the `NeptuneAnalyticsClient` object |
| Env var `NETWORKX_ARN_IAM_ROLE` | reads `NETWORKX_S3_IAM_ROLE_ARN` |
| "Transparently syncs your graph" | clears the remote graph first (`MATCH (n) DETACH DELETE n`) unless `skip_graph_reset` |
| `vertex_label="Person", edge_labels=["KNOWS"]` backend example | synced data is labeled `Node` / `RELATES_TO`, so those filters match nothing on synced graphs |
| Interface page lists 12 algorithms | 14 are wired: also `weakly_connected_components` and `jaccard_coefficient` (the Algorithms page does document them) |
| `CleanupTask` STOP/RESET described in docstrings | only DESTROY acts, only in `with`, and it isn't awaited |
| `import_from_table` "returns graph ID" | returns the import task id |
| `NeptuneConfig` in `nx_plugin/config.py` handles SessionManager settings | it configures the **backend** only |

Re-check this table when upgrading past 0.6.0. It's an alpha, and these are the spots most likely to change.
