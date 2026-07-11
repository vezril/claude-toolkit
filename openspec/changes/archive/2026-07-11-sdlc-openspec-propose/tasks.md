# Tasks: sdlc-openspec-propose

> Docs ARE the implementation here; every task below is a doc-sync surface from CLAUDE.md.

## 1. Core wiring

- [x] 1.1 `skills/sdlc-orchestration/SKILL.md` — Phase 3 gains the OpenSpec propose step (container at Solutioning start, artifact→role mapping, distill-and-point rule); readiness-gate paragraph gains the `openspec validate` layer; Implementation gains the archive closing step
- [x] 1.2 `agents/sdlc-orchestrator.md` — Solutioning routing paragraph: open the change, artifact ownership, the two-layer deterministic gate (lint-story + openspec validate, same short-circuit), archive as the named closing step
- [x] 1.3 `agents/story-planner.md` — territory grows: delta specs + tasks.md inside the change, story files unchanged; rework loop now triggered by either validator

## 2. Playbook + figures

- [x] 2.1 `docs/using-the-sdlc-dev-team.md` — Phase 3 walkthrough rewritten around the propose flow; brownfield note promoted to the standard path; worked example + cheat sheet updated; archive step added to the Implementation section
- [x] 2.2 `docs/figures/solutioning-phase.svg` — change-container framing + propose artifacts; keep the color language (teal = LLM, purple = human gate)
- [x] 2.3 `docs/figures/readiness-gate.svg` — `openspec validate` amber box beside `lint-story.py`, same short-circuit arrow

## 3. Mirrors

- [x] 3.1 `agents/README.md` — wiring description matches 1.2/1.3
- [x] 3.2 `skills/prime/` — update Solutioning narration if present (bindings table is stack-only, likely untouched — verify)

## 4. Verify + ship

- [x] 4.1 Consistency grep: every file narrating Solutioning mentions the propose step and validate layer identically; no stale "stories are the only Solutioning artifact" phrasing anywhere
- [x] 4.2 SVGs render (open in browser), strict-YAML check on touched skills, `openspec validate sdlc-openspec-propose`
- [x] 4.3 Ship via git-ship (gated)
