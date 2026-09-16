## 0. Verify assumptions

- [x] 0.1 Capture real SubagentStop and Stop hook payloads from the installed Claude Code version; confirm which transcript path fields exist and the `usage` field names in subagent transcripts; record findings in `design.md` D5 (verified from the 2.1.209 input schema plus real transcripts: `agent_transcript_path` present; usage must be de-duplicated by `message.id`)
- [x] 0.2 Confirm Claude Code's Bash tool runs without a TTY (so `decide.py`'s TTY check blocks agents) and record the check used (no TTY by default, but `script` and Python `pty` fake one, so decisions now require a human-presence signature; see D6)
- [x] 0.3 Fill `pricing.yaml` from Anthropic's published pricing page with `source` and `as_of`; no remembered numbers
- [x] 0.4 Live payload capture: confirmed 2026-09-16 — a real `SubagentStop` carried `agent_id`, `agent_type`, `agent_transcript_path`, `stop_hook_active` and `last_assistant_message`, matching the 2.1.209 schema; `SubagentStart` fires too
- [ ] 0.5 Choose the human-presence signing key (FIDO `ed25519-sk` or Secure Enclave with Touch ID), and confirm `ssh-keygen -Y sign` prompts for presence on each signature on both Macs

## 1. Config and templates

- [ ] 1.1 Create `templates/delivery-flow/delivery-flow.yaml` (tracker, forge, punch-out policy with triggers, cost budget and external-tracker flag, deploy and auto-roll, per-step models, roster overrides, test command, artifact commit policy, vault binding, tracker-write MCP matcher list) with comments
- [ ] 1.2 Create `templates/delivery-flow/roster.yaml` with initial kinds of work (`ux`, `frontend`, `backend`, `contracts`, `infra`, `data`, `mobile`, `docs`) mapped to existing toolkit agents and skills only
- [x] 1.3 Create `templates/delivery-flow/pricing.yaml` (from 0.3)
- [ ] 1.4 Write a shared `scripts/delivery-flow/common.py`: git-root discovery, `.delivery-flow.yaml` detection (the inert-outside rule), config and roster loading with wholesale per-key override

## 2. Adapters

- [ ] 2.1 `scripts/delivery-flow/adapters/github_issues.py`: `fetch`, `comment`, `transition`, `related` via `gh`; exit codes 0/2/3; normalized item JSON
- [ ] 2.2 `scripts/delivery-flow/adapters/github_pr.py`: `open-pr`, `ci-status` via `gh`
- [ ] 2.3 `scripts/delivery-flow/adapters/local_markdown.py`: `fetch`, `comment`, `transition`, `related`, `import` (new file only)
- [ ] 2.4 Open-punch-out refusal inside `open-pr`, `comment` and `transition` (shared helper in `common.py`)
- [ ] 2.5 Adapter fixture tests: normalized output, determinism (byte-identical reruns), auth-failure exit 3, refusal while a punch-out is open, import against a copy of the Olympus feature backlog

## 3. Validators

- [ ] 3.1 `scripts/delivery-flow/validate-artifact.py` kinds: `item`, `triage`, `spec-ready`, `challenge`, `implementation`, `verify`, `pr`, `posted`, `outcome`; stdlib only; exit 0/1 with a report
- [ ] 3.2 `implementation` kind cross-checks traced Skill tool calls against the story's dispatch plan
- [ ] 3.3 Manual-correction detection: compare a file's current sha to its trace record
- [ ] 3.4 Fixture tests per kind (valid and invalid)

## 4. Work-type routing

- [ ] 4.1 Add optional `Domains:` to `skills/spec-driven-development/references/story-schema.md` and `--require-domains` plus duplicate-label checks to `scripts/lint-story.py`, in the same commit; existing lint fixtures stay green
- [ ] 4.2 `scripts/delivery-flow/resolve-roster.py`: label validation and JSON dispatch plan
- [ ] 4.3 Update `agents/story-planner.md`: propose `Domains:` from evidence, cite it in Dev Notes, when invoked under delivery-flow
- [ ] 4.4 Update `agents/sdlc-orchestrator.md` and `skills/sdlc-orchestration/SKILL.md`: when stories carry `Domains:`, dispatch the architect, reviewers and skill injection from `resolve-roster.py`; attended behavior otherwise unchanged
- [ ] 4.5 Tests for `resolve-roster.py`: unknown label, multi-domain union, override replacement
- [ ] 4.6 Support `tasks.md` group-heading domains (`<!-- domains: … -->`) for quick-path items without story files, with tests

