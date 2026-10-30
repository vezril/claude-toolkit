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

- [ ] 1.1 Create `scripts/workflow/` with the workflow-agnostic core moved out of
      `scripts/delivery-flow/`: registry loader, profile-aware router, trace append, edge
      dispatch, outcome writer, `check-certification.py`, signature/pricing helpers
- [ ] 1.2 Define the workflow **descriptor** (`workflow.yaml`): step table, schema dir, artifact
      root, profiles, punch-out triggers, model policy
- [ ] 1.3 Reduce `scripts/delivery-flow/` to delivery-specific steps; leave the existing module
      paths as thin re-export shims so no import in the submitted tree changes
- [ ] 1.4 `pytest tests/delivery-flow/` green with **zero behavioural diff**; bypass suite still
      15/15 blocked. If either moves, the extraction is wrong, not the test
- [ ] 1.5 Descriptor resolution helper: given a repo, find the active workflow(s) or return none

## 2. Generalise the hooks

- [ ] 2.1 `hooks/check-edge.py`: resolve the descriptor instead of keying on
      `delivery/<ITEM-KEY>/` and `.delivery-flow.yaml`; stay inert with no descriptor present
- [ ] 2.2 `hooks/trace-step.py`: same, and keep recording the model a step *actually ran on*
      plus drift from the declared tier (design D7)
- [ ] 2.3 `hooks/enforce-punch-outs.py`: same, reading triggers from the descriptor
- [ ] 2.4 Both workflows' hooks exercised in one repo without interfering; add a test for a repo
      holding both descriptors
- [ ] 2.5 Confirm a repo with neither descriptor sees no behaviour change at all

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

- [ ] 4.1 `skills/sdlc-orchestration/steps.yaml`: six segments per design D1, each declaring
      nodes, terminus, hand-off artifact and schema, and a certification state
- [ ] 4.2 `sdlc/workflow.yaml` descriptor pointing at that registry
- [ ] 4.3 Mark every segment except `readiness` **uncertified**; verify
      `check-certification.py` blocks delegation to each one
- [ ] 4.4 Profiles for the segments so a run can be scoped to `readiness` alone and stop at its
      terminus with an `outcome.json`
- [ ] 4.5 Move the readiness gate's `lint-story.py` + `openspec validate` into the edge
      dispatch; delete the orchestrator's instruction to invoke them (design D4)
- [ ] 4.6 `schemas/readiness-verdict.schema.json`: `REFUTED` / `WEAKENED` / `SURVIVED` plus
      findings
- [ ] 4.7 Harness applying the fixed verdict rules — `REFUTED` reruns the producer, `WEAKENED`
      requires each finding addressed, `SURVIVED` proceeds — in the substrate, not the
      orchestrator (design D5)

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
