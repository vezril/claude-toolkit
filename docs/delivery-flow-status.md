# delivery-flow: running status

Short, current, and overwritten each session. The full picture is in
`docs/delivery-flow-handoff.md`; what comes *after* the submission is in
`docs/delivery-flow-next-workflows.md` (AWS testing, ready-to-PR, PR review — assessed, not
started, and deliberately not started until Stage 4 has its runs). This is just where things
stand right now.

Last updated 2026-11-02.

## What is blocking submission

**Only volume.** Criteria 1, 2, 3 and 5 are evidenced, and criterion 4 has its first certified
run. What is missing is a week's worth of runs behind it, which is execution rather than
engineering.

Two standing prerequisites before each run:

- **The plugin cache must match `main`.** It is built from the marketplace *directory* source
  at `/Users/mferecal/Code/claude-toolkit`, so the checkout has to be pulled *before*
  `claude plugin update` — otherwise the update finds nothing newer and silently keeps a stale
  version. Every fix merged on 2026-10-29 and 10-30 sat inert for a day for exactly this
  reason.
- **`nx-neptune` must be on `profile: triage`.** It gets switched to `full` for implementation
  work, and `full` adds `propose` and `implementation`, neither of which can contribute to the
  certified-only figure.

## Runs

```
AN-3702             completed    profile=triage   1 failed edge    0 corrections   certified
DISCARDED-AN-3630   contaminated trace (orchestrator attribution)
DISCARDED-AN-3631   74 failed edges, 62 of them one bug repeating
DISCARDED-AN-3702   48 identical failure records from the retry loop
DISCARDED-AN-3704   contaminated trace (orchestrator attribution)
```

Four discarded, one good. Every discard is a hook defect found by running real data, not a
pipeline failure — the nodes did their work and the artifacts were valid in all four.

## The regression I shipped, and what it cost

PR #105 made a failed edge re-check on every subsequent hook invocation, on the reasoning that
only a failure can be stale. The premise is true; the conclusion that every failure becomes
*fresh* does not follow. A failure whose cause is neither the artifact nor its sentinel never
changes, so it re-checked forever and appended a record each time.

Measured on the live runs: `proposal.json` on AN-3702 reached **44 identical failure records**,
and AN-3631 went from 8 failed edges to 65. Criterion 4's numbers were being computed over
that.

Fixed in 0.14.1 (`415d45e`): the gate now compares the edge's *whole* input — the artifact's
sha and its sentinel's — and re-checks when either moved, which keeps #105's real fix and
gives it the termination condition it never had.

**The existing traces kept the junk records,** since the trail is append-only — so both runs
were discarded rather than corrected. AN-3631 went on Calvin's decision on 2026-11-02, once
AN-3702's clean completion meant discarding it no longer left zero runs.

The suite missed it because it tested that a *passing* record suppresses re-checking and never
asked what a failing one does. That is the third time this week a test asserted the right thing
about the wrong half of a condition.

## The five criteria

| Criterion | State |
|---|---|
| Workflow definition | Evidenced — skill, router, schemas |
| Guardrails | Evidenced — edge hook, sentinels, schemas |
| Punch-out evidence | Evidenced — triggers, signed decisions that verify, blocking hook, bypass report (as of 2026-10-28) |
| **End-to-end success rate** | **Machinery correct; no certified run yet** |
| Audit trail | Evidenced — trace hook, report |

`package-evidence.py --dry-run` builds all five directories with no `MISSING.md`, and all four
certified prompts pass their gates (`triage` 38/40, plus `breakdown`, `challenge-breakdown`,
`pr-description`).

## Fixed today

1. **The certified-only rate could only ever be 0/0.** `trace-step.py` records the
   orchestrator's own turns as `step: "orchestrator"` with `certified: false` — deliberately,
   its cost is real — and `delivery-report.py` disqualified a run if *any* record was
   uncertified. So every orchestrated run, which is every real run, was excluded.
   DISCARDED-AN-3704 is the proof: a clean `triage`-profile run whose only uncertified step was
   the conductor. `report` and the other deterministic steps did the same thing.

   `certifiable()` now judges only steps whose routing-table kind is `node` or `sdlc`. The
   report names what it set aside and which nodes genuinely failed, under *What the
   certified-only rate claims*, because **this is a claim a reviewer may reject** and it should
   not be applied silently. If the orchestrator belongs inside the claim, the answer is to
   certify it, not to widen the denominator.

