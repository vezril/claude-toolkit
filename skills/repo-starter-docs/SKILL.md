---
name: repo-starter-docs
description: "Create the starter documentation for a repository: a basic README.md and an MIT LICENSE.md, written into the local working copy (not committed — the git-ship skill handles commit/PR/merge). Takes an optional one-line project description; infers the project name from the directory/repo. Use when a fresh repo needs its baseline docs, typically right after github-new-repo in the new-github-project workflow."
argument-hint: "[one-line project description]"
license: MIT
---

# Starter docs (README.md + LICENSE.md)

Write two files into the current repository's working tree. Do **not** commit or push —
shipping is the git-ship skill's job, so the human gets one reviewable diff.

## Inputs

- `NAME` — the project name: the repo name from `git remote get-url origin` if there is an
  origin, else the current directory's basename.
- `DESCRIPTION` — the arguments, if given; otherwise ask for one short line (or accept the
  human's "skip" and use a `_TODO: describe <NAME>_` placeholder rather than inventing a
  description).
- `YEAR` — from `date +%Y`. `HOLDER` — from `git config user.name`.

If `README.md` or `LICENSE.md` already exists, do not overwrite it silently — show what's
there and ask.

## README.md

Keep it honest for an empty project — short, no invented features, no fake badges:

```markdown
# <NAME>

<DESCRIPTION>

## Status

Early scaffolding — nothing to see yet.

## Getting started

_TODO: document how to build, run, and test once there is something to build._

## License

MIT — see [LICENSE.md](LICENSE.md).
```

## LICENSE.md

The standard MIT text, verbatim, with the year and holder substituted:

```
MIT License

Copyright (c) <YEAR> <HOLDER>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Report

List the files written, the license holder/year used, and remind that nothing is committed
yet — point to git-ship for that.

## Guardrails

- Never overwrite existing docs without confirmation.
- The filename is `LICENSE.md` by this skill's contract (not `LICENSE`); note that GitHub
  detects it either way.
- Don't embellish the README — a placeholder that says "TODO" beats plausible fiction about
  a project that doesn't exist yet.
