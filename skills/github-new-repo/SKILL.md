---
name: github-new-repo
description: "Create a brand-new, empty GitHub repository under the configured owner (vezril) and seed its main branch with an empty initial commit. Requires two parameters: the repo name and the visibility (public or private). Use when starting a new project from nothing and only the remote repo + local git checkout are needed — no scaffolding, no docs (see repo-starter-docs), no branch protection (see github-branch-protection). First step of the new-github-project workflow."
argument-hint: <repo-name> <public|private>
license: MIT
---

# New empty GitHub repo

Create the remote repository, initialize the local checkout, and seed `main` with one **empty**
commit. The repo ends up "empty" in the useful sense (zero files) but with `main` existing —
without that seed commit, branch protection would block the first push outright and no PR could
ever be opened against the repo (a PR needs a base branch).

Fixed conventions (don't ask): GitHub owner `vezril`, default branch `main`, gh CLI for all
GitHub calls.

## Parameters

Both come from the arguments; if either is missing, ask for it and stop.

- `NAME` — the repository name. Must match `[a-z0-9][a-z0-9._-]*` (lowercase). If it doesn't,
  propose the lowercased/sanitized form and confirm.
- `VISIBILITY` — literally `public` or `private`. No default: the human must choose.

## Step 1 — preflight

- `gh auth status` succeeds and is logged in as `vezril`.
- The repo must NOT already exist: `gh repo view vezril/<NAME>` must fail. If it exists, STOP
  and report — never reuse or overwrite an existing repo.
- Decide the local directory:
  - If the current directory is a freshly created, **empty** directory named `<NAME>` (the
    workflow case), use it.
  - Otherwise use `~/Code/<NAME>`, which must not already exist; create it.

## Step 2 — confirm (outward-facing)

Creating a repo is publishing. Unless the human already authorized this run (they invoked the
new-github-project workflow with these exact parameters, or explicitly pre-approved in
conversation), confirm first:

> About to create **github.com/vezril/&lt;NAME&gt;** (visibility: **&lt;VISIBILITY&gt;**) and push an empty
> initial commit to `main`. Proceed?

## Step 3 — create and seed

From the local directory:

```
git init -b main
git commit --allow-empty -m "Initial commit"
gh repo create vezril/<NAME> --<VISIBILITY> --source . --remote origin
git push -u origin main
```

(End the commit body with the standard `Co-Authored-By` line for the current model.)

## Step 4 — verify and report

- `gh repo view vezril/<NAME> --json visibility,defaultBranchRef` shows the requested visibility
  and `main` as default branch.
- Report: local path, repo URL, visibility, and that `main` holds exactly one empty commit.

## Guardrails

- Never run `git add` here — the repo is intentionally file-less at this stage.
- If any step after `gh repo create` fails, report the partial state honestly (remote exists,
  push failed) rather than retrying destructively; the fix is usually a plain re-push.
- Private-vs-public is the human's call. Never silently default.
