# promptfoo in CI/CD — GitHub Actions, gating, cost

Source: promptfoo.dev/docs/integrations/ci-cd + github-action, usage/command-line, and github.com/promptfoo/promptfoo(-action), fetched 2026-07. Current action: **`promptfoo/promptfoo-action@v1`**. Node `^20.20.0` or `>=22.22.0`.

## The CI contract

`promptfoo eval` sets its process exit code from the results, so it gates a job like any test runner:
- **`0`** — all tests pass.
- **`100`** — ≥1 test failed, or the pass rate is below `PROMPTFOO_PASS_RATE_THRESHOLD`.
- **`1`** — other error.

Env overrides: `PROMPTFOO_PASS_RATE_THRESHOLD` (suite-level pass %, default 100) and `PROMPTFOO_FAILED_TEST_EXIT_CODE` (change the `100`). The gate is the assertions + thresholds you write — no extra glue.

## Path A — the official GitHub Action

Headline feature: on a PR it evals and **posts results as a PR comment** (pass/fail counts + a viewer link for before/after comparison).

```yaml
name: Prompt Evaluation
on:
  pull_request:
    paths:
      - 'skills/**'          # run when a skill (or its eval) changes
      - 'evals/**'
jobs:
  evaluate:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write   # required to post the comment
    steps:
      - uses: actions/checkout@v4
      - name: Cache promptfoo
        uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: ${{ runner.os }}-promptfoo-v1
          restore-keys: ${{ runner.os }}-promptfoo-
      - name: Run promptfoo evaluation
        uses: promptfoo/promptfoo-action@v1
        with:
          config: 'evals/phq-9.promptfooconfig.yaml'
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          cache-path: ~/.cache/promptfoo
          fail-on-threshold: 95        # gate: suite must pass ≥95%
```

**Action inputs** (from `action.yml`): `config` (req), `github-token` (req), `prompts` (newline globs of changed files), `working-directory`, `cache-path`, `promptfoo-version` (default `latest`), `no-share`, `use-config-prompts`, `env-files`, `fail-on-threshold` (suite pass % gate), `max-concurrency` (default 4), `no-table`/`no-progress-bar`/`no-cache`, `disable-comment`, `workflow-files`/`workflow-base` (for `workflow_dispatch`), `repeat` (≥2) + `repeat-min-pass` (flake control), `force-run`, `debug`.

**API-key inputs** (each → a secret): `openai-api-key`, `anthropic-api-key`, `azure-api-key`, `huggingface-api-key`, `aws-access-key-id`, `aws-secret-access-key`, `replicate-api-key`, `palm-api-key`, `vertex-api-key`, `cohere-api-key`, `mistral-api-key`, `groq-api-key`. Keys come only from `secrets.*` — never inlined.

## Path B — plain CLI (full control, JUnit, artifacts, non-PR triggers)

```yaml
name: promptfoo-eval
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - name: Cache promptfoo results
        uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: ${{ runner.os }}-promptfoo-${{ hashFiles('skills/**', 'evals/**') }}
          restore-keys: ${{ runner.os }}-promptfoo-
      - name: Run eval
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          PROMPTFOO_CACHE_PATH: ~/.cache/promptfoo
        run: |
          npx promptfoo@latest eval \
            -c evals/phq-9.promptfooconfig.yaml \
            -o results.json -o results.junit.xml \
            --tag git.sha="$GITHUB_SHA" --tag ci.run-id="$GITHUB_RUN_ID"
      - name: Upload results
        if: always()                # save artifacts even when the eval step fails the job
        uses: actions/upload-artifact@v4
        with:
          name: promptfoo-results
          path: |
            results.json
            results.junit.xml
```

- `-o`/`--output` accepts multiple paths; format inferred from extension (`csv, txt, json, jsonl, yaml, html, xml, **junit.xml**`). `junit.xml` is the CI-native one.
- `if: always()` keeps artifacts when the eval exits `100`.
- Custom bash gate (alternative to `fail-on-threshold`): parse `results.json` with `jq` for `.results.stats.successes/failures`, compute pass rate, `exit 1` below your bar — or just set `PROMPTFOO_PASS_RATE_THRESHOLD` and let exit `100` fail the job.

## Gating layers (innermost first)

1. **Per-assertion** pass/fail; some carry their own `threshold` (`similar`, `cost`, `latency`).
2. **Per-test `threshold`** — weighted-average of the test's assert scores must clear it (`weight` per assert, default 1.0).
3. **`assert-set`** — a cluster with its own sub-threshold (require only a subset).
4. **Suite level** — any failing test → exit `100` → job fails. Loosen with `PROMPTFOO_PASS_RATE_THRESHOLD` or the action's `fail-on-threshold`.

**Blocking vs non-blocking:** `weight: 0` for a report-only check; a low per-test `threshold` for best-effort tests; `assert-set` thresholds to require a subset; or split soft evals into a separate job with `continue-on-error: true`.

## Cost & determinism

- **Deterministic asserts are free; model-graded asserts cost tokens.** Express checks programmatically where you can.
- **Cache** provider responses (`PROMPTFOO_CACHE_PATH` + `actions/cache` on `~/.cache/promptfoo`) so unchanged prompt/provider/test combos don't re-hit the API. `--no-cache` (action: `no-cache: true`) only when you want fresh sampling.
- **Concurrency** `-j/--max-concurrency` (action default 4) — raise for speed, lower for rate limits.
- **Reduce model-graded flakiness:** prefer deterministic asserts; use `threshold`/`weight` so a borderline grade doesn't flip the suite; `repeat` + `repeat-min-pass` to require N-of-M; **pin the grader model** in `defaultTest.options.provider` (with `temperature: 0`) so grading is stable across runs.

## Sharing / comparison

- `promptfoo share` (or `--share` on `eval`) uploads a snapshot and returns a **private** web-viewer URL (auth via `promptfoo auth login -k KEY` or `PROMPTFOO_API_KEY` in CI). Self-host with `PROMPTFOO_REMOTE_API_BASE_URL` / `PROMPTFOO_REMOTE_APP_BASE_URL`.
- The action's PR comment links to the viewer for **baseline-vs-PR** comparison — its main regression-catching UX. There's no built-in time-series dashboard; cross-run comparison is via the viewer and by tagging runs (`--tag git.sha=…`).
