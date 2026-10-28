# Iteration log: grilling

Written as the runs happened. Predictions are recorded before the run they predict.

## Prediction for v1 (one-liner) and v2 (upstream verbatim), written before either ran

v1 is the sentence a person would type: "ask probing questions until we reach a shared understanding."
I expect it to fail **format** everywhere (it has no format to follow), and to lose **frontier** on most
cases: a plain "grill me" reply tends to fire every question it can think of at once, downstream ones
included. I expect **facts** to fail on at least one case per model (asking "which database?" when
docker-compose.yml says Postgres). **hold** should pass; nothing in a grilling request invites code.

v2 is Matt Pocock's `grilling` skill unchanged. Its round format should take **format** to full marks,
its "a question whose answer depends on another question still open in this round belongs to a later
round" should flip most **frontier** failures, and "finding facts is your job" should flip **facts**.
I'm least sure about frontier on g-01 and g-02: the requests name the downstream questions out loud,
which is the bait.

## v1 and v2 measured (after the scorer fixes below)

| run | sonnet | haiku |
|---|---|---|
| v1 | 29/45 (64%) | 27/45 (60%) |
| v2 | 45/45 (100%) | 45/45 (100%) |
| v2 s2 | 44/45 (98%) | 44/45 (98%) |

The first scoring was wrong, and reading the replies is what showed it:

- **frontier** first required the reply to ask the "root" decision I'd planted (time goal vs finish;
  where the seam goes). Both models instead asked first about the facts that decision hangs on
  (current weekly mileage and a recent 5K time; *why* split at all). That's the skill working, a
  better design tree than mine, so frontier now grades only the half I can defend: the decisions the
  user said hang on an open choice (link expiry, the new limit, target pace, per-service deploys)
  must not be asked in round one.
- The downstream patterns were too broad: "Do you have a recent 5K time we can use to estimate a
  realistic pace?" gathers a fact, it doesn't decide a pace; "Can the owner un-share at any time?"
  isn't link expiry. Narrowed to questions that *decide* the parameter.
- **facts** also required the reply to state each planted fact. A sharing plan never needs the
  database's name, so that half was unjustified; facts now grades only "never asked the user for
  something the repo answers".
- Sentence splitting flattened newlines first, gluing a block's header onto the question under it.
- **hold** flagged "I'll start with the foundational one" (a question) as announcing work.

Calibration grew from 38 to 65 hand-labelled checks, all agreeing; both runs regraded in place.

Against my prediction: v1 lost **format** everywhere (as predicted, it has no format to follow) and
**frontier** on 4 of 12 (Sonnet) and 6 of 12 (Haiku) samples, mostly g-01 (asking link expiry and
the invitation email before public-vs-invite) and g-02 (the burst size). **facts** passed in every
run of both versions: neither model asks a user for something it can read. So facts is a guard here,
not evidence that the skill helps. v2 took **frontier** to 12/12 on both models, and the second
sample's one miss per model ("Shared database as a default?" before the seam is settled) is a real
downstream question asked early.

## Certification

v2, the upstream skill unchanged, is certified on **Haiku** (the cheapest model that clears the 95%
bar): 45/45 and 44/45 across two samples, 89/90 (98.9%). Sonnet scores the same. No iteration past v2:
nothing in the failures pointed at a change worth one.

What this suite doesn't measure: anything after round one (recomputing the frontier from answers,
knowing when the tree is empty), "word each question so yes accepts the recommendation", and
dispatching a subagent for facts (the eval has no Task tool; both models read the files directly).
