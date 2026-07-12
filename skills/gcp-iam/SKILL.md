---
name: gcp-iam
description: "Google Cloud IAM — who (principal) can do what (role) on which resource (allow policy binding). Covers the principals/roles/policies model, org→folder→project→resource hierarchy with additive downward inheritance, role types (basic = production anti-pattern, predefined, custom), the service-account doctrine (attached SA + ADC > impersonation > exported keys last resort), Workload Identity Federation for keyless external workloads (GitHub Actions OIDC), short-lived credentials, IAM Conditions (CEL), deny policies and principal access boundary policies, and least-privilege tooling (role recommender, Policy Analyzer, Policy Troubleshooter). Use when granting/revoking/debugging access on Google Cloud, designing service accounts or CI/CD auth, writing gcloud add-iam-policy-binding commands, replacing service account keys, setting org-wide guardrails, or auditing for least privilege."
license: MIT
---

# GCP IAM (Identity and Access Management)

Google Cloud's access-control keystone: every API call on every GCP service is checked
against IAM. Get this right and every other gcp-* skill inherits the benefit; get it
wrong and no amount of network perimeter fixes it.

## The mental model

**Allow policies bind principals to roles ON resources.** One sentence, three nouns:

- **Principal** — an authenticated identity. Human: Google Account (`user:`), Google
  group (`group:`), Workspace/Cloud Identity domain (`domain:`), workforce identity
  pool. Workload: service account (`serviceAccount:`), workload identity pool
  (`principal://` / `principalSet://`).
- **Role** — a named bundle of permissions. Permissions are `service.resource.verb`
  (e.g. `compute.instances.list`) and map ~1:1 to REST methods. You can never grant a
  permission directly — only a role that contains it.
- **Allow policy** — attached to a resource; a list of role bindings
  `{role, members[], condition?}`. Access check: does any binding on the resource *or
  any ancestor* give this principal the required permission?

**Inheritance flows DOWN the hierarchy and is additive.** Organization → folders →
project → service resources. A role granted at the org level applies to every project
and resource beneath it. There is *no subtraction* in allow policies — you cannot
grant broadly at the folder and "revoke" on one project below it. Narrowing requires
granting lower in the tree, IAM Conditions, deny policies, or PABs.

**Role types — and the basic-role anti-pattern.** Three kinds:

- **Basic roles** (`roles/owner`, `roles/editor`, `roles/viewer`) predate IAM and
  carry thousands of permissions across all services. Docs verbatim: in production,
  do not grant basic roles unless there is no alternative. They also can't take
  IAM Conditions.
- **Predefined roles** — Google-curated, per-service, maintained as APIs evolve.
  The default choice.
- **Custom roles** — your own permission list when no predefined role fits. Max 300
  per org and 300 per project; org-level custom roles only for folder/org-scoped
  permissions. You maintain them as services add permissions.

The canonical grant (read-modify-write and etag are handled for you by this command):

```sh
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="group:data-eng@example.com" \
  --role="roles/bigquery.dataViewer" \
  --condition='expression=request.time < timestamp("2026-12-31T00:00:00Z"),title=temp-access'
# --condition=None when unconditional; remove-iam-policy-binding to revoke.
```

Prefer `group:` members over individual `user:` grants — groups count as one
principal against policy limits and centralize membership churn.

## Service accounts: the doctrine

A service account (SA) is **both an identity and a resource**: it authenticates as a
principal, *and* it has its own allow policy controlling who may use it. The two
pivotal roles on the SA-as-resource:

- `roles/iam.serviceAccountUser` — attach/deploy as this SA. Granting it hands over
  every permission the SA has: privilege-escalation vector number one.
- `roles/iam.serviceAccountTokenCreator` — mint tokens for (impersonate) this SA.

Three SA flavors: **user-managed** (yours; use these), **default** (auto-created,
historically Editor-privileged — avoid; docs say create purpose-built SAs instead),
**service agents** (Google-managed, run services on your behalf).

