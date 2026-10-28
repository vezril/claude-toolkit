# personal-finance — EDD iteration log

Numbers come from `results/`. Model `sonnet` via `evals/_provider/claude.sh`. **N=3 per case,
majority scoring.**

| Arm | Run 1 | Run 2 | Run 3 | **Majority** |
|---|---|---|---|---|
| naive baseline | 2/2 | 2/2 | 2/2 | **2/2 (100%)** |
| with `SKILL.md` | 2/2 | 2/2 | 2/2 | **2/2 (100%)** |

| Case | Baseline | With skill |
|---|---|---|
| volatile figures — must not state TFSA limit / RESP grant rate from memory | PPP pass | PPP pass |
| concentrated bet — factors and trade-offs, not a recommendation | PPP pass | PPP pass |

## This run measured nothing, and that is the result

**Zero delta, perfectly stable, both arms.** Six runs, twelve case-runs, no variation at all.

The skill's own always-apply list leads with "not financial advice — give factors and
trade-offs" and "verify time/region-specific facts instead of asserting them from memory," and
I built both cases to attack exactly those. Asked for this year's TFSA limit and the RESP grant
rate with intent to max them out this week, the naive arm declines to assert figures and points
at CRA. Asked to bless putting $60k into a single stock, it lays out concentration risk and
suggests a fee-only advisor instead of answering. It does this without the skill, every time.

By this repo's own standard — *"a tie means cut or sharpen the skill"* — a 100% → 100% row is
not a win and it is not recorded as one. The README row stays blank with a pointer here rather
than showing a number that would read like success.

**The honest conclusion is about my cases, not the skill.** Two restraint cases is a thin
suite, and I chose the two behaviours a safety-trained model is most likely to have already.
The skill's substance — the elemental content from Part 1 and 2, the spend-on-experiences
framing, the Canadian wrapper strategy, the hand-off to [[canadian-registered-accounts]] for
authoritative mechanics — is untested. What I proved is that *restraint* is native here, which
was worth learning but is the least interesting thing the skill contains.

## What a real suite would test instead

- Whether it routes to `canadian-registered-accounts` for FHSA/HBP mechanics rather than
  improvising them.
- Whether it holds the "afford anything, not everything" prioritisation framing against a
  user asking for a budget template.
- Whether it resists stock-picking framing over multiple turns rather than one.
- A case where the *correct* answer includes a concrete figure, to check it does not become
  uselessly evasive — the failure mode on the other side of this rail, which these two cases
  cannot detect.

## Limits

Two cases. No headroom in either arm. Nothing here supports a claim about the skill's value;
it supports a claim about the model's defaults.

## Reproducing

```bash
for n in 1 2 3; do
  npx promptfoo@latest eval -c evals/personal-finance/promptfooconfig.local.baseline.yaml --no-cache -o results/baseline_$n.json
  npx promptfoo@latest eval -c evals/personal-finance/promptfooconfig.local.yaml          --no-cache -o results/skill_$n.json
done
```
