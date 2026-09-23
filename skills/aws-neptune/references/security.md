# Neptune security

## Network

- **VPC-only.** Instances can't be reached from outside the VPC. To reach them from elsewhere: run the app in the VPC (Lambda in the VPC, ECS, EC2); use VPN, Direct Connect or peering; use an SSM port-forward through a bastion for humans; or put a proxy or load balancer in front (terminate carefully, and remember that IAM auth signs with the *Neptune host*).
- **TLS 1.2 only** (HTTPS/WSS), with a strong ECDHE cipher list. Plain HTTP is impossible since 1.0.4.0, and `neptune_enforce_ssl` is deprecated.
- The DB subnet group needs **at least 2 AZs**; use 3. Security groups should allow 8182 only from the app tiers that need it.
- Neptune **Analytics** can have a **public endpoint** (opt-in) as well as private ones. Prefer private endpoints for anything real.

## Authentication: IAM database auth

- Neptune has **no username/password**. Enable **IAM database authentication** on the cluster, and every data-plane request must then be **SigV4-signed** with `service=neptune-db`, the cluster's region, and the host used for the connection. Without IAM auth, network reachability is the only barrier.
- Neptune authenticates at connect time and **re-checks WebSocket permissions periodically**. Rotating or deleting a principal's credentials **doesn't close already-open connections**. IAM-auth WebSockets are forcibly closed about **10 days** after opening.
- Clients:
  - `awscurl --service neptune-db`
  - the AWS CLI `neptunedata` commands and boto3 `neptunedata` (signed automatically)
  - TinkerPop drivers with a SigV4 handshake interceptor (AWS publishes `amazon-neptune-sigv4-signer`, and the gremlin-python and Java drivers take request interceptors)
  - Bolt with an auth token built from a SigV4-signed request
- Use **roles with temporary credentials** (Lambda or ECS task roles, instance profiles). Never long-lived keys.

## Authorization: data-access policies

The action prefix is `neptune-db:`. The resource is the cluster's data plane, `arn:aws:neptune-db:<region>:<account>:<cluster-resource-id>/*` (the *resource ID* `cluster-XXXX`, not the cluster name).

- Engine **≥ 1.2.0.0** has granular query actions. Earlier versions only had cluster-level connect:

| Action | Needed by |
|---|---|
| `ReadDataViaQuery` | any read, including the read half of writes |
| `WriteDataViaQuery` | inserts: `addV`, `addE`, `MERGE`, `CREATE`, SPARQL INSERT |
| `DeleteDataViaQuery` | `drop()`, `DETACH DELETE`, SPARQL DELETE, **and any `property()` or `SET`** (they may replace a value) |
| loader, streams, status, reset, ML actions | separate `neptune-db:*` actions (for example starting and reading loader jobs, reading stream records, resetting the database). Grant them only to the pipelines that need them |

- Permission is computed from **every action a query *could* perform**, not what it actually does on your data. `g.addV()` needs Read+Write. `g.V('1').property(single,'k','v')` needs Read+Write+Delete. openCypher `SET` always needs all three, and `MERGE` needs Read+Write.
- **Condition keys** can restrict by query language (let an analytics role use openCypher reads only). **Tag-based access control** is available for data-plane operations. Check the current condition-key names in the "IAM condition keys for accessing data" page before writing policies.
- Minimal read-only app role:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["neptune-db:ReadDataViaQuery"],
    "Resource": "arn:aws:neptune-db:ca-central-1:111122223333:cluster-ABCDEFGHIJKLMNOP/*"
  }]
}
```

- Keep **management-plane** permissions (`neptune:CreateDBCluster`, `ModifyDBCluster`, parameter groups, snapshots) separate from **data-plane** `neptune-db:*` permissions. The console needs `NeptuneReadOnlyAccess`.
- **Destructive endpoint:** the fast-reset API (`/system`, `ResetDatabase` tokens) wipes the graph. Deny its action explicitly for everything except controlled admin roles.

## Encryption

- **At rest:** AWS KMS, **chosen at cluster creation** (customer-managed keys supported). It covers storage, automated backups, snapshots and replicas. You can't encrypt an existing unencrypted cluster in place: snapshot, restore with encryption, then cut over.
- **In transit:** TLS 1.2, always.
- Bulk-load sources can be SSE-S3 or SSE-KMS (the loader role needs `kms:Decrypt`). SSE-C isn't supported.

## Auditing and monitoring

- **Audit logs** (`neptune_enable_audit_log=1`, static) to CloudWatch Logs: who ran what, from where.
- **CloudTrail** records management API calls. Data-plane queries appear in audit logs, not CloudTrail.
- **Slow-query logs** help spot abusive or runaway queries. Pair them with a sane `neptune_query_timeout`.

## Multi-tenancy isolation

There's one graph per cluster, so tenant isolation is either:
- **cluster per tenant**: strongest; Serverless keeps the cost reasonable
- **a shared graph with a mandatory `tenantId`** on every element and every query, enforced in a data-access layer that application code can't bypass

IAM can't filter rows by property, so the shared-graph model relies entirely on the application.
