---
name: gcp-workflows
description: "Google Cloud Workflows — serverless orchestration of GCP services and HTTP APIs via declarative YAML/JSON: steps, assign, call, switch, try/retry/except, parallel branches, subworkflows; connectors (googleapis.*) with built-in auth/retry/LRO polling; callbacks for human-in-the-loop waits up to a year. Use when designing or debugging a workflow definition, choosing retry/parallel/callback patterns, hitting execution or memory limits, estimating per-step pricing, or deciding Workflows vs Application Integration vs Cloud Tasks vs Eventarc vs plain Cloud Run code."
license: MIT
---

# Google Cloud Workflows

Serverless orchestrator: you declare an ordered series of steps in YAML (or JSON), Google runs them durably — combining Google Cloud services, Cloud Run/Functions, and any HTTP API — with zero infrastructure and scale-to-zero.

## The mental model

- A workflow is **declarative steps**, not code: each step is an `assign` (set variables), a `call` (HTTP or stdlib/connector function with `args` and a `result` variable), or control flow (`switch` conditions, `next` jumps, `for` loops, `try/retry/except`, `parallel`, `return`, `raise`).
- **State is durable between steps.** Variables persist across steps and survive infrastructure churn; an execution can run up to a year. You pay per step executed, not per second waited — waiting is nearly free, which is the whole economic point vs holding a Cloud Run instance open.
- **Connectors** (`googleapis.<service>.<version>.<resource>.<method>`, e.g. `googleapis.bigquery.v2.jobs.insert`) are authenticated wrappers over Google Cloud APIs: they sign requests with the workflow's service account, apply built-in retry policies (idempotent for GET, non-idempotent otherwise), and transparently poll long-running operations to completion (exponential backoff 1s→60s; each poll is a billable step). Tune via `connector_params` (`timeout` — default 30 min, up to 1 year; `polling_policy`; `skip_polling`).
- **Callbacks** = human-in-the-loop / external-event waits: `events.create_callback_endpoint` mints a unique HTTPS URL, `events.await_callback` blocks (default timeout 43,200 s = 12 h) until something with the `workflows.callbacks.send` IAM permission hits it. Approval flows, "wait for the human to review the order", webhook rendezvous.
- Expressions live in `${...}` — a small purpose-built language (arithmetic, comparisons, stdlib functions like `sys.get_env`, `base64.encode`, `text.encode`, `map.get`, `json.decode`), not a general-purpose one. Reuse logic via subworkflows, not functions.

## Verified YAML shapes

Call with a custom retry policy and error handling:

```yaml
- read_item:
    try:
      call: http.get
      args:
        url: https://example.com/someapi
      result: api_response
    retry:
      predicate: ${http.default_retry_predicate}   # or just: retry: ${http.default_retry}
      max_retries: 5
      backoff:
        initial_delay: 2
        max_delay: 60
        multiplier: 2
```

(Add an `except: {as: e, steps: [...]}` block after `retry` to catch what retries can't fix; `e.code`/`e.message` carry the error.)

Parallel branches writing to shared variables (unshared writes are branch-local):

```yaml
- enrichUserData:
    parallel:
      shared: [userProfile, recentItems]
      branches:
        - getUserProfileBranch:
            steps:
              - getUserProfile:
                  call: http.get
                  args:
                    url: '${"https://example.com/users/" + input.userId}'
                  result: userProfile
        - getRecentItemsBranch:
            steps:
              - getRecentItems:
                  call: http.get
                  args:
                    url: '${"https://example.com/items?userId=" + input.userId}'
                  result: recentItems
```

A parallel `for` swaps `branches:` for `for: {value: item, in: ${list}, steps: [...]}`; optional `concurrency_limit` and `exception_policy: continueAll`.

Connector call + subworkflow:

```yaml
main:
  params: [input]
  steps:
    - publish:
        call: googleapis.pubsub.v1.projects.topics.publish
        args:
          topic: ${"projects/" + sys.get_env("GOOGLE_CLOUD_PROJECT_ID") + "/topics/mytopic"}
          body:
            messages:
              - data: ${base64.encode(text.encode("Hello world!"))}
        result: publish_result
    - greet:
        call: greeting          # subworkflow call
        args:
          first: "Ada"
        result: msg

greeting:
  params: [first, last: "Lovelace"]   # defaults allowed
  steps:
    - done:
        return: ${"Hello " + first + " " + last}
```

## Gotchas and limits

- **512 KB total memory for all variables** per execution — the killer limit. A 2 MB HTTP response (the max) won't even fit; project fields server-side, pass GCS/BigQuery references between steps, not payloads.
- Workflow source max **128 KB**; expressions max **400 characters** each; strings max 256 KB; steps capped at 100,000.
- Execution duration max **1 year**; execution history/results retained **90 days**. Callback wait defaults to 12 h — raise `timeout` explicitly for longer approvals.
- Parallelism is bounded: ~20 concurrent branches/iterations actually run at once; branches must declare `shared:` variables or their writes vanish.
- The expression language has no user-defined functions, no regex-heavy stdlib, and dynamic typing — push real logic into a Cloud Run/Function step and keep the workflow as glue.
- No built-in cron: trigger via Cloud Scheduler, Eventarc, API call, or another workflow.
- **Pricing shape:** billed per executed step in two classes — *internal* (GCP calls via `*.googleapis.com`, assigns, conditions, connector polls; first 5,000/mo free, then $0.01/1,000) and *external* (non-Google HTTP + `events.await_callback`; first 2,000/mo free, then $0.025/1,000). Retries and failed steps bill; connector LRO polling bills per poll. Rounded up in 1,000-step increments — chatty polling loops are the surprise line item.

## vs siblings

- **Application Integration** — iPaaS with a visual designer, data mapping, and third-party SaaS connectors (Salesforce, SAP...). Heavier, pricier, aimed at enterprise integration flows; Workflows is the lean code-first orchestrator for your own services and Google APIs.
- **Cloud Tasks** — a queue of independent, fire-and-forget HTTP tasks with rate/retry control; no inter-task state, ordering logic, or branching. Use Workflows when step N+1 depends on step N's result.
- **Eventarc** — event *routing* (this event → that destination), not sequencing. Common combo: Eventarc triggers a workflow.
- **Cloud Scheduler** — just cron; it starts workflows, it doesn't orchestrate.
- **Writing it in Cloud Run** — imperative code is more expressive, but you pay for wall-clock while waiting, must persist state and implement retry/polling yourself, and can't sleep for months. Workflows gives durability and cheap waits; call Cloud Run for the hard logic.

## Related

[[gcp-cloud-run]] · [[gcp-cloud-functions]] · [[gcp-cloud-tasks]] · [[gcp-cloud-scheduler]] · [[gcp-eventarc]] · [[gcp-application-integration]] · [[gcp-pubsub]] · [[gcp-secret-manager]] · [[gcp-iam]]

Sources: https://docs.cloud.google.com/workflows/docs, https://docs.cloud.google.com/workflows/docs/reference/syntax, https://docs.cloud.google.com/workflows/docs/execute-parallel-steps, https://docs.cloud.google.com/workflows/docs/connectors, https://docs.cloud.google.com/workflows/docs/creating-callback-endpoints, https://docs.cloud.google.com/workflows/quotas, https://cloud.google.com/workflows/pricing, https://github.com/GoogleCloudPlatform/workflows-samples (fetched 2026-07).
