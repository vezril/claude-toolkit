# Iteration log: writing-for-agents

Written as the runs happened. Predictions are recorded before the run they predict.

## Prediction for v1 (one-liner) and v2 (upstream verbatim), written before either ran

v1 says "make it clear and concise". Sonnet will cut the obvious no-ops ("be thorough", the
expert-role line) and the duplicate on its own, so I expect **prune** to mostly pass on w-01 and
fail on w-02, where the command and layout lists look useful rather than redundant. I expect v1 to
fail **steps** (nothing asks for a done-when on each step), **disclosure** (nothing suggests moving
the monorepo table out) and **positive** (it'll keep "Don't use `any`" because it's already short).
**pointer** is a coin toss: "concise" pulls the description shorter but won't stop it opening with
"This skill…".

v2 is Matt Pocock's skill unchanged, with SKILL-MECHANICS.md in its base directory. Its sections map
almost one-to-one onto the criteria: completion criteria → **steps**, progressive disclosure →
**disclosure**, negation → **positive**, the environment-as-cache rule → **prune** on w-02, pointer
rules → **pointer**. I expect it to flip most of them. The risk I see is **preserve**: a skill that
preaches pruning might cut the ledger reason or the BREAKING rationale.

## v1 and v2 measured (after the scorer fixes below)

| run | sonnet | haiku |
|---|---|---|
| v1 | 28/48 (58%) | 28/48 (58%) |
| v2 | 42/48 (88%) | 42/48 (88%) |

The first scoring of these runs was wrong in several places, all found by reading the revisions, all
fixed, calibrated (61/61) and both runs regraded with `rescore.js --write`:

- "Work on a branch; main stays untouched" keeps the main-branch guardrail without the word
  "commit", and `git log --no-merges` keeps the merge-commit rule. preserve now accepts those.
- "Type everything precisely" is the positive form of "Don't use `any`", the very rewrite the skill
  asks for; preserve and positive were demanding the word `any` or `unknown`.
- Completion criteria come phrased as "Finish only when…", "Step is complete when…", "Before
  reporting done…". The regex only knew "Done when".
- The duplicate check counted the description's mention of Keep a Changelog. Frontmatter is the
  pointer's business, so prune now reads bodies only.
- Synonym padding was counted as mentions, which penalized repeating the leading word. It's now
  distinct synonyms for one branch, max 2.

Against my prediction: v1 already passed **preserve** on Sonnet and **format** everywhere, and failed
**prune** on w-01 too, not only w-02 (it kept "Make sure to" and the duplicate). v2 flipped
**disclosure** (0 → 3/3 on both), **positive** and **prune** as predicted. **preserve** held on Sonnet;
Haiku dropped the BREAKING rationale once, the risk I named.

What's left in v2 is two things, both rules the skill already states in the abstract:

- **pointer**: Sonnet keeps "CHANGELOG.md, release notes, version history" in every w-01 description
  (3/3), and Haiku opens two of three w-03 descriptions with "Use when…".
- **steps**: Sonnet leaves a conditional step ("In a monorepo, read …") or the last step without a
  done-when on 2 of 6 cases; Haiku once.

## v3: make the pointer rules concrete (one concern)

Hypothesis: the two pointer bullets are right but abstract. "Front-load the leading word" doesn't say
what the leading word *is*, and "synonyms that rename a single branch" doesn't show one. Adding a
worked example to each should flip the w-01 synonym failures (3 on Sonnet) and the w-03 "Use when…"
openings (2 on Haiku), and move nothing else. Change: those two bullets only.

I first wrote those examples using the eval's own words ("changelog, release notes, version history",
"App Store release notes") and started the run before I noticed: that teaches to the test. I killed it
before it finished, deleted the partial results, and rewrote the examples from an unrelated domain
(invoice reminders; deploy/ship/release/roll out). Only the second wording was measured.

## v3 measured

| run | sonnet | haiku |
|---|---|---|
| v3 | 43/48 (90%) | 39/48 (81%) |

