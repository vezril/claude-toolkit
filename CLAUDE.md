# claude-toolkit — project instructions

## Keep the SDLC workflow docs in sync

Any change to the SDLC team workflow — agents added/split/renamed, gates added or
reordered, enforcement mechanisms changed (`hooks/enforce-dev-pair-boundary.py`,
`scripts/lint-story.py`), phase routing rewired — is **incomplete until the
documentation is updated in the same commit/PR**:

- `docs/using-the-sdlc-dev-team.md` — the playbook (cast tables, phase walkthroughs,
  worked example, cheat sheet).
- `docs/figures/*.svg` — the workflow diagrams embedded in the playbook
  (`sdlc-pipeline`, `solutioning-phase`, `readiness-gate`, `implementation-dev-pair`,
  `human-gates`). They are hand-written, self-contained SVGs; edit the affected one(s)
  to match the new shape and keep the color language: purple = human gate,
  amber = deterministic script, teal = LLM checker, coral = build,
  red/green = the test-writer/implementer pair.
- The mirror files that repeat the workflow wiring: `agents/README.md`,
  `skills/sdlc-orchestration/SKILL.md`, and the team bindings in `skills/prime/`.

The pipeline's own rule is "artifacts drive state" — stale workflow docs break it.

## Related consistency rules

- The dev pair's file-territory definition lives in three places that must stay
  identical: `agents/test-writer.md`, `agents/implementer.md`, and the classifier in
  `hooks/enforce-dev-pair-boundary.py`.
- The story file format is normative: `skills/spec-driven-development/references/story-schema.md`
  and `scripts/lint-story.py` must change together.