## 5. The delivery-flow skill

- [ ] 5.1 `skills/delivery-flow/SKILL.md`: routing table, one-step rule, `--status` / `--step`, item-type branching, bounded reruns, mandatory challenge points, outcome recording, `.current-step` writes before each delegation
- [ ] 5.2 References: `references/config.md`, `references/adapters.md` (contract plus how to add Jira/GitLab/Bitbucket), `references/roster.md`, `references/trace.md`
- [ ] 5.3 Triage prompt section with the ambiguity-hands-off-to-a-human rule, and the `triage.md` output format matching the validator

## 6. Audit trail

- [ ] 6.1 `hooks/trace-step.py`: SubagentStop per-step records from `agent_transcript_path`, usage de-duplicated by `message.id`, 5m and 1h cache writes priced separately (per-model split), Stop orchestrator delta, `trace_error` on lookup failure, inert outside delivery-flow repos
- [ ] 6.2 Register the SubagentStop and Stop hooks in `hooks/hooks.json`
- [ ] 6.3 `scripts/delivery-flow/delivery-report.py`: per-item, per-step and per-model tables labeling cost as API-equivalent at list prices, weekly end-to-end and punch-out rates, pricing `as_of`, Markdown and CSV
- [ ] 6.3a `delivery-report.py backfill`: historical per-session usage from `~/.claude/projects/*/*.jsonl` labeled `source: backfill`, excluded from end-to-end rates; reads committed traces from repo git history so both Macs' runs aggregate
- [ ] 6.4 Tests: synthetic transcripts → expected trace lines; report math (the 4/1/2 → 80% scenario); non-delivery repo creates no file

## 7. Decision-point enforcement

- [ ] 7.1 `scripts/delivery-flow/check-punch-out.py`: deterministic triggers (triage handoff, architecture/breaking/contract-path changes, REFUTED twice, retry limit and cost budget from trace, protected paths, external tracker post); writes `punch-out-<n>.md`; fixture tests per trigger, plus a no-trigger case that must not stop
- [ ] 7.2 `scripts/delivery-flow/decide.py`: hash-bound decision file signed with `ssh-keygen -Y sign -n delivery-flow-decision` using a human-presence key; a shared verifier (`ssh-keygen -Y verify` against `allowed_signers`) used by the hook and adapters; optional TTY prompt as convenience only
- [ ] 7.3 `hooks/enforce-punch-outs.py`: write protection on `decisions/` and punch-out files (tools and Bash), continuation blocking while a punch-out is open, always-deny merge actions, deploy check, MCP matcher list, inert outside delivery-flow repos
- [ ] 7.4 Register in `hooks/hooks.json` (PreToolUse matchers for Bash, Write/Edit/MultiEdit/NotebookEdit, Task/Agent, configured MCP tools)
- [ ] 7.5 Unit tests for the hook's decisions from recorded tool-input payloads
- [ ] 7.6 `deploy` rule: configurable deploy action patterns plus the `auto_roll` rule (routine non-breaking bumps skip; API/schema/breaking/first-deploy/exposure do not), with policy-decision trace records; seed defaults from `codex/docs/session-coordination.md`
- [ ] 7.7 `tests/delivery-flow/bypass/`: fixture repo plus one headless `claude -p` scenario per attack in design D6 (continue past a punch-out, open PR or post during a punch-out, merge, deploy a breaking change, write or clear decisions and punch-outs, invoke `decide.py` directly and inside a faked terminal, sign with a key readable on disk, edit after deciding, suppress a trigger); writes `bypass-report.md`; non-zero on any breach
- [ ] 7.8 Confirm no fixed human checkpoint remains: a fixture item with no triggers runs from intake to an open PR and ticket update with zero stops

## 8. Evals

- [ ] 8.1 `evals/delivery-flow-routing/`: directory-state fixtures covering bug/feature/task, recall skipped, validation rerun, REFUTED rerun, each decision-point stop; deterministic JS asserts on `{next_step, decision_point_stop, branch}`; keyless Agent SDK provider
- [ ] 8.2 `evals/work-type-classifier/`: labeled story plus manifest fixtures (seeded from Olympus answer 8.3 when available); exact-set asserts; 95% bar
- [ ] 8.3 Run both suites on the target models and commit the results JSON

