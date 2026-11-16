# Load-bearing map — `prompts/prompt_v2.md` (readiness story-planner)

Which instructions in the prompt an assert actually depends on. Task 5.1's bar is **≥90% of
instructions load-bearing**: an instruction no assert exercises is either untested or
unnecessary, and a certification that cannot tell which is reporting on text nobody measured.

## The map

| # | Instruction | Assert that depends on it | Criterion |
|---|---|---|---|
| 1 | One `=== stories/<file>.md ===` block per story, nothing outside the blocks | `storyFiles()` finds no files and every criterion fails at its first line | all |
| 2 | `# Story <E>.<N>: <title>` as the first heading | `lint-story.py` `[title]` rule — **this is the assert v1 failed** | schema |
| 3 | `<E>` and `<N>` are digits, not the change name | the same rule; added in v2 after `# Story 2fa.1:` was rejected | schema |
| 4 | A `Status:` line | `lint-story.py` `[status]` rule | schema |
| 5 | `## Story` in `As a … I want … so that …` form | `lint-story.py` `[story]` grammar rule | schema |
| 6 | `## Acceptance Criteria` with `- AC-n:` items | `lint-story.py` `[ac]` rule | schema |
| 7 | Criteria in Given/When/Then order | `lint-story.py` `[ac]` ordering rule | schema |
| 8 | Criteria state observable outcomes, not test coverage | `decomposition` rubric: a criterion whose outcome is "covered by a test" asserts nothing about the product | decomposition |
| 9 | `## Tasks / Subtasks` with `(AC: n)` on every top-level task | `lint-story.py` `[tasks]` closure rule | schema |
| 10 | Every criterion covered by ≥1 task | the same closure rule, other direction | schema |
| 11 | `## Dev Notes` present | `lint-story.py` `[structure]` rule | schema |
| 12 | The requirement id named in Dev Notes as plain text | `coverage` scans the set for every input id | coverage |
| 13 | `### References` with `[Source: path#anchor]` that resolve | `lint-story.py` `[refs]` rule, against the sources `materialise()` writes to disk | schema |
| 14 | Trace every requirement in the input | `coverage`: missing ids are named | coverage |
| 15 | Cite no requirement id absent from the input | `grounding`: invented ids are named | grounding |
| 16 | Add no story for work the requirements do not ask for | `coverage` max-story ceiling, and `decomposition` on case-03 (no "set up Redis" story) | coverage, decomposition |
| 17 | Split by user-visible outcome, never by layer | `decomposition` on case-02 (no Celery/S3/email/migration story) | decomposition |
| 18 | One story per requirement as the default; split only on two noticeable outcomes | `coverage` min- and max-story bounds | coverage |
| 19 | Say what is missing after the last block, not as a story | `grounding`'s generic-statement check and the max-story ceiling | grounding, coverage |

**19 of 19 instructions are load-bearing (100%).** Every instruction has at least one assert
that fails if the model ignores it.

## What the map does not cover, stated rather than hidden

- **Three cases is the floor, not comfort.** They were chosen for distinct failure modes —
  clean one-to-one requirements (case-01), an architecture that invites layer-splitting plus a
  droppable FR-3 and a non-FR CAP-1 (case-02), and a change small enough to punish padding
  (case-03). They do not cover a change with genuinely multiple epics, so instruction 3's
  "if the change needs only one epic" branch is exercised and the multi-epic branch is not.
- **`decomposition` is a rubric on two of three cases.** "Independently valuable" is not a
  property a script can read off the text, so it is judged by a model. It is scoped to the two
  cases built to invite the failure rather than applied everywhere, because a rubric asked a
  question with no wrong answer available tends to say yes.
- **Instruction 8 is the weakest link.** The vacuous-criterion failure ("then the behaviour is
  covered by a test") is caught only by the rubric, and only where the rubric runs. A
  deterministic check for it is possible — flag criteria whose `then` clause names a test
  rather than an outcome — and is the first thing to add.
- **Nothing tests the dependency order between stories.** The readiness segment hands on
  stories with no declared sequencing, and the prompt does not ask for one, so neither does the
  suite. That is consistent, not complete: a planner that emits stories in an order that cannot
  be built front to back would pass every criterion here.
