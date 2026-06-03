---
name: github-actions
description: Automating software workflows with GitHub Actions, distilled from Heller's *Automating Workflows with GitHub Actions*. Covers the workflow model (events/triggers, jobs, steps, runners), YAML workflow syntax (on, jobs, runs-on, steps, uses vs run, with/env, needs, if, matrix strategy, concurrency, permissions), contexts & expressions (github/env/secrets/matrix, functions), using and writing actions (composite, JavaScript, Docker container actions; action.yml; inputs/outputs), the Marketplace (finding & publishing), runners (GitHub-hosted vs self-hosted, labels, security), secrets & variables & OIDC, artifacts & caching, CI/CD pipelines (build/test/lint/deploy, environments & approvals), reusable workflows & composite actions for DRY, debugging/logs, and security hardening (least-privilege GITHUB_TOKEN, pinning actions to SHAs, untrusted input/script-injection, pull_request_target risks). Use whenever creating, reviewing, or debugging GitHub Actions workflows or custom actions — setting up CI/CD, matrix builds, releases on tags, caching, secrets/OIDC, self-hosted runners, reusable workflows, or hardening workflow security. Comprehensive; pairs with git, devops, secure-coding, and tdd.
---

# GitHub Actions

How to automate build/test/release/deploy with **GitHub Actions** — the workflow model, the YAML syntax, writing and consuming actions, CI/CD patterns, and (critically) **security hardening**. Distilled from **Automating Workflows with GitHub Actions** (Priscila Heller).

Cross-links: [[git]] (Actions are triggered by Git events — pushes, PRs, tags), [[devops]] (CI/CD, the Three Ways, DORA metrics), [[secure-coding]] (workflow security: secrets, token scope, script injection), [[tdd]] (run the test suite as the core CI job).

## The model

