## Why

The SDLC team starts from an idea in chat and stops at code. Nothing takes a work item from a tracker, picks the right specialists for the kind of work, and delivers a PR plus a tracker update. The intake flows that do exist (`github-issue-fix-flow`, unattended mode) are GitHub-only and skip specialist routing. The pattern that works, defect-flow (state kept in files, a per-repo config, human decision points, post-back to the ticket), lives in a private, bug-only, single-client repo. A general, measurable version is also the workflow Calvin needs for Stage 4 AI Maturity certification. That requires per-step traces with model, tokens and cost, decision points that are enforced and bypass-tested, and automatic checks between steps. None of these exist today.

## What Changes

- **New `delivery-flow` skill**, a wrapper around the SDLC orchestrator: tracker item → intake → triage → (optional vault recall) → SDLC phases → verify → PR → post-back → report. Like the SDLC pipeline, state lives in files (`delivery/<ITEM-KEY>/` in the target repo). The skill routes to the first step whose output file is missing and runs one step per invocation.
- **Per-repo config** `.delivery-flow.yaml`: tracker, PR host, decision points, per-step models, roster overrides, test command, optional vault binding.
- **Adapter contract with v1 adapters**, implemented as scripts that emit JSON and no LLM:
  - trackers: GitHub Issues (`gh`) and a local markdown backlog;
  - PR host: GitHub (`gh`).
  - Jira, GitLab, Bitbucket and Linear are specified by the contract but deferred.
- **Routing by item type:** the triage step classifies the item as bug, feature or task and picks the path (quick or standard). Each branch is documented and evaluated.
- **Routing by kind of work at story level:** story files gain an optional `Domains:` line (e.g. `ux, backend, infra`). A plugin-level `roster.yaml` maps each kind of work to an architect, skills, reviewers and optional deploy agent, and repos can override it. A script checks the labels and resolves the agents. The test-writer/implementer pair stays a single pair, loaded with the right skills per story.
- **Per-step audit trail:** a hook writes one `trace.jsonl` record per step (step, agent, model, input/output/cache tokens, cost, output file, validator result), taken from Claude Code transcripts. A report script rolls it up into an end-to-end success rate and cost per item and per week.
- **Policy-triggered punch-outs, not fixed checkpoints:** following the Stage 4 rule that human review between steps is Stage 2, quality between steps is fully automated (validators plus adversarial challenges), and the flow runs from intake to an open PR and ticket update without stopping. A deterministic policy check at every handoff stops the flow and asks Calvin when the decision shouldn't be left to AI: an unclear or out-of-scope item, an architecture or breaking change, repeated refutation, retry or budget limits, protected paths, or a post to a client tracker. **Merging is always human** (agents are blocked from merging), and **deploys are human unless the auto-roll rule applies**. Decisions are human-created and hash-bound; hooks block agents from writing decisions, clearing punch-outs, merging, or continuing past an open punch-out. A scripted bypass suite provides the evidence.
- **Checks between steps:** a deterministic validator per output file (item.json schema, triage file shape, pr.md sections, post receipt matching the posted body), run automatically at every handoff. Adversarial review becomes mandatory at the spec and implementation handoffs.
- **Evals:** a promptfoo suite for the orchestrator's routing and one for the work-type classifier.
- **Every step must be Stage 3 compliant, on the cheapest model that passes:**
  - **Step registry** (`skills/delivery-flow/steps.yaml`): every LLM step (skill or agent) the flow can run, with its prompt path, declared model tier, eval suite, certified results, the prompt hash at certification time, and its iteration log.
  - **Stage 3 bar per step:** a structured prompt whose instructions are ≥90% load-bearing; ≥3 distinct eval criteria scoring ≥95% on the declared tier; evals on Sonnet or lower; an iteration log with ≥2 iterations.
  - **Enforcement:** `check-certification.py` blocks a step that isn't certified, or whose prompt changed since certification.
  - **Cheapest tier by default:** Haiku first, then Sonnet. Opus only with recorded eval evidence that Sonnet scores below 95% on that step.
  - **Runtime check:** the trace compares the model that actually ran against the declared tier and flags a mismatch, including the main session running the orchestrator on Opus.
- Docs updated per the CLAUDE.md doc-sync rule.

## Capabilities

### New Capabilities
- `delivery-flow-orchestration`: the step sequence, file-based routing, per-repo config, item-type branching, one-step-per-invocation rule, and handoff into and out of the SDLC orchestrator.
- `tracker-forge-adapters`: the adapter contract (fetch, comment, transition, related; open PR, CI status), deterministic JSON output, and the v1 GitHub and local-markdown adapters.
- `work-type-routing`: the story `Domains:` field, the roster format and override rules, label validation, and agent/skill resolution per story.
- `delivery-audit-trail`: the per-step trace record format, transcript-to-trace extraction, cost calculation, and the end-to-end report.
- `punch-out-enforcement`: the deterministic punch-out triggers, punch-out and decision files (human-created, hash-bound), the always-human merge and deploy rules, the blocking hook, and the bypass-test suite.
- `step-certification-and-model-tiering`: the step registry, the per-step Stage 3 bar and its deterministic check, recertification on prompt change, the cheapest-tier escalation policy, and runtime model conformance.

### Modified Capabilities

<!-- none: no existing spec covers the SDLC pipeline's attended behavior or the story format; the Domains: field is additive and optional for non-delivery-flow use -->

## Impact

- **New:**
  - `skills/delivery-flow/` (SKILL.md with references for config, adapters, roster, trace);
  - `scripts/delivery-flow/` (adapters, `validate-artifact.py`, `resolve-roster.py`, `delivery-report.py`, `check-punch-out.py`, `decide.py`);
  - `hooks/trace-step.py` and `hooks/enforce-punch-outs.py`, registered in `hooks/hooks.json`;
  - `templates/delivery-flow/` (`.delivery-flow.yaml`, `roster.yaml`);
  - `evals/delivery-flow-routing/` and `evals/work-type-classifier/`.
- **Modified:** `skills/spec-driven-development/references/story-schema.md` and `scripts/lint-story.py` (optional `Domains:` field plus `--require-domains`, changed together per CLAUDE.md), `agents/story-planner.md` (tags stories), `agents/sdlc-orchestrator.md` and `skills/sdlc-orchestration/SKILL.md` (per-story dispatch from the roster when invoked by delivery-flow).
- **Docs (doc-sync rule):** `docs/using-the-sdlc-dev-team.md` (new delivery-flow section), a new `docs/figures/delivery-flow.svg`, `agents/README.md`, the `skills/prime/` team bindings (read the roster), `CLAUDE.md` consistency rules (new paired files).
- **Dependencies:** `gh` CLI (GitHub adapters); the optional vault recall/update steps depend on the separate change `extend-vault-graphrag-projects` and are skipped when no vault binding is configured.
- **Non-breaking:** the existing SDLC pipeline, `github-issue-fix-flow`, unattended mode and `git-ship` keep working unchanged. Rebuilding them on top of delivery-flow is out of scope.
