# Load-bearing map: haiku (v10)

This file is documentation, not part of the prompt. The certified prompt is `skills/haiku/SKILL.md`, byte-identical to `prompts/prompt_v10.md`, and that's what the suite runs.

Every instruction maps to the criterion it serves and the evidence behind it. Criteria: **contract** (the reply has the right shape), **craft** (the poem follows English-language haiku conventions), **knowledge** (what the reply says about haiku is true). Evidence cites versions and runs in `results/`; "S" is Sonnet, "H" is Haiku, and every count is out of the repeats named.

Some instructions are **guards**: they're scored on every run but no run ever failed them, on either model, even under the one-line v1. I can't show they caused anything; I can show that a regression would be caught. The refactor (v8) wrote them down on purpose, because behavior a model does unprompted is the behavior that drifts when the model changes.

The frontmatter `description` isn't counted. It decides whether the skill triggers, and nothing here measures triggering.

| # | Instruction | Serves | Evidence |
|---|-------------|--------|----------|
| 1 | Role: a craft companion in modern English-language practice who answers questions accurately | all | motivates 3, 7 and 23; the v1–v7 skill only said "write, revise, critique", and in v3 one Sonnet run called Bashō's frog "outside the skill's scope" |
| 2 | Task: work out which of write / critique / quote / answer is wanted, and follow that section | contract, knowledge | v5 → v6: with only a writing rule, Sonnet answered "show me Bashō's frog" as if writing (k-13 0/3); once quoting was its own task, 3/3 |
| 3 | Write the poem in English | contract | v8 S s2: one w-04 reply opened with a Japanese haiku; no writing-case contract failure since, in 72 writing replies per model (v9, v10) |
| 4 | The reply's first line is the poem's first line; the poem is the whole reply (no preamble, title, fence, explanation, offer) | contract | v4 → v5: writing-case contract failures 5/12 → 0/12, S contract 31/36 → 36/36. H v1: 42 of 72 contract checks failed; 0 of 144 in v9–v10 |
| 5 | A note after the poem only when asked, or when the 5-7-5 rule requires it | contract, knowledge | w-05 and w-06 are the two cases that allow a note; w-06's requested explanation passed every run of every version |
| 6 | 5-7-5 is a misconception; Japanese counts *on*; ~12 syllables carry 17 *on* | knowledge | k-10 (H v1 missed *on*/morae once); motivates 7 and 10 |
| 7 | Aim for 10–14 syllables: short / long / short, first and last lines 2–4, middle 5–7; a five-syllable end line means you've slipped into 5-7-5 | craft | v2 → v3: S craft 7/21 → 18/21. v2 stated the fact (6) without this target and craft didn't move at all |
| 8 | The two short/long/short examples | craft | shipped together with 7 in v3, so not separately proven; counted with 7 |
| 9 | An explicit 5-7-5 request overrides the target: exactly 5/7/5, counted syllable by syllable (with the "win-ter fog" examples) | craft | v3–v6: w-05 strict 5-7-5 held only 1–2/3 per run after v3's short-line target; from v7 on, every Sonnet run hit it (6/6 in each of v7, v8, v9 and v10) |
| 10 | Then mention once that most English-language haiku don't use 5-7-5 | knowledge | v1 → v2: w-05 note missing 3/3 → 0/3 on S; H: missing in 6/6 at v1, 0/12 in v9–v10 |
| 11 | When critiquing, never grade against 5-7-5; comment on length only if it can't be read in one breath | knowledge | v1 → v2: c-07's myth-pushing and miscounted lines, 3/3 in v1 ("Syllable count is off. Traditional haiku aims for 5-7-5"), 0/3 in v2. H v1 praised the weak draft's 5-7-5 in all 6 runs ("has the correct 5-7-5 syllable structure, which is a great foundation") |
| 12 | Quoting: the Japanese original in romaji, then your own literal gloss | knowledge | v5 → v6: k-13 0/3 → 3/3 |
| 13 | Never reproduce a modern translator's published version or a copyrighted modern haiku | none | **not load-bearing.** The check requires the original; it can't tell whether a copyrighted translation came with it. Kept deliberately: it's the research note's legal guardrail, and v3 S once printed "the classic translation by Robert Hass" |
| 14 | "The reply is the poem" is for poems you write, not poems you quote | knowledge | the v5 regression behind 12: all three k-13 replies were only a remembered English translation |
| 15 | Critique: work through the checklist, say which items fail and why | knowledge | v3 → v4: c-08 "names the cut" missed 3 of 6 in v2–v3 → 0/3; c-07's keyword groups are this output |
| 16 | Offer exactly one revision, or none if the poem already works | contract | v3 → v4: c-07 offered two revisions in 2/3 (v1), 3/3 (v2) and 3/3 (v3) → 0/3; c-08 allows none |
| 17 | Checklist: two parts meeting at a cut | knowledge | c-08's cut group; see 15 |
| 18 | Checklist: words that tell the reader what to feel | knowledge | c-07 group 1. A guard: no run on either model missed it |
| 19 | Checklist: does the second part just restate the first | knowledge | c-07 group 3 ("restat…" is one of its phrasings) |
| 20 | Checklist: concrete and plain words | knowledge | c-07 group 2. The Sonnet residual: missed in 1/3 of runs of v6, v8 s2, v9 s1 and both v10 samples |
| 21 | Checklist: padding, words that only fill a line or repeat another | knowledge | c-07 group 3. Group-3 misses hit 3 of 12 Sonnet runs in v7–v8 and none in the 24 runs since, but v1–v6 had none either, so I don't credit this line with the fix |
| 22 | The revision follows every rule for writing | craft | c-07's revision craft: S 2/3 failed at v1, 0/36 from v3 on. H: 6/6 failed at v1, 3/12 still fail in v9–v10 (16 syllables, the Haiku residual) |
| 23 | Answer questions in the first sentence, then explain | contract | H v1: 4/24 answers didn't lead with the answer ("Traditional Structure"); 0/48 in v9–v10. S led with the answer unprompted in every run |
| 24 | Two parts, one cut (definition) | knowledge | w-06's cut explanation and c-08's cut group |
| 25 | Show the cause, not the feeling; no interpreting words | craft | H v1: telling words in 5 of 42 poems ("miss", "my heart" on the grandmother case); 0 of 84 in v9–v10. S never used them |
| 26 | One season word; naming the season works, implying it works better | craft | the kigo check on w-01, w-04 and w-06 |
| 27 | Match season words to the user's local climate | craft | w-04 (cherry blossoms forbidden in a Montreal March). A guard: no run on either model reached for blossoms |
| 28 | "moon" on its own is autumn | knowledge | k-09. A guard: 0 failures in every run of every version on both models |
| 29 | No title | contract | H v1: 7 of 36 writing replies opened with a title ("# First Snow Haiku"); 0 of 72 in v9–v10 |
| 30 | No rhyme | craft | the rhyme check. The Haiku residual: "light / night" in H v1 and v9 s2, "bright / night" in v10 s2, all on the strict 5-7-5 case |
| 31 | No overt simile | craft | the simile check. A guard: 0 flagged in any run of any version on either model |
| 32 | Haiku vs senryu: nature and season → haiku; foibles, irony, satire without a season word → senryu | knowledge | k-11 and k-12. A guard on both models (the one k-12 miss in v2 was a scorer bug, fixed and regraded) |
| 33 | The line is blurry; say which way the poem leans and why | knowledge | the verdict check on k-11 and k-12 measures "which way"; nothing measures "why" |

32 of 33 instructions are load-bearing (97.0%). Instruction 13 is the deliberate exception: it's the one rule I'd keep even if every score said it did nothing.

Six more instructions were in v9 and are gone from v10 because nothing measured them: four checklist items (only one season word, present tense, would a stranger see the scene, one breath), the frog and flowers kigo facts, and "plain words, present tense". v10 was run twice on each model to check the trim cost nothing: v9 332/336 and v10 331/336 across both models, a one-assert difference, with every v10 miss one that earlier versions already had.
