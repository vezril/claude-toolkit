# Skill evals

Behavioral regression tests for the skills in this repo, using [promptfoo](https://promptfoo.dev)
(see the **promptfoo** skill for the framework itself, and `docs/skill-and-agent-evaluation.md`
for the wider playbook).

A skill is a `SKILL.md` that shapes model behavior when it's loaded into context. These evals
make that behavior **testable**: load the skill as context, send a query, and assert on what
comes back. An edit that silently drops a rail fails the build.

## Layout — one directory per skill

```
evals/<skill>/
  promptfooconfig.yaml   # the test matrix for this skill
  prompt.txt             # wraps the SKILL.md as context + the {{request}} turn
  cases/*.txt            # (optional) longer inputs referenced via file://cases/…
  asserts/*.js           # (optional) custom JavaScript assertions
```

Every config points `defaultTest.vars.skill` at `file://../../skills/<skill>/SKILL.md` and runs
the shared `prompt.txt`, which injects the skill and the test's `{{request}}`.

Suites currently in the repo: **akka**, **calvin-voice**, **cross-examine**, **detect-ai**,
**humanize**, **outreach**, **phq-9**, **pr-description**.

## Run one

The provider under test is the **Claude Agent SDK** (`anthropic:claude-agent-sdk`) — the model
that actually reads the skill in real use. Locally it uses your existing Claude auth
(`apiKeyRequired: false`), so no extra key is needed:

```bash
npx promptfoo@latest eval -c evals/akka/promptfooconfig.yaml
npx promptfoo@latest view                                    # browse the matrix
```

`eval` exits **`100`** if any test fails (not `1`), which is what gates CI. Caching is on by
default, so a re-run that changes nothing is free.

**Two models, two jobs:** the *model under test* (`providers:`) is whatever will really read the
skill; the *grader* (`defaultTest.options.provider`) is pinned separately so swapping the model
under test doesn't silently change the judge too.

## Testing a nondeterministic system without pretending it's deterministic

The model's *prose* is nondeterministic. The **properties** you care about mostly aren't. So:

- **Assert properties, not text.** This is property-based testing, not example-based.
  `icontains: "akka-cluster"` holds across every rephrasing; `equals: "<exact paragraph>"` holds
  across none. If a test breaks when the model rewords, the test is wrong.
- **The skill is the variable, not the model.** Hold the model fixed, edit `SKILL.md`, see whether
  the rail survived. It's a *differential* test — nondeterminism is noise in the measurement, not
  the thing being measured.
- **Where the property really is fuzzy, gate on a statistic.** Tone, restraint, deferral: use
  `llm-rubric` + a `threshold`, and in CI require the behavior in N-of-M samples (`repeat` +
  `repeat-min-pass`) so one unlucky grade doesn't flip the suite.

## The three tiers (cheapest first)

| Tier | Assert with | Cost | Use for |
|---|---|---|---|
| **Routing / classification** | `icontains`, `contains-any`, `regex` | free | "which module/tool does it reach for" — has a right answer |
| **Hard facts** | `contains`, `regex` | free | claims that must not rot (BSL licensing, Typed-over-Classic, Jackson) |
| **Judgment** | `llm-rubric` + `threshold` | tokens | restraint, refusals, tone, "does it defer instead of bluffing" |

Push as much as possible into the free tiers. The judge is the exception, not the rule.
Tag every assert with `metric:` (`routing`, `accuracy`, `restraint`, `safety`, `tone`, …) so a
failure tells you *which dimension* regressed.

## Adding an eval for a skill

1. `mkdir evals/<skill>` and copy an existing `prompt.txt` into it (they're identical).
2. Write `evals/<skill>/promptfooconfig.yaml`: point `defaultTest.vars.skill` at
   `file://../../skills/<skill>/SKILL.md`, keep the `anthropic:claude-agent-sdk` provider block.
3. Write tests for that skill's **contract** — the rails you'd be upset to lose:
   - a *safety* skill → the rail must always appear (e.g. crisis resources regardless of score)
   - a *routing* skill → the right module comes back
   - a *factual* skill → the specific claims survive
4. Nothing to wire in CI — [`.github/workflows/skill-evals.yml`](../.github/workflows/skill-evals.yml)
   auto-discovers every `evals/*/promptfooconfig.yaml`.

## CI

`.github/workflows/skill-evals.yml` runs on PRs that touch `skills/**` or `evals/**`, and on
manual `workflow_dispatch`. It discovers every suite and runs each on the official
`promptfoo/promptfoo-action`, which posts results as a PR comment and gates on the pass rate.
Model-graded asserts are sampled with `repeat` + `repeat-min-pass` (require the behavior in N-of-M
runs) so a flaky judge doesn't redden the suite. The job needs an `ANTHROPIC_API_KEY` repo secret;
forked PRs can't read secrets, so it's skipped there rather than failing red.

## Honest limits

- Loading `SKILL.md` as context is a faithful **proxy** for how Claude Code injects skills, not a
  replica of the harness. It tests the skill's content as an instruction set — which is the thing
  worth guarding — but it is not end-to-end.
- These evals test **behavior once the skill is loaded**. They do *not* test whether the skill
  *triggers* in the first place (that's a property of the `description:` field, a separate eval
  worth building).
- A green suite means "the rails I thought to test survived." It does not mean the skill is good.
  Evals catch **regressions**, not the absence of quality.
- Model-graded asserts cost tokens and drift across model versions. Model IDs in the configs are
  current as of authoring — update them deliberately, and expect grades to shift when you do.
