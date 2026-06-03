# Evaluating skill & agent efficiency

A framework for validating that the skills and subagents in this toolkit actually *earn their keep* — they fire when they should, improve the output when they fire, and don't bloat context doing it. It wraps and extends the existing **skill-creator** harness (`scripts/run_eval.py`, `scripts/run_loop.py`, the grader/comparator/analyzer agents, `evals/evals.json`, `improve_description.py`) rather than reinventing it.

## The core idea

A skill or agent is a *bet*: you spend context (its description is always loaded; its body loads on trigger) in exchange for better behaviour. Validation is just checking the bet pays off. That breaks into four measurable dimensions:

| Dimension | Question it answers | Cheap to measure? |
|-----------|--------------------|--------------------|
| **Structural health** | Is it well-formed? (name==dir, links resolve, frontmatter valid, description sane) | Yes — static, no model calls |
| **Triggering accuracy** | Does the right artifact fire — and stay quiet otherwise? | Medium — needs prompt sets + model runs |
| **Output quality** | When it fires, is the result better than no skill / the previous version? | Expensive — needs graded runs |
| **Context cost** | How much context does it consume, and is the quality gain worth it? | Cheap static + free from run metrics |

The discipline: **structural is a gate** (must pass, run in CI), **triggering and quality are scored** (track over time, gate on regression), **cost is a budget** (flag outliers, weigh against quality).

## Match the method to the artifact

Not everything should be evaluated the same way. Five archetypes in this repo, each with a different success criterion:

1. **Knowledge skills** (`functional-programming`, `clean-code`, `6502-assembly`, `cryptography` …) — mostly advisory prose. Success = *triggers on the right topic* and *measurably shifts the answer toward the source's guidance*. Hard to assert mechanically; lean on triggering + judge-graded quality vs a no-skill baseline.
2. **Procedure/output skills** (`docx`, `xlsx`, `pdf`, `pptx`, the Akka SDK how-tos) — produce a concrete artifact or follow fixed steps. Success = *objectively verifiable* (file exists, has the right structure, the right script ran). Best ROI for `expectations`-based grading.
3. **Meta/router skills** (`akka`, `apple-dev`, `operating-systems`) — should trigger broadly for a domain and point to the right sub-skill. Success = triggering recall across the domain + "named the correct sub-skill."
4. **Reviewer agents** (`scala-fp-reviewer`, `git-and-ci-reviewer`, `crypto-reviewer` …) — read-only, produce findings. Success = *delegated to for the right request* + *findings are correct and well-prioritised* (catches seeded issues, low false-positive rate).
5. **Active agents** (`tdd-coach`, `issue-fixer`, `ios-app-debugger`) — take actions. Success = *task completed* (tests pass, build green, issue closed) measured on the end state, plus delegation correctness.

## Dimension 1 — Structural health (build a repo linter)

The fastest, highest-confidence signal, and the one piece skill-creator doesn't fully cover at repo scope. `scripts/quick_validate.py` validates a single skill (SKILL.md present, exactly one SKILL.md, frontmatter); extend that into a repo-wide check that asserts:

- `name:` frontmatter exists and **equals the directory name** (kebab-case).
- `description:` present, non-empty, and within a length band (say 200–1500 chars — long enough to trigger well, not a wall).
- Every `[[link]]` resolves to an existing skill directory.
- Skills referenced in every agent's `skills:` list (`claude-toolkit:<skill>`) exist.
- No nested `SKILL.md` (plugin discovery is one level deep).
- Agent frontmatter valid (`name`, `description`, `tools`, `model`).
- References named in a SKILL.md "How to use" section exist on disk; no orphaned reference files.

This is a few-hundred-line Python script with **zero model calls**, so it runs in CI on every commit and is the merge gate. (Most of the manual `grep`/`ls` verification done when authoring each skill is exactly this — worth automating.)

## Dimension 2 — Triggering accuracy

Whether the description causes Claude to invoke the artifact. `scripts/run_eval.py` already does this for skills: give it a set of queries and it reports whether the skill triggered. Extend the eval set with **negatives**, because triggering has two failure modes:

- **Recall miss** — a prompt that *should* fire the skill doesn't (description too narrow).
- **False trigger** — a prompt for a *different* domain fires it anyway (description too broad / overlaps a sibling).

So each skill's `evals.json` grows two prompt lists: `should_trigger` (positives) and `should_not_trigger` (near-miss negatives, ideally drawn from sibling skills — e.g. `git` negatives borrowed from `github-actions` positives, since those two overlap). Score as precision/recall (or just "N/M positives fired, K/L negatives stayed quiet"). `improve_description.py` then optimises the description against that set. This matters most where skills overlap: git/github-actions, clean-code/software-design, the Akka cluster, the OS subsystems.

For **agents**, triggering = *delegation*: does a request route to the right subagent by its `description`? Same harness shape — a set of task prompts, assert the intended agent is selected — but run at the agent layer.

## Dimension 3 — Output quality

The real payoff, and the expensive part. Two complementary modes, both already supported:

