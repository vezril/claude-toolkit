# Iteration log: haiku

The task: a skill that writes, critiques and explains haiku the way modern English-language practice does, built eval-first. The spec is my research note on haiku craft (copied here as `research.md`), which rates every claim for confidence and ends with instructions for an agent. The prompt under test is the skill itself, from a one-line v1 to the certified v10.

Every number below comes from an executed promptfoo run. Each run repeats all 13 cases 3 times; the cases carry 28 asserts, so a run is 84. The bar is 95%. Evidence is in `results/run_<version>_<model>[.s2].json`. Runs use the Claude Agent SDK provider with no working directory, so the model sits in an empty temp dir with no tools. Sonnet is `claude-sonnet-5`, Haiku is `claude-haiku-4-5-20251001`. The wrapper (`prompt.txt`) only says "execute this skill"; it never says "reply with just the poem", because a harness line like that would do the skill's job and the contract criterion would end up measuring the wrapper. The whole thing took 819 model calls, about $22 at API rates (the runs were on a subscription). Grading is all deterministic JavaScript, so it cost nothing.

**One convention to know before the numbers:** I fixed the scorer five times along the way, each time because reading the outputs showed it was wrong. After every fix I regraded every earlier run with `rescore.js --write`, which re-scores the recorded outputs without new model calls. So every number in this log and in the table at the end comes from the *final* scorer, and the progression is comparable end to end. Where a regrade changed a number, I say what it was before.

## Setup (before any prompt change)

Thirteen cases. Each plants one trap from the research note:

- w-01 winter, w-02 morning coffee: plain requests, where the trap is padding to 5-7-5, naming the feeling, rhyme, a simile
- w-03 missing my late grandmother: the pull to name grief. A short kind line after the poem is allowed here, a preamble isn't
- w-04 "I live in Montreal. Write a haiku for late March": the Kyoto calendar says blossoms; Montreal says slush
- w-05 "a strict 5-7-5 haiku about a lighthouse": comply exactly, and say once that English practice rarely counts that way
- w-06 first snow, with the season word and the cut explained: the one writing case that asks for annotation
- c-07 critique the research note's own bad draft ("The autumn leaves fall / I feel so sad and lonely / Nature is so sad"): name the flaws, offer one revision
- c-08 critique the note's good haiku ("first frost / the dog's breath lingers / at the gate"): see the cut, don't invent problems, don't push it toward 5-7-5
- k-09 what season "moon" signals (autumn), k-10 whether a haiku has to be 5-7-5 (no, and why), k-11 and k-12 haiku or senryu, k-13 show me Bashō's frog (the public-domain original, not a modern translation)

Three criteria, each a deterministic JS assert, and a test only carries the criteria that apply to it, so no case gets a free pass on a criterion it doesn't have:

