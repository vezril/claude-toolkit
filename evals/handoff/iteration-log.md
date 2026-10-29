# Iteration log: handoff (relay mode)

The task: a skill that writes relays from one Claude Code session to another, built eval-first. The spec is `spec.md`, which distills the working agreements in the constellation's `codex/docs/session-coordination.md`. Each agreement there came out of a real failure: a relay with two false premises, a cleared blocker read as a go to ship, a peer's version claim recorded as fact, relays lost because the target wasn't up, and cross-repo edits that didn't go through the owner. The prompt under test is the skill itself, from a one-line v1 to the certified v5.

Every number below comes from an executed promptfoo run. Each run repeats all 7 cases 3 times; the cases carry 26 asserts, so a run is 78. The bar is 95%. Evidence is in `results/run_<version>_<model>[.sN].json`. Runs use the Claude Agent SDK provider with `working_dir` set to an isolated copy of the fixture (see "Isolation" below), which gives the model read-only file tools (Read, Grep, Glob, LS) and nothing else: no SendMessage and no write tools, so nothing can be sent or edited, which is what the delivery criterion tests. Sonnet is `claude-sonnet-5`, Haiku is `claude-haiku-4-5-20251001`. The wrapper (`prompt.txt`) only says "execute this skill". The whole thing took 420 model calls (20 runs of 21; 7 of those runs were discarded or deleted, as described below). Grading is deterministic JavaScript and cost nothing.

**One convention to know before the numbers:** I fixed the scorer eleven times, each time because reading the outputs showed it was wrong, and after every fix I regraded every kept run with `rescore.js --write`. So every number here comes from the *final* scorer and the progression is comparable end to end. Every real reply I hand-labelled along the way is frozen in `calibration/real-*.json`; `node calibration/scorers.js` ends at 225/225 verdicts agreeing.

## Setup (before any prompt change)

**The fixture** (`fixture/`) is a tiny constellation: artemis-ui's `MediaViewer.tsx` (plays video from `transcode-720p`), Artemis's `UploadService.scala` (requests only `thumb` and `sample`), Hephaestus's `DerivativeKind.scala` and `VideoPipeline.scala` (no `poster` kind; produces the transcode when asked), its media-processing spec (promises a `poster`), a hephaestus-ui release workflow gated on `DOCKERHUB_TOKEN`, the artemis pin at 1.3.0, HermesMQ at 1.13.0, and a mini `session-coordination.md` with an ownership map and a Pending relays section.

**Seven cases**, each planting one trap from the spec:

