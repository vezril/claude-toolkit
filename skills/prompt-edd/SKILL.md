---
name: prompt-edd
description: Eval-driven prompt development (EDD) with promptfoo — build a prompt, a measurable eval suite, and an iteration log with real Red/Green/Refactor evidence. Use this whenever the user wants to develop or certify a prompt with measurable quality (AI Maturity Stage 3 certification, "build evals for my prompt", "measure whether my prompt change helped", before/after prompt metrics, iteration log, promptfoo, load-bearing prompt review). Trigger even if they only ask for one piece (just the evals, just the log) — the pieces only mean something built together, in order.
user-invocable: true
argument-hint: "[task the prompt should perform, e.g. 'meeting notes -> action items']"
---

# Eval-Driven Prompt Development (EDD)

Produce three artifacts that prove a prompt works: **the prompt** (structured, every instruction load-bearing), **the evals** (promptfoo, ≥3 distinct criteria), and **the iteration log** (measured Red/Green/Refactor progression). The core discipline: write the evals first, measure a naive baseline, then change the prompt one hypothesis at a time. Never write the log from memory or invent scores — every number must come from a promptfoo run you actually executed.

## Step 0 — Pick a task that can be measured

If the user hasn't fixed the task, steer toward **transformation/extraction with structured output** (notes→tickets, transcript→action items, diff→changelog, report→classification). These allow deterministic asserts with ground truth, which score reliably on mid-tier models. Open-ended generation ("write a blog post") forces LLM-rubric grading: noisy, expensive, and it muddies cause-and-effect in the log. If the user's task is open-ended, say so and help them carve out the measurable core.

## Step 1 — Build the eval suite FIRST

Layout (all paths relative to the project root):

```
prompt.md                  # final deliverable (written last)
prompts/prompt_v1.md ...   # version history, one file per iteration
evals/
  promptfooconfig.yaml
  transcripts/ (or inputs/) # test inputs
  expected/                 # ground truth per input
  asserts/lib.js schema.js recall.js precision.js
  provider/
results/                    # promptfoo -o output per run, this is the evidence
```

### Three distinct criteria (not three variations of one check)

1. **Format/schema** (strict): output parses raw, exact top-level shape, exact keys, valid value formats. No fence-stripping, no leniency — this criterion IS the strictness.
2. **Recall/completeness** (lenient parse): every ground-truth item is present.
3. **Precision/faithfulness** (lenient parse): nothing hallucinated, no duplicates, attributes (owners, dates, labels) exactly right; placeholders like "Unassigned"/"TBD"/"N/A" count as wrong — null is the only legal "absent".

Criteria 2 and 3 must parse leniently (strip fences, accept a bare array, find the item list) so a formatting mistake is penalized once by criterion 1, not three times. If one root cause can flip all your criteria at once, they aren't distinct — and the iteration log becomes unreadable because every change moves every number.

### Test inputs: embed the failure modes

6–10 inputs, each planting a known trap. For extraction tasks the reliable set is: a happy path; items with absent fields (nulls must not be invented); speculative "someday" chatter (should be excluded); decisions and already-completed work (not actions); implicit attribution ("I'll take that" → the labeled speaker); relative dates resolvable from a stated date in the input header; one long noisy input; and one **empty case** (correct answer is an empty list — models hate this one, and it catches over-extraction).

Ground truth uses **keyword groups**, not exact strings: an output item matches if, for every group, at least one alternative appears in its text (case-insensitive). This survives paraphrase without an LLM judge. Pick 1–2 distinctive tokens per item ("kafka", "invoice"), not common words.

### Scoring rules

Each assert passes only at score 1.0 for its test case. Suite bar: ≥95% of all asserts (e.g. 23/24). Return `{pass, score, reason}` from each JS assert with a reason string specific enough to diagnose from the results JSON alone.

### promptfoo mechanics that will bite you

- **Exec provider arguments:** promptfoo calls the script with THREE args — rendered prompt, options JSON, context JSON. The context JSON **contains the test's ground truth**. Use `$1` only. Grabbing the last arg silently leaks expected answers to the model and invalidates every score while looking like everything works.
- Run with `--no-cache` and `-o results/run_vN.json` every time; the results files are the log's evidence.
- A keyless provider: `claude -p "$1" --model sonnet` (Claude Code CLI, needs `claude /login`). Certification frameworks usually require mid-tier models (Sonnet/GPT-4) — this satisfies that and any teammate can re-run it.
- For reproducibility, support a replay mode: if `REPLAY_DIR` is set, return the saved output for the input's ID instead of calling the model. Recorded runs then re-score deterministically.

