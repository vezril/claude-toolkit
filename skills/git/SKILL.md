---
name: git
description: Using Git well — mastery of the model and the day-to-day/advanced workflows, distilled from Narębski's *Mastering Git* and Pidoux's *Git Best Practices Guide*. Covers the object model & DAG (blobs/trees/commits/tags, refs, HEAD, the index/staging area), exploring history (log/diff/blame/bisect), the everyday cycle (stage/commit/amend, .gitignore, stash, reset vs restore vs revert), branching & merging & rebasing (fast-forward vs 3-way merge, conflict resolution, interactive rebase, cherry-pick), keeping history clean (rewriting, squashing, reflog recovery, filter-repo), collaboration (remotes, fetch/pull/push, tracking branches, pull requests), branching models (GitHub Flow, Git Flow, trunk-based), commit-message conventions, tags & semver releases, subprojects (submodules/subtrees), hooks & customization, and repo administration/large-repo care. Use whenever working with Git — committing, branching, merging/rebasing, resolving conflicts, rewriting or recovering history, designing a team branching/PR workflow, writing commit messages, tagging releases, or recovering from a Git mess. Comprehensive, opinionated toward clean history and clear collaboration; pairs with github-actions, devops, and tdd.
---

# Git

How to use **Git** well — both a correct mental model of how Git works and the **best-practice workflows** for everyday and advanced use. Distilled from **Mastering Git** (Narębski — the model, internals, and advanced features) and the **Git Best Practices Guide** (Pidoux — collaboration, conflicts, CI). Opinionated toward **clean history** and **clear collaboration**.

Cross-links: [[github-actions]] (CI/CD on top of Git), [[devops]] (version control as the backbone of CI/CD/IaC and the First Way), [[tdd]] (commit discipline around the red-green-refactor loop), [[clean-code]]/[[software-design]] (small, coherent changes), [[secure-coding]] (never commit secrets).

## The mental model (get this right and the commands follow)

Git is a **content-addressable store** plus a **DAG of commits**. Internalize these and most confusion disappears:

- **Objects** (in `.git/objects`, keyed by SHA-1/SHA-256 hash of their content): **blob** (file contents), **tree** (a directory: names → blobs/trees), **commit** (a snapshot = one tree + parent commit(s) + author/committer + message), **tag** (annotated tag object). Identical content is stored once.
- **Snapshots, not diffs** — each commit references a full tree; diffs are computed on demand.
- **Refs** are pointers to commits: **branches** (`refs/heads/*`, a moving pointer), **tags** (`refs/tags/*`, fixed), **remote-tracking** (`refs/remotes/*`). **HEAD** points to the current branch (or a commit when "detached").
- **The three areas**: the **working tree** (your files), the **index / staging area** (the proposed next commit), and the **repository** (committed history). `add` moves working-tree → index; `commit` moves index → repo. Understanding the index explains `reset`, `restore`, partial staging, etc.
- **History is a Directed Acyclic Graph** — commits point to their parents; branches and merges are just the shape of that graph.

## The everyday cycle

- **Status & staging**: `git status`, `git add -p` (stage hunks, not whole files — make each commit coherent), `git diff` (working vs index) and `git diff --staged` (index vs HEAD).
- **Commit**: small, focused, atomic commits that each leave the tree working. `git commit --amend` to fix the *last* (unpushed) commit. Write good messages (below).
- **Undo, carefully** — know the three:
  - `git restore <file>` / `git restore --staged <file>` — discard working-tree change / unstage (the modern, safe verbs).
  - `git reset` — move HEAD/branch: `--soft` (keep index+worktree), `--mixed` (default, keep worktree), `--hard` (discard everything — dangerous).
  - `git revert <commit>` — make a **new** commit that undoes an old one (safe for shared history).
- **`git stash`** — shelve work-in-progress (`stash push -m`, `pop`, `list`, `--include-untracked`).
- **`.gitignore`** for generated files; **never commit secrets** ([[secure-coding]]) — use ignored env files / secret managers; if a secret lands in history, rotate it and scrub with `git filter-repo`.

## Exploring history (Mastering Git)

`git log` (with `--oneline --graph --decorate --all`, `-S`/`-G` pickaxe to find when a string changed, `--follow` across renames), `git show`, `git diff A..B` / `A...B`, `git blame` (who/when per line), and **`git bisect`** (binary search for the commit that introduced a bug — `start`/`bad`/`good`, or `bisect run <test>` to automate). Reference commits with `~`/`^`, ranges, and `@{…}` reflog syntax.

## Branching, merging, rebasing

- **Branch** = cheap movable pointer. `git switch -c <name>` (modern) / `git checkout -b`. Keep branches short-lived and topic-focused.
- **Merge**: **fast-forward** when the target hasn't diverged (no merge commit) vs **3-way merge** (creates a merge commit with two parents). `--no-ff` to always record a merge commit; `--ff-only` to refuse non-FF.
- **Rebase**: replay your commits onto a new base for a **linear history** (`git rebase main`). **Interactive rebase** (`git rebase -i`) to squash/fixup/reword/reorder/drop commits before sharing. **Golden rule: never rebase commits that have been pushed/shared** (it rewrites hashes).
- **Conflicts**: Git marks `<<<<<<< ======= >>>>>>>`; resolve, `git add`, then `git merge --continue`/`git rebase --continue`. Tools: `git mergetool`, `git checkout --ours/--theirs`, **`rerere`** (reuse recorded resolutions). Reduce conflicts with small, frequent integration.
- **`git cherry-pick`** to copy a specific commit onto the current branch.

