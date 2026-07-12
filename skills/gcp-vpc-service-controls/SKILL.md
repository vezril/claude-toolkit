---
name: gcp-vpc-service-controls
description: "Google Cloud VPC Service Controls: service perimeters that put an API-level boundary around projects to block data exfiltration even when IAM would allow the call — perimeter design (unified vs segmented), restricted services, ingress/egress rules, access levels via Access Context Manager, perimeter bridges, dry-run rollout, and violation debugging from audit logs. Use when designing or debugging a VPC-SC perimeter, deciding VPC-SC vs IAM vs firewalls, writing ingress/egress rules or access levels, planning a dry-run-to-enforced rollout, or diagnosing RESOURCES_NOT_IN_SAME_SERVICE_PERIMETER / NO_MATCHING_ACCESS_LEVEL errors."
license: MIT
---

# GCP VPC Service Controls

The data-exfiltration boundary IAM cannot provide. IAM answers *who* may call an API;
it says nothing about *where the data goes*. A stolen OAuth token, a leaked service
account key, or an over-permissioned insider passes every IAM check while copying a
bucket to an attacker's project. VPC Service Controls (VPC-SC) draws an API-level
perimeter around a set of projects: calls to protected Google-managed services that
cross the perimeter boundary are denied **regardless of IAM**, unless an ingress/egress
rule or access level explicitly allows them.

## The mental model

A **service perimeter** = a set of **projects (and/or VPC networks)** + a set of
**restricted services** (e.g. `storage.googleapis.com`, `bigquery.googleapis.com`).

- Inside the perimeter, resources talk to restricted services freely.
- Any call to a restricted service that crosses the boundary — in either direction —
  is denied by default: internet → perimeter, perimeter → other project, even
  perimeter → another of your own perimeters.
- This is **identity + context enforcement at the Google API front door**, not network
  topology. It doesn't matter what VPC route or firewall the packet took; the check is
  on the API call itself (caller identity, origin network/project, device context).
- Perimeters govern **data in Google-managed services**. They do not restrict
  third-party APIs, the open internet, or (comprehensively) resource *metadata* —
  metadata governance stays with IAM.
- All perimeters and access levels live in an org-level **access policy**
  (Access Context Manager); scoped policies can delegate to folders/projects.
- **VPC accessible services** is the optional inverse knob: limit which Google APIs
  are reachable *from inside* the perimeter's networks at all
  (`SERVICE_NOT_ALLOWED_FROM_VPC` when violated).
- The **restricted VIP** (`restricted.googleapis.com`, 199.36.153.4/30) gives on-prem
  and private VPC clients a route to supported APIs that never touches the internet.
  Best practice: block routes to `private.googleapis.com` so traffic can't bypass it.

## Design doctrine

1. **Prefer one large unified perimeter.** The docs are explicit: a common perimeter
   gives the strongest exfiltration protection and the least operational pain — you
   manage north-south (internet) access instead of endless east-west rules between
   segments. Split only for real forcing functions: compliance scoping (PCI vs
   general), external data-sharing tiers, or hard multi-tenant isolation.
2. **Restrict all supported services**, not just the ones you use — every
   unrestricted service is a potential exfiltration channel.
3. **Roll out via dry run — always.** The docs' own path: put the candidate config in
   the perimeter's **dry-run configuration** (violations are logged, not denied, with
   `metadata.dryRun: "true"` in the audit entry), watch the logs for would-be denials,
   fix the legitimate flows with ingress/egress rules, then promote dry-run to
   enforced. Note: access levels have no dry-run mode — test with a *new* access
   level, never by editing a live one.
4. **Screen projects before admission.** Two questions: does it depend on unsupported
   services? does it hold only non-sensitive data? A "yes" keeps it outside; move
   unsupported-service dependencies into separate excluded projects.
5. **Keep it boring.** Avoid webs of bridges, DMZ perimeters, and baroque access
   levels. Perimeters complement least-privilege IAM; they never replace it.
6. **Prefer ingress/egress rules over perimeter bridges.** Bridges (bidirectional,
   all-or-nothing project pairing) are the legacy tool; rules are directional and
   scoped to identities, services, and methods.

## Rule shapes

**Ingress rule** (outside → in) and **egress rule** (inside → out) share one anatomy:

