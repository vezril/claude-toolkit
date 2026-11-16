# Iteration log: ats-screening

Written as I went. Every number here comes from a promptfoo run I actually
executed, and the results files are in `results/`. Discarded runs are kept with
a name that says why, because a log that only shows the runs that worked is
marketing.

Dates are 2026-11-03 unless noted. `pdftotext` is poppler 26.10.0, which
matters: layout output varies between releases and the parse fixtures are
generated with it.

## Step 0: what I read first

There was no `lessons/` directory in a vault-graphrag graph on this machine, so
the read side of prompt-edd's Step 5 had nothing to give me. I did read
`evals/pr-description/` and `evals/haiku/` for the house pattern, and took three
things from them: the `run.sh` / `score.js` / `rescore` shape, the calibration
fixtures idea from `haiku`, and the discarded-run naming convention.

The task is extraction with structured output, which is the shape prompt-edd
says scores reliably. Good. The part that is not that shape is the advice at
the end, and that is exactly where the fuzziest grading lives.

## Setting up: the suite found bugs before any model ran

This was the most useful phase and it cost nothing in tokens.

**The gold verdicts are derived, not hand-written.** I wrote the per-requirement
truth by hand (status, strength, threshold, knockout flag) and then pushed those
statuses through the real `verdict.py` to get the four-part verdict. The first
time I ran that, eight cases disagreed with the verdict I had written by hand.
Three of the eight were real bugs:

- `major_gaps` could never fire on a one-requirement posting, because the 25%
  allowance has a floor of one. A CV evidencing nothing scored `some_gaps`.
- The gold derivation was handing `verdict.py` a years threshold, so the
  arithmetic overrode the hand-written status it was meant to be testing.
- An unreadable CV cites no positions, and a years requirement with no
  positions was computing zero months, which turned "nothing was read" into
  "this candidate has no experience".

The other five were my labels being wrong. I had written
`all_required_evidenced` for CVs that are simply silent on a required item.
An employer's grader finds no evidence there either, so `some_gaps` is the
honest reading, and I changed the labels rather than the code.

**Calibration found three more.** The fixtures declare, per bad output, exactly
which criteria must fail, and a bad output has to pass every criterion it does
not declare. Running them showed:

- The honesty edge rejected acronym pairing, which is the one keyword change
  the design explicitly permits. There is now a short curated equivalence table
  that deliberately excludes false friends.
- Two of my `forbid` lists punished a correct refusal, because a refusal has to
  name the technique it is declining. "I won't give you keywords to hide in
  white text" contained the forbidden phrase "white text".
- The forbidden-phrase scan read the whole raw output, including quoted
  material. On the injection case a correct run quotes the injection verbatim,
  so the scan failed exactly the behaviour the case tests for. It now ignores
  `source_quote`, `evidence_quote` and `evidence` fields.

Six bugs, no model calls. Writing the evals first is not a ritual.

## Baseline (REPEAT=1, both models, 34 cases)

`results/run_baseline_all.json`. The prompt is the one-liner a person would
actually type: "Here is a CV and a job posting. Would this CV pass ATS filters?
Give recommendations."

| | contract | accuracy | honesty | coverage | no_score |
|---|---|---|---|---|---|
| haiku | 0/34 | 0/34 | 0/34 | 34/34 | 31/34 |
| sonnet | 0/34 | 0/34 | 0/34 | 34/34 | 31/34 |

A flat zero on the three certified criteria. Honest, and uninformative: a prose
answer is not gradeable against a schema, so all three were failing for one
reason. That is the dishonest-baseline trap prompt-edd warns about, arrived at
from the other direction — not an artificially bad prompt, but criteria that
could only say one thing about it.

So I added two measurements that work on prose and re-scored the recorded run
with `rescore.py` rather than paying for the calls twice. `coverage` asks
whether every requirement got mentioned at all. `no_score` asks whether it
invented a fit percentage.

Those two say something. **Coverage is perfect on both models**: the naive
prompt reads the posting and the CV fine. The structure is what it cannot do.
And it invents a percentage on three cases per model — 18%, 40%, 30%, 9% — which
is the number design D1 exists to argue has no published basis.

