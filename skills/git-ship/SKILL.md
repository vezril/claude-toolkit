---
name: git-ship
description: "Ship the working tree's changes: commit on a feature branch, push, create the PR, and merge — with the merge gated on explicit human authorization. Auto mode (merge without asking) only when the human explicitly said so for this run (the literal argument auto, or an unambiguous statement in conversation). Use when changes are ready to land on the default branch of a repo that requires PRs, e.g. as the final step of the new-github-project workflow."
argument-hint: "[auto] [branch-name or commit-message hint]"
license: MIT
---

# Ship it (commit → PR → merge)

Land the current working tree's changes on the default branch through a PR. The merge is the
irreversible step, so it is gated: **ask the human, unless they explicitly enabled auto mode
for this run.** "The workflow usually runs in auto" or a past approval does NOT carry over.

## Mode

- **Gated (default)** — do everything up to and including PR creation, then stop and ask:
  "Merge PR #N?" Only merge on a clear yes.
- **Auto** — merge without asking. Active only if the arguments contain the literal word
  `auto`, or the human explicitly authorized unattended merging for this run in conversation.
  When running inside a workflow, auto is active only if the workflow was invoked with
  `auto: true`.

## Step 1 — survey

- `git status` — if the tree is clean and nothing is staged, STOP: nothing to ship.
- Review what changed (`git diff`, `git status`) so the commit message and PR body describe
  reality. List any unexpected files (build artifacts, secrets, `.env`) and leave them out.

## Step 2 — branch

If on the default branch (`main`/`master`), create a feature branch first — protected repos
reject direct pushes anyway. Name it from the change (e.g. `docs/starter-docs`,
`feat/<topic>`), or use the branch name given in the arguments. If already on a feature
branch, stay on it.

## Step 3 — commit and push

- Stage the reviewed files **explicitly by path**. Blanket `git add -A` is allowed only in a
  freshly scaffolded repo where every file was just created deliberately.
- Commit with a message that says what and why; end the body with the standard
  `Co-Authored-By` line for the current model.
- `git push -u origin <branch>`.

## Step 4 — pull request

`gh pr create` with a real title and a body containing a short Summary and a Verification
note (what was checked, or "not verified" — honestly). End the body with the standard
"Generated with Claude Code" line.

## Step 5 — merge (the gate)

- **Gated mode:** report the PR URL and the diff summary, ask for authorization, and wait.
  Inside a workflow (no human available mid-run), return the PR URL with
  `pendingApproval: true` instead of asking — the outer conversation owns the gate.
- **Auto mode:** `gh pr merge <N> --merge`.

After merging (either mode): verify with `gh pr view <N> --json state,mergeCommit` that the
state is `MERGED`, then sync the local default branch (`git checkout main && git pull`).
Keep the remote feature branch unless asked to delete it.

## Step 6 — report

PR URL, merged-or-pending, merge commit SHA if merged, and anything deliberately left
unstaged.

## Guardrails

- The merge gate is the whole point of this skill: when in doubt about whether auto was
  authorized, it wasn't — ask.
- Never force-push, never merge with failing required checks, never bypass a ruleset.
- If the push or merge is rejected by branch protection, report the rule that fired rather
  than working around it.
- Report failures honestly (tests not run, checks pending) — no "should work".
