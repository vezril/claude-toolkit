# Design: add-archive-skill

## Decisions

**Archive is a move, not a copy.** The component's files are moved verbatim into `archive/<name>/` (git preserves history across the rename). An active component and its archived copy must never coexist — that is the whole point of retirement.

**`RETIRED.md` is the archive's contract.** Every archived component gets one, written by the skill at archive time, with four mandatory fields:

- **What it was** — one paragraph, plus the component type (skill / workflow / script).
- **Why retired** — the actual reason, not boilerplate.
- **Replaced by** — the successor component(s), or "nothing" explicitly.
- **Retired on** — absolute date.

The component's own documentation (its SKILL.md body, references, scripts) rides along unchanged — `RETIRED.md` sits next to it, it does not rewrite it.

**Inert by convention, not mechanism.** Nothing in `archive/` is wired into the plugin manifest, skill discovery, or workflow lookup — the plugin only surfaces `skills/`, `agents/`, and `workflows/`. The skill also removes installed copies (e.g. `~/.claude/skills/<name>/`, `~/.claude/workflows/<name>.js`) so a retired component can't keep firing from a stale install; it reports each removal.

**De-indexing is part of archiving.** The skill removes the component's entries from `README.md` (skill index, workflows section) in the same change. A retired component that still appears in the index is a stale doc — same principle as the SDLC doc-sync rule.

**Scope guard.** The skill archives components of *this* toolkit (or a repo it is pointed at). It refuses to archive a component that other active components still reference (grep for the name first; report referrers instead of proceeding).

## Skill interface

- Arguments: `<component-path> [replaced-by...]` — e.g. `skills/new-scala-service` (or an absolute path such as `~/.claude/skills/new-scala-service` for components living outside the repo), plus optional successor names.
- Interactive gaps (why retired, successor if not given) are asked, not invented.
- Output: the `archive/<name>/` tree, `RETIRED.md`, index edits, and a report of installed copies removed. No commit — shipping stays with git-ship.
