# Branching, merging, rebasing & clean history

The graph-shaping operations — where most Git skill (and most Git accidents) live.

## Branches

A branch is a movable pointer to a commit; creating one is O(1). `git switch <name>` / `git switch -c <name>` (modern) or `git checkout [-b]`. List with `git branch [-a -v]`; delete merged with `-d`, force with `-D`. Keep branches **short-lived and single-purpose** — long divergence is what produces painful merges.

## Merging

- **Fast-forward**: if the target branch is a direct ancestor of the source, Git just moves the pointer forward — no merge commit, linear history. Forbid/force with `--ff-only` / `--no-ff`.
- **Three-way merge**: when branches have diverged, Git finds the **merge base** (common ancestor) and combines the two sides, creating a **merge commit with two parents**. Non-conflicting changes merge automatically.
- **Merge conflicts** happen when both sides change the same region. Git inserts markers:
  ```
  <<<<<<< HEAD
  your side
  =======
  their side
  >>>>>>> other-branch
  ```
  Edit to the desired result, remove markers, `git add` the file, then `git merge --continue` (or `git commit`). Abort with `git merge --abort`.
- Helpers: `git mergetool`, `git checkout --ours/--theirs <file>` (take one side wholesale), `git diff` during a conflict shows the combined diff. **`git rerere`** ("reuse recorded resolution") remembers how you resolved a conflict and replays it next time the same conflict appears — invaluable during long rebases.

## Rebasing

- **`git rebase <base>`** replays your branch's commits one-by-one onto `<base>`, producing a **linear history** with no merge commit. Conflicts are resolved per replayed commit (`--continue`/`--skip`/`--abort`).
- **Interactive rebase** `git rebase -i <base>` opens a todo list to **reword, edit, squash, fixup, drop, reorder** commits — the primary tool for curating a branch before opening/merging a PR. Combine `git commit --fixup=<sha>` while working with `git rebase -i --autosquash` to auto-arrange fixups.
- **`git pull --rebase`** keeps a feature branch current without merge bubbles.
- **THE GOLDEN RULE**: never rebase (or otherwise rewrite) commits that have already been pushed/shared — it changes their hashes and forces everyone else to recover. Rewrite only local, unshared history.

## Merge vs rebase — when to use which

- **Rebase** local/topic commits to keep them clean and linear before sharing; rebase your feature branch onto an updated base.
- **Merge** (often `--no-ff`) to integrate a completed, reviewed branch into the mainline when you want to preserve the fact that a set of commits belonged together — or any time the commits are already public.
- Many teams: rebase-and-squash feature branches, merge into `main` via PR. Document the team policy so history stays consistent.

## Cherry-pick

`git cherry-pick <commit>` applies the change introduced by a specific commit onto the current branch (new commit, new hash). Use for backporting a fix to a release branch. `-n` to stage without committing; ranges supported.

## Keeping history clean & recovering

- **Curate before merge**: squash noise (`-i`), write meaningful messages, ensure each commit builds.
- **The reflog is your safety net**: `git reflog` lists every position HEAD has held (even after "destructive" `reset --hard`, bad rebase, deleted branch). Recover with `git reset --hard HEAD@{n}` or `git branch rescue HEAD@{n}`. Unreferenced commits survive ~90 days before `gc`.
- **Undo a bad rebase/merge**: `git reset --hard ORIG_HEAD` (Git stashes the pre-operation position there) or via reflog.
- **Bulk history rewriting** (purge a committed secret or huge file from *all* history): use **`git filter-repo`** (modern, fast; `filter-branch` is deprecated and error-prone). Then force-push the rewritten history and have collaborators re-clone; **rotate any leaked secret regardless**.
- **`--force-with-lease`** when you must overwrite your own remote branch after a rebase — it refuses if someone else pushed in the meantime, unlike bare `--force`.