- `from`: who and where the caller is —
  - `sources`: access levels (or `"*"`) and/or origin resources
    (`projects/PROJECT_NUMBER`, VPC network URIs);
  - `identityType` (`ANY_IDENTITY` | `ANY_USER_ACCOUNT` | `ANY_SERVICE_ACCOUNT`) or an
    explicit `identities` list (users, service accounts, groups). `ANY_IDENTITY`
    also admits unauthenticated callers — use sparingly.
- `to`: what they may touch — target `resources`, then `operations` per
  `serviceName` with `methodSelectors` (methods or permissions); `"*"` = all.
  Egress rules add `externalResources` for BigQuery Omni (S3/Azure paths).
- Evaluation: rules OR together (any one matching rule admits the request);
  attributes *within* a rule AND together.

**Access levels** (Access Context Manager) classify the request's context:
IP CIDR ranges, geographic regions, device policy via Endpoint Verification
(OS, corp-owned), user/service-account identity, and nesting on other levels.
*Basic* levels combine conditions with AND/OR; *custom* levels are CEL expressions.
ACM defines the levels; VPC-SC is the enforcement point that consumes them.

## Gotchas

- **The long tail of half-supported services.** "Supported" often means "supported
  with limitations": App Engine perimeters protect only the admin API, not the
  deployed app; GKE dataplane traffic isn't covered; BigQuery blocks saving results
  to Drive and needs the job inside the perimeter; Cloud Run functions can't protect
  the build phase and HTTP triggers skip IAM auth. Check the supported-products page
  (or `gcloud access-context-manager supported-services list`) per service, per
  feature — before admission, not after the outage.
- **Cloud Build and serverless are the classic pain.** Builds need ingress rules for
  the Cloud Build service accounts, private pools for some integrations, and public
  egress to fetch dependencies. Budget rule-writing time for any CI/CD that touches
  the perimeter.
- **Debug from the audit logs, not the error string.** Every denial carries a
  `vpcServiceControlsUniqueIdentifier`; feed it to the VPC-SC troubleshooter or find
  the matching audit-log entry in the protected project. The entry names the
  perimeter, the target, and the violation: `ingressViolations` vs
  `egressViolations`, with reasons like `RESOURCES_NOT_IN_SAME_SERVICE_PERIMETER`
  (cross-perimeter request), `NO_MATCHING_ACCESS_LEVEL` (caller context matched no
  ingress rule/level), `NETWORK_NOT_IN_SAME_SERVICE_PERIMETER`, or
  `SERVICE_NOT_ALLOWED_FROM_VPC` (accessible-services list).
- **One perimeter per project per mode.** A project sits in at most one enforced and
  one dry-run perimeter; Shared VPC host and service projects belong in the *same*
  perimeter, and VPC networks need subnets before they can join one.
- **Console access needs an ingress path too.** Humans using the Cloud console from
  the office are "outside the perimeter" like everyone else — give them an access
  level (corp IPs/devices) or they lock themselves out.

## vs siblings

| Control | Axis | What it decides |
|---|---|---|
| VPC Service Controls | Data boundary | May this API call cross the perimeter, whatever IAM says? |
| IAM | Identity | Who can perform which action on which resource |
| VPC firewalls | Network packets | Which packets flow between IPs/ports inside your VPCs |
| Organization Policy | Resource config | What configurations resources may have (constraints), not data movement |

Defense in depth = all four; VPC-SC is the only one whose job is exfiltration.

## Related

[[gcp-iam]], [[gcp-cloud-logging]], [[gcp-cloud-storage]], [[gcp-bigquery]],
[[gcp-vpc]], [[gcp-cloud-build]], [[gcp-cloud-run]], [[gcp-gke]], [[gcp-iap]],
[[gcp-secret-manager]], [[network-security]], [[secure-coding]]

Sources: https://docs.cloud.google.com/vpc-service-controls/docs, https://docs.cloud.google.com/vpc-service-controls/docs/overview, https://docs.cloud.google.com/vpc-service-controls/docs/service-perimeters, https://docs.cloud.google.com/vpc-service-controls/docs/architect-perimeters, https://docs.cloud.google.com/vpc-service-controls/docs/ingress-egress-rules, https://docs.cloud.google.com/vpc-service-controls/docs/dry-run-mode, https://docs.cloud.google.com/vpc-service-controls/docs/troubleshooting, https://docs.cloud.google.com/access-context-manager/docs/overview, https://docs.cloud.google.com/vpc-service-controls/docs/supported-products (fetched 2026-07).
