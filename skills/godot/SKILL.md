---
name: godot
description: The Godot Engine (4.x) — the open-source, MIT-licensed 2D/3D game engine — distilled from the official docs. Covers the core mental model (Nodes as building blocks, Scenes as composable/reusable trees a.k.a. prefabs, the SceneTree, Signals as the built-in observer pattern, Groups, Autoload singletons, Resources), GDScript (the Python-like native language; `_init`/`_ready`/`_process(delta)`/`_physics_process(delta)` lifecycle, `@export`, `@onready`, first-class signals/Callables) and the C#/GDExtension alternatives, the 2D vs 3D pipelines and their node types (CharacterBody2D/3D, Area, RigidBody, Camera, etc.), the subsystems (rendering/Forward+, physics, input map/actions, animation, Control-node UI, audio buses, navigation, tilemaps, particles, the Godot shading language, high-level multiplayer, export), project structure (project.godot, res://, .tscn/.tres, the import system), and the composition-over-inheritance ethos. Use when building or reviewing a Godot game, choosing nodes/scenes/signals, writing GDScript, structuring a Godot project, using a subsystem, or migrating Godot 3→4. The chosen-engine skill of the game-dev cluster; pairs with game-programming-patterns, game-design, and the technical skills.
---

# Godot Engine

Building games in **Godot 4.x** — the free, **MIT-licensed**, open-source 2D/3D engine — from the official docs (docs.godotengine.org, currently the 4.x branch). Godot is the chosen engine for the game-dev cluster: lightweight, scene/node-based, composition-first, with a built-in scripting language.

> Canonical: *"In Godot, a game is a tree of nodes that you group together into scenes. You can then wire these nodes so they can communicate using signals."* Internalize that one sentence and the engine follows.

