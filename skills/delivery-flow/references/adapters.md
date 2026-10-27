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
refusal), **3** a remote or auth failure, with the fix on stderr.

## Rules

- **No LLM inside an adapter.** Summarising is a separate step that reads `item.json`.
- **Deterministic:** the same input twice gives byte-identical output, which is what the
  fixture tests assert.
- **Outward actions refuse while a punch-out is open**, and refuse a post to an
  `external: true` tracker without a decision. The hook blocks these too; the adapter
  checking as well is deliberate — one layer can be wrong.

## Adding Jira, GitLab or Bitbucket

Write `scripts/delivery-flow/adapters/<kind>.py` implementing the subcommands above, map the
remote's fields onto `item.schema.json` (identifier values are strings), and name it in
`.delivery-flow.yaml`. Nothing else changes: the flow, the schemas and the hooks are
adapter-agnostic. A Jira adapter may wrap REST or the Atlassian connector behind the same
CLI — the flow never sees the difference.