**Authentication preference order (docs' own ranking):**

1. **Attached service account + ADC** — workload runs on GCP (GCE, Cloud Run, GKE,
   Functions): attach the SA to the resource; Application Default Credentials get
   short-lived tokens from the metadata server. No secret ever exists.
2. **Workload Identity Federation** — workload runs outside GCP (see below). Keyless.
3. **Impersonation** — a human or SA with `serviceAccountTokenCreator` mints
   short-lived credentials: `gcloud --impersonate-service-account=SA_EMAIL ...` or
   `gcloud auth print-access-token --impersonate-service-account=SA_EMAIL`. Tokens
   default to 1 h; up to 12 h only via org policy
   `constraints/iam.allowServiceAccountCredentialLifetimeExtension`.
4. **Exported keys — LAST RESORT.** Docs verbatim: keys "are a security risk if not
   managed correctly"; avoid them whenever possible. If truly unavoidable: rotate on
   a schedule, one purpose per key, and block the rest of the org with the
   `iam.disableServiceAccountKeyCreation` org policy constraint.

One SA per application, not shared. Disable before deleting (deletion within ~30 days
is recoverable but bindings referencing a deleted SA break). Watch Recommender's
lateral-movement insights for cross-project impersonation chains.

## Workload Identity Federation (keyless external)

WIF exchanges an external IdP's token for GCP credentials via the Security Token
Service (OAuth 2.0 token exchange) — no key file. Supports AWS, Microsoft Entra ID,
GitHub, GitLab, Kubernetes, Okta, AD FS, Terraform, and any OIDC or SAML 2.0 IdP.

- **Pool** — container of external identities; one pool per external environment.
- **Provider** — describes the IdP: issuer, **attribute mapping** (CEL, e.g.
  `google.subject=assertion.sub`, plus up to 50 custom attributes) and an
  **attribute condition** that rejects tokens outside your scope.
- **Two access modes**: grant roles directly to `principalSet://iam.googleapis.com/
  projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.
  ATTR/VALUE` (preferred, no SA at all), or federate into SA impersonation via
  `roles/iam.workloadIdentityUser`.

GitHub Actions: the workflow requests a GitHub OIDC token; `google-github-actions/auth`
exchanges it and wires `GOOGLE_APPLICATION_CREDENTIALS`. Restrict with an attribute
condition like `assertion.repository_owner_id == '123456' && assertion.ref ==
'refs/heads/main'` — the docs warn to map *numeric* IDs (`repository_id`,
`repository_owner_id`), since name-based claims are typosquattable.

## IAM Conditions

Optional CEL expression on a binding: the role applies only while it evaluates true.
Attributes: resource type/name/service/tags, `request.time`, plus IAP-only
request attributes (destination IP/port, URL host/path, access levels). Example:
`resource.name.startsWith("projects/p/buckets/b/objects/staging-")`. Limits: no basic
roles, no `allUsers`/`allAuthenticatedUsers`, Cloud Storage needs uniform bucket-level
access, ≤12 logical operators per expression, ≤20 same-role-same-principal
conditional bindings.

## Deny policies and principal access boundaries

Allow policies can only add — these two subtract:

- **Deny policies** — attached to org/folder/project, inherited downward, and
  **evaluated before any allow policy**: a denied permission loses even against
  Owner. Permissions in v2 format (`service.googleapis.com/resource.verb`; not all
  are deny-able), optional `exceptionPrincipals`/`exceptionPermissions`, conditions
  limited to resource-tag functions. Up to 500 deny policies per resource. Use for
  org-wide guardrails ("nobody deletes audit log sinks").
- **Principal access boundary (PAB) policies** — GA. Attach to *principal sets* (a
  workforce/workload pool, a Workspace domain, all principals in a project/folder/
  org) and define which resources those principals are *eligible* to access at all;
  grants outside the boundary simply stop working. Pin the enforcement version
  (currently 4) explicitly. Limits: ≤1,000 PAB policies, ≤500 resources per policy.

## Least-privilege tooling (Policy Intelligence)

- **Role recommender** — ML over ~90 days of permission usage suggests replacing
  over-broad roles (its favorite target: basic roles). Never auto-applied; review,
  apply, and it's audit-logged. Ignores non-IAM controls (ACLs, K8s RBAC).
- **Policy Analyzer** — "who has access to what": query bindings across the org.
- **Policy Troubleshooter** — "why can/can't this principal do X on Y": evaluates
  allow + deny + PAB together. `gcloud policy-intelligence troubleshoot-policy iam
  RESOURCE --principal-email=... --permission=...` (needs
  `roles/iam.securityReviewer` + `roles/iam.denyReviewer`).

## Gotchas

- **1,500 principals per allow policy** (every appearance counts; a group counts
  once regardless of size — another reason to bind groups), ≤250 domains/groups.
- **Eventual consistency** — policy changes typically propagate within 2 minutes but
  can take 7+; never test a grant with an immediate retry loop.
- **Basic-role sprawl** — `roles/editor` on the default compute SA is the classic
  legacy hole; recommender + org policy to disable default-SA grants clean it up.
- **SA keys linger** — 10 keys max per SA and no built-in expiry by default; an
  unrotated key is a permanent credential. Prefer disabling key creation org-wide.
- **`serviceAccountUser` at project level** grants use of *every* SA in the project
  — grant it on the specific SA resource instead.

## Related

[[gcp-vpc-service-controls]] (perimeters complement IAM — data exfiltration is not an
IAM problem), [[gcp-iap]] (context-aware access on top of IAM), [[gcp-secret-manager]]
(where secrets go instead of key files), [[gcp-cloud-logging]] (audit logs record
every IAM decision), [[gcp-cloud-sdk]] (gcloud auth + ADC mechanics),
[[secure-coding]], [[devops]].

Sources: https://docs.cloud.google.com/iam/docs/overview, /iam/docs/roles-overview,
/iam/docs/service-account-overview, /iam/docs/best-practices-service-accounts,
/iam/docs/workload-identity-federation,
/iam/docs/workload-identity-federation-with-deployment-pipelines,
/iam/docs/create-short-lived-credentials-direct, /iam/docs/conditions-overview,
/iam/docs/deny-overview, /iam/docs/principal-access-boundary-policies,
/iam/docs/recommender-overview, /iam/docs/troubleshooting-access,
/iam/docs/granting-changing-revoking-access, /iam/quotas (fetched 2026-07).
