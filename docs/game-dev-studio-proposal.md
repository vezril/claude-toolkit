# Game Dev Studio — skills, resources & agent design

A plan to add a **game-development cluster** to `claude-toolkit` and assemble a **Game Dev Studio** — a multi-agent team that mirrors the [[sdlc-orchestration]] / [[sdlc-orchestrator]] pattern, adapted to how games are actually made. Nothing built yet. Synthesized from the *Generalist Programmer* "essential game-dev books" list plus the canonical resources of the field.

---

## The one decision that gates everything: pick an engine

Skills, agents, and roughly half the resources depend on your target engine. Choose **one** to start:

| Engine | Language | Why |
|--------|----------|-----|
| **Godot 4** | GDScript / C# | open-source, lightweight, great 2D + capable 3D; fits a FOSS/indie, solo workflow. *(My default recommendation for you.)* |
| **Unity** | C# | largest ecosystem/jobs, asset store; books go stale fast → lean on Unity Learn. |
| **Unreal 5** | C++ / Blueprints | AAA fidelity (Nanite/Lumen), C++ heavy; steepest. |

The book list explicitly warns **engine books age fast** — for whichever you pick, **gather the official docs, not books**. Everything else below (design, patterns, math, AI, rendering theory) is engine-agnostic and durable.

---

## Proposed skills + the resources to gather

Grouped like the SDLC cluster: design (the "what"), technical (the "how"), and production (ship it). ✅ = the book is on your list; ➕ = recommended addition (often free); 🧩 = already covered by an existing toolkit skill you'd cross-link.

### Design & player experience
**`game-design`** — design theory, the core loop, mechanics, player psychology, "is it fun?"
- ✅ *The Art of Game Design: A Book of Lenses* — Jesse Schell **(top pick — start here)**
- ✅ *A Theory of Fun for Game Design* — Raph Koster
- ✅ *Game Feel* — Steve Swink (juice, control, polish)
- ✅ *Rules of Play* — Salen & Zimmerman (systems framing)
- ✅ *Challenges for Game Designers* — Romero & Schreiber (exercises)
- ✅ *The Design of Everyday Things* — Norman → 🧩 you already have [[ux-design]] for game-UI
- ➕ GDC Vault talks; Game Maker's Toolkit (YouTube)

### Game-dev process (the studio meta)
**`game-development`** (meta / studio orchestration) — the lifecycle (concept → prototype → vertical slice → production → polish → ship), the **GDD**, and "prove the fun before you produce."
- ➕ derive from Schell + *Blood, Sweat, and Pixels* (✅, real production stories) + agile/[[sdlc-orchestration]] adapted for games
- ➕ "the vertical slice" and "find the fun" methodology (GDC talks, Extra Credits)

### Technical / programming
**`game-programming-patterns`** — game loop, update method, component, state, observer, object pool, spatial partition, dirty flag…
- ✅ *Game Programming Patterns* — Robert Nystrom **(top pick; free at gameprogrammingpatterns.com)** → 🧩 builds on [[design-patterns]]

**`game-engine-architecture`** — engine subsystems: memory, rendering, animation, physics, audio, gameplay, the runtime.
- ✅ *Game Engine Architecture* — Jason Gregory (the reference) → 🧩 cross-link [[software-architecture]], [[operating-systems]] (memory/scheduling), [[6502-assembly]] (low-level mindset)

**`game-math`** — vectors, matrices, quaternions, transforms, intersection tests.
- ✅ *Mathematics for 3D Game Programming & Computer Graphics* — Eric Lengyel
- ➕ *3D Math Primer for Graphics and Game Development* — Dunne & Parberry (gentler); ➕ Red Blob Games (visual, free)

**`game-graphics`** (real-time rendering + shaders) — the pipeline, lighting/shadows, PBR, optimization, shader programming.
- ✅ *Real-Time Rendering* (4th) — Akenine-Möller et al. (the "bible")
- ✅ *The Book of Shaders* — Gonzalez Vivo & Lowe (free, GLSL) → 🧩 ties to [[information-theory]] only loosely; mostly its own thing

**`game-ai`** — pathfinding (A*), steering, FSMs, behaviour trees, GOAP, utility AI.
- ✅ *AI for Games* (3rd) — Ian Millington **(top intermediate pick)**
- ➕ *Game AI Pro* series (free articles); Red Blob Games on A*/pathfinding

**`game-physics`** — collision detection/response, rigid bodies, constraints.
- ✅ *Game Physics Engine Development* — Ian Millington
- ➕ *Real-Time Collision Detection* — Christer Ericson (the collision reference)

**`multiplayer-networking`** — client-server, replication, prediction & reconciliation, lag compensation.
- ✅ *Multiplayer Game Programming* — Glazer & Madhav
- ➕ Gaffer On Games (gafferongames.com, free, definitive); Valve's Source netcode articles → 🧩 strong cross-link to your new [[network-engineering]] / [[tcp-ip]] and even [[akka]] (actor model for game servers)

**`procedural-generation`** — levels, quests, narrative, roguelike generation.
- ✅ *Procedural Content Generation in Games* — Shaker/Togelius/Nelson (free PDF online)
- ➕ Red Blob Games (noise, hexes, dungeon gen)

**`game-audio`** — DSP, synthesis, spatial/procedural audio.
- ✅ *The Audio Programming Book* — Boulanger & Lazzarini
- ➕ middleware docs: FMOD / Wwise (what most teams actually use)

