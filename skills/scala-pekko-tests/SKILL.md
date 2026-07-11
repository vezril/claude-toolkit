---
name: scala-pekko-tests
description: "Scaffold the TEST sources of a Scala 3 + Pekko service into the current working tree: the core GreetingSpec and the server route specs (hello + health, status and body assertions, readiness UP/DOWN, sealed-route 404) with ScalaTest. Production-territory counterpart is scala-pekko-server; this skill never touches production sources and reads the real package from the generated production code rather than re-deriving it. Run after scala-pekko-server in the new-scala-pekko-service workflow."
argument-hint: "<project-name>"
license: MIT
---

# Scala Pekko tests scaffold (tests only)

Generate the scaffold's test suite — deterministically, via the bundled script. This is the
RED-territory half of the scaffold pair: **test sources only, never production** (the
test-writer agent's file-territory rule, applied to scaffolding).

Bundled script: `scaffold.sh` in this skill's folder.

## Run

```
bash <skill-dir>/scaffold.sh <project-name>
```

No pkg-root argument: the script locates the generated `Greeting.scala` and reads the
`package` declaration from it — the production sources are the source of truth. It fails
with a clear error if they don't exist yet (run scala-pekko-server first), and refuses to
run if `server/src/test/scala` already exists.

What it writes:

- `core/src/test/scala/<pkg>/GreetingSpec.scala`
- `server/src/test/scala/<pkg>/http/HelloRoutesSpec.scala` — `GET /` 200 + body.
- `server/src/test/scala/<pkg>/http/HealthRoutesSpec.scala` — 200 UP with service+version,
  503 DOWN when readiness withdrawn, 404 via the sealed route.

## Report

Files written and the package they were read into.

## Guardrails

- Territory is absolute: no production sources, no build files, no docs, no CI.
- If a spec reveals a production bug, report it for scala-pekko-server — don't fix it here.
- Never overwrite existing test sources (the script refuses).
