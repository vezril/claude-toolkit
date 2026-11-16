## 0. Sequencing notes — not a gate

**Dropped, 2026-10-29: "nothing lands before the Stage 4 submission is accepted" was my
invention, not a requirement from the deck or a reviewer.** It blocked Calvin from doing his
day job — feeding delivery-flow output into the orchestrator — for a risk that does not need a
freeze to manage. What design D2 actually warrants is narrower: **do not restructure the files
already submitted** (sections 1 and 2, the substrate extraction and hook generalisation) while
a submission is open. Additive work that leaves the submitted tree where it is may proceed,
and section 3 is exactly that.

- [~] 0.1 SPENT, 2026-11-11 — the constraint has nothing left to protect. Sections 1–2 landed as
      PR #113 and sections 3–8 as PR #128, both merged; there is no open submission whose tree
      could be restructured underneath it. Kept in the list rather than deleted because the
      narrowing it records (additive work proceeds; do not relayout a submitted tree) is the
      reusable part, and the next submission will want it again
- [ ] 0.2 **BLOCKED on a human — this is the change's one load-bearing unknown.** Ask the
      reviewer Open Question 1: is a pipeline of certified 2–3 node segments joined by
      deterministic edges certifiable *segment by segment*? The assumption is mine, not the
      deck's. A "no" does not undo what shipped — per-segment certification is the submittable
      unit either way — but it retracts the pipeline-level claim, which is why
      `skills/workflow-certification/SKILL.md` already records the rule as unconfirmed and
      `delivery-report.py` refuses a pipeline-wide rate
- [ ] 0.3 **BLOCKED on a human.** Ask Open Question 2: do knowledge skills loaded as context need
      their own certification? sdlc loads many more than delivery-flow, so the answer changes
      the cost. Nothing shipped depends on the answer; it sizes the work after `readiness`
- [~] 0.4 RETIRED, 2026-11-11 — a pre-extraction baseline recorded *after* the extraction merged
      is not a baseline, it is a measurement with nothing to compare against. The function was
      served at the time by 1.4, which recorded 532 delivery-flow tests green and unchanged
      across every slice plus the bypass suite at 24/24 blocked, and that is the comparison this
      task existed to enable. Ticking it now would be back-dating evidence
