# Using the Game Dev Studio

A practical playbook for taking a game from idea to ship with the `claude-toolkit` Game Dev Studio — the skills, the agents, the lifecycle, and the principles. Built to mirror `using-the-sdlc-dev-team.md`, adapted to how games are actually made. Designed for an Obsidian vault; the `[[links]]` map to the skills/agents. Engine: **Godot**.

---

## The cast

**Skills** (the disciplines the agents draw on):

| Skill | Owns | One-liner |
|-------|------|-----------|
| [[game-development]] | the lifecycle | phases, find-the-fun-first, **playtesting as the gate** |
| [[game-design]] | the *what & why* | core loop, mechanics, balance, game feel, the GDD |
| [[game-programming-patterns]] | code architecture | game loop, component, state, object pool… (Nystrom) |
| [[godot]] | the engine | nodes/scenes/signals, GDScript, 2D/3D, subsystems |
| [[game-math]] | the math | vectors, transforms, quaternions, intersection, curves |
| [[game-graphics]] | rendering & shaders | the pipeline, PBR, shaders, juice, perf budget |
| [[game-ai]] | NPC behavior | steering, pathfinding (A*/navmesh), FSM/BT/utility/GOAP |
| [[game-physics]] | motion & collision | integration, broad/narrow phase, impulse response |
| [[multiplayer-networking]] | netcode | UDP, the 3 models, prediction/reconciliation |
| [[procedural-generation]] | content gen | noise/Voronoi/WFC/grammars, seeds, validation |
| [[game-audio]] | sound & music | DSP, spatial audio, adaptive music, buses |
| [[game-production]] | ship it | scope, milestones, anti-crunch, launch, ethics |

**Agents** (the studio — they apply the skills):

| Agent | Role | Produces |
|-------|------|----------|
| [[game-dev-orchestrator]] | director/producer | sequences the lifecycle, gates on playtests, delegates |
| [[game-designer]] | designer | the GDD, core loop, mechanics, balance |
| [[game-systems-architect]] | tech lead | engine choice, code architecture, patterns |
| [[gameplay-programmer]] | dev | mechanics in Godot (writes & runs code) |
| [[level-designer]] | level/content | levels, pacing, encounters, author-vs-PCG |
| [[playtest-lead]] | QA / fun gate | playtests, telemetry, go/no-go (+ code QA) |
| [[technical-artist]] | tech art | shaders, VFX, juice, rendering, graphics perf |
| [[game-producer]] | production | scope, milestones, launch/marketing, ethics |

**Reused from the rest of the toolkit:** [[tdd-coach]], [[clean-code-reviewer]], the language reviewers, [[git-and-ci-reviewer]] + [[github-actions]] (engine code is still code), [[ux-design]] (game UI), and the networking/[[akka]] skills for multiplayer servers.

---

## The lifecycle at a glance

```
   CONCEPT      →   PROTOTYPE     →   VERTICAL SLICE  →   PRODUCTION   →   POLISH    →   SHIP   →  LIVE
 (pre-prod)        "find the fun"     one slice at         build all       feel/juice,   release   patches,
  GDD, core         playable proto     shipping quality     content/        perf, bugfix            content,
  loop, engine                                              systems                                  ops
        └──────── orchestrated by game-dev-orchestrator · every gate is a PLAYTEST · human approves ────────┘
```

**The one rule that makes games different from the SDLC pipeline:** you can't lock a spec and build — **fun is discovered, not specified.** So the lifecycle is *prototype-first*: prove the core loop is fun before you produce content, and **gate every phase on a playtest**, not a checklist. The GDD is the central artifact (the games' PRD), but it's lighter and living.

---

## How to invoke it (Claude Code)

With the plugin installed (`/plugin install claude-toolkit@vezril-toolkit`):

- **Let it delegate** — *"take this game idea through to a prototype"* pulls in the orchestrator; *"design the core loop for X"* pulls in the game-designer.
- **Or call an agent by name** — *"have the game-systems-architect plan the Godot architecture,"* *"use the technical-artist to write a hit-flash shader,"* *"playtest-lead: is this loop fun?"*
- **Skills auto-trigger** on topic (writing a shader pulls in [[game-graphics]] + [[godot]]).
- **One workflow per chat / fresh context per phase**; load only that phase's artifacts.

---

## The workflow, step by step

