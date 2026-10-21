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

## Before anything: the binding

Read `.delivery-flow.yaml` at the repo root ([references/config.md](references/config.md)).
It names the tracker and forge adapters, the punch-out policy, the per-step models, any
roster overrides, and the optional vault binding. **If it is missing, stop and ask which
repo this is** — never guess a tracker or open a PR against an unconfigured forge.

## The routing table

| # | Artifact | Step | Who runs it |
|---|----------|------|-------------|
| 1 | `item.json` | intake | tracker adapter (script) |
| 2 | `triage.json` | triage | certified node → `references/triage.md` |
| 3 | `project-context.json` | project-memory | vault recall (skipped with no vault binding) |
| 4 | `breakdown.json` | breakdown | certified node → `references/breakdown.md` |
| 5 | `challenge-breakdown.json` | challenge-breakdown | `cross-examine` → adversarial-validator |
| 6 | `spec-ready.json` | solutioning | SDLC orchestrator (standard path) |
| 7 | `implementation.json` | implementation | SDLC dev pair, per story |
| 8 | `verify.json` | verify | the repo's test command + protected-paths check |
| 9 | `challenge-implementation.json` | challenge-implementation | `cross-examine` |
| 10 | `pr.md` → `pr-opened.json` | pr-description, open-pr | node, then forge adapter |
| 11 | `post.md` → `posted.json` | post-summary, post-back | node, then tracker adapter |
| 12 | `outcome.json` | report | script |
| 13 | `vault-updated.json` | vault-update | vault update (skipped with no vault binding) |

**Branching.** A `bug` or `task` takes the quick path and skips the breakdown and its
challenge; a `feature` takes the standard path and runs everything. The path comes from
`triage.json`, not from your judgement, and `flow-status.py` already applies it.

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

- **One step per invocation** unless the human says to run ahead. Say what was produced and
  what comes next.
- **Artifacts are contracts.** Never hand-write or "tidy" an artifact. If one is wrong,
  rerun the step that produces it — a hand-edited artifact hides the regression and marks
  the item `failed` with reason `manual-correction` when the trace sha no longer matches.
- **Never advance past a failed edge.** Rerun the producing step with the edge report, at
  most 3 times; after that it is a punch-out, not another attempt.
- **The challenge is a node, not a rubber stamp.** It runs in a fresh context with the
  artifact and the raw material, never the reasoning that produced it. Its verdict routes
  mechanically: REFUTED reruns the producing step with the findings and invalidates
  everything downstream; WEAKENED means each finding is addressed in the next version;
  SURVIVED proceeds.
- **Punch-outs are the human's, and only the human's.** You may not write a decision, clear
  a punch-out, merge a PR, or deploy anything beyond a routine bump. The hooks block all of
  these; do not attempt them and then report the block as a problem.
- **Quality between steps is automated.** There is no "ask the human to review this spec"
  step. If an artifact is wrong, the edge or the challenge catches it, or the success rate
  records that neither did.

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
- `references/triage.md`, `references/breakdown.md` — the certified node prompts (edit either and it is uncertified until its suite is re-run)