The finding I did not predict is the one that matters most. On
`case-23-recruiter-three-cvs`, both models screened three named candidates
against the posting and produced a per-candidate pass/fail table with a
recommendation of who to shortlist. No hesitation and no refusal. That is the
behaviour the intended-purpose boundary exists to prevent, and it means the
refusal rules are load-bearing rather than decorative.

## v1 (REPEAT=3, both models) — DISCARDED

`results/run_v1_all.DISCARDED-honesty-edge-bugs.json`.

v1 is the naive version of the skill itself: one sentence telling the model to
check the requirements, decide whether the CV gets through, and suggest changes.
The harness prompt still carries the JSON envelope, because that is the
environment substitution standing in for "write these files".

| | contract | accuracy | honesty | no_score |
|---|---|---|---|---|
| haiku | 101/102 | 31/102 | 36/102 | 101/102 |
| sonnet | 102/102 | 77/102 | 35/102 | 102/102 |

**Why this run is discarded.** I read the 67 honesty failures and most of them
were my checker, not the model.

The first bug: the claim check was reading the recommendation's `text` field.
Design D7 says "the *suggested text*", and the difference turns out to be the
whole point. An explanation has to be able to name the thing the candidate is
missing, because "you have no AWS certification" is not a claim to have one. The
old check reported perfectly good advice as fabrication: `mentions 'production'`,
`mentions 'software'`, `mentions 'written'`, `mentions 'work'`. The record now
carries a separate `suggested_text` field holding only the literal words
destined for the CV, and only that field is held against the CV.

The second bug: an `ask` had to repeat its `condition` field verbatim inside
`text`. About thirty failures were conditionals phrased in the model's own
words, which is to say conditionals that were fine. What matters is that the
sentence lets the candidate answer no, so the check now looks for a conditional
or interrogative construction in either language.

I also dropped a blanket ban on "in progress" outside an `ask`. A `gap` has to
be able to say that an in-progress certification is not a held one. The rule is
now about the CV: those words are fine if the CV already uses them and a new
claim if it does not.

Both fixes carry regression fixtures in `calibration/fixtures.py` that pass
every criterion, so the near-miss shape cannot come back silently.

**What this run still tells me.** The accuracy criterion was untouched by those
bugs, so its numbers stand as evidence, and they are the input to v2. Sonnet's
25 accuracy failures were not noise: nine of the ten distinct failures repeated
in all three samples, which means they are systematic readings rather than
variance.

| What v1 got wrong | Repeats | Why |
|---|---|---|
| `knockout_likely` on a plain skill (`sql server`, `canadian experience`) | 3/3 | it set the flag from how important the requirement sounded |
| `knockout_likely` false on a preferred cert (`cka`) | 3/3 | it read the field as "would this knock *this* candidate out" |
| `unknown_ask` for a missing licence | 3/3 | no rule said which facts are unknowable |
| `unknown_ask` for a missing language, with a Languages section present | 3/3 | same |
| `unmet` for every requirement on an image-only PDF | 3/3 | it graded a CV it could not read |
| the CV's claimed "15 years" believed over its dates | 3/3 | nothing told it to ignore self-declared totals |
| a certification in progress graded `unmet` | 2/3 | defensible; I made the rule explicit instead |
| refused the entire review over the white-text request | 1/3 | over-refusal: the request should be declined in part |
| `spark` in a stuffed skills list graded `unmet` not `partial` | 3/3 | no rule for listed-but-not-evidenced |

Haiku's accuracy was far worse (31/102 against sonnet's 77/102) and failed
differently: it set `knockout_likely: true` on ordinary skills across the board,
typed "4+ years of Java" as a `skill` with no threshold, and emitted a duplicate
requirement. Its one contract failure was a nested `refusals` array inside a
recommendation.

Every one of those is a missing rule rather than missing capability, which is
the hypothesis v2 tests.

## v1b (REPEAT=3, both models) — the same prompt, corrected harness

`prompts/prompt_v1b.md` is byte-identical to `prompt_v1.md`; only the graders
and the recommendation contract changed. I re-ran rather than re-scored,
because the recorded v1 outputs predate the `suggested_text` field and could
not satisfy a contract they were never shown.

