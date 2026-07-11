# Tasks: decompose-scala-scaffold

> Prerequisite: change `add-archive-skill` is implemented (task group 6 uses it).

## 1. new-github-project bare mode

- [x] 1.1 Add `docs`/`ship` flags (default true) to `workflows/new-github-project.js`; fail fast on `docs:false, ship:true`
- [x] 1.2 Re-sync the installed copy in `~/.claude/workflows/`; update the workflow's README entry

## 2. Scaffold skills (split scaffold.sh by concern)

- [x] 2.1 `skills/scala-sbt-build/` — SKILL.md + scaffold.sh (build.sbt with deps, project/, plugins, fmt/fix configs, .gitignore); pkg-root parameter, default `me.cference`; README-enrichment step
- [x] 2.2 `skills/scala-pekko-server/` — SKILL.md + scaffold.sh (Main, HttpServer, Hello/Health routes, AppConfig, conf, logback); production-only territory
- [x] 2.3 `skills/scala-pekko-tests/` — SKILL.md + scaffold.sh (core spec, route specs); test-only territory; imports read from generated sources
- [x] 2.4 `skills/github-actions-scala-ci/` — SKILL.md + scaffold.sh (ci/dev/release + setup-scala); secrets-absent → publish skipped (env-indirection `if:` pattern)
- [x] 2.5 Verify the split covers the monolith: diff the union of generated trees against old `scaffold.sh` output minus README/LICENSE (drop-list documented)

## 3. dockerhub-setup skill

- [x] 3.1 `skills/dockerhub-setup/SKILL.md` — inherit dockerhub-repo.sh logic; add CI-token minting + fallback; `gh secret set` piping; credential hygiene guardrails

## 4. Orchestration workflow

- [x] 4.1 `workflows/new-scala-pekko-service.js` — args contract (name/visibility/dockerhub required, pkgRoot/auto optional), phases per design, green gate, single gated PR, development-branch post-merge step
- [x] 4.2 Install to `~/.claude/workflows/`

## 5. End-to-end verification

- [ ] 5.1 Full gated run against a throwaway repo name: verify bare bootstrap, scaffold, green gate, PR, `awaiting-merge-approval`; approve, merge, confirm `development` created; then delete the throwaway repo (human does the deletion)
- [x] 5.2 Red-path check: sabotage one generated file in a scratch run, confirm `status: failed` and nothing pushed
- [ ] 5.3 `dockerhub:false` run — confirm CI green with publish skipped (can piggyback on 5.1)

## 6. Retirement + docs

- [x] 6.1 Archive `~/.claude/skills/new-scala-service` via toolkit-archive (successors: new-scala-pekko-service workflow + the five skills); dockerhub-repo.sh noted as inherited by dockerhub-setup
- [x] 6.2 README: index the five skills + the workflow; note LICENSE.md standardization
- [ ] 6.3 Strict-YAML check across all SKILL.md frontmatters; ship via git-ship (gated)
