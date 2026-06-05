# Game Programming Patterns — full catalog

Each pattern: intent · when to use · trade-off · Godot equivalent. (Nystrom, *Game Programming Patterns*.)

## Design Patterns Revisited
- **Command** — encapsulate a call (+ receiver/args) as an object. *Use:* input remapping, undo/redo, replays, AI actions, action queues. *Trade:* more objects/indirection. *Godot:* `Callable`/custom command objects.
- **Flyweight** — split intrinsic (shared) from extrinsic (per-instance) state; share the intrinsic. *Use:* tiles, vegetation, particles, anything with many near-identical instances. *Trade:* indirection to the shared data. *Godot:* shared `Resource`/`Mesh`/`Material`; MultiMesh.
- **Observer** — subject notifies subscribers on change, no direct coupling. *Use:* UI reacting to model, achievements, decoupled systems. *Trade:* can obscure control flow; lifetime/dangling-listener bugs. *Godot:* **signals** (first-class in 4.x).
- **Prototype** — clone an exemplar to make new objects; data describes spawns. *Use:* spawners, monster breeds, data-driven content. *Trade:* clone semantics (deep vs shallow). *Godot:* `Scene.instantiate()`, `duplicate()`, packed scenes as prototypes.
- **Singleton** — one global instance. *Nystrom's verdict:* usually an **anti-pattern** — global mutable state, hidden coupling, concurrency/test pain. *Prefer:* dependency injection or Service Locator. *Godot:* **autoload** (constrained; not a true singleton).
- **State** — encapsulate state-specific behavior; transitions swap the active state object. *Use:* character/AI behavior (idle/walk/jump/attack), menus, parsers. *Extends:* hierarchical FSM, pushdown automaton (state stack). *Trade:* many state classes. *Godot:* a state node/script per state, or `AnimationTree` state machine.

## Sequencing
- **Game Loop** — `while running: input(); update(dt); render()`, decoupled from real time. *Variants:* fixed update + variable render (interpolate) — see Fix-Your-Timestep ([[multiplayer-networking]]). *Godot:* engine main loop + `_process`/`_physics_process`.
- **Update Method** — each object has `update(dt)` called per frame to advance itself. *Trade:* order-of-update dependencies; objects modified mid-iteration. *Godot:* `_process(delta)` / `_physics_process(delta)`.
- **Double Buffer** — write to a back buffer, swap atomically so readers never see partial state. *Use:* rendering, cellular-automata/sim steps. *Trade:* 2× memory.

## Behavioral
- **Bytecode** — define behavior as data executed by a VM/interpreter. *Use:* spells/abilities/AI scripted by designers without recompiling, sandboxed & moddable. *Trade:* you're building a language — significant effort; debugging the VM. *Godot:* often unnecessary (GDScript is already the scripting layer); reserve for sandboxed user/mod scripting.
- **Subclass Sandbox** — base class provides protected primitive ops; subclasses implement behavior by combining them. *Use:* many similar behaviors (abilities, enemies) sharing a controlled toolkit. *Trade:* base-class coupling.
- **Type Object** — model "types" as instances of a Type class (data), not subclasses. *Use:* monster/item/tile types defined in data, designer-editable. *Trade:* less compile-time checking. *Godot:* custom `Resource` types as data definitions.

## Decoupling
- **Component** — an entity is a bag of components (transform, sprite, body, AI), each owning one domain. *Use:* avoid deep inheritance, mix-and-match behavior — the basis of **ECS**. *Trade:* inter-component communication; data layout. *Godot:* **nodes/scenes** (composition-first) — this is Godot's whole model.
- **Event Queue** — decouple sending from processing by queuing events. *Use:* input, audio requests, async cross-system messaging, deferred work. *Trade:* latency, ordering, queue lifetime/ownership. *Godot:* `call_deferred`, a custom queue, or signals + a buffer.
- **Service Locator** — a global provides access to a service without hard-coupling to its concrete class. *Use:* audio, logging, platform services. *Trade:* still global access (a tamed Singleton); register/null-service discipline. *Godot:* an autoload service registry.

## Optimization (measure first)
- **Data Locality** — arrange data contiguously / struct-of-arrays so the cache stays hot in tight loops. *Use:* the per-frame update of many entities (CPU-bound). *Trade:* harder code, less OO. *Gateway to* data-oriented design / ECS. ([[operating-systems]] caches.)
- **Dirty Flag** — mark derived data stale on change; recompute lazily only when read. *Use:* world transforms, derived geometry, expensive aggregates. *Trade:* flag-management bugs.
- **Object Pool** — preallocate and reuse a fixed set; "free" returns to the pool. *Use:* bullets, particles, enemies, anything spawned/destroyed frequently. *Trade:* fixed capacity; stale state on reuse (must reset). *Godot:* a pool node/array; reuse instances instead of `queue_free()`+`instantiate()`.
- **Spatial Partition** — store objects in a structure keyed by position (uniform **grid**, **quadtree**/octree, **BVH**, **BSP**, k-d tree). *Use:* collision broad-phase, range/nearest queries, culling, AI perception. *Trade:* structure maintenance as objects move. ([[game-physics]], [[game-math]].)

## Choosing
Start with what [[godot]] gives you (nodes=Component, signals=Observer, loop/`_process`=Game Loop/Update). Add a hand-rolled pattern only when you hit its specific pain: undo/replay→Command; many identical objects→Flyweight; per-frame spawn churn→Object Pool; slow spatial queries→Spatial Partition; tangled flags→State; recompute storms→Dirty Flag; CPU-bound entity loop→Data Locality. Never add a pattern without the problem.
