# cross-examine — EDD iteration log

**Read this first: despite the directory name, this suite does not test the `cross-examine`
skill.** Its `defaultTest.vars` binds `agent: file://../../agents/adversarial-validator.md`,
so what it measures is the **adversarial-validator agent definition**. The `cross-examine`
skill has no suite, and its row in the README's EDD table is deliberately left blank rather
than filled in with the number below.

Model: `sonnet` via `evals/_provider/claude.sh`. **N=3 per case, majority scoring**, matching
CI's `repeat: 3` / `repeat-min-pass: 2`.

## Result

| Arm | Run 1 | Run 2 | Run 3 | **Majority** |
|---|---|---|---|---|
| naive baseline, no agent definition | 0/2 | 0/2 | 0/2 | **0/2 (0%)** |
| with `adversarial-validator.md` | 2/2 | 2/2 | 2/2 | **2/2 (100%)** |

| Case | Baseline | With agent |
|---|---|---|
| contradicted analysis — the timeline disproves the stated cause | **FFF fail** | PPP pass |
| sound analysis — consistent evidence; must not invent a hole | **FFF fail** | PPP pass |

Both arms perfectly stable across three runs.

## A 0% baseline is the expected answer, not a broken harness

The asserts require a structured deliverable: a `## Verdict:` line reading
REFUTED/WEAKENED/SURVIVED, an attack log table with at least three rows, and an absence of
endorsement vocabulary. A generic assistant handed the same artifact writes balanced review
prose. The recorded failure reason is literally `missing or malformed "## Verdict:" line;
missing Attack log section; only 0 attack rows (minimum 3); used endorsement vocabulary
(CONFIRMED)`.

That is a contract failure, so 0% is honest — but it also means **this suite mostly measures
whether the output format survives**, not whether the adversarial reasoning is good. The
`sound analysis` case is the one with real teeth: it checks the agent does not manufacture a
hole in order to look productive, which is the actual failure mode of an agent told to refute.
It passes, and that is the result worth keeping.

**I nearly misreported this run.** The baseline's 0/2 looked indistinguishable from the
provider crash described below, and a zero caused by a broken harness would have been reported
as a finding. What settled it was checking for empty outputs and `Command failed` separately
from assert failures: all six baseline cases produced real model output and failed on their
asserts. A 0% score and a 0% error rate look identical in the summary line — always separate
them before writing anything down.

## A provider bug this suite found, and the other two hid

The first attempt at the with-skill arm errored on every case:
`error: unknown option '---'`.

`evals/cross-examine/prompt.txt` begins with `{{agent}}`, so the rendered prompt starts with
the `---` of the agent file's YAML frontmatter. The provider passed the prompt as a positional
argument, and the CLI parsed a leading `-` as an option. `phq-9` and `detect-ai` were unaffected
only because their templates put prose ahead of the injected file — the bug is structural but
presents as suite-specific, which is the worst way for a bug to present.

Fixed by sending the prompt on **stdin** in `evals/_provider/claude.sh`, which also removes any
`ARG_MAX` ceiling on large prompts. Any future suite whose template leads with an injected file
would have hit the same wall.

## Limits

- **The asserts are weighted toward format.** Three deterministic JavaScript checks police the
  verdict line, the table and the vocabulary; two `llm-rubric` asserts cover the reasoning. A
  format-only regression would be caught instantly; a subtly worse *attack* might not be.
- Two cases, both single-turn, with raw material pasted in. The real agent has `Read, Grep,
  Glob, Bash` and is told execution beats opinion — the eval cannot exercise that at all, and
  the prompt says so explicitly, asking it to state what it *would* run.
- Tools are disabled in the provider, which is both necessary for a clean baseline and the
  reason the point above is unavoidable here.
- **Someone should rename this directory or add a suite for the actual skill.** A suite named
  after a skill that tests an agent is a bookkeeping trap — it is what left `cross-examine`
  looking like a scored skill in the first place.

## Reproducing

```bash
for n in 1 2 3; do
  npx promptfoo@latest eval -c evals/cross-examine/promptfooconfig.local.baseline.yaml \
    --no-cache -o results/baseline_$n.json
  npx promptfoo@latest eval -c evals/cross-examine/promptfooconfig.local.yaml \
    --no-cache -o results/skill_$n.json
done
```

The `.local.*` configs are generated from the canonical `promptfooconfig.yaml` (the CI arm) by
`evals/_provider/make-local-configs.py`; edit the canonical one and regenerate.
