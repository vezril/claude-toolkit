# Load-bearing map — `prompts/prompt_v4.md` (readiness-review)

Which instructions an assert actually depends on. Task 5.1's bar is **≥90% load-bearing**: an
instruction no assert exercises is either untested or unnecessary, and a certification that
cannot tell which is reporting on text nobody measured.

## The map

| # | Instruction | Assert that depends on it | Criterion |
|---|---|---|---|
| 1 | Emit one JSON object, nothing else | `verdict()` returns null and every criterion fails at its first line | all |
| 2 | `change`, `verdict`, `attacks`, `findings` present | `validate-artifact.py` against `readiness-verdict.schema.json` | contract |
| 3 | `verdict` is one of the three words | the schema's enum | contract |
| 4 | At least three attacks | explicit floor in `contract.js` — a review with fewer is an opinion | contract |
| 5 | Each attack's `result` is `landed` or `failed` | the schema's enum, plus a cross-check in `contract.js` | contract |
| 6 | Exactly `attack`, `method`, `result` on an attack | the schema's `additionalProperties: false` — **added in v3** | contract |
| 7 | Exactly `finding`, `evidence`, optional `story` on a finding | the same rule; **this is what v2 failed on** (`summary`, `file`) | contract |
| 8 | Omit `story` rather than sending `""` | the schema's `minLength: 1` — **what v1 failed on** | contract |
| 9 | `findings` always present, `[]` for SURVIVED | the schema's `required`; **what v3 failed on** | contract |
| 10 | `findings` empty when SURVIVED | explicit check in `contract.js` | contract |
| 11 | Every finding carries evidence | explicit non-empty check in `contract.js` | contract |
| 12 | REFUTED when a requirement has no story | `accuracy` on the dropped case: SURVIVED is a hard failure, and the findings must name FR-3 and say it has no story | accuracy |
| 13 | WEAKENED when a requirement is traced but not delivered | `accuracy` on the vacuous case, plus its rubric | accuracy |
| 14 | Vacuous criteria are a defect ("covered by a test" asserts nothing) | the vacuous-case rubric names this exact failure | accuracy |
| 15 | Do not declare a set "not a plan" when it is | `safety`: REFUTED on the set that stands is a hard failure | safety |
| 16 | Cite no requirement the change does not contain | `safety` checks every id in the findings against the change | safety |
| 17 | Report failed attacks as honestly as successful ones | `safety` requires at least one `failed` attack on the set that stands | safety |
| 18 | Expect SURVIVED to be rare; WEAKENED is the review working | `safety` permits WEAKENED with grounded findings — **the correction from iteration 1** | safety |

**18 of 18 instructions are load-bearing (100%).** Nine of them were added or sharpened in
response to a specific run failure, which is recorded against each in the table.

## What the map does not cover, stated rather than hidden

- **The "attacks worth making" list is advisory.** Five suggested attack types are in the
  prompt; no assert requires any particular one. Pinning them would test obedience rather than
  review quality, and the attack-count floor plus the accuracy criteria already force real
  work. A reviewer could pass with three attacks of its own devising, which is intended.
- **Only one case has a rubric.** `accuracy` on the vacuous case is the only semantic judgement
  in the suite; everything else is deterministic. That is deliberate after iteration 3 — three
  attempts to check a finding's *truth* with a word list each rejected a correct review — but
  it means the suite's judgement of finding quality rests on a single rubric.
- **`safety` no longer checks whether findings are true**, only that they do not cite material
  outside the change and do not reach REFUTED. A reviewer could pass `safety` with a grounded
  but trivial finding. Closing that needs a rubric on the sound case, which is the first thing
  to add.
- **The sound case is not sound**, and the suite now says so rather than pretending. Both models
  found real gaps in it on every run. It functions as "a set that is a plan for its change",
  which is what `safety` actually tests, not as a set beyond criticism.
