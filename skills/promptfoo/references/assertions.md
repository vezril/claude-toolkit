# promptfoo assertions — the full catalog

Source: promptfoo.dev/docs/configuration/expected-outputs (+ deterministic/, model-graded/, llm-rubric/, factuality/, similar/, g-eval/, javascript/, python/ subpages), fetched 2026-07. Assertions are the contract that makes an eval meaningful.

## The assert schema

Each entry in a test's `assert:` array:

```yaml
assert:
  - type: equals          # required — the assertion type
    value: 'expected'     # expected output / comparison target (string, list, or schema)
    threshold: 0.75       # numeric cutoff (similar, cost, latency, g-eval, custom scores)
    weight: 2.0           # relative importance in the test's weighted score (default 1.0)
    metric: accuracy      # named tag — aggregates this assert into a suite-level metric
    provider: openai:gpt-4o   # grader/embedding override (model-graded & similar)
    transform: 'output.trim()'   # preprocess output before asserting
    rubricPrompt: '...'   # custom grader prompt (model-graded only)
```

**Negation:** prepend `not-` to any type (`not-contains`, `not-regex`, `not-llm-rubric`). **Attachment:** put shared asserts on `defaultTest.assert` (applied to every test); grader config goes under `defaultTest.options`.

## Deterministic assertions (fast, free, no LLM — prefer these)

```yaml
- { type: equals, value: 'Expected exact output' }        # exact match
- { type: contains, value: 'substring' }                  # WORKHORSE
- { type: icontains, value: 'substring' }                 # case-insensitive — WORKHORSE
- { type: contains-any, value: ['a', 'b'] }               # any present
- { type: contains-all, value: ['x', 'y'] }               # all present
- { type: icontains-any, value: ['a', 'b'] }              # (+ icontains-all)
- { type: regex, value: '\d{4}' }                         # WORKHORSE
- { type: starts-with, value: 'Expected start' }
- { type: is-json }                                       # valid JSON — WORKHORSE
- type: is-json                                           # + optional JSON Schema
  value:
    type: object
    required: ['latitude', 'longitude']
    properties:
      latitude: { type: number, minimum: -90, maximum: 90 }
- { type: contains-json }                                 # contains a valid JSON blob
- { type: is-xml }            # (value.requiredElements: [root.child]); + contains-xml
- { type: is-sql, value: { databaseType: 'PostgreSQL' } }
- { type: is-valid-openai-function-call }                 # output matches a tool schema
- { type: javascript, value: "output.length > 10" }       # arbitrary JS — WORKHORSE
- { type: python, value: "len(output) > 10" }             # arbitrary Python — WORKHORSE
- { type: cost, threshold: 0.001 }                        # generation cost ≤ USD
- { type: latency, threshold: 5000 }                      # response time ≤ ms
- { type: perplexity, threshold: 1.5 }                    # perplexity ≤
- { type: rouge-n, value: 'expected text', threshold: 0.75 }   # ROUGE ≥
- { type: bleu, value: 'expected text', threshold: 0.7 }       # BLEU ≥
- { type: levenshtein, value: 'expected text', threshold: 5 }  # edit distance ≤
```

Direction: `cost`/`latency`/`perplexity`/`levenshtein` thresholds are **upper bounds**; `rouge-n`/`bleu`/`similar` thresholds are **lower bounds** (minimum score).

## Model-graded assertions (an LLM judges the output — cost tokens)

| type | judges |
|---|---|
| `llm-rubric` | freeform rubric — the main general grader |
| `model-graded-closedqa` | whether the answer meets stated requirements |
| `factuality` | factual consistency vs a reference statement |
| `answer-relevance` | output is on-topic for the query |
| `g-eval` | criteria via chain-of-thought steps (default threshold 0.7) |
| `similar` | embedding cosine similarity vs expected (threshold) |
| `context-relevance` / `context-faithfulness` / `context-recall` | RAG checks |
| `classifier` | HuggingFace classifier (tone/bias/toxicity) |
| `moderation` | OpenAI moderation policy compliance |
| `select-best` | compares multiple provider outputs, picks best on criteria |