- **Expectation grading** (`run_eval.py` + the **grader** agent): each eval case lists `expectations` — verifiable statements ("created a .docx with a TOC", "used `pathlib` not `os.path`", "flagged the unpinned action as a security issue"). The grader reads the transcript + outputs and marks each pass/fail with evidence, yielding a pass-rate. Best for archetypes 2 & 4 (verifiable). Write expectations that assert *outcomes*, not trivia.
- **Blind A/B** (`run_loop.py` + the **comparator** agent): run the same prompt **with** and **without** the skill (or new vs old version), hand both outputs to a comparator that doesn't know which is which, and record won/lost/tie. This is how you prove a *knowledge* skill (archetype 1) helps at all — if the no-skill baseline ties the with-skill output, the skill isn't pulling weight. `history.json` tracks version-over-version pass-rate and win/loss.

For reviewer agents, build **seeded-defect fixtures**: small repos/diffs with known planted issues (a `var` where a `val` belongs, an unpinned GitHub Action, a hardcoded secret). The expectation is "agent reports defect X." This gives reviewers an objective recall score and surfaces false-positive noise.

## Dimension 4 — Context cost

Two numbers, both nearly free:

- **Static footprint** — bytes/tokens of the description (always loaded) and of SKILL.md + references (loaded on trigger). The linter can print these; flag descriptions that are very long or bodies that are huge relative to peers.
- **Runtime footprint** — `run_eval.py` already emits `execution_metrics` (tool-call counts, steps, `transcript_chars`, errors). A skill that triggers a lot of flailing tool calls or balloons the transcript is expensive even if correct.

Cost isn't pass/fail; it's the denominator. The decision rule is **quality-per-token**: a skill that wins A/B by a hair but doubles context is a worse bet than a lean one that wins clearly. Set a soft budget (e.g. description ≤ ~1.5k chars, body proportional to scope) and require a quality justification for outliers.

## A unified eval-case schema

Extend skill-creator's `evals/evals.json` (kept inside each skill, ignored by packaging) so one file drives all dimensions:

```json
{
  "skill_name": "git",
  "should_trigger": [
    "How do I squash my last three commits before opening a PR?",
    "Undo a pushed commit without rewriting history"
  ],
  "should_not_trigger": [
    "Write a GitHub Actions workflow that runs my tests on push"
  ],
  "evals": [
    {
      "id": 1,
      "prompt": "I pushed a commit with a secret. What do I do?",
      "expectations": [
        "Advises rotating the secret regardless",
        "Mentions git filter-repo (not filter-branch) to scrub history",
        "Warns that rewriting shared history requires coordination"
      ]
    }
  ]
}
```

Agents get a parallel `agent-evals.json` with `should_delegate` / `should_not_delegate` prompt sets and `fixtures` (paths to seeded-defect repos + the defects each must catch).

## Scoring & decision rules

- **Structural**: binary. Any failure blocks merge.
- **Triggering**: report precision & recall on the prompt sets. Target recall ≥ 0.9 on positives and ≥ 0.9 "stayed quiet" on negatives; below that, run `improve_description.py` or disambiguate against the sibling it's colliding with.
- **Quality**: expectation pass-rate (target, e.g., ≥ 0.8) and/or A/B win vs baseline (must beat "no skill"; a tie means cut or sharpen the skill). Track per version in `history.json`; a new version that *loses* to the current best is rejected.
- **Cost**: advisory budget; outliers need a quality story.

Roll the four into a one-line scorecard per artifact so the whole toolkit's health is visible at a glance (a small aggregator over the per-skill JSON, à la `aggregate_benchmark.py`).

## Rollout (incremental, cheapest-first)

1. **Repo linter** (no model calls) — write it, wire into CI, fix everything it flags. Immediate, durable value; turns the manual verification ritual into a gate.
2. **Triggering sets for the overlap-prone clusters first** (git/github-actions, clean-code/software-design, the OS and Akka families), then the rest. Optimise descriptions where recall/precision is weak.
3. **Expectation evals for the verifiable skills** (docx/xlsx/pdf/pptx, procedural Akka SDK skills) — highest grading ROI.
4. **Seeded-defect fixtures + delegation sets for the reviewer agents.**
5. **A/B-vs-baseline for the knowledge skills** — last, because it's the most expensive and most subjective.
6. **Aggregate scorecard + CI**: linter on every commit; triggering/quality on a schedule or pre-release (they cost model calls), gating on regression against the stored baseline.

## Worked example: the `git` skill

- *Structural*: linter confirms `name: git` == dir, all `[[links]]` (github-actions, devops, tdd, …) resolve, three reference files referenced and present. ✅ gate.
- *Triggering*: 8 `should_trigger` git prompts, 4 `should_not_trigger` borrowed from `github-actions`. If "set up CI on push" wrongly fires `git`, tighten the description boundary between the two.
- *Quality*: the secret-in-history case above, graded on three expectations; plus an A/B where the no-skill baseline likely forgets to say "rotate the secret anyway" — that delta is the skill's value.
- *Cost*: description ~1.4k chars, body + 3 refs load on trigger; within budget.

## What exists vs what to build

Already in **skill-creator**: `run_eval.py` (triggering), `run_loop.py` + grader/comparator/analyzer (quality + A/B), `improve_description.py` (description tuning), `aggregate_benchmark.py` + `eval-viewer/` (reporting), `quick_validate.py` (single-skill structural), the `evals.json`/`history.json`/`grading.json` schemas.

To build for this repo: (a) the **repo-wide structural linter** + CI hook; (b) `should_not_trigger` **negative sets** and a precision/recall reporter; (c) the **agent delegation harness** and **seeded-defect fixtures**; (d) a **toolkit-level scorecard** aggregating all four dimensions across every skill and agent.
