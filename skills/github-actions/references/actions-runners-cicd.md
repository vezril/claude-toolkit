# Actions, runners, CI/CD & security hardening

Writing custom actions, choosing runners, building pipelines, and securing it all. (From *Automating Workflows with GitHub Actions*, Ch. 4–9.)

## Writing your own actions

Every action has an **`action.yml`** (metadata: `name`, `description`, `inputs`, `outputs`, `runs`). Three types:

**Composite** — bundle steps; no runtime overhead. Best for packaging a sequence of `run`/`uses` steps.
```yaml
# action.yml
name: Setup project
inputs:
  node-version: { default: '20' }
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with: { node-version: ${{ inputs.node-version }} }
    - run: npm ci
      shell: bash
```

**JavaScript** — runs on the runner via Node; fast, cross-platform. Use the toolkit (`@actions/core` for inputs/outputs/logging, `@actions/github` for the API/context).
```yaml
runs: { using: node20, main: dist/index.js }
```
Read inputs with `core.getInput('x')`, set outputs with `core.setOutput('y', val)`, fail with `core.setFailed(msg)`.

**Docker container** — runs in your image; any language/tooling; Linux runners only; slower (image pull/build).
```yaml
runs: { using: docker, image: Dockerfile, args: ['${{ inputs.path }}'] }
```

Consume actions: `uses: owner/repo@<sha>` (pin third-party to a full commit SHA), `uses: ./.github/actions/setup` (local), `uses: docker://alpine:3.20`.

## Marketplace

Discover reusable actions on the **GitHub Marketplace**; prefer **verified creators**, check stars/maintenance, and **read the source** — an action runs with your workflow's token. Publish your own by tagging a release and adding it to the Marketplace; document inputs/outputs and pin your own dependencies.

## Runners

- **GitHub-hosted** — ephemeral fresh VM per job (Ubuntu/Windows/macOS) with preinstalled toolchains; billed per minute; zero maintenance. The default choice.
- **Self-hosted** — register your own machines with **labels**/groups (`runs-on: [self-hosted, linux, gpu]`); for special hardware, large caches, private-network access, or cost at scale. Responsibilities: patch the OS and **auto-update the runner agent**, isolate jobs, and **never expose self-hosted runners to untrusted PRs on public repos** (forked code would execute on your machine). Prefer ephemeral runners.

## Secrets, variables & OIDC

- **Secrets** (repo / environment / org level) — encrypted, masked, read via `${{ secrets.NAME }}`. **Variables** (`vars.NAME`) for non-sensitive config.
- **`GITHUB_TOKEN`** — auto-created per run, scoped by `permissions:`; expires at run end. Default it to read-only.
- **OIDC** (recommended for cloud) — set `permissions: id-token: write`, then use the cloud provider's official login action to exchange a short-lived OIDC token for cloud credentials. **No long-lived cloud secrets stored in GitHub.**

## CI/CD pipeline recipes

**CI (every PR):**
```yaml
on: { pull_request: {} }
permissions: { contents: read }
jobs:
  verify:
    runs-on: ubuntu-latest
    strategy: { matrix: { version: [18, 20, 22] } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.version }}, cache: npm }
      - run: npm ci
      - run: npm run lint && npm run typecheck
      - run: npm test
```
Make these checks **required** in branch protection ([[git]]).

**CD (on tag → deploy with approval):**
```yaml
on: { push: { tags: ['v*.*.*'] } }
permissions: { contents: read, id-token: write }
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production        # protection rules: required reviewers, wait timer
    steps:
      - uses: actions/checkout@v4
      - uses: <cloud>/login@<sha>   # OIDC, no stored secret
      - run: ./deploy.sh
```

**DRY with reusable workflows:**
```yaml
# .github/workflows/ci.yml
on: { workflow_call: { inputs: { node: { type: string, default: '20' } } } }
# caller:
jobs:
  ci: { uses: ./.github/workflows/ci.yml, with: { node: '20' } }
```
Plus composite actions for repeated step sequences. Track flow with DORA metrics ([[devops]]).

## Migration (Ch. 7)

Migrating from Jenkins/Azure Pipelines/Travis/CircleCI: map stages→jobs, agents→runners, credentials→secrets/OIDC, plugins→Marketplace actions. Move incrementally (run both in parallel), and re-pin/audit any third-party actions you adopt.

## Debugging

Expand step logs; set the **`ACTIONS_STEP_DEBUG`** secret to `true` for verbose runner/step debug output; emit `::group::`/`::error::` workflow commands; write a Markdown report to `$GITHUB_STEP_SUMMARY`; re-run individual failed jobs; reproduce locally with `act` (with caveats); iterate via `workflow_dispatch`.

## Security hardening checklist (treat workflows as production code)

1. **Least-privilege `permissions:`** — default `contents: read`; grant writes per-job only as needed; avoid `write-all`.
2. **Pin third-party actions to a full commit SHA** (tags/branches are mutable → supply-chain risk); let Dependabot propose updates you review.
3. **Never interpolate untrusted input into shells** — PR titles, branch names, issue bodies (`${{ github.event.* }}`) can carry shell injection. Pass them through `env:` and reference quoted `"$VAR"`.
4. **`pull_request_target` / `workflow_run` caution** — these run with the **base repo's write token and secrets**; do not check out and execute untrusted fork code in that context.
5. **OIDC over stored cloud credentials**; rotate any secret that is ever exposed.
6. **Don't print secrets** to logs (masking is a backstop, not a guarantee).
7. **Self-hosted runners**: isolate/ephemeralize, keep updated, never on public repos for untrusted PRs.
8. **Protect workflow files and `main`**; require reviews for changes to `.github/workflows`.

(See [[secure-coding]] for the broader principles; [[git]] for branch protection that consumes these checks.)
