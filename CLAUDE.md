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
  `human-gates`, `human-gates-unattended`). They are hand-written, self-contained SVGs; edit the affected one(s)
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
- The unattended-mode policy lives in three places that must stay consistent:
  the "Unattended mode" section of `skills/sdlc-orchestration/SKILL.md`, the Modes section of
  `agents/sdlc-orchestrator.md`, and the reference templates in `templates/unattended/`.
- `scripts/check-protected-paths.py` parses the `protected_paths:` block format of
  `templates/unattended/unattended-policy.yml` — change the format and the parser together.
- `load_profiles` in `scripts/delivery-flow/common.py` parses
  `templates/delivery-flow/profiles.yaml` — change the format and the parser together. The
  profiles' steps must also stay in step with the `STEPS` table in
  `scripts/delivery-flow/flow-status.py`; `tests/delivery-flow/test_profiles.py` asserts that
  every profile step exists in the table and that no table step is left out of every profile.
- The brief's template and its edge check share
  `scripts/delivery-flow/brief.py` — `render-brief.py` and `hooks/check-edge.py` both import
  it so the renderer and the checker cannot disagree about what an identifier is.
- The derived punch-out triggers live only in `scripts/delivery-flow/triggers.py`, imported by
  both `scripts/delivery-flow/check-punch-out.py` and `hooks/check-edge.py`. The ceilings are
  config (`punch_out.*` in `.delivery-flow.yaml`), documented in
  `skills/delivery-flow/references/config.md` — change the keys and that reference together.
- The adapter contract lives in `scripts/delivery-flow/common.py`: `Usage`/`Remote` and
  `dispatch` are the exit codes, `emit` is the stdout format, and `outward_refusal` is the
  one definition of "blocked" that every adapter's `comment`, `transition` and `open-pr`
  consults. Adapters map remote fields; they never re-decide policy. The contract and each
  adapter's field mapping are documented in `skills/delivery-flow/references/adapters.md` —
  change a mapping and change that reference.
- `load_roster` in `scripts/delivery-flow/common.py` parses
  `templates/delivery-flow/roster.yaml`, whose closed vocabulary of work kinds is repeated in
  `skills/delivery-flow/references/roster.md` and in `tests/delivery-flow/test_roster.py`.
  All three change together. Every agent and skill the roster names must exist on disk; the
  test is what enforces it.
