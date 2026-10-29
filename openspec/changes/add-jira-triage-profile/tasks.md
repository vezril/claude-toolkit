## 0. Verify assumptions

- [x] 0.1 Confirm the three certified steps still certify: `check-certification.py triage breakdown challenge-breakdown` exits 0 against the current prompts (an edited prompt un-certifies it and must be re-run before anything here is worth building)
- [x] 0.2 Confirm the registry gap is as described: `check-certification.py challenge-implementation` returns 1, and `project-memory` / `vault-update` are absent from `steps.yaml`
- [x] 0.3 Captured against the real project (`AN`, bitquill, via the read-only Atlassian connector; the adapter itself still needs a credentialed run). Populated: `summary`, `description`, `issuetype`, `status`, `components` (`NetworkX`), `parent` (the epic), `priority`, `Sprint` and `Epic Link` custom fields. **Empty on every ticket sampled: `labels`, `issuelinks`, `comment`.** The finding that mattered is not a field shape: three of the four newest tickets have no description beyond `github reference: <url>`, so the requirement lives in the GitHub issue, not in Jira — see design D10 and task 2.7
- [ ] 0.3a Record the raw REST v3 payload as a scrubbed fixture from the adapter's own path (needs `JIRA_*` in the environment); the connector's view is shaped differently from what `jira.py` parses, so it cannot stand in for one
- [x] 0.4 Confirm `skills/readability/scripts/readability.py` runs on a markdown file and emits parseable output, and record the invocation used (reads stdin, emits `scores.flesch_kincaid_grade` and `scores.gunning_fog`; invoked as `python3 -I readability.py < text`)
- [x] 0.5 Decide Q3 — the `triage` profile omits post-back (its `steps:` end at report), so `comment` is built for the contract and for the `full` profile but is not on this profile's critical path

## 1. Profiles