- [x] 0.5 Both confirmed by execution, 2026-11-11. `lint-story.py` over a story set whose file
      has no `# Story {epic}.{n}:` heading exits **1**, naming all eight violated rules and
      printing `GATE: FAIL`. `openspec validate` (v1.15.0) over a change directory whose
      `specs/thing/spec.md` carries no delta header exits **1** with
      `✗ [ERROR] ... No delta sections found` and `No deltas found`. Neither passes by absence —
      and `scripts/sdlc/readiness-gate.py` treats a missing `openspec` CLI as a failure for the
      same reason

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
- [~] 3.3 RETIRED, 2026-11-11 — the premise died with the rest of section 3. "Schema validation
      plus the semantic checks a schema cannot express" presupposed `schemas/story.schema.json`
      and a second, JSON story format; both are gone, so there is no schema half to rewrite and
      a JSON schema cannot validate markdown. `lint-story.py` already enforces the whole of
      `story-schema.md` — structure, Given/When/Then grammar, task↔AC closure in both
      directions, `[Source:]` resolution and FR/CAP traceability — which is the entire list this
      task asked for. The scope note it carried ("`story-schema.md` now says so in a Scope
      section") was also false: no such section existed, and with one format there is nothing
      for it to scope. What *was* actually wrong in these files is fixed under 3.6
- [~] 3.4 RETIRED — `render-story.py`: generate `story.md` from `story.json` for human readers; never
      parsed. **Deferred and demoted to a convenience.** It was implicitly the plan for making
      the handoff work, and it is not needed for that: the dev pair consumes `story.json`
      directly (3.7), so nothing blocks on a markdown rendering. Worth building only when a
      human wants to read a story outside an editor — and it must stay unparsed, because a
      markdown story that `lint-story.py` could accept would have to carry invented tasks and
      `FR`/`CAP` IDs
- [~] 3.5 RETIRED, 2026-11-11 — a migration needs a destination. It was to convert markdown
      stories into `story.json`, which no longer exists and which nothing would read. Markdown
      stories are not broken and need no conversion; the format they already satisfy is the
      surviving one
- [x] 3.6 Done, and the real content was not what this task anticipated. The pair is intact
      (`story-schema.md` + `lint-story.py`, no `story.schema.json` to add), but both still
      described the **pre-4.5** gate, and so did two files nobody had listed as mirrors:
      - `story-schema.md` claimed the linter "runs before any LLM review" and is "layer zero".
        That ordering is now **inverted**: the `readiness` segment is `readiness` →
        `readiness-review`, and the reviewer's write of `readiness-verdict.json` is what fires
        the check. Rewritten as "an edge check, not an instruction", stating the narrower
        guarantee a `PostToolUse` hook can actually make — the failure is recorded and advancing
        past it is refused — instead of "no LLM review runs on a malformed set", which is no
        longer true
      - `scripts/lint-story.py`'s docstring, same correction, plus its three real callers (the
        edge, standalone use, and `evals/readiness-stories/`'s `schema` criterion)
      - `skills/spec-driven-development/SKILL.md`, same
      - **`agents/story-planner.md` was the worst of the four**: it told the planner "the
        orchestrator runs **two deterministic validators**" — the exact instruction 4.5 deleted
        for being no guardrail — so the agent whose output the gate judges was documented
        against a gate that no longer works that way
      Root cause: section 8's mirror list was hand-maintained and scoped to the pipeline's own
      docs, so four files under `spec-driven-development/` and `agents/` were never in it.
      `tests/workflow/test_documentation_mirrors.py` gains
      `TestTheStoryContractMirrorsAgreeWithTheEdge`, which derives the obligation from the claim
      — any file naming the linter must name what dispatches it, none may claim the pre-4.5
      ordering, and a mention of `story.json` must say it is retired
- [x] 3.6b The change's own spec deltas said the retired thing, which `openspec archive` would
      have promoted into the living specs. `specs/sdlc-story-contract/spec.md` was six ADDED
      requirements about `story.json`, `schemas/story.schema.json`, `story.md` and the renderer
      — rewritten to the markdown contract, the OpenSpec change as the handoff, the semantic
      checks, and the normative pair. Separately, 4.5 changed behaviour the **living** spec
      `openspec/specs/sdlc-solutioning-openspec/spec.md` describes ("short-circuit ... before any
      LLM alignment review runs") and the change had no delta for it, so a new
      `specs/sdlc-solutioning-openspec/spec.md` carries the `## MODIFIED Requirements` that
      corrects both who runs the gate and when. `openspec validate certify-sdlc-pipeline` clean
- [~] 3.7 RETIRED — Update `test-writer` and `implementer` prompts to consume `story.json`. Each gained a
      "When the story is a `story.json`" section: `acceptance_criteria[]` is the spec,
      `sources[]` is context to **open** rather than a summary to trust, there are no tasks and
      no dependency order, and a missing criterion is a gap in the plan to raise rather than
      infer. Territory definition untouched, so the three-place agreement
      (`agents/test-writer.md`, `agents/implementer.md`, `hooks/enforce-dev-pair-boundary.py`)
      still holds — the boundary is by file path and a `story.json` is read, never written, by
      either agent
- [x] 3.8 Open Question 5 resolved by dissolution, 2026-11-11: **stories did not become data**,
      so the condition the question was asked under never arrived. Dev-pair territory stays
      path-based, and the three-place agreement `CLAUDE.md` requires — `agents/test-writer.md`,
      `agents/implementer.md`, `hooks/enforce-dev-pair-boundary.py` — is unchanged and still
      holds. Worth recording *why* it would have held even on the retired path: a story is read
      and never written by either agent, so no story file falls in either territory whatever its
      format. The question was about the wrong risk

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

- [x] 5.1 `evals/readiness-stories/`: three changes, four criteria, 11 asserts, gate-clean. The `schema` criterion shells out to `scripts/lint-story.py` — the same script the readiness edge runs — rather than carrying its own copy of the rules, which could pass a set the edge rejects. Asserts mutation-tested both ways before any model run: they accept a hand-written reference answer and each fails on the defect it owns
- [x] 5.2 Haiku first, and haiku certified both readiness nodes, so no escalation needed. The reviewer's *other* suite (`evals/cross-examine/`) did measure haiku below the bar — 100%, 100%, 83.3%, failing by using endorsement vocabulary on an analysis it was required to refute — and that file is committed as D7 evidence even though the node it would have justified is now certified on its own suite instead
- [x] 5.3 Open Question 4 answered twice, because the first answer was wrong. **Do not reuse `evals/cross-examine/`.** Its criteria design is reused — contract / accuracy / safety with a sound case as the false-positive test — but it feeds an incident ticket and a timeline and expects markdown, while this node is handed a story set and must emit `readiness-verdict.json`. I first ruled 'reuse' on the strength of its per-criterion breakdown without checking the input and output domains; certifying a node against inputs it never sees in production is the same error as certifying a prompt the suite never saw. Design D5's claim that the suite tests reasoning lightly is separately false: 4 of its 6 asserts are reasoning
- [x] 5.4 `evals/readiness-review/`: three cases — a set that stands, one with a dropped requirement, and one where the requirement is traced and delivered by nothing observable, which is the defect that looks like coverage and the reason the reviewer is a node rather than a script. `contract` validates against the real `readiness-verdict.schema.json` via `validate-artifact.py`. Fresh context and no tools: the reviewer judges only the material it is given
- [x] 5.5 Three consecutive passing runs recorded for each node, with the prompt sha in `steps.yaml` and a frozen `certified_version` the gate compares against — so editing either live prompt un-certifies its step. The rule earned its place twice: `readiness` v1 passed two runs then scored 83.3%, and `readiness-review` v3 passed one arm and failed the other on identical input. A single run would have certified both
- [~] 5.6 Both `readiness` nodes are certified and the gate agrees — `PASS readiness: haiku 11/11, 4 criteria, load-bearing 19/19, 3 iterations, 3 consecutive runs` and `PASS readiness-review: haiku 7/7, 3 criteria, load-bearing 18/18, 4 iterations, 3 consecutive runs`. A test asserts the segment's nodes are all certified and that each live prompt still matches its frozen copy.

      **Still open:** confirming at runtime that delegation is now permitted and that editing a prompt re-blocks it. The gate says so statically; nothing drives the orchestrator through the segment yet, and that needs section 7's harness.

## 6. Punch-outs and attack evidence

- [x] 6.1 Declared in `skills/sdlc-orchestration/workflow.yaml` under `punch_out`: four `human_gates` (analysis, planning, readiness, verification), the trigger kinds this workflow raises, and the ceilings. The gates are not invented — they are the approvals `docs/using-the-sdlc-dev-team.md` already documents, moved from prose a model has to remember into data the machinery reads, for the same reason task 4.5 moved the readiness gate onto a hook. Per-repo values live in `templates/sdlc/sdlc.yaml`, whose `protected_paths` ships non-empty with the pipeline's own config in it: a run that can edit its own guardrails has none.

      Found by doing this: the descriptor parser returned `retry_limit` as the string `"3"`. Nothing in the delivery-flow descriptor is numeric so the gap had stayed invisible, and a ceiling that is quietly a string compares wrongly against an int and raises on arithmetic — failing at the point of use, far from the parse. `_scalar` now parses numbers, and a quoted `"3"` still reads as text
- [x] 6.2 Parameterised in place by workflow rather than split across files: `PROFILES` names each workflow's config file, artifact directory, item key, guarded artifact and attack set, and the profile travels inside the fixture dict so `state()` and `judge()` reach it without threading an argument through every call site. `--workflow` selects it.

      Not split because this suite *is* criterion 3's evidence, and a 659-line refactor across a new import graph risks the artifact for a tidier shape. One report covering both workflows is also what a reviewer wants to read.

      Verified without model calls first: both fixtures build, neither leaves a stray config, the trace shas match the artifacts on disk, the hooks are wired, and delivery-flow's untouched-fixture triggers are still exactly `architecture, scope` — the same pair its existing report records. Two bugs in my own patch were caught that way: both branches wrote to the same config path so delivery-flow's overwrote sdlc's, and `.current-step` was left in the wrong function
- [x] 6.3 Run against sdlc's gates. **Four breaches of six**, and three were one bug.

      `enforce-punch-outs.py` recognised an sdlc repo — task 2.3 generalised its gate — and then every lookup inside it used `common.artifact_root(repo)` and `common.load_config(repo)`, which hard-code `delivery` and `.delivery-flow.yaml`. For an sdlc repo the root does not exist, `open_punch_outs` found nothing, and the hook permitted everything. **It reported nothing, because "no punch-out is open" and "I looked in the wrong place" produce the same silence.** Right checker, wrong input — the sixth instance of that class this week and the most consequential, since the control it disabled is the one that stops an agent writing its own decision.

      Fixed by resolving the descriptor and using `layout.artifact_root` with the workflow's own directory and config. Six call sites. Re-run: **5 of 6 blocked**, with decision-write (tool and shell), `decide.py` invocation and merge-during-punch-out all holding.

      The remaining breach is **a missing control, not a broken one**, and is recorded as such: `grep protected` finds nothing in `enforce-punch-outs.py` — protected paths are enforced by `scripts/check-protected-paths.py` in CI, after the fact. So an agent editing `.sdlc.yaml` to remove its own protected-path list is not stopped at the point of the write. Claiming that as a bug I fixed would be wrong, and claiming the hook covers protected paths would be worse
- [x] 6.4 `tests/delivery-flow/bypass/bypass-report-sdlc.md` and its `.results.json`, committed as the punch-out evidence for this workflow alongside delivery-flow's. 5 of 6 blocked, 1 breached, with the breach's cause named as an absent PreToolUse control rather than a failure of an existing one
- [x] 6.5 `scripts/check-protected-paths.py` was **not** reachable from a punch_out-nested config, which is exactly what this task existed to find. It matched `protected_paths:` only at column 0 — the shape `templates/unattended/unattended-policy.yml` uses — while `.delivery-flow.yaml` and `templates/sdlc/sdlc.yaml` nest the same key under `punch_out:`. On either of those it found no block.

      It was caught only because an empty list exits 2, "refusing to pass by absence", rather than permitting everything. That line is the reason this was a finding instead of a silent hole, and it is what the new tests defend hardest.

      The parser now matches the key at any indentation and ends the block at the next sibling key; both config shapes read, and both still fail a run on violation. 10 tests in `tests/workflow/test_protected_paths.py`, including that the sdlc policy protects its own `.sdlc.yaml`, that ordinary edits still pass, and that a policy with no block is an error rather than a pass

## 7. Audit trail and success rate

- [x] 7.1 Confirmed against real traces on disk rather than from the hooks' source, because the question is what ended up recorded. Four of the five facts are there; two defects were not.

      **`trace-step` records carried no `hook` field** while `check-edge`'s did, so 93 of AN-3702's 127 records were anonymous and anything grouping by author dropped every step record into an unlabelled bucket — including the first version of my own audit script, which reported "model: NO" for every step while the data sat right there. Both of the hook's record shapes now name it, the error shape included: an anonymous error record is a failure nobody can attribute.

      **`claude-haiku-5-5` is not in the pricing table** (it covers `claude-haiku-4-5`), so every haiku step records `api_equivalent_cost_usd: null` with `pricing_missing: true`. The flag is the right behaviour — a guessed price is worse than none — but this is the tier design D7 pushes work toward, and both readiness nodes are certified on it, so criterion 4's cost figures currently omit the cheapest and most-used tier. **Needs a published price, which I will not invent.** A test asserts the gap exists so it cannot be forgotten, and says to delete itself once a real price is added.

      11 tests in `tests/workflow/test_audit_trail.py`, including that `cost_usd` returns None rather than 0 for a row it could not price: zero and unknown are different claims, and a report adding them together under-reports while looking complete.

      Also observed while auditing, not fixed here: AN-3702 carries a `step: "orchestrator"` record at $9.91 with `certified: false` — the orchestrating session's own usage attributed as a pipeline step. That is the attribution problem the status doc already records, and it inflates any per-step cost built from these traces.
- [x] 7.2 All four statuses already worked — for delivery-flow. On an sdlc repo `write-outcome.py`
      gated on `is_delivery_repo` and exited 2, so an sdlc run could never be closed out at all,
      and a profile that cannot write a terminal artifact is indistinguishable from one that
      stalled. It failed *honestly*, unlike the enforcement hook in 6.3, which recognised the
      repo and then looked in the wrong directory.

      Now resolves the active workflow from the descriptor and reads its own config, item dir
      and profiles through it. `flow-status.by_step(table)` was added so a profile can be
      resolved against a second workflow's routing table rather than delivery-flow's, which is
      all `profile_steps` could reach before.

      Both punch-out denominator readings turned out to be a *report* concern, not a field on
      `outcome.json` — `delivery-report.py` already emitted them, so the work landed in 7.4.

      10 tests in `tests/workflow/test_sdlc_outcome.py`, mutation-checked: four deliberately
      broken detectors, all killed.
- [x] 7.3 Verified by the hand-edit, not by reading the code: a `WEAKENED` verdict that blocks,
      rewritten to `SURVIVED` after its edge had already recorded the sha of what it saw. The run
      is `failed` with reason `manual-correction` and names the artifact, while the artifact
      itself now looks perfect. The opposite direction is tested too — a clean run must not be
      accused, or every outcome is `failed` and the signal is worthless.
- [x] 7.4 Two defects in `delivery-report.py`, both the section 5/6 class — present, successful,
      checking nothing. The numbers come from this file.

      **It could not see an sdlc run.** `trace_files` gated on `is_delivery_repo` and globbed a
      hard-coded `delivery/`. Loud rather than silent (`main` exits non-zero on no items instead
      of printing 0%), but "no runs exist" and "this report cannot see the runs that exist" are
      different facts. Now resolves each declared workflow's `artifacts.root` — with
      `common.parse_mapping`, since the descriptor parser returns a flat mapping and every
      absolute artifact root was quietly falling back to `<repo>/<artifact_dir>`, which exists
      for nobody who configured a root outside the repo. That one only showed up under a test
      whose artifacts were in a vault rather than in-repo.

      **An unrecognised uncertified step was waved through the certification claim.**
      `certifiable()` asked whether the step's kind was in `CERTIFIABLE_KINDS`; a step absent
      from the table answered `False` — identical to a deterministic producer — so it was *set
      aside* and the run still counted toward the certified-only rate. Invisible while
      delivery-flow's sixteen steps were the whole table. With two workflows every sdlc node was
      unknown, and worse: the sdlc table is keyed by **segment** while the trace records the
      **node**, so even reading both descriptors left all eleven node names unrecognised. The
      role is now tri-state (`node` / `deterministic` / `unknown`), unknown disqualifies, and
      `unknown_steps` is reported separately from `excluded_from_certification` — one bucket is
      how the first version hid this. The deliberate `orchestrator` exclusion is a closed named
      set, guarded by a test, so it cannot grow back into a fallback.

      Per-segment rather than end-to-end: `segment_certification()` reads the registry's
      `certified:` flags and a segment counts as certified only when **every** node in it is.
      The report names `readiness` as the one certified sdlc segment, names the other five as
      outside any claim, and states in words that **no end-to-end rate is asserted** for a
      pipeline containing an uncertified segment. An unreadable registry reports `unknown`, not
      certified.

      21 tests in `tests/workflow/test_report_certification.py`; five mutants including a full
      revert to the pre-fix two-answer `certifiable`, all killed.

      Found on the way: `tests/workflow/test_readiness_gate.py` permanently repointed the shared
      `descriptor.PLUGIN_ROOT` at a temp directory, so every later test in the same run saw a
      plugin with no workflows in it. Only the tests resolving an artifact root two modules away
      noticed. Now restored with `addCleanup`.
- [ ] 7.5 Real runs at story granularity until the readiness rate is meaningful. Evals guard
      regressions; only real runs produce the rate

## 8. Documentation, in the same PR

- [x] 8.1 New "Segments" section in the playbook: why the pipeline is cut up at all (the unit is
      2–3 nodes; this pipeline is eleven), the four properties a segment must have, the six
      segments with their real node names and hand-off artifacts, and the composition rule
      stated as a rule. Three limits are stated rather than buried: it is this project's
      reading and **unconfirmed**, a `PostToolUse` hook cannot un-write a file, and no
      end-to-end rate is claimed.

      The data contract is the mechanical version — *if a node consumes it, it has a schema; if
      only a human reads it, it can be prose* — with the consequence that bit me in section 7
      spelled out: `readiness` hands off **markdown stories plus a schema-backed verdict**, not
      a `story.json[]` set. D1 and D3 describe the design; the renderer was built and retired,
      and the doc now says which one shipped.

      Phase 3 step 4 was rewritten for the same reason: it described the validators as layers
      the orchestrator runs *before* the LLM review. The real order is node → node → edge, and
      the edge fires on the verdict's write.
- [x] 8.2 `sdlc-pipeline.svg` redrawn as the six segments with per-segment certification badges
      and the edge/punch-out between each; `readiness-gate.svg` redrawn to the actual mechanism
      (the review node writes the verdict, *that write* fires `check-edge.py`, which dispatches
      the declared check) — the old figure drew the validators as a step before the review;
      `human-gates.svg` reordered to match and given the missing `openspec archive` gate.
      Colour language kept, and purple now appears in `readiness-gate.svg`, which previously
      had a human approval with no human colour on it.

      A checker (`/tmp` throwaway) verified all six figures are well-formed XML and that nothing
      is drawn outside its `viewBox`. Its first version could not fail: it measured the
      full-canvas background rect, so every figure looked exactly as tall as its own viewBox.
- [x] 8.3 `agents/README.md` and `skills/prime/SKILL.md` updated; `skills/sdlc-orchestration/SKILL.md`
      covered by 8.4.

      **`agents/sdlc-orchestrator.md` still instructed the orchestrator to run
      `lint-story.py` and `openspec validate` itself** — the exact instruction task 4.5 moved
      onto a hook *because* an instruction is not a guardrail. The skill had been updated and
      the agent had not, so the two mirrors disagreed about whether the gate was the
      orchestrator's job. Found by the new test, not by reading.

      `prime` now reports two things it was silent about: whether the repo actually opts in (a
      `.sdlc.yaml` at the root — a filesystem fact, not an assumption) and which segments are
      certified, since that is what decides whether anything can run unattended.
- [x] 8.4 Wrong in both halves, and fixed in all six places that asserted it. *Independence* is
      the mechanism — a different model **or** the same model in a fresh context with a
      refute-framed prompt — and *tier* runs the opposite way to what the line implied: haiku
      first, sonnet next, frontier only with a committed results file showing the cheaper tier
      below the bar on the same suite. Both certified readiness nodes run on haiku.

      `skills/requirements-engineering/SKILL.md` and
      `skills/agentic-workflows/references/patterns-and-frameworks.md` carried the same claim by
      citation and were corrected too; a test now fails on any file that prescribes a stronger
      model, allowing it only where the old wording is quoted in order to correct it.
- [x] 8.5 It does. Node-prompt suites are wired differently from skill suites, and the README
      only documented the latter: the prompt is a versioned file rather than a `SKILL.md`, and
      `steps.yaml` binds the suite to the running prompt by sha so that **editing a node prompt
      un-certifies the step**. Also recorded: certifying against inputs the node never sees in
      production is the trap (the `cross-examine` near-miss), the three-consecutive-runs rule at
      the cheapest passing tier, `load-bearing.md` / `iteration-log.md` as required artifacts
      whose five labels are counted so a fixed *assert* cannot pass as prompt development, and
      that a green score deserves suspicion — `score.js` once printed PASS at 100% on a run
      where four of six cases had errored.
- [x] 8.6 Recorded in `skills/workflow-certification/SKILL.md` as a named section, with the rule
      stated and its status stated next to it: **unconfirmed — no reviewer has been asked**, and
      nothing in the course text addresses composition either way. What survives if it is
      rejected is named (the per-segment certification, which is submittable regardless), along
      with the three things that keep the gap honest meanwhile: uncertified segments are blocked
      from unattended delegation rather than merely labelled, no end-to-end rate is reported,
      and the caveat is repeated in the playbook where omitting it would have been convenient.
- [x] 8.7 `tests/workflow/test_documentation_mirrors.py` — 24 tests reading the descriptor and
      the registry and requiring the docs to agree. Added because `CLAUDE.md`'s "docs change in
      the same commit" rule was itself prose, and prose is what nobody re-reads; it is what
      caught the stale orchestrator agent in 8.3.

      Seven mutants, all killed — but two survived the first pass and both were my fault: one
      mutant was a no-op (it added a comment instead of flipping `certified:`), and one test was
      genuinely weak (it searched the whole file for "unconfirmed", a word that also appears in
      a passing mention, so deleting the actual status declaration left it green). The test now
      asserts on the status line itself.
