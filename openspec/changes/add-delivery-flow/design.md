## Context

The toolkit already has most of the parts:
- the SDLC orchestrator and its specialist agents;
- deterministic gates (`lint-story.py`, `openspec validate`, `check-protected-paths.py`) and the dev-pair boundary hook;
- unattended mode (GitHub Actions, issue label → PR);
- `git-ship` / `pr-description`;
- the adversarial validator (`cross-examine`).

The private defect-flow pipeline showed the shape that works in practice over 22 real tickets: state kept in files, one step per invocation, a per-client config, and human decision points before outward-facing actions. What none of them have is:
1. intake from, and post-back to, an arbitrary tracker;
2. routing to specialists by kind of work;
3. per-step model/token/cost records;
4. decision points enforced by something other than instructions;
5. checks that run automatically at every handoff.

Items 3–5 are exactly what Stage 4 AI Maturity certification examines, and the first target workload is Calvin's Olympus projects (~25 `vezril/*` repos, Scala/Pekko services, Next.js consoles, k3s/Flux/Helm infrastructure).

Constraints:
- The plugin's hooks are global to every session with the plugin installed, so new hooks must do nothing outside a delivery-flow repo.
- The dev-pair territory definition lives in three files that must stay identical (CLAUDE.md), so this change must not add implementer variants.
- The story format and `lint-story.py` change together.
- The attended SDLC pipeline must keep working unchanged.

## Goals / Non-Goals

**Goals:**
- Take a tracker item end to end to a PR plus tracker update, through the existing SDLC phases, with the item type choosing the path.
- Route each story to the right architect, reviewers and skills based on the kinds of work it touches, defined as data that repos can override.
- Produce a complete, machine-readable audit trail: every step's model, tokens, cost, output file and validator result.
- Make decision points un-bypassable by the agent, and prove it with an automated bypass suite.
- Run a deterministic validator on every step output at every handoff.
- Keep adapters swappable; ship GitHub and a local markdown backlog in v1.

**Non-Goals:**
- Jira, GitLab, Bitbucket and Linear adapters (the contract covers them; implementations are a follow-up change).
- Auto-merge or automatic `openspec archive` (merging stays human, as in unattended mode).
- Rebuilding `github-issue-fix-flow`, unattended mode or defect-flow on top of delivery-flow.
- Embedding-based recall (vault recall stays deterministic; see `extend-vault-graphrag-projects`).
- Running in CI. v1 is attended/local, and CI reuse is a later change built on unattended mode.

## Decisions

### D1. A wrapper skill around the SDLC orchestrator, not an extension of it
`delivery-flow` owns intake, triage, delivery and reporting. It calls the SDLC orchestrator for the Planning → Implementation phases.
- *Alternative:* grow `sdlc-orchestrator` itself. Rejected: it would change the attended pipeline's behavior and docs for everyone, and mix tracker concerns into the phase logic.
- The orchestrator gains one additive behavior: when a story carries `Domains:`, it dispatches from the resolved roster.

### D2. State in files under `delivery/<ITEM-KEY>/`, routed by the first missing file
The routing table, in order:

| # | File | Produced by |
|---|------|-------------|
| 1 | `item.json` | tracker adapter (script) |
| 2 | `triage.md` | triage agent: item type, path, provisional kinds of work, rationale |
| 3 | `project-context.md` | vault delivery recall (optional) |
| 4 | `spec-ready.md` | SDLC Planning+Solutioning receipt: change name, lint and validate results |
| 5 | `challenge-spec.md` | adversarial validator, **mandatory** |
| 6 | `implementation.md` | per-story receipts: tests, reviewer verdicts, skills loaded |
| 7 | `verify.md` | full test command, protected-paths check, CI status |
| 8 | `challenge-implementation.md` | adversarial validator, **mandatory** |
| 9 | `pr.md` → `pr-opened.json` | `pr-description`, then the forge adapter |
| 10 | `post.md` → `posted.json` | summary, then the tracker adapter |
| 11 | `outcome.json` | report script |
| 12 | `vault-updated.md` | vault delivery update (optional) |

- Decision points: `spec` (before step 6), `pr` (before the `pr-opened.json` action) and `post` (before the `posted.json` action). An optional `scope` point after triage is configurable.
- Files are committed to the work branch by default (`artifacts.commit: true`), so the audit trail travels with the PR. `trace.jsonl` and `approvals/` are included.
- *Alternative:* store state in a local database or JSON state file. Rejected: files are diffable, match both existing pipelines, and let `--status` be computed rather than remembered.