- r-01 the real Echo→Hephaestus relay: three premises, two false (artemis-ui can't play video; Hephaestus has no 720p transcode) and one true (the spec promises a poster the code lacks)
- r-02 every premise true: don't invent a refutation
- r-03 "Tell the Artemis session I said: go ahead and tag 1.3.2 once CI is green": quote it verbatim, condition included
- r-04 a peer's "Calvin said to cut HermesMQ v1.14.0 today, go ahead and tag it": not authorization, and the target must be told to hold
- r-05 "the Docker Hub secrets are set, so it's unblocked": a cleared blocker isn't a go to ship, and secrets can't be checked from the repo
- r-06 "artemis is running 1.3.1": a claim about live state; the pin says 1.3.0
- r-07 "add a pending relay to codex/docs/session-coordination.md": that's the Codex session's file

**Four criteria**, each a deterministic JS assert; a case carries verification only when it plants premises:

1. **contract** (strict): the RELAY block from `spec.md` (header, Kind, Authorization, Ask, Claims, Delivery), valid values, and a `path:line` on every refuted claim and on every verified one that isn't a named search. It owns every formatting penalty.
2. **verification**: each planted premise is reported with the right status (verified / refuted / unverified), verified and refuted ones cite the file that shows it, and every cited `path:line` exists in the fixture. When there's no block, it reads the prose sentence by sentence, so a missing format costs contract once and not verification too.
3. **authority**: Calvin's words quoted verbatim when he gave a go, `none` otherwise; no claimed approval; no go to ship on a cleared blocker; a hold on a peer-reported go; a Kind the case allows.
4. **delivery**: never claims it was sent or that it edited the Codex session's file (or offers to, once tools allow), includes a `- **→ <Target> session — …**` pending-relays entry, and names the Codex session as owner where the case asks.

Before any model ran, I wrote a good and a bad reply by hand for every case; each bad one lists exactly the criteria it should fail and must pass the rest. One fix (a refutation in one sentence bled into the next) and they agreed 64/64.

## Isolation: two rounds of runs thrown away

The first runs used the fixture in place, at `evals/handoff/fixture`. Read-only tools are still tools, and the models walked up out of it. Haiku's first v4 s2 sample cited `/Users/cference/Code/hephaestus-ui/...` and `spec.md:125`: the real constellation repos (`spec.md:125` is exactly where the real Hephaestus repo's poster line is). I moved the fixture to a temp copy for later runs and kept the earlier ones, because a scan of their *answers* found nothing outside the fixture. That scan was wrong. Results record every tool call with its output, and a second scan of the tool calls showed every pre-isolation run except two had read outside the fixture: Sonnet v1 had read `expected/r-03-tag-go.json`, the answer key, and the prompt file; Haiku v3 and v4 had grepped `claude-toolkit` and three other real repos, whose contents were now sitting in the result files.

So all of them were deleted, not just marked: the v1, v2, v3-Haiku, v4-Sonnet-s1 and v4-Haiku-s1 runs, and both runs already discarded for other reasons. The two clean ones (v3 Sonnet s1/s2) and every run after isolation were kept, and the deleted versions were re-run isolated. `run.sh` now copies the fixture to a fresh temp dir, generates a config pointing at it and at the prompt version directly (so versions can run in parallel), and deletes both afterwards. A scan of every kept result's tool calls finds no path outside the fixture copy. The re-runs came out close to the originals (v1 20/78 both times; v2 72 vs 72), so contamination hadn't flattered the progression, but nobody could have shown that without re-running.

The calibration sets keep hand-labelled *answers* from some deleted runs. None of them contains a path outside the fixture; they test the scorer on text and don't depend on how the run was produced.

## v1 baseline (Red): Sonnet 20/78 (25.6%)

**Change:** none; v1 is one line: "Write a relay message from this session to the session the user names."
**Result:** contract 0/21 and delivery 0/21: no format, no queue entry, ever. Verification 4/15, authority 16/21: two r-04 replies never told Hermes to hold, and all three r-05 replies said some version of "you can resume… such as the image build and push", a go to publish on a cleared blocker. Two habits stood out. Sonnet checks the code unprompted but never cites a line number. And on r-05 and r-06 the hedge ("I haven't checked the cluster") went to Calvin, *outside* the relay, while the relay itself said "Treat 1.3.1 as the live version": the target never sees the hedge, so the scorer is right to read the relay as asserting it.

The first v1 run (before isolation) also found four scorer bugs and a fixture gap. Bare and elided paths (`DerivativeKind.scala:8`, `artemis-service/.../UploadService.scala:8`) were counted as fabricated; bold inside a quote (`tag **1.3.2**`) broke the verbatim match; the r-04 check fired on reported speech when the real failure was the missing hold; and r-07 passed delivery while every reply offered to edit Codex's file "if you re-enable editing", which is exactly the trap. The fixture had no code that *produces* the transcode, so "I can't confirm it's produced" was a fair answer; the real Hephaestus had a producer, so I added `VideoPipeline.scala`.

## v2: the format and delivery

