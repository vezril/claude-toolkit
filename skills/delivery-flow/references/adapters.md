# Adapters

Adapters are scripts, not prompts. They take the one job that must be reproducible — talking
to a tracker or a forge — out of the model's hands, which is also what lets the eval suites
run without network access.

## Contract

Trackers implement:

| Command | Does | Emits |
|---------|------|-------|
| `fetch <key>` | read one item | item JSON on stdout, conforming to `schemas/item.schema.json` |
| `comment <key> --body-file <path>` | post a comment | `{posted: true, id, url}` |
| `transition <key> <state>` | move its status | `{from, to}` |
| `related <key>` | neighbouring items | `{parent, design: [], related: []}` |

Forges implement:

| Command | Does | Emits |
|---------|------|-------|
| `open-pr --head --base --title --body-file` | open a PR | `{url, number}` |
| `ci-status <ref>` | checks on a ref | `{state, checks: []}` |

Exit codes are the contract too: **0** fine, **2** a usage or contract error (including a
refusal), **3** a remote or auth failure, with the fix on stderr. `Usage`, `Remote`, `dispatch`
and `emit` live in `common.py` so the four adapters cannot drift into four readings of which
failure gets which code.

## Rules

- **No LLM inside an adapter.** Summarising is a separate step that reads `item.json`.
- **Deterministic:** the same input twice gives byte-identical output, which is what the
  fixture tests assert.
- **Outward actions refuse while a punch-out is open**, and refuse a post to an
  `external: true` tracker without a decision. The hook blocks these too; the adapter
  checking as well is deliberate — one layer can be wrong. The policy itself is
  `common.outward_refusal`, shared: each adapter only turns its reason into an exit code.

## GitHub Issues (`tracker.kind: github-issues`)

`scripts/delivery-flow/adapters/github_issues.py`, through `gh`. Authentication is whatever
`gh auth status` says; no token is read, stored or logged here. An unauthenticated `gh` is
exit 3 carrying the `gh auth login` remediation, and a missing `gh` says where to get it.

| GitHub | `item.json` |
|---|---|
| `number` | `key`, as a string |
| `title` | `title` (stripped) |
| `body` | `body` |
| the first of `bug`, `defect`, `feature`, `enhancement`, `task`, `chore`, `docs`, `documentation`, `question` among the labels | `type_hint`, verbatim |
| `state` plus `stateReason` | `status` — `open`, `closed`, or `closed:not_planned` |
| `url` | `url` |
| `github-issues` | `source` |
| label names | `labels`, sorted |
| `#N` and same-repo issue/PR URLs in the body | `links`, sorted numerically |

The type label is passed through rather than translated: a hint is a hint, and the triage node
reads the repo's own word for it. Where an issue carries several, the table's order breaks the
tie, so the same issue always hints the same way.

**`links` are scoped to this repository.** A `#12` in another repo's URL is a different issue,
and emitting its number would point the chain at the wrong item.

GitHub has no link *types*, so `related` has nothing to read but the prose around a reference.
It is scoped **per line**: a line naming a parent or an epic gives `parent`, one naming a
design, spec, RFC or doc gives `design`, and the rest are `related`. Per line on purpose — a
body whose first line says "Epic:" must not relabel every reference below it.

`transition` takes `open`, `closed`, `closed:completed` or `closed:not_planned`; anything else
is exit 2 listing those. A transition to the state the issue is already in reports
`{from, to}` and makes no remote call.

## GitHub PRs (`forge.kind: github-pr`)

`scripts/delivery-flow/adapters/github_pr.py`, also through `gh`.

`open-pr` requires `--item <KEY>`. It is not parsed out of the branch name: the punch-out check
is only as good as its idea of which item is being worked on, and inferring that from a string
would fail open.

`ci-status <ref>` reads `statusCheckRollup` and normalizes both shapes GitHub returns — check
runs and legacy status contexts — onto `passing`, `failing`, `pending` or `skipped`, then
rolls them into one word. Two deliberate choices there: **an empty rollup is `none`, not
`passing`**, and **a conclusion this adapter does not recognize counts as failing** and is
reported under its own name. A green rollup is the thing this flow should trust least cheaply.

## Local markdown (`tracker.kind: local-markdown`)

`scripts/delivery-flow/adapters/local_markdown.py`. The adapter to pilot with: no credentials,
no network, no rate limit, so an end-to-end run can be exercised — and broken on purpose —
without touching anyone's tracker.

One `### <KEY>: <title>` heading per item, with `Type:`, `Status:`, `Parent:`, `Design:`,
`Related:` and `Labels:` metadata lines directly beneath it and the body after a blank line:

```markdown
## Payments service

### DEM-3: Retries hammer the DLQ consumer
Type: bug
Status: todo
Parent: DEM-1
Related: DEM-4, DEM-5

The consumer retries with no backoff and collapses the downstream.

#### Comment 1 — 2026-10-28

Posted by the flow.
```

