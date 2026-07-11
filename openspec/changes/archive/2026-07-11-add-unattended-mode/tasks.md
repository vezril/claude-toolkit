## 1. Policy (skill + agent)

- [x] 1.1 Add an "Unattended mode (trust rung 1)" section to `skills/sdlc-orchestration/SKILL.md`: gate-replacement table, untrusted-input boundary, protected paths, escalation protocol + circuit breaker, explicit non-goals (no auto-merge, no auto-archive, no architecture work)
- [x] 1.2 Update `agents/sdlc-orchestrator.md` with mode awareness: attended default unchanged; unattended resolves gates per policy, treats CONCERNS as FAIL, and escalates (never improvises) on any non-PASS
- [x] 1.3 Update `agents/story-planner.md` and `agents/qa-test-architect.md` only if wording assumes a human is present at their gates (audit; minimal edits)

## 2. Protected-path checker script

- [x] 2.1 Write `scripts/check-protected-paths.py`: reads the policy file's globs, diffs the work branch against base, exits non-zero listing any protected-path violations
- [x] 2.2 Test it against fixtures (clean diff passes; CI-file, policy-file, hook, and prompt-template touches each fail) and document exit-code semantics in the script header

## 3. Reference templates

- [x] 3.1 Create `templates/unattended/unattended-policy.yml`: author allowlist, protected-path globs (CI workflows, policy file, hooks/, scripts/, release/deploy scripts, prompt templates), budget caps, circuit-breaker settings
- [x] 3.2 Create `templates/unattended/claude-auto.yml` (GitHub Actions): label trigger + guards (allowlist, concurrency group, budget stamp, circuit-breaker check), phase-per-job `claude -p` invocations on the `claude-auto/<issue>-<slug>` branch with artifact commits between jobs, validator steps (`lint-story.py`, `openspec validate`), protected-path check in verify
- [x] 3.3 Add the independent-review job to the template: different model, refute-framed prompt, verdict reported as a commit status suitable for required checks
- [x] 3.4 Add PR-creation and audit-trail steps: green path opens the evidence-bearing PR and comments the issue (PR link first line); every escalation path posts findings + applies `needs-human`
- [x] 3.5 Create `templates/unattended/issue-form.yml`: GitHub issue form making intake fields (symptom, repro, scope hints) deterministic
- [x] 3.6 Write `templates/unattended/README.md`: copy-into-repo instructions (secret, branch protection + required checks, label creation, policy tuning), rung-1 expectations, re-arming the circuit breaker

## 4. Documentation (doc-sync rule)

- [x] 4.1 Add an "Unattended mode" section to `docs/using-the-sdlc-dev-team.md`: when to use it, the gate-replacement table, the escalation model (human as exception handler), setup pointer to the templates
- [x] 4.2 Create `docs/figures/human-gates-unattended.svg` (rung-1 variant of human-gates: purple pills replaced by amber/teal except the final merge) and embed it in the new section
- [x] 4.3 Update `agents/README.md` (orchestrator entry) and `CLAUDE.md` (templates + checker script become mirror/paired files under the consistency rules)

## 5. Verification

- [x] 5.1 Run the protected-path checker fixture suite and `openspec validate --change add-unattended-mode`; both green
- [x] 5.2 Validate `claude-auto.yml` mechanically (YAML parse + `actionlint` if available) and walk one simulated run: green path to PR text, and one forced gate failure to the escalation comment + `needs-human`
