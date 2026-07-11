---
name: scala-sbt-build
description: "Scaffold the sbt build definition for a two-module (pure core / Pekko server) Scala 3 service into the current working tree: build.sbt with all library dependencies (Pekko, pekko-http, ScalaTest, logback), project/ with plugins (sbt-dynver, native-packager, scalafmt, scalafix, scoverage, buildinfo), the formatter/linter configs, and .gitignore. Package root is a parameter (default me.cference). Writes no application sources, tests, docs, or CI — those belong to scala-pekko-server, scala-pekko-tests, repo-starter-docs, and github-actions-scala-ci. First scaffold step of the new-scala-pekko-service workflow."
argument-hint: "<project-name> [pkg-root]   (e.g. athena-service org.example)"
license: MIT
---

# Scala sbt build scaffold

Generate the build definition — deterministically, via the bundled script. Run from the
project's working tree (the repo root).

Bundled script: `scaffold.sh` in this skill's folder (invoke by absolute path).

## Run

```
bash <skill-dir>/scaffold.sh <project-name> [pkg-root]
```

- `project-name` — lowercase `[a-z0-9-]`, e.g. `athena-service`. The script derives
  `SERVICE` (name minus `-service`/`-svc`) and the package segment.
- `pkg-root` — optional, default `me.cference`; full package becomes
  `<pkg-root>.<segment>`.

The script refuses to run if `build.sbt` already exists, writes only its own territory
(`build.sbt`, `project/`, `.scalafmt.conf`, `.scalafix.conf`, `.gitignore`), and
substitutes all placeholders itself.

## README enrichment (after repo-starter-docs)

If `README.md` exists (repo-starter-docs wrote it), **append** the scala Getting-started
content — never replace the file or its description/license sections. Replace the
`## Getting started` TODO section with:

- Layout: `core/` (pure domain, no Pekko) and `server/` (Pekko HTTP runtime + Docker).
- Endpoints: `GET /` → hello; `GET /health` → status/service/version JSON (503 during shutdown).
- Develop: `sbt compile`, `sbt test`, `sbt server/run` (port 8080, `HTTP_PORT` overrides),
  `sbt scalafmtAll`.
- Docker: `sbt server/Docker/publishLocal`, then `docker run -p 8080:8080 <user>/<service>:<version>`.
- CI/CD: ci.yml on PRs; dev.yml publishes `:dev` images from `development`; release.yml
  publishes `:X.Y.Z` + `:latest` from a `vX.Y.Z` tag; versioning is git-tag-driven
  (sbt-dynver); image publishing needs the `DOCKERHUB_*` secrets (skipped gracefully if absent).

## Report

Files written, the derived package, and what was appended to the README.

## Guardrails

- Territory: never write application sources, tests, README/LICENSE creation, or CI files.
- Never overwrite an existing `build.sbt` (the script enforces this).
- Version bumps (Scala, Pekko, plugin versions) happen in the script — this file's list of
  concerns is stable, the pins live in one place.