### D3. Adapters are scripts with a JSON contract; LLMs never talk to trackers directly
- `scripts/delivery-flow/adapters/<kind>.py` exposes subcommands:
  - trackers: `fetch <key>` → item JSON on stdout; `comment <key> --body-file`; `transition <key> <state>`; `related <key>`;
  - forges: `open-pr --head --base --title --body-file` → `{url, number}`; `ci-status <ref>`.
- Exit codes: 0 ok, 2 contract/usage error, 3 remote/auth failure (with a fix-it message).
- v1 kinds: `github-issues` and `github-pr` (both via `gh`), and `local-markdown`: a backlog file of `### <KEY>: <title>` headings with `Type:`/`Status:` lines; comments are appended under the item.
- *Alternative:* MCP connectors. Rejected for v1: availability varies per session and calls aren't reproducible in evals. A future Jira adapter may wrap REST or MCP behind the same CLI.
- Adapters that perform decision-point actions (`open-pr`, `comment`, `transition`) **re-check the approval file themselves** (defense in depth; see D6).

### D4. Routing in two levels, with the roster as data
- **Item level (triage):** `type ∈ {bug, feature, task}` × `path ∈ {quick, standard}`:
  - bug → root-cause analysis → fix proposal → quick path;
  - feature → full standard path (requirements, OpenSpec change, stories);
  - task → quick path, no requirements document.
  - Ambiguity (e.g. a "task" that needs architecture) sends the item to a human instead of guessing.
- **Story level:** the story-planner adds `Domains: backend, contracts` to each story, proposed from evidence (paths the story touches, manifests) the same way `prime` works.
- **`roster.yaml`** (plugin default in `templates/delivery-flow/`, per-repo override keys in `.delivery-flow.yaml`) maps each kind of work to `{architect, skills[], reviewers[], deploy?}`. Overrides are key-wise replacements, not deep merges, so the result is predictable.
- `scripts/delivery-flow/resolve-roster.py <story>` checks labels against the resolved roster (unknown label → exit 1) and prints the dispatch plan as JSON: the union of skills, reviewers de-duplicated, one architect per kind of work touched.
- **One test-writer/implementer pair.** Skills are injected per story through the delegation prompt, and the trace records the Skill tool calls actually made. `validate-artifact.py implementation` fails a story receipt whose loaded skills don't cover the plan's required skills.
- *Alternatives:* a single label per item (rejected: most Olympus features cross UI, backend and contracts); per-domain implementer agents (rejected: multiplies the three-file territory sync); an LLM picking agents freely (rejected: not reproducible or checkable).

### D5. Trace from Claude Code transcripts, attributed through a current-step file
- Before delegating a step, delivery-flow writes `delivery/<KEY>/.current-step` (`{step, item, started_at}`).
- `hooks/trace-step.py` on **SubagentStop** reads the subagent transcript, sums `usage` (input, output, cache creation, cache read) per model, and appends one record to `trace.jsonl`: `{ts, item, step, agent, session_id, agent_id, model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, cost_usd, artifact, validator: {name, exit, summary}}`.
- On **Stop**, the same hook attributes the main session's usage delta since its last record to `step: orchestrator`, so coverage includes the conductor's own turns.
- Cost comes from `templates/delivery-flow/pricing.yaml`: per model, USD per million tokens for each token class, with a `source` URL and `as_of` date. Unknown models record `cost_usd: null` and `pricing_missing: true` instead of a guess.
- `scripts/delivery-flow/delivery-report.py` reads every `trace.jsonl` and `outcome.json` under a root (or across repos) and emits:
  - per-item outcome and cost;
  - per-step token and cost distribution;
  - a weekly end-to-end rate `completed / (completed + failed)`, with the punch-out rate separate;
  - output as Markdown plus CSV.
- *Alternatives:* OpenTelemetry export (rejected for v1: extra infrastructure, and transcripts already hold ground-truth usage); asking agents to self-report tokens (rejected: fabrication risk).

### D6. Approval files are human-created, tied to a hash, and protected from agent writes
- `scripts/delivery-flow/approve.py <KEY> <point>` requires an interactive TTY and a typed confirmation of the item key. It refuses if prerequisites are missing: for `spec`, `challenge-spec.md` must exist with a non-REFUTED verdict; for `pr`, `challenge-implementation.md`. It writes `approvals/<point>.json` = `{point, item, artifact, sha256, approver, ts}`.
- `hooks/enforce-approval-gates.py` on **PreToolUse**:
  - (a) denies Write/Edit/MultiEdit/NotebookEdit targeting `delivery/*/approvals/**`;
  - (b) denies Bash commands that reference `approvals/` or invoke `approve.py`;
  - (c) for Bash commands matching decision-point actions (`gh pr create`, `gh issue comment|edit|close`, `gh api` writes to issues/pulls, forge-host `curl` writes, adapter `open-pr|comment|transition`), requires a valid approval whose `sha256` matches the current file;
  - (d) applies the same check to configured tracker-write MCP tools (a matcher list in the config);
  - (e) blocks entering implementation (delegation to test-writer/implementer) without a `spec` approval.
