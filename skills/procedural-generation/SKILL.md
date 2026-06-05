---
name: procedural-generation
description: Procedural content generation (PCG) for games — algorithmically creating levels, maps, terrain, dungeons, items, quests, and narrative — distilled from the Hendrikx et al. survey, *Procedural Content Generation in Games*, and Red Blob Games. Covers the methods (pseudo-random + seeds for reproducibility, noise functions — Perlin/Simplex/value, fBm/octaves — for terrain; grammars & L-systems; cellular automata for caves; Voronoi/Delaunay & Poisson-disk/blue-noise for maps; BSP/room-and-corridor & drunkard's-walk for dungeons; wave function collapse for tile-based; search/constraint-based & answer-set; grammar-based quests/narrative), the taxonomy (online vs offline, constructive vs generate-and-test, content type), controllability/expressiveness and evaluation, and the design role (replayability vs authored quality, the "10,000 bowls of oatmeal" problem). Use when generating levels/terrain/dungeons/items/quests, choosing a PCG technique, designing seeds/reproducibility, or balancing variety vs authored quality. Builds on game-math (noise/voronoi/grids) and pairs with game-design, game-ai (graphs), and godot.
---

# Procedural Content Generation (PCG)

Algorithmically **creating game content** — levels, terrain, dungeons, maps, items, quests, even narrative — from the **Hendrikx et al. survey** ("Procedural Content Generation for Games"), the **PCG in Games** book (Shaker/Togelius/Nelson), and **Red Blob Games** (the best interactive map-gen guides). PCG buys replayability, scale, and surprise — at the cost of control over quality.

Cross-links: [[game-math]] (noise, Voronoi/Delaunay, grids, probability — the math behind PCG), [[game-design]] (variety vs authored quality, what's worth generating), [[game-ai]] (graphs/grids, pathfinding-aware generation), [[godot]] (TileMap, noise, instancing), [[information-theory]] (noise as signal, entropy).

## First principle: seeds & reproducibility

PCG is **pseudo-random**: a **seed** + a deterministic algorithm = the same content every time. Seeds give you reproducibility (share a world by its seed, debug a bad layout, daily challenges). Separate **streams** of randomness per system so changing one doesn't shift everything. (Use a seeded PRNG, not the global RNG; [[game-math]] probability.)

## The taxonomy (how to classify a technique)

- **Online vs offline** — generated at runtime (roguelike levels, endless terrain) vs at build/author time (baked maps).
- **Constructive vs generate-and-test** — build it right in one pass (fast, e.g. BSP dungeons) vs generate then evaluate/reject/repair until it passes constraints (e.g. ensure the level is solvable).
- **By content type** — Hendrikx's pyramid: bits/textures → sound/vegetation/buildings → **levels/maps/terrain** → systems/economies → **scenarios/quests/narrative** → derived/emergent. Different layers want different methods.
- **Controllability/expressiveness** — how much the designer can steer it, and how varied yet coherent the output is.

## Core methods

- **Noise functions** — **Perlin/Simplex** (gradient) and value noise produce smooth coherent randomness; sum **octaves (fBm)** for natural detail; threshold/colour-map for **terrain, heightmaps, biomes, textures, clouds**. (Red Blob "Map generation from noise"; [[game-math]]/[[information-theory]] — noise as a signal.)
- **Voronoi / Delaunay + Poisson-disk (blue noise)** — partition space into regions for **polygonal maps, biomes, territories, organic caves**; blue noise for even-but-random placement (trees, spawns). (Red Blob "Polygonal map generation".)
- **Cellular automata** — iterate simple neighbor rules to grow **organic caves** (the classic 4-5 rule), erosion, fluids.
- **Dungeon generation** — **BSP** (recursively split into rooms) or **room-and-corridor**; **drunkard's walk**/random walk for organic caves; graph-based for connectivity guarantees.
- **Grammars & L-systems** — rewrite rules generate **plants/trees** (L-systems), buildings, road networks, and **mission/quest structure** (shape grammars; graph grammars for level topology).
- **Wave Function Collapse (WFC)** — constraint propagation over a tile set to generate **tile-based** levels/textures that locally resemble an example; powerful for coherent tile maps.
- **Search / constraint-based** — treat generation as search/optimization (genetic algorithms, answer-set programming) over a fitness/constraint function (generate-and-test at scale).
- **Grammar/planner-based quests & narrative** — generate objectives, quest chains, and story beats from rules/templates ([[game-ai]] planning ideas apply).

## Controllability, evaluation & quality

- **Constrain and validate** — generate, then **test** (is it connected? solvable? balanced? reachable via [[game-ai]] pathfinding?) and **repair/reject**. PCG without validation ships broken levels.
- **Expressive range** — measure the variety/coverage of what a generator can produce; avoid a generator that technically varies but feels samey.
- **The "10,000 bowls of oatmeal" problem (Kate Compton)** — generating endless *technically distinct but perceptually identical* content. Aim for **perceptual** differentiation, not just numeric variety.
- **Mixed-initiative / authored hybrids** — combine generation with hand-authored set-pieces; generate the connective tissue, author the memorable moments.

## The design view

- **Why generate?** Replayability, scale (vast worlds), surprise, personalization, reduced authoring cost. **Why not?** You trade away **authorial control and guaranteed quality** — generated content rarely matches a great hand-crafted level. Generate where variety matters more than crafted perfection.
- Decide **what** to generate (terrain & loot: yes; the critical-path boss puzzle: maybe author it) — a [[game-design]] decision.
- Make it **reproducible** (seeds), **steerable** (parameters/constraints), and **validated**.

## Anti-patterns

- No **seed/determinism** → unreproducible, undebuggable generation; using the global RNG so unrelated systems interfere.
- **No validation** → unsolvable/disconnected/broken levels shipped (always generate-and-test critical properties).
- The **oatmeal problem** — variety in numbers but not in perception; chasing infinite content that all feels the same.
- Over-generating what should be **authored** (key story/tutorial moments), or under-using PCG where variety would help.
- Hand-rolling noise/Voronoi instead of [[game-math]]/[[godot]] `FastNoiseLite`; offset-grid hacks instead of proper coordinates.
- Pure generate-and-test with a weak fitness function → slow and low quality.

## Always-apply

1. **Seed everything** (reproducible, per-system streams); use a proper PRNG.
2. Pick the method by goal: **noise** (terrain/biomes), **Voronoi/CA** (organic maps/caves), **BSP/grammars** (dungeons/structure), **WFC** (coherent tiles), **search** (constraint-heavy).
3. **Generate-and-test**: validate critical properties (connected, solvable, balanced) and repair/reject.
4. Optimize for **perceptual** variety, not numeric (avoid the oatmeal problem); hybridize with authored set-pieces.
5. Decide **what's worth generating** ([[game-design]]); build on [[game-math]] noise/Voronoi/grids and [[godot]] tools.

## Related

- [[game-math]] — noise, Voronoi/Delaunay, grids, probability (the PCG math).
- [[game-design]] — replayability vs authored quality; what to generate.
- [[game-ai]] — graphs/grids and validating reachability/solvability; [[godot]] — TileMap, `FastNoiseLite`, instancing.
- [[information-theory]] — noise as signal / entropy.
- Sources: Hendrikx et al., "Procedural Content Generation for Games" (survey); *Procedural Content Generation in Games* (Shaker, Togelius, Nelson — free online); Red Blob Games (map generation, noise, Voronoi).
