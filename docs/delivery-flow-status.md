# delivery-flow: running status

Short, current, and overwritten each session. The full picture is in
`docs/delivery-flow-handoff.md`; this is just where things stand right now.

Last updated 2026-10-30.

## The one thing blocking submission

**Criterion 4 needs completed runs on the `triage` profile, and there are none.**

Everything else is either built and evidenced or is a question for the reviewer. The two
structural reasons criterion 4 could not produce a number are both fixed as of today, so the
remaining work is to run the thing.

## The five criteria

| Criterion | State |
|---|---|
| Workflow definition | Evidenced — skill, router, schemas |
| Guardrails | Evidenced — edge hook, sentinels, schemas |
| Punch-out evidence | Evidenced — triggers, signed decisions, blocking hook, 23/23 bypass report |
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

## What is left

1. **Run AN-3702 to completion on the `triage` profile.** This is the only thing that produces
   a certified data point, and it is also the first live test of the PR #105 fix — the fixture
   reproduces the sequence, but every real run this week has found something a fixture did not.
2. **Ask the reviewer whether criterion 4 wants a weekly trend or a single rate with a stated
   denominator.** Still unsent. It decides whether this is one week of running or four, and it
   is the only item that can shrink the remaining work rather than add to it.
3. **Settle whether the signing key requires presence.** Three consecutive
   `ssh-keygen -Y sign` calls succeeded with no prompt, after one that did. Either Secretive
   caches authorization or the key lacks *Authenticate before use*; it is not determinable from
   the shell. Criterion 3's claim rests on it.
4. **Re-run the bypass suite.** 23/23 stands, but it was measured before today's changes to
   `check-edge.py`, and the 24th attack (`write-decision-absolute-variable`) has never run.
   The suite spends API credits per attack, so this is a deliberate choice, not an oversight.
5. **Self-test #7 has no answer in the report.** "Can you state the number of
   manually-corrected runs?" — `write-outcome.py` detects them and marks the run `failed`, but
   `report.md` carries no count. A reviewer asking that question gets nothing.

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

- 505 tests pass, 1 skipped. Neither `pytest` nor `uv` is on PATH and mise has no global
  python pinned, so the suite needs a venv built from
  `~/.local/share/mise/installs/python/3.12.15/bin/python3`. Worth making permanent.
- Three sessions share this checkout; each should work in its own git worktree. `main` moved
  four times in one afternoon, so merge `origin/main` and re-run the suite before pushing.