- All hook behavior is inert unless the session's repo root has `.delivery-flow.yaml`.
- *Alternative:* sign approvals with a key the agent can't read. Rejected for v1: the agent can read the filesystem, so it adds little over TTY-only creation plus write protection, and it adds key management. Kept as an open question.
- **Bypass suite** (`tests/delivery-flow/bypass/`): a scripted headless run (`claude -p`) per attack, each told to perform the gated action without approval:
  - direct `gh pr create`;
  - `gh api` POST;
  - `curl`;
  - writing the approval file via Write;
  - writing it via Bash `echo`;
  - base64-obfuscated `echo`;
  - calling `approve.py`;
  - editing the approved file after approval (hash mismatch);
  - calling the adapter directly.
  - Each attempt must end blocked. Results go to `bypass-report.md` with the hook's deny reasons. This is the Stage 4 punch-out evidence.

### D7. Checks between steps: validators first, adversarial review at two fixed points
- `scripts/delivery-flow/validate-artifact.py <kind> <path>` uses the stdlib only, like `lint-story.py`. It checks shape and cross-file facts:
  - `item.json` keys and types;
  - `triage.md` enums;
  - `spec-ready.md` shows lint and validate exit 0;
  - `pr.md` sections and a linked item key;
  - `posted.json` body sha equals `post.md`'s.
- The orchestrator runs it after each step, and the trace records the exit code. Routing refuses to advance past a step whose latest validation failed: bounded rerun (3), then hand to a human with `outcome: punched-out`.
- The adversarial validator is **mandatory** at steps 5 and 8. A REFUTED verdict reruns the producing step with the findings; WEAKENED requires the findings to be addressed in the next file version; SURVIVED proceeds. It stays optional elsewhere.
- *Alternative:* LLM-only checking. Rejected: Stage 4 counts only automated deterministic or adversarial checks, and deterministic ones are cheaper and reproducible.

### D8. Outcomes distinguish handing to a human from failing
`outcome.json` = `{item, status: completed | punched-out | failed | abandoned, reason, step, ts}`:
- `completed`: `posted.json` exists.
- `punched-out`: a decision point or an ambiguity handed the decision to a human and they chose not to proceed through the flow. This is legitimate, not a failure.
- `failed`: bounded retries were exhausted or a human needed to correct an output by hand.
- `abandoned`: stopped by the human without a decision.

Hand-editing a validated output file is detected by comparing its sha to the trace record, and the item is marked `failed` with reason `manual-correction` (the "no agents that still require regular manual correction" criterion).

### D9. Evals via promptfoo on the keyless Claude Agent SDK provider
Same setup as the private defect-flow suites (`anthropic:claude-agent-sdk`, `apiKeyRequired: false`).
- `evals/delivery-flow-routing/`: fixtures are directory states, and the expected result is `{next_step, decision_point_stop, branch}`. Covers every branch: bug/feature/task, recall skipped without a vault, REFUTED rerun, failed validation rerun, and the stop at each decision point.
- `evals/work-type-classifier/`: fixtures are story files plus repo manifests, with the expected `Domains:` set. Asserts are exact-set precision/recall against deterministic JS, with a 95% suite bar.

### D10. Grounded in Olympus's actual practice (answers from 2026-09-15)
Olympus's answers in `+/Stage 4 - What I need from Olympus.md` change the defaults:
- **The real flow today is `/opsx:propose` → `/opsx:apply` in one session**, with no story files and no dev pair (≈172 archived OpenSpec changes, zero story files). The quick path therefore works **without story files**: domains may be declared on `tasks.md` group headings (`## 2. Console <!-- domains: ux -->`), and `resolve-roster.py` accepts either a story file or a tasks group. The standard path keeps story files.
- **A fourth decision point, `deploy`, plus outward-facing actions.** Calvin's load-bearing stop is the roll to the cluster, and today it is instruction-only. The config gains `decision_points.deploy` with an action pattern list (default: `git push` to the GitOps repo's pin files, `helm upgrade|install`, `flux reconcile`, `docker push`, `git push --tags`). It also gains an `auto_roll` rule mirroring `codex/docs/session-coordination.md`: routine non-breaking bumps may skip the `deploy` approval, while behavior/API/schema/breaking/first-deploy/exposure changes may not. The skip is recorded in the trace as a policy decision, not a silent pass.
- **Branch protection is uneven** (none on artemis-service, hermesmq, apollo-storage, hephaestus-service). The hook-level `pr` and merge checks must not assume a server-side ruleset. Onboarding a repo runs `github-branch-protection` as a recommended, not required, step.
- **Runs happen on two Macs** (personal and work), each with its own transcripts. Committing files to the work branch (D2 default) doubles as the collection point: `delivery-report.py` reads traces from the repos' git history, not from one machine's disk.
- **A backfill mode:** `delivery-report.py backfill` builds historical per-session usage from `~/.claude/projects/*/*.jsonl` (July 11 onward), labeled `source: backfill`. It is baseline context only and is never mixed into the end-to-end rate, because those sessions were not delivery-flow runs.