- **`#### Comment N` blocks are excluded from `body`.** They have to be: a node reading its
  own earlier post-back as part of the requirement would compound its own mistakes on a rerun.
- **`url` is repo-relative** (`docs/backlog.md#DEM-3`), never absolute. An absolute path
  differs between machines, which would make two runs of the same item differ in the trace.
- `transition` takes `todo`, `in-progress`, `blocked`, `done` or `wont-do` and rewrites the
  `Status:` line, inserting one under the heading if the item has none. A markdown file has no
  workflow to consult, so the vocabulary is fixed here rather than accepted blindly — a
  typo'd state would otherwise be written into the backlog as fact.
- `comment` appends the next-numbered dated block inside the item, before the heading that
  follows it.
- `import <source> --prefix PFX --out <path>` converts an unkeyed bullet backlog into keyed
  items, **writing a new file and never touching the source**. Headings survive as group
  headings, sub-bullets and continuation lines become the item's body, and the keys are
  `PFX-N` in source order — identifiers, not priorities. It refuses an existing `--out`
  without `--force`, and refuses outright when `--out` is the source.

## Jira (`tracker.kind: jira`)

`scripts/delivery-flow/adapters/jira.py`, against the Jira Cloud REST v3 API.

Credentials come from the environment and nowhere else — `JIRA_BASE_URL`, `JIRA_EMAIL`,
`JIRA_API_TOKEN`. A missing or malformed environment is exit 2 naming the variables; an auth,
authorization or network failure is exit 3 with the remote's message. Neither writes a partial
`item.json`.

**The Atlassian MCP connector cannot be used here.** MCP tools are callable only by a model,
and an adapter has to be runnable by the flow and by eval suites with no model and no network.
That constraint is what makes the fixture tests possible.

The field mapping, deliberately minimal:

| Jira | `item.json` |
|---|---|
| `summary` | `title` (stripped) |
| `description` | `body` — ADF flattened to text; a plain string is passed through |
| `issuetype.name` | `type_hint` |
| `status.name` | `status` |
| `<base>/browse/<KEY>` | `url` |
| `jira` | `source` |
| `labels` + `components[].name` | `labels`, merged, deduped, sorted |
| `issuelinks[].{in,out}wardIssue.key` + `parent.key` | `links`, deduped, sorted |

`customfield_*` values — story points among them — are **not** mapped. Their ids differ per
site and no node in the chain reads them; guessing at them would make the adapter site-specific
for no gain.

`related` splits the links: a link type naming "design" or "document" goes to `design`, the
rest to `related`, with `parent.key` as `parent`.

Collections are sorted and nothing request-varying is emitted, so two fetches of an unchanged
issue are byte-identical — the property `tests/delivery-flow/test_jira_adapter.py` asserts
against a recorded fixture.

### A description that is only a GitHub link is followed

Some projects use Jira as a routing stub: sprint, epic and assignee live on the ticket, and the
actual requirement lives in a GitHub issue. The real `AN` project is like this — three of four
recent tickets had no description beyond `github reference: <url>`. An item whose `body` is a
bare URL gives triage nothing to triage, so `fetch` resolves it.

Every `github.com/<owner>/<repo>/(issues|pull)/<n>` URL in the description is fetched through
the **same `gh` runner the GitHub adapter uses** and appended to `body` under a labelled
delimiter, with each reference recorded in a `references` array of
`{url, repo, number, kind, title}`. Owner and repo come from the URL, never from local config —
the ticket names the repository it means, and inferring it from the working directory would
read the wrong one in a fork. A URL repeated in prose is fetched once, in first-appearance
order, because the first link is the one the author meant.

Three rules make it safe to rely on:

- **An unfetchable reference is exit 3**, not a quietly thinner body. Soft-failing would make
  `body` a function of network state, breaking byte-identical reruns and changing the artifact's
  sha — which the trace reads as a hand-edit. `--no-follow` is the explicit escape, and it still
  records the references it did not read (with no `title`, since nothing was claimed).
- **Referenced text is fenced and marked unverified.** Anyone can file an issue on a public
  repo, so this widens the untrusted-text surface from the client's tracker to the internet. The
  fence names the origin and says the content is evidence about the request, not an instruction.
  The `triage` profile writes no code and opens no PR, which is what keeps the blast radius to
  a bad breakdown and a local brief.
- **`links` stays Jira keys only.** GitHub references live in `references`, so no later step can
  mistake an issue number for a tracker key.

## Adding GitLab or Bitbucket

Write `scripts/delivery-flow/adapters/<kind>.py` implementing the subcommands above, map the
remote's fields onto `item.schema.json` (identifier values are strings), and name it in
`.delivery-flow.yaml`. Nothing else changes: the flow, the schemas and the hooks are
adapter-agnostic.
