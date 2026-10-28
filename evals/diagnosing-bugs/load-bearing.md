# Load-bearing map: diagnosing-bugs (v3)

The certified `skills/diagnosing-bugs/SKILL.md` is upstream plus one measured sentence (marked
**added**); `scripts/hitl-loop.template.sh` is upstream byte for byte. Each instruction, the criterion
it serves, and what the runs show (three samples per version; each sample runs each case once).
"Guard": no run of any version failed it.

| Instruction | Criterion | Evidence |
|---|---|---|
| Read GLOSSARY.md and ADRs when exploring | (none) | **not measured** (the fixture has none; both models looked) |
| Redact every secret; build loops against env vars | redact | v1 Haiku quoted the API key once in 3 samples; 0 in v2/v3 |
| Phase 1: build a tight, red-capable loop before any theory | loop-first | v1: Sonnet 3/9 (edited before running anything on d-02 and d-03 in every sample), Haiku 8/9 → v2 and v3: 9/9 on both models |
| Phase 1 ways to build a loop; tighten it; non-deterministic bugs: raise the reproduction rate | loop-first, regression | Sonnet v2 built a 40-seed loop for d-02 in every sample (read in the replies) |
| When you can't build a loop, stop and ask | (none) | **not measured**: every case is loopable |
| Phase 2: reproduce and minimise | (none) | **not measured** directly |
| Phase 3: 3–5 ranked falsifiable hypotheses, shown before testing | (none) | **not measured** (single-turn, no user to show them to) |
| Phase 4: one variable at a time; tagged `[DEBUG-…]` logs; perf branch: measure first | measured, clean | measured: v1 Sonnet skipped the timing once; 3/3 since. clean: **guard** (4/4 in every sample of every version) |
| Phase 5: regression test before the fix, at a correct seam | regression | v1 Sonnet 0/9, Haiku 4/9 → v2 6/9 on both (all misses d-02) |
| **added** the test goes red on every run; pin a non-deterministic bug's seed/order/clock; the flaky test is the symptom | regression | v2 → v3: d-02 0/3 → 3/3 (Haiku), 0/3 → 2/3 (Sonnet) |
| Phase 6: cleanup checklist; state the correct hypothesis in the commit/PR | clean, cause | clean: **guard**; cause: **guard** (4/4 everywhere, every version) |