**`llm-rubric`** — `value` is the rubric; the grader returns `{ reason, score (0–1), pass }`. Pass requires `pass===true` and, if set, `score>=threshold`. The rubric can reference `{{vars}}`:

```yaml
assert:
  - type: llm-rubric
    value: 'Provides a direct answer to "{{question}}" and is not apologetic'
    threshold: 0.8
```

**`factuality`** — grades output vs a reference into A–E; default passing = A/B/C/E, failing = D:

```yaml
- { type: factuality, value: 'Sacramento is the capital of California' }
# tune which categories pass:
defaultTest:
  options:
    factuality: { subset: 1, superset: 1, agree: 1, disagree: 0, differButFactual: 1 }
```

**`similar`** (embeddings; `similar:dot`, `similar:euclidean` variants); `value` may be a list (OR-match):

```yaml
- { type: similar, value: ['The expected output', file://expected.txt], threshold: 0.8 }
```

**`g-eval`** — `value` = a criterion or list of steps (scores averaged):

```yaml
- { type: g-eval, value: ['Maintains a professional tone', 'Uses technical terms correctly'], threshold: 0.8 }
```

## Custom assertions (the escape hatch)

**JavaScript** — inline expression, or `file://script.js[:namedExport]`; return `boolean` | `number` (vs threshold) | GradingResult; async ok:

```yaml
- { type: javascript, value: "output.includes('Hello, World!')" }
- { type: javascript, value: file://path/to/script.js:customFunction }
```
```javascript
module.exports = (output, context) => {
  // context = { prompt, vars, test, logProbs, config, provider, providerResponse, trace, metadata }
  return { pass: output.length > 5, score: 0.8, reason: 'long enough' };
};
```

**Python** — inline or `file://script.py[:custom_assert]`, signature `def get_assert(output, context)`:

```yaml
- { type: python, value: "output[5:10] == 'Hello'" }
- { type: python, value: file://validator.py:custom_assert }
```
```python
def get_assert(output, context):
    return {
        'pass': True, 'score': 0.6, 'reason': 'Looks good',
        'namedScores': {'quality': 0.8},   # feeds named metrics
    }
```
`context` (Python) = `prompt, vars, test, config, provider, providerResponse, logProbs, trace`.

## Grading config, thresholds, metrics

- **Override the grader** globally (`defaultTest.options.provider`) or per-assert (`provider:` with a `config` block, e.g. `temperature: 0` for stable grading). Embedding provider for `similar` via `defaultTest.options.provider.embedding` or per-assert.
- **Custom rubric prompt** — `defaultTest.options.rubricPrompt` (templated with `{{output}}` and `{{rubric}}`).
- **Test-level `threshold`** — each assert contributes `weight × score`; the test passes only if the weighted-average clears the test's `threshold`:
  ```yaml
  tests:
    - threshold: 0.5
      assert:
        - { type: equals, value: 'Hello world', weight: 2 }
        - { type: contains, value: 'world', weight: 1 }
      # "Goodbye world" → (0×2 + 1×1)/3 = 0.33 < 0.5 → fails
  ```
- **`assert-set`** — group asserts with their own sub-threshold (e.g. at least half the set must pass), for non-blocking clusters.
- **Named metrics** — `metric:` tags an assert so its score aggregates into a named suite-level metric (track `safety` vs `accuracy` vs `tone` separately in the UI/output). Custom JS/Python asserts emit several at once via `namedScores`.

*(Docs gaps: `model-graded-closedqa` shares the `type/value` shape of `llm-rubric` with no separate example page; `select-best` = `type: select-best`, `value:` = selection criteria, compares outputs across providers in one test.)*
