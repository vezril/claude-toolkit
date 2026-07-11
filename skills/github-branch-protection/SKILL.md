---
name: github-branch-protection
description: "Set up branch protection on a specific GitHub repository via a repository ruleset: require a pull request before merging into the default branch (zero required approvals, solo-friendly), and block force-pushes and branch deletion. Takes the repo as parameter (bare name defaults to owner vezril; or owner/name; or derived from the current directory's origin). Idempotent — detects an existing ruleset and reports instead of duplicating. Use when a repo's main branch should only change through PRs."
argument-hint: "[owner/]repo  (omit to use the current directory's origin)"
license: MIT
---

# Branch protection (protect-main ruleset)

Apply the standard `protect-main` repository ruleset to one repo. Rulesets are the modern
mechanism — the classic `branches/<name>/protection` API is legacy; do not use it here.

The standard rules, deliberately minimal for a solo maintainer:

- **pull_request** — every change to the default branch goes through a PR; `0` required
  approvals so the owner can merge their own PRs; all merge methods allowed.
- **non_fast_forward** — no force-pushes (history on the default branch is immutable).
- **deletion** — the default branch cannot be deleted.
- **No bypass actors** — the rules bind the owner too. Direct `git push origin main` will be
  rejected; that is the point. Mention this in the report.

## Step 1 — resolve the repo

From the arguments: `owner/name` as given; a bare `name` means `vezril/<name>`. With no
argument, derive from `git remote get-url origin` in the current directory. If none of those
work, ask.

Preflight: `gh repo view <owner>/<name>` must succeed. **The default branch must exist** (at
least one commit) — on a truly empty repo the require-PR rule would block the initial push and
lock the repo. If `gh api repos/<owner>/<name>/branches` is empty, STOP and say to seed the
default branch first (the github-new-repo skill does this).

## Step 2 — idempotency check

`gh api repos/<owner>/<name>/rulesets` — if a ruleset named `protect-main` already exists,
report its id and current rules and stop. Also run
`gh api repos/<owner>/<name>/rules/branches/<default-branch>` and surface any other active
rules so the human knows the full effective picture.

## Step 3 — create the ruleset

```
gh api -X POST repos/<owner>/<name>/rulesets --input - <<'EOF'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["merge", "squash", "rebase"]
      }
    }
  ]
}
EOF
```

## Plan restriction (private repos on the free plan)

GitHub's free plan does not allow branch protection on **private** repos — the rulesets
API (and the legacy protection API alike) returns **HTTP 403** with an "Upgrade to GitHub
Pro or make this repository public" message. This is an account-plan limit, not a failure
of the run:

- Report **loudly**: "Branch protection UNAVAILABLE on this plan for private repos — the
  repo continues UNPROTECTED. PR discipline is by convention only; direct pushes to
  <default-branch> are possible. Re-run this skill after making the repo public or
  upgrading the plan."
- Treat the step as completed-with-warning, not failed: no retry, no fallback to the
  legacy API (same restriction applies), no visibility change on your own initiative.

## Step 4 — verify and report

`gh api repos/<owner>/<name>/rules/branches/<default-branch>` must now list all three rule
types (`deletion`, `non_fast_forward`, `pull_request`). Report the ruleset id, its html link
(`https://github.com/<owner>/<name>/rules/<id>`), and the no-bypass caveat above.

## Guardrails

- Never delete or modify an existing ruleset without being explicitly asked — Step 2 reports
  and stops instead.
- Changing who can do what to a repo is persistent configuration: outside the
  new-github-project workflow (where launching the workflow is the authorization), confirm
  with the human before creating the ruleset.
- If the human wants required checks, review counts, or bypass actors, adjust the JSON to
  their spec — the block above is the default, not a limit.