### Engine skill (pick one) — gather **docs, not books**
**`godot`** / **`unity`** / **`unreal`**
- Godot → docs.godotengine.org, GDQuest; ✅ *Godot Engine Game Development Projects* (Godot 3 — adapt for 4)
- Unity → learn.unity.com + docs; ✅ *Unity in Action*, *Unity Game Optimization*
- Unreal → dev.epicgames.com/documentation; Unreal Learning

### Production & business
**`game-production`** — scoping, milestones, avoiding crunch/scope-creep, indie marketing & launch.
- ✅ *Blood, Sweat, and Pixels* + *Press Reset* — Jason Schreier (production realities)
- ✅ *The Indie Game Developer Handbook* — Hill-Whittall
- ✅ *The Lean Startup* — Ries (MVP / find-the-fun cheaply)
- ✅ *Hooked* — Nir Eyal ⚠️ **ethics flag:** habit/retention design shades into dark patterns; capture it *with* the critique (design for player value, not compulsion) — same stance as [[ux-design]]'s dark-patterns caveat.

---

## The Game Dev Studio (multi-agent, mirroring the SDLC team)

Same shape as [[sdlc-orchestration]]: an orchestrator drives a lifecycle, delegates to discipline agents, gates each phase, human approves. **The one big adaptation:** in games the quality gate isn't "tests pass" — it's **"is it fun?", and fun is empirical → you must playtest.** Playtesting is the game-dev analog of the SDLC team's *execution-grounded review*. And games are **prototype-first**: prove the fun before producing content.

### Lifecycle (the phases the orchestrator drives)
```
Concept → Prototype ("find the fun") → Vertical Slice → Production → Polish/Juice → Ship → Live/Post-launch
   GDD       playable proto              one slice at        content &      game feel    release   updates
                                          full quality        systems
```
Central artifact = the **GDD** (Game Design Document) — the PRD analog — but lighter and living, because games iterate on feel.

### Agents (map to your SDLC roles)

| Game studio agent | SDLC analog | Role | Skills |
|-------------------|-------------|------|--------|
| **game-dev-orchestrator** | [[sdlc-orchestrator]] | drives the lifecycle, gates phases ("is it fun yet?"), delegates, HITL | game-development, [[agentic-workflows]] |
| **game-designer** | [[requirements-analyst]] | GDD, core loop, mechanics, balance | game-design |
| **game-systems-architect** | [[solution-architect]] | engine choice, code architecture, patterns | game-engine-architecture, game-programming-patterns, [[software-architecture]] |
| **gameplay-programmer** | developer / [[tdd-coach]] | implement mechanics in the engine | engine skill, game-programming-patterns, game-math/physics/ai |
| **technical-artist / shader-engineer** | — (new) | rendering, shaders, game feel/juice | game-graphics |
| **level-designer** | [[story-planner]] | levels/content/encounters, PCG | game-design, procedural-generation |
| **playtest-lead** | [[qa-test-architect]] | runs playtests, measures "fun"/difficulty/retention — the empirical gate | game-design, game-production |
| **game-producer** | — (new) | scope, milestones, avoid crunch, launch/marketing | game-production |

Reuse what you already have: [[tdd-coach]] (engine code is still code), [[clean-code-reviewer]], the language reviewers, [[git-and-ci-reviewer]] + [[github-actions]] (build pipelines), [[ux-design]] (game UI). The networking/[[akka]] skills feed multiplayer.

### Build order (when you're ready)
1. **Foundations:** `game-design` + `game-programming-patterns` (+ your chosen engine docs) + the `game-dev-orchestrator`, `game-designer`, `gameplay-programmer` agents. → enough to design + prototype.
2. **Core tech:** `game-engine-architecture`, `game-math`, `game-ai`, `game-physics`.
3. **Polish & scope-out:** `game-graphics`, `procedural-generation`, `multiplayer-networking`, `game-audio`; `playtest-lead` + `game-producer`.
4. **Ship:** `game-production` + the existing CI/release agents.

---

## What to send me (resource checklist)

**Decide first:** which engine (Godot / Unity / Unreal)?

**Highest-value first purchases** (the article's top picks, mostly cheap/free):
- ✅ *The Art of Game Design* (Schell) · ✅ *Game Programming Patterns* (Nystrom, **free online**) · ✅ *AI for Games* (Millington) · ✅ *Game Engine Architecture* (Gregory)

**Then, per skill** (from the ✅/➕ lists above): *Game Feel*, *Real-Time Rendering* + *Book of Shaders* (free), *Mathematics for 3D Game Programming*, *Game Physics Engine Development* (+ Ericson), *Multiplayer Game Programming* (+ Gaffer On Games, free), *Procedural Content Generation in Games* (free PDF), *The Audio Programming Book*, and the production set (*Blood Sweat & Pixels*, *Indie Game Dev Handbook*, *Lean Startup*, *Hooked*).

**Free/online you can just point me at:** gameprogrammingpatterns.com · thebookofshaders.com · redblobgames.com · gafferongames.com · your engine's official docs · selected GDC talks.

Hand me a skill's resources (book PDF/EPUB or a docs URL) and I'll build that skill + its agent exactly as we did for the SDLC and networking clusters — defensively scoped (the *Hooked* ethics caveat baked in).

---
*Source: Generalist Programmer, "Best Game Development Books in 2026" + the canonical resources of game development. Companion to `docs/sdlc-agent-team-proposal.md`.*
