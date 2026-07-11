# new-scala-pekko-service-workflow

## ADDED Requirements

### Requirement: Args contract

The workflow SHALL require `name`, `visibility` (`public`|`private`), and `dockerhub` (boolean) — all explicit, no defaults — and accept optional `auto` (default false) and `pkgRoot` (default `me.cference`). A missing required arg SHALL fail fast with a message telling the outer conversation to ask the human (Docker Hub needed? public or private?).

#### Scenario: dockerhub not answered

- **WHEN** invoked without `dockerhub`
- **THEN** the workflow throws before any side effect, naming the missing decision

### Requirement: Phase order and composition

The workflow SHALL run: (1) `new-github-project` in bare mode via nested `workflow()`; (2) sequentially on branch `feat/scaffold`: scala-sbt-build → scala-pekko-server → scala-pekko-tests → repo-starter-docs → github-actions-scala-ci; (3) dockerhub-setup iff `dockerhub:true`; (4) the green gate; (5) git-ship.

#### Scenario: Bare bootstrap

- **WHEN** phase 1 completes
- **THEN** the GitHub repo exists with protected, seeded `main` and no docs PR was created

### Requirement: Green gate before anything ships

The workflow SHALL run `sbt -batch scalafmtAll compile test` after scaffolding and SHALL NOT push code, open a PR, or return `awaiting-merge-approval` unless it exits 0. On red it SHALL return `status: failed` with the failure output and `repoCreated: true` so the human knows an empty remote shell exists.

#### Scenario: Red scaffold

- **WHEN** the sbt gate fails
- **THEN** no branch is pushed and the result names the failing step and the leftover empty repo

### Requirement: Single gated merge

In non-auto mode the workflow SHALL end with `awaiting-merge-approval` exactly once — the scaffold PR — with a `nextStep` covering: merge on human yes, sync `main`, then create and push `development` from merged `main`. In auto mode it SHALL do all of that itself and return `complete`.

#### Scenario: Gated run

- **WHEN** run with `auto` absent and a green gate
- **THEN** the result carries the PR URL, `pendingApproval: true`, and the development-branch instruction

#### Scenario: Auto run

- **WHEN** run with `auto:true` and a green gate
- **THEN** the PR is merged, `development` exists on the remote at merged `main`, and status is `complete`
