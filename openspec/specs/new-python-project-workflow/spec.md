# new-python-project-workflow Specification

## Purpose
TBD - created by archiving change new-python-project. Update Purpose after archive.
## Requirements
### Requirement: Args contract

The workflow SHALL require `name`, `visibility` (`public`|`private`), and `dockerhub` (boolean) with no defaults, accept optional `auto` (default false) and `pkg` (default: scala-consistent derivation), tolerate stringified args (parse-then-validate), and fail fast naming the missing human decision.

#### Scenario: dockerhub not answered

- **WHEN** invoked without `dockerhub`
- **THEN** it throws before any side effect, telling the outer conversation to ask the human

### Requirement: Phase order and reuse

The workflow SHALL run: (1) `new-github-project` bare mode via nested `workflow()` (bringing branch protection with its plan-403 degrade, and `openspec init`); (2) sequentially on `feat/scaffold`: python-uv-build → python-package → python-tests → repo-starter-docs → README enrichment → github-actions-python-ci; (3) `dockerhub-setup` iff `dockerhub:true`; (4) the uv green gate; (5) `git-ship`.

#### Scenario: Bare bootstrap reused

- **WHEN** phase 1 completes
- **THEN** the repo exists with seeded `main`, protection applied or degraded-with-warning, and the OpenSpec config present uncommitted

### Requirement: uv green gate before anything ships

The workflow SHALL run `uv sync` (generating `uv.lock`), `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest` after scaffolding, and SHALL NOT push, open a PR, or return `awaiting-merge-approval` unless all pass. On red it SHALL return `status: failed` with the failing output and `repoCreated: true`. The generated `uv.lock` SHALL ship with the PR.

#### Scenario: Red gate

- **WHEN** any gate command fails
- **THEN** nothing is pushed and the result names the failing command and the leftover empty repo

### Requirement: Single gated merge with development post-merge

Non-auto mode SHALL end with exactly one `awaiting-merge-approval` (the scaffold PR) whose `nextStep` covers merge → sync `main` → create and push `development`. Auto mode SHALL do all of that and return `complete`.

#### Scenario: Gated run

- **WHEN** run without `auto` and the gate is green
- **THEN** the result carries the PR URL, `pendingApproval: true`, and the development-branch instruction

