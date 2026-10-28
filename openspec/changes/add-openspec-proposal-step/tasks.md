## 0. Verify assumptions

- [x] 0.1 Confirmed absent at design time; **now installed** (1.15.0). The optional-layer design still holds and is still the right shape — a teammate's machine may not have it — but on this machine the layer runs for real. See task 8.2
- [x] 0.2 Confirm the live spec `openspec/specs/sdlc-solutioning-openspec/spec.md` still names the four change artifacts and keeps archive human-triggered; this change must agree with it
- [x] 0.3 Confirm no step consumes `spec-ready.json` before retiring it

## 1. The contract and its edge (edge before producer)

- [x] 1.1 `schemas/proposal.schema.json`: `change_id`, `change_path`, `specs_touched[]`, `tasks[{id, description, files[]}]`, `dependencies_added[]`, and the node's `scope`/`architecture`/`breaking` claims; `counts` for tasks and files; `produced_by: propose`, `consumed_by: [implementation, brief]`
- [x] 1.2 `scripts/delivery-flow/validate-proposal.py`: change dir + four artifacts, task-id closure both ways, named specs exist, task file paths inside the repo, no empty task or empty file list
- [x] 1.3 Optional `openspec validate <id> --strict` layer when the CLI is on PATH; record `skipped: not installed` otherwise, never pass by absence
- [x] 1.4 Wire `proposal.json` into `hooks/check-edge.py` alongside the schema checks
- [x] 1.5 `tests/delivery-flow/test_proposal.py` for every scenario in the node spec, including both mismatch directions and the path-escape case

## 2. Routing

- [x] 2.1 `flow-status.py`: `("proposal.json", "propose", "node", None)` replaces `("spec-ready.json", "solutioning", "sdlc", None)`
- [x] 2.2 `templates/delivery-flow/profiles.yaml`: `full` gains `propose`, loses `solutioning`, and `brief` moves to directly after `propose`; `triage` unchanged
- [x] 2.3 Assert the `triage` profile's routing table is unchanged by this change (a test, not an eyeball)

## 3. The brief as the approval surface

- [x] 3.1 `brief.py`: a "What will change" section from `proposal.json` — change id, task count, files touched, dependencies added, flags raised; present and explicit when no proposal exists
- [x] 3.2 Extend `coverage_problems` to require every proposal task id, and extend the known-identifier set so proposal paths are not flagged as invented
- [x] 3.3 `tests/delivery-flow/test_render_brief.py`: the new section, the omitted-task failure, and a test asserting the `triage` profile's brief is byte-identical to its pre-change output

## 4. The decision gate

- [x] 4.1 `triggers.py`: `proposal-scope`, `proposal-breaking`, `protected-path`, `new-dependency`, derived from planned paths and counts
- [x] 4.2 Ceilings `proposal_task_ceiling` and `proposal_file_ceiling` with documented defaults
- [x] 4.3 Fire the proposal triggers at the `brief → implementation` handoff only
- [x] 4.4 Claims-and-derivation composition, with disagreement recorded and never failing the edge
- [x] 4.5 `tests/delivery-flow/test_triggers.py`: each trigger, the rewording-cannot-evade case, the clean-change pass-through, and the suppressed-claim case
- [x] 4.6 Four proposal-trigger attacks added (suppress every claim, relocate the planned paths, drop the declared dependency, evaluate policy at the wrong step) with a `proposal-gate-holds` judgement. Fixed a fixture gap found doing it: the harness seeded a trace sha for `triage.json` only, so a hand-edited proposal looked undetectable when a real run's hook would have caught it

## 5. Lifecycle closure

- [x] 5.1 `scripts/delivery-flow/close-openspec-change.py`: tick `tasks.md` from `implementation.json` by id, report ticked and left-open, exit non-zero on an unknown id
- [x] 5.2 Print the `openspec archive <id>` command; never run it
- [x] 5.3 `flow-status.py` reports outstanding unticked tasks for the item's change
- [x] 5.4 `tests/delivery-flow/test_lifecycle_closure.py` for each scenario

## 6. The node prompt

- [x] 6.1 `skills/delivery-flow/references/propose.md`: inputs (`item.json`, `triage.json`, `breakdown.json`, `challenge-breakdown.json`, carry-forward findings), the four change artifacts to produce, the `proposal.json` contract, and the rule that it distills and references the breakdown rather than reforking it
- [x] 6.2 Add `propose` to `allow_uncertified` in the config template and document why
- [x] 6.3 **Found and fixed a real bug.** `trace-step.py` recorded `certified: None` for a step with no registry entry, and `delivery-report.py` tests `is False` — so an uncertified node's runs were counted in the certified-only Stage 4 rate. Now records `False`, with two tests in `test_trace.py` asserting the flag and the report's exclusion

## 7. Docs (doc-sync rule)

- [x] 7.1 `skills/delivery-flow/SKILL.md`: the routing table, the `full` profile's new shape, the brief as the approval surface, the proposal triggers
- [x] 7.2 `skills/delivery-flow/references/config.md`: the proposal ceilings and `allow_uncertified`
- [x] 7.3 `skills/delivery-flow/references/trace.md`: the `openspec_validate` field and the proposal disagreement entries
- [x] 7.4 `docs/figures/delivery-flow-profiles.svg`: `full` gains propose → brief, and the gate sits after the brief
- [x] 7.5 `docs/delivery-flow-handoff.md`: the new files, the test count, and that `full` is not submittable until `propose` is certified

## 8. Follow-up, not in this change

- [ ] 8.1 Certify `propose` (`prompt-edd`: suite, ≥3 criteria, load-bearing map, iteration log, Haiku-first escalation evidence, 3 consecutive runs) — needs model runs and its own change
- [x] 8.2 **Installed** (openspec 1.15.0). The proposal edge's optional layer now actually runs — verified against a real change (valid) and an unknown one (exit non-zero). All three changes pass `openspec validate --strict`; fixing the four >500-character requirements it flagged moved rationale out of requirement text and into scenarios, which is where it belonged
- [ ] 8.3 Consider a `challenge-proposal` node; the certified challenge prompt is certified against breakdowns and retargeting it un-certifies it
