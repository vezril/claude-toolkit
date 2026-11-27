# Independent audit of the "submittable" claim, 2026-11-27

I reran the gate myself rather than taking the result on report. **It does pass**, and I found
no laundering. Three things would still draw a reviewer's fire, and one of them is a bug in the
file a reviewer opens first.

## The gate, rerun

```
ok   chain steps certified      triage 95.0% · breakdown 100% · challenge-breakdown 99.1%
ok   evidence package builds clean
ok   criterion 4 has a certified-only rate     n = 9, rate 100.0%
ok   the denominator is at least 5             n = 9
ok   every terminal run has step records       10 of 10
ok   the denominator's composition is disclosed  9 of 10 are replays
Submittable.
```

## What I checked for and did not find

- **No hand-corrected artifacts.** `manual_corrections` is empty on every outcome, and that is
  measured by comparing each artifact to the sha the trace recorded, not attested.
- **No re-rolling until green.** Twelve `DISCARDED-` runs exist. Four were discarded on
  2026-11-26 (`AN-3698`, `AN-3705`, `AN-3713`, `AN-3717`) and all four had **completed
  successfully** with every edge passing; they were dropped because their step records were
  attributed to another run. Discarding successes lowers `n`, it cannot inflate a rate. The
  older discards predate this push and are documented in their own `DISCARDED.md`.
- **The seven "failed edges" are all one benign thing.** Every one is
  `no readable sentinel beside the artifact` on `triage.json` — the edge hook fires on the
  artifact write, before `write-sentinel.py` has run. Each was retried and passed. No edge
  rejected an artifact's *content* in any counted run.

## 1. Chain depth — I overstated this

**Calvin's push-back is right and this is corrected.** The deliverable is a pipeline, and
routing a `bug` down the quick path is the pipeline working, not the pipeline being skipped.
Criterion 4 asks *"what is the rate over real runs, on what denominator?"* — a rate over runs,
not per-node coverage. Nine runs of the profile are nine runs of the profile.

Two things I had the wrong weight on:

- `breakdown` and `challenge-breakdown` are **separately certified at Stage 3** on their own
  eval suites (24/24 and 107/108). Their quality is evidenced there. Criterion 4 is not a place
  to re-prove each node, and a run that correctly skips a node is not a run missing evidence.
- The branch is **computed from `triage.json`, not chosen** by anyone, so eight quick-path runs
  are eight samples of the routing decision as well as of triage.

What actually survives is small and is a presentation point, not an evidence gap: the standard
path has one sample, so if the standard path held a defect these runs would not show it. The
package's `RESIDUALS.md` already says the rate is thin. Worth having the one-line answer ready
— *the profile branches by work kind and the branch is derived, not chosen* — rather than
meeting the question cold.

### The original framing, for the record

| run | kind | path | breakdown | challenge | certified nodes exercised |
|---|---|---|---|---|---|
| AN-3641 | bug | quick | — | — | triage |
| AN-3645 | task | quick | — | — | triage |
| AN-3649 | task | quick | — | — | triage |
| **AN-3662** | **feature** | **standard** | **yes** | **yes** | **triage, breakdown, challenge-breakdown** |
| AN-3665 | bug | quick | — | — | triage |
| AN-3708 | bug | quick | — | — | triage |
| AN-3711 | bug | quick | — | — | triage |
| AN-3733 | task | quick | — | — | triage |
| AN-3739 | task | quick | — | — | triage |

The triage profile routes a `bug` or `task` past the breakdown and its challenge, so these runs
completed the profile **correctly**. The rate is not wrong. But the submission's chain is three
certified nodes, and the three-node chain ran end to end exactly **once**. Eight of nine runs
exercised one node.

"100% end-to-end, n=9" is literally true and invites the question *nine samples of what?* The
answer today is: eight samples of triage, one of the chain.

The four discarded-but-complete runs are `bug`, `task`, `task`, `task` — recovering them adds
denominator and no depth.

More `feature` runs would strengthen the standard path, and they are cheap if tickets exist.
They are **not** a blocker.

## 2. Every counted run is a replay

Nine of ten, and the single non-replay (`AN-3702`) is the uncertified one. So the certified rate
contains zero live deliveries. The report discloses this prominently and argues the case — for
an analysis-only profile a replay exercises exactly what the rate measures — which is the
honest handling. It is still the second thing a reviewer will ask about, and worth having an
answer ready rather than discovering the question.

## 3. The package overstated the run count 22× — the one real blocker (now fixed)

This is worse than I first wrote, because it is not only the manifest. Built the default way
the package's README reported:

| | package said | actually |
|---|---|---|
| completed runs | **220** | 10 |
| discarded runs | **264** | 12 |
| manifest entries | **10,244** | 498 (499 distinct files) |

Every manifest entry repeated about 22 times with an identical package path, source path and
sha256, and the run census was multiplied by the same factor. A reviewer reading "220 completed
runs" beside a rate quoted over n=9 would find an inconsistency that looks like invention.

Cause, traced: `package-evidence.py:250` falls back to `known_repos()`, and the registry at
`~/.config/delivery-flow/repos` holds 22 entries — `nx-neptune` plus 21 of its per-ticket
worktrees under `.worktrees/`. `ensure-worktree.py` copies `.delivery-flow.yaml` into each
worktree by design (a worktree without it has inert hooks), so each one registers itself as a
delivery repo, and they all resolve to the same `artifacts.root`. The packager walks all 22 and
lists the same files once per repo.

Two consequences:

- The gate prints `manifest entries 10242` as though it were a measure of evidence volume. It
  is a measure of how many worktrees happen to be registered.
- A reviewer told "every file is listed with its sha so you can diff it" opens the manifest and
  finds the same line 22 times. The packager's whole argument is checkability.

**Fixed.** `dedupe_by_artifact_root` in `package-evidence.py` keeps one path per resolved
artifact root — the artifact root is the unit of evidence, so walking it twice can only
duplicate — and prints what it collapsed rather than dropping paths silently. Rebuilt: 10
completed, 12 discarded, 498 manifest entries, 21 duplicate paths named in the output.

## Smaller defects, not blockers

- **Step attribution sticks on the first node.** In `AN-3641`'s trace, the edge records for
  `project-context.json`, `summary.md` and `outcome.json` all carry `step: triage`:
  `.current-step` is not rewritten per step, so `project-memory`, `brief` and `report` produce
  no step record of their own. They are scripts, so nothing is uncertified by it, but the
  per-step token and model tables in the report are attributing their cost to `triage`.
- **The spurious failed edge** on seven of nine runs (item above). Writing the sentinel before
  the artifact, or having the hook wait for it, would clear the record. As it stands every clean
  run carries a failed edge a reviewer has to be talked out of.

## Verdict

The gate passes, the evidence is honest, and the one defect that mattered — a package claiming
220 runs when there were 10 — is fixed. The bug/task objection I raised first was the weaker
point and Calvin was right to push on it.

Submittable once the fixed packager is merged and the package is rebuilt. More `feature` runs
would strengthen the standard path and are worth doing, but they do not gate this.
