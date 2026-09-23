# Iteration log: pr-description

The task: given a branch's diff and commit subjects, write the PR description. It's the step in my delivery flow that turns finished work into the thing a reviewer reads first, so an invented reason or a missing file costs real review time. The prompt under test is my existing `pr-description` skill. Until this work it lived only in `~/.claude/skills/`, unversioned, typo included. v1 is that file byte for byte.

Every number below comes from an executed promptfoo run. Each run repeats all 10 cases 3 times on each model, so every model gets 90 asserts per version. The bar is 95%. Evidence is in `results/run_<version>_all.json`. Runs go through the Claude Agent SDK provider with no working directory, which means the model sits in an empty temp dir with no tools. It can't run `git diff` against this repo and has to work from the diff it's given. I checked the provider's source for that before trusting any score.

## Setup (before any prompt change)

Ten cases. Nine are real merged PRs from my own public Olympus repos, fetched with `gh pr diff`. One is the synthetic case the old suite had. Each plants a trap:

- case-01: synthetic; one modified, one deleted and one added file
- case-02 (hermesmq #89): tests and a README across three client suites, with no client source change, so naming `HermesClient.scala` would be inventing a file
- case-03 (dionysus-service #6): a Docker volume fix spread across build, Helm chart and app config
- case-04 (apollo-storage #29): one dependency plus a regression test
- case-05 (dionysus-service #7): a behaviour change with spec, repository, route and tests
- case-06 (hermesmq #88): client hardening across Scala source and three test suites
- case-07 (artemis-service #69): an OpenSpec archive, five renames and one new spec, no code
- case-08 (ariadne-service #20): a subtle timestamp-precision fix
- case-09 (hephaestus-service #9): a logging toggle across build and logback config
- case-10 (demeter-service #53): a Dependabot action bump whose diff says nothing about why

Three criteria, each a deterministic JS assert:

1. **contract** (strict): starts with `## What`, exactly What/Why/Changes in order, a one-sentence What, a non-empty Why, only bullets under Changes, no code fence. It owns every formatting penalty.
2. **coverage** (lenient; a wrapping fence is stripped first): every required file is named, deleted or renamed files are called out as such, and every key change is present as a keyword group.
3. **fidelity** (lenient): nothing invented. Every file-like token, every version-like number and every ticket reference must appear in what the model was given. No speculation phrased as fact ("may include", "typically include"), plus a few case-specific inventions.

Before any model run I fed the scorers a hand-written good description and a deliberately bad one, to check they pass and fail for the right reasons.

## v1 run 1: discarded

**Baseline:** Haiku 29/30, Sonnet 30/30, one repeat each.
**Hypothesis:** none; this was meant to be the baseline.
**Change:** none.
**Result:** too good to trust. When I read the outputs, Haiku's case-10 Why said v6.0.0 "may include bug fixes, security improvements, or performance enhancements". My fidelity check only knew "security fix/patch/update/issue", so it let that through.
**Reasoning:** two things in my suite were wrong. Fidelity was too lenient, and my harness told the model "Reply with ONLY the PR description", which the skill itself never says. That line was doing the prompt's job. I kept the run as `results/run_v1_all.DISCARDED-lenient-suite.json`, removed the harness line, and made fidelity catch speculation. A second single-repeat v1 run on the fixed suite (Haiku 29/30, Sonnet 28/30) turned up two more suite problems: my file check flagged a real path shortened with "..." (`client/src/test/scala/.../HermesClientSpec.scala`), and "typically include" slipped past the speculation list. I fixed both and switched to 3 repeats because single runs were too noisy to act on. That intermediate results file got overwritten by the next run, so there's no evidence file for it; I'm reporting it from my notes only, and nothing below depends on it.

## v1 baseline (Red): Haiku 83/90 (92.2%), Sonnet 84/90 (93.3%)

**Baseline:** the unmodified skill on the corrected suite.
**Hypothesis:** none.
**Change:** none.
**Result:** both below the bar, failing in different ways. Sonnet's problem was shape: four preambles ("Writing a PR description for the … branch based on the diff shown.") and one trailing "Note:" paragraph. Haiku's was content: bullets that didn't name the main changed file (case-06, case-09), Dependabot security filler twice, and "OpenAPI 3" turned into "3.0". Sonnet also claimed the JS client "already ignores content-type" through `res.json()`, but no JS client source is in that diff. My file rule caught it because `res.json` looks like a file name. The verdict is right, but the rule caught it for a slightly wrong reason.
**Reasoning:** three concerns, three iterations: shape, then naming files, then where Why comes from.

## v2: output contract

**Baseline:** Haiku 83/90, Sonnet 84/90.
**Hypothesis:** add an output contract only. Sonnet contract goes 25 → ~30; Haiku stays at 30; coverage and fidelity don't move.
**Change:** an Output section: the reply is the description and nothing else, first line `## What`, no preamble, notes or fence, only bullets under Changes.
**Result:** Haiku 77/90 (85.6%), Sonnet 87/90 (96.7%). The contract part landed exactly (Sonnet 25 → 30). What I didn't predict: coverage fell, Sonnet 30 → 27 and Haiku 26 → 20, almost all from bullets that stopped naming the file they describe.
**Reasoning:** telling a model "nothing else, only bullets" made it terser, and file names were the first thing to go. A shape constraint needs a matching content requirement next to it, or it trades one failure for another.

## v3: every bullet names its files

**Baseline:** Haiku 77/90, Sonnet 87/90.
**Hypothesis:** each Changes bullet names its file(s) and what changed, and every changed file appears. Haiku coverage 20 → ≥28, Sonnet 27 → 30, fidelity unchanged.
**Change:** one bullet added under Changes: name the files each bullet covers, cover every changed file, say what a new file contains.
**Result:** Haiku 87/90 (96.7%), Sonnet 90/90 (100%). Coverage 30/30 on both, as predicted; fidelity unchanged, as predicted. Haiku's only failures were case-10's security filler, 3 of 3 repeats.
**Reasoning:** Haiku technically passes at 96.7%, but a failure on every repeat of one case is a defect, not noise. Next is the Why.

## v4: Why comes from evidence only

**Baseline:** Haiku 87/90, Sonnet 90/90.
**Hypothesis:** Why only states reasons the diff, commits and comments give; with none, say what kind of change it is and stop. Haiku fidelity 27 → 30, nothing else moves.
**Change:** rewrote the Why line to say where reasons may come from and what to do when there's none.
**Result:** the first run hit my usage limit partway through (19 of 30 Haiku case-runs, none of case-10). I kept it as `results/run_v4_all.DISCARDED-usage-limit-partial.json` and didn't score it. The full re-run: Haiku 89/90 (98.9%), Sonnet 90/90 (100%). case-10 passed 3 of 3. One thing I didn't predict: in 1 of 3 Haiku runs on case-08 it named `PostgresFlyerLedger.scala`, which is a class inside `FlyerLedger.scala`, not a file.
**Reasoning:** case-08 was 3 of 3 in v3, so I read the new miss as sampling variance rather than something v4 caused. Both models are above the bar.

## v5: Refactor to Role / Task / Context / Constraints

**Baseline:** Haiku 89/90, Sonnet 90/90.
**Hypothesis:** restructuring costs nothing: same scores on both models.
**Change:** restructured into Role, Task, Context, Format and Constraints; fixed the "amde" typo; wrote down two behaviors the model mostly does on its own (copy numbers exactly, name files the way the diff headers do). The second one aims at the case-08 slip, so this isn't a pure refactor, and I don't credit it as one.
**Result:** Haiku 89/90 (98.9%), Sonnet 90/90 (100%). No regression. The file-name rule didn't cure case-08: Haiku named `PostgresFlyerLedger.scala` again in 1 of 3 runs.
**Reasoning:** the refactor held. case-08 is now 2 of 6 across v4 and v5, a small persistent habit on Haiku rather than pure chance. It sits well inside the bar, so I'm certifying v5 on Haiku and noting it as the known residual to watch.

## Score progression

| Run | Model | contract | coverage | fidelity | Total | Evidence |
|-----|-------|----------|----------|----------|-------|----------|
| v1 (discarded, lenient suite) | Haiku | 10/10 | 9/10 | 10/10 | 29/30 | run_v1_all.DISCARDED-lenient-suite.json |
| v1 (discarded, lenient suite) | Sonnet | 10/10 | 10/10 | 10/10 | 30/30 | same |
| v1 baseline | Haiku | 30/30 | 26/30 | 27/30 | 83/90 (92.2%) | run_v1_all.json |
| v1 baseline | Sonnet | 25/30 | 30/30 | 29/30 | 84/90 (93.3%) | run_v1_all.json |
| v2 output contract | Haiku | 30/30 | 20/30 | 27/30 | 77/90 (85.6%) | run_v2_all.json |
| v2 output contract | Sonnet | 30/30 | 27/30 | 30/30 | 87/90 (96.7%) | run_v2_all.json |
| v3 name the files | Haiku | 30/30 | 30/30 | 27/30 | 87/90 (96.7%) | run_v3_all.json |
| v3 name the files | Sonnet | 30/30 | 30/30 | 30/30 | 90/90 (100%) | run_v3_all.json |
| v4 Why from evidence | Haiku | 30/30 | 30/30 | 29/30 | 89/90 (98.9%) | run_v4_all.json |
| v4 Why from evidence | Sonnet | 30/30 | 30/30 | 30/30 | 90/90 (100%) | run_v4_all.json |
| v5 refactor | Haiku | 30/30 | 30/30 | 29/30 | **89/90 (98.9%)** | run_v5_all.json |
| v5 refactor | Sonnet | 30/30 | 30/30 | 30/30 | 90/90 (100%) | run_v5_all.json |

Certified: v5 on **Haiku**, the cheapest model that clears 95%. Sonnet also clears it.

## What I'd carry to the next prompt

- Read the outputs of a green baseline before believing it. My first "passing" v1 was a lenient suite plus a harness line doing the prompt's work.
- Keep the eval harness neutral. If the wrapper tells the model how to format, the contract criterion measures the wrapper.
- A shape constraint makes models terser. Pair it with an explicit content requirement, or coverage pays for it.
- Repeat every case. Single runs moved by one or two asserts between identical runs, which is the same size as the effects I was trying to measure.
