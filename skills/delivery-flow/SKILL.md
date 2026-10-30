---
name: delivery-flow
description: "Drive one work item from a tracker to a merged, deployed change — the orchestrator that turns 'new issue' into triage, plan, build, verify, PR, and a ticket update. Artifact-driven: it reads delivery/<ITEM-KEY>/ and the trace to find where the item is, then runs the next step. Use when starting work on a tracker item, resuming one, or asking what the next step is. Routes to the triage and breakdown nodes, the adversarial validator, the SDLC team, pr-description, and the tracker/forge adapters."
user-invocable: true
argument-hint: "<ITEM-KEY> [--status | --step <name>]"
---

# Delivery flow — the orchestrator

Drive one item through the pipeline. This skill owns **sequence and state**; the step
prompts own content. State lives on disk: `delivery/<ITEM-KEY>/` in the working repo, plus
`trace.jsonl`, is the single source of truth for where an item has got to.

## Position is computed, never remembered

Never decide from memory, or from this conversation, where an item is. Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/delivery-flow/flow-status.py <ITEM-KEY>
```

It prints the routing table with what exists, what each artifact's edge check said, any open
punch-out, and either `Next: <step>` or `BLOCKED — <reason>`. Do what it says. If it says
blocked, stop and tell the human what the block is; do not route around it.

`--status` means: print that and stop. `--step <name>` forces one step, which is for redoing
a distillation after new input arrives, not for skipping a block.

## Artifacts live in the vault, never in the repo

A run's artifacts are the ticket body, the triage rationale, the breakdown and the brief —
someone else's words, most of the time. In the code repo that is one `git add` from a branch
and one push from publishing a client's text, so `artifacts.root` points at the vault's
`_runs` directory and the vault's own private git does the versioning and the cross-machine
sync.

This is enforced, not advised: `flow-status.py` exits 2 before computing a position if the
root is inside the code repo, or if a vault is bound and the root sits outside it. The only
exception is `artifacts.in_repo_ack`, a written reason rather than a flag. **Never add that
ack to get a blocked run moving** — it is a decision about where a client's data may live,
which makes it a human's, and the honest fix is almost always to point `artifacts.root` at
the vault instead.

## Before anything: the binding

Read `.delivery-flow.yaml` at the repo root ([references/config.md](references/config.md)).
It names the tracker and forge adapters, the punch-out policy, the per-step models, any
roster overrides, and the optional vault binding. **If it is missing, stop and ask which
repo this is** — never guess a tracker or open a PR against an unconfigured forge.

Nothing else in this plugin is per-project, so a repo opts in with one command:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/delivery-flow/init-delivery-flow.py <repo> \
    [--profile triage|full] [--jira-project KEY] [--internal] [--contract-paths a,b]
```

