# Tasks: add-archive-skill

## 1. Skill

- [x] 1.1 Create `skills/toolkit-archive/SKILL.md` (strict-YAML frontmatter; body per design: move → RETIRED.md → de-index → remove installed copies → report; guardrails: referrer check, ask-don't-invent, no commit)

## 2. Repo wiring

- [x] 2.1 Create `archive/` with a short `archive/README.md` stating the convention (inert, RETIRED.md contract)
- [x] 2.2 Update root `README.md`: Layout section gains `archive/`; skill index gains `toolkit-archive`

## 3. Verify

- [x] 3.1 All SKILL.md frontmatters still pass strict YAML parse
- [x] 3.2 Dry-run the skill against a throwaway dummy component in a scratch copy; confirm RETIRED.md fields, de-indexing, and the referrer guard
- [x] 3.3 Ship via git-ship (gated)
