# Story file schema (normative)

The machine-checkable contract for story files. `scripts/lint-story.py` enforces exactly this;
the story-planner writes to it; the readiness gate short-circuits on violations. Prose guidance
lives in the skill body — this file is the format law. Keep the three in sync.

## Required structure

```markdown
# Story {epic}.{n}: {title}
Status: {non-empty, e.g. draft | ready-for-dev | in-progress | done}

## Story
As a {role}, I want {action}, so that {benefit}.

## Acceptance Criteria
- AC-1: Given {context}, when {action}, then {outcome}.
- AC-2: [ ] {testable checklist item}          <!-- checklist form, unless --gwt-only -->

## Tasks / Subtasks
- [ ] {task} (AC: 1)
  - [ ] {subtask — no AC ref required}
- [ ] {task} (AC: 1, 2)

## Dev Notes
- {constraints / patterns from the architecture}

### References
- [Source: docs/prd.md#FR-3]
- [Source: docs/architecture.md#api-patterns]

## Dev Agent Record
{optional at planning time — filled during implementation}
```

## Rules the linter enforces (errors — any one fails the story)

1. **Title**: first heading is `# Story {epic}.{n}: {title}` (e.g. `# Story 1.2: Verify TOTP at login`).
2. **Status**: a `Status:` line (or `## Status` section) with a non-empty value.
3. **Story statement**: the `## Story` section matches `As a …, I want …, so that …`.
4. **Acceptance criteria**: `## Acceptance Criteria` has ≥ 1 item of the form `- AC-{n}: …`; IDs unique.
   Each AC is **either** Given/When/Then (contains the words *given*, *when*, *then* in that order;
   may span multiple lines until the next AC) **or** an explicit checklist item (`- AC-n: [ ] …`).
   With `--gwt-only`, checklist form is rejected too.
5. **Task ↔ AC mapping is closed**: `## Tasks / Subtasks` has ≥ 1 top-level checkbox task; every
   top-level task carries an AC reference (`(AC: 1)`, `(AC: 1, 2)`, `(AC-1)`); every referenced AC
   exists; every AC is covered by ≥ 1 task. Indented subtasks need no reference.
6. **Dev notes**: `## Dev Notes` section present.
7. **References resolve**: a `References` section (h2 or h3) has ≥ 1 `[Source: path#anchor]`; each
   `path` exists (resolved against `--root`, default cwd); each `#anchor`, when present, matches a
   heading slug in that file **or** appears literally in its text (covers `#FR-3`-style stable IDs).
8. **Traceability**: the story mentions ≥ 1 `FR-{n}` / `CAP-{n}` ID; if any referenced source file
   looks PRD-like (basename contains `prd`, `srs`, or `spec`), every mentioned ID must appear in
   one of those files.

Warnings (reported, non-fatal): missing `## Dev Agent Record`; FR/CAP IDs present but no PRD-like
source to verify them against.

## Gate semantics (short-circuit)

The linter is **layer zero of the readiness gate** and runs before any LLM review:

- exit `0` — lint-clean; the LLM alignment review (substance: are the criteria *meaningful*?) may proceed.
- exit `1` — **the gate fails immediately**; the orchestrator returns the report to the story-planner
  for rewrite (bounded — ~3 iterations, then escalate to the human). No LLM review, no approval,
  no implementation on a lint-dirty set.

The split is deliberate: the script owns *form* (deterministic, reproducible), the reviewer owns
*substance*. A vacuous-but-well-formed criterion ("given the system, when used, then it works")
passes the linter by design — catching it is the LLM/human reviewer's job.

## Usage

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint-story.py" stories/ --root .
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint-story.py" stories/1-2-verify-totp.md --root . --gwt-only
```
