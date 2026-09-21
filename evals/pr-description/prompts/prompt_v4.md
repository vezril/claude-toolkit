---
name: pr-description
description: Write pull request descriptions. Use when creating a PR, or when the user asks to summarize changes for a pull request.
---

When writing a PR description:

1. Run `git diff main...HEAD` to see all changes on this branch
2. Write a description following this format:

## What
One sentence explaining what this PR does.

## Why
Brief context on why this change is needed, taken only from what the diff, commit messages and code comments actually say. If they give no reason, say plainly what kind of change it is (for example, an automated dependency bump) and stop. Don't guess what a new version, library or release may include.

## Changes
- Bullet points of specific changes amde
- Group related changes together
- Mention any files deleted or renamed
- Each bullet names the file or files it covers (a path or file name) and says what changed in them; every changed file appears in at least one bullet. For a new file, say what it contains.


## Output
Your reply is the PR description itself and nothing else. The first line is `## What` and the last line is the last bullet under `## Changes`. Don't put any sentence before `## What` (no "Here's the PR description"), don't add notes or a sign-off after the list, and don't wrap it in a code fence. `## Changes` contains only bullet lines.