1. **contract** (strict): the shape of the reply, as given. Poem-only replies, poem-first where a note is allowed (with a word cap), exactly one revision in a critique, the answer in the first sentence of a question. It owns every formatting penalty.
2. **craft** (lenient; the poem is found wherever it sits, so a preamble costs contract and not craft too): 6–15 syllables in total (the note says "roughly 10 to 14"; I allowed 15 for "roughly", which still fails 5-7-5's 17), exact 5-7-5 when asked, no end rhyme, no overt simile, no words that interpret ("sad", "beautiful", "I feel"), a season word where one's expected, and no wrong-climate season word.
3. **knowledge**: what the reply says about haiku is true. Keyword groups (for the flaws a critique must name, the kigo and cut an annotation must name, *on* and morae), the verdict in the first sentence for haiku vs senryu, the first season named for "moon", romaji for Bashō.

The syllable counter is the piece everything leans on, so I calibrated it before trusting it. The first version missed six of 45 hand-counted lines ("rises" came out as 1 syllable, "whole" as 2, "lonely" as 3). After fixing the rules behind those, I wrote a 20-line holdout I never tuned on, and it scored 20/20. Then I wrote a good and a bad reply by hand for every case. The bad ones list exactly which criteria they should fail, and they must pass the rest; that's the check that the criteria are distinct and one mistake doesn't cost two numbers. That run turned up five more miscounts ("peaceful", "beautiful", "aches", "Montreal", "carrier's"). None flipped a verdict, but they would have on a strict 5-7-5 case, so I fixed them too. `calibration/syllables.js` ends at 181/181 lines exact across four sets, and `calibration/scorers.js` ends at 77/77, including real model replies I labeled by hand.

## v1 run 1: discarded

**Baseline:** Sonnet 63/84 on the suite as it stood.
**Hypothesis:** none; this was meant to be the baseline.
**Change:** none. v1 is one line: "Help the user write, revise, and critique haiku."
**Result:** the number was plausible, but reading the critiques showed my knowledge check was too lenient. All three c-07 critiques treated 5-7-5 as the standard ("Syllable count is off. Traditional haiku aims for 5-7-5"), and two got the draft's counts wrong ("The autumn leaves fall = 6 syllables (should be 5)"; it's 5). On the good poem, one said "the dog's breath lingers is 6 syllables… 2-6-4" (it's 5, and 2-5-3). My check only asked whether the critique named the right flaws, so it passed all of this. c-08 did forbid pushing 5-7-5, but its regex only knew "should/must/try to … 5-7-5" and missed "against a 5-7-5 template".
**Reasoning:** pushing the 5-7-5 myth is the research note's number-one contested belief, so a critique that does it has said something false. I kept the run as `results/run_v1_sonnet.DISCARDED-narrow-critique-check.json` and added two knowledge checks to both critique cases. One flags any sentence that presents 5-7-5 as the standard with no negation or hedge in the same sentence. The other flags any syllable count the reply states for a line of the draft that isn't that line's true count. I froze the six real critiques as calibration cases, labeled them by hand before running the new checks on them, and the checks agreed with every label. (The same run also turned up "sidewalk" counted as 3 syllables. Silent-e compounds are now handled; no verdict changed.)

## v1 baseline (Red): Sonnet 59/84 (70.2%)

**Baseline:** the one-line skill on the corrected suite.
**Hypothesis:** none.
**Result:** 59/84, and the discarded run regraded on the same suite is also 59/84, so two samples agree exactly. (As first run this showed 60/84: one critique said "line 2 has 6… line 3 has 6", and my count detector only knew the "N syllables" phrasing. I added "line N has N", calibrated it on that reply, and regraded.) Craft was the floor at 7/21. Sonnet pads nearly every poem to 5-7-5, and in one of them miscounted its own line ("Silent snowfall settles" is 6). Contract lost 5 to preambles, a trailing "Want a different tone?" offer and two-revision critiques, and knowledge lost 6: the critique myth-pushing above, plus w-05 never mentioning that English haiku rarely use 5-7-5. What was already right is worth noting: no telling words, no similes, no rhyme, and no cherry blossoms in Montreal. Sonnet already knew moon = autumn and got haiku vs senryu right every time.

## v2: the 5-7-5 policy

**Baseline:** 59/84.
**Hypothesis:** say what the research note says: 5-7-5 is a misconception, Japanese counts *on*, English haiku run about 10–14 syllables, comply with an explicit 5-7-5 request with one note, and never grade a critique against 5-7-5. Craft 7/21 → ≥19/21, the c-07 myth-pushing disappears, and the w-05 note appears.
**Change:** a "Length: not 5-7-5" section.
**Result:** 65/84 (77.4%). Two out of three predictions landed: c-07's knowledge failures went from 3/3 to 0, and the w-05 note appeared 3/3. The main one didn't: **craft didn't move at all**, 7/21 again. Sonnet kept writing exact 5-7-5 ("Bare branch, snow-heavy— / a single crow shifts its weight, / then the silence breaks"). Where it did change, it wrote longer instead (6-6-4 = 16).
**Reasoning:** telling the model the fact changed what it *says* about haiku but not how it *writes* one. It needs a concrete shape to aim at, not a statement of the rule. (This run also exposed a scorer bug: "This is a haiku, with no human-centric wit or twist, which is the hallmark of senryu" was failed for mentioning senryu in its first sentence. The verdict is now the first label the sentence names, ignoring "not a / unlike / rather than". Before the fix, v2 showed 64/84.)

## v3: a concrete length target

**Baseline:** 65/84.
**Hypothesis:** make the target something the model can hit: first and last lines usually 2–4 syllables, the middle 5–7, "a five-syllable first or last line is the sign you've slipped back into 5-7-5", plus two short/long/short examples. Craft 7/21 → ≥18/21; nothing else moves.
**Change:** rewrote the Length section. I wrote the two examples fresh (heat haze, cicadas). The research note's own examples would have leaked answers: "first frost" is the c-08 test poem, and "sap bucket" is exactly the Montreal-March answer.
**Result:** 75/84 (89.3%). Craft 7 → 18/21, as predicted. Two things moved that I said wouldn't. The explicit 5-7-5 case (w-05) broke, falling from 3/3 to 1/3 ("silent tower" is 4), and one k-13 reply quoted "the classic translation by Robert Hass" with no Japanese original.
**Reasoning:** w-05 is my own doing: the short-first-line rule is bleeding into the case that asks for five. The Hass reply is the copyright problem the research note warns about, but it happened in 1 of 3 runs and v3 didn't touch quoting, so I left it and watched it.

## v4: the critique protocol

**Baseline:** 75/84.
**Hypothesis:** c-07 had offered two revisions in 2/3 of runs in v1 and 3/3 in v2 and v3. Give critiques the research note's checklist plus "offer exactly one revision, or none if the poem already works". c-07 contract 0/3 → 3/3, and c-08's occasional failure to name the cut goes away, since the checklist's first item is two parts at a cut.
**Change:** a Critiquing section: the checklist, say which items fail and why, one revision.
**Result:** 76/84 (90.5%). Both predictions landed: c-07 offered one revision 3/3, and c-08 named the cut 3/3. What I didn't predict: the *writing* replies got chatty. Five of the 12 writing-case replies failed contract, against 1 in v3, with scene-setting openers ("Late March in Montreal — snowmelt, dirty ice…") and explanations of the poem nobody asked for. Two replies also copied the ``` fences from v3's examples. (As first run this was 75/84; one critique named the redundancy as "restates" and "saying the same season three times", phrasings my third c-07 keyword group didn't list. That was found in v5; see below.)
**Reasoning:** writing-case contract had been noisy all along (v1 3/12, v2 0/12, v3 1/12), and the checklist seems to have tipped Sonnet into teaching mode. The real gap is that the skill has never said what a written reply looks like.

## v5: the reply is the poem

**Baseline:** 76/84.
**Hypothesis:** an output contract for writing, using an anchored literal instead of a vague prohibition: "your reply's first line is the poem's first line", with no preamble, title, fence, explanation or offer, and a note only when asked or when the 5-7-5 rule requires one. Contract 31/36 → ≥35/36; nothing else moves.
**Change:** a Writing section, placed first.
**Result:** 80/84 (95.2%). Contract hit 36/36 as predicted. What I didn't predict: k-13 went from 2/3 to **0/3**. All three replies were just a remembered English translation ("old pond / a frog jumps in / the sound of water") with no Japanese and no framing. Sonnet had applied "the reply is the poem" to *quoting* a poem as well as writing one. (As first run this was 79/84. The fifth c-07 critique listed "saying the same season three times" and "line 3 just restates line 2", and my redundancy group didn't have those phrasings. I added them, froze the reply as a labeled pass, and regraded everything.)
**Reasoning:** technically over the bar, but a failure on 3 of 3 repeats is a defect, not noise.

## v6: quoting existing haiku

**Baseline:** 80/84.
**Hypothesis:** say how to quote: the Japanese original in romaji (public domain), then your own literal gloss, never a modern translator's version, and "the reply is the poem" is for poems you write, not ones you quote. k-13 0/3 → 3/3; nothing else moves.
**Change:** a Quoting section.
**Result:** 81/84 (96.4%). k-13 3/3, as predicted. w-05 still broken: "winter fog / the lighthouse holds its beam / steady on the rocks" is 3-6-5, sent with "written in strict 5-7-5". One c-07 critique skipped the checklist's "concrete and plain" item and never called "Nature" an abstraction.
**Reasoning:** the w-05 trend is the clearest thing in the data: 3/3 in v1 and v2, then 1/3, 1/3, 2/3, 1/3 from v3 on. It's the v3 regression, compounded by Sonnet not counting its own lines.

## v7: the explicit 5-7-5 request wins

**Baseline:** 81/84.
**Hypothesis:** say that an explicit 5-7-5 request overrides the length target, and have the model count syllable by syllable, using its own failures as examples ("win-ter fog" is 3, not 5; "the light-house holds its beam" is 6, not 7). w-05 craft → 3/3; nothing else moves.
**Change:** rewrote that one bullet.
**Result:** 83/84 (98.8%). w-05 3/3, as predicted. The one miss was a c-07 critique that framed the repeated "so sad" only as telling, never as padding.
**Reasoning:** I checked whether that miss was the scorer again, and decided it wasn't: the critique really doesn't flag the padding. Widening the scorer after every near-miss would only fit it to Sonnet. The cause was in my skill: when I wrote v4's checklist I'd dropped the research note's padding item, because v2 had banned grading against 5-7-5.

## v8: refactor to Role / Task / Context / Constraints (Red)

**Baseline:** 83/84.
**Hypothesis:** restructuring costs nothing. The refactor also writes down everything Sonnet did right without being told: no telling words, no simile or rhyme, local-climate season words, moon = autumn, haiku vs senryu, answer questions first. That's the behavior most likely to drift on a different model. It also puts the padding item back in the checklist, so like PR #77's v5 it isn't a pure refactor, and I don't claim it as one. I kept the tuned sections word for word, and kept test answers out: the research note's Quebec kigo table (sap buckets, slush) stays out of the skill, because it's the w-04 answer.
**Change:** restructured into Role, Task, Context, Constraints; widened the description to cover questions and senryu.
**Result:** 81/84 (96.4%), two worse than v7. With one sample each I couldn't tell a two-assert difference from noise, so I took a second sample of *both* versions rather than re-rolling v8 until it looked good: v7 83 and 83, v8 81 and 81. The refactor cost something real. The new failures were all on writing cases: a 5-8-4 poem, a 16-syllable one, a w-05 note that explained itself for 41 words, and a w-04 reply that **opened with a line of Japanese**, then translated it.
**Reasoning:** v8 put about twenty lines of background (kigo, kireji, "Japanese classical seasons") ahead of the tuned writing rules. The rules got diluted, and the Japanese-flavored context primed Japanese output. From here on every version gets two samples.

## v9: constraints first

**Baseline:** 83/84 (v7), 81/84 (v8).
**Hypothesis:** same content as v8, but with Constraints ahead of Context so the tuned rules lead again, plus "write it in English" in the writing contract. That's two changes, bundled because they fix one regression; I predict them separately. Back to v7's level (≥83/84 per sample) with no writing-case failures and no Japanese.
**Change:** moved the Context section below Constraints; added "write it in English".
**Result:** 83/84 and 84/84, 167/168 (99.4%) across both samples, including the first perfect run. No Japanese, and no writing-case contract failure in 36 writing replies. (As first run, sample 1 was 82/84. A w-04 poem opened "last patch of snow", which is saijiki's *zansetsu* ("remaining snow"), a real spring season word. My Montreal list had "last snow" but not "patch of snow". I fixed the list, froze the reply as a labeled pass, and regraded everything.)
**Reasoning:** the refactor is repaired. The order of the sections turned out to be load-bearing, which the Role/Task/Context/Constraints acronym doesn't tell you.

## Haiku

**Baseline:** the naive v1 on Haiku, two samples: 32/84 and 37/84, 69/168 (41.1%). Haiku titles its poems ("# First Snow Haiku"), opens with "Here's a haiku about winter:" and closes with "This haiku captures…". It pads to 5-7-5, and it told the weak c-07 draft, in all 6 runs, that it "has the correct 5-7-5 syllable structure, which is a great foundation". It marked the good "first frost" poem down for being "2-5-3 rather than the traditional 5-7-5". It also missed the w-05 note in 6/6 and didn't lead with the answer on 4 of 24 questions.
**Hypothesis:** v9 carries over to Haiku unchanged.
**Change:** none.
**Result:** 82/84 and 83/84, 165/168 (98.2%), on the first try. The three misses are real: two c-07 revisions that run to 16 syllables (one of them reuses the draft's "autumn leaves fall"), and one strict 5-7-5 that rhymes "night / light".
**Reasoning:** most of the gap between the two models was in exactly the things the refactor wrote down for Sonnet's sake: the reply is the poem, no title, answer first, no telling words. Sonnet did those unprompted; Haiku didn't, until the skill said so. The skill lifts Haiku by 57 points and Sonnet by 29.

## v10: cut what nothing measures

**Baseline:** v9: Sonnet 167/168, Haiku 165/168.
**Hypothesis:** mapping v9 line by line against the suite, 33 of 40 instructions served a criterion (82.5%), below the 90% I hold these to. Cut the six unmeasured ones that aren't a safety rule: four checklist items (only one season word, present tense, would a stranger see the scene, one breath), the frog and flowers kigo facts, and "plain words, present tense". Keep the copyright rule anyway (see `load-bearing.md`). Nothing measurable changes on either model.
**Change:** those six deletions.
**Result:** Sonnet 82/84 and 83/84 (165/168, 98.2%); Haiku 84/84 and 82/84 (166/168, 98.8%). Across both models v10 is 331/336 against v9's 332/336, and every v10 miss is one earlier versions already had (c-07 not calling "Nature" abstract, one 5-7-5 creeping back on the grandmother case, a Haiku revision at 16 syllables, a Haiku "bright / night" rhyme).
**Reasoning:** the trim cost nothing I can measure, and v10 is 32 of 33 load-bearing (97.0%).

## Score progression

Every row is the recorded outputs graded by the final scorer. "s2" is the second sample of a version.

| Version | Model | Sample | contract | craft | knowledge | Total | % |
|---|---|---|---|---|---|---|---|
| v1 | sonnet | discarded | 33/36 | 6/21 | 20/27 | 59/84 | 70.2% |
| v1 | sonnet | s1 | 31/36 | 7/21 | 21/27 | 59/84 | 70.2% |
| v2 | sonnet | s1 | 33/36 | 7/21 | 25/27 | 65/84 | 77.4% |
| v3 | sonnet | s1 | 32/36 | 18/21 | 25/27 | 75/84 | 89.3% |
| v4 | sonnet | s1 | 31/36 | 19/21 | 26/27 | 76/84 | 90.5% |
| v5 | sonnet | s1 | 36/36 | 20/21 | 24/27 | 80/84 | 95.2% |
| v6 | sonnet | s1 | 36/36 | 19/21 | 26/27 | 81/84 | 96.4% |
| v7 | sonnet | s1 | 36/36 | 21/21 | 26/27 | 83/84 | 98.8% |
| v7 | sonnet | s2 | 36/36 | 21/21 | 26/27 | 83/84 | 98.8% |
| v8 | sonnet | s1 | 35/36 | 20/21 | 26/27 | 81/84 | 96.4% |
| v8 | sonnet | s2 | 35/36 | 20/21 | 26/27 | 81/84 | 96.4% |
| v9 | sonnet | s1 | 36/36 | 21/21 | 26/27 | 83/84 | 98.8% |
| v9 | sonnet | s2 | 36/36 | 21/21 | 27/27 | 84/84 | 100.0% |
| v10 | sonnet | s1 | 36/36 | 20/21 | 26/27 | 82/84 | 97.6% |
| v10 | sonnet | s2 | 36/36 | 21/21 | 26/27 | 83/84 | 98.8% |
| v1 | haiku | s1 | 14/36 | 2/21 | 16/27 | 32/84 | 38.1% |
| v1 | haiku | s2 | 16/36 | 3/21 | 18/27 | 37/84 | 44.0% |
| v9 | haiku | s1 | 36/36 | 19/21 | 27/27 | 82/84 | 97.6% |
| v9 | haiku | s2 | 36/36 | 20/21 | 27/27 | 83/84 | 98.8% |
| v10 | haiku | s1 | 36/36 | 21/21 | 27/27 | 84/84 | 100.0% |
| v10 | haiku | s2 | 36/36 | 19/21 | 27/27 | 82/84 | 97.6% |

Certified: **v10 on Haiku**, 166/168 (98.8%) across two samples, the cheapest model that clears 95%. Sonnet clears it too, at 165/168 (98.2%). `skills/haiku/SKILL.md` is byte-identical to `prompts/prompt_v10.md`.

## Known residuals

- **c-07 on Sonnet:** about 1 critique in 3 skips the "concrete and plain" item and never calls "Nature" an abstraction.
- **c-07 on Haiku:** some revisions run to 16 syllables (3 of 12 in v9–v10).
- **Strict 5-7-5 on Haiku rhymes sometimes** ("night / light", "bright / night"): 1 in 6 runs of w-05 in both v9 and v10. The no-rhyme rule lives in Context and the 5-7-5 override says "overrides everything above". A one-line "5-7-5 still doesn't rhyme" is the obvious next hypothesis, but at 1 in 6 it would take more samples than it's worth to show.

## Honest limits

- The suite checks conventions, not quality. A poem can pass every check and still be flat. None of this measures whether the poems are *good*; it measures that the skill follows the practice the research describes.
- The checks are heuristics I calibrated, not ground truth. The syllable counter is 181/181 on the lines I've tested; a new word can still fool it. The keyword groups and the 5-7-5 detectors each missed a phrasing at least once (all found by reading outputs, all fixed and regraded, all frozen into calibration), so assume a few more are out there.
- A critique can say something false without numbers in it. One v1 critique told the user the good poem was "already there" for strict 5-7-5 (it's 2-5-3). No check can see that.
- Some instructions are guards: simile, the Montreal blossoms, moon = autumn and the w-06 annotation never failed on either model, even under v1. They're written down for the next model, not because this data shows they did anything.
- Triggering isn't tested: nothing here checks that the skill loads when it should.
- Loading the skill into a wrapper prompt stands in for how Claude Code actually injects skills. It tests the skill's content as instructions, which is the thing I wanted to guard, but it isn't end to end.

## What I'd carry to the next skill

- Telling a model a fact changes what it says, not how it acts. v2 made Sonnet explain the 5-7-5 myth correctly and still write 5-7-5; v3's concrete target and examples fixed the writing.
- Every new rule has a blast radius. The short-line rule broke explicit 5-7-5, the checklist made writing replies chatty, and the reply-is-the-poem rule broke quoting. Each fix needed its scope stated ("the explicit request wins", "for poems you write, not poems you quote").
- The order of a prompt's sections is load-bearing. The same words cost two points when the background came first.
- Take two samples before calling a two-assert difference. One sample of v8 against one of v7 couldn't separate a regression from noise; two of each could.
- Write down what the strong model does unprompted. Sonnet never needed "no title" or "answer first"; Haiku did, and those rules are most of why the skill ports.
- Read the outputs of every run, including the green ones. All five scorer bugs were found that way, and three of them made the skill look *worse* than it was.
