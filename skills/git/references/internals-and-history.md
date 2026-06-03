# Git internals & exploring history (Mastering Git)

The model that makes every command make sense, plus the tools for reading history.

## The object model

`.git/objects` is a **content-addressable store**: every object is stored under the hash (SHA-1, or SHA-256 in newer repos) of its content. Four object types:

- **blob** — raw file contents (no name, no metadata). Identical files share one blob (dedup).
- **tree** — a directory listing: entries of `(mode, type, hash, name)` pointing at blobs (files) and other trees (subdirs).
- **commit** — a snapshot: one **root tree** + zero-or-more **parent** commit hashes + author + committer + message. Zero parents = root commit; one = normal; two+ = merge.
- **tag** (annotated) — a named, signed/annotated pointer to an object (usually a commit) with its own message.

Because a commit names its parents, history is a **Directed Acyclic Graph (DAG)**. Inspect raw objects with `git cat-file -p <hash>` and `git rev-parse`.

## Refs, HEAD, and the index

- **Refs** are just files containing a hash: branches under `refs/heads/`, tags under `refs/tags/`, remote-tracking under `refs/remotes/`. A **branch** is a pointer that moves forward when you commit on it.
- **HEAD** normally contains `ref: refs/heads/<branch>` (symbolic) — "where the next commit attaches." **Detached HEAD** = HEAD points straight at a commit (checking out a tag/old commit); commits made there are unreferenced unless you branch.
- **The index (staging area)** — `.git/index`, a binary file describing the tree of the *next* commit. `git add` writes blobs + updates the index; `git commit` turns the index into a tree + commit object. Partial staging (`add -p`), `reset`, and `restore --staged` all manipulate the index.
- **Packfiles** — loose objects get compressed into packfiles by `git gc`/`maintenance` (delta-compressed; this is where storage efficiency comes from).

## Revision selection (how to name commits)

- By hash (short prefix ok), by ref name, `HEAD`.
- **Ancestry**: `HEAD^` (first parent), `HEAD^2` (second parent of a merge), `HEAD~3` (three first-parents back).
- **Reflog**: `HEAD@{2}`, `main@{yesterday}` — recent positions of a ref (local, time-limited).
- **Ranges**: `A..B` (reachable from B but not A — "what's new on B"), `A...B` (symmetric difference), `^A B`, `--not`.

## Exploring history

- **`git log`** — `--oneline --graph --decorate --all` for the DAG; `-p` for patches; `--stat`; `--author`/`--since`/`--grep` filters; **pickaxe** `-S"text"` (commits that changed the count of a string) and `-G<regex>`; `--follow <file>` across renames; `log <range>`.
- **`git show <obj>`** — a commit's message + diff, or any object's content.
- **`git diff`** — working↔index (`git diff`), index↔HEAD (`--staged`), commit↔commit (`A..B`), or `--stat`/`--name-only`.
- **`git blame <file>`** — last commit to touch each line (`-L` to limit lines, `-C`/`-M` to follow copies/moves); pair with `git log -L`.
- **`git bisect`** — binary search for the first bad commit: `git bisect start; git bisect bad; git bisect good <old>` then test each checkout and mark `good`/`bad`; or **automate** with `git bisect run <test-script>` (script exits 0 = good, non-zero = bad). `git bisect reset` when done.
- **`git grep`** — search the worktree/any tree fast (respects Git's knowledge of tracked files).

## Useful plumbing/inspection

`git rev-parse`, `git cat-file -p/-t`, `git ls-tree`, `git reflog`, `git fsck` (find dangling/corrupt objects), `git count-objects -v` (repo size). You rarely need plumbing day-to-day, but it's how the porcelain commands are built — and how you debug a confusing repo state.
