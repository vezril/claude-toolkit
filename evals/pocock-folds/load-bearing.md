# Load-bearing map: the Pocock folds

Each fold maps to the case that measures it and the evidence (target, Haiku / Sonnet, v1 → v2, from
`iteration-log.md`). A fold that no case moves is listed as not proven rather than given a mapping.

| Fold | Where | Case | v1 → v2 | Load-bearing? |
|------|-------|------|---------|---------------|
| Dependency categories; an owned remote gets a port and an in-memory adapter | `software-design/references/seams-and-testing.md` | sd-01 | Sonnet 1/3 → 3/3 | yes |
| Replace, don't layer: delete the old wrapper's tests once the boundary test exists | same | sd-01 | (same case, the "delete" alternative) | yes |
| One adapter is a hypothetical seam: don't add the trait yet | same | sd-02 | 2/3 → 3/3, 2/3 → 3/3 | yes |
| The deletion test | same | none | not measured | not proven |
| Design it twice: three designs, compared on depth, locality and seam | same, plus the pointer in `SKILL.md` item 7 | sd-03 | 0/3 → 2/3, 0/3 → 3/3 | yes |
| Mock only at system boundaries | `tdd/SKILL.md` | t-02 (guard) | guard 2/3 → 3/3 on Haiku | yes, as a guard |
| Tautological assertion anti-pattern | `tdd/SKILL.md` | t-01 | 0/3 → 3/3, 2/3 → 3/3 | yes |
| Horizontal slicing anti-pattern | `tdd/SKILL.md` | t-03 | 3/3 → 3/3 on both | not proven (v1 already passed) |
| Glossary *Avoid* aliases | `domain-driven-design/SKILL.md` | ddd-01 | 0/3 → 3/3 on both | yes |
| ADR three-test gate (hard to reverse, surprising, a real trade-off) | `software-architecture/SKILL.md`, `references/decisions-and-diagramming.md` | arch-01, arch-02 | 6/6 → 6/6 on both | not proven (v1 already declined the trivial ADR) |
| Short-form ADR | `references/decisions-and-diagramming.md` | arch-02 | 3/3 → 3/3 | not proven |

7 of 11 folds are measured moving a case. The four that aren't are kept because they're small and
the suites show they cost nothing (guards 15/15 on v2), but I'm not claiming them.