### Phase 1 — Concept (pre-production)
Define the idea before building.
- **Agents:** [[game-designer]] (core loop, GDD) + [[game-producer]] (scope, engine = Godot, budget/runway).
- **Skills:** [[game-design]] (the Lenses, MDA), [[game-development]] (lifecycle).
- **Output:** a living **GDD** (director's vision + one-pagers), the core-loop concept. **Gate:** the concept is clear and *worth prototyping* — **you approve**.

### Phase 2 — Prototype → "find the fun" *(the make-or-break gate)*
Build the cheapest thing that tests whether the core loop is fun.
- **Agents:** [[gameplay-programmer]] builds a rough playable; [[playtest-lead]] runs a playtest and judges fun.
- **Skills:** [[godot]], [[game-programming-patterns]], [[game-math]].
- **Output:** a playable prototype + playtest findings. **Gate: is the core loop actually fun?** Proven by **real play**, not opinion. **Do not proceed until fun is proven** — killing an unfun prototype here is a *win*.

### Phase 3 — Vertical slice
Build one representative slice at *shipping quality* to set the bar.
- **Agents:** [[game-systems-architect]] (tech design + ADRs), [[gameplay-programmer]], [[technical-artist]] (final-quality art/feel), [[game-designer]] (tuning).
- **Skills:** [[game-programming-patterns]], [[godot]], [[game-graphics]], [[game-physics]], [[game-ai]].
- **Output:** one polished level/mode. **Gate:** the slice proves the quality bar and the feel — playtested — **you approve** before scaling content.

### Phase 4 — Production
Build the content and systems at scale.
- **Agents:** [[level-designer]] (levels/content, author-vs-[[procedural-generation]]), [[gameplay-programmer]] (mechanics, [[game-ai]], [[game-physics]]), [[technical-artist]] (VFX/shaders), + [[game-audio]] for sound/music; [[multiplayer-networking]] if online.
- **Reuse:** [[tdd-coach]] + reviewers for the code; [[git-and-ci-reviewer]] + [[github-actions]] for builds.
- **Gate:** content playtests clean (clear, fair, right difficulty, bug-free P0s) — recurring playtests with [[playtest-lead]].

### Phase 5 — Polish / juice
Game feel, performance, bugfixing.
- **Agents:** [[technical-artist]] (juice: screen shake, hit-stop, particles, easing; perf budget), [[game-designer]] (feel tuning), [[playtest-lead]].
- **Skills:** [[game-design]] (feel), [[game-graphics]] (perf).
- **Gate:** it *feels* great and holds the frame budget — playtested.

### Phase 6 — Ship
- **Agent:** [[game-producer]] — [[godot]] export, storefront, pricing, marketing/wishlists, launch.
- **Gate:** release-ready (gold); **you approve** the launch.

### Phase 7 — Live / post-launch
Patches, content, community; for online games, ops via [[devops]] / [[site-reliability-engineering]].

---

## Pick the track (scope to the project)

| Track | When | Process |
|-------|------|---------|
| **Game jam / tiny** | days | one-page concept → prototype → polish → ship; skip heavy docs |
| **Solo / indie** | the usual | light GDD, vertical slice, ruthless scope; lean on the agents (you wear all hats) |
| **Team / commercial** | bigger | full GDD, milestones, all disciplines ([[game-production]]) |

The enemy is **scope creep** — cut features to ship. A shipped B+ beats an unshipped A+.

---

## The principles that make it work

1. **Find the fun first.** Prototype the core loop and prove it's fun *before* producing content.
2. **Playtesting is the gate.** Fun/clarity/difficulty/fairness are verified by **real players observed**, never asserted — the game-dev analog of execution-grounded review.
3. **Artifacts drive state.** Where are we? = GDD? prototype? slice? content? — not chat history.
4. **Build a vertical slice** to set the quality bar before scaling content.
5. **Scope ruthlessly; fight crunch.** Cut to ship; crunch is a planning failure.
6. **Use the engine's affordances** ([[godot]] nodes/signals/`_physics_process`) before hand-rolling; reach for a [[game-programming-patterns]] pattern only on real pain.
7. **Design ethically** — no dark patterns / predatory monetization ([[game-production]], [[ux-design]]).

---

## A worked example (solo/indie track)

> *"A fast 2D roguelike: dash through rooms, kill, loot, descend."*

1. **Concept** — [[game-designer]]: core loop = *enter room → dash/attack → clear → loot → next*; GDD one-pager; non-goal "no meta-progression in v1." [[game-producer]]: scope to ~10 enemy types, procedural floors, 4-week prototype. *You approve.*
2. **Prototype** — [[gameplay-programmer]] builds dash + one enemy + one room in [[godot]]; [[playtest-lead]] runs it: **is the dash-attack loop fun?** If yes → proceed; if not → tune or kill. *(The whole project hinges here.)*
3. **Vertical slice** — [[game-systems-architect]] (object pool for bullets/enemies, state machine for the player, ADR on save format); [[technical-artist]] (hit-stop, screen shake, dash trail — the *juice* that makes it feel good); one floor at shipping quality. *You approve the bar.*
4. **Production** — [[level-designer]] designs the floor archetypes and picks **procedural** room layout ([[procedural-generation]]: seeded BSP + validation that floors are completable); [[gameplay-programmer]] builds the enemy roster ([[game-ai]]: steering + simple FSM) and combat ([[game-physics]]); [[game-audio]] adds adaptive combat music. [[playtest-lead]] tests difficulty/clarity each build; [[tdd-coach]] + reviewers keep the code clean.
5. **Polish** — [[technical-artist]] + [[game-designer]] tune feel and frame budget; final playtest.
6. **Ship** — [[game-producer]]: Steam page + wishlists (from day one!), demo for Next Fest, export, launch. *You approve.*

---

## Cheat sheet

- **Start:** *"Use the game-dev-orchestrator to take `<idea>` to a prototype."*
- **Design:** *"game-designer: design the core loop + GDD for `<X>`."*
- **Architecture:** *"game-systems-architect: plan the Godot architecture for `<X>`."*
- **Build a mechanic:** *"gameplay-programmer: implement `<mechanic>` in Godot."*
- **Levels:** *"level-designer: design the floors / pick author-vs-procedural."*
- **Juice/shaders:** *"technical-artist: add `<effect>` / write a `<shader>`."*
- **Is it fun?:** *"playtest-lead: plan a playtest for `<feature>` and give a go/no-go."*
- **Ship it:** *"game-producer: scope/milestones + a launch plan."*
- **Always:** find the fun first · gate on playtests · fresh chat per phase · scope to ship · juice it · ethical monetization.

---

*Source: the `claude-toolkit` game-dev skills & agents (Godot; built from Schell, Nystrom, Millington, Lengyel, Akenine-Möller, Glazer & Madhav, Gaffer On Games, Red Blob, and more). Companion to `docs/using-the-sdlc-dev-team.md`, `docs/game-dev-studio-proposal.md`, and `docs/game-dev-studio-cheatsheet.md`.*
