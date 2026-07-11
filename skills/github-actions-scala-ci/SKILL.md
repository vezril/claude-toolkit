---
name: github-actions-scala-ci
description: "Scaffold the GitHub Actions CI/CD surface for a Scala 3 + Pekko service into the current working tree: ci.yml (scalafmt check, compile + test with coverage, sbt-dynver sanity, gitleaks secret scan, on PRs to development/main), dev.yml (:dev and :dev-<sha> images from development), release.yml (immutable :X.Y.Z + :latest images and a GitHub Release from a vX.Y.Z tag on main), plus the shared setup-scala composite action. Image publishing degrades gracefully: absent DOCKERHUB_* secrets skip the publish steps instead of failing. Final scaffold step of the new-scala-pekko-service workflow."
argument-hint: "<project-name>"
license: MIT
---

# GitHub Actions CI/CD scaffold (Scala)

Generate the pipeline — deterministically, via the bundled script.

Bundled script: `scaffold.sh` in this skill's folder.

## Run

```
bash <skill-dir>/scaffold.sh <project-name>
```

Refuses to run if `.github/workflows/ci.yml` already exists. Writes only `.github/`.

What it writes:

- `.github/actions/setup-scala/` — JDK 21 (Temurin) + sbt + Coursier caching, shared by all
  workflows; every third-party action is SHA-pinned.
- `ci.yml` — PRs to `development`/`main`: format (own job, can't be masked by green tests),
  compile + test + coverage (reported, not gated), dynver snapshot sanity, gitleaks scan.
- `dev.yml` — push to `development`: tests, then `:dev` + `:dev-<short-sha>` images.
- `release.yml` — `vX.Y.Z` tag: tag-on-main ancestry check, tests, immutable `:X.Y.Z` +
  moving `:latest`, GitHub Release with generated notes.

## Docker Hub degradation (by design)

`dev.yml`/`release.yml` check the `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets via an
env-indirection step (`secrets.*` is not readable in `if:`) and **skip** every image step
when absent — tests and the GitHub Release still run, the workflow stays green. Wiring the
secrets is dockerhub-setup's job; adding them later needs no CI change.

## Report

Files written, and whether the repo currently has the Docker Hub secrets (publish active
vs. skipped).

## Guardrails

- Territory: only `.github/` — no build, sources, tests, or docs.
- Keep third-party actions SHA-pinned when editing versions.
- Never weaken the release gates (tag-on-main check, semver immutability) — they are the
  spec'd contract of release.yml.
