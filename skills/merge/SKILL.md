---
name: merge
description: "Run the end-of-change train for the current repo: merge the gated PR, tag the release, archive the completed OpenSpec change and land its bookkeeping — one invocation, one authorization for every merge the train performs. Use when a PR is at the merge gate and the human says merge / run the train / ship it home. Absolute stop conditions: failing required checks are never overridden, versions are never invented, ambiguity (multiple PRs, multiple candidate changes, incomplete tasks) always stops and asks. Composes with git-ship (which gets changes TO the gate; this skill takes them from the gate onward)."
argument-hint: "[pr] [vX.Y.Z | major|minor|patch] [--no-tag] [--no-archive]"
license: MIT
---

# Merge (the train: merge → tag → archive)

Invoking this skill IS the human's authorization for **every merge the train performs** —
the target PR and, if archiving, the bookkeeping PR. That is the skill's whole point:
collapse the train's confirmations into the one explicit act of invoking it. In exchange,
the stop conditions below are absolute, and the final report enumerates each merge made.

## Car 1 — MERGE

1. Resolve the target PR: the argument (number or URL) → else the current branch's single
   open PR → else STOP and ask. More than one candidate → STOP and ask.
2. **Checks gate (absolute):** `gh pr checks <pr>`. All green (or none required) → proceed.
   Pending required checks → `gh pr checks --watch` briefly (≤ ~5 min) or stop and say so.
   **Any failing required check → STOP, name it, never merge, never override.**
3. `gh pr merge <pr> --merge`, then verify: `gh pr view <pr> --json state,mergeCommit`
   must say `MERGED`. Sync: `git checkout main && git pull`.

## Car 2 — TAG (skippable: `--no-tag` or "don't tag")

1. Version: the argument verbatim (`vX.Y.Z`), or a bump word applied to the latest `v*`
   tag (`git tag -l 'v*' --sort=-v:refname | head -1`; `major|minor|patch`). **No argument
   → propose the next patch bump (or `v0.1.0` if the repo has no `v*` history) and WAIT
   for the human's choice. Tags are permanent — never invent a version.**
2. Tag the merge commit on synced `main` — never a feature branch (release workflows
   enforce tag-on-main ancestry): `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. If the repo has a release workflow, report the triggered run's link
   (`gh run list --workflow release.yml --limit 1`).

## Car 3 — ARCHIVE (skippable: `--no-archive`; auto-skips when inapplicable)

1. Candidate: the single active OpenSpec change (`openspec list`) whose tasks are all
   `[x]` and which corresponds to the merged work (or the change named in conversation).
   No candidate → skip with a note. Multiple → STOP and ask.
   **Incomplete tasks in the candidate → STOP and hand off to the interactive
   `/opsx:archive` flow** (it owns the skip-with-warning decision — don't force-archive).
2. `openspec archive <name> -y` (the CLI promotes the delta specs), commit the bookkeeping
   with a message linking the merged PR.
3. Land it: repo requires PRs → push a branch, `gh pr create`, merge it (covered by the
   train's authorization), sync `main`. No protection → push to `main` directly.

## Report

- Every merge performed (PR + SHA, bookkeeping PR + SHA).
- The tag and the release run link (or "tag skipped").
- The archive location (or "no completed change — skipped").
- Anything the train stopped short of, and why.

## Guardrails

- The authorization covers exactly the train's own merges in THIS repo, this invocation —
  nothing else, and never a red or ambiguous merge.
- Never force-push, never tag off-main, never re-tag an existing version (if the tag
  exists → STOP; semver image tags are immutable downstream).
- If any car fails mid-train, report what completed and what didn't — the train is
  resumable by re-invoking (merge and archive are idempotent to re-runs; the tag car
  detects an existing tag).