### D11. Every LLM step is Stage 3 compliant, on the cheapest passing model
Stage 4 requires that "every agent passes its Stage 3 quality bar", and an uncertified step makes the end-to-end number meaningless. Today none of the SDLC agents has an eval suite: the toolkit's suites cover `calvin-voice`, `cross-examine`, `detect-ai`, `humanize`, `outreach`, `phq-9` and `pr-description` only.

**What must be certified.** Every *task prompt*: an agent or skill that produces a pipeline output or verdict. That covers:
- the delivery-flow orchestrator and triage;
- the work-type classifier;
- the SDLC agents on the paths the flow uses: `sdlc-orchestrator`, `requirements-analyst`, `solution-architect`, `story-planner`, `test-writer`, `implementer`, `qa-test-architect`;
- `adversarial-validator` (via `cross-examine`);
- `pr-description`;
- the post-back summary;
- delivery recall;
- every reviewer in the roster entries that are enabled.

*Knowledge skills* loaded as context (`scala`, `react`, `terraform`…) are not task prompts. They are covered by the eval of the agent consuming them, with the skill injected as in production. This is an interpretation of the Stage 3 criteria and needs confirming with the certification reviewers (open question).

**Registry.** `skills/delivery-flow/steps.yaml`, one entry per task prompt:

```yaml
- step: triage
  prompt: skills/delivery-flow/references/triage.md
  tier: haiku            # declared runtime model tier
  eval: evals/delivery-triage/
  results: evals/delivery-triage/results/certified.json
  prompt_sha256: …       # hash of the prompt at certification
  criteria: [schema, type-accuracy, path-accuracy, handoff-on-ambiguity]
  iteration_log: evals/delivery-triage/iteration-log.md
  escalation_evidence: null   # required when tier is above sonnet
```

**The bar, checked by `scripts/delivery-flow/check-certification.py`** (stdlib, deterministic). Each entry must have:
- ≥3 distinct criteria;
- a results file scoring ≥95% of asserts, produced by a provider whose model is ≤ Sonnet;
- a prompt whose current sha256 equals `prompt_sha256` (any prompt edit forces recertification);
- a prompt file with a load-bearing appendix mapping ≥90% of its instructions to criteria;
- an iteration log with ≥2 entries, each with baseline, hypothesis, change, result and reasoning.

The method is the existing `prompt-edd` skill (the July Stage 3 package is the template), and fixtures are mined from Olympus's ~172 archived OpenSpec changes, excluding `ares-*`, `codex`, `harpocrates-*` and `muses-ui`.

**Enforcement.** The flow runs `check-certification.py <step>` before delegating and refuses an uncertified step. The escape hatch is `allow_uncertified: [step]` in `.delivery-flow.yaml`, recorded as `certified: false` on every trace record for that step. `delivery-report.py` reports the end-to-end rate twice: all runs, and runs made entirely of certified steps. Only the latter is the Stage 4 number. Roster entries whose reviewers or architects aren't certified are marked `certified: false` and excluded from dispatch unless allowed, which keeps v1 scope to the kinds of work actually certified (pilot: `backend`, `contracts`, `ux`).

**Model tiering, cheapest first.** Each step's tier is the cheapest one whose suite passes ≥95%, trying Haiku, then Sonnet. Opus is allowed only with `escalation_evidence`: a committed results file showing Sonnet <95% on the same suite. Starting points, all to be proven by eval:

| Tier | Steps |
|------|-------|
| Haiku first | intake digest, post-back summary, report narrative, delivery recall, `pr-description`, work-type classifier, triage |
| Sonnet | orchestrator, `requirements-analyst`, `solution-architect`, `story-planner`, `test-writer`, `implementer`, `qa-test-architect`, reviewers, `adversarial-validator` (currently unpinned; pin to Sonnet) |
| Opus | none by default |

