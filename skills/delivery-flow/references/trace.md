# The trace

`delivery/<ITEM-KEY>/trace.jsonl`, one JSON object per line, appended by hooks rather than
written by steps. It answers the question Stage 4 actually asks: which step produced which
output, on which model, at what cost — and when something failed, where it started.

## Records

A **step record** (written by `trace-step.py` on SubagentStop):

```json
{"ts": "…", "item": "DEM-12", "step": "breakdown", "agent": "general-purpose",
 "session_id": "…", "agent_id": "…", "model": "claude-sonnet-5",
 "input_tokens": 14230, "output_tokens": 1870,
 "cache_creation_tokens": 0, "cache_read_tokens": 12000,
 "api_equivalent_cost_usd": 0.0472, "artifact": "breakdown.json",
 "certified": true, "model_conformant": true}
```

An **edge record** (written by `check-edge.py` on PostToolUse, pass or fail):

```json
{"ts": "…", "item": "DEM-12", "step": "breakdown", "artifact": "breakdown.json",
 "hook": "check-edge", "sha256": "ab0e92…",
 "edge": {"name": "parse+schema+sentinel+counts+input-contract+policy-claim", "exit": 1,
          "summary": "sentinel claims stories=8 but the file holds 5"}}
```

`sha256` is the artifact as the edge found it. The sentinel carries one too, but it sits
beside the artifact and is as editable as the artifact is; the trace is append-only, which is
what makes a later hand-edit detectable at all. `write-outcome.py` compares every artifact
against its last traced sha and marks the run `failed` with reason `manual-correction` on a
mismatch — so "how many runs were corrected by hand" is a number you can state.

## `name: "no-schema"` — the artifact nothing checked

Eight artifacts in the routing table have no schema to be checked against:
`implementation.json`, `verify.json`, `challenge-implementation.json`, `pr-opened.json`,
`posted.json`, `vault-updated.json`, and the `pr.md` / `post.md` prose. All eight sit in the
`full` profile past `propose`, so this is most likely a profile whose edges were never built
rather than a regression — but the pipeline could not say so, because a missing schema was a
silent skip. No check ran, nothing recorded that none had, and `flow-status.py` printed
"no edge recorded" beside a **✓**.

They now get a record saying exactly that:

```json
{"artifact": "verify.json", "sha256": "7c1d04…",
 "edge": {"name": "no-schema", "exit": 0,
          "summary": "no schema declares this artifact, so no edge ran"}}
```

**Read it by `name`, never by `exit`.** `exit: 0` here means "nothing failed because nothing
ran", which an unchecked artifact shares with a checked one that passed — collapsing the two is
the whole defect. `delivery-report.py` counts these in its own `Unchecked` column, separate
from `Failed edges`, and `flow-status.py` marks them `?` rather than `✓`.

Recording the gap is not closing it: those eight artifacts are still unchecked. What changed is
that the absence is countable, the way an uncertified step is countable because it records
`certified: false` instead of quietly not being certified. An artifact declared in neither the
routing table nor `schemas/` is still skipped silently — there is nothing to compare it against.

## Optional fields

Two optional fields appear on edge records:

```json
{"artifact": "summary.md", "edge": {"name": "coverage+readability", "exit": 0, "summary": "ok"},
 "metrics": {"flesch_kincaid_grade": 11.5, "gunning_fog": 13.5}}

{"artifact": "triage.json",
 "policy_disagreement": [{"trigger": "breaking", "flag": "breaking_change",
                          "claimed": false, "derived": true,
                          "evidence": "the text says 'breaking change'"}]}
```

- **`metrics`** on `summary.md` records the brief's readability. Measured, never gated: the
  prose is inherited from the breakdown node, so a trend here is evidence about *that*
  prompt rather than grounds for failing the renderer.
- **`openspec_validate`** appears in the `proposal.json` edge record's summary: the CLI's
  output where it ran, or `skipped: openspec is not installed`. Skipped is recorded as skipped,
  not folded into a pass — an unavailable layer is a gap in the evidence.
- **`policy_disagreement`** records where `triage.json`'s or `proposal.json`'s gating flags and the independent
  derivations part company. The edge still passes — see `triggers.py` for why the claim and
  the derivation are often not the same proposition — but the count of disagreements is a
  thing a reviewer can ask about. The trigger itself fires on either signal regardless.

A **verdict record**, one per challenge run:

```json
{"ts": "…", "item": "DEM-12", "step": "challenge-breakdown",
 "artifact": "challenge-breakdown.json", "target": "breakdown.json", "verdict": "REFUTED"}
```

The challenge artifact on disk is only the latest verdict; the trace is every one of them.
That is what lets `flow-status.py` and `check-punch-out.py` agree on when a rerun has
become a punch-out — two refutations of the same target, counted from here rather than from
a file that gets overwritten.

## Reading it

- **Token counts come from Claude Code's own transcripts**, never from an agent reporting
  its own usage. Usage is counted once per `message.id`, because a transcript repeats the
  same usage object on every content block of one API message — summing lines overcounts
  several-fold.
- **Cost is `api_equivalent_cost_usd`**: the step's tokens priced at published API list
  rates from `pricing.yaml`. Under a subscription that is not money billed, and the report
  labels it so. A model missing from the table records `null` and `pricing_missing: true`
  rather than a guess.
- **`model_conformant: false`** means the step ran on a heavier model than its registry tier
  — worth knowing, since it is how a Sonnet-tiered pipeline quietly becomes an Opus one.
- **The latest edge per artifact wins.** That is how a rerun clears a failure, and how
  `flow-status.py` decides whether the flow may advance.
- **Edge records are also the write ledger**, and their order is what tells a current
  challenge from a stale one: a target whose last edge record sits after its challenge's
  was written again after it was attacked, so that verdict no longer applies.

- **A failed recall and a cold-start recall look different here, deliberately.** An
  unreachable vault leaves the step with no artifact and a non-zero exit; a reachable vault
  with nothing relevant leaves an artifact recording `matched: false` and a full coverage
  section. If you cannot tell those apart in the trace, you cannot tell a pipeline that
  consulted its memory from one whose memory was switched off.
- **A stale recall is a third state, and it is recorded rather than failed.** The vault is a
  local clone, so recall succeeds off the home network; the step's record carries the clone's
  `days_since_sync` and `stale`, so a report can count how many runs leaned on memory nobody
  had refreshed. Freshness replaced reachability as the signal when the vault stopped being a
  network mount.
- **The end-to-end rate is also grouped by profile**, taken from `outcome.json`'s `profile`.
  The certified chain's number and the whole pipeline's number are different claims, and
  averaging them reports neither. A profile with no terminal runs has *no* rate rather than
  0%: "nobody ran it" and "it never works" are opposite conclusions.

`delivery-report.py` rolls this up: outcome and cost per item, distribution per step and
model, and the weekly end-to-end rate — reported both excluding punch-outs and counting them
as unsuccessful, since which one the certification wants is still an open question.
