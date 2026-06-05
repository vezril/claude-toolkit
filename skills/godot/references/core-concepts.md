# Godot 4 — core concepts & subsystem reference

Detail for the godot skill (official docs, 4.x). Routing URLs are under docs.godotengine.org/en/stable/.

## Nodes, scenes, the tree
- **Node:** smallest building block; has name, properties, per-frame callbacks; extendable; child of another node. Big built-in library.
- **Scene:** a saved node tree with **one root**; behaves as a new node type when instanced; fills both **prefab** and **scene** roles; **nestable**. Instance via `var n = preload("res://Enemy.tscn").instantiate(); add_child(n)`.
- **SceneTree:** runtime tree + main loop; one **main scene** at startup (Project Settings → Application → Run). `get_tree()` for scene-change, groups, pause.
- **Change scene:** `get_tree().change_scene_to_file("res://Level2.tscn")` or `change_scene_to_packed(packed)`.

## Signals (observer)
```gdscript
signal health_changed(new_value)
func take_damage(d):
    hp -= d
    health_changed.emit(hp)
# elsewhere:
enemy.health_changed.connect(_on_enemy_health_changed)
func _on_enemy_health_changed(v): ...
```
First-class since 4.0 (pass `Callable`s, no strings). Wire via the editor **Signals dock** too. Decouples emitter from listener.

## Groups, autoload, resources
- **Groups:** `add_to_group("enemies")`; `get_tree().call_group("enemies", "explode")`; `get_tree().get_nodes_in_group("enemies")`.
- **Autoload:** Project Settings → Autoload; an always-loaded singleton script (e.g. `GameState`, `AudioManager`, scene router). Access globally by its name. Not a *true* singleton.
- **Resource:** subclass `Resource`, `@export` fields, save as `.tres` → data-driven design (item/enemy definitions = Type Object/Flyweight).

## GDScript lifecycle & idioms
```gdscript
extends CharacterBody2D
class_name Player

@export var speed := 200.0
@onready var sprite := $Sprite2D
signal died

func _ready():
    # node + children in tree: safe to get refs / connect
    pass

func _process(delta):
    # per drawn frame (framerate-dependent): animation, UI, non-physics
    pass

func _physics_process(delta):
    # fixed step: movement, physics, collisions
    var dir := Input.get_vector("left","right","up","down")
    velocity = dir * speed
    move_and_slide()           # CharacterBody2D helper

func _unhandled_input(event):
    if event.is_action_pressed("jump"): ...
```
- `$Path` = `get_node("Path")`; `%UniqueName` for scene-unique nodes.
- `await get_tree().create_timer(1.0).timeout` to wait; `await sig` to await a signal.
- Tween: `create_tween().tween_property(self, "modulate:a", 0.0, 0.5)`.

## 2D node map
`Node2D` (transform) · `Sprite2D` / `AnimatedSprite2D` · `CharacterBody2D` (+`move_and_slide()`) · `RigidBody2D` / `StaticBody2D` · `Area2D` (+`body_entered` signal) · `CollisionShape2D` · `Camera2D` · `TileMapLayer` (+`TileSet`) · `CanvasLayer` (HUD) · `GPUParticles2D`.

## 3D node map
`Node3D` · `MeshInstance3D` · `CharacterBody3D` / `RigidBody3D` / `StaticBody3D` · `Area3D` · `CollisionShape3D` · `Camera3D` · `DirectionalLight3D`/`OmniLight3D` · `NavigationRegion3D` + `NavigationAgent3D` · `GPUParticles3D`. Transforms via `Transform3D`, `Basis`, `Quaternion` ([[game-math]]).

## Subsystem quick reference
| Subsystem | Key nodes/APIs | Docs path |
|-----------|----------------|-----------|
| Input | Input Map actions, `Input`, `_input`/`_unhandled_input` | tutorials/inputs/ |
| Physics | CharacterBody/RigidBody/StaticBody/Area, CollisionShape, `_physics_process` | tutorials/physics/ |
| Animation | `AnimationPlayer`, `AnimationTree` (state machine/blend), Tweens | tutorials/animation/ |
| Rendering | Forward+/Mobile/Compatibility; `WorldEnvironment`, materials | tutorials/rendering/ |
| Shaders | Godot shading language (`shader_type canvas_item/spatial/particles`) | tutorials/shaders/ |
| UI | `Control` nodes, containers, anchors, `Theme` | tutorials/ui/ |
| Audio | audio **buses**, `AudioStreamPlayer`/2D/3D, effects | tutorials/audio/ |
| Navigation | `NavigationServer`, `NavigationRegion`, `NavigationAgent` | tutorials/navigation/ |
| Multiplayer | `@rpc`, `MultiplayerSpawner`, `MultiplayerSynchronizer`, ENet/WebSocket/WebRTC | tutorials/networking/ |
| Export | export templates + presets (desktop/mobile/web/console) | tutorials/export/ |

## Project files
- `project.godot` (manifest) · `res://` (project) / `user://` (writable) · `.tscn`/`.tres` (text) · `.gd`/`.cs` (scripts) · `.gdshader` · `*.import` (import sidecars) · `export_presets.cfg`.
- VCS: commit `.tscn`/`.tres`/scripts/`project.godot`/`.import`; `.gitignore` the `.godot/` cache and exports.

## Godot 3 → 4 cheat (translating old tutorials)
`Spatial`→`Node3D` · `KinematicBody[2D]`→`CharacterBody[2D/3D]` (+`move_and_slide()` signature changed; `velocity` is now a property) · `instance()`→`instantiate()` · `yield(x,"sig")`→`await x.sig` · `connect("sig", obj, "f")`→`x.sig.connect(f)` · `SpatialMaterial`→`StandardMaterial3D` · `.shader`→`.gdshader` · `Tween` node→`create_tween()` · `OS.get_ticks_msec()`→`Time.get_ticks_msec()` · Mono→.NET 6. Use the Project Manager's "Convert" tool, back up first.