## Keeping history clean (Mastering Git)

Decide a policy and apply it consistently: **squash/curate before merge** (interactive rebase, `--fixup` + `--autosquash`) so each merged commit is meaningful. Recover from mistakes with the **reflog** (`git reflog` — Git's safety net; almost nothing is truly lost for ~90 days) and `git reset --hard <reflog-entry>`. For bulk history surgery (remove a file/secret from all history) use **`git filter-repo`** (not the deprecated `filter-branch`). Understand that rewriting shared history forces collaborators to recover — coordinate it.

## Collaboration & remotes

- **Remotes**: `git remote -v`, `fetch` (download, don't merge), `pull` (= fetch + merge/rebase — prefer `pull --rebase` or set `pull.ff only`), `push` (set upstream with `-u`). Remote-tracking branches (`origin/main`) mirror the remote.
- **Pull/merge requests** are the review gate: small PRs, clear description, CI green ([[github-actions]]), at least one review. Protect `main` (require reviews + passing checks, no force-push).
- Keep a topic branch current with `git fetch` + `rebase` (or merge) of the base; force-push *your own* unshared branch with `--force-with-lease` (safer than `--force`).

## Branching models (pick one, document it)

- **GitHub Flow / trunk-based** — short-lived feature branches off `main`, PR + CI, merge and deploy frequently. Best default for continuous delivery ([[devops]]).
- **Git Flow** — long-lived `develop` + `main` with `feature/`, `release/`, `hotfix/` branches. Heavier; suits scheduled, versioned releases.
- **Forking workflow** — contributors fork, PR from their fork (open source).
- Whatever you pick: protect the mainline, keep branches short, integrate often (reduces conflicts and ties to CI).

## Commit messages & tags

- **Message convention**: a concise (~50-char) imperative subject ("Add X", not "Added X"), blank line, then a body explaining **why** (not what — the diff shows what), wrapping ~72 cols; reference issues. Consider **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`…) to drive changelogs/semver.
- **Tags**: prefer **annotated** tags (`git tag -a v1.2.0 -m`) for releases; follow **SemVer** (MAJOR.MINOR.PATCH). Push tags explicitly (`git push --tags`); tags often trigger release pipelines ([[github-actions]]).

## Subprojects, customization, administration

- **Submodules** (pin another repo at a commit; explicit, fiddly) vs **subtrees** (vendor code into your tree; simpler for consumers) — choose deliberately.
- **Hooks** (`.git/hooks` / a managed `pre-commit` framework) for local lint/test/format gates; **`.gitattributes`** for line-endings, diff/merge drivers, and `export-ignore`; per-repo/global `git config`, aliases.
- **Administration / large repos**: `git gc`/`maintenance`, `git lfs` for large binaries, shallow/partial clones (`--depth`, `--filter=blob:none`) and **sparse-checkout** for monorepos; mirror/bare repos for hosting.

## Anti-patterns (flag in review)

- Giant, mixed-purpose commits; meaningless messages ("wip", "fix", "stuff"); committing generated artifacts or **secrets**.
- `git push --force` to shared branches; rebasing already-pushed/public commits; `pull` creating noisy merge bubbles where rebase was intended.
- `git reset --hard` / `checkout -f` without realizing work is discarded (when in doubt, `stash` or branch first; the reflog can rescue you).
- Long-lived divergent branches (merge hell); committing directly to a protected `main`; ignoring CI status before merge.
- Using submodules where a package/dependency manager is the right tool.

## How to use this skill

- **`references/internals-and-history.md`** — the object model & DAG, refs/HEAD/index, and exploring history (log/diff/blame/bisect, revision selection).
- **`references/branching-merging-rebasing.md`** — branching, fast-forward vs 3-way merge, rebase/interactive rebase, cherry-pick, conflict resolution & rerere, keeping history clean (reflog, filter-repo).
- **`references/collaboration-and-workflows.md`** — remotes & PRs, branching models, commit conventions, tags/releases, submodules/subtrees, hooks, CI integration, and the *Git Best Practices Guide* recommendations.

## Always-apply defaults

1. **Small, atomic, well-described commits** (imperative subject + *why* body); stage with `-p` to keep them coherent.
2. **Short-lived topic branches + PRs with green CI** ([[github-actions]]); protect the mainline; integrate often.
3. **Rebase to curate local history; never rewrite shared history**; use `--force-with-lease`, never bare `--force`, and only on your own branches.
4. **`revert` (not `reset`) to undo public commits**; trust the **reflog** to recover.
5. **Never commit secrets** ([[secure-coding]]); `.gitignore` generated files; annotated tags + SemVer for releases.

## Related

- [[github-actions]] — CI/CD triggered by Git events; the natural automation layer on top.
- [[devops]] — version control as the foundation of flow, CI/CD, and IaC.
- [[tdd]] — commit cadence around red-green-refactor.
- [[clean-code]] / [[software-design]] — small, coherent changes; the same care applied to history.
- [[secure-coding]] — secret hygiene; scrubbing history with filter-repo.
- Sources: *Mastering Git* (Jakub Narębski), *Git Best Practices Guide* (Eric Pidoux).