2. **A failed edge is retried when its cause was never the artifact's bytes** (PR #105).
   AN-3702 deadlocked on a correct artifact: the node wrote `triage.json`, the hook fired
   before the sentinel existed, and nothing ever looked again. Both seams fixed — the sha gate
   now retries a *failed* record, and Bash paths resolve against the real configured roots
   instead of a `delivery/` regex that cannot survive a space in `Amazon RAG`.

3. **Eight artifacts had no edge and nothing said so** (PR #102). They now record
   `edge: {"name": "no-schema"}`. Recording the gap is not closing it — they are still
   unchecked — but the absence is countable now.

4. **`delivery-report.py` could not read the real runs at all** (PR #102), so criterion 4's
   numbers had been uncomputable since `artifacts.root` moved the artifacts to the vault. The
   failure read like an empty directory.

## Where the runs stand

```
AN-3631   completed    52 steps   8 failed edges   0 unchecked   $44.36
          certified=no — ran `propose` and `implementation`, both uncertified nodes
AN-3702   in-flight     0 steps   1 failed edge    0 unchecked
          next: triage
DISCARDED-AN-3630, DISCARDED-AN-3704 — excluded, contaminated token/cost records
```

Weekly, all profiles: 1 completed, 0 failed, 0 punched out → 100% on n=1.
Certified-only: still 0/0, now for an honest reason rather than a structural one.

**`nx-neptune` is switched back to `profile: triage`.** `full` adds `propose` and
`implementation`, so a `full` run can never contribute to criterion 4 however cleanly it
finishes. AN-3631 is the proof. Switch to `full` when there is implementation work to drive;
certifying `propose` is what would remove the choice.

## Also landed since the last pass

- **Run artifacts belong in the vault, enforced** (0.14.0, `e471e2e`). `flow-status.py` exits 2
  before computing a position when the root is inside the code repo, or when a vault is bound
  and the root sits outside it. `artifacts.in_repo_ack` is the only exception and it is a
  sentence, not a boolean. `init` refuses to guess: `--vault-path` or
  `--artifacts-in-repo "<reason>"`. `artifacts.commit` is deleted — it was written into every
  generated config and read by no code.
- **The proposal edge resolves against the code repo** (`f5cbf86`), not the artifact's own
  directory, which under an external root was the vault.

## The first certified run

**AN-3702 completed the `triage` profile on 2026-11-02 and is the Stage 4 data point.**

```
AN-3702   completed   profile=triage   failed_edges=1   certified=True   corrections=0
2026-W45  certified-only: 1 completed, 100.0%
```

Three punch-outs were raised (`architecture`, `breaking`, `breaking`), all three decided
`proceed`, and all three signatures verify against `allowed_signers`. That is criterion 3 on
real evidence rather than a fixture.

`triage.json` failed its edge at 15:47:41 on the missing sentinel and cleared itself at
15:47:45 — the 0.14.1 fix working in production on the exact deadlock that killed the previous
attempt.

**One caveat for the submission.** Its directory also holds `proposal.json` and
`implementation.json`, because the profile was switched to `full` after the terminus and the
flow continued. Its `outcome.json` predates the `off_profile_artifacts` field, so nothing in
the file records that. Either note it in the submission or re-run the item clean now that the
guards are in place.

## What is left

1. **Runs on more tickets.** One is a data point, not a rate. **A week's worth is the target**
   (decided 2026-11-02), with the profile held at `triage` throughout — `full` adds `propose`
   and `implementation`, and neither can contribute to the certified-only figure.
2. ~~Ask the reviewer about trend versus rate.~~ **Decided: give both** (2026-11-02). The
   report emits a weekly trend *and* a single rate over all runs with the denominator stated,
   so the question no longer gates the submission. While there are only a week or two of data
   the single rate is the more honest of the two — two points are not a curve.
3. ~~Settle whether the signing key requires presence.~~ **Accepted as-is** (2026-11-02):
   ship it, and adjust if review comes back on it. Fail fast rather than block. The open
   question stands on the record — three consecutive `ssh-keygen -Y sign` calls succeeded
   with no prompt after one that did, so either Secretive caches authorization or the key
   lacks *Authenticate before use*, and it is not determinable from the shell. Criterion 3's
   "an agent cannot forge this" claim rests on the answer.
4. ~~Re-run the bypass suite.~~ **Not re-running** (2026-11-02). The report stands as a dated
   measurement — it says "on the evidence of this run" with its own timestamp — and is cited
   that way rather than as current. It predates roughly ten changes to the gate code, and the
   24th attack (`write-decision-absolute-variable`) has never run. The suite itself is kept:
   it is criterion 3's only adversarial evidence, and deleting it would remove the answer to
   "has anyone actually attacked the punch-outs?".
5. ~~Self-test #7 has no answer in the report.~~ **Done.** `outcome.json` had carried the
   evidence all along — artifact, traced sha, actual sha — and nothing read it, so the honest
   answer to a reviewer was "no". `report.md` now has a *Manually-corrected runs* section
   stating runs corrected over terminal runs, with the artifacts named. No terminal runs
   reports "no rate", which is not the same claim as zero.

## Open decisions

1. **A path gate cannot tell a signature change from a body change.** `contract_paths` is
   narrowed as far as paths allow and is still coarse: any edit to an exported module fires.
   Either accept the false-positive rate and say so, or derive the breaking trigger from the
   public API rather than from file paths. Not worth starting before a clean run says how
   often it actually fires.
2. **Three registry steps declare an input their schema does not claim.** `breakdown` and
   `challenge-breakdown` read `item.json`; `challenge-breakdown` reads `triage.json`. These are
   *under*-declarations, so no check runs that shouldn't, but no input contract is enforced
   either. Closing it means deciding which fields those certified steps require, which would
   start failing edges in a chain whose evals ran without them. Pinned at exactly three by a
   test.
3. **`certify-sdlc-pipeline` is 5/58 tasks** and predates the D10 stories seam. Worth checking
   whether the task list still describes the plan being followed.
4. **AN-3631 holds `propose` and `implementation` records on the `triage` profile.** Either a
   legitimate handoff into `full` or steps run outside the profile; its `outcome.json` still
   says `triage`. Its step count also went 32 → 52 and failed edges 7 → 8 overnight, so
   something re-ran it.

## The pattern worth putting in the report

Fifteen defects across three runs, and five of them share a shape: **a gate that was present,
reported success, and was measuring nothing.** They are not one class, which matters for the
recommendation:

- **Dispatch** (three): the wrong diff to a correct matcher; nothing at all to a correct
  validator; the guarded node's own reasoning to a correct trigger. Wants a test at the
  dispatch boundary — "given this artifact in the real place, does the checker run at all".
- **Check** (one): both path gates matched by string prefix, so `lib` matched
  `lib_extra/core.py`. Wants the matcher tried against near-misses.
- **Declaration** (one): `story.schema.json` declared `story.json` while the producer writes
  `story-E1-S1.json`. Wants a test whose filename comes from the producer, not the registry.

Two second-order lessons, both earned the hard way:

- **A test parametrised over a registry inherits whatever the registry gets wrong.** Found by
  mutation-testing a test that passed on broken code.
- **Recording a skip can be worse than the silence it replaces.** The first version of the
  `no-schema` record said `summary: "ok"`. Silence is honestly empty; a success record is a
  false statement a reviewer would reasonably believe.

## Housekeeping

- 526 tests pass, 1 skipped. Neither `pytest` nor `uv` is on PATH and mise has no global
  python pinned, so the suite needs a venv built from
  `~/.local/share/mise/installs/python/3.12.15/bin/python3`. Worth making permanent.
- Three sessions share this checkout; each should work in its own git worktree. `main` moved
  four times in one afternoon, so merge `origin/main` and re-run the suite before pushing.
