# Load-bearing map: delivery-challenge (v3a)

Documentation, not part of the prompt. The certified prompt is
`skills/delivery-flow/references/challenge-breakdown.md`, byte-identical to
`prompts/prompt_v3a.md`.

Criteria: **schema** (raw JSON conforming to `challenge-breakdown.json`, through the same
`validate-artifact.py` the edge hook runs), **verdict** (the verdict equals the ground
truth — the only field the harness routes on), **detection** (the findings name the planted
defect), **discipline** (the attack log is an honest record, and every id cited exists).

| # | Instruction | Serves | Proven by |
|---|-------------|--------|-----------|
| 1 | Role: the adversarial node of a delivery pipeline; the job is to break the breakdown | detection | frames the task |
| 2 | Role: not a reviewer offering balanced feedback — assume it is wrong and hunt for evidence | verdict, detection | v1 → v2: moved the hedge from WEAKENED (21/27) to REFUTED (17/27), so it demonstrably changes posture; the verdict rule is what then aims it |
| 3 | Task: attack the breakdown against the item it claims to plan | detection | the item is the authority every attack resolves against |
| 4 | Context: written straight to `challenge-breakdown.json` and parsed by `json.loads` with no cleanup step | schema | v1 → v2 (0/27 → 27/27), kept in the same paragraph as instruction 7 |
| 5 | Context: checked against a schema before anything downstream runs | schema | motivates 7–13 |
| 6 | Context: the harness routes on `verdict` without re-reading the reasoning | verdict | motivates the verdict rule; why a wrong verdict is not recoverable downstream |
| 7 | Raw JSON, first character `{`, last `}`, no preamble, no commentary, no fence — with the parse-error consequence beside it | schema | v1 → v2: 25/27 of Sonnet's v1 schema failures were preamble or fence, and 1 was stray whitespace; 27/27 after |
| 8 | A worked example of the opening, with no line above it | schema | v1 emitted fenced and prose-wrapped replies; 27/27 after, across 4 runs |
| 9 | Exactly this shape, exactly these keys and no others | schema | v1 emitted free-form shapes |
| 10 | `attacks[].method` records what you actually checked, not what you thought | discipline | the method-says-nothing and method-restates-the-attack checks; 0/27 → 27/27 |
| 11 | `attacks[].result` is the enum `"landed"` / `"failed"`, with the gloss "landed = it broke; failed = the artifact held" | schema, discipline | v1's non-fenced Sonnet rows narrated prose into `result`; it also produced verdict/landed consistency with no rule demanding it (hypothesis predicted 8–16/27, actual 27/27) |
| 12 | `findings[].evidence` — what demonstrates the hole | discipline | the evidence-too-thin check |
| 13 | `attacks` holds at least three entries; `findings` may be empty | discipline | the three-attack floor; "findings may be empty" is what makes a clean SURVIVED expressible |
| 14 | The verdict is not an impression; it follows from which defects are actually present | verdict | v2 → v3a (13/27 → 27/27) |
| 15 | REFUTED — the three A-class conditions, and "these are the only three", with the reason beside it (REFUTED throws the breakdown away and runs it again) | verdict, detection | v2 over-escalated 8 B-class rows to REFUTED; closing the list fixed all 8 |
| 16 | WEAKENED — the four B-class conditions, with the reason beside it (the plan stands and these are fixed in place) | verdict, detection | same 8 rows; also names the classes that drove detection 21/27 → 26/27 |
| 17 | SURVIVED — none of the seven defects is present, plus the positive half: a plan you would have written differently is not a broken one | verdict | 0 SURVIVED verdicts in 81 rows before this instruction; 6/6 clean rows correct after |
| 18 | A breakdown with both kinds of defect is REFUTED, and you report all of them | — | **not measured** — no fixture carries two defects |

17 of 18 instructions load-bearing (94%).

**The one that is not:** "A breakdown with both kinds of defect is REFUTED, and you report
all of them." Every fixture carries exactly one planted defect by construction, so no case
in this suite exercises an A-class and a B-class defect together. The instruction is kept
because the precedence it sets is the safe direction — an A-class defect must not be
downgraded to WEAKENED by a B-class one also being present, and WEAKENED advances the flow
where REFUTED reruns it — but it is **asserted, not measured**, and a fixture with two
planted defects would be the way to measure it.

## What was considered and dropped

Two staged prompts were not certified, and not because they failed:

- **`prompt_v3.md`** adds seven prescribed attacks (coverage, contradiction, invention,
  criteria-test-their-story, observable outcomes, duplication, domains) on top of v3a.
  Dropped: v3a reaches detection 26/27 and 27/27 by *naming the defect classes* in the
  verdict rule alone. The hunting procedure was predicted to be what found defects and the
  measurement said otherwise.
- **`prompt_v4.md`** adds an anti-fabrication rule. Dropped: fabricated-id rows are 0 at
  every prompt version once `derive-fixtures.py` stopped leaking defects through id
  numbering. The rule addresses a failure this suite has never observed.

Both remain in `prompts/` as the record. Certifying either would mean carrying rules with no
measured effect, against a prompt already at 99.1 / 100 / 100.
