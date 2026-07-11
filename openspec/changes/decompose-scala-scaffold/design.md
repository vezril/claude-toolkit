# Design: decompose-scala-scaffold

## Shape

```
new-scala-pekko-service (workflow)
│  args: { name, visibility: 'public'|'private', dockerhub: boolean, auto?: false }
│        — name, visibility AND dockerhub are required: the outer conversation
│          must ask the human ("Docker Hub repo needed?"); no silent default.
│
├─ Phase 1  BOOTSTRAP   workflow('new-github-project', {name, visibility,
│                         docs:false, ship:false})   ← bare mode, returns inline
├─ Phase 2  SCAFFOLD    on branch feat/scaffold, sequential, disjoint files:
│                         scala-sbt-build → scala-pekko-server →
│                         scala-pekko-tests → repo-starter-docs →
│                         github-actions-scala-ci
├─ Phase 3  DOCKERHUB   only if dockerhub:true → dockerhub-setup skill
├─ Phase 4  VERIFY      sbt -batch scalafmtAll compile test
│                         red → status:failed, nothing pushed
└─ Phase 5  SHIP        git-ship: push branch, open PR
                          auto:false → return awaiting-merge-approval + nextStep
                          auto:true  → merge, sync main, create+push development
```

## Decisions

**Single gated PR.** Bare mode (docs:false, ship:false) means no placeholder-docs PR and no nested merge gate; docs are written by `repo-starter-docs` *inside* the scaffold branch. One PR carries the entire scaffold; `awaiting-merge-approval` fires exactly once, and only after the green gate.

**Green-before-remote survives repo-first.** The GitHub repo shell (empty seed commit, protected) exists from Phase 1, but no *code* leaves the machine until Phase 4 is green. A red scaffold leaves an empty repo — annoying, not broken. The workflow result must say so honestly (`status: failed, repoCreated: true`).

**Sequential scaffold, not parallel.** The five scaffold skills write disjoint file sets and could fan out, but sequential lets later skills read earlier output (tests read the server's real package names) and costs seconds. Each skill = one `agent()` call in the same working tree; no worktree isolation.

**Each scaffold skill carries its own script.** `scaffold.sh` (978 lines) splits by concern into `skills/<skill>/scaffold.sh` with the same quoted-heredoc + placeholder-substitution technique. Determinism stays in shell; SKILL.md orchestrates, verifies, and reports. Name derivation (NAME/SERVICE/PKGSEG) is duplicated per script from a shared documented convention — scripts stay standalone-runnable.

**Package root is a parameter.** `--pkg-root me.cference` default; flows from the workflow args into `scala-sbt-build`, `scala-pekko-server`, `scala-pekko-tests`. The toolkit is public; the personal convention becomes a default, not a hardcode.

**Docs ownership moves.** The scaffold scripts no longer write README/LICENSE. `repo-starter-docs` owns them → `LICENSE.md` becomes the standard (the old scaffold's `LICENSE` disappears). The scala README needs real Getting-started content (sbt server/run, endpoints) — `repo-starter-docs` stays generic; the `scala-sbt-build` step appends the scala-specific Getting-started section to the README afterward. Ownership: repo-starter-docs creates, the flavor enriches.

**`development` branch after merge.** Creating it at bootstrap would leave it pointing at the empty seed commit. Instead: after the scaffold PR merges, create `development` from merged `main` and push (protection only rules `main`; direct push is fine). auto mode does it inline; gated mode puts it in the returned `nextStep` so the outer conversation does it post-approval.

**Docker Hub token flow** (`dockerhub-setup`):
1. Requires `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN` (an existing admin PAT) in the environment. Absent → the skill stops with instructions; it never asks for or handles a password in chat.
2. Login to `hub.docker.com/v2` with the admin PAT → JWT.
3. Create the repo (existing `dockerhub-repo.sh` logic, inherited).
4. Mint a **new** access token for CI (`POST /v2/access-tokens`, label `<repo>-ci`, write scope). Personal access tokens are account-wide, not per-repo — accepted limitation, recorded in the skill's report. If token minting fails (2FA/plan restrictions), fall back to using the admin PAT as the CI secret, loudly flagged in the report.
5. `gh secret set DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` on the repo — values piped, never echoed.

**CI must degrade without Docker Hub.** `dev.yml`/`release.yml` image-publish jobs guard on the secrets' presence (`if: secrets.DOCKERHUB_USERNAME != ''` via an env indirection, since `secrets` isn't directly usable in `if`) so a `dockerhub:false` project still gets green CI.

**Retirement.** Last step: `toolkit-archive` (from add-archive-skill) archives `~/.claude/skills/new-scala-service` into the repo's `archive/` with RETIRED.md pointing at the new workflow + skills. Sequencing: add-archive-skill ships first.

## Risks

- Hub API token endpoints are less stable than GitHub's; the fallback path (admin PAT as secret) keeps the workflow shippable.
- Splitting the heredoc monolith risks drift between the four scripts' name-derivation logic — mitigated by a documented shared convention and the Phase 4 compile gate, which catches package mismatches immediately.
- The `secrets`-in-`if` GitHub Actions quirk needs the env-indirection pattern; get it right once in `github-actions-scala-ci`.
