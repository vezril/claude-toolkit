# Load-bearing map: delivery-review (v2)

This file is documentation, not part of the prompt. The prompt under test is
`skills/delivery-flow/references/review.md`, copied verbatim to `prompts/prompt_v2.md`.

Criteria: **contract** (the reply parses raw as `review.json` and satisfies its schema),
**accuracy** (the verdict is right for this change and the findings name the defect that is
really there), **grounding** (nothing invented — every finding's evidence is locatable in the
material the reviewer was handed).

| # | Instruction | Serves | Proven by |
|---|-------------|--------|-----------|
| 1 | Role: you review the code; you are the last reader before this becomes a PR someone merges | accuracy | motivates 7–11; the whole suite |
| 2 | You are not the adversarial node; `challenge-implementation` judged the *record*, not the code | accuracy | case-02 and case-04, where the record claims success and the code or the suite says otherwise |
| 3 | Inputs are the diff, the story, and `verify.json`, and nothing else | grounding | every case: the harness supplies exactly these three and no tools |
| 4 | You are **not** given `implementation.json`, deliberately | grounding | the why behind 3; a reviewer handed the argument reviews the argument |
| 5 | If the diff cannot be judged without something you were not given, that is a finding | accuracy | case-07 — the fix's correctness depends on THRESHOLDS and TIERS, neither in the diff; ground truth forbids asserting it is correct |
| 6 | Reply is raw JSON: first character `{`, last `}`, no fence, no preamble | contract | `contract` anchors on both literals; the fence and preamble mutants |
| 7 | Every finding carries `evidence`: a path and line, or a quoted hunk, from the diff | grounding | the cites-a-file-not-in-the-diff and empty-evidence mutants |
| 8 | Mark a finding `blocking` when it should not merge, `advisory` otherwise | accuracy | case-02 and case-04 require blocking; case-01 and case-06 forbid it |
| 9 | Check 1: does it do what the change was supposed to do? | accuracy | case-02 — the inverted comparison implements the opposite of its AC |
| 10 | Check 3: what does it break — anything a revert would not undo? | accuracy | case-05, the dropped column; ground truth requires the one-way language |
| 11 | Check 4: the change should carry tests for P0/P1 and not below; tests beyond that are a finding | accuracy | case-03, three tests for a P3 criterion |
| 12 | Check 5: if the diff is too large to judge honestly, say so and say which part you could not assess | accuracy | case-08 — 40 generated files, 760 lines |
| 13 | Never claim a test result you were not given; `verify.json` is the only source | grounding | case-04 and the claims-the-suite-passed mutant |
| 14 | `SURVIVED` with a blocking finding is a contradiction the harness rejects | contract | the SURVIVED-with-blocking mutant |
| 15 | Judge the diff, not the author; no praise or style preference the roster's skills do not support | accuracy | the praises-the-author mutant; a banned-phrase check in `accuracy` |
| 16 | Do not propose the rewrite; name the defect and its evidence | accuracy | the proposes-a-rewrite mutant; a fenced-block/diff-marker check in `accuracy` |
| 17 | An empty `findings` list with `SURVIVED` is a real answer; do not manufacture a concern | accuracy | case-06, the empty case, with `findings_max` |
| 18 | `diff_sha256` is the sha of the diff you reviewed; a verdict is about one version | contract | the hex-digest format check |
| 19 | Report only your own `reviewers[]` entry; the step merges them | contract | the non-empty-reviewers check and the per-entry agent/verdict checks |

**19 of 19 instructions are load-bearing (100%).**

It read 17/19 (89.5%) first — below the 90% bar — with four instructions mapped to nothing.
Closing it took two different fixes, and neither was inventing a mapping:

- **5 and 12** had no case, so the cases were added: `case-07-unjudgeable` (correctness depends
  on `THRESHOLDS` and `TIERS`, neither in the diff) and `case-08-too-large` (40 generated
  files, 760 lines).
- **15 and 16** had no assert, so they got one. "Do not propose the rewrite" is measurable on
  the shape a rewrite takes — a fenced block or a diff marker inside a finding. "Judge the diff,
  not the author" is measurable on a banned-phrase list. Both are deterministic, which is why
  they belong in `accuracy` rather than in a rubric this suite deliberately avoids.

The method's rule is that an instruction mapping to nothing gets deleted rather than papered
over. Deleting these four would have been the lazy reading: all four describe behaviour worth
having, and the real options were a case or an assert.

## Why there is no iteration log yet

`iteration-log.md` is absent on purpose. Every number in one has to come from a promptfoo run
that actually executed, and the three runs this suite needs have not happened: the agent-SDK
provider reports `Not logged in`, so no model call is possible here. Writing the log now would
be fabricated evidence, which the method names as a failure to refuse.

What has been done before any model call, which is the method's own ordering:

- the suite exists, with three distinct criteria and six cases, each planting one trap
- `contract` is strict; `accuracy` and `grounding` parse leniently, so a formatting mistake
  costs one mark rather than three and the log stays attributable
- **the asserts are mutation-tested**: `node asserts/selftest.js` accepts a hand-written
  reference answer for all six cases and kills 14 mutants, each on the criterion that owns it
- one assert bug was found that way and fixed: `grounding` rejected `verify.json` as evidence,
  because it matched the files' contents and not their names. A reference answer caught it,
  which is the point of writing them first
- `prompts/prompt_v1.md` is the naive baseline — the one-liner someone would actually type —
  so the baseline is honest rather than pre-hardened
