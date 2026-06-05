---
name: game-math
description: The mathematics of games and 3D graphics, distilled from Lengyel's *Mathematics for 3D Game Programming and Computer Graphics*, Dunne & Parberry's *3D Math Primer*, and Red Blob Games. Covers vectors (dot/cross products, normalization, projection), matrices and the transform pipeline (model/view/projection, translation/rotation/scale, homogeneous coordinates), rotations (Euler angles, gimbal lock, quaternions, slerp), coordinate spaces and change-of-basis, linear interpolation/easing, trigonometry for movement/aiming, geometry & intersection tests (ray/plane/sphere/AABB/triangle, closest-point, separating axis), splines/Bézier curves, grids (square/hex — axial/cube coordinates), noise, and probability for game balance. Use for any math in a game — moving/rotating/aiming objects, camera and transform math, collision/intersection queries, interpolation and smoothing, hex/grid math, curves and paths, or randomness/probability tuning. The math foundation under game-physics, game-graphics, and game-ai; pairs with godot (Vector2/3, Transform3D) and information-theory.
---

# Game Math

The **practical mathematics** behind games and real-time graphics — vectors, matrices, rotations, transforms, geometry/intersection, interpolation, curves, grids, and probability. Distilled from **Lengyel's *Mathematics for 3D Game Programming and Computer Graphics***, **Dunne & Parberry's *3D Math Primer***, and **Red Blob Games** (the interactive guides). The foundation the technical game skills stand on.

Cross-links: [[game-physics]] (collision math, integration), [[game-graphics]] (the transform/rendering pipeline), [[game-ai]] (pathfinding/steering geometry), [[godot]] (`Vector2`/`Vector3`/`Transform3D`/`Basis`/`Quaternion` implement all of this), [[information-theory]] (noise/probability).

## Vectors (the workhorse)

A vector = direction + magnitude (and points as position vectors). Master these:
- **Add/subtract/scale**; `b - a` = the vector from a to b (and its `length()` = distance).
- **Magnitude & normalization** — `‖v‖`; a **unit vector** (`v/‖v‖`) is a pure direction (for movement/facing).
- **Dot product** `a·b = ‖a‖‖b‖cosθ` — projection, "how aligned" (sign = in front/behind), angle between, and the basis of lighting (N·L). Zero ⇒ perpendicular.
- **Cross product** (3D) `a×b` — a vector perpendicular to both; magnitude = parallelogram area; gives **surface normals**, the 2D "perp/which-side" test, and torque.
- **Movement:** `position += direction.normalized() * speed * delta` (frame-rate independent — multiply by `delta`).

## Matrices & the transform pipeline

- A matrix encodes a linear transform; **translate · rotate · scale** combine by multiplication (**order matters** — usually scale, then rotate, then translate). **Homogeneous coordinates** (4D for 3D points) let a single 4×4 matrix include translation and perspective.
- **Spaces:** model/local → world → view/camera → clip/screen, via the **model → view → projection** matrix chain ([[game-graphics]]). Know **change-of-basis** (express a point in another space) — the key to camera, parenting, and attaching objects.
- In [[godot]]: `Transform2D`/`Transform3D` (a `Basis` + origin) bundle this; `to_local()`/`to_global()` do change-of-basis.

## Rotations

- **Euler angles** (yaw/pitch/roll) — intuitive but suffer **gimbal lock** and order-dependence; fine for simple cases.
- **Quaternions** — the robust representation for 3D rotation: no gimbal lock, compose cleanly, and **slerp** (spherical lerp) gives smooth shortest-path interpolation between orientations. Use them for cameras, character orientation, animation blending. ([[godot]] `Quaternion`.)
- **2D rotation** is just an angle; rotate a vector with a 2×2 matrix or `Vector2.rotated(θ)`.

## Interpolation, easing & trig

- **Lerp** `a + (b−a)·t` — the most-used function in games (smooth movement, fades, value blending). **Inverse lerp** & **remap** to convert ranges.
- **Easing / tweens** — ease-in/out curves make motion feel good ([[game-design]] feel; [[godot]] tweens). **Smoothing/damping** (exponential smoothing, `lerp` toward target each frame) for cameras and follow.
- **Trig** — `atan2(dy,dx)` to aim/face a target; `sin/cos` for circular motion, oscillation, waves.

## Geometry & intersection tests (collision math)

The toolkit for [[game-physics]] and queries:
- **Closest point** on segment/line/plane/AABB; **distance** point-to-X.
- **Ray casts:** ray–plane, ray–sphere, ray–AABB (slab method), ray–triangle (Möller–Trumbore) — for shooting, picking, line-of-sight.
- **Overlap tests:** sphere–sphere, AABB–AABB, sphere–AABB, circle–circle; the **Separating Axis Theorem (SAT)** for convex polygons/OBBs.
- **2D visibility / line-of-sight** (Red Blob's sweep algorithm) for FOV/lighting/stealth.

## Curves, grids & noise

- **Splines / Bézier curves** — smooth paths, camera rails, animation curves; Catmull-Rom for paths through points (Red Blob "curved roads").
- **Grids:** square grids (tiles/edges/vertices), and **hex grids** — use **axial/cube coordinates** (Red Blob's hex reference) for clean neighbor/distance/rounding math. Line drawing via lerp; circle rasterization.
- **Noise** (Perlin/Simplex, value noise) — coherent randomness for terrain/textures/motion; the basis of [[procedural-generation]]; think of it as a signal (octaves/fBm).

## Probability (balance & feel)

Distributions for damage rolls, loot tables, crit chance, spread; uniform vs normal vs custom; expected value for balance; "bad luck protection" (pity timers). Red Blob's "Probability for RPG damage." Use `secrets`/PRNG appropriately ([[cryptography]] only if it must be unpredictable/secure). Output vs input randomness ([[game-design]]).

## Anti-patterns

- Forgetting to **normalize** a direction (speed varies with vector length) or to multiply movement by **`delta`** (frame-rate-dependent).
- **Euler angles** for free 3D rotation → gimbal lock; not using **quaternions/slerp** for smooth orientation.
- Wrong **transform order** (scale/rotate/translate) or mixing up local vs world space.
- Comparing **distances with `sqrt`** in hot loops — compare squared lengths instead (skip the sqrt).
- Rolling your own intersection tests when the engine/[[game-physics]] provides robust ones; off-the-shelf math (Godot, GLM) over hand-rolled.
- Offset/array-based hex math instead of **cube/axial** coordinates (endless edge cases).

## Always-apply

1. **Normalize directions**, scale movement by **`delta`**, and use **dot/cross** for alignment/perpendicular/normals.
2. Respect **transform order** and **spaces** (model→view→projection; local vs world); use the engine's `Transform`.
3. **Quaternions + slerp** for 3D rotation/blending; **lerp/easing/damping** for smooth motion and cameras.
4. Use the standard **intersection tests**; compare **squared distances** in hot paths.
5. **Cube/axial** coords for hex; **noise** for procedural; **probability** deliberately for balance.

## Related

- [[game-physics]] — collision detection/response built on this geometry; [[game-graphics]] — the transform/rendering pipeline.
- [[game-ai]] — steering/pathfinding geometry; [[procedural-generation]] — noise/voronoi.
- [[godot]] — `Vector2/3`, `Transform2D/3D`, `Basis`, `Quaternion`, `lerp`, `move_toward`.
- [[information-theory]] — noise and probability foundations.
- Sources: *Mathematics for 3D Game Programming and Computer Graphics* (Eric Lengyel); *3D Math Primer for Graphics and Game Development* (Dunne & Parberry); Red Blob Games (redblobgames.com).