A **workflow** is a YAML file in `.github/workflows/` that runs one or more **jobs** in response to **events**. Each job runs on a **runner** (a VM/container) and contains ordered **steps**; a step either **runs a shell command** (`run:`) or **uses an action** (`uses:`). Jobs run in parallel by default; order them with `needs:`.

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm test
```

## Events / triggers (`on:`)

- Common: `push`, `pull_request` (and the riskier `pull_request_target`), `workflow_dispatch` (manual, with `inputs`), `schedule` (cron), `release`, `workflow_call` (reusable), `workflow_run`, `issues`/`issue_comment`, `repository_dispatch`.
- Filter by `branches`/`branches-ignore`, `tags`, `paths`/`paths-ignore`. Tag pushes (`on: push: tags: ['v*']`) are the idiomatic **release** trigger ([[git]] SemVer tags).

## Workflow syntax essentials

- **`jobs.<id>.runs-on`** — runner label (`ubuntu-latest`, `windows-latest`, `macos-latest`, or self-hosted labels).
- **`steps`** — `uses:` (an action, pinned by tag/branch/**SHA**) vs `run:` (shell; set `shell:` and multi-line with `|`). Pass inputs via **`with:`**, environment via **`env:`** (job/step/workflow scope).
- **`needs:`** — declare job dependencies (build → test → deploy). **`outputs`** pass data between jobs.
- **`if:`** — conditional execution using expressions (e.g. `if: github.ref == 'refs/heads/main'`, `if: failure()`/`always()`/`success()`).
- **`strategy.matrix`** — fan a job across combinations (OS × language version); `fail-fast`, `max-parallel`, `include`/`exclude`.
- **`concurrency`** — cancel/queue superseded runs (`group:` + `cancel-in-progress`) to save minutes.
- **`permissions`** — scope the automatic `GITHUB_TOKEN` (set least-privilege, e.g. `contents: read`).
- **`environment`** — named deploy targets with **protection rules** (required reviewers, wait timers, environment secrets).
- **`timeout-minutes`**, **`continue-on-error`**, **`defaults.run`** (default shell/working-dir).

## Contexts & expressions

Inside `${{ }}` you read **contexts**: `github` (event, ref, sha, actor, repository), `env`, `vars` (repo/org variables), `secrets`, `matrix`, `needs`, `job`, `runner`, `steps`. Built-in **functions**: `contains`, `startsWith`/`endsWith`, `format`, `join`, `toJSON`/`fromJSON`, `hashFiles` (cache keys), and status checks `success()`/`failure()`/`always()`/`cancelled()`. Set step outputs via `echo "key=val" >> "$GITHUB_OUTPUT"` and env via `>> "$GITHUB_ENV"`.

## Using & writing actions

Three kinds of custom action (defined by an **`action.yml`** with `inputs`/`outputs`/`runs`):
- **Composite** — bundle multiple steps/shell into one reusable action (simplest; no extra runtime).
- **JavaScript** — runs directly on the runner via Node (`runs: { using: node20, main: index.js }`); use `@actions/core`, `@actions/github` toolkit.
- **Docker container** — runs in a container you specify; any language, slower startup, Linux runners only.

Consume actions with `uses: owner/repo@ref`. **Pin to a full commit SHA** for third-party actions (tags/branches are mutable — supply-chain risk). Reference local actions with `./path` and same-repo reusable workflows with `./.github/workflows/x.yml`.

## Marketplace

Find vetted actions on the **GitHub Marketplace**; prefer **verified creators** and review the source. Publish your own by adding `action.yml` + a release tag and (optionally) listing it. Treat every third-party action as code you're running with your repo's token — audit and pin it.

## Runners

- **GitHub-hosted** — fresh ephemeral VM per job (Ubuntu/Windows/macOS), preinstalled tooling, billed by minute. Zero maintenance; ideal default.
- **Self-hosted** — your own machines (labels, groups), for special hardware, private network access, or cost at scale. **Security caveat**: never use self-hosted runners on **public** repos for untrusted PRs — forked code can run on your infrastructure. Keep them ephemeral/isolated, auto-update the runner, scope access.

## Secrets, variables & OIDC

- **Secrets** (repo/environment/org) are encrypted, masked in logs, exposed via `secrets.NAME`. **Variables** (`vars.NAME`) for non-sensitive config.
- **`GITHUB_TOKEN`** is auto-provisioned per run; scope it with `permissions:` (default to read-only, grant write only where needed).
- Prefer **OIDC** for cloud deploys: the workflow requests a short-lived token from the cloud provider (`permissions: id-token: write`) instead of storing long-lived cloud credentials — fewer standing secrets ([[secure-coding]]).

## Artifacts & caching

- **`actions/upload-artifact`/`download-artifact`** — persist build outputs / test reports across jobs and for download (set `retention-days`).
- **`actions/cache`** (or built-in setup-action caching) — cache dependencies keyed by `hashFiles('**/lockfile')` with `restore-keys` fallbacks to speed builds.

## CI/CD patterns

- **CI**: on `push`/`pull_request` → checkout → setup language → install → **lint + type-check + test** ([[tdd]]) → upload coverage; matrix across versions/OS; require these checks to merge ([[git]] branch protection).
- **CD**: on merge to `main` or on a **tag** → build artifact/image → deploy to an **environment** (with approval gates for prod). Use OIDC for cloud auth. Separate build from deploy via `needs:` and artifacts.
- **DRY**: extract shared logic into **reusable workflows** (`on: workflow_call`, called with `uses: ./.github/workflows/ci.yml`) and **composite actions**. Track DORA metrics ([[devops]]).

## Debugging

Read job **logs** (expand steps); enable **step debug logging** (`ACTIONS_STEP_DEBUG=true` secret); add `echo`/`::group::`/`::error::` workflow commands; re-run jobs (with debug); test locally with tools like `act` (caveats apply); validate YAML and use `workflow_dispatch` to iterate.

## Security hardening (treat workflows as production code)

- **Least-privilege `GITHUB_TOKEN`** — set `permissions:` to the minimum; default read-only.
- **Pin third-party actions to a full SHA**, not a moving tag; review and update deliberately (Dependabot can bump them).
- **Beware `pull_request_target`** and `workflow_run` — they run with **write token + secrets** in the context of the **base** repo while potentially handling **untrusted fork** code. Never check out and execute untrusted PR code with secrets available.
- **Script injection**: never interpolate untrusted input (`${{ github.event.issue.title }}`, PR titles/branch names) directly into `run:` shells — pass via `env:` and reference `"$VAR"` quoted, so an attacker can't inject shell.
- Don't `echo` secrets; rely on masking but don't depend on it. Restrict who can change workflows; protect `main`. Scope/secure **self-hosted runners** (above).

## Anti-patterns (flag in review)

- Unpinned third-party actions (`@main`/floating tags); overbroad `permissions: write-all`; long-lived cloud secrets where OIDC fits.
- Interpolating untrusted event data into shell (`run:`); using `pull_request_target` to run fork code with secrets.
- No dependency caching (slow, costly builds); no `concurrency` (wasted minutes on superseded runs); monolithic copy-pasted workflows instead of reusable workflows/composite actions.
- Self-hosted runners exposed to untrusted PRs; no environment protection on prod deploys; secrets printed to logs.

## How to use this skill

- **`references/workflow-syntax.md`** — the full `on`/`jobs`/`steps` syntax, contexts & expressions, matrix, concurrency, permissions, artifacts/caching, with examples.
- **`references/actions-runners-cicd.md`** — writing the three action types (composite/JS/Docker), the Marketplace, runners (hosted vs self-hosted), secrets/OIDC, reusable workflows, CI/CD pipeline recipes, migration, and the security-hardening checklist.

## Always-apply defaults

1. **Least-privilege `permissions:`** + **pin actions to SHAs**; never feed untrusted input into shells.
2. **CI on PRs gating merge** (lint + types + tests, [[tdd]]); cache deps; use a **matrix** for version/OS coverage.
3. **CD via environments with approvals**; prefer **OIDC** over stored cloud secrets ([[secure-coding]]).
4. **DRY with reusable workflows / composite actions**; add `concurrency` to cancel superseded runs.
5. **Tag-triggered releases** ([[git]] SemVer); upload artifacts; keep workflows reviewed and `main` protected.

## Related

- [[git]] — the events (push/PR/tag) and SemVer tags that trigger workflows; branch protection consumes the checks.
- [[devops]] — CI/CD, flow, and DORA metrics that Actions implements.
- [[secure-coding]] — token scope, secret/OIDC handling, script-injection and supply-chain defenses.
- [[tdd]] — the test suite as the heart of the CI job.
- Source: *Automating Workflows with GitHub Actions* (Priscila Heller, Packt 2021).
