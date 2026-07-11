---
name: toolkit-archive
description: "Retire a toolkit component (skill, workflow, or script) by moving it into the repo's archive/ folder with a RETIRED.md that documents what it was, why it was retired, and what replaced it — then de-index it from the README and remove any installed copies under ~/.claude. Use when a component is superseded or obsolete and its content should be preserved for future reference instead of deleted. Refuses to archive a component that active components still reference."
argument-hint: "<component-path> [replaced-by...]   (e.g. skills/new-scala-service new-scala-pekko-service)"
license: MIT
---

# Toolkit archive (retire a component)

Retirement is a **move, not a copy** — the component's files land verbatim in
`archive/<name>/` and disappear from every active surface in the same change. An active
component and its archived copy must never coexist.

## Inputs

- `COMPONENT` — first argument: a repo-relative path (`skills/<name>`, `workflows/<name>.js`)
  or an absolute path for components living outside the repo (e.g.
  `~/.claude/skills/<name>`). If missing, ask which component to retire and stop.
- `REPLACED_BY` — remaining arguments: successor component name(s). If none given, ask —
  "nothing" is an acceptable answer, but it must be the human's answer.
- `REASON` — why it's being retired. Never invent this: if it isn't clear from the
  conversation, ask.

## Step 1 — referrer guard

Search the repo's **active** components for references to the component's name:

```
grep -rn "<name>" skills/ workflows/ agents/ hooks/ scripts/ --include="*" -l
```

Exclude the component's own files and pure-history matches (CHANGELOG-style mentions).
If any active component still references it, **STOP** — report the referrers and do not
move anything. The successors must take over those references first.

## Step 2 — move

- `git mv <component> archive/<name>` when the component is inside the repo (preserves
  history). For an outside-the-repo component (e.g. only in `~/.claude/skills/`), copy the
  tree into `archive/<name>/` instead — that copy IS the preservation; the original is
  removed in Step 4.
- Move files **verbatim**: no reformatting, no "cleanup", no frontmatter edits. The archive
  is a historical record, not a refactor.

## Step 3 — RETIRED.md

Write `archive/<name>/RETIRED.md` with all four fields (none optional):

```markdown
# RETIRED: <name>

- **What it was:** <one paragraph + component type (skill / workflow / script)>
- **Why retired:** <the actual reason>
- **Replaced by:** <successor(s), or explicitly "nothing">
- **Retired on:** <absolute date, YYYY-MM-DD>
```

The component's own documentation rides along unchanged — RETIRED.md sits beside it, it
does not rewrite it.

## Step 4 — de-index and de-install

- Remove the component's entries from `README.md` (skill index, Workflows section). A
  retired component still in the index is a stale doc.
- Remove installed copies so it can't keep firing from a stale install:
  `~/.claude/skills/<name>/`, `~/.claude/workflows/<name>.js` — check both, delete what
  exists, and report each deletion (or "no installed copies found").

## Step 5 — report (no commit)

Summarize: what moved where, the RETIRED.md fields, index edits, installed copies removed.
Leave everything **uncommitted** — shipping is git-ship's job, so the human reviews the
retirement as one diff.

## Guardrails

- Referrer guard is absolute: never archive a component an active component still uses.
- Ask, don't invent: reason and successor come from the human.
- Never edit the archived files themselves; only add RETIRED.md next to them.
- Deleting installed copies under `~/.claude` is the ONLY deletion this skill performs,
  and only for the component being archived.
- No commit, no push, no PR — hand off to git-ship.