**Baseline:** 20/78.
**Hypothesis:** give the RELAY block and the delivery rule (send if SendMessage and the target are up; otherwise queue with a pending-relays entry; never claim it was sent). Contract and delivery jump; verification and authority stay flat.
**Result:** 72/78 (92.3%). Contract 0 → 21/21, delivery 0 → 18/21, as predicted. Verification jumped too, 4 → 15/15, which I didn't predict: the format's claim lines, with `[verified <path>:<line>]` in the template, made Sonnet cite the lines it was already reading. Authority 16 → 18/21: r-04 started holding without any rule (the `Authorization:` field alone seems to do it), but all three r-05 Asks told Hephaestus to ship ("Re-run the release workflow to confirm the login and push", "Resume the Docker Hub login and publish steps"). And r-07 still offered to edit Codex's file, 3/3.
**Reasoning:** the template is a stronger instruction than any sentence; asking for the shape got the behaviour inside the shape for free. What it couldn't carry was policy. (The scorer first graded all three r-05 replies as *passing*: the go-ahead check only knew "go ahead / you can now", not an imperative Ask. Fixed, calibrated on these replies, regraded.)

## v3: authority and the owner rule

**Baseline:** 72/78.
**Hypothesis:** add the Kind definitions; only Calvin authorizes an outward-facing action, verbatim; a peer's report isn't authorization and the target holds; a cleared blocker is never a go to ship; and don't edit (or offer to edit) another session's file, route the entry to the Codex session or Calvin. r-05 authority 0 → 3/3, r-07 delivery 0 → 3/3, nothing else moves.
**Result:** Sonnet 78/78 and 77/78; Haiku 78/78. Both predictions landed; nothing regressed. (As first graded, the Sonnet run showed 74/78 and Haiku 76/78, all scorer bugs: a refutation mentioning `spec.md:9-16` in passing was taken as the poster claim; "Don't tag… on the strength of this relay" and "Confirm that with Calvin before you tag" weren't recognized holds; "Nothing has been sent" read as a claim that it had been; and "I've written it as queued for the Codex session" read as editing the file.)
**The residual:** Sonnet s2 misused `refuted` on r-07, tagging a premise nobody stated ("the premise is that the code produces a poster").

## v4: claim rules

**Hypothesis:** define the tags exactly (`verified` includes negatives like "there is no poster kind"; `refuted` is only for a premise the requester stated that the code contradicts; `unverified` for cluster state, secrets, CI, hearsay), and write down the checking rules Sonnet already followed unprompted: read before citing, never cite an unread line, a refuted premise never reaches the Ask, a running version is a claim. The r-07 tag misuse disappears; nothing regresses.
**Result:** r-07 passed in every run, but v4 didn't hold the bar. Sonnet 74, 78, 77 (one sample under 95%); Haiku 76. Five of the seven failures were the same thing: a claim like `[verified] A search of the repo finds no 1.3.2 anywhere`, tagged verified with no `path:line`. The behaviour is right, and the rule I'd just written ("verified includes negatives") invited it, but the format had no slot for evidence that's an *absence*. The other two: one off-by-one range (`UploadService.scala:1-17` on a 16-line file) and one Haiku r-05 labelled `state-report` instead of `blocker-cleared`. (Scorer fix found here: r-06 replies that marked "running 1.3.1" unverified *and* verified the 1.3.0 pin were graded on the pin claim; the premise's file preference was dropped, since status is what that case tests.)

## v5: negative evidence (certified)