It detects the forge, base branch, test command and the protected paths that actually exist,
and refuses to guess the three things guessing would get wrong: the Jira project key,
`tracker.external` (a Jira not declared `--internal` is assumed to be someone else's), and
`contract_paths`. Credentials are never written to the file — the Jira adapter reads
`JIRA_BASE_URL`, `JIRA_EMAIL` and `JIRA_API_TOKEN` from the environment. Run it with
`--dry-run` first; it will not overwrite an existing config without `--force`.

## Which adapter to run

`tracker.kind` and `forge.kind` in the config name the script. Do not read a tracker any other
way — not with an MCP connector, not with a web fetch. An MCP tool is callable only by a model,
and the whole point of an adapter is that the flow, the tests and the eval suites can call it
with no model and no network.

| Config | Script | Subcommands |
|---|---|---|
| `tracker.kind: jira` | `adapters/jira.py` | `fetch`, `related`, `comment`, `transition` |
| `tracker.kind: github-issues` | `adapters/github_issues.py` | the same, via `gh` |
| `tracker.kind: local-markdown` | `adapters/local_markdown.py` | the same, plus `import` |
| `forge.kind: github-pr` | `adapters/github_pr.py` | `open-pr`, `ci-status` |

Exit codes are the contract: **0** fine, **2** a usage error or a refusal, **3** a remote or
auth failure with the fix on stderr. **A 2 is never something to work around.** It is usually
the adapter refusing an outward action while a punch-out is open, which is the guardrail doing
its job; raise the decision instead. Field mappings and each adapter's quirks are in
[references/adapters.md](references/adapters.md).

## The routing table

| # | Artifact | Step | Who runs it |
|---|----------|------|-------------|
| 1 | `item.json` | intake | tracker adapter (script) |
| 2 | `triage.json` | triage | certified node → `references/triage.md` |
| 3 | `project-context.json` | project-memory | script → `vault-recall.py` (skipped with no vault binding) |
| 4 | `breakdown.json` | breakdown | certified node → `references/breakdown.md` |
| 5 | `challenge-breakdown.json` | challenge-breakdown | certified node → `references/challenge-breakdown.md`, in a fresh context via `cross-examine` → adversarial-validator |
| 6 | `proposal.json` + `openspec/changes/<id>/` | propose | node → `references/propose.md` (**uncertified**) |
| 7 | `summary.md` | brief | script → `render-brief.py` |
| 8 | `implementation.json` | implementation | SDLC dev pair, per task |
| 9 | `verify.json` | verify | the repo's test command + protected-paths check |
| 10 | `challenge-implementation.json` | challenge-implementation | `cross-examine` |
| 11 | `pr.md` → `pr-opened.json` | pr-description, open-pr | node, then forge adapter |
| 12 | `post.md` → `posted.json` | post-summary, post-back | node, then tracker adapter |
| 13 | `outcome.json` | report | script → `write-outcome.py` |
| 14 | `vault-updated.json` | vault-update | node → `references/vault-update.md` (**uncertified**; skipped with no vault binding) |

**Branching.** A `bug` or `task` takes the quick path and skips the breakdown and its
challenge; a `feature` takes the standard path and runs everything. The path comes from
`triage.json`, not from your judgement, and `flow-status.py` already applies it.

## Profiles: running part of the table

`profile:` in `.delivery-flow.yaml` names an ordered slice of the table from
`templates/delivery-flow/profiles.yaml`, and routing happens inside that slice only. A repo
naming no profile gets `full`, which is every step.

| Profile | Steps | Ends with |
|---|---|---|
| `triage` | intake → triage → (project-memory) → breakdown → challenge-breakdown → brief → report | `summary.md`, then `outcome.json` |
| `full` | …the same, then propose → brief → implementation → verify → challenge-implementation → PR → post-back → report → vault-update | `vault-updated.json` |

`triage` is the Stage 4 certified chain: three certified nodes, deterministic edges between
them, a rendered brief for a human, and an outcome. Nothing is implemented and no PR is
opened, so it has no outward action.

`full` adds the proposal and everything after it. **Its rate is not a Stage 4 number** while
`propose` is uncertified: an uncertified node in the chain makes the end-to-end figure
meaningless, which is why the report breaks the rate out per profile.

**A profile hands over through the artifact directory, not through you.** When a profile
reaches its terminus, `flow-status.py` names the next profile and stops. The next profile
recomputes its own position from `delivery/<ITEM-KEY>/`; nothing records which profile wrote
what. Do not "continue into" the next profile in the same invocation, and never invent a
supervising step that decides which profile runs — profile selection is config, and position
is computed. A model whose job is routing is a node, not an edge.

## The proposal, and the brief as the approval surface

In `full`, `propose` turns the challenged breakdown into an OpenSpec change —
`openspec/changes/<id>/` with `proposal.md`, `design.md`, at least one delta spec and
`tasks.md` — plus `proposal.json`, the contract the implementation step reads. The change
directory is for humans and for `openspec archive`; the JSON is the edge.

Its edge checks the two against each other: task ids must match **in both directions**, named
specs must exist, and every planned file path must stay inside the repo. `openspec validate
--strict` runs as an extra layer where the CLI is installed and is recorded as *skipped* where
it is not — never as a pass.

`brief` then runs, and `summary.md` gains a "What will change" section. The proposal's
punch-out triggers fire on leaving the brief, not on writing the proposal: explanation before
decision, so the human is never asked to decide with nothing to read. Those triggers —
`proposal-scope`, `proposal-breaking`, `proposal-architecture`, `protected-path`,
`new-dependency` — derive from the **planned file paths**, so unlike the triage-sourced ones
they cannot be reworded away.

After implementation, `close-openspec-change.py` ticks the change's `tasks.md` from
`implementation.json` and prints the `openspec archive` command. It never archives: that is a
human's, and `flow-status.py` reports any change left with unticked tasks so a change directory
cannot be abandoned quietly.

## Project memory

`project-memory` is a **script**, not a node: `vault-recall.py` implements the specified
scoring (3 per same project, 3 per shared service, 2 per shared domain — 3 during
implementation — 1 per keyword, threshold 3, capped 5/5/3/3) over note frontmatter. There is no
judgement in that, so there is nothing to certify, and it reports facts by construction rather
than because a prompt was told to.

**An unreachable vault is not an empty one.** Recall checks the graph root before scanning: a
missing root is exit 3 with no artifact and the flow stops. A reachable vault with nothing above
the threshold is exit 0 with an artifact whose `matched: false` and whose coverage section says
what was scanned. Never treat the first as the second — proceeding would silently drop the
project's memory from the run while the trace still read as successful.

**The vault is a local git clone, so check freshness, not reachability.** The canonical bare
repo lives on a NAS; the clone is always there, which is the point — work continues off the
home network. The cost is that a clone weeks behind looks identical to a current one, so recall
reports its sync state and sets `stale` against `punch_out.vault_staleness_days`. A stale run
still proceeds, and `project-context.md` opens with a warning. Staleness counts from the last
**fetch**: a push proves the remote answered but teaches the clone nothing. **Never push** —
`vault-update` commits, and the push is a human's to make on the right network.

`vault-update` is a node, because writing a delivery note's one-line `goal` / `approach` /
`outcome` is composition rather than traversal. It is uncertified and declared.

## The brief is rendered, not written

`summary.md` is produced by `render-brief.py` from `item.json`, `triage.json`,
`breakdown.json` and `challenge-breakdown.json` on a fixed template. It is a script, not a
node: it has no prompt, no certification, and no sentinel, because a deterministic producer
has no claim to test. Never hand-write or reword it — rerun the renderer.

Its edge asserts what the renderer is answerable for: every epic and story id present, the
verdict present, every finding the verdict requires present, and no identifier that appears
in none of its inputs. Readability (Flesch-Kincaid, Gunning Fog) is measured into the trace
but never gated, because the prose is inherited from the breakdown node and the renderer
cannot rewrite it.

## Running a step

1. **Check the step is certified.** `check-certification.py <step>` must exit 0, unless the
   config lists the step under `allow_uncertified` — in which case the trace records
   `certified: false` and the run is excluded from the certified-only success rate.
2. **Write `.current-step`** (`{"step": "<name>", "item": "<KEY>", "started_at": "<iso>"}`)
   so the trace hook can attribute the tokens.
3. **Delegate in a fresh context**, handing the step only its declared inputs: the artifacts
   named in `steps.yaml`, and the binding. Never the conversation that produced them —
   that is what makes a reviewer a rubber stamp.
4. **The node writes its artifact and then its sentinel**
   (`write-sentinel.py <artifact> --step <name>`).
5. **The edge hook checks it automatically.** You do not run the validator; it fires on the
   write. Read the result from the trace via `flow-status.py`.

## The rules that make this a workflow rather than a script

- **One step per invocation** unless the human says to run ahead. Report it as
  [Reporting to the human](#reporting-to-the-human) requires — that section is binding, not
  advisory.
- **Artifacts are contracts.** Never hand-write or "tidy" an artifact. If one is wrong,
  rerun the step that produces it — a hand-edited artifact hides the regression and marks
  the item `failed` with reason `manual-correction` when the trace sha no longer matches.
- **Never advance past a failed edge.** Rerun the producing step with the edge report, at
  most 3 times; after that it is a punch-out, not another attempt.
- **The challenge is a node, not a rubber stamp.** It runs in a fresh context with the
  artifact and the raw material, never the reasoning that produced it. Its verdict routes
  mechanically, and `flow-status.py` applies the routing rather than you:
  - **REFUTED** reruns the producing step with the findings. Twice on the same target is a
    punch-out, not a third attempt.
  - **WEAKENED** proceeds. The findings come back from `flow-status.py` under
    `carry_forward`, and the step that consumes the artifact has to address each one.
  - **SURVIVED** proceeds.
  - A verdict is about **one version** of its target. Rewrite the target and the challenge
    on disk is stale, so the challenge reruns against the version that now exists — which
    is also why a refutation does not block the flow forever.
- **Punch-outs are the human's, and only the human's.** You may not write a decision, clear
  a punch-out, merge a PR, or deploy anything beyond a routine bump. The hooks block all of
  these; do not attempt them and then report the block as a problem.
- **The policy flags are not the gate.** `scope`, `architecture` and `breaking` each fire on
  the node's flag in `triage.json` *or* on a derivation that never reads it, so clearing a
  flag does not clear the trigger. Where flag and derivation disagree, the edge records
  `policy_disagreement` and passes — the disagreement is evidence, not a failure. Do not
  rewrite an artifact to quiet a trigger: hand-editing one marks the run `failed` with reason
  `manual-correction`, and rerunning the node to launder its own text is the one residual this
  design admits to rather than hiding.
- **Quality between steps is automated.** There is no "ask the human to review this spec"
  step. If an artifact is wrong, the edge or the challenge catches it, or the success rate
  records that neither did.

## Reporting to the human

**Follow the `writing-for-adhd` skill for every message you send the human.** It is the
authority on the shape; this section is only how it applies here. Do not restate its rules,
and do not treat a long report as thoroughness — a wall of text is the failure mode, not the
evidence.

This pipeline is already built the way that skill asks for: **the artifact is the detail and
the message is the pointer.** `summary.md`, `punch-out-<n>.md` and `flow-status.py` are all
addressable and re-readable. A message that repeats them has created a second version that
will go stale, and has spent the reader's attention to do it.

So, per step:

- **Four sentences at the outside.** First sentence says what to do or what happened — not
  what you ran, not how it went, not the approach.
- **Name the path, don't summarise the file.** "Decision in `delivery/AN-3630/punch-out-1.md`"
  beats a paragraph restating its evidence. Never paste an artifact's contents into chat.
- **One decision.** If `check-punch-out.py` raised several, present the lowest-numbered one and
  leave the rest in their files. Two asks in one message reliably gets one answered and the
  other silently dropped — and you will not know which.
- **End on one concrete next action**, never a menu and never "let me know how you'd like to
  proceed".
- **Don't narrate the routing.** The table, the step list and the edge results are what
  `flow-status.py` prints on demand. Saying "next: breakdown" is the report; reproducing the
  table is noise.
- **Open with what worked.** A message that opens on the block reads as bad news before it is
  parsed, and the block is usually one clause.

When a step fails or an edge rejects an artifact, the same limits hold — the full edge report
is in the trace, so the message is the one-line cause plus the path. A failure is the case
where the temptation to write ten paragraphs is strongest and the reader's capacity for them
is lowest.

## Finishing

Every item ends with `outcome.json`: `completed`, `punched-out` (a human took the decision
and the flow stopped), `failed` (retries exhausted, or an artifact was hand-corrected), or
`abandoned`. The report script writes it; `delivery-report.py` rolls outcomes up into the
end-to-end rate and the per-step model, token and cost tables.

## References

- [references/config.md](references/config.md) — `.delivery-flow.yaml`, every key
- [references/adapters.md](references/adapters.md) — the adapter contract, and how to add Jira, GitLab or Bitbucket
- [references/roster.md](references/roster.md) — kinds of work → specialists
- [references/trace.md](references/trace.md) — what the trace records and how to read it
- `writing-for-adhd` — the shape of every message this flow sends the human (see
  [Reporting to the human](#reporting-to-the-human))
- `references/triage.md`, `references/breakdown.md`, `references/challenge-breakdown.md` — the certified node prompts, one per chain node (edit any of them and it is uncertified until its suite is re-run)
