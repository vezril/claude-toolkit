# Tasks

Ordered so each group leaves the suite green. Groups 1–3 are independent of each other; group 4
is the documentation `CLAUDE.md` requires in the same change, and group 5 is the end-to-end
check that the three controls actually fire on a real run.

## 1. The review step

- [x] 1.1 `schemas/review.schema.json`: per-reviewer attribution (which agent reviewed, against
      which diff sha), findings with evidence, and the SURVIVED / WEAKENED / REFUTED verdict
      (D3). Register it so `schema_for` resolves `review.json`; confirm by writing a malformed
      artifact and seeing the edge reject it, not by reading the registry.
- [x] 1.2 `skills/delivery-flow/references/review.md`: the node prompt. States its inputs as the
      diff, the story/proposal and `verify.json`, and states that `implementation.json`'s
      narrative is deliberately withheld (D2) so a reader of the prompt knows that is a choice
      rather than an omission.
- [x] 1.3 `skills/delivery-flow/steps.yaml`: registry entry, `certified: false` with a stated
      residual naming the absent eval suite. Assert in a test that it claims no
      `prompt_sha256`, `results` or `consecutive_runs` — the same guard the sdlc nodes carry.
- [x] 1.4 Add `review` to `allow_uncertified` in the config template and document why in
      `skills/delivery-flow/references/config.md` (the keys and that reference change together).
- [x] 1.5 `templates/delivery-flow/profiles.yaml`: insert `review` between
      `challenge-implementation` and `pr-description` in `full` **and** add it to the `STEPS`
      table in `scripts/delivery-flow/flow-status.py`. `tests/delivery-flow/test_profiles.py`
      enforces the pair; run it before anything else in this group is believed.
- [x] 1.6 `skills/delivery-flow/workflow.yaml`: routing row keyed on `review.json`, and
      `verdict_policy.weakened: require-addressed` declared explicitly (D3) so a substrate
      default change cannot move it.
- [x] 1.7 The fan-out (D1): one step dispatching each roster reviewer in its own fresh context,
      merging into one `review.json`. A work kind with an empty reviewer list is an error, not a
      skip — test that case, because a silent skip is the failure that would make this step
      decorative.
- [x] 1.8 Wire review findings into `carry_forward` and make `pr-description` obliged to
      address each. Test the staleness rule: an unchanged diff means nothing was addressed, so
      the review reruns rather than advancing on self-report.

## 2. Diff-size ceilings

- [x] 2.1 `punch_out.max_diff_files` and `punch_out.max_diff_lines` in the config template, with
      `skills/delivery-flow/references/config.md` updated in the same commit. An absent ceiling
      is reported, never treated as unlimited.
- [x] 2.2 The derivation in `scripts/delivery-flow/triggers.py` — the one home for derived
      triggers, imported by `check-punch-out.py` and `hooks/check-edge.py` so it cannot be
      computed two ways. Reads the diff only; no node's size or scope field is consulted (D4).
- [x] 2.3 Record the measured file and line counts next to the ceilings they breached, so the
      punch-out carries its own evidence.
- [x] 2.4 Evaluate at `verify`, and re-evaluate when the diff changes after a passing check.
- [x] 2.5 Tests: within both ceilings advances; breaching either raises; an artifact claiming
      the change is small does not clear it; a missing ceiling is an error. Mutation-check the
      derivation — a trigger that cannot fire is the defect this repo keeps finding.

## 3. P0/P1 test scope

- [x] 3.1 Add the per-criterion priority to the story/proposal contract and its schema (D5).
      An acceptance criterion with no priority is an error naming that criterion.
- [x] 3.2 `agents/test-writer.md`: cover P0 and P1, never below; a disputed priority is reported
      as a finding, never overridden (D6). Leave the file-territory definition untouched so the
      three-place agreement with `agents/implementer.md` and
      `hooks/enforce-dev-pair-boundary.py` still holds — and assert that in a test rather than
      trusting the diff.
- [ ] 3.3 The verify check, **both directions**: every P0/P1 criterion has a test, and no test
      claims a criterion below P1. The second direction is the one this change exists for.
- [x] 3.4 A test covering several criteria counts for each; no duplicate test is demanded.
- [x] 3.5 Tests for all four cases above, with the out-of-scope direction mutation-checked.

## 4. Documentation, in the same change

- [ ] 4.1 `skills/delivery-flow/SKILL.md`: the routing table gains `review`; the profile table
      is updated; the sentence about `full` not being a Stage 4 number is extended to say it now
      carries a sixth uncertified node.
- [ ] 4.2 `skills/delivery-flow/references/roster.md`: say that `reviewers:` is now dispatched,
      and by which step. It has described an unused field since the roster was written.
- [ ] 4.3 `docs/delivery-flow-handoff.md` and `docs/delivery-flow-status.md`. Not
      `docs/using-the-sdlc-dev-team.md` — this is delivery-flow, not the SDLC pipeline.
- [ ] 4.4 State the trade-off from the design where a reader will meet it: P0/P1-only reduces
      coverage deliberately, and a later regression in a P2 path is the cost of smaller PRs.

## 5. Prove the controls fire

- [ ] 5.1 Drive one `full` run end to end **from a session whose cwd is the delivery repo** —
      `hooks/trace-step.py` records only then, so a run orchestrated from the toolkit produces
      no step records and proves nothing.
- [ ] 5.2 Confirm from the trace, not from a report: `review` ran, its edge checked
      `review.json`, and its findings reached `pr-description` as `carry_forward`.
- [ ] 5.3 Confirm the size ceiling fires by running against a deliberately oversized diff, and
      that only a signed human decision clears it.
- [ ] 5.4 Confirm the verify edge rejects both an uncovered P0 and an out-of-scope P3 test.
- [ ] 5.5 Record in the run's notes that `full` remains outside any certified-only rate, so
      these runs are not later mistaken for Stage 4 evidence.
