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
Brief context on why this change is needed.

## Changes
- Bullet points of specific changes amde
- Group related changes together
- Mention any files deleted or renamed


## Output
Your reply is the PR description itself and nothing else. The first line is `## What` and the last line is the last bullet under `## Changes`. Don't put any sentence before `## What` (no "Here's the PR description"), don't add notes or a sign-off after the list, and don't wrap it in a code fence. `## Changes` contains only bullet lines.
