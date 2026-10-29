# Load-bearing map: grilling (v2, upstream verbatim)

Every instruction in the certified `skills/grilling/SKILL.md`, the criterion it serves, and what the
runs show. "Guard" means no run of either version ever failed it, so the evidence can't show the
instruction caused anything, only that a regression would be caught.

| Instruction | Criterion | Evidence |
|---|---|---|
| Interview relentlessly until a shared understanding; map a design tree | (framing) | not separately measurable |
| Work in rounds; ask the whole **frontier** (decisions whose prerequisites are settled) | frontier | v1 → v2: frontier 8/12 → 12/12 (Sonnet), 6/12 → 12/12 (Haiku) |
| Round format: numbered ❓ question with a ➡️ recommended answer | format | v1 → v2: 0/12 → 12/12 on both |
| Word each question so "yes" accepts the recommendation | (none) | **not measured** |
| A question depending on another open question belongs to a later round | frontier | same flip as above; the s2 misses (1 per model) are this rule broken once |
| Facts are the agent's job; don't ask the user for anything you can look up | facts | **guard**: 9/9 in every run of v1 and v2 |
| Dispatch a subagent for facts, don't block | (none) | **not measured**: no Task tool in the eval |
| Done when the frontier is empty; don't act until the user confirms | hold | **guard** for v2 (12/12); v1 missed once, a scorer false positive since fixed |
