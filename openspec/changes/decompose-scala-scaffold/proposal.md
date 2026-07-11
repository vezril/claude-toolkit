# Proposal: decompose-scala-scaffold

## Why

`new-scala-service` is a 978-line monolithic personal skill (`~/.claude/skills/`) that duplicates what the toolkit's new bootstrap primitives already own (repo creation, docs, shipping), pushes unreviewed scaffolds directly to `main`, applies no branch protection, and hardcodes personal conventions. Now that `new-github-project` exists as the bootstrap primitive, the scala flavor should be decomposed into hyper-specific, individually reusable parts composed by a workflow — with the whole scaffold landing as one gated PR only after `sbt compile test` is green.

## What Changes

- `new-github-project` workflow gains `docs` and `ship` flags (both default `true`); both `false` = **bare mode** (repo + protection only, returns synchronously). **BREAKING** for nobody — defaults preserve current behavior.
- The monolithic scaffold splits into four scaffold skills, each owning one concern and its own deterministic scaffold script: `scala-sbt-build`, `scala-pekko-server`, `scala-pekko-tests`, `github-actions-scala-ci`.
- New `dockerhub-setup` skill: create the Docker Hub repo, mint the access token for CI, and set `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` as GitHub Actions secrets.
- New `new-scala-pekko-service` workflow orchestrating: bare bootstrap → scaffold (four skills + reused `repo-starter-docs`) → optional dockerhub-setup → `sbt` green gate → git-ship (gated PR, `awaiting-merge-approval`). Keeps the `development` branch convention (created from `main` after the scaffold PR merges).
- Package root becomes a parameter (default `me.cference`); LICENSE standardizes on `LICENSE.md` via the reused `repo-starter-docs` (the scaffold stops writing README/LICENSE).
- The old `new-scala-service` skill is retired into `archive/` via the `toolkit-archive` skill (depends on change `add-archive-skill`).

## Capabilities

### New Capabilities
- `scala-sbt-build`: the sbt build definition — two-module build.sbt with library dependencies, project/, plugins (dynver, native-packager), scalafmt/scalafix, .gitignore.
- `scala-pekko-server`: production sources only — Main, HttpServer, hello + health routes, AppConfig, application.conf, logback.
- `scala-pekko-tests`: test sources only — core spec + route specs; red/green territory split mirrors the dev pair.
- `github-actions-scala-ci`: the ci/dev/release GitHub Actions workflows + setup-scala composite action.
- `dockerhub-setup`: Docker Hub repo + CI token + GitHub secrets, end to end.
- `new-scala-pekko-service-workflow`: the orchestration — phases, gates, args contract.
- `new-github-project-bare-mode`: the `docs`/`ship` flags on the existing bootstrap workflow.

### Modified Capabilities
<!-- none — openspec/specs/ is empty; new-github-project's flags are specced above as a new capability -->

## Impact

- `workflows/new-github-project.js` (flags) + installed copy in `~/.claude/workflows/`.
- New `workflows/new-scala-pekko-service.js`; five new skill folders under `skills/`.
- `README.md` index + Workflows section; `~/.claude/skills/new-scala-service` retired (archive + de-install).
- CI templates keep Docker Hub publishing; when dockerhub-setup is skipped the image-push steps must degrade gracefully (secrets absent → skip publish, don't fail).
