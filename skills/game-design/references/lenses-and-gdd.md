# Lenses, MDA, balance & the GDD

Working detail for game-design (Schell; Hunicke et al. MDA; the GDD guide).

## A working subset of Schell's Lenses (design questions)

Schell offers 113 "lenses" — each a set of questions to view the design through. You don't run all of them; pick the few that bite. High-value ones:

- **Lens of Essential Experience** — what experience do I want the player to have? What's essential to it? How can the game capture it?
- **Lens of Surprise** — what will surprise the player? Are the rules, story, art, and tech full of pleasant surprises?
- **Lens of Fun** — what parts are fun? what parts need more fun?
- **Lens of Curiosity** — what questions does the game put in the player's mind? how do I make them care?
- **Lens of Flow** — are the goals clear? is challenge matched to skill? is there steady feedback? are there distractions?
- **Lens of the Player** — who are they, what do they like, expect, and how will they feel?
- **Lens of the Elemental Tetrad** — are mechanics, story, aesthetics, technology all reinforcing the theme?
- **Lens of the Core Loop** — what's the repeated action? is it satisfying on its own?
- **Lens of Challenge** — is difficulty ramped well? variety of challenge? a corridor between boredom and frustration?
- **Lens of Reward** — what rewards, how often, are they meaningful, varied, and well-paced?
- **Lens of Skill vs Chance** — the mix of skill and luck right for the audience?
- **Lens of Feedback** — does the player always know what's happening and the result of their actions?
- **Lens of the Toy** — is it fun to play with *before* there's a goal? (game feel — Swink)
- **Lens of Moments / Juiciness** — do actions produce satisfying, responsive feedback?
- **Lens of Economy / Balance** — are the numbers fair? any dominant strategy? feedback loops controlled?
- **Lens of Simplicity/Complexity** — emergent complexity from simple rules, or needless complication?
- **Lens of the Playtester** — what are real players actually experiencing (vs what I intended)?

## MDA & the aesthetics of fun

**Mechanics → Dynamics → Aesthetics.** Designer authors mechanics; player feels aesthetics; dynamics are the emergent runtime behavior in between. Design by deciding the target aesthetic, then the dynamics that produce it, then the mechanics that produce those.

The 8 aesthetics (kinds of "fun"): **Sensation** (pleasure), **Fantasy** (make-believe), **Narrative** (drama), **Challenge** (obstacle course), **Fellowship** (social), **Discovery** (exploration), **Expression** (self-discovery/creativity), **Submission** (pastime/relaxation). Most games target a few; naming them sharpens the design.

## Balance techniques

- **Fairness:** symmetric (same start) vs asymmetric (different but equivalent) balance.
- **Meaningful choices:** every option should be viable in some situation; eliminate **dominant strategies** and **trap options**.
- **Feedback loops:** **positive** (the leader pulls ahead — exciting but can snowball/decide too early) vs **negative** (catch-up/rubber-banding — keeps it close but can feel unfair). Tune deliberately.
- **Risk/reward:** higher risk should pay more; **transitive** (rock beats scissors) vs **intransitive** (rock-paper-scissors) relationships.
- **Numbers:** sources/sinks in the economy, pacing curves, exponential vs linear progression. Prototype with spreadsheets; tune by playtest.
- *Challenges for Game Designers* (Romero & Schreiber): a workbook of non-digital exercises to drill exactly these — do them with paper prototypes.

## The Game Design Document (GDD)

**Principles:** a **living** document (evolves with the project), a **Master Document + Feature Documents** (not one monolith), and **not a substitute for a prototype**. Over-document *intent*; expect details to change. Scale the rigor to the team (AAA → all docs; indie/solo → a subset).

**The 9-step structure (Ostap Dovbush / Ubisoft), 5 essential + 4 supporting:**

*Essential:*
1. **Director's Vision** — one page, the north star. Chapters: Stakeholders · Elevator pitch · User stories · Requirements (**Gold/Silver/Bronze** quality tiers) · Features · Constraints.
2. **One-Pager** — the most useful info on a single scannable page; one per feature (a feature set typically yields 10–15 one-pagers).
3. **Prototype Requirement Document** — everything needed to build a playable prototype to compare candidate features.
4. **Creative Brief** — an expanded one-pager once the prototype exists; ~20–30 slides. Chapters: Overview · Gameplay & Rules · UI · Progression/Formulas/Balance · Summary & Known Pros/Cons · References.
5. **Feature Document** — the detailed, multi-owner doc (programmers add implementation, level designers add maps); include a **Backlog/Future** chapter to preserve the original vision.

*Supporting (AAA; pick as needed):*
6. **Levels of Quality (LoQ)** — implementation order in 5 levels: **L0** core mechanic/reuse prototype → **L1** main mechanics + partial UI → **L2** feature-ready + final UI on main widgets → **L3** supportive (telemetry, narrative, SFX/VFX/UI) → **L4** final polish/shippable tuning.
7. **UX/UI Document** — mostly visual (Figma): UI flow, widget states, non-UI feedback (VFX/SFX/haptics). ([[ux-design]])
8. **Feature Sign-Off (FSO)** — a table, one line per statement, each *implementable by a programmer and validatable by a tester* (e.g. "Smoke bomb lasts [5 s]"). The acceptance-criteria analog → feeds playtesting.
9. **Narrative/Localization** — UI screenshots + text + localization constraints; player-facing vs dev-facing text.

**Lightweight default (indie/solo):** Director's Vision (1 page) + a one-pager per major feature + a prototype-requirement list + an FSO-style checklist for the playtest gate. Keep it in Markdown/Obsidian; let it evolve.
