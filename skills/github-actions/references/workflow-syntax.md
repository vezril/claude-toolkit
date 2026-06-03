# Workflow YAML syntax, contexts & expressions

The reference for writing `.github/workflows/*.yml`. (From *Automating Workflows with GitHub Actions*, Ch. 1–3.)

## Top-level keys

```yaml
name: CI                    # display name (optional)
run-name: ...               # dynamic run title (optional, supports expressions)
on: { ... }                 # triggers (required)
permissions: { ... }        # GITHUB_TOKEN scopes (set least-privilege)
env: { ... }                # workflow-wide env vars
concurrency: { ... }        # serialize/cancel runs
defaults: { run: { shell: bash, working-directory: ./app } }
jobs: { ... }               # one or more jobs (required)
```

## Triggers (`on:`)

```yaml
on:
  push:
    branches: [main, 'release/**']
    tags: ['v*.*.*']
    paths: ['src/**']           # or paths-ignore
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:            # manual run
    inputs:
      environment:
        type: choice
        options: [staging, prod]
  schedule:
    - cron: '0 6 * * 1'         # Mondays 06:00 UTC
  workflow_call: { ... }        # makes this a reusable workflow
```

Other events: `release`, `issues`, `issue_comment`, `workflow_run`, `repository_dispatch`, and the security-sensitive **`pull_request_target`** (runs in base-repo context with secrets — see security reference).

## Jobs & steps

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
    outputs:
      version: ${{ steps.ver.outputs.value }}
    steps:
      - uses: actions/checkout@v4
      - name: Compute version
        id: ver
        run: echo "value=$(cat VERSION)" >> "$GITHUB_OUTPUT"
      - name: Build
        run: make build
        env:
          NODE_ENV: production

  test:
    needs: build               # runs after build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test
```

- **`uses:` vs `run:`** — `uses:` invokes an action (`owner/repo@ref`, `./local`, `docker://image`); `run:` executes shell. Provide action inputs with `with:`.
- **`needs:`** orders jobs and exposes `needs.<job>.outputs.*`.
- **`if:`** conditionals: `if: github.event_name == 'push'`, `if: success()`, `if: failure()`, `if: always()`, `if: github.ref == 'refs/heads/main'`. (Don't wrap the whole thing in `${{ }}` — it's implied in `if`.)

## Matrix builds

```yaml
strategy:
  fail-fast: false
  max-parallel: 4
  matrix:
    os: [ubuntu-latest, macos-latest]
    version: [18, 20, 22]
    include:
      - { os: ubuntu-latest, version: 20, coverage: true }
    exclude:
      - { os: macos-latest, version: 18 }
runs-on: ${{ matrix.os }}
```

## Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true     # cancel superseded runs (saves minutes)
```

## Permissions (least-privilege GITHUB_TOKEN)

```yaml
permissions:
  contents: read               # default to read-only
  pull-requests: write         # grant only what a job needs
  id-token: write              # required for OIDC cloud auth
```

## Contexts (read inside `${{ }}`)

- **`github`** — `event_name`, `ref`, `ref_name`, `sha`, `actor`, `repository`, `run_id`, `event.*` (the raw webhook payload).
- **`env`**, **`vars`** (repo/org configuration variables), **`secrets`**, **`matrix`**, **`needs`**, **`steps`**, **`job`**, **`runner`** (`runner.os`, `runner.temp`), **`inputs`** (dispatch/reusable).

## Expression functions

`contains(a,b)`, `startsWith`/`endsWith`, `format('{0}-{1}', x, y)`, `join(list, ',')`, `toJSON(x)`/`fromJSON(s)` (build matrices/objects dynamically), `hashFiles('**/package-lock.json')` (cache keys), and status checks `success()`, `failure()`, `always()`, `cancelled()`.

## Passing data: outputs, env, summaries

```yaml
- run: echo "key=value" >> "$GITHUB_OUTPUT"     # step output -> steps.<id>.outputs.key
- run: echo "MY_VAR=value" >> "$GITHUB_ENV"     # env for later steps
- run: echo "PATH_ADD" >> "$GITHUB_PATH"        # prepend to PATH
- run: echo "## Results" >> "$GITHUB_STEP_SUMMARY"   # Markdown job summary
```
Workflow commands in logs: `::group::`/`::endgroup::`, `::error file=...,line=...::msg`, `::warning::`, `::add-mask::` (mask a value).

## Artifacts & caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: npm-
- uses: actions/upload-artifact@v4
  with: { name: dist, path: dist/, retention-days: 7 }
# in a later/other job:
- uses: actions/download-artifact@v4
  with: { name: dist }
```
