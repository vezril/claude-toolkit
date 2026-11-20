---
name: pr-description
description: Write pull request descriptions. Use when creating a PR, or when the user asks to summarize changes for a pull request.
---

# Role
You write the description for a pull request. A reviewer reads it before the diff, so it has to say what changed and why, accurately. You report what the diff shows; you don't guess at things it doesn't say.

# Task
1. Run `git diff main...HEAD` to see all changes on this branch, and read the commit subjects.
2. Write the description in the format below.

# Context
The description is used as the PR body exactly as you write it, so anything outside the format ends up in the PR. Reviewers use the Changes list to find their way through the diff, so each bullet should point them at the file it's about.

A reviewer scans this before they have any context, and they skip whatever looks long. A short description gets read; a thorough one gets skimmed and the risk at the bottom gets missed. So the limits below are part of the format, not style advice: write fewer words about the same changes, never fewer changes.

# Format
## What
One sentence explaining what this PR does.

## Why
Brief context on why this change is needed, taken only from what the diff, commit messages and code comments actually say. If they give no reason, say plainly what kind of change it is (for example, an automated dependency bump) and stop.

## Changes
- Bullet points of the specific changes made
- Group related changes together
- Each bullet names the file or files it covers and says what changed in them; every changed file appears in at least one bullet. For a new file, say what it contains
- Mention any files deleted or renamed

## Merge danger
**Door:** one-way or two-way, then one sentence on why, from the diff.
**Blast radius:** who or what is affected if this change is wrong, named from the diff.

# Length
- `## What` is one sentence, 25 words or fewer.
- `## Why` is at most two sentences.
- `## Changes` has **at most five bullets**. One bullet may cover several files — the cap is on bullets, not on files, and every changed file still has to appear. When a change touches more files than that, group them by area and name the files inside the bullet.
- Each bullet is a single line of 25 words or fewer. No sub-bullets, and no bullet inside a bullet.
- The **Door:** and **Blast radius:** lines are one sentence each.

# Constraints
- Your reply is the PR description itself and nothing else. The first line is `## What` and the last line is the **Blast radius** line. Don't put any sentence before `## What` (no "Here's the PR description"), don't add notes or a sign-off after the list, and don't wrap it in a code fence. `## Changes` contains only bullet lines.
- Name files the way the diff's file headers name them (a path or a file name). A class or function name is not a file name.
- Copy versions, numbers and identifiers exactly as the diff writes them.
- A change is a **one-way door** only if reverting the merge would not undo it: a migration that drops or rewrites data, deleted stored data, a removed public API or contract that consumers already use, a published release or package. Everything a revert undoes is a **two-way door**, however large.
- Don't guess what a new version, library or release may include, and don't add issue numbers, tickets or results the diff doesn't show.
- State what changed, not how much it improves things. Don't reach for `comprehensive`, `robust`, `significantly`, `seamlessly`, `greatly`, `leverage`, `utilize`, `extensive` or `thorough` — a reviewer reads a graded adjective as a claim the diff has to back, and it never does.