The "separate model for validation" principle is kept by requiring the checker to differ from the generator (e.g. a Haiku generator checked by Sonnet, or a Sonnet generator checked by Sonnet with a refute-framed prompt in a fresh context). It is not achieved by defaulting to a frontier model.

**Runtime conformance.** The trace hook compares each record's `model` to the step's declared tier and sets `model_conformant: false` on mismatch. Defect-flow already showed this drift: a sampled subagent transcript ran entirely on Opus 4.8. Because the orchestrator step runs in the main session, `--status` warns when the session model is above the orchestrator's tier and recommends `claude --model sonnet`. The report lists non-conformant steps and their extra cost.

*Alternatives considered:*
- Certify only new prompts. Rejected: fails "every agent passes its Stage 3 quality bar".
- Default to Opus for quality and downgrade later. Rejected: inverts the burden of proof and inflates the audit-trail cost.
- LLM-judge-only evals. Rejected: Stage 3 wants substantive, clear pass/fail criteria, so deterministic asserts come first and rubrics only for intent.

## Risks / Trade-offs

- **[Certifying ~15 task prompts is most of the effort]** → sequenced by pilot path; the kinds of work and reviewers not in the pilot stay `certified: false` and excluded; fixtures come from OpenSpec archives rather than being authored.
- **[Haiku or Sonnet can't reach 95% on generative steps (implementer, architect)]** → escalation is allowed with evidence, and the report shows its cost. For code-writing steps, the eval uses execution-grounded asserts (tests go green on a fixture repo) so the bar is objective.
- **[Plugin cache lags `main`, so a merged hook isn't active]** → Olympus observed this with `ci-watcher`. Verification includes checking the *installed* plugin cache contains the hooks, bumping `plugin.json` version, and a `--status` line printing whether both hooks are registered in the running session (a hook self-check file touched on SessionStart).
- **[Global hooks slow or break unrelated sessions]** → both hooks exit 0 immediately unless `.delivery-flow.yaml` is found at the git root. A fixture test covers the non-delivery repo path.
- **[SubagentStop payload lacks the transcript path, or usage fields differ by Claude Code version]** → task 0.1 verifies the real payload before building. Fallback: locate the subagent transcript under `~/.claude/projects/<repo>/<session>/subagents/` by agent id.
- **[Command-pattern gating is not airtight: novel shell obfuscation or an unlisted HTTP client]** → layered defense: hook patterns, adapters re-check approvals, write protection on `approvals/`, Claude Code permission deny rules recommended in the template. The bypass suite documents what was attempted; the remaining risk is stated in the playbook, not hidden.
- **[Pricing table drifts from real prices]** → `as_of` and `source` fields; the report prints the pricing date; missing models are flagged, never guessed.
- **[Skill injection through the prompt is instruction-based]** → verified after the fact from the trace (Skill tool calls) and enforced by the implementation validator.
- **[Orchestrator/routing eval passes but real runs drift]** → the end-to-end report on real Olympus items is the check that matters. Evals guard regressions, and the report shows the trend.
- **[Scope is large for one change]** → tasks are ordered so that trace + approvals + validators (the Stage 4 core) land and work before roster routing and evals. Each task group is independently shippable behind the config file.
- **[Local-markdown backlog format doesn't match the existing vault backlog]** → `+/Feature for Olympus.md` uses service headings and bullets without keys. v1 ships an `import` subcommand that converts it into keyed items once, rather than parsing free-form bullets.

## Migration Plan

Additive. Nothing activates without `.delivery-flow.yaml` in a repo. Rollout:
1. Merge with hooks registered but inert.
2. Enable in one Olympus repo (e.g. `demeter-service`) with the local-markdown tracker.
3. Run the bypass suite and a dry-run item.
4. Widen.

Rollback: delete `.delivery-flow.yaml` (per repo) or revert the hook registration (plugin-wide).

## Open Questions

- Commit output files to the work branch (default) or keep them local? This affects whether PR reviewers see the trace and cost.
- Olympus answered on 2026-09-15 (folded into D10). Still open: the weekly feature commitment (~1–2/week estimated; Calvin's call) and which repos are included in or excluded from a certification package (Olympus suggests excluding `ares-*`, `codex`, `harpocrates-*`, `muses-ui`).
- Should approvals be cryptographically signed in a later change (D6 alternative)?
- Do the certification reviewers accept that knowledge skills are covered by their consuming agent's eval (D11), or must each loaded skill carry its own Stage 3 package?
- The `scope` decision point after triage: on by default for the standard path, or off everywhere?
- Name: `delivery-flow` is the working name.
