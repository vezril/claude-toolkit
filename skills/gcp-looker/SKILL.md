---
name: gcp-looker
description: "Google Cloud Looker — the LookML-based BI platform: a version-controlled semantic layer (model → explore → view, dimensions/measures) that generates SQL against your warehouse instead of extracting data; explores, Looks, dashboards; PDTs/derived tables; Git-backed dev mode → production flow; signed embedding and API; Looker (Google Cloud core) editions vs Looker (original) vs Looker Studio disambiguation. Use when modeling data in LookML, designing explores or PDTs, wiring Looker's Git workflow, embedding dashboards, choosing between Looker and Looker Studio, or sizing editions/licensing."
license: MIT
---

# Looker (Google Cloud)

Looker is Google Cloud's platform for business intelligence, data applications, and
embedded analytics. Its core bet: a **governed semantic layer** written in LookML,
version-controlled in Git, that turns business questions into SQL run directly against
your warehouse — no extracts, no per-dashboard metric definitions.

**Family disambiguation — say it plainly:**

- **Looker (Google Cloud core)** — the Google-managed offering, provisioned and
  administered from the Google Cloud console (gcloud, Terraform, Looker Admin API).
  Google Cloud infrastructure only. Three editions: **Standard** (≤50 internal users),
  **Enterprise** (unlimited users, VPC Service Controls, Private Service Connect, CMEK),
  **Embed** (Enterprise + signed embedding and custom themes at scale).
- **Looker (original)** — the pre-acquisition product line, including customer-hosted
  deployments. Core lacks a few original features (LDAP, username/password login, user
  impersonation) but adds console-native management and Knowledge Catalog integration.
- **Looker Studio** — a **different product**. Formerly Data Studio: free-tier,
  self-service report builder with direct data connections and no LookML. It can
  *consume* Looker's semantic layer via the Looker connector (each Looker Studio data
  source maps to a single Looker Explore), but it is not "Looker lite" — governance,
  modeling, and APIs are Looker's, not Studio's.

## The mental model

- **LookML is a dependency language, not a query language** ("like make"). You declare
  SQL expressions once; Looker reuses them everywhere. DRY for analytics.
- **Hierarchy: project → model → explore → view.** A *project* is a Git repo of LookML
  files. A *model* declares which explores exist and how views join. An *explore* is the
  query entry point users see. A *view* maps a table (or derived table) to *dimensions*
  (attributes) and *measures* (aggregates).
- **Queries run in the warehouse.** Looker generates dialect-specific SQL and sends it to
  the connected database (BigQuery, Snowflake, Postgres, ...). There is no proprietary
  data store or extract — freshness and cost are the warehouse's.
- **PDTs materialize.** Persistent derived tables are written to a scratch schema *in
  your database* and rebuilt on triggers. They are Looker-orchestrated warehouse tables,
  and they cost warehouse compute/storage like any other table.
- **Consumption objects:** an *Explore* answers ad-hoc questions; a *Look* is a saved
  query/visualization; a *dashboard* composes tiles (user-defined via UI, or LookML
  dashboards as code).

## LookML shapes

A view with a dimension and a measure (from the docs):

```lookml
view: orders {
  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
  }
  measure: count {
    type: count
  }
}
```

An explore with a join, in a model file:

```lookml
explore: orders {
  join: customer {
    sql_on: ${orders.customer_id} = ${customer.id} ;;
    relationship: many_to_one
    type: left_outer    # both relationship and type default to these values
  }
}
```

Derived tables — two flavors, either can persist:

```lookml
view: customer_order_summary {
  derived_table: {
    sql:
      SELECT customer_id,
        MIN(DATE(time)) AS first_order,
        SUM(amount) AS total_amount
      FROM orders
      GROUP BY customer_id ;;
    datagroup_trigger: nightly_etl   # or sql_trigger_value / interval_trigger / persist_for
  }
}
```

Native derived tables use `explore_source:` (LookML-defined columns) instead of raw SQL —
prefer them for maintainability. Always alias SQL columns (`AS`); you reference them as
`${TABLE}.column_name`. Cascade PDTs with `${other_pdt.SQL_TABLE_NAME}`. For dialects that
support it, `materialized_view: yes` delegates persistence to the database.

