# Design: add-merge-skill

## The train

```
/merge [pr#|url] [vX.Y.Z | major|minor|patch] [--no-tag] [--no-archive]

MERGE   resolve PR (arg → else current branch's open PR → else ask)
        gate: all checks green or none required; NEVER merge red/pending-required
        gh pr merge --merge → verify MERGED → checkout main + pull
TAG     version: arg verbatim | bump over latest v* tag | propose next patch + ask
        annotated? no — lightweight vX.Y.Z on merged main; push tag
        (fires release.yml in repos scaffolded by the flavors; report the run link)
ARCHIVE candidate = the single completed OpenSpec change whose tasks are all [x]
        (or named in conversation); 0 candidates → skip with note; >1 → ask
        openspec archive <name> -y → commit bookkeeping →
        repo requires PRs? PR + merge (train authorization) : push to main
REPORT  merge SHA · tag + release run · archive location · what was skipped
```

## Decisions

**One invocation = one authorization, loudly documented.** The skill exists to collapse
the train's confirmations; `/merge` therefore authorizes both merges it may perform (the
target PR and the archive bookkeeping). This is stated in the skill body AND the report
lists every merge performed. Everything else stops: red checks are never overridden, a
missing version is asked (tags are permanent, no silent invention), multiple candidate
PRs/changes are disambiguated by the human.

**Checks gate is absolute.** Pending required checks → wait briefly (`gh pr checks
--watch` bounded) or stop and say so; failing checks → stop, report which, never merge.
Repos without required checks merge immediately (the toolkit's own protect-main shape).

**Tag is step 2, optional by instruction only.** `--no-tag` (or "don't tag" in
conversation) skips it; absence of a `v*` history means the proposal is `v0.1.0`. The tag
goes on the merge commit on `main` — never on the feature branch — matching release.yml's
tag-on-main ancestry gate.

**Archive reuses the existing machinery.** The skill does not reimplement /opsx:archive's
delta-spec sync; it runs `openspec archive <name> -y` (the CLI handles promotion) and
ships the bookkeeping. Incomplete tasks in the candidate → stop and hand off to
/opsx:archive's interactive flow instead (that flow owns the skip-with-warning decision).

**Composition, not duplication.** git-ship owns getting changes TO the gate; merge owns
the gate onward. The two together are the full lifecycle of a change.

## Risks

- Standing authorization is broad by design; the mitigations are the absolute checks gate,
  the ask-on-ambiguity rule, and the explicit per-merge report.
- Tag pushes are effectively irreversible on repos with immutable-semver release gates —
  hence version-by-explicit-choice only.
