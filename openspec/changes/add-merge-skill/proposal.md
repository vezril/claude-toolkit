# Proposal: add-merge-skill

## Why

The end-of-change train — merge the gated PR, tag the release, archive the OpenSpec change and land its bookkeeping — is run by hand constantly (a dozen times in one working day building this toolkit), each time as three-to-five separate confirmations. One skill, one explicit invocation, one authorization for the whole train.

## What Changes

- New skill **`merge`**: runs the train **merge → tag vX.Y.Z → openspec archive** for the current repo:
  1. **Merge** — resolve the PR (argument, or the current branch's open PR), require green/complete checks, merge, verify `MERGED`, sync local `main`.
  2. **Tag** — version from the argument (`vX.Y.Z` or `major|minor|patch` bump), else propose the next patch bump over the latest `v*` tag and ask; tag merged `main` and push (fires release.yml where the repo has one). Skippable on request; never silently invented.
  3. **Archive** — if a completed OpenSpec change corresponds to the merged work, `openspec archive`, commit the bookkeeping, and land it (PR + merge under the train's standing authorization when the repo requires PRs; direct push otherwise).
- **Authorization model:** invoking `/merge` IS the human authorization for every merge the train performs (the target PR and the archive-bookkeeping PR) — that is the skill's whole point. Anything ambiguous (failing checks, multiple candidate PRs/changes, no version given) still stops and asks.

## Capabilities

### New Capabilities
- `merge-train`: the merge → tag → archive train, its authorization model, and its stop conditions.

### Modified Capabilities
<!-- none -->

## Impact

- New `skills/merge/SKILL.md`; README index (Toolkit maintenance group). No changes to git-ship (the pre-merge half of shipping) or the opsx skills (archive internals) — the train composes them.
