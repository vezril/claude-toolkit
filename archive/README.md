# Archive

Retired toolkit components, preserved for reference. Nothing in this folder is active:
the plugin only surfaces `skills/`, `agents/`, and `workflows/` — archived components are
not installed, indexed, or invocable.

Every archived component sits in `archive/<name>/` with its original files **verbatim**
plus a `RETIRED.md` recording:

- **What it was** — one paragraph + component type (skill / workflow / script)
- **Why retired** — the actual reason
- **Replaced by** — successor component(s), or explicitly "nothing"
- **Retired on** — absolute date

Components are archived with the `toolkit-archive` skill, which enforces this contract
(and refuses to archive anything an active component still references).