## 8b. Stage 3 certification and model tiering

- [ ] 8b.1 Create `skills/delivery-flow/steps.yaml` with one entry per task prompt on the pilot path (`backend`, `contracts`, `ux`); mark every other roster agent `certified: false`
- [ ] 8b.2 Write `scripts/delivery-flow/check-certification.py`: ≥3 criteria, ≥95% results, provider tier ≤ Sonnet, prompt sha match, ≥90% load-bearing appendix, iteration log ≥2 complete entries, escalation evidence above Sonnet; fixture tests for each failure
- [ ] 8b.3 Wire certification into the flow (pre-step check, `allow_uncertified`, `certified` trace field) and the report (certified-only end-to-end rate)
- [ ] 8b.4 Add `model_conformant` to trace records, report the extra cost of non-conformant records, and add the `--status` session-model warning
- [ ] 8b.5 Pin `agents/adversarial-validator.md` to `model: sonnet` (currently inherits); record escalation evidence if its suite later requires Opus
- [ ] 8b.6 Mine real-work fixtures from Olympus's archived OpenSpec changes (dionysus-planner, hermesmq, artemis-service, apollo-storage, hephaestus-service; exclude `ares-*`, `codex`, `harpocrates-*`, `muses-ui`), anonymizing nothing secret-adjacent
- [ ] 8b.7 Using `prompt-edd`, certify on Haiku first, then Sonnet, each with a baseline, ≥2 iterations, results and a load-bearing appendix: triage, work-type classifier (8.2), delivery-flow routing (8.1), intake digest, post-back summary, `pr-description` (extend its existing suite to ≥3 criteria if needed), delivery recall
- [ ] 8b.8 Certify on Sonnet (execution-grounded asserts for code-writing steps: tests green on a fixture repo): `sdlc-orchestrator`, `requirements-analyst`, `solution-architect`, `story-planner`, `test-writer`, `implementer`, `qa-test-architect`, `adversarial-validator`, and the pilot reviewers (`scala-fp-reviewer`, `frontend-reviewer`, `git-and-ci-reviewer`)
- [ ] 8b.9 For any step failing 95% on Sonnet, commit the Sonnet results as escalation evidence before declaring a higher tier; record the decision in the step's iteration log
- [ ] 8b.10 Run `check-certification.py --all`; every pilot-path step exits 0

## 9. Documentation (doc-sync rule)

- [ ] 9.1 Add a "Delivery flow" section to `docs/using-the-sdlc-dev-team.md`: when to use it, routing table, branching, roster, punch-out policy and bypass evidence, trace and report, remaining risks
- [ ] 9.2 Create `docs/figures/delivery-flow.svg` in the house color language (purple = human decision point, amber = deterministic script, teal = LLM checker, coral = build, red/green = dev pair) and embed it
- [ ] 9.3 Update `agents/README.md`, `skills/prime/` team bindings (read the roster), and `skills/sdlc-orchestration/SKILL.md` mirrors
- [ ] 9.3a Add a playbook subsection on step certification and model tiering (the bar, recertification on prompt change, escalation evidence, the certified-only end-to-end rate)
- [ ] 9.4 Update `CLAUDE.md` consistency rules (including: any agent or task-skill prompt edit requires re-running its suite and updating `steps.yaml`'s `prompt_sha256`): roster ↔ `resolve-roster.py` ↔ `roster.md`; `validate-artifact.py` ↔ the skill's file formats; punch-out hook ↔ `check-punch-out.py` ↔ `decide.py` ↔ adapters' refusal

## 10. Verification

- [ ] 10.1 `openspec validate add-delivery-flow` green; all script, hook and linter test suites green
- [ ] 10.2 Run the bypass suite; commit `bypass-report.md` with every attempt blocked
- [ ] 10.2a Bump `.claude-plugin/plugin.json` version; after merge, confirm the *installed* plugin cache on both Macs contains both hooks and `delivery-flow --status` reports them registered (plugin-cache-lag check)
- [ ] 10.3 Enable in one Olympus repo (suggested: `demeter-service`, the only one with required status checks plus mutation testing) with the local-markdown tracker; run one real item end to end; confirm complete `trace.jsonl` coverage (every step plus orchestrator) and a generated report
