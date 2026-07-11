## Context

The SDLC pipeline (claude-toolkit) is human-gated by design: 4 + N approvals per feature, "agents propose, humans dispose". Its structure is already CI-friendly — fresh context per workflow ≡ one CI job per phase; artifacts drive state ≡ commits on the work branch between jobs; two deterministic validators (`scripts/lint-story.py`, `openspec validate`) plus an execution-grounded QA gate already exist as machine-checkable steps. What's missing for unattended operation is (a) a defined replacement for each human gate, (b) a trigger mechanism from a GitHub issue, and (c) safety guardrails for running an agent with commit rights on untrusted input.

Stakeholders: Calvin (sole operator/approver today), any future user of the public plugin who copies the reference workflow.

## Goals / Non-Goals

**Goals:**
- Trust rung 1: a labeled GitHub issue produces, unattended, a PR with full evidence (spec → change artifacts → code + tests → independent review). One human action remains: merging.
- Every unattended failure path converges on a clean, visible escalation (`needs-human` label + issue comment) — never a stall, never an improvised decision.
- Attended mode is untouched and remains the default.
- The workflow template is generic enough to copy into any repo that has the plugin, an `ANTHROPIC_API_KEY` secret, and branch protection.

**Non-Goals:**
- Auto-merge (trust rung 2+) — explicitly out of scope; revisit with data from rung 1.
- Automating `openspec archive` — stays a human close-out.
- Architecture-changing work running unattended — the policy routes standard/enterprise-track work to `needs-human` at triage.
- A self-hosted webhook daemon — GitHub Actions is the only supported trigger in this change.
- Work-toolkit (JIRA/Bitbucket) integration — this is the GitHub-native flow only.

## Decisions

1. **GitHub Actions as trigger, not a webhook daemon.** `on: issues: types: [labeled]` with a label opt-in (`claude-auto`). Rationale: GitHub is already the webhook receiver; no infra to run or secure. Alternative considered: self-hosted daemon (more control, long runs) — rejected for rung 1 as unnecessary infrastructure; the 6h/job runner limit is acceptable for quick-track work.
2. **One CI job per pipeline phase, artifacts committed between jobs.** Each job is a fresh `claude -p` invocation on the work branch (`claude-auto/<issue>-<slug>`); the branch is the state carrier. Rationale: this is the pipeline's own fresh-context discipline, enforced by the runner; failed jobs resume from disk. Alternative: one long session for everything — rejected (context pollution, no resumability, violates the pipeline's operating principles).
3. **Gate replacements, per the trust-rung-1 policy:**
   - *Worth planning?* → trigger policy (label + author allowlist + quick-track triage; anything larger escalates).
   - *PRD approval* → skipped on quick track (lightweight spec instead), spec sanity-checked by the validator model.
   - *Architecture approval* → not replaced; out of scope for unattended runs (escalate).
   - *Readiness* → `lint-story.py` + `openspec validate` (hard exits) + separate-model review where CONCERNS = FAIL.
   - *Per-story merge* → full suite green + coverage vs the P0/P1 map + refuting reviewer PASS; result is a PR, not a merge.
4. **Independent reviewer as a separate job on a different model, prompted to refute.** Its verdict lands as a required status check so the merge button is gated by branch protection even for the human. Rationale: prevents self-approval collusion structurally, not by convention.
5. **Issue text is data, never instructions.** The pipeline derives a spec *from* the issue; pipeline policy lives only in repo files (workflow YAML, policy file, CLAUDE.md) which are protected paths. Rationale: the issue is the injection surface; the derivation boundary is the mitigation.
6. **Protected paths as a policy file** (e.g. `.claude/unattended-policy.yml` in the target repo): globs the unattended run may never modify — CI workflows, the policy file itself, hooks/validators, release/deploy scripts, prompt templates. Enforced by instruction *and* checked deterministically in the verify job (diff inspection); a violation fails the run. Rationale: mirror of the dev-pair hook pattern — charter plus mechanism.
7. **Escalation protocol:** any gate failure, budget breach, bounded-loop exhaustion (~3), or out-of-scope classification → comment findings on the issue, apply `needs-human`, stop cleanly. Circuit breaker: 3 consecutive escalated runs disable the trigger (workflow checks a marker) until manually re-armed. Rationale: the human becomes exception handler; the escalation rate is the metric that justifies rung 2.
8. **Ship as reference templates in the plugin** (`templates/unattended/`) rather than live workflow files in claude-toolkit itself. Rationale: the toolkit is a plugin consumed by many repos; each target repo copies and adapts. Avoids the toolkit's own CI running unattended builds by accident.

## Risks / Trade-offs

- [Prompt injection via issue body/comments] → author allowlist on the trigger; issue-as-data boundary (Decision 5); protected paths; secrets never echoed into comments; PR-not-merge ceiling caps blast radius.
- [Self-approval collusion between builder and reviewer] → separate job, different model, refute-framing, required status check (Decision 4).
- [Runaway cost/loops] → per-run budget caps (wall-clock + iteration bounds), circuit breaker (Decision 7); GitHub Actions concurrency group serializes runs per repo.
- [Quick-track misclassification (feature disguised as bug)] → triage escalates on any architecture/spec-surface touch; diff-size cap in the verify job as a backstop.
- [Headless `claude -p` needs broad permissions] → permissions scoped in the workflow via allowed-tools configuration; the dev-pair boundary hook still applies inside the run; protected-path check is deterministic in verify.
- [Template drift vs pipeline evolution] → the templates become mirror files under the CLAUDE.md doc-sync rule; changing gates without updating templates is flagged as incomplete.
- Trade-off: rung 1 keeps a human click on merge — deliberately trading full autonomy for a data-gathering period on escalation/false-pass rates.

## Migration Plan

Additive, opt-in: ship policy section + templates; nothing activates until a target repo copies the workflow, sets the secret, defines the policy file, and labels an issue. Rollback = remove the label/workflow from the target repo; attended mode is unaffected throughout.

## Open Questions

- Which model pairing for builder vs refuting reviewer (cost vs strength) — decide at template authoring; make it a template variable.
- Should the verify job's protected-path check live in `lint-story.py`-style script form inside the plugin (reusable) or inline in the workflow template? Leaning: small script in `scripts/` for testability.
- Issue template (form) to make intake fields deterministic — worth adding to the reference templates in this change or defer to rung 2?
