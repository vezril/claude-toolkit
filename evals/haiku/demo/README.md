# The evolving config — a demo of how an eval suite is built

A spec (stage 0), five config stages and one offline calibration stage. Each stage adds **one idea** to
`promptfooconfig.yaml`, in the order you'd actually discover you needed it. Same
skill, same model, growing rig.

Run any stage from its own directory:

```bash
cd evals/haiku/demo/stage1-minimal
npx promptfoo eval
npx promptfoo view -y --filter-description '^demo stage'
```

| Stage | The one new idea | Cost |
|---|---|---|
| **0 · the spec** | where the cases come from — `stage0-the-spec.md`, `research.md` | none |
| **1 · minimal** | a prompt, a model, one case, one check | 1 call |
| **2 · skill as a variable** | the prompt under test is `vars.skill`, so any version can be swapped in | 1 call |
| **3 · cases** | one trap per case, plus `--repeat` — and the limits of string matching | 9 calls |
| **4 · real checks** | JavaScript asserts with `metric:` names and readable reasons | 6 calls |
| **4b · calibration** | the test suite for the test suite — offline, no model calls | none |
| **5 · certification** | two models, ground truth per case, the three real criteria | 24 calls |

## What to say at each stage

**Stage 0.** Before any config: the research note (`research.md`, symlinked from
the suite root) is the spec, and every case plants a trap drawn from it.
`stage0-the-spec.md` maps each claim to the case and criterion that enforces it,
and names the two things deliberately kept out of the prompt so the suite measures
craft rather than recall. **Spec → cases → checks → prompt, in that order.**

**Stage 1.** "This is a complete eval." A prompt, a model, one case, one check.
Everything after this is elaboration, not a different kind of thing.

**Stage 2.** The demo line:

```yaml
defaultTest:
  vars:
    skill: file://../../prompts/prompt_v1.md
```

Change `v1` to `v10`, run it again, and the number moves. The prompt has become a
**variable in the experiment** instead of the experiment itself. Also worth
showing: `prompt.txt` never says "reply with just the poem". A helpful line there
would do the skill's job, and the contract score would end up measuring the wrapper.

**Stage 3.** Cases with planted traps, and `--repeat 3` because one sample can't
tell a regression from noise. Then show why this stage doesn't hold: the telling-words
check needs every word listed by hand and still misses "sorrow" and "aches", and the
5-7-5 question can't be judged by keyword at all, because "no, that's a
misconception" and "yes, 5-7-5 is standard" both contain `5-7-5`.

**Stage 4.** Replace the keyword lists with code.
- `metric:` splits one blended score into **contract / craft / knowledge**, so you
  can see *which* thing broke.
- The assert returns a **reason**: `padded to 5-7-5 (5-7-5, 17 syllables)` instead
  of `0`. That's what makes a failing run diagnosable without rerunning it.
- `not-575.js` reuses the suite's **calibrated** syllable counter. It was wrong on
  6 of 45 hand-counted lines before it was fixed, and now scores 181/181 across four
  sets. Calibrate the ruler before you measure with it.

**Stage 4b.** `node calibrate.js` — 12 checks, no model calls, so this one works
with the Wi-Fi off. The asserts are code now, and code has bugs: a scorer bug
doesn't fail loudly, it silently changes every number in the log. Show the two
directions — a good reply passes everything, and a bad reply fails *exactly* what
it should and **passes the rest**. The coffee fixture is the one to point at: the
shape is fine, so it must fail craft and pass contract. Then show the real
`../../calibration/`: 181 hand-counted lines including a 20-line holdout, 77/77
scorer checks, and three files of real replies frozen as regression cases after
five scorer bugs — three of which made the skill look *worse* than it was.

**Stage 5.** The shape that gets certified:
- **Two providers**, same suite, so "the cheapest model that clears 95%" is a
  number rather than an argument.
- **Ground truth per case** in `expected/<case>.json`, found via `vars.case`.
  The winter case lists 24 acceptable season words — frost, sleet, verglas,
  woodstove — so the check knows what *this* case should contain.
- **Each case carries only the criteria its spec defines**, so nothing gets a
  free pass on a criterion it should have had.
- The three asserts **own separate failures**: contract takes every formatting
  penalty, craft reads the poem leniently so a preamble isn't punished twice,
  knowledge checks the claims. One mistake costs one point.

Then switch `skill:` from `prompt_v10.md` to `prompt_v1.md` and rerun for the
before-and-after on the real criteria.

## Notes

- Stages 1–4 use the **haiku** model only, to keep stage runs short. Stage 5 uses
  both, like the real suite.
- Stage 5 is 4 of the real suite's 13 cases, so it runs in about a minute. The
  numbers in `../iteration-log.md` come from the full suite (`../promptfooconfig.yaml`),
  not from this trimmed copy — don't quote stage-5 output as the certified score.
- Nothing here writes to `../results/`. These runs land in promptfoo's local
  database, where `--filter-description '^demo stage'` keeps them separate.
- Every stage except 0 and 4b calls a real model. Budget roughly 40 calls to run
  them all once; stages 0 and 4b are free and work offline.
