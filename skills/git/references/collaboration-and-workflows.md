# Collaboration, workflows & best practices (Git Best Practices Guide)

Remotes, team workflows, conventions, releases, and the practical recommendations from Pidoux's *Git Best Practices Guide* (with continuous-integration tie-ins).

## Remotes & syncing

- A **remote** is a named URL (`origin`, `upstream`). `git remote -v` to list, `git remote add <name> <url>`.
- **`git fetch`** downloads new objects + updates remote-tracking refs (`origin/main`) **without touching your branches** — always safe.
- **`git pull`** = fetch + integrate. Prefer **`git pull --rebase`** (or `git config pull.rebase true` / `pull.ff only`) to avoid spurious merge commits on feature branches.
- **`git push`** uploads commits; `git push -u origin <branch>` sets the upstream the first time. Push tags with `git push --tags` or `--follow-tags`.
- **Tracking branches**: a local branch can track a remote one so `status` shows ahead/behind and `pull`/`push` know the target.

## Working in a team

- **Branch per task/feature/bugfix**, short-lived, named clearly (`feature/login`, `fix/issue-123`). Branch off the latest mainline; integrate frequently to minimize divergence and conflicts.
- **Pull requests / merge requests** are the review and quality gate: keep them **small and focused**, write a description of *why* and *how to test*, require **CI green** ([[github-actions]]) and at least one reviewer. Review for correctness, design ([[clean-code]]/[[software-design]]), and tests ([[tdd]]).
- **Protect the mainline**: require PRs, passing checks, and reviews; forbid force-push and direct commits to `main`.
- Communicate before any **history rewrite** that touches shared branches.

## Finding & resolving conflicts (Pidoux)

Conflicts are normal, not failures. Minimize them by integrating often and keeping changes small; resolve them by understanding *both* intents (use `git log`/`blame` on the conflicting region), not by blindly taking one side. Use `git diff`, `mergetool`, and **`rerere`** for repeated resolutions. After resolving, **re-run the tests** before continuing the merge/rebase.

## Branching models (choose and document one)

- **GitHub Flow / trunk-based development** — one always-deployable `main`; short-lived feature branches; PR + CI; merge and deploy continuously. Best default for continuous delivery ([[devops]]); fewest long-lived branches.
- **Git Flow** — `main` (releases) + `develop` (integration) + supporting `feature/`, `release/`, `hotfix/` branches. Structured but heavy; fits scheduled, versioned releases. Beware the overhead for fast-moving teams.
- **Forking workflow** — contributors work in personal forks and open PRs upstream; standard for open source.

## Commit message conventions

- **Subject**: imperative mood, ≤ ~50 chars, capitalized, no trailing period ("Fix race in cache eviction").
- **Body** (after a blank line, wrap ~72 cols): explain the **why** and any consequences/trade-offs; reference issues/tickets (`Fixes #123`).
- Consider **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `BREAKING CHANGE:`) — machine-readable, drives automated changelogs and SemVer bumps.
- One logical change per commit; the history should read as a story of the project.

## Tags & releases

- Mark releases with **annotated tags** (`git tag -a v2.1.0 -m "..."`); they carry metadata and can be signed (`-s`). Push explicitly.
- Follow **Semantic Versioning** (MAJOR.MINOR.PATCH): breaking / feature / fix. Tags commonly **trigger release pipelines** ([[github-actions]] `on: push: tags`).

## Subprojects

- **Submodules** — embed another repo pinned at a specific commit (`git submodule add/update --init --recursive`). Explicit and exact, but easy to leave un-updated and confusing for contributors.
- **Subtree** — merge another project's tree into a subdirectory of yours (`git subtree add/pull`). Simpler for consumers (no extra clone step), harder to push changes back.
- Often a real **package/dependency manager** is the better answer than either.

## Hooks, attributes & config

- **Hooks**: client-side (`pre-commit`, `commit-msg`, `pre-push`) to lint/format/test/validate messages locally; server-side for policy enforcement. The **`pre-commit`** framework manages them portably.
- **`.gitattributes`**: normalize line endings (`* text=auto`), mark binary files, set diff/merge drivers, `export-ignore`.
- **`git config`** (system/global/local), aliases (`git config --global alias.lg "log --oneline --graph --all"`), and a sensible global `.gitignore`.

## Using Git for Continuous Integration (Pidoux Ch. 5)

Git is the trigger and source of truth for CI/CD: pushes and PRs kick off builds/tests; tags kick off releases; status checks gate merges. Keep `main` always green and deployable; small, frequent commits give CI tight feedback loops. The automation layer is [[github-actions]] (or another CI), and the philosophy is [[devops]] (the First Way — fast flow from commit to production).