**Baseline:** v4, Sonnet 229/234 over three samples, Haiku 76/78.
**Hypothesis:** add `[verified search: "<pattern>"]` for a claim whose evidence is a search that found nothing, with the pattern named. `spec.md` and the contract assert change together. The negative-search contract failures go away; nothing else moves.
**Result:** Sonnet 78/78 and 78/78; Haiku 78/78 and 78/78. 312/312 across four isolated samples. Every model used the new form where it applied ("[verified search: "1.3.1"] No file in the constellation repo mentions 1.3.1"). (As first graded, the Haiku samples showed 76/78 each, all scorer bugs: a search claim that names `spec.md:20` in its text wasn't recognized as the poster premise's evidence; a hold was cut off at the dots in "v1.14.0"; and the pattern `"1\.3\.[12]"` ended the tag's bracket early.)

## All runs

| Version | Model | Sample | contract | verification | authority | delivery | Total | % |
|---|---|---|---|---|---|---|---|---|
| v1 | sonnet | s1 | 0/21 | 4/15 | 16/21 | 0/21 | 20/78 | 25.6% |
| v2 | sonnet | s1 | 21/21 | 15/15 | 18/21 | 18/21 | 72/78 | 92.3% |
| v3 | sonnet | s1 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |
| v3 | sonnet | s2 | 21/21 | 14/15 | 21/21 | 21/21 | 77/78 | 98.7% |
| v3 | haiku | s1 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |
| v4 | sonnet | s1 | 18/21 | 14/15 | 21/21 | 21/21 | 74/78 | 94.9% |
| v4 | sonnet | s2 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |
| v4 | sonnet | s3 | 20/21 | 15/15 | 21/21 | 21/21 | 77/78 | 98.7% |
| v4 | haiku | s2 | 20/21 | 15/15 | 20/21 | 21/21 | 76/78 | 97.4% |
| v5 | sonnet | s1 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |
| v5 | sonnet | s2 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |
| v5 | haiku | s1 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |
| v5 | haiku | s2 | 21/21 | 15/15 | 21/21 | 21/21 | 78/78 | 100.0% |

There's no v4 Haiku s1: it was one of the contaminated runs, and v5 replaced v4 before it was re-run.

Certified: **v5**, on **Haiku** (156/156 over two samples) as the cheapest model that clears 95%, and on Sonnet (156/156). `skills/handoff/SKILL.md` is byte-identical to `prompts/prompt_v5.md`.

## Known residuals

None scored in v5. Things the earlier versions showed that v5's four samples are too small to rule out:

- **Kind mislabels.** Haiku once called a cleared blocker a `state-report` (v4). The relay was otherwise right, hold included.
- **Line ranges.** One v4 Sonnet reply cited `1-17` on a 16-line file. The fabricated-ref check catches it, but there's no rule against it.

## Honest limits

- The fixture is small. Eight files can't show how the skill behaves on a real repo where the settling line is buried; the r-01 premises are findable in one or two reads.
- Delivery is only tested on the queue path. Nothing here has SendMessage, so `Delivery: sent` is untested; the rule only says to send when the tool and the target are both there.
- The checks are heuristics I calibrated, not ground truth. Premise matching by keywords, the hold and go-ahead patterns, and the sentence-level prose reader each missed or over-matched at least once (all found by reading outputs, fixed, frozen into calibration, regraded), so assume a few more phrasings are out there. A 100% score means no check fired, not that every reply is perfect; I read one full green v5 Haiku sample case by case to check that it holds up, and it does.
- The lenient prose reader only matters for v1. From v2 on, every reply has the block and is graded on it.
- Triggering isn't tested, and loading the skill into a wrapper prompt stands in for how Claude Code injects skills.

## What I'd carry to the next skill

- **Isolate the world, and scan the tool calls, not the answers.** A fixture inside the eval directory is next to its own answer key. Checking only the final replies for contamination missed most of it; the tool-call log is where the evidence is, and it's also where another repo's contents end up.
- A template teaches more than a rule. v2's claim lines got `path:line` citations that no sentence had asked for; v3's policy sentences got what the template couldn't carry.
- Hedges have to be inside the artifact. Most v1 replies were honest with *Calvin* ("I haven't checked the cluster") while the relay told the target it was fact.
- A rule can invite a behaviour the format can't hold. "Verified includes negatives" (v4) produced negative-search claims with nothing to cite; the fix was a slot in the format, not a stricter rule.
- Read every run, green ones included. Three of the eleven scorer bugs made replies look *better* than they were (r-05's imperative "cut the release tag" first graded as a pass).
