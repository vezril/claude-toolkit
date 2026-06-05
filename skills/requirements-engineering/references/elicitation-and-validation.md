# Elicitation methods & validation

How to pull requirements out of stakeholders, and how to check the result. Adapted from the BMAD advanced-elicitation registry (MIT) and Definition-of-Ready practice.

## Running an elicitation session

1. State the goal and the current draft (if any).
2. Pick **2–3 methods** that fit (don't run the whole list); apply them.
3. Capture new requirements, risks, and **open questions** as you go.
4. Re-draft; offer to reshuffle methods or proceed.

Don't try to elicit everything at once — iterate, and let later phases (correct-course) refine.

## Method catalog (pick what fits)

**Drilling to the real need**
- **5 Whys** — repeatedly ask "why" to get from symptom to root requirement.
- **Jobs-to-be-Done interview** — "what progress are you hiring this to make?" Reframes features as outcomes.
- **Socratic questioning** — challenge the assumption behind each stated need.

**Exploring the option space**
- **Tree / Graph of Thoughts** — branch alternative interpretations/solutions before committing.
- **SCAMPER** — Substitute/Combine/Adapt/Modify/Put-to-other-use/Eliminate/Reverse to generate variants.
- **First principles** — strip to fundamentals, rebuild.

**Stress-testing**
- **Pre-mortem** — "it's a year later and this failed — why?" Surfaces risks and hidden/non-functional requirements.
- **Inversion** — state what would guarantee failure; avoid it.
- **Red team / Blue team** — one side attacks the requirement set, the other defends.
- **Steelmanning** — argue the strongest version of an opposing view.
- **Six Thinking Hats** — rotate perspectives (facts, feelings, risks, benefits, creativity, process).

**Framing & communication**
- **Working-Backwards / PRFAQ** — write the launch press release + FAQ first; if it doesn't sound compelling, the concept needs work.
- **Minto Pyramid** — structure the ask top-down (answer first, then support).

## Validation / Definition-of-Ready checklist

Run with a **separate, stronger reviewer model** where possible (avoid self-confirmation).

**PRD/SRS level**
- [ ] Every non-functional requirement is **measurable** and has a **verification method**.
- [ ] Every functional requirement is **singular, unambiguous, testable**, and has a **stable ID**.
- [ ] **Non-goals** present; scope is bounded.
- [ ] Success metrics map to FRs; each has a **counter-metric**.
- [ ] **Assumptions** and **open questions** are surfaced, not silently resolved.
- [ ] Internally **consistent** — no FR contradicts a constraint or another FR.
- [ ] **Traceable** — needs → FRs → (later) design & tests.

**Story level (Definition of Ready)**
- [ ] Follows role-action-benefit; meets **INVEST**.
- [ ] **Acceptance criteria** are explicit and testable (Given/When/Then or checklist).
- [ ] Small enough to finish in a sprint; dependencies identified.
- [ ] References the source FR(s)/CAP(s).

**Output of validation:** an alignment report — what passes, what's mismatched, and a percentage/priority view — feeding the implementation-readiness gate in [[sdlc-orchestration]].
