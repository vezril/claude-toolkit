# design-patterns — EDD iteration log

Numbers come from `results/`. Model `sonnet` via `evals/_provider/claude.sh`. **N=3 per case,
majority scoring.**

| Arm | Run 1 | Run 2 | Run 3 | **Majority** |
|---|---|---|---|---|
| naive baseline | 2/3 | 2/3 | 2/3 | **2/3 (67%)** |
| with `SKILL.md` | 3/3 | 2/3 | 2/3 | **3/3 (100%)** |

| Case | Baseline | With skill |
|---|---|---|
| Visitor over an AST → ADTs + exhaustive match, expression problem | PPP pass | PFP pass |
| Singleton requested by name → push back | PPP pass | PPP pass |
| Strategy requested by name → it is just a function | **FFF fail** | PPF pass |

## The first run was wrong, and the asserts were the reason

Run 1 scored the Strategy case **FFF in both arms**, which looks like a damning skill gap. It
was not. Reading the transcript, the with-skill answer builds the classic trait plus concrete
classes and then says the hierarchy *"reduce[s] to `type Pricing = Order => BigDecimal`"* —
which is precisely the behaviour the skill asks for. My asserts were broken in both directions
at once:

- One accepted a bare `=>`. That appears in any Scala lambda or `match`, so it could pass on an
  answer that never mentioned functions at all. It happened to match something meaningful here,
  which is the dangerous kind of false pass.
- The other demanded a **historical framing** — `1994`, `GoF`, `workaround` — that the skill
  nowhere requires. The skill says to check whether a function expresses the pattern more
  directly; it does not ask anyone to cite the Gang of Four.

So I was testing for a rationale I had invented and rejecting a correct answer for not reciting
it. Both asserts were rewritten to assert the skill's actual instruction (offer the
function-based alternative, in prose or as a function type), plus one `llm-rubric` for the
judgment the regex cannot reach: that the reader is not left thinking the class hierarchy is
the right answer.

**Both arms were then re-run from scratch**, because changing an assert invalidates comparison
with the old numbers. The table above is entirely post-fix. The result after the fix is a real
delta — the naive arm genuinely never offers the function form for Strategy, FFF across three
runs — which the broken assert had been hiding behind a false negative in the skill arm.

## What the baseline already knows

Visitor and Singleton are base-strong, PPP. Unprompted, the model reaches for a sealed trait
with exhaustive matching over an AST and names the expression-problem trade-off, and it pushes
back on a Singleton request as global mutable state. The skill's measured value is narrower
than its "modern/critical lens" section suggests: the lens is largely internalised already,
except for Strategy.

## Limits

- Three cases, all Scala-flavoured. Nothing tests Adapter/Facade/Composite — the patterns the
  skill says still *earn their keep* — so the suite only checks the dissolving half of the
  argument.
- The Visitor case flapped once in the skill arm (PFP), the Strategy case once (PPF).
- One assert is `llm-rubric`; the rest are deterministic.

## Reproducing

```bash
for n in 1 2 3; do
  npx promptfoo@latest eval -c evals/design-patterns/promptfooconfig.local.baseline.yaml --no-cache -o results/baseline_$n.json
  npx promptfoo@latest eval -c evals/design-patterns/promptfooconfig.local.yaml          --no-cache -o results/skill_$n.json
done
```