Cross-links: [[game-programming-patterns]] (Godot bakes in Component/Observer/Game-Loop), [[game-design]] (what you're building), [[game-math]] (Vector2/3, Transform), [[game-graphics]] (the shading language), [[game-physics]]/[[game-ai]]/[[game-audio]]/[[procedural-generation]]/[[multiplayer-networking]] (subsystems), [[game-development]] (the lifecycle/export).

## The mental model

- **Node** — *"the fundamental building blocks of your game."* Each has a name, properties, per-frame callbacks, and can be extended; nodes form a **tree**. Godot ships a large library of node types (Sprite2D, CharacterBody3D, Camera, AudioStreamPlayer, Control, …) you combine and extend.
- **Scene** — a tree of nodes saved as a unit. *"Scenes work like new node types… the instance appears as a single node with its internals hidden."* A scene can be a character, a weapon, a level, a UI — Godot scenes **fill the role of both prefabs and scenes**. Scenes **nest** (a scene instanced inside another). One root node per scene; instance as many times as you like (`PackedScene.instantiate()`).
- **SceneTree** — the runtime tree of all active scenes/nodes and the main loop manager. One **main scene** loads first.
- **Signals** — *"Godot's version of the observer pattern"*: a node **emits** a signal on an event; others **connect** to react, **without referencing each other** → low coupling ([[game-programming-patterns]] Observer). First-class type since 4.0: `button.pressed.connect(_on_pressed)`.
- **Groups** — tag nodes into named groups; act on all members (`get_tree().call_group(...)`).
- **Autoload (singletons)** — always-loaded scripts/nodes for global state and scene switching (GDScript has no globals by design). A constrained Singleton/Service Locator ([[game-programming-patterns]]).
- **Resources** — ref-counted data containers (`.tres`/`.res`): textures, materials, and your own `Resource` subclasses (great for data-driven design — Type Object).
- **Ethos: composition over inheritance** — compose behavior from nodes/sub-scenes rather than deep class trees.

## GDScript (and the alternatives)

*"GDScript is a high-level, object-oriented, gradually typed language built for Godot… indentation-based, similar to Python (but independent of it)."* Built for the engine: native `Vector2/3`/`Transform3D`, tight editor integration, fast iteration — the recommended default.

- A file **is** a class; `extends Node2D`; optional `class_name Foo`. `var`/`const`/`enum`; optional typing (`var hp: int`, infer `var s := "x"`), typed arrays/dicts. `match` with pattern guards; `await` for signals/coroutines; `preload`/`load`.
- **Lifecycle callbacks** (Node virtuals, underscore-prefixed):
  - `_init()` — on creation.
  - `_ready()` — once the node + children enter the tree; **the place to grab child refs and connect signals**.
  - `_process(delta)` — every rendered frame (framerate-dependent); general per-frame logic (Update Method).
  - `_physics_process(delta)` — fixed rate (default 60 Hz); **movement, physics, collision** go here.
  - `_input(event)` / `_unhandled_input(event)` — input events.
- **`@export`** exposes a var to the Inspector (`@export var speed := 200`, `@export_range(...)`); **`@onready`** defers init to `_ready()` (`@onready var sprite = $Sprite2D`). `$NodePath` / `get_node()` to reference children.
- **Signals:** `signal died`; emit `died.emit()`; connect `enemy.died.connect(_on_enemy_died)`; convention `_on_<node>_<signal>`. Or wire via the editor **Signals dock**.
- **Alternatives:** **C#** (.NET 6; PascalCase `_Ready`/`_Process`; no C# on web export) for teams/perf with few engine calls; **C++/GDExtension** for native hot paths/libraries. Perf order: C++ > C# ≈ GDScript (same order of magnitude). Default to GDScript; drop to C++ for measured hot paths.

## 2D vs 3D

Two pipelines sharing similar APIs (nodes end in `2D`/`3D`):
- **2D** — `Node2D` base; `Sprite2D`, `AnimatedSprite2D`, **`CharacterBody2D`** (player movement with collision), `RigidBody2D`, `StaticBody2D`, `Area2D` (overlap/detection), `Camera2D`, `CollisionShape2D`, `TileMapLayer`. Units = **pixels**, rotation in **radians**.
- **3D** — `Node3D` base (was `Spatial`); `MeshInstance3D`, **`CharacterBody3D`**, `RigidBody3D`, `Area3D`, `Camera3D`, `DirectionalLight3D`, `CollisionShape3D`. Units = **meters**; `Transform3D`/`Basis` for transforms ([[game-math]]).

## Subsystems (route to these)

Rendering (**Forward+ / Mobile / Compatibility** renderers; [[game-graphics]]) · **Physics** (Godot Physics; `CharacterBody`/`RigidBody`/`StaticBody`/`Area`, `CollisionShape`; `_physics_process`; [[game-physics]]) · **Input** (Input Map → named **actions**, `Input` singleton) · **Animation** (`AnimationPlayer`, `AnimationTree` state machines, Tweens via `create_tween()`) · **UI** (**`Control`** nodes, containers, anchors, themes; [[ux-design]]) · **Audio** (audio **buses**, `AudioStreamPlayer`/2D/3D; [[game-audio]]) · **Navigation** (NavigationServer, `NavigationAgent2D/3D`, navmeshes; [[game-ai]]) · **TileMaps** (`TileMapLayer` + `TileSet`) · **Particles** (GPU/CPU) · **Shaders** (the **Godot shading language**, a GLSL-like DSL; canvas_item/spatial/particle types; [[game-graphics]]) · **Multiplayer** (high-level API: `@rpc`, `MultiplayerSpawner`/`MultiplayerSynchronizer`, ENet/WebSocket/WebRTC; [[multiplayer-networking]]) · **Export** (one-click to desktop/mobile/web/console via export templates).

## Project structure & workflow

- **`project.godot`** at the root (marks the project; `res://` = resource path; `user://` = writable user data). Edit via **Project → Project Settings**.
- **`.tscn`** (text scene), **`.tres`** (text resource) — VCS-friendly; binary `.scn`/`.res` exist. Scripts `.gd` (GDScript) / `.cs` (C#); shaders `.gdshader`.
- **Import system:** source assets (png/gltf/wav) import to engine formats with a `.import` sidecar; reimport on change.
- Favor **signals over polling** to decouple; gate per-frame work with `set_process()`.
- Learning path (docs): Getting Started → Step by step (nodes & scenes → instancing → first script → input → signals) → Your first 2D/3D game → the Manual (per-subsystem). The full **class reference** is in the script editor.

## Godot 3 → 4 (some uploaded books target 3)

Key renames/changes (an automated upgrade tool exists — **back up first**): `Spatial`→`Node3D`; `KinematicBody[2D]`→`CharacterBody[2D/3D]`; `SpatialMaterial`→`StandardMaterial3D`; `instance()`→**`instantiate()`**; `yield`→**`await`**; string-based `connect("sig",...)` → **first-class `sig.connect(...)`**; Mono→**.NET 6**; GLES2 removed (Forward+/Mobile/Compatibility); Bullet→GodotPhysics; `.shader`→`.gdshader`; `Tween` node → `create_tween()`; OS time → `Time` singleton. Treat Godot-3 tutorials as needing translation.

## Anti-patterns

- Deep inheritance instead of **scene composition**; one giant scene instead of small reusable scenes.
- Hard-referencing nodes across the tree instead of **signals**/groups → tight coupling, brittle paths.
- Grabbing child nodes in `_init()` instead of **`_ready()`** (not in the tree yet); physics/movement in `_process` instead of **`_physics_process`**.
- Overusing **autoload** as a global-variable dumping ground (a tamed Singleton — still global state).
- Following **Godot 3** tutorials verbatim in Godot 4 (renamed APIs).
- Reaching for C#/C++ before measuring — GDScript is fine for most gameplay; optimize hot paths only.
- Polling every frame what a **signal** could deliver.

## Always-apply

1. Think **nodes → scenes → SceneTree**, wired by **signals**; compose, don't inherit.
2. Use the right callback: refs/connections in **`_ready()`**, gameplay in **`_process`**, movement/physics in **`_physics_process`**.
3. Build reusable **scenes (prefabs)**; expose tuning with **`@export`**; keep data in **Resources**.
4. **GDScript by default**; C#/GDExtension only for measured needs; text scenes/resources in VCS.
5. Use the **engine's subsystems** (Input Map, AnimationTree, audio buses, high-level multiplayer) before hand-rolling; mind **Godot 3→4** differences.

## How to use the reference

- **`references/core-concepts.md`** — nodes/scenes/signals/autoload/resources in detail, the GDScript lifecycle and idioms, the 2D/3D node maps, and a subsystem-by-subsystem quick reference with the docs URLs.

## Related

- [[game-programming-patterns]] — Godot implements Component (nodes), Observer (signals), Game Loop/Update (SceneTree/`_process`); reach for hand-rolled patterns when the engine's affordance doesn't fit.
- [[game-design]] — the design you're realizing; [[game-development]] — the lifecycle and export.
- [[game-math]] (Vector/Transform), [[game-graphics]] (shaders/rendering), [[game-physics]], [[game-ai]] (navigation), [[game-audio]], [[procedural-generation]], [[multiplayer-networking]] (high-level multiplayer API).
- [[ux-design]] — Control-node UI.
- Source: official Godot Engine documentation (docs.godotengine.org, 4.x), MIT-licensed engine / CC-BY docs.
