## 0. Sequencing notes — not a gate

**Dropped, 2026-10-29: "nothing lands before the Stage 4 submission is accepted" was my
invention, not a requirement from the deck or a reviewer.** It blocked Calvin from doing his
day job — feeding delivery-flow output into the orchestrator — for a risk that does not need a
freeze to manage. What design D2 actually warrants is narrower: **do not restructure the files
already submitted** (sections 1 and 2, the substrate extraction and hook generalisation) while
a submission is open. Additive work that leaves the submitted tree where it is may proceed,
and section 3 is exactly that.

- [ ] 0.1 While a submission is open, keep sections 1–2 (substrate extraction, hook
      generalisation) out of the submitted tree's layout. Additive work proceeds (design D2,
      narrowed)
- [ ] 0.2 Ask the reviewer Open Question 1: is a pipeline of certified 2–3 node segments joined
      by deterministic edges certifiable *segment by segment*? This is the assumption the whole
      change rests on and it is mine, not the deck's. A "no" stops the change at section 4
- [ ] 0.3 Ask Open Question 2: do knowledge skills loaded as context need their own
      certification? sdlc loads many more than delivery-flow, so the answer changes the cost
- [ ] 0.4 Record the baseline: `pytest tests/delivery-flow/` and
      `python3 tests/delivery-flow/bypass/run-bypass.py` both green, with the output committed,
      so the extraction has something to be compared against
- [ ] 0.5 Confirm the readiness gate's two checks still behave as documented:
      `lint-story.py` non-zero on a malformed story set, and `openspec validate` non-zero on a
      malformed change dir

## 1. Substrate extraction (behaviour-preserving)

- [x] 1.1 Done in five slices, each its own commit and each leaving the existing suite green and unchanged: `pricing.py`, `trace.py`, `registry.py`, `schema.py`, `layout.py`. `common.py` 640 -> 464 lines. Nothing in the substrate defaults — every path is required, because a default is how a second workflow gets priced off this one's rates or validated against contracts it was never written for
- [x] 1.2 `skills/*/workflow.yaml`, parsed by `scripts/workflow/descriptor.py`. Carries the opt-in file name, artifact directory, signing namespace, pointers and the routing table. The table was Python literals in `flow-status.py`; a test compares the descriptor's against `STEPS` directly so a YAML typo cannot drop or reorder a step
- [x] 1.3 Thin re-export shims in `common.py`. The shim tests assert **identity**, not equality: `common.price_for` must *be* `pricing.price_for`. Equality would pass against two diverging copies that happen to agree on the cases tested, which is the whole failure shims exist to prevent
- [x] 1.4 532 delivery-flow tests green and unchanged across every slice, and the bypass suite 24/24 blocked, 0 breached, 0 inconclusive against the generalised hooks — including `write-decision-absolute-variable`, which had been in the table but never executed, so the count had stood at 23/23 for want of a run
- [x] 1.5 `descriptor.resolve(repo)`. No workflow is `(None, None)` rather than an error — the common case, on the path of every hook invocation in every unrelated session, so inertness is a tested property. Two active workflows is an error, not a choice: picking one silently routes a step by the wrong table and the run looks successful

## 2. Generalise the hooks

- [x] 2.1 `check-edge.py` builds its Bash pattern from every descriptor's artifact directory as an escaped, longest-first alternation; `_registered_bases` unions every workflow's registry, each consulted with *its own* predicate. A broken descriptor degrades to "no workflows" rather than failing every tool call. Also fixed: `descriptor.py` did not honour `CLAUDE_PLUGIN_ROOT` while `common.py` does, so with it set the descriptors and the schemas they point at came from different trees
- [x] 2.2 `trace-step.py` resolves the descriptor, and stopped hard-coding `skills/delivery-flow/steps.yaml` — it takes the registry from the workflow. Reading another workflow's registry would report model drift against tiers never declared for those steps. No descriptor yields `{}`, the same answer as a missing registry, which the caller already handles
- [x] 2.3 `enforce-punch-outs.py` resolves the descriptor, and its item-key regex tries every workflow's artifact directory, escaped. This is the hook that stops an agent writing its own decision, so a pattern that silently stops matching disables the control that matters most
- [x] 2.4 `tests/workflow/test_hook_generalisation.py`: a fixture plugin root with two descriptors, both artifact directories scanned, a repo opted into either or both, the variable-base shape that defeated earlier versions, and the metacharacter case. Proven for real when the sdlc descriptor landed — all 532 delivery-flow tests passed unaltered the first time two descriptors existed
- [x] 2.5 A repo with no descriptor produces no output and exits 0, for all three hooks; a malformed payload never fails a tool call. The four answers the hooks ask live in `descriptor.py` and all three delegate, rather than each deriving its own — which is how the artifact directory ended up in one regex in `check-edge.py` and a different one in `enforce-punch-outs.py`

