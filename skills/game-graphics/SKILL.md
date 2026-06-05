---
name: game-graphics
description: Real-time game graphics and shader programming, distilled from Akenine-Möller et al.'s *Real-Time Rendering* and *The Book of Shaders*, applied through Godot's shading language. Covers the real-time rendering pipeline (application → geometry/vertex → rasterization → fragment/pixel → output), the GPU and how shaders run (vertex vs fragment shaders, SIMD/parallelism), transforms & spaces in rendering, lighting and shading models (Lambert/Phong/Blinn-Phong, physically based rendering — BRDF, metallic/roughness, energy conservation), materials and textures (UVs, normal/roughness/metallic maps, mipmaps, filtering), shadows, the fragment-shader mindset (per-pixel functions, UV space, SDFs, procedural patterns, noise), post-processing, and performance/optimization (draw calls, batching, overdraw, LOD, culling, the frame budget). Use when writing shaders, reasoning about the rendering pipeline, choosing a lighting/material approach, debugging visual/performance issues, or adding "juice"/visual polish. Pairs with game-math (the transform/vector math), godot (the shading language & renderers), and game-design (game feel).
---

# Game Graphics & Shaders

How games **render in real time**, and how to **program shaders** — from **Akenine-Möller, Haines & Hoffman's *Real-Time Rendering*** (the field's reference) and **Patricio Gonzalez Vivo & Jen Lowe's *The Book of Shaders***, applied through [[godot]]'s shading language. The constraint that defines everything: a **frame budget** (~16.6 ms at 60 fps) you cannot exceed.

Cross-links: [[game-math]] (vectors/matrices/transforms underpin all of this), [[godot]] (renderers + the Godot shading language), [[game-design]] (visual feel/juice), [[operating-systems]] (the GPU as a device), [[information-theory]] (noise).

## The real-time rendering pipeline

Conceptually four stages (RTR's model):
1. **Application** (CPU) — game logic, culling, deciding what to draw, issuing **draw calls**.
2. **Geometry / vertex processing** (GPU) — transform vertices through **model → view → projection** ([[game-math]]); per-vertex work in the **vertex shader**; clipping; projection to screen.
3. **Rasterization** — turn triangles into fragments (candidate pixels); interpolate vertex outputs across the triangle.
4. **Fragment / pixel processing** (GPU) — the **fragment shader** computes each pixel's colour (lighting, textures); then depth/stencil test, blending → the framebuffer.

The GPU is **massively parallel** (SIMD): the same shader runs on thousands of vertices/fragments at once — so shaders must be branch-light and data-parallel. Render to the screen or to **render targets** (for post-processing, shadow maps, reflections).

## Shaders: the two you write most

- **Vertex shader** — runs per vertex: position transforms, pass UVs/normals/colours to the fragment stage; vertex animation (wind, waves).
- **Fragment (pixel) shader** — runs per pixel: sample textures, compute lighting, output colour. *The Book of Shaders* mindset: **a fragment shader is a pure function `(uv, time, …) → colour`** evaluated independently per pixel — so you think in **UV space**, math, and **procedural** patterns (gradients, shapes via step/smoothstep, **SDFs**, **noise**, fbm) rather than drawing commands.
- Also: compute shaders (general GPU compute), geometry/tessellation (less common). In [[godot]]: the **Godot shading language** (GLSL-like), `shader_type canvas_item` (2D), `spatial` (3D), `particles`, `sky`, `fog`; plus visual shaders.

## Lighting & shading models

- **Lambert (diffuse)** — `N·L` ([[game-math]] dot product); matte surfaces.
- **Phong / Blinn-Phong** — diffuse + specular highlight; the classic real-time model.
- **Physically Based Rendering (PBR)** — the modern standard: a **BRDF** that obeys **energy conservation**, parameterized by **metallic** + **roughness** (and base colour, normal, AO). Looks consistent under any lighting; what Godot's `StandardMaterial3D` uses. Pair with image-based lighting / environment maps.
- **Normals** drive lighting; **normal maps** fake surface detail cheaply.

## Materials, textures & sampling

- **UV coordinates** map textures onto geometry; **texture maps**: albedo/base-colour, **normal**, **roughness**, **metallic**, AO, emission, height.
- **Mipmaps** (prefiltered downscales) + **filtering** (bilinear/trilinear/anisotropic) prevent shimmering/aliasing at distance.
- **Sampling** is a cost — texture bandwidth matters in the fragment shader.

## Shadows, transparency & post

- **Shadows** — usually **shadow mapping** (render depth from the light, compare); soft shadows, bias/acne issues. Expensive — budget them.
- **Transparency** — alpha blending needs back-to-front sorting (order-dependent); alpha-test/cutout avoids sorting.
- **Post-processing** — full-screen fragment passes on the rendered image: bloom, tone mapping/HDR, color grading, SSAO, FXAA/TAA, vignette, chromatic aberration. Cheap source of look-and-feel and **juice** ([[game-design]]).

## "Juice" & 2D effects

For [[game-design]]'s game feel: screen shake, hit-flash, dissolve/SDF effects, outline shaders, palette/posterize, CRT/retro filters, particle materials. Most are short fragment shaders in UV space (the *Book of Shaders* toolkit) — high impact, low cost.

## Performance (the frame budget)

CPU-bound vs GPU-bound — profile to know which. Key levers:
- **Draw calls / batching** — fewer, batched draws (instancing/MultiMesh) beat thousands of small ones (CPU cost).
- **Overdraw** — pixels shaded then covered; minimize transparent layering and shade complexity.
- **Culling** — frustum + occlusion culling so you don't draw the unseen; **LOD** (level of detail) for distant meshes.
- **Shader cost** — keep fragment shaders cheap (they run per pixel × resolution); avoid dynamic branches/heavy loops; precompute.
- **Texture/VRAM** budget; resolution scaling. Target the frame budget per platform ([[game-development]] perf phase).

## Anti-patterns

- Expensive work in the **fragment shader** (runs millions of times/frame) that belongs in the vertex shader or CPU.
- Thousands of **draw calls** / no batching; ignoring **overdraw** with stacked transparency.
- Heavy dynamic **branching/loops** in shaders (GPU divergence); not using mipmaps (shimmer/aliasing).
- Ad-hoc non-PBR materials that break under different lighting; ignoring **energy conservation**.
- Optimizing without **profiling** (guessing CPU vs GPU bound); shadow/post effects with no budget.
- Hand-rolling transform math instead of the pipeline/[[game-math]] conventions.

## Always-apply

1. Think in the **pipeline** (vertex → raster → fragment) and the **frame budget**; profile CPU vs GPU before optimizing.
2. Write shaders as **per-pixel pure functions** in UV space; keep fragment shaders cheap and branch-light.
3. Prefer **PBR** (metallic/roughness, energy-conserving); use normal/roughness maps + **mipmaps**.
4. Cut **draw calls** (batch/instance), **overdraw**, and unseen geometry (**culling/LOD**).
5. Use cheap **post/2D fragment effects** for look & **juice**; budget shadows/post per platform.

## Related

- [[game-math]] — vectors, matrices, the transform pipeline, noise/SDFs.
- [[godot]] — Forward+/Mobile/Compatibility renderers and the Godot shading language; `StandardMaterial3D` (PBR).
- [[game-design]] — visual feel and juice.
- [[operating-systems]] — the GPU as a parallel device; [[information-theory]] — noise.
- Sources: *Real-Time Rendering, 4th ed.* (Akenine-Möller, Haines, Hoffman); *The Book of Shaders* (Gonzalez Vivo & Lowe, thebookofshaders.com).