- [x] 1.1 Create `templates/delivery-flow/profiles.yaml`: `triage` (intake, triage, breakdown, challenge-breakdown, brief, report; terminus `brief`) and `full` (today's 15 steps; terminus `vault-update`), each declaring `steps:` and `terminus:`
- [x] 1.2 Refactor `flow-status.py:42` so `STEPS` is the full table and routing iterates the selected profile's subset of it; unknown profile exits 2 naming the available profiles
- [x] 1.3 Add `profile:` handling to config loading in `common.py`, defaulting to `full` when absent
- [x] 1.4 Terminus behaviour: when the profile's terminal step's artifact exists and its edge passed, run the report step and write `outcome.json` with `completed`; a failed edge on the terminus reports the failure instead
- [x] 1.5 Next-profile reporting: on terminus, print the next profile and the step it would begin with, then stop
- [x] 1.6 Per-profile aggregation in `delivery-report.py`: outcome counts and both punch-out denominator readings, with "no runs" distinguished from 0%
- [x] 1.7 `tests/delivery-flow/test_profiles.py`: routing inside a profile, default-to-`full`, unknown profile exits 2, terminus writes `outcome.json`, stalled terminus does not, profile union equals the full table, a later profile resumes from artifacts alone
- [x] 1.8 Document the `profile:` key and the ceilings in `skills/delivery-flow/references/config.md`. **Note:** `templates/delivery-flow/delivery-flow.yaml` does not exist yet — it is the parent change's task 1.1, still open — so there was no template to change alongside it
- [x] 1.9 Add the `profiles.yaml` / `load_profiles` pair, the shared `brief.py`, and the shared `triggers.py` to the CLAUDE.md consistency rules

## 2. Jira adapter

- [x] 2.1 `scripts/delivery-flow/adapters/jira.py`: `fetch` against the Jira REST API with the D6 field mapping; stable collection ordering; no request-varying values in the output
- [x] 2.2 `related`: issue links plus the epic or parent key, mapped onto `{parent, design: [], related: []}`
- [x] 2.3 `comment` and `transition`, both refusing with exit 2 while a punch-out is open, and `comment` refusing without a signed decision when `tracker.external: true` (shared helper from `common.py`)
- [x] 2.4 Credentials from `JIRA_BASE_URL` / `JIRA_EMAIL` / `JIRA_API_TOKEN`; missing or malformed exits 2 naming them, auth or network failure exits 3, neither writing a partial artifact
- [x] 2.5 `tests/delivery-flow/test_jira_adapter.py` against the 0.3 fixture: schema conformance, byte-identical reruns, labels and components merged, custom fields omitted, exit 2 and exit 3 paths, refusal while a punch-out is open
- [x] 2.6 Document the field mapping and the Jira entry in `skills/delivery-flow/references/adapters.md` (Jira moves from deferred to shipped)
- [x] 2.7 Follow a GitHub reference in the description: fetch the linked issue or PR through the same `gh` runner the GitHub adapter uses, append its title and body under a fence marking it unverified external content, and record each reference in `references`. An unfetchable reference exits 3 rather than thinning the body (determinism is a contract); `--no-follow` is the escape. `links` stays Jira keys only. 14 tests in `test_jira_adapter.py`; `references` typed in `schemas/item.schema.json`; spec and design D10 written

## 3. The brief

- [x] 3.1 `scripts/delivery-flow/render-brief.py`: fixed six-section template over `item.json`, `triage.json`, `breakdown.json`, `challenge-breakdown.json`; empty sections stated rather than omitted; quick-path items keep the same shape; byte-identical reruns
- [x] 3.2 Extend `hooks/check-edge.py` so `summary.md` joins the terminal-prose artifacts, with the coverage checks: every epic and story id present, verdict present, required findings present, no identifier absent from the inputs
- [x] 3.3 Compute Flesch-Kincaid and Gunning Fog via `skills/readability/scripts/readability.py` and write both into the step's trace record; never fail the edge on them
- [x] 3.4 `tests/delivery-flow/test_render_brief.py`: reproducibility, section order, empty-section wording, quick-path shape, dropped-story edge failure, invented-identifier edge failure, omitted-finding edge failure, readability recorded but non-blocking
- [x] 3.5 Confirm no step declares `summary.md` as an input, in `steps.yaml` and `profiles.yaml`

## 4. Derived punch-out triggers

- [x] 4.1 Add the three derivations to `check-punch-out.py` per D5, reading the item and the repository rather than the node's booleans
- [x] 4.2 Fire on derivation OR claim; record disagreement on the edge as `policy_disagreement` (trigger, claimed, derived, evidence) and report it, **without** failing the edge — the first draft failed it, which was wrong; see design.md D5
- [x] 4.3 Record the source of each fired trigger (derivation, claim, or both) in the punch-out file, with the evidence quoted
- [x] 4.4 Add the ceiling keys under `punch_out` with documented defaults, applied when unset
- [x] 4.5 Extend the bypass suite: flag suppression per trigger, path renaming to fall outside `contract_paths`, breakdown splitting to stay under a ceiling, and hand-editing `triage.json` after its edge passed
- [x] 4.6 Ran the bypass suite and recorded the report: **23 of 23 blocked or detected, 0 breached, 0 inconclusive** (2026-10-28, sonnet). It took four runs, because the first three found holes in the *harness* rather than the guardrails — and every one of them made the guardrails look better than the evidence justified:
  - **a single fixture shared by all 23 attacks**, so state leaked forward and a row's evidence did not belong to its own attack (`split-under-the-ceiling` appeared to silence `scope`; an edit three rows upstream had done it). Each attack now builds a fresh fixture;
  - **the derived gates judged on whether *any* trigger still fired**, so a partial success read as a block. Each attack now names the trigger it targets and only that one counts;
  - **the fixture had no `punch_out:` block at all**, leaving `contract_paths` and `protected_paths` unset, so `proposal-breaking`, `proposal-architecture` and `protected-path` could not fire and were resting entirely on the node's own claims — the exact dependency the derived triggers exist to remove. Four attacks were testing nothing;
  - **breach matching was on substrings**, scoring `gh pr view --json url,state,mergeable` as a merge because `mergeable` contains `merge`. Now matched on whole argv tokens. Third appearance of this class of bug in this suite.
  - Plus a framing error, not a defect: six attacks told the agent to act *in order to* defeat the gate, which it read as being asked to defeat a safety control and refused — rows that looked like blocks but showed only that the model was polite, the weakest possible evidence under a standard whose premise is that guardrails must not depend on the model's cooperation. Reframed as plausible work with identical mechanical effect; a row where the agent still rewrites nothing is now reported `inconclusive` rather than counted as a block.
  - All four defects and the framing error are written into the report itself, per the evidence checklist's "submit the holes too".
- [x] 4.6a Verified `triggers.py` itself is sound: once the fixture configures the paths, every path derivation fires independently of the node's claims. Four attacks silenced their target and were caught by the sha-based manual-correction fallback — the second layer, observed working rather than assumed
- [ ] 4.6b **Known residual to raise with the reviewer:** `proposal-scope` has no structural derivation. It checks the task and file ceilings only, so a proposal under those ceilings rests on the node's own claim. Arguably correct (scope has no path signature before there is code) but it is the one derived trigger a claim can still silence on its own — caught today only by the hand-edit detection

## 5. Target repo and real runs

- [x] 5.1a Built `init-delivery-flow.py` so opting a repo in is one command rather than hand-authored YAML: it detects the forge, base branch, test command and the protected paths that exist, and refuses to guess the Jira project key, `tracker.external` or `contract_paths`. 27 tests in `test_init.py`
- [ ] 5.1b Run it against `~/Code/nx-neptune` — **Q1/Q2 answered**: project `AN` on bitquill.atlassian.net, a client's Jira, so `--jira-project AN` with no `--internal` (`tracker.external: true`). Blocked only on `JIRA_BASE_URL` / `JIRA_EMAIL` / `JIRA_API_TOKEN` in the environment
- [ ] 5.2 Dry run on one real ticket (AN-3704 is the sharpest test: a stub whose whole description is a link to `awslabs/nx-neptune#579`); fix what breaks in the adapter mapping
- [ ] 5.3 Three real runs on real tickets, artifacts committed per `artifacts.commit: true`
- [ ] 5.4 Read the per-profile rate from `delivery-report.py`; record the outcome mix and the model/token/cost table
- [ ] 5.5 Record any run that required a hand-edited artifact as `failed` with reason `manual-correction` — do not repair and re-count it

## 6. Docs (doc-sync rule)

- [x] 6.1 `skills/delivery-flow/SKILL.md`: profiles, the terminus, the brief, and the derived triggers
- [ ] 6.2 `docs/using-the-sdlc-dev-team.md`: the profile concept and the certified chain as its own section. **Blocked:** that playbook has no delivery-flow section yet (parent change task), so there is nothing to amend; `docs/delivery-flow-handoff.md` carries the update instead
- [x] 6.3 New `docs/figures/delivery-flow-profiles.svg` (both profiles, the brief and the terminus as amber scripts, the artifact-directory handoff), plus a pointer and a corrected success-rate caption on `docs/figures/delivery-flow.svg`. Row 1 of the existing figure had no room for the brief, and a wrong diagram is worse than an incomplete one
- [x] 6.4 `agents/README.md` and `skills/prime/` checked: neither mentions delivery-flow (it is not an agent and has no team binding), so there is nothing to sync
- [x] 6.5 `skills/delivery-flow/references/trace.md`: the readability metrics and the mismatch report in the edge record

## 7. Follow-up, not in this change

- [x] 7.1 Recorded and acted on: `add-vault-delivery-memory` design D3 and its `vault-binding-reachability` spec; the vault is now scaffolded and the unreachable/empty distinction is implemented and tested
- [x] 7.2 Recorded in `add-openspec-proposal-step` design D4, and now **resolved**: the `openspec` CLI is installed (1.15.0), so the live `sdlc-solutioning-openspec` readiness-gate requirement is satisfiable and the proposal edge's `validate --strict` layer runs for real