## 3. The story becomes a data contract

**Section 3 RETIRED, 2026-10-30.** `render-stories.py` is deleted. It rendered the story set from `breakdown.json` and was forbidden from changing anything, so its stories were frozen *before* the challenge findings were resolved — and `propose` is what resolves them. AN-3631 proved it: propose folded S5 into S1 and dropped S6, while the rendered six still listed both. It was also not a step in any profile, so it wrote into run directories the flow does not route, producing six edge-failing artifacts that halted a live run. The handoff into implementation is the OpenSpec change — `proposal.json` plus `tasks.md` — and there is no second story set.

S.1–S.6, 3.1, 3.2, 3.4, 3.7 are retired rather than done. 3.3, 3.5, 3.6 and 3.8 still apply to the *markdown* story path, which `lint-story.py` owns and which is untouched by this.

- [~] S.1 RETIRED — `scripts/delivery-flow/render-stories.py` (delivery-flow for now; moves to `scripts/workflow/` with the substrate): render one `story.json` per `breakdown.epics[].stories[]`, carrying id, statement, domains and acceptance criteria across unchanged, plus a `sources` array naming `item.json`, `breakdown.json`, `challenge-breakdown.json` and the OpenSpec change directory where one exists
- [~] S.2 RETIRED — `stories.py` shared between the renderer and the story validator, as `brief.py` does for the brief, so neither can disagree about what a story is
- [~] S.3 RETIRED — `invented()` and `missing_from()` in the shared module; no story, criterion or domain may appear that the breakdown does not contain — the renderer invents nothing, and that is enforced rather than reviewed
- [~] S.4 RETIRED — `ordering.determined: false` on every story, with the basis spelled out. State the sequencing gap in the brief: stories are in breakdown order and dependency ordering is undetermined. Ordering is a judgement, so it belongs to a node or a human, not the renderer
- [~] S.5 RETIRED — Keep `story-planner` as the entry point for work with no `breakdown.json`, and say so in `skills/sdlc-orchestration/SKILL.md` — the rendered path is for tracker items only. Added "Where stories come from (two entry points)" to `SKILL.md` (the rule keys off whether a `breakdown.json` exists, not preference) plus a `[[delivery-flow]]` line under Related, and "When you are the right entry point" to `agents/story-planner.md` so the agent refuses a breakdown handed to it for re-decomposition instead of relying on the orchestrator to route correctly
- [~] S.6 RETIRED — 18 tests in `tests/delivery-flow/test_stories.py`: exact story/criterion counts from a fixture breakdown, the invented-identifier refusal, and the no-breakdown path still reaching `story-planner`


- [~] 3.1 RETIRED — `schemas/story.schema.json`: the normative structure. **Also fixed the bug that made
      it unreachable:** its `artifact` was the fixed name `story.json` while rendered files are
      `story-E1-S1.json`, so `schema_for` returned None for every one — the schema existed and
      nothing could find it, leaving the whole handoff unvalidated by both
      `validate-artifact.py` and the edge hook (which skipped them in `changed_artifacts`
      before its checker saw them). `artifact` is now the glob `story-*.json` and `schema_for`
      resolves globs generally, replacing the `*.sentinel.json` special case rather than adding
      a second one
- [~] 3.2 RETIRED — `scripts/workflow/story.py`: the shared template + coverage checks, imported by both
      the renderer and the edge, so they cannot disagree about what a story is (the `brief.py`
      pattern)
- [ ] 3.3 Rewrite `scripts/lint-story.py` as schema validation plus the semantic checks a schema
      cannot express: Given/When/Then grammar, task↔AC closure, resolvable references, FR/CAP
      traceability. Keep the name and CLI. **Scope corrected: this is for the markdown path
      only.** Rendered stories are not linted by it and must not be — `story-schema.md` now
      says so in a Scope section. The two formats have two laws and one of them is a JSON
      schema already enforced at the edge
