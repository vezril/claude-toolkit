---
name: new-scala-service
description: Scaffold a brand-new Scala 3 + Apache Pekko service under ~/Code with the full constellation boilerplate (two-module sbt build, Hello-World + /health HTTP server, sbt-dynver, scalafmt/scalafix, Docker image via native-packager, ci/dev/release GitHub Actions, OpenSpec folder), then create + push the GitHub repo and create the Docker Hub repo. Use when Calvin wants to start a new service/project from nothing.
argument-hint: <project-name>  (e.g. athena-service)
license: MIT
---

# New Scala service

Scaffold a fresh Scala 3 + Apache Pekko service that matches the constellation conventions
(modelled on `hephaestus-service`), verify it compiles + tests green, then wire up GitHub and
Docker Hub. The heavy lifting lives in two bundled scripts — your job is to orchestrate them, gate
the outward-facing steps on the user's confirmation, and report clearly.

Bundled scripts (reference by absolute path):
- `~/.claude/skills/new-scala-service/scaffold.sh` — generates the whole project tree.
- `~/.claude/skills/new-scala-service/dockerhub-repo.sh` — creates the Docker Hub repo via the Hub API.

Fixed conventions (don't ask): GitHub owner `vezril`, Docker Hub namespace `calvinference`,
package root `me.cference.<service>`, JDK/Docker base 21, branches `main` + `development`.

---

## Step 0 — resolve the name

The project name is in the arguments. If empty, ask for one (e.g. `athena-service`) and stop.
It must be lowercase `[a-z0-9-]`. Derive (the script does this too, shown here so you can echo it):
- `NAME` = the argument (`athena-service`)
- `SERVICE` = `NAME` minus a trailing `-service`/`-svc` (`athena`) — the image name + health `service` field
- package = `me.cference.<service-without-hyphens>`

## Step 1 — preflight

- `~/Code/<NAME>` must NOT already exist (the script refuses otherwise — surface the error).
- Confirm tooling: `sbt`, `gh`, `docker`, `jq`, `git` on PATH; `gh auth status` logged in as `vezril`.
- Note whether `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are set in the environment (needed for the
  Docker Hub repo + setting repo secrets). If absent, those steps are SKIPPED (not fatal) — say so.

## Step 2 — scaffold

Run: `bash ~/.claude/skills/new-scala-service/scaffold.sh <NAME>`

This writes the full tree under `~/Code/<NAME>`: `build.sbt` + `project/`, pure `core/` (Greeting +
test), Pekko `server/` (Main, HttpServer, HelloRoutes `GET /`, HealthRoutes `GET /health`, AppConfig,
`application.conf`, `logback.xml`, route tests), `.github/` (ci/dev/release + setup-scala action),
`openspec/`, and `.scalafmt.conf` / `.scalafix.conf` / `.gitignore` / `LICENSE` / `README.md`.

## Step 3 — verify (green before anything leaves the machine)

From `~/Code/<NAME>`, run: `sbt -batch scalafmtAll compile test`

- `scalafmtAll` normalizes formatting so CI's `scalafmtCheckAll` will pass.
- First run downloads Pekko/ScalaTest — it's slow; that's expected.
- If compile or tests fail, STOP and fix the scaffold output before proceeding. Do not push broken
  boilerplate. (Report the failure honestly.)

## Step 4 — git

From `~/Code/<NAME>`:
```
git init -b main
git add -A            # brand-new repo you just created — -A is fine HERE only
git commit -m "Scaffold <NAME>: Scala 3 + Pekko service, Hello-World + /health, CI/CD, OpenSpec"
git branch development
```
(End the commit body with the standard `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` line.)

## Step 5 — GitHub repo + push  ⚠️ CONFIRM FIRST

Creating a repo + pushing is outward-facing. BEFORE doing it, show the user exactly what will happen
and get a yes:

> About to create **github.com/vezril/<NAME>** (visibility: **public**) and push `main` + `development`.
> Also create Docker Hub **calvinference/<SERVICE>** (public). Proceed?

Default visibility is **public** (matches the constellation). If they want private, use `--private`.
On approval:
```
gh repo create vezril/<NAME> --public --source . --remote origin --description "<SERVICE> — Scala 3 + Pekko service"
git push -u origin main
git push -u origin development
```

## Step 6 — Docker Hub repo (best-effort)

Only if `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN` are in the env (else skip with a note that CI's
first push will auto-create it):
```
DOCKERHUB_USERNAME="$DOCKERHUB_USERNAME" DOCKERHUB_TOKEN="$DOCKERHUB_TOKEN" \
  bash ~/.claude/skills/new-scala-service/dockerhub-repo.sh calvinference <SERVICE> "<SERVICE> — Scala 3 + Pekko service"
```

## Step 7 — repo secrets (so CI can publish)

Only if the Docker Hub creds are available, set them as repo secrets so `dev.yml` / `release.yml`
can log in and push images:
```
printf '%s' "$DOCKERHUB_USERNAME" | gh secret set DOCKERHUB_USERNAME --repo vezril/<NAME>
printf '%s' "$DOCKERHUB_TOKEN"    | gh secret set DOCKERHUB_TOKEN    --repo vezril/<NAME>
```

## Step 8 — report

Summarize crisply:
- Local path, GitHub URL, Docker Hub URL (or "will be created on first CI push" if skipped).
- Endpoints (`GET /`, `GET /health`) and how to run locally (`sbt server/run`, port 8080).
- Manual follow-ups the skill deliberately did NOT do, so nothing is silently assumed:
  - **Branch protection** on `main` (require the `Format` + `Compile & test` checks) — optional, not
    set by default so a solo dev isn't locked out. Offer the `gh api` command if they want it.
  - Docker Hub creds / secrets if they were skipped.
  - First release: tag `v0.1.0` on `main` to trigger `release.yml`.

---

## Guardrails

- **`git add -A` is allowed ONLY in the freshly-created `~/Code/<NAME>`** (nothing else lives there).
  Never run it in any other repo.
- **Confirm before Step 5** (public GitHub repo + public Docker Hub repo are outward-facing and hard
  to undo). One confirmation covers both creates.
- **Never print secrets.** Docker Hub creds are read from the env and piped straight into `gh secret`
  / the Hub API — don't echo their values.
- If a best-effort step (Docker Hub, secrets, protection) fails, report it and continue — the repo and
  code are already safely created; these are recoverable follow-ups.