## Development flow

- Opening a project shows **Production Mode**; "Create Developer Copy" gives you a
  personal Git branch (`dev-<name>`, read-only to others) in **Development Mode**.
- Cycle: edit LookML → validate → commit to your dev branch → pull from production →
  merge to the production branch (default `master`) → **deploy**. The latest commit on
  the production branch is what production users run against.
- Teams wanting review use pull-request-required mode through their Git provider; custom
  production branch names and advanced deploy mode (pin an exact commit) exist.
- Dev mode is PDT-safe: modifying a derived table definition builds a *development
  version* of the table, leaving the production PDT untouched.

## Gotchas

- **PDTs bill your warehouse.** Every rebuild is a warehouse query; trigger-cascades can
  rebuild chains of tables. Docs' own advice: avoid PDTs until you need them. `persist_for`
  PDTs inside trigger-based cascades rebuild on the *dependents'* schedule; incremental
  PDTs don't support `persist_for`. Looker-hosted PDT builds time out at one hour.
- **Edition ceilings are real:** Standard caps at 50 internal users and ~1K query API +
  1K admin API calls/month (Enterprise: 100K/10K; Embed: 500K/100K). Auth-related API
  calls (login/logout) are not metered. Private networking (PSC, private services
  access), VPC-SC, and CMEK are Enterprise/Embed only.
- **Embedding auth:** *private embedding* iframes content for users who already have
  Looker sessions; **signed embedding** (SSO embed) builds a
  `https://HOST/login/embed/...&signature=...` URL — HMAC-signed with an admin-generated
  embed secret — carrying `external_user_id`, `nonce`, `time`, `session_length`,
  `permissions`, and `models`. Guard the embed secret like a credential; the Embed SDK
  (`sdk=2`) layers JS conveniences on top.
- **Pricing shape** (no public unit prices — sales-quoted): annual platform subscription
  per edition (Standard/Enterprise/Embed, 1–3 year terms, one production instance) plus
  per-user licenses in three roles — **Developer** (full, incl. API and dev mode),
  **Standard User** (explore + SQL Runner, no API/admin), **Viewer** (consume only).
  Every edition bundles 10 Standard + 2 Developer users. Conversational analytics is
  metered separately in data tokens with per-edition monthly allocations.

## Vs siblings

- **Looker vs Looker Studio:** Looker = governed, modeled, embedded/API-driven BI for
  organizations; Studio = fast self-service reports for individuals/teams. If metric
  definitions must be consistent and access-controlled, model in Looker — optionally let
  Studio users report off Looker Explores via the connector (viewers need `access_data`
  on the model).
- **Looker vs querying BigQuery directly:** BigQuery (with BI Engine-era acceleration and
  console-native tools) answers SQL; Looker adds the reusable metric layer, row-level
  governance, scheduling, and embedding on top. Teams fluent in SQL with few shared
  metrics may not need Looker; teams shipping metrics to many consumers do.
- **Embedded analytics:** the Embed edition + signed embedding is the intended path for
  customer-facing dashboards inside your own app, rather than hand-rolled iframes to
  Studio reports.

## Related

[[gcp-bigquery]] · [[gcp-lakehouse]] · [[gcp-dataflow]] · [[gcp-cloud-sql]] ·
[[gcp-alloydb]] · [[gcp-spanner]] · [[gcp-iam]] · [[gcp-vpc-service-controls]] ·
[[gcp-secret-manager]] · [[gcp-iap]] · [[gcp-cloud-monitoring]] · [[gcp-cloud-logging]]

Sources: https://docs.cloud.google.com/looker/docs, https://docs.cloud.google.com/looker/docs/intro, https://docs.cloud.google.com/looker/docs/what-is-lookml, https://docs.cloud.google.com/looker/docs/derived-tables, https://docs.cloud.google.com/looker/docs/version-control-and-deploying-changes, https://docs.cloud.google.com/looker/docs/looker-core-overview, https://docs.cloud.google.com/looker/docs/single-sign-on-embedding, https://docs.cloud.google.com/looker/docs/reference/param-explore-join, https://docs.cloud.google.com/looker/docs/studio/connect-to-looker, https://cloud.google.com/looker/pricing (fetched 2026-07).