**pointer** moved as predicted: Sonnet 3/6 → 5/6, Haiku 4/6 → 5/6. One Sonnet w-01 description still
lists three names, and one Haiku w-03 still opens "Use when…". Nothing else should have moved, and on
Sonnet nothing did (preserve lost one sample on the `any` rule). Haiku's total fell from 42 to 39,
spread over prune (one kept duplicate), disclosure (one left the table inline), and positive (one
dropped the passive-voice rule outright, one kept "never `any`"). None of those touch the bullets v3
changed, and each is one sample of three, so I read it as Haiku's sample-to-sample spread rather than
an effect; it's why the certification runs below take more samples. (Scorer fix found here: "starts
with an active verb … not 'Retry was added'" is the positive form of the passive-voice rule; positive
now accepts it. Recalibrated 68/68 and regraded v1–v3.)

## v4: a done-when on every step (one concern)

Hypothesis: the skill says "every step ends on a completion criterion" but Sonnet skips it on
conditional steps ("In a monorepo, read …") and on the last step, 3 of 6 cases in both v2 and v3.
Saying where the criterion goes (the step's last sentence) and naming the two kinds of step it gets
skipped on should take **steps** to 6/6 on Sonnet and leave the rest alone. The examples are from an
unrelated domain (a service with a queue).

## v4 measured

| run | sonnet | haiku |
|---|---|---|
| v4 | 46/48 (96%) | 43/48 (90%) |

**steps** went to 6/6 on both models, as predicted (Sonnet was 3/6 in v2 and v3). Nothing else
regressed beyond the one-sample wobble seen before. What's left, read in the replies:

- Sonnet: once dropped the type rule entirely (no `any`, no "type precisely"); once kept Keep a
  Changelog twice in the body.
- Haiku: dropped the BREAKING rationale ("downstream teams search for that word") in 2 of 3 w-01
  samples, kept "Never use default exports" next to its positive in 2 of 3 w-02 samples, and opened
  one w-03 description with a verb ("Drafts and translates…").

## v5: keep the reason with its rule (one concern)

Hypothesis: the pruning section already says to cache "the reason behind a choice", but as one item
in a list about what a document should restate. Haiku reads "make it shorter" and shortens the
reason away. A bullet of its own, saying to shorten a rule's wording but never its reason, should
flip Haiku's two **preserve** misses on w-01 and move nothing else.

## v5 measured, and one more scorer fix

| run | sonnet | haiku |
|---|---|---|
| v5 | 47/48 (98%) | 45/48 (94%) |
| v5 s2 | 46/48 (96%) | 44/48 (92%) |

**preserve** went to 9/9 on both models in both samples, as predicted (Haiku had lost the BREAKING
rationale in 2 of 3 v4 samples).

Scorer fix found while reading v5: the duplicate check counted every mention of "Keep a Changelog",
so a revision that states the format once and then says "sort each commit under one Keep a Changelog
section" was marked as keeping the planted duplicate. The planted defect is the *rule* said twice;
prune now counts statements of conformance ("follow/conform to Keep a Changelog", "Keep a Changelog
format"). Calibrated 82/82 (a real v5 reply that passes, a doubled rule that fails), all five versions
regraded. The table rows above and below are the regraded numbers.

## Progression (all regraded with the final asserts)

| run | sonnet | haiku |
|---|---|---|
| v1 one-liner | 28/48 (58%) | 28/48 (58%) |
| v2 upstream verbatim | 42/48 (88%) | 42/48 (88%) |
| v3 + pointer examples | 43/48 (90%) | 41/48 (85%) |
| v4 + done-when on every step | 46/48 (96%) | 43/48 (90%) |
| v5 + keep the reason with its rule | 47/48 (98%) | 45/48 (94%) |
| v5 s2 | 46/48 (96%) | 44/48 (92%) |

## Certification

v5 is certified on **Sonnet**: 93/96 (96.9%) over two samples. Haiku doesn't clear the 95% bar
(89/96, 92.7%), and its remaining misses don't share a cause I could write a rule for: one
description opened with a verb, one dropped the monorepo trigger, one kept "Never use `any`" next to
its positive, one left the table inline. So the skill ships with Sonnet as the eval model, and the
README says Haiku sits just under the bar. Sonnet's remaining misses are the w-01 description still
naming three things (changelog, release notes, version history) in 3 of 6 samples. The skill tells it
not to; in a toolkit whose users do say "release notes", I'm not sure it's wrong.

What the suite doesn't measure: SKILL-MECHANICS.md (invocation choice, router skills), "when to
split", leading-word refactoring beyond the description, and whether the rewritten documents work
better for an agent, which would need a second eval running each revision.