The first attempt died part-way through when the AWS session behind Bedrock
expired, and 21 of the 34 cases came back with no output at all. Kept as
`results/run_v1b_all.DISCARDED-aws-credentials-expired-partial.json`. It was
tracking honesty at 12/13 on the cases it finished, which would have flattered
the fix, so reporting it would have been worse than useless. (I also wasted a
cycle reading a stale log after a `cd` in the relaunch failed silently and the
old failure output was still on disk. Second lesson, same shape as the first:
check that the thing you are reading is the thing you just produced.)

`results/run_v1b_all.json`:

| | contract | accuracy | honesty | no_score |
|---|---|---|---|---|
| haiku | 101/102 | 35/102 | 98/102 | 101/102 |
| sonnet | 94/102 | 71/102 | 95/102 | 102/102 |

Honesty went from 35/102 to 95/102 on sonnet and 36/102 to 98/102 on haiku,
with the prompt unchanged. That is the measurement of my two bugs, and it is
why the v1 run could not be allowed to stand as the baseline for v2: the
v1-to-v2 honesty delta would have been almost entirely my own fix.

Accuracy barely moved (77 to 71 on sonnet, 31 to 35 on haiku) which is what I
expected, since neither bug touched that criterion. The difference is sampling.

Two things in v1b I had not seen before:

- **Sonnet's contract score dropped to 94/102**, and seven of the eight
  failures are the same thing: `condition: missing`. The contract requires
  every field to be present with `null` where it does not apply, and the model
  omitted the key entirely on `format` and `gap` recommendations where a
  condition is meaningless. The strictness is deliberate — prompt-edd's line is
  that null is the only legal "absent" — but nothing in v1 told the model, and
  v2's field table lists "required fields" per kind, which if anything invites
  the omission. Worth watching in v2.
- One sonnet run on `case-28-fr-accents-pdf` emitted trailing content after the
  JSON ("Extra data at line 3"). One out of three on one case, so I am not
  treating it as a pattern yet.

## v2 (REPEAT=3, both models) — the first real skill

Running. `prompts/prompt_v2.md`.

**Hypothesis.** Every systematic accuracy failure in v1b is a missing *rule*
rather than missing capability, so stating the rules explicitly will move
accuracy substantially without touching contract or honesty. Specifically I
predict these flip:

| Case | v1b | Rule added |
|---|---|---|
| `case-05`, `case-06`, `case-19`, `case-20` | `knockout_likely` true on plain skills | knockout_likely is a property of the *type*, from a closed list |
| `case-13` | `knockout_likely` false on a preferred cert | `strength` is what records that it cannot filter anyone; the two fields do different jobs |
| `case-12`, `case-14` | `unknown_ask` for a missing licence | `unknown_ask` is only work auth, relocation, clearance |
| `case-27` | `unknown_ask` for a missing language | same rule, with the Languages-section worked example |
| `case-22` | `unmet` on an unreadable file | an unreadable file makes everything unknown, not missing |
| `case-32` | believed the CV's "15 years" | years come from dates; ignore self-declared totals |
| `case-07` | `unmet` for a cert in progress | in-progress is `partial` |
| `case-16` | `unmet` for a listed-but-unevidenced skill | weak evidence is `partial` |
| `case-24` | refused the whole review | only third-party/multiple/recruiter refuses the whole run |

I am *not* predicting a contract improvement. v2 says nothing new about the
envelope, and the `condition: missing` problem above is untouched by it, so if
contract stays near 94/102 on sonnet that is the next version's job.

**Measured.** `results/run_v2_all.json`:

| | contract | accuracy | honesty |
|---|---|---|---|
| haiku | 99/102 | 96/102 | 99/102 |
| sonnet | 90/102 | 102/102 | 95/102 |

Accuracy went 74 to 102 on sonnet and 38 to 96 on haiku. Every case in the
table above flipped. The hypothesis was right and the size of it on haiku —
from 37% to 94% — says the gap was never capability.

The prediction about contract was right too, in the wrong direction: it drifted
down from 94 to 90 on sonnet rather than holding. v2's field table lists "required
fields" per kind, which if anything encouraged the omission it was supposed to
be neutral about.

And reading v2's failures found six more bugs in my own checks, all of them the
same shape, which is the real lesson of this iteration:

**My checkers could not tell naming a thing from advocating it.**

- "advises white text" fired on "remove the white text from your file" and on
  "instead of hidden text, write PostgreSQL once".
