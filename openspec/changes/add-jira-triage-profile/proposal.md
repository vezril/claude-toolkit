## Why

`add-delivery-flow` built a 15-step pipeline and named the chain it would certify first:
**triage → breakdown → challenge-breakdown**, three nodes with structured contracts between
them. Those three nodes are certified — registered in `skills/delivery-flow/steps.yaml`, sonnet
tier, ≥95% of asserts over 3 consecutive runs each, with load-bearing maps, iteration logs and
haiku escalation evidence. The guardrails, sentinels, trace, punch-out enforcement and the
15-attack bypass suite are built around them.

What is missing is the ability to *run only that chain and stop*. The routing table in
`scripts/delivery-flow/flow-status.py:42` is a single hard-coded list of 15 steps, so an item
always routes toward solutioning, implementation, a PR and a post-back. Three of those steps —
`challenge-implementation`, `project-memory`, `vault-update` — appear in the table but not in
the registry, and `check-certification.py` returns 1 for an unregistered step
(`check-certification.py:280`). With the documented default `allow_uncertified: []`, an item
blocks before it reaches a PR. The consequence is the one that matters: **there is no way to
produce the three real end-to-end runs the Stage 4 submission is built on**, because the
pipeline cannot reach a terminal state through certified steps alone.

The second reason is scope. Stage 4's own scale is "a chain of roughly 2–3 nodes, each clearing
its Stage 3 bar over 3 consecutive runs" — explicitly not an entire department of agents. The
full delivery flow is the right thing to *build*; a 3-node slice is the right thing to
*certify*. Slicing also deletes most of the risk rather than deferring it: with nothing
implemented and no PR opened, there is no branch-creation step, no CI boundary, no OpenSpec
`apply`/`archive` lifecycle to keep in sync, and untrusted tracker text never reaches a step
that writes code.

The third reason is the input source. The first real workload's tickets live in Jira, and
`add-delivery-flow` shipped GitHub Issues and a local markdown backlog only, deferring Jira by
name. A tracker adapter is a deterministic script with no LLM in it, so changing the input
source costs nothing in certification — it is the cheapest possible way to point the certified
chain at real work.

## What Changes

- **Profiles: a named slice of the routing table.** A `profile:` key in `.delivery-flow.yaml`
  selects an ordered subset of steps, and `flow-status.py` routes within that subset only. Two
  profiles ship: `triage` (this change's chain) and `full` (today's behaviour, the default, so
  existing repos are unaffected). A profile declares its terminus; reaching it writes
  `outcome.json` with `completed` rather than falling through to the next step.
- **Profile handoff is the artifact directory, not an orchestrator.** When the `triage` profile
  completes, `flow-status.py` reports the next profile by name and stops. A later profile
  resumes the same `delivery/<ITEM-KEY>/` by reading the artifacts already there. No supervising
  LLM step is introduced: routing stays code, which is the only thing that makes it an edge.
- **Jira tracker adapter** (`scripts/delivery-flow/adapters/jira.py`) implementing the existing
  contract — `fetch`, `comment`, `related`, `transition` — against the Jira REST API, mapping
  Jira's fields onto `schemas/item.schema.json`. Deterministic, no LLM, exit codes 0/2/3, and it
  refuses outward writes while a punch-out is open. The Atlassian MCP connector is **not** usable
  here: MCP tools are callable only by the model, and an adapter must be a script.
- **A deterministic brief, not a node.** `scripts/delivery-flow/render-brief.py` renders
  `summary.md` from `item.json`, `triage.json`, `breakdown.json` and `challenge-breakdown.json`
  on a fixed template: what the ticket asks for, the epics and stories with counts, the challenge
  verdict, the findings that must be addressed, and any open punch-out. It is the chain's
  terminal prose artifact, read by a human and consumed by no step, which is the one place the
  Stage 4 rules permit prose. Being a script, it costs no `prompt-edd` package and cannot
  invent reassurance about work it did not inspect.
