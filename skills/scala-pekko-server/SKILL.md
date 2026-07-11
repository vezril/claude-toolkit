---
name: scala-pekko-server
description: "Scaffold the PRODUCTION sources of a Scala 3 + Pekko service into the current working tree: the pure core domain (Greeting), the server (Main, HttpServer with coordinated-shutdown wiring, HelloRoutes GET /, HealthRoutes GET /health with readiness, AppConfig) and its resources (application.conf, logback.xml with JSON/text toggle). Test-territory counterpart is scala-pekko-tests; this skill never creates or edits test files. Run after scala-sbt-build in the new-scala-pekko-service workflow."
argument-hint: "<project-name> [pkg-root]"
license: MIT
---

# Scala Pekko server scaffold (production only)

Generate the production code — deterministically, via the bundled script. This is the
GREEN-territory half of the scaffold pair: **production sources only, never tests** (the
same file-territory rule as the implementer agent, applied to scaffolding).

Bundled script: `scaffold.sh` in this skill's folder.

## Run

```
bash <skill-dir>/scaffold.sh <project-name> [pkg-root]
```

Same name/pkg-root contract as scala-sbt-build — pass identical values or the compile gate
will catch the mismatch. Refuses to run if `server/src/main/scala` already exists.

What it writes:

- `core/src/main/scala/<pkg>/Greeting.scala` — pure domain, zero Pekko.
- `server/src/main/scala/<pkg>/` — `Main` (bind, readiness, exit-on-bind-failure),
  `http/HttpServer` (bind + coordinated shutdown), `http/HelloRoutes` (`GET /`),
  `http/HealthRoutes` (`GET /health`, UP/DOWN by readiness), `config/AppConfig`.
- `server/src/main/resources/` — `application.conf` (env-overridable, no secrets),
  `logback.xml` (LOG_FORMAT=json toggle).

## Report

Files written and the package they landed in.

## Guardrails

- Territory is absolute: no test files, no build files, no docs, no CI.
- If a needed change belongs in a test, report it for scala-pekko-tests instead of writing it.
- Never overwrite existing production sources (the script refuses).