- [~] 3.4 RETIRED — `render-story.py`: generate `story.md` from `story.json` for human readers; never
      parsed. **Deferred and demoted to a convenience.** It was implicitly the plan for making
      the handoff work, and it is not needed for that: the dev pair consumes `story.json`
      directly (3.7), so nothing blocks on a markdown rendering. Worth building only when a
      human wants to read a story outside an editor — and it must stay unparsed, because a
      markdown story that `lint-story.py` could accept would have to carry invented tasks and
      `FR`/`CAP` IDs
- [ ] 3.5 One-shot migration script for existing markdown stories, with a report of what it
      could not convert
- [ ] 3.6 Update `story-schema.md` and `lint-story.py` together — they are a normative pair per
      `CLAUDE.md`
- [~] 3.7 RETIRED — Update `test-writer` and `implementer` prompts to consume `story.json`. Each gained a
      "When the story is a `story.json`" section: `acceptance_criteria[]` is the spec,
      `sources[]` is context to **open** rather than a summary to trust, there are no tasks and
      no dependency order, and a missing criterion is a gap in the plan to raise rather than
      infer. Territory definition untouched, so the three-place agreement
      (`agents/test-writer.md`, `agents/implementer.md`, `hooks/enforce-dev-pair-boundary.py`)
      still holds — the boundary is by file path and a `story.json` is read, never written, by
      either agent
- [ ] 3.8 Resolve Open Question 5: whether dev-pair territory is still path-based once stories
      are data

## 4. Register the pipeline as segments

