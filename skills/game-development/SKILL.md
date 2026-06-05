---
name: game-development
description: The game-development lifecycle and how the disciplines fit together — the meta/overview and "studio" orchestration skill for the game-dev cluster, the games analog of sdlc-orchestration. Covers the phases (concept/pre-production → prototype "find the fun" → vertical slice → production → polish/juice → ship → live/post-launch), the central GDD artifact, the prototype-first / find-the-fun-before-you-produce principle, the unique quality gate (playtesting — "is it fun?" — the empirical analog of execution-grounded review), scoping & milestones to avoid crunch and scope-creep, choosing an engine, the disciplines (design, programming, art/tech-art, audio, level design, QA/playtest, production) and how they hand off, and the map to the cluster's skills and the Game Dev Studio agents. Use to orient in game development, plan a project's phases, decide what comes next, sequence prototype→production, or coordinate the discipline agents. Routes to game-design, game-programming-patterns, godot, game-math/graphics/ai/physics, multiplayer-networking, procedural-generation, game-audio, and game-production.
---

# Game Development

The **meta/overview and orchestration** skill for making games — the lifecycle, how the disciplines fit, and how to drive a project from idea to ship. This is the games analog of [[sdlc-orchestration]]: it owns *sequence and process*; the specialist skills own *content*.

Routes to: [[game-design]] (the what/why), [[game-programming-patterns]] / [[godot]] (the how), [[game-math]] / [[game-graphics]] / [[game-ai]] / [[game-physics]] / [[multiplayer-networking]] / [[procedural-generation]] / [[game-audio]] (technical specialties), [[game-production]] (scope/ship/business). Cross-links [[agentic-workflows]] (wiring the studio agents) and reuses the general [[tdd]] / [[clean-code]] / [[git]] disciplines (engine code is still code).

## The lifecycle

```
Concept/Pre-production → Prototype → Vertical Slice → Production → Polish/Juice → Ship → Live/Post-launch
   GDD, core loop,        "find       one slice at     build all     game feel,    release   patches,
   pitch, feasibility      the fun"    full quality     content/systems  bugfix, perf          content, ops
```

1. **Concept / pre-production** — the pitch, the **core loop**, the target experience, feasibility, and the **GDD** ([[game-design]]). Decide the **engine** ([[godot]]) and scope ([[game-production]]).
2. **Prototype — "find the fun."** Build the cheapest thing that tests whether the core loop is *actually fun* (paper/graybox/playable). **Do not proceed until the fun is proven.** This is the defining discipline of game dev: prototype-first.
3. **Vertical slice** — one representative slice built to **shipping quality** (one level/mode with final-quality art, audio, feel) — proves the production bar and the feel before committing to volume.
4. **Production** — build the content and systems at scale: levels ([[procedural-generation]] / [[game-design]]), mechanics ([[game-programming-patterns]] + [[godot]]), AI ([[game-ai]]), physics ([[game-physics]]), rendering/shaders ([[game-graphics]]), audio ([[game-audio]]), multiplayer ([[multiplayer-networking]]).
5. **Polish / juice** — game feel, performance, bugfixing; the difference between "works" and "feels great" ([[game-design]] feel, [[game-graphics]]).
6. **Ship** — release/build/export ([[godot]] export), store, marketing ([[game-production]]).
7. **Live / post-launch** — patches, content updates, community, ops (ties to [[devops]] / [[site-reliability-engineering]] for online games).

## The central artifact: the GDD

The **Game Design Document** is the through-line (the games analog of the PRD — [[requirements-engineering]]): a **living** master doc + feature docs + one-pagers that carry intent across phases. It evolves — games iterate on *feel*, so the GDD is lighter and more fluid than a software PRD. Details change; the prototype is co-equal with the doc. ([[game-design]] for the full GDD structure.)

## The defining principle: find the fun (prototype-first)

