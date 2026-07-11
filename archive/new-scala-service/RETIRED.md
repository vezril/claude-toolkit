# RETIRED: new-scala-service

- **What it was:** A monolithic personal skill (component type: skill, lived in
  `~/.claude/skills/`, never in this repo) that scaffolded a complete Scala 3 + Apache
  Pekko service in one shot: a 978-line `scaffold.sh` generating the two-module sbt build,
  server, tests, CI/CD, README/LICENSE and an OpenSpec folder, plus `dockerhub-repo.sh`
  for the Docker Hub repo, orchestrated by its SKILL.md (scaffold → sbt verify → git init →
  gh repo create → direct push to main → Docker Hub → secrets).
- **Why retired:** Decomposed into hyper-specific, individually reusable parts
  (OpenSpec change `decompose-scala-scaffold`). The monolith duplicated what the bootstrap
  primitives own (repo creation, docs, shipping), pushed unreviewed scaffolds directly to
  `main`, applied no branch protection, and hardcoded personal conventions
  (`me.cference` package root).
- **Replaced by:** the `new-scala-pekko-service` workflow composing `new-github-project`
  (bare mode), `scala-sbt-build`, `scala-pekko-server`, `scala-pekko-tests`,
  `repo-starter-docs`, `github-actions-scala-ci`, `dockerhub-setup`
  (which inherits `dockerhub-repo.sh`'s repo-creation logic), and `git-ship`.
- **Retired on:** 2026-07-11
