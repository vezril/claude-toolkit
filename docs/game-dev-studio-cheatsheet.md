# Game Dev Studio — One-Page Reference

Quick-reference companion to `game-dev-studio-proposal.md`. ✅ = on your book list · ➕ = recommended add (often free) · 🧩 = already in toolkit.

## Step 0 — Pick an engine (gates everything; gather DOCS not books)
- **Godot 4** (GDScript/C#) — open-source, light, great 2D — *recommended default*
- **Unity** (C#) — biggest ecosystem; books stale fast → Unity Learn
- **Unreal 5** (C++/Blueprints) — AAA fidelity, steepest

## Proposed skills + resources

**Design**
- `game-design` — ✅ *Art of Game Design* (Schell, **start here**) · ✅ *Theory of Fun* (Koster) · ✅ *Game Feel* (Swink) · ✅ *Rules of Play* · ✅ *Challenges for Game Designers* · 🧩 [[ux-design]] for UI
- `game-development` (studio meta) — lifecycle + GDD + "find the fun first"; ✅ *Blood, Sweat, and Pixels* · adapt [[sdlc-orchestration]]

**Technical**
- `game-programming-patterns` — ✅ Nystrom (**free online**) · 🧩 [[design-patterns]]
- `game-engine-architecture` — ✅ Gregory · 🧩 [[software-architecture]], [[operating-systems]]
- `game-math` — ✅ Lengyel · ➕ *3D Math Primer*, Red Blob Games (free)
- `game-graphics` — ✅ *Real-Time Rendering* · ✅ *Book of Shaders* (free)
- `game-ai` — ✅ *AI for Games* (Millington) · ➕ Game AI Pro (free), Red Blob A*
- `game-physics` — ✅ *Game Physics Engine Development* · ➕ Ericson *Real-Time Collision Detection*
- `multiplayer-networking` — ✅ Glazer & Madhav · ➕ Gaffer On Games (free) · 🧩 [[tcp-ip]]/[[network-engineering]]/[[akka]]
- `procedural-generation` — ✅ *PCG in Games* (free PDF) · ➕ Red Blob Games
- `game-audio` — ✅ *The Audio Programming Book* · ➕ FMOD/Wwise docs

**Engine (pick one, gather docs)**
- `godot` (docs.godotengine.org, GDQuest) / `unity` (learn.unity.com) / `unreal` (Epic docs)

**Production**
- `game-production` — ✅ *Blood Sweat & Pixels* + *Press Reset* · ✅ *Indie Game Dev Handbook* · ✅ *Lean Startup* · ✅ *Hooked* ⚠️ (capture with dark-patterns ethics caveat, per [[ux-design]])

## The Studio (mirrors the SDLC team)
- **Lifecycle:** Concept → Prototype (find the fun) → Vertical Slice → Production → Polish/Juice → Ship → Live
- **Central artifact:** the **GDD** (lighter/living vs a PRD)
- **Key twist:** the quality gate is **"is it fun?" → playtesting** = the game-dev version of execution-grounded review; **prototype before you produce**

**Agents (↔ SDLC analog):**
- `game-dev-orchestrator` ↔ [[sdlc-orchestrator]] — drives lifecycle, gates "is it fun?", delegates, HITL
- `game-designer` ↔ [[requirements-analyst]] — GDD, core loop, mechanics, balance
- `game-systems-architect` ↔ [[solution-architect]] — engine choice, architecture, patterns
- `gameplay-programmer` ↔ developer/[[tdd-coach]] — implement mechanics
- `level-designer` ↔ [[story-planner]] — levels/content, PCG
- `playtest-lead` ↔ [[qa-test-architect]] — runs playtests, the empirical "fun" gate
- `technical-artist` (new) — rendering/shaders/juice
- `game-producer` (new) — scope, milestones, avoid crunch, launch
- **Reuse:** [[tdd-coach]], [[clean-code-reviewer]], [[git-and-ci-reviewer]], [[github-actions]], [[ux-design]]

## Build order
1. `game-design` + `game-programming-patterns` + engine docs → orchestrator + game-designer + gameplay-programmer *(design & prototype)*
2. `game-engine-architecture` + `game-math` + `game-ai` + `game-physics`
3. `game-graphics` + `procedural-generation` + `multiplayer-networking` + `game-audio`; `playtest-lead` + `game-producer`
4. `game-production` + existing CI/release agents

## What to send me
1. **The engine choice.**
2. **First buys (cheap/free):** ✅ Schell · ✅ Nystrom (free) · ✅ Millington *AI for Games* · ✅ Gregory
3. Then any skill's book (PDF/EPUB) or docs URL → I build that skill + agent, same as the SDLC/networking clusters.
- **Free, just link me:** gameprogrammingpatterns.com · thebookofshaders.com · redblobgames.com · gafferongames.com · your engine's docs · GDC talks