## Step 2 — Baseline (Red)

v1 is the naive one-liner a person would actually type first ("Extract the X from this Y. Return JSON."). Do not pre-harden it — an artificially bad baseline is dishonest, and an accidentally good one still teaches you where the real gaps are. Run the full suite, save the results JSON, and record per-criterion numbers. Typical honest finding: mid-tier models often already nail *content* (recall) and fail on *shape* (fences, wrong top-level) — the log is more credible when it reports what actually failed rather than what you expected to fail.

## Step 3 — Iterate (Green), one hypothesis at a time

Each iteration: state the hypothesis (which asserts will flip and why), change **one concern** in the prompt, save as a new `prompts/prompt_vN.md`, re-run, record. Resist bundling fixes — the certifier (and future you) needs each delta attributable to one cause. Predictions that match measured deltas are the strongest evidence in the whole package.

Known high-leverage fixes, in the order they usually land:
- **No output contract → add one**: raw JSON only, exact top-level shape, exact keys, value formats. Fixes most schema failures at once.
- **String-typed fields with no null option → allow null and ban placeholders.** Models fill specification gaps with plausible inventions; give them a legal way to say "absent".
- **Prose prohibitions losing to the harness → anchor literals.** "No code fences" can lose to a chat-tuned system prompt; "The first character of your response must be { and the last must be }" wins.

When the suite is green, do the **Refactor**: restructure into RTCC (Role, Task, Context, Constraints) and promote every behavior the model does implicitly into an explicit instruction — implicit correct behavior is what drifts when the model version changes. Re-run to prove the refactor cost nothing. That re-run IS the refactor evidence; without it you just rewrote the prompt.

**Verify on the environment the evaluator will use.** Scores from one harness (SDK, API) don't automatically transfer to another (CLI with a chat system prompt). If a live run flakes where replay was clean, that's a real iteration — treat it as a new Red, not noise to re-roll.

## Step 4 — Write the artifacts

**prompt.md**: the final RTCC prompt plus a load-bearing appendix — a table mapping every instruction to the criterion(s) it serves. If an instruction maps to nothing, delete the instruction, don't invent a mapping. Target ≥90% load-bearing (certifications commonly require this).

**iteration-log.md**: per iteration — baseline scores, hypothesis, exact change, measured result, reasoning. Include a score-progression table across all runs and criteria. Include the embarrassing parts (discarded contaminated runs, harness bugs, wrong guesses): self-incriminating detail is what makes a log credible, and omitting it is the difference between evidence and marketing.

Write both in a plain first-person voice: contractions fine, varied sentence lengths, no em-dash chains, no "not X — it was Y" constructions, no identical bolded skeleton repeated per section. Polished-symmetric prose reads as AI-generated and undermines a document whose entire job is credibility.

**Package** (if a certification wants a bundle): zip prompt.md, iteration-log.md, evals/, prompts/, outputs/, results/ — history and evidence included, scratch excluded.

## Step 5 — Persist the learnings (close the loop)

An iteration log proves the work; it doesn't make the next run smarter. If the user keeps a [[vault-graphrag]] knowledge graph, end every EDD run by writing the transferable findings into it as `lesson` notes (schema in that skill's references/schema.md): each confirmed hypothesis→measured-delta pair is a candidate. Only mint what generalizes beyond this task ("an output contract with anchored literals fixes shape failures" qualifies; "case-07 needed a design-link rule" doesn't). Check `lessons/` first and extend an existing note's Evidence section instead of minting a near-duplicate. And the read side is the actual payoff: at Step 1 of the NEXT run, read `lessons/` before designing the suite — persisted memory you don't consult is a diary, not memory.

## Failure modes to refuse

- Writing the iteration log before or without running evals (fabricated evidence).
- "Improving" a score by weakening an assert instead of the prompt — if an assert is genuinely wrong, fix it, say so in the log, and re-run **all** prior versions so the progression stays comparable.
- LLM-rubric asserts as the primary criteria when deterministic checks are possible.
- Reporting a contaminated or misconfigured run's numbers because they look good.