Software SDLC locks the spec then builds; **games can't, because fun is discovered, not specified.** You must prototype and play to learn whether the design works. So the lifecycle is **iterative and prototype-driven**: cheap experiments → prove the loop → then produce. Killing a fun-less prototype early is a *success*, not a failure (scope/crunch are the enemies — [[game-production]]).

## The quality gate: playtesting

The game-dev analog of the SDLC team's **execution-grounded review** is **playtesting**. You cannot assert a game is fun, balanced, or learnable — you must put it in front of real players and **observe** (where they struggle, quit, get bored, break it). Every phase gate is a playtest, not a checklist. Instrument for telemetry on live games. ("Is it fun / clear / fair?" answered empirically — never by opinion.)

## The disciplines (and their studio agents)

| Discipline | Skill(s) | Studio agent | SDLC analog |
|------------|----------|--------------|-------------|
| Design | [[game-design]] | game-designer | requirements-analyst |
| Tech architecture | [[game-programming-patterns]], [[godot]], [[software-architecture]] | game-systems-architect | solution-architect |
| Gameplay programming | [[godot]], patterns, [[game-math]]/[[game-physics]]/[[game-ai]] | gameplay-programmer | developer / tdd-coach |
| Art / tech-art | [[game-graphics]] | technical-artist | — |
| Level / content | [[game-design]], [[procedural-generation]] | level-designer | story-planner |
| Audio | [[game-audio]] | (gameplay/tech-art) | — |
| QA / feel | [[game-design]], [[game-production]] | playtest-lead | qa-test-architect |
| Production | [[game-production]] | game-producer | (new) |

The **game-dev-orchestrator** drives the lifecycle, delegates to these, gates each phase on a playtest, and keeps a human in the loop — exactly like the **sdlc-orchestrator** agent (built on [[sdlc-orchestration]]). Reuse the existing **tdd-coach**, reviewers, **git-and-ci-reviewer**, and [[github-actions]] for the code/build side, and [[ux-design]] for game UI.

## Tracks (scope to the project)

- **Game jam / tiny:** skip heavy docs — a one-page concept, prototype, polish, ship in days.
- **Solo / indie:** light GDD, vertical slice, disciplined scope; you wear all hats (lean on the agents).
- **Team / commercial:** full GDD, milestones, the whole discipline set ([[game-production]]).

Match weight to the project; the enemy is **scope creep** — cut features to ship.

## Anti-patterns

- **Producing before proving the fun** (building content on an unfun core loop) — the cardinal sin.
- Skipping the **vertical slice** → discovering the production bar/feel is wrong after building everything.
- Treating the GDD as frozen; designing on paper without prototyping.
- **No playtesting** / "I know it's fun" — fun is empirical.
- Scope creep and **crunch** as a plan ([[game-production]]); polishing endlessly instead of shipping.
- Choosing tech/engine for novelty over fit; over-engineering systems a small game doesn't need.

## Always-apply

1. **Find the fun first** — prototype the core loop and prove it before production.
2. Carry a **living GDD**; build a **vertical slice** to set the quality bar before scaling content.
3. **Gate every phase on playtesting** (the empirical "is it fun?" — the execution-grounded analog).
4. **Scope ruthlessly to ship**; cut features, fight crunch ([[game-production]]).
5. Route work to the right discipline/agent; reuse the general code/build skills ([[tdd]], [[git]], [[github-actions]]).

## Related

- [[game-design]] — the design discipline and the GDD this pipeline carries.
- [[game-programming-patterns]] / [[godot]] — implementing the game.
- [[game-math]] / [[game-graphics]] / [[game-ai]] / [[game-physics]] / [[multiplayer-networking]] / [[procedural-generation]] / [[game-audio]] — the technical specialties.
- [[game-production]] — scoping, milestones, anti-crunch, launch/business.
- [[sdlc-orchestration]] — the software analog this mirrors; [[agentic-workflows]] — wiring the studio agents.
- Sources: synthesized from *The Art of Game Design* (Schell), *Blood, Sweat, and Pixels* (Schreier), industry GDD practice, and agile/SDLC adapted for games.
