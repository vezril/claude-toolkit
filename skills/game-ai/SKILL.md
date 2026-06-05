---
name: game-ai
description: Game AI — making NPCs and agents move, decide, and behave believably — distilled from Millington's *AI for Games*, the *Game AI Pro* collection, and Red Blob Games. Covers movement/steering (seek/flee/arrive/pursue/wander/flocking, obstacle/wall avoidance), pathfinding (graphs, BFS/Dijkstra, A* and heuristics, navigation meshes, flow fields, hierarchical pathfinding, path smoothing), decision making (finite & hierarchical state machines, decision trees, behavior trees, utility AI, goal-oriented action planning/GOAP, planning), tactical/strategic AI (influence maps, waypoints, spatial reasoning), sensing/perception and knowledge, and the design view (AI for *fun* and believability, not optimality; difficulty, telegraphing, "artificial stupidity"). Use when designing or implementing enemy/NPC behavior, pathfinding, steering/movement AI, decision systems (FSM/BT/GOAP/utility), or tuning AI difficulty/feel. Builds on game-math (geometry/pathfinding) and pairs with godot (NavigationAgent), game-design, and game-programming-patterns (State/Component).
---

# Game AI

Making agents **move, decide, and behave** in ways that are fun and believable — from **Ian Millington's *AI for Games***, the **Game AI Pro** articles, and **Red Blob Games** (pathfinding). Game AI is not academic AI: the goal is **the player's experience** — believable, beatable, well-telegraphed behavior — not optimal play.

Cross-links: [[game-math]] (vectors/geometry/graphs under steering & pathfinding), [[godot]] (NavigationServer/`NavigationAgent`, navmeshes), [[game-programming-patterns]] (State machines, Component), [[game-design]] (AI difficulty/feel), [[procedural-generation]] (graphs/grids).

Millington's classic structure: **Movement → Decision Making → Strategy**, with **sensing/world-interface** underneath.

## Movement & steering

