---
name: game-programming-patterns
description: Software design patterns for games, distilled from Robert Nystrom's *Game Programming Patterns*. Covers the architecture/performance/dev-speed tension unique to games and the pattern catalog — the Game Loop, Update Method, Component (entity composition / ECS roots), State (finite state machines), Observer, Command (input handling/undo/replay), Event Queue, Service Locator, Flyweight, Type Object, Subclass Sandbox, Bytecode, Prototype, Double Buffer, Data Locality, Dirty Flag, Object Pool, and Spatial Partition — plus a games-eye critique of the GoF patterns (incl. Singleton as an anti-pattern). Use when structuring game code, choosing how to represent entities/behavior/state, decoupling systems, handling input, optimizing a hot path (cache locality, pooling, spatial queries), or picking the right pattern for a gameplay problem. The code-architecture layer of the game-dev cluster; builds on design-patterns and pairs with godot, game-development, and the technical skills.
---

# Game Programming Patterns

Battle-tested **software design patterns for games**, from **Robert Nystrom's *Game Programming Patterns*** (free at gameprogrammingpatterns.com). Where [[design-patterns]] is the Gang-of-Four for general software, this is the games dialect — patterns shaped by the game loop, real-time performance, and designer-driven content.

Cross-links: [[design-patterns]] (the GoF base these revisit), [[godot]] (which builds several of these in — nodes/scenes ≈ Component, signals ≈ Observer, the SceneTree ≈ Game Loop), [[software-architecture]] / [[software-design]] (the general design tier), [[game-development]] (where these are applied), [[functional-programming]] (immutability/data-oriented thinking).

## The central tension

Nystrom frames it up front: game code lives in tension between **good architecture** (decoupled, changeable), **runtime performance** (the frame budget — ~16 ms at 60 fps), and **development speed** (ship the game). Patterns are tools to buy one without sacrificing too much of the others — *and knowing when not to use them* is as important as knowing them. Don't apply a pattern speculatively; apply it when the pain it solves is real ([[design-patterns]]/[[software-design]] restraint).

## The catalog (when to reach for each)

Grouped as in the book. Full one-liners + trade-offs in `references/pattern-catalog.md`.

**Design Patterns Revisited (GoF, for games)**
- **Command** — wrap an action as an object → input remapping, undo/redo, replays, AI issuing orders, queued actions.
- **Flyweight** — share the identical part of many objects (tile/tree/forest data) → massive memory savings.
- **Observer** — let systems react to state changes without coupling (achievements, UI updating on model changes). *(Godot signals are this.)*
- **Prototype** — spawn objects by cloning exemplars → data-driven spawners, monster "breeds."
- **Singleton** — included **as a cautionary tale**: usually an anti-pattern (global state, hidden coupling, untestable); prefer passing dependencies or a Service Locator. *(Godot autoloads are a constrained version.)*
- **State** — finite state machines: behavior that changes with internal state (idle/run/jump/attack) instead of a tangle of booleans; extends to hierarchical & pushdown FSMs.

**Sequencing (control time & order)**
- **Double Buffer** — compute into a back buffer, swap atomically → no tearing/half-updated state (rendering, simulation steps).
- **Game Loop** — the heart: process input → update the world → render, **decoupled from real time** (fixed timestep — see [[multiplayer-networking]]/Fix-Your-Timestep). *(Godot's main loop + `_process`/`_physics_process`.)*
- **Update Method** — each entity gets `update(dt)` called once per frame to advance its own behavior. *(Godot `_process(delta)`.)*

**Behavioral (define behavior, data-driven)**
- **Bytecode** — encode behavior as data run by a little VM → safe, sandboxed, hot-reloadable designer scripting.
- **Subclass Sandbox** — a base class exposes safe primitive ops; subclasses combine them to define behavior.
- **Type Object** — represent "kinds" (monster types, item types) as runtime data, not subclasses → data-driven categories.

**Decoupling**
- **Component** — compose entities from reusable components (position, sprite, physics, AI) instead of deep inheritance — the root of **ECS**. *(Godot nodes/scenes are composition-first.)*
- **Event Queue** — decouple *when* an event is sent from *when* it's handled (input, audio, async messaging).
- **Service Locator** — global access to a service (audio, logging) without hard-coupling to its implementation; a disciplined alternative to Singleton.

**Optimization (the frame budget)**
- **Data Locality** — lay data out for cache friendliness (contiguous arrays, struct-of-arrays) → big speedups on CPU-bound update loops; the gateway to **data-oriented design** / ECS. ([[operating-systems]] caches.)
- **Dirty Flag** — defer expensive recomputation until the result is actually needed (transforms, derived state).
- **Object Pool** — reuse a fixed pool instead of alloc/free per frame (bullets, particles, enemies) → no fragmentation/GC stalls.
- **Spatial Partition** — index objects by position (grid, quadtree, BVH, BSP) for fast collision/range/visibility queries. ([[game-physics]] broad-phase; [[game-math]].)

## How this maps to Godot

[[godot]] bakes in several patterns, so "use the engine's version" is often the answer: **nodes/scenes = Component/composition**, **signals = Observer**, **the SceneTree + `_process`/`_physics_process` = Game Loop/Update Method**, **autoload = (constrained) Singleton/Service Locator**, **resources = Type Object/Flyweight-ish data**. Reach for the hand-rolled pattern when the engine's affordance doesn't fit (e.g. an Object Pool for bullets, a Command stack for undo, a Spatial Partition for a custom collision query).

## Anti-patterns

- Applying patterns **speculatively** (Nystrom's biggest warning) — pattern soup that adds indirection for no real problem.
- **Singleton everywhere** → global mutable state, hidden coupling, untestable; reach for it last.
- Deep **inheritance hierarchies** for entities where **Component** composition fits.
- Allocating per-frame in hot loops (no **Object Pool**) → GC/alloc stutter; ignoring **Data Locality** in the update loop.
- Recomputing derived state every frame instead of a **Dirty Flag**; O(n²) collision checks instead of a **Spatial Partition**.
- Tangled boolean flags where a **State** machine belongs; tight coupling where **Observer**/**Event Queue** would decouple.

## Always-apply

1. Mind the **architecture / performance / dev-speed** trade-off; apply a pattern only when the pain is real.
2. Prefer **composition (Component)** over inheritance; **State machines** over flag tangles; **Observer/Event Queue** to decouple.
3. In hot paths optimize with **Data Locality, Object Pool, Dirty Flag, Spatial Partition** — but measure first.
4. **Use the engine's built-in version** ([[godot]] nodes/signals/loop) before hand-rolling.
5. Avoid **Singleton**; treat patterns as tools, not goals ([[design-patterns]] restraint).

## How to use the reference

- **`references/pattern-catalog.md`** — every pattern with its intent, when-to-use, trade-offs, and Godot equivalent.

## Related

- [[design-patterns]] — the GoF patterns these revisit for games.
- [[godot]] — the engine that implements many of these; where you apply them.
- [[software-architecture]] / [[software-design]] — the general design tier and the "apply only to real complexity" restraint.
- [[game-physics]] (spatial partition / broad-phase), [[game-ai]] (State/behavior), [[operating-systems]] (data locality / caches), [[functional-programming]] (data-oriented thinking).
- Source: *Game Programming Patterns* (Robert Nystrom, free at gameprogrammingpatterns.com).
