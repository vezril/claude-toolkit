# Tasks: add-merge-skill

## 1. Skill

- [x] 1.1 `skills/merge/SKILL.md` — the train per design: PR resolution, absolute checks gate, merge + verify + sync, version proposal/confirmation + tag on merged main, archive candidate detection + `openspec archive -y` + bookkeeping landing (PR+merge under train authorization / direct push), skips, the per-merge report; strict-YAML frontmatter with `argument-hint: "[pr] [vX.Y.Z|major|minor|patch] [--no-tag] [--no-archive]"`

## 2. Wiring + verification

- [x] 2.1 README: index under *Toolkit maintenance*; note the composition (git-ship gets changes to the gate, merge takes them from it)
- [x] 2.2 Strict-YAML check across all frontmatters
- [x] 2.3 Live dry-run of the resolution logic (read-only): point the skill's PR/change/version detection at this repo's current state and confirm it identifies the right PR, next version, and archive candidate without acting
- [ ] 2.4 Ship via git-ship (gated) — and close the loop by running `/merge` itself on that PR as its first live train
