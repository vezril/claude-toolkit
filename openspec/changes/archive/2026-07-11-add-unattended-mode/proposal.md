## Why

The SDLC team currently requires a human at every gate (4 + N approvals per feature), which makes it unusable for fire-and-forget work: filing a GitHub issue and having the pipeline spec, build, test, and deliver a PR without supervision. The pipeline is already structurally ready — deterministic validators (`lint-story.py`, `openspec validate`), execution-grounded QA, artifact-driven state that maps 1:1 onto CI jobs — but there is no defined policy for what replaces each human gate, no trigger mechanism, and no guardrails against the risks unattended operation introduces (prompt injection via issue text, self-approval, runaway cost).

## What Changes

- Add an **unattended mode** (autonomy policy) to the SDLC pipeline: each human gate gets a defined mechanical replacement (deterministic check, separate-model refuting reviewer, or policy rule), with every failure path converging on a clean `needs-human` escalation instead of a stall or a guess.
- Scope autonomy to **trust rung 1**: the pipeline ends by opening a PR with full evidence; **merge remains human**. `openspec archive` likewise remains a human close-out. (Auto-merge is explicitly out of scope for this change.)
- Add a **reference GitHub Actions workflow template** that turns a labeled issue into an unattended pipeline run: trigger guards (author allowlist, label opt-in, concurrency lock, budget caps), one job per phase with artifacts committed to the work branch between jobs, and an issue-comment audit trail.
- Add an **unattended safety policy**: issue text is data (never pipeline instructions), protected paths the unattended pipeline may never modify (CI config, the policy itself, hooks/validators, release scripts, prompt templates), bounded iterations, and a circuit breaker after repeated escalations.
- Update the `sdlc-orchestrator` agent and `sdlc-orchestration` skill to recognize the mode; update the playbook, figures, and mirror files per the CLAUDE.md doc-sync rule (the human-gates figure gains an unattended variant).

## Capabilities

### New Capabilities
- `unattended-sdlc-policy`: the autonomy policy — gate-by-gate replacement of human approvals, trust-rung scoping (rung 1: auto-PR, human merge), escalation protocol (`needs-human`), safety rules (untrusted-input handling, protected paths, budgets, circuit breaker).
- `unattended-trigger-workflow`: the reference GitHub Actions workflow — issue-label trigger with guards, phase-per-job execution with artifact handoff via the work branch, PR creation with evidence, and the issue-comment audit trail.

### Modified Capabilities

<!-- none — existing specs cover project scaffolding, not the SDLC pipeline; the pipeline's attended behavior is unchanged -->

## Impact

- `skills/sdlc-orchestration/SKILL.md` — new unattended-mode section (policy, gate table, escalation).
- `agents/sdlc-orchestrator.md` — mode awareness: attended (default, unchanged) vs unattended (gates resolve per policy; every non-PASS → escalate, never improvise).
- New reference template(s): the GitHub Actions workflow + protected-paths policy file, shipped in the plugin for users to copy into target repos.
- Docs per the doc-sync rule: `docs/using-the-sdlc-dev-team.md`, `docs/figures/` (unattended variant of `human-gates`), `agents/README.md`, `CLAUDE.md` consistency rules if new paired files are introduced.
- No breaking changes: attended mode stays the default; unattended is opt-in per issue via label.
- Operational dependencies (documented, not shipped): `ANTHROPIC_API_KEY` secret in the target repo, branch protection requiring PR + status checks.