- **Punch-out triggers are derived, not declared.** Today `check-punch-out.py:74–86` reads
  `handoff`, `architecture_change` and `breaking_change` straight out of `triage.json` — the node
  sets the booleans that fire its own punch-out, which is the guard depending on the thing it
  guards. Each trigger gains an independent derivation over the item and breakdown text, the
  domains and the counts, and **a trigger fires on the derivation or the claim**, so suppressing
  a flag no longer skips a gate. Disagreement between claim and derivation is recorded on the
  edge as `policy_disagreement` and reported, but does not fail the edge — see design.md D5 for
  why the stronger rule was wrong. The bypass suite gains attacks on the derivation.
- **Brief coverage is a hard edge; readability is measured, not blocking.** The edge check
  asserts that every epic and story id in `breakdown.json` appears in `summary.md`, that the
  verdict and every `WEAKENED` finding appears, and that the brief introduces no identifier
  absent from its inputs. Flesch-Kincaid and Gunning Fog are computed via
  `skills/readability/scripts/readability.py` and recorded in the trace as metrics, because the
  prose the brief inherits comes from the breakdown node and failing the renderer for it would
  punish the wrong step.
- **Three real runs and the number.** `delivery-report.py` gains per-profile aggregation so the
  end-to-end rate is reported for the certified chain specifically, with `completed` /
  `punched-out` / `failed` / `abandoned` broken out and both readings of the punch-out
  denominator emitted.
- Docs updated per the CLAUDE.md doc-sync rule.

## Capabilities

### New Capabilities
- `delivery-flow-profiles`: the `profile:` config key, the named step subsets, per-profile
  terminus and `outcome.json` semantics, next-profile reporting, and the rule that profile
  handoff happens through artifacts rather than a supervising step.
- `jira-tracker-adapter`: the Jira implementation of the tracker contract, the field mapping
  onto `item.schema.json`, credential handling, determinism, and its exit-code behaviour.
- `delivery-brief-rendering`: the fixed brief template, the deterministic renderer, the coverage
  and no-new-identifier edge checks, and the traced readability metrics.
- `derived-punch-out-triggers`: independent derivation for each trigger, flags treated as
  claims, claim-versus-derivation disagreement as an edge failure, and the added bypass attacks.

### Modified Capabilities

<!-- none live: delivery-flow's specs belong to the unarchived change add-delivery-flow and are
     not yet in openspec/specs/. This change's requirements amend that change's deltas and the
     two archive together; see design.md D9. -->

## Impact

- **New:**
  - `scripts/delivery-flow/adapters/jira.py`;
  - `scripts/delivery-flow/render-brief.py`;
  - `templates/delivery-flow/profiles.yaml` (the named step subsets);
  - `tests/delivery-flow/test_profiles.py`, `test_render_brief.py`, `test_jira_adapter.py`
    (fixture-based, no network);
  - `tests/delivery-flow/bypass/` additions for the derived triggers.
- **Modified:**
  - `scripts/delivery-flow/flow-status.py` (profile-aware routing; `STEPS` becomes a lookup over
    the profile's subset rather than a module-level list);
  - `scripts/delivery-flow/check-punch-out.py` (derivations; claims cross-checked);
  - `scripts/delivery-flow/delivery-report.py` (per-profile rates);
  - `hooks/check-edge.py` (`summary.md` joins the terminal-prose checks, with coverage);
  - `templates/delivery-flow/delivery-flow.yaml` and
    `skills/delivery-flow/references/config.md` (the `profile:` key, changed together);
  - `skills/delivery-flow/SKILL.md` (profiles, the terminus, the brief);
  - `skills/delivery-flow/references/adapters.md` (Jira moves from deferred to shipped).
- **Docs (doc-sync rule):** `docs/using-the-sdlc-dev-team.md`, `agents/README.md`, the
  `skills/prime/` team bindings, `docs/figures/delivery-flow.svg` (the profile boundary and the
  terminus), and a new `CLAUDE.md` consistency rule for the paired profile template and parser.
- **Dependencies:** `add-delivery-flow` (partially implemented; this change assumes its hooks,
  schemas, sentinels, trace and punch-out machinery). A Jira API token, supplied by environment
  and never committed.
- **Deferred, unchanged:** the vault steps stay off (`vault.binding: null`), so
  `extend-vault-graphrag-projects` is not a blocker here. OpenSpec proposal, SDLC implementation,
  verify, PR and post-back remain in the `full` profile and are the subject of follow-up changes.
- **Non-breaking:** repos without a `profile:` key get `full`, which is today's routing table
  unchanged.
