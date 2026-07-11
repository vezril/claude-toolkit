# Unattended mode (trust rung 1) — setup

Reference templates for running the claude-toolkit SDLC pipeline unattended from a labeled
GitHub issue: the run ends at an **open PR with evidence; merging stays human**. Policy and
rationale: `skills/sdlc-orchestration/SKILL.md` → "Unattended mode (trust rung 1)".

## Files

| Template | Copy to (target repo) |
|----------|----------------------|
| `unattended-policy.yml` | `.claude/unattended-policy.yml` |
| `claude-auto.yml` | `.github/workflows/claude-auto.yml` |
| `issue-form.yml` | `.github/ISSUE_TEMPLATE/claude-auto-bug.yml` |

## Setup (per target repo)

1. **Secret** — add `ANTHROPIC_API_KEY` (repo → Settings → Secrets → Actions). Unattended runs
   are API-billed; set a spend alert on the key.
2. **Policy** — copy `unattended-policy.yml`, set your `author_allowlist` and adjust the
   `protected_paths` globs (release scripts, prompt templates, anything the pipeline must never
   touch). This file is itself protected.
3. **Labels** — create `claude-auto` (the opt-in trigger) and `needs-human` (the escalation marker).
4. **Branch protection** — require a PR into the default branch and add
   **`claude-auto/review`** as a required status check (the independent reviewer's verdict);
   this makes even the human merge gated on the refuting review. (The
   `github-branch-protection` skill can set the ruleset up.)
5. **Workflow** — copy `claude-auto.yml`, then work through every `ADJUST` marker: models,
   toolchain setup, and — **required** — the real test command in the `verify` job (the template
   fails closed until you wire it).
6. **Issue form** (optional but recommended) — copy `issue-form.yml` so intake fields are
   deterministic.

## Operating it

- **Trigger**: file the issue, then apply the `claude-auto` label (allowlisted authors only —
  the label is the "worth planning?" gate). One run at a time per repo.
- **Green path**: PR opens with the evidence (change artifacts, test results, review verdict);
  the issue gets a comment with the PR link on the first line. You merge. `openspec archive`
  for the change remains your close-out.
- **Escalation**: any gate failure, budget breach, out-of-scope classification (architecture or
  prompt-side work), or protected-path violation posts findings on the issue, applies
  `needs-human`, and stops. Watch the escalation rate — it is the data that justifies (or
  forbids) trust rung 2 (auto-merge), which these templates deliberately do not implement.
- **Circuit breaker**: if the last 3 processed `claude-auto` issues all escalated, the guard job
  refuses new runs. **Re-arm** by resolving one of those issues properly: handle it and remove
  its `needs-human` label (or close it as resolved) so the last-3 window is no longer all
  escalations.

## Security notes

- Issue text is treated as **data** (snapshotted to `.claude-auto/issue.json`, never interpolated
  into prompt strings); instructions embedded in issues are ignored and noted in the audit trail.
- The builder cannot approve itself: the reviewer runs as a separate job, on a different model,
  prompted to refute, reported as a required check.
- `--dangerously-skip-permissions` is scoped to an ephemeral CI runner; blast radius is capped by
  job permissions, the protected-path check, and the PR-not-merge ceiling.
