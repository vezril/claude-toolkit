# Stage 0 — the spec, before any config exists

`research.md` (symlinked into this folder) is where the suite came from. It's a
research note on haiku craft: every claim carries a **confidence rating** (High /
Medium / Low) and numbered sources, and it ends with a short "agent instructions"
section for when the note is used as a skill.

**The order matters, and it's the point of this stage:** the spec came first, then
the cases, then the checks, then the prompt. Nobody wrote a prompt and went looking
for tests afterwards. That's what makes the eval an experiment instead of a
justification.

## How a spec claim becomes a test case

Every case in `../expected/` plants **one trap drawn from the note**. The traps are
the note's own contested beliefs and conventions — the places a model is most likely
to be confidently wrong.

| Claim in the research note | Case | Criterion that catches it |
|---|---|---|
| "5-7-5 English syllables is a misconception" (**contested belief #1**) | `k-10-575-myth` | knowledge — the answer must be in the first sentence |
| …and the model must not *write* that way either | `w-01-winter`, `w-02-coffee` | craft — 6–15 syllables, not 17 |
| …but an explicit request still wins | `w-05-575-lighthouse` | craft (exactly 5-7-5) + knowledge (say once that English practice differs) |
| "Show the cause, not the feeling" | `w-03-grandmother` | craft — no telling words ("sad", "I feel") |
| Season word anchors the poem, calibrated to the **user's local climate** | `w-04-montreal-march` | craft — a Montreal kigo (slush, sap buckets), not Kyoto blossoms |
| "Two parts, one cut" + kigo, when teaching | `w-06-first-snow-annotated` | knowledge — name the kigo and the cut |
| The note's own **bad draft**, quoted verbatim | `c-07-critique-weak` | knowledge (name the flaws) + contract (exactly one revision) |
| The note's own **good haiku** | `c-08-critique-strong` | knowledge — see the cut, invent no faults, don't push it to 5-7-5 |
| Moon = autumn in the classical calendar | `k-09-kigo-moon` | knowledge — first season named |
| "Nature points to haiku, human foibles to senryu" | `k-11`, `k-12` | knowledge — the verdict in the first sentence |
| "Never reproduce modern translations; use public-domain originals" | `k-13-basho-frog` | knowledge — romaji original, own gloss |

The "agent instructions" section supplies the **contract** rules directly: poem
first, annotation only if asked, one revision not five.

## Two things the spec deliberately did NOT give the prompt

Worth saying out loud, because it's the difference between a test and a leak:

1. **The note's Quebec kigo table** (sap buckets, slush) stayed out of the skill —
   it is the `w-04` answer.
2. **The note's own examples** stayed out of the written-in examples. "first frost"
   is the `c-08` test poem, and "sap bucket" is the Montreal answer, so v3's
   examples were written fresh (heat haze, cicadas).

If the answer key is in the prompt, the suite measures recall, not craft.

## Confidence ratings do real work

The note rates each claim, and the suite only hard-checks the ones rated **High**
or **Medium-High**. Claims rated lower stay in the skill as guidance but don't
become pass/fail asserts. That's why `load-bearing.md` can map instructions to
criteria honestly instead of inventing a check for every sentence.

## The line for the room

> The eval suite is the spec, made executable.

Anything in the spec you can't turn into a check is either a judgement call worth
saying out loud, or a claim you don't actually believe strongly enough to enforce.