How an agent physically moves:
- **Kinematic** (set velocity directly) vs **steering** (apply accelerations/forces — Reynolds' steering behaviors).
- **Steering behaviors:** **seek / flee / arrive** (ease in near target), **pursue / evade** (predict the target), **wander**, **path following**, **obstacle avoidance** & **wall avoidance**, **separation / cohesion / alignment** → **flocking/boids** (emergent crowd movement).
- **Combine** behaviors by weighted sum or priority; cap with max speed/acceleration ([[game-math]] vectors, `delta`). Smooth with steering, not teleporting.

## Pathfinding

Getting from A to B through a navigable space (Red Blob's interactive guides are the best intro):
- **Represent the world as a graph** — grid (4/8-neighbor), waypoints, or a **navigation mesh** (navmesh, polygons of walkable area — what 3D engines use).
- **Algorithms:** **BFS** (unweighted), **Dijkstra** (weighted, no goal bias), **A\*** (Dijkstra + a **heuristic** toward the goal — the workhorse). The heuristic must be **admissible** (never overestimate) for optimal paths; Manhattan/Euclidean/octile depending on movement.
- **Many units to one goal:** **flow fields** / **Dijkstra maps** (compute once, every unit follows the gradient) — far cheaper than per-unit A* (Red Blob "tower defense pathfinding").
- **Scale:** **hierarchical pathfinding** (HPA*) for big maps; path **caching**; time-slicing A* across frames.
- **Path smoothing** — raw grid paths look robotic; smooth with line-of-sight ("string pulling"/funnel) or splines ([[game-math]] curves).
- In [[godot]]: `NavigationServer` + `NavigationRegion` + `NavigationAgent2D/3D` give navmesh pathfinding out of the box.

## Decision making

How an agent chooses *what* to do:
- **Finite State Machine (FSM)** — states + transitions (patrol→chase→attack→flee); simple, readable; **hierarchical FSM** and **pushdown** for reuse/return-to-previous ([[game-programming-patterns]] State). Can sprawl into transition spaghetti.
- **Decision Trees** — a tree of conditions → actions; fast, designer-readable.
- **Behavior Trees (BT)** — the modern default for complex NPCs: composable trees of **Sequence / Selector / Parallel / Decorator / Condition / Action** nodes, ticked each frame; scalable, reusable, designer-friendly. (Dominant in AAA.)
- **Utility AI** — score each possible action by a utility function of the world state, pick (or weight-pick) the highest; great for many competing considerations (The Sims, shooters). Smooth, emergent, tunable via curves.
- **GOAP (Goal-Oriented Action Planning)** — agent has goals + actions with preconditions/effects; an A*-like planner finds an action sequence to reach a goal at runtime (F.E.A.R.). Flexible/emergent; heavier to build/debug.
- **Planning / HTN** — hierarchical task networks for richer plans. Use the *simplest* that gives the behavior you need.

## Tactical & strategic AI

- **Influence maps** — a grid of "who controls/threatens what," summed from units; drives positioning, target selection, where-to-flee, RTS strategy.
- **Waypoint tactics / cover points** — annotated positions (cover, sniper spots, choke points) for tactical movement.
- **Spatial reasoning** — line-of-sight, flanking, formation movement.

## Sensing, perception & knowledge

What the agent "knows": vision cones + **line-of-sight** ([[game-math]] visibility), hearing/noise, memory (last-known position), and **honest perception** (the AI should only act on what it could plausibly sense — no omniscience) for fairness and believability. Event-driven sensing (Observer/Event Queue, [[game-programming-patterns]]) over per-frame polling.

## The design view: AI for fun, not optimality

The hardest part of game AI is making it **fun to play against**, not smart:
- **Believability over optimality** — perfect AI is unfun; add human-like imperfection.
- **Telegraphing** — wind-ups/tells so the player can read and counter; AI that's readable feels fair.
- **"Artificial stupidity"** — deliberate mistakes, reaction delays, accuracy caps, so the player can win and feel good.
- **Difficulty** tuned via perception/reaction/accuracy, not just HP. ([[game-design]] flow/difficulty.)
- AI exists to create the intended **experience** — pressure, puzzle, companionship — define that first.

## Anti-patterns

- Per-unit **A\*** every frame for crowds → use **flow fields**/Dijkstra maps; recomputing paths needlessly (cache/time-slice).
- **FSM spaghetti** for complex behavior → use **behavior trees** or **utility**.
- **Omniscient AI** (sees through walls, perfect aim) → feels cheap/unfair; model honest perception + telegraph.
- "Smart" but **unfun** AI (optimal, unreadable) — design for the player's experience, not the AI's win rate.
- Non-admissible A* heuristic (wrong paths) or wrong heuristic for the movement type; raw unsmoothed grid paths.
- Hand-rolling navmesh/pathfinding when [[godot]]'s NavigationServer suffices.
- Reaching for **GOAP/planning** when an FSM/BT would do (over-engineering).

## Always-apply

1. **Movement → decision → strategy**, with honest **sensing** underneath.
2. **A\*** (admissible heuristic) on a graph/navmesh; **flow fields** for many-to-one; **smooth** paths; use [[godot]] navigation.
3. Pick the simplest decision model that works: **FSM → behavior tree → utility → GOAP** as complexity grows.
4. Design AI for **fun & believability** — telegraph, allow mistakes, tune difficulty by perception/reaction, no omniscience.
5. Build on [[game-math]] (vectors/graphs/LOS) and [[game-programming-patterns]] (State/Component/Event Queue).

## Related

- [[game-math]] — vectors, graphs, geometry, line-of-sight under steering/pathfinding.
- [[godot]] — NavigationServer/NavigationAgent, navmeshes, `Area` perception.
- [[game-programming-patterns]] — State (FSM), Component, Event Queue (sensing).
- [[game-design]] — AI difficulty, telegraphing, fun-to-fight; [[procedural-generation]] — graphs/grids.
- Sources: *AI for Games, 3rd ed.* (Ian Millington & John Funge); *Game AI Pro* (ed. Steve Rabin); Red Blob Games (A*, pathfinding).