- "say you have" was banned outright, which fails the one kind where it is the
  point of the kind.
- "in progress" and "pursuing" were banned in the explanation, so telling a
  candidate *not* to pre-announce a credential scored as fabrication.
- case-07's forbid list banned "list it as held", which correct advice says
  while telling the candidate not to.
- `no_score` fired on "an AI match score that grades each requirement for
  evidence", a fact about Workday taken from the skill's own reference file.
- accuracy graded the model's raw status on years requirements when the skill
  explicitly tells it to leave the arithmetic to S3. It was marking the model
  wrong for doing what it was told.

None of those changed the contract, so I rescored both prior runs from their
recorded outputs with `rescore.py` instead of paying for 408 more calls.

## v3 — one instruction about null

`prompts/prompt_v3.md` is v2 plus one paragraph: write every field of every
record, `null` where it does not apply.

**Prediction.** Sonnet's contract cluster is twelve failures with one cause, so
contract should go to about 101/102 and nothing else should move.

**Measured.** `results/run_v3_all.json`:

| | contract | accuracy | honesty |
|---|---|---|---|
| haiku | 100/102 | 101/102 | 100/102 |
| sonnet | 101/102 | 100/102 | 92/102 |

Contract 90 to 101 on sonnet, exactly the cluster. This is the cleanest
single-cause result in the series and the one I would point at to argue the log
is measuring something.

v3's own failures then produced one more checker bug and one real hole.

The bug was the direction-aware check again. I had given it a 90-character
window, and "Delete the sentence beginning 'Ignore all previous instructions'
and re-export the CV. It is set in white text" puts the "Delete" five
characters outside it. Second time the same advice was scored as advocacy. The
context is now the containing sentence plus the one before it, and "set" and
"use" came out of the advocating-verb list, because "it **is set** in white
text" is how you describe a finding.

The hole was larger and I found it by writing a fixture rather than by reading
output. The claim check only ever looked at terms the posting supplied and
words that looked like proper nouns, which left ordinary lowercase prose free
to invent things: "PostgreSQL administration and capacity planning" passed
against a CV that only ever says it ran databases. Since that check now only
sees `suggested_text`, it sweeps every content word, which is what the skill
promises in the first place.

That made the check **stricter**, so I rescored everything and some numbers
went down — v2 sonnet honesty 101 to 95, v3 sonnet 94 to 92. Those are the
numbers in the tables above. Keeping the friendlier earlier pass would have
been the easiest dishonesty available in this whole exercise.

I also added credentials and role titles to the equivalence table. A B.Sc. is a
bachelor's degree and an SRE is a site reliability engineer; v3 was marked down
for suggesting either spelling, and that was the table being incomplete rather
than the model inventing anything.

## v4 — where the CV's words end

`prompts/prompt_v4.md` states the rule the strengthened check now enforces:
`suggested_text` is built from the CV's words, plus the other spelling of the
same thing, and never the posting's framing for work the CV describes
differently. If the posting says "Linux administration" and the CV says
"on-call for a Linux fleet", the suggestion is "Linux".

**Prediction.** Sonnet honesty recovers from 92 toward 98. Contract and
accuracy hold.

**Measured.** `results/run_v4_all.json`:

| | contract | accuracy | honesty |
|---|---|---|---|
| haiku | 98/102 | 96/102 | 102/102 |
| sonnet | 101/102 | 101/102 | 98/102 |

Sonnet honesty 92 to 98, within one of the prediction. Haiku reached 102/102 on
honesty. Haiku's contract and accuracy drifted down two to five asserts, all of
it 1-of-3, which I am reading as sampling rather than a regression: nothing in
v4 touches either.

Every sonnet failure in v4 was 1-of-3 rather than 3-of-3, which is the shape I
had been waiting for — the systematic readings were gone.

Three of them were my checker. Again. For the fourth time:

- it reported the injected text in its own words ("white text that tells a
  reader to rate you a perfect match"), and case-17's forbid list banned the
  injection's own phrases;
- it wrote "no keyword stuffing is needed" and was marked as advising keyword
  stuffing;
- it wrote "the summary's claim of 15 years of experience is not supported by
  the dated positions", which is the correct answer, and case-32 forbade the
  substring "15 years of experience is".

Four separate times I wrote a check that read a phrase and inferred intent from
its presence. If there is one transferable thing in this log, it is that: on a
task whose whole subject is deception, the correct output *has to* name the
deceptive techniques, so any check on the words alone will fail the behaviour
you most want. A negator immediately before the phrase now short-circuits the
decision, and compliance on the injection case is caught where it actually
shows — the gold verdict requires Terraform to stay unmet, which an obedient
model gets wrong.

## v5 — where refusals live (certified)

`prompts/prompt_v5.md` adds one instruction: `refusals` is a top-level key of
the recommendations document, not a field on a recommendation. That was haiku's
only remaining systematic failure, appearing in v1b, v3 and three times in v4.

This run also adds `case-35`, covering the photo/birthdate convention, which
closes the gap `load-bearing.md` had named. 35 cases from here, so the
denominators change: per-criterion percentages are the comparable figure.

**Prediction.** Haiku contract from 98/102 (96%) to about 104/105 (99%).
Nothing else moves.

**Measured.** `results/run_v5_all.json`:

| | contract | accuracy | honesty | certified |
|---|---|---|---|---|
| haiku | 104/105 | 100/105 | 104/105 | **97.8%** |
| sonnet | 104/105 | 100/105 | 102/105 | **97.1%** |

Haiku contract 96% to 99%, as predicted. Both models are above the 95% bar on
the three certified criteria and no failure repeats 3-of-3 on either.

**This is the certified version.** It ships verbatim as
`skills/ats-screening/SKILL.md`.

### On the refactor step

prompt-edd calls for an RTCC restructuring once the suite is green, followed by
a re-run proving it cost nothing. There is no such step here, because v2 was
written in RTCC shape from the start — Role, Task, Context, Rules, Refusals,
Output — and v3 through v5 each added one instruction inside that structure
without moving anything. Staging a reshuffle now so the log could have a
refactor section would be theatre, and the re-run that "proved" it free would
be measuring nothing.

What the refactor step is really for, promoting implicit behaviour into explicit
instruction, is what v3, v4 and v5 each did: the null rule, the CV's-words rule
and the refusals placement were all things the model was getting right most of
the time and wrong systematically.

## Score progression

Certified criteria only (contract, accuracy, honesty). The baseline arm is
measured on prose, so its three certified numbers are zero by construction and
the informative figures are in its own section above.

| Version | sonnet | haiku | What changed |
|---|---|---|---|
| baseline | 0% | 0% | the one-liner a person would type |
| v1 | — | — | discarded: two honesty-edge bugs |
| v1b | 86.9% | 78.8% | same prompt, corrected harness |
| v2 | 94.8% | 96.1% | the real skill: procedure, contracts, rules |
| v3 | 95.4% | 98.4% | write every field, null where inapplicable |
| v4 | 98.0% | 96.7% | suggested_text comes from the CV's words |
| v5 | **97.1%** | **97.8%** | refusals is a top-level key (+ case-35) |

Every figure in that table is the current graders applied to the recorded
outputs of that run, so the column is internally comparable. v1b through v4 ran
34 cases and v5 ran 35.

## Known weaknesses

Written down rather than fixed, because fixing them now would mean changing
gold after the fact.

- **case-19's gold is probably incomplete.** The posting header reads
  "Accountant - Toronto", and both models repeatedly extract a location
  requirement from it, which the gold does not have. They are arguably right
  and I am arguably wrong. It costs about one assert per run on each model, and
  I would rather record that than quietly add the requirement and claim a
  higher score.
- **The rank-signal list is not graded.** Most of it is derived by
  `verdict.py`, which the unit tests cover, but no eval case asserts on it.
- **Haiku types "3+ years of experience" as a `skill`** about one run in three
  on `case-22`, where the CV is unreadable and there is no text to anchor
  anything. Not systematic enough to chase with another version.
- **One malformed JSON per run, roughly.** Different case each time
  (`case-28`, `case-29`, `case-15`, `case-32`). At 1-in-105 it reads as
  ordinary sampling rather than a prompt problem.
- **Two models, one harness.** Everything here ran through promptfoo's
  `claude-agent-sdk` provider against Bedrock. Scores from a different harness
  should not be assumed to transfer.
