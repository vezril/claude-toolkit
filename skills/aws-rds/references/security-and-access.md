# Security and access

Source: docs.aws.amazon.com (AmazonRDS/latest/UserGuide, security) + AWS's RDS advisor agent skill. Fetched 2026-09.

## Encryption

- **At rest:** `--storage-encrypted --kms-key-id <arn>` at creation time. Use a **customer-managed** KMS key over the default AWS-owned key so you control rotation, access policy, and cross-account sharing — the AWS-owned default can't be inspected or restricted the same way.
- **In transit:** enforced at the **parameter-group** level, not just by asking the client to use TLS:
  - MySQL/MariaDB: `require_secure_transport=ON`
  - PostgreSQL: `rds.force_ssl=1`
```bash
aws rds create-db-parameter-group --db-parameter-group-family mysql8.4 --db-parameter-group-name my-tls --description "TLS enforced"
aws rds modify-db-parameter-group --db-parameter-group-name my-tls \
  --parameters "ParameterName=require_secure_transport,ParameterValue=ON,ApplyMethod=pending-reboot"
aws rds modify-db-instance --db-instance-identifier my-db --db-parameter-group-name my-tls --apply-immediately
```

## Authentication and credentials

- **`--manage-master-user-password`** instead of a plaintext `--master-user-password` — this provisions the password directly into Secrets Manager and rotates it automatically. Never accept a plaintext production password.
- **Never a default master username** (`admin`, `root`, `postgres`, `master`) — pick something application- or team-specific; well-known usernames make credential-guessing meaningfully easier.
- **IAM database authentication** is preferable to username/password for application connections where the engine supports it — short-lived tokens instead of long-lived credentials.
- Store the master password's Secrets Manager ARN, never the credential text, in your app config/deploy scripts.

## Network placement

- Deploy in a **private subnet**; `--no-publicly-accessible` for anything production.
- Security groups scoped to specific application CIDR ranges or security-group references — **never `0.0.0.0/0`**.
- EC2-Classic DB security groups are legacy (EC2-Classic itself retired in 2022) — use VPC security groups.

## Parameter groups vs option groups

Easy to conflate:

- **Parameter group** — engine-level configuration knobs, the equivalent of `my.cnf`/`postgresql.conf` settings (TLS enforcement, memory tuning, logging behavior). Applies to every engine.
- **Option group** — bolts on engine *features* that need extra plumbing (IAM roles, network access) beyond a config value — e.g. SQL Server Integration Services (SSIS) requires associating both an option group and a parameter group, plus an existing Active Directory domain and IAM role. Not every engine uses option groups the same way; MySQL/MariaDB/PostgreSQL use them far less than Oracle/SQL Server.

## Audit logging

Export database logs to CloudWatch Logs so security-relevant events (failed logins, suspicious queries) are centrally visible, and encrypt the resulting log groups with KMS since they can contain SQL literals and usernames:

```bash
--enable-cloudwatch-logs-exports '["error","slowquery","audit"]'   # MySQL/MariaDB
--enable-cloudwatch-logs-exports '["postgresql"]'                   # PostgreSQL
aws logs associate-kms-key --log-group-name /aws/rds/instance/<name>/error --kms-key-id <kms-key-arn>
```
The `audit` stream is **empty unless audit logging is separately enabled first** — MySQL via the `MARIADB_AUDIT_PLUGIN` in an option group, MariaDB via built-in server audit parameters (e.g. `server_audit_logging=1`) in a parameter group, PostgreSQL via the `pgaudit` extension.

## Full production example (MySQL 8.4)

```bash
aws rds create-db-instance \
  --db-instance-identifier my-db \
  --engine mysql --engine-version 8.4 \
  --db-instance-class db.r7g.xlarge \
  --allocated-storage 100 --storage-type gp3 \
  --storage-encrypted --kms-key-id <kms-key-arn> \
  --no-publicly-accessible --multi-az \
  --manage-master-user-password --master-username <custom-non-default-username> \
  --backup-retention-period 7 \
  --enable-performance-insights --performance-insights-retention-period 7 \
  --performance-insights-kms-key-id <kms-key-arn> \
  --deletion-protection \
  --enable-cloudwatch-logs-exports '["error","slowquery","audit"]' \
  --tags Key=created_by,Value=<your-tooling> \
  --region us-east-1
```
Then apply the TLS-enforcement parameter group and log-group KMS association shown above — RDS doesn't do either automatically.

## Minimum IAM for operating (read-only advisory work)

`AmazonRDSReadOnlyAccess` + `CloudWatchReadOnlyAccess` covers inspection/monitoring. Provisioning needs `rds:CreateDBInstance` + `rds:AddTagsToResource`, and `logs:CreateLogGroup` if CloudWatch Logs export is enabled. Never grant broad write/admin access to work around a permission error — narrow the actual gap instead.

## Pitfalls

- TLS "enforced" only client-side (connection string flag) with no server-side parameter-group enforcement — trivially bypassed.
- A default master username on a production instance.
- Plaintext `--master-user-password` instead of `--manage-master-user-password`.
- `audit` log stream configured but silently empty because audit logging itself was never turned on at the engine level.
- Security group rules scoped to `0.0.0.0/0` "temporarily," left that way.
