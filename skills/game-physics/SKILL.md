---
name: game-physics
description: Real-time game physics, distilled from Millington's *Game Physics Engine Development* and Ericson's *Real-Time Collision Detection*. Covers numerical integration of motion (Euler, semi-implicit/symplectic Euler, Verlet, RK4) and the fixed-timestep loop, particle and rigid-body dynamics (forces, mass, momentum, torque, inertia tensors, angular velocity), collision detection in two phases (broad phase via spatial partitioning/AABB sweep-and-prune/BVH; narrow phase via SAT, GJK, sphere/AABB/OBB/capsule tests, contact generation), collision response (impulses, restitution/bounciness, friction, penetration resolution), constraints and joints, springs/dampers, and stability/tuning (the importance of a fixed timestep, determinism, sleeping bodies). Use when implementing or debugging movement/collision/physics, choosing an integrator, building collision detection or response, tuning bounciness/friction, or deciding when to use the engine's physics vs custom. Builds on game-math (vectors/geometry/intersection) and pairs with godot (RigidBody/CharacterBody/Area, _physics_process) and multiplayer-networking (deterministic/fixed-step sim).
---

# Game Physics

Simulating **motion and collision** in real time — from **Ian Millington's *Game Physics Engine Development*** (building a physics engine from scratch) and **Christer Ericson's *Real-Time Collision Detection*** (the collision reference). Even when you use an engine's physics, knowing the model is what lets you tune and debug it.

Cross-links: [[game-math]] (vectors, geometry, intersection tests — the substrate), [[godot]] (`RigidBody`/`CharacterBody`/`StaticBody`/`Area`, `_physics_process`, the built-in solver), [[game-programming-patterns]] (Spatial Partition for broad phase; fixed Game Loop), [[multiplayer-networking]] (deterministic fixed-step simulation).

## Integration: turning forces into motion

Each step, integrate acceleration → velocity → position:
- **Explicit (forward) Euler** — simplest, but **unstable** and gains energy at large steps; avoid for anything springy.
- **Semi-implicit / symplectic Euler** — update velocity *then* position with the new velocity; nearly as simple, far more stable; the **common default** for games.
- **Verlet** — position-based, stable, great for particles/cloth/ropes and constraint solving (position deltas carry velocity).
- **RK4** — accurate, heavier; for when precision matters (Gaffer's "Integration Basics").
- **Fix your timestep!** — run the simulation at a **fixed delta** with an accumulator, and **interpolate** the render between steps. Variable timesteps make physics non-deterministic and explode springs. ([[godot]] `_physics_process` is the fixed step; see [[multiplayer-networking]].)

## Particle & rigid-body dynamics

- **Particle** (point mass) — position, velocity, mass, accumulated force; `a = F/m`. Good for effects, projectiles, simple sims.
- **Rigid body** — adds **orientation, angular velocity, torque**, and the **inertia tensor** (rotational mass). Forces applied off-center produce torque → spin. Linear: momentum `p = mv`; angular: `L = Iω`.
- **Forces:** gravity, drag, springs (Hooke's law + damping), buoyancy, thrust; accumulate per step, then integrate. **Damping** keeps the sim stable and bleeds numerical energy.

## Collision detection (two phases)

Brute-force pairwise is O(n²) — split it:
- **Broad phase** — quickly reject far-apart pairs using **spatial partitioning** ([[game-programming-patterns]] Spatial Partition): uniform grid, **sweep-and-prune** (sort AABBs on an axis), quadtree/octree, **BVH**. Produces candidate pairs.
- **Narrow phase** — exact tests on candidates ([[game-math]] intersection): sphere–sphere, AABB–AABB, **OBB/SAT** (Separating Axis Theorem for convex shapes), **GJK** (convex distance/overlap), capsule tests, ray casts. Generate **contact points, normal, and penetration depth** for response.
- Ericson's book is the reference for robust, efficient versions of all of these.

## Collision response

Make collisions look/behave right:
- **Impulse-based response** — apply an instantaneous impulse along the contact normal to change velocities; this is the standard real-time approach.
- **Restitution** (bounciness, 0–1: 0 = inelastic/no bounce, 1 = perfectly elastic) and **friction** (tangential, static vs kinetic, Coulomb model) at contacts.
- **Penetration resolution** — push overlapping bodies apart (positional correction / baumgarte) to stop sinking/jitter.
- **Resting contact & stacking** — the hard case; needs a constraint solver (sequential impulses) and **sleeping** (deactivate settled bodies) for stability and performance.

## Constraints, joints & springs

- **Constraints** restrict motion (distance, hinge, fixed, slider joints); solved iteratively (sequential impulse / position-based dynamics).
- **Springs & dampers** for soft connections, suspension, ropes, cloth (often Verlet + distance constraints).

## Stability, determinism & performance

- **Fixed timestep + interpolation** = stable, deterministic-ish; essential for networked/lockstep sims ([[multiplayer-networking]]) — but beware **floating-point determinism** across machines (Gaffer).
- **Tuning:** damping, restitution, friction, solver iterations, contact slop; too-stiff springs or too-big steps explode.
- **Performance:** broad-phase to cut pairs, **sleep** idle bodies, simplify collision shapes (use primitives/convex hulls, not raw meshes), cap substeps.

## Engine vs custom

Use the engine's physics ([[godot]] Godot Physics: `RigidBody` for dynamic, `CharacterBody` for player-controlled-with-collision, `StaticBody` for immovable, `Area` for detection/triggers; `CollisionShape` primitives) for almost everything — it's robust and tuned. Build custom (Millington-style) only for special mechanics (deterministic lockstep, bespoke soft-body, a teaching exercise, or a constraint the engine can't express). Either way, the concepts here are what let you configure and debug it.

## Anti-patterns

- **Explicit Euler** for springy/stiff systems → energy gain/explosions; not using a **fixed timestep** → nondeterministic, unstable physics.
- Doing physics/movement in `_process` instead of **`_physics_process`** (frame-rate-dependent) ([[godot]]).
- O(n²) collision with no **broad phase**; raw concave **mesh colliders** for dynamic bodies (use primitives/convex hulls).
- Ignoring **penetration resolution** (sinking/jitter) or **sleeping** (CPU waste, jitter in stacks).
- Hand-rolling a full physics engine when the engine's solver suffices; assuming float math is deterministic across platforms for lockstep.
- Tuning restitution/friction/stiffness blindly without a fixed step (chasing instability that's really the integrator).

## Always-apply

1. **Semi-implicit Euler (or Verlet/RK4)** on a **fixed timestep** with render interpolation; physics in `_physics_process`.
2. **Two-phase collision:** broad phase (spatial partition/sweep-and-prune/BVH) then narrow phase (SAT/GJK/primitive tests) producing contact + normal + depth.
3. **Impulse-based response** with restitution & friction; resolve penetration; sleep settled bodies.
4. Prefer the **engine's physics** (Godot RigidBody/CharacterBody/Area); go custom only for special/deterministic needs.
5. Tune with a fixed step; mind **float determinism** for networked sims ([[multiplayer-networking]]).

## Related

- [[game-math]] — vectors, inertia, geometry, and the intersection tests narrow phase relies on.
- [[godot]] — Godot Physics bodies/areas/shapes and `_physics_process`.
- [[game-programming-patterns]] — Spatial Partition (broad phase), fixed Game Loop.
- [[multiplayer-networking]] — fixed-step/deterministic simulation, networked physics.
- Sources: *Game Physics Engine Development, 2nd ed.* (Ian Millington); *Real-Time Collision Detection* (Christer Ericson).
