# SDLC orchestrator build — running status

Short and overwritten each session. Full spec is
`openspec/changes/certify-sdlc-pipeline/`. Last updated 2026-10-30.

## Where it stands

**8 of 58 tasks.** The story contract is done. The pipeline is not started.

| Section | State |
|---|---|
| 0. Sequencing | Gate dropped — it was invented, not required |
| 1. Substrate extraction | Not started |
| 2. Generalise the hooks | Not started |
| 3. Story as data contract | S.1–S.6, 3.1, 3.7 done. 3.2–3.6, 3.8 open |
| 4. Register pipeline as segments | Not started |
| 5. Certify readiness segment | Not started |
| 6. Punch-outs and attack evidence | Not started |
| 7. Audit trail and success rate | Not started |
| 8. Documentation | Not started |

## The one open decision

**Does `render-stories.py` survive?**

It works: a challenged `breakdown.json` renders to validated `story-*.json` with
sentinels, the dev pair knows the contract, the edge checks them.

But AN-3631 — the first real run — did not use it. The chain went breakdown →
propose → `tasks.md`, and propose *superseded* the rendered stories: S5 folded
into S1, S6 dropped as a story. `render-stories.py` is also not a step in any
profile, so its output lands in run directories the flow does not route. That is
what produced six edge-failing files that halted the run until they were parked.

Two ways out:

1. **Retire it.** Propose is the handoff; `proposal.json` + `tasks.md` is the
   sanctioned input. Retires S.1–S.6 and 3.4 instead of finishing them.
2. **Promote it.** Make it a real step before propose, registered in a profile
   with a schema'd artifact.

Recommendation: **retire it.** Propose already reconciles the challenge findings,
which the renderer cannot do — it is forbidden from changing anything the
breakdown said. Two sources of truth for the story set is the problem, not a
feature.

Everything in sections 4–7 is blocked behind this, because it decides what
section 3 is for.

## Done this session

- **S.5** — story-planner vs rendered path documented in three places
  (`skills/sdlc-orchestration/SKILL.md`, `agents/story-planner.md`,
  `docs/using-the-sdlc-dev-team.md`).
- **3.1 + 3.7** — `schemas/story.schema.json` made reachable, dev-pair prompts
  taught the `story.json` contract.
- **Three real bugs**, all found by running real data, none by the test suites:
  the story schema was unreachable (`artifact: "story.json"` vs real
  `story-E1-S1.json`), the renderer wrote no sentinels, and `proposal.json`'s
  change directory resolved against the vault instead of the repo. The last one
  was blocking the live run at propose.

Commits on `worktree-sdlc-story-seam`: `7a9a480`, `2aab6c1`, `ca61f29`. 488 tests
green.

## The finding worth keeping

Five defects today were the same class: **a gate that was present, reported
success, and was checking nothing.** Three were dispatch (right checker, wrong or
no input), one was a check bug, one was a declaration bug. Each subtype wants a
different test:

- dispatch → a boundary test ("does the checker run at all")
- check → the matcher tested against near-misses
- declaration → a test keyed to the *producer's* filename, not the registry's

My first attempt at the boundary test was itself inert: it iterated declared
names, so it passed while every real story went unchecked. Caught only by
mutating the code and expecting a failure that did not come.

`tests/delivery-flow/test_edge_dispatch.py` covers this. It also pins eight
routed artifacts that no checker covers — six `full`-profile JSON artifacts past
propose, plus `pr.md` and `post.md`.