- [x] 4.1 `skills/sdlc-orchestration/steps.yaml`: eleven nodes across six segments, each naming its segment, agent, prompt, tier and inputs/outputs. Every one `certified: false` with a stated residual. Design D1 names `analyst`, `requirements-reviewer` and `readiness-reviewer`; none exists as an agent, so the analysis/planning seats are `requirements-analyst` and every refute-framed reviewer seat is `adversarial-validator` — the same agent in a different chair, which is why task 5.3 asks about reusing `evals/cross-examine/`. Each seat still needs its own certification
- [x] 4.2 `skills/sdlc-orchestration/workflow.yaml`: the six segments as the routing table, each with nodes, terminus and handoff. Parsed by the shared `descriptor.py` with **no parser change**, which is the real test that sections 1-2 generalised something. Distinct `config_name` and `artifact_dir` from delivery-flow, or `parse_artifact_path` would be ambiguous and every repo would opt into both
- [x] 4.3 Every node marked uncertified, with tests asserting none claims `prompt_sha256`, `results`, `consecutive_runs` or `certified_version`. Declaring the pipeline does not make it runnable — a registry that declared six segments and let an orchestrator drive them would read as evidence of a pipeline that has none
- [x] 4.4 `templates/sdlc/profiles.yaml`: `readiness` alone (the slice section 5 certifies first), `implementation`, and `full`. Same parser and same orphan/terminus rules as delivery-flow's
- [x] 4.5 Move the readiness gate's `lint-story.py` + `openspec validate` into the edge dispatch; delete the orchestrator's instruction to invoke them (design D4). `scripts/sdlc/readiness-gate.py` exposes the same `problems(path, repo)` contract as `validate-proposal.py`, and the sdlc descriptor declares it under `edge_checks` keyed by `readiness-verdict.json`. `check-edge.declared_checks` dispatches from the descriptor rather than from `if path.name == ...`, so a workflow adds a checker without editing the shared hook. A declared script that is missing or that raises becomes a *problem*, never a skip — the code that runs the gates is the one place the inert-gate failure must not return. A missing `openspec` CLI blocks instead of passing by absence. SKILL.md now states that the hook runs them and the orchestrator does not.
- [x] 4.6 `schemas/readiness-verdict.schema.json`: the fixed three verdicts, findings with evidence, and an attacks floor of 3 — a verdict reached without attacking anything is not a review. The first draft carried a `gates` field recording lint-story and openspec results; that is a node witnessing its own guardrail, which D4 and D5 put on the edge, so it was removed before commit
- [x] 4.7 Harness applying the fixed verdict rules in the substrate, not the orchestrator (design D5). `scripts/workflow/verdict.py`: SURVIVED advances, REFUTED reruns the producing node and twice on one target is a punch-out (REFUTE_LIMIT = 2, the same number as delivery-flow's loop bound rather than a second one meaning the same thing).

      **WEAKENED differs between the two workflows, so the policy is declared not decided.** delivery-flow documents "a verdict of WEAKENED never blocks"; D5 says WEAKENED requires every finding addressed. Both are right for their own pipeline — one feeds a brief a human reads, the other feeds a build — and a shared harness imposing either would have silently changed one. Each descriptor now declares `verdict_policy.weakened`, delivery-flow explicitly `advance` so a default change cannot move it, and the default itself is `advance` because the workflow that predates this module must not change by its arrival.

      "Every finding addressed" is tested without inventing an artifact for it: the target must have been rewritten since the verdict, which is the staleness rule delivery-flow already applies to challenges. Unchanged stories mean nothing was addressed, whatever anyone claims; rewritten ones mean the verdict no longer describes what is on disk, so the reviewer runs again. There is deliberately no path from WEAKENED to advance that skips a fresh verdict — self-reported resolution is the claim an edge exists to not take on trust.

      Two cases that block rather than guess: an unreadable or unrecognised verdict (treating it as SURVIVED would advance a build on a malformed artifact; as REFUTED would rerun a node that may have been right), and SURVIVED carrying findings, which is a reviewer saying the artifact both stands and has defects.


## 5. Certify the readiness segment

- [ ] 5.1 `prompt-edd` package for `story-planner`: ≥3 distinct criteria, ≥95% of asserts, a
      load-bearing map covering ≥90% of instructions, a real iteration log
- [ ] 5.2 Haiku first; escalate only with a committed results file showing haiku below the bar on
      the same suite (design D7)
- [ ] 5.3 Decide Open Question 4: reuse `evals/cross-examine/` for the readiness reviewer or
      build its own suite. If reusing, strengthen the reasoning asserts first — that suite is
      currently weighted toward output format
- [ ] 5.4 `prompt-edd` package for the readiness reviewer, same bar, fresh context, refute-framed
- [ ] 5.5 Three consecutive passing runs per node; record each certified prompt's sha in
      `steps.yaml` so an edit forces recertification
- [ ] 5.6 Flip `readiness` to certified; confirm delegation is now permitted and that editing
      either prompt re-blocks it

## 6. Punch-outs and attack evidence

- [ ] 6.1 Define sdlc's punch-out triggers in its descriptor: phase gates, protected paths,
      unattended-mode ceilings
- [ ] 6.2 Generalise `tests/delivery-flow/bypass/run-bypass.py` to run against any registered
      workflow's gates
- [ ] 6.3 Run it against sdlc's gates. Record every hole it finds and fix them — the delivery-flow
      run found 3 real holes in 15 attacks, so expect holes rather than a clean sheet
- [ ] 6.4 Commit the bypass report as the punch-out evidence artifact
- [ ] 6.5 Verify `check-protected-paths.py` is reachable from the generalised substrate and still
      fails a run on violation

## 7. Audit trail and success rate

- [ ] 7.1 Confirm the trace records, per step: model actually used, tokens, cost, artifact sha,
      edge verdict
- [ ] 7.2 `write-outcome.py` distinguishing `completed` / `punched-out` / `failed` / `abandoned`
      for sdlc runs, emitting both punch-out denominator readings (design D8)
- [ ] 7.3 Manual-correction detection: artifact sha vs trace sha, run marked `failed` with reason
      `manual-correction`. Verify by deliberately hand-editing a story to force a gate pass
- [ ] 7.4 A per-segment report; **do not** promise a thirteen-node pipeline rate (design risks)
- [ ] 7.5 Real runs at story granularity until the readiness rate is meaningful. Evals guard
      regressions; only real runs produce the rate

## 8. Documentation, in the same PR

- [ ] 8.1 `docs/using-the-sdlc-dev-team.md`: segments, the composition rule, the data contract
- [ ] 8.2 Figures: `readiness-gate`, `sdlc-pipeline`, `human-gates` — keep the colour language
      (purple human gate, amber deterministic script, teal LLM checker, coral build,
      red/green dev pair)
- [ ] 8.3 Mirrors per `CLAUDE.md`: `agents/README.md`,
      `skills/sdlc-orchestration/SKILL.md`, `skills/prime/` team bindings
- [ ] 8.4 Fix the model-policy line: "separate, stronger model" → checker differs from generator,
      haiku-first (design D7)
- [ ] 8.5 `evals/README.md` if the substrate changes how suites are wired
- [ ] 8.6 Record in `skills/workflow-certification/` that composition is this project's reading
      and whether a reviewer confirmed it
