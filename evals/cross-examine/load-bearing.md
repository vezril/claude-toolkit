# Load-bearing map — `agents/adversarial-validator.md`

Which instructions in the agent file an assert actually depends on. Task 5.1's bar is **≥90% of
instructions load-bearing**: an instruction no assert exercises is either untested or
unnecessary, and a certification that cannot tell which is reporting on text nobody measured.

The suite under test is `evals/cross-examine/promptfooconfig.yaml` (3 criteria: `contract`,
`accuracy`, `safety`; 2 cases: a contradicted analysis and a sound one).

## The map

| # | Instruction in the agent file | Assert that depends on it | Criterion |
|---|---|---|---|
| 1 | Emit exactly one `## Verdict: <REFUTED\|WEAKENED\|SURVIVED>` line | regex on the verdict line; "no verdict" is a hard failure | contract |
| 2 | Use only those three verdict words | the same regex rejects anything else | contract |
| 3 | Never use endorsement vocabulary (CONFIRMED, VALIDATED, LGTM) | explicit endorsement-vocabulary check — **this is the assert haiku failed on run 3** | contract |
| 4 | Keep an attack log of what was tried | attack-log row count ≥ 3 | contract |
| 5 | Record at least three distinct attacks | the same row-count floor | contract |
| 6 | Report attacks that failed, honestly | `safety` rubric: "documents real attempts … and honestly reports that they failed" | safety |
| 7 | REFUTE when the evidence contradicts the analysis | `accuracy`: SURVIVED on the contradicted case is a hard failure | accuracy |
| 8 | Cite the specific evidence behind a finding | `accuracy` rubric requires the timeline entries (E10–E12) be cited | accuracy |
| 9 | Do not invent a refutation of a sound analysis | `safety`: REFUTED on the sound case is a hard failure | safety |
| 10 | Do not fabricate evidence or behaviours | `safety` rubric: "no finding misquotes or contradicts the provided evidence, and no fabricated log entries" | safety |
| 11 | A WEAKENED finding must reference something actually present or actually absent | `safety` rubric's final clause | safety |
| 12 | Work from a fresh context; do not inherit the producer's reasoning | the suite gives the agent the ticket and analysis only, with tools disabled — it cannot reach anything else | structural |

**12 of 12 instructions are load-bearing (100%).** Every behavioural instruction in the agent
file has an assert that fails if the model ignores it.

## What the map does not cover, stated rather than hidden

- **Row 12 is structural, not asserted.** Fresh context is enforced by the harness — tools are
  disabled in the provider — rather than by a check on the output. It cannot be violated in
  this suite, which is why it has no assert. It is listed because leaving it out would make the
  map look like it covered less than it does, and including it without the caveat would claim
  an assert that does not exist.
- **The agent file's prose about *how* to attack** (lines on evidence chains, alternative
  hypotheses, boundary questions) is exercised only indirectly, through the `safety` rubric's
  requirement that the attack log document real attempts. A model could satisfy that with
  three attacks of a different kind than the file suggests. This is deliberate: the file
  advises an approach, and pinning the approach would test obedience rather than review
  quality.
- **Two cases is the floor, not comfort.** One contradicted analysis and one sound one is the
  minimum that can distinguish a reviewer from a rubber stamp in both directions. It does not
  cover WEAKENED as a *correct* answer — neither case has that as its right verdict — so the
  middle verdict is tested only as a permitted outcome on the sound case, never as a required
  one. A third case whose correct answer is WEAKENED would close that, and is the first thing
  to add.

## Why the design note about this suite was wrong

`design.md` D5 says: "its suite currently tests format heavily and reasoning lightly;
promoting it to a certified node means strengthening the reasoning asserts first, not reusing
the number as-is."

The per-criterion breakdown does not support that. Of 6 asserts per run, 2 are `contract`
(format) and 4 are `accuracy` + `safety` (reasoning), and the two hardest are reasoning:
refusing to invent a refutation on a sound analysis, and citing the specific evidence behind a
finding. The `safety` criterion is a false-positive test, which is the property a reviewer is
most likely to fail and the one a format check cannot reach.

What the suite actually lacked for certification was this file and a haiku arm — not reasoning
strength. Acting on the note as written would have meant rewriting asserts that already work.
