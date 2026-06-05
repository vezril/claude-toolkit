# Home Assistant — automations, scripts & templating

The full automation/script vocabulary and Jinja2 templating (HA docs).

## Automation structure
```yaml
- alias: "Hallway light on motion at night"
  mode: restart            # single (default) | restart | queued | parallel
  triggers:                # OR — any one fires it
    - trigger: state
      entity_id: binary_sensor.hallway_motion
      to: "on"
  conditions:              # AND (default) — all must pass; see CURRENT state
    - condition: numeric_state
      entity_id: sun.sun
      attribute: elevation
      below: -4
  actions:                 # script syntax (runs top to bottom)
    - action: light.turn_on
      target: { entity_id: light.hallway }
      data: { brightness_pct: 60 }
```
Triggers OR'd, conditions AND'd, actions = script syntax. UI-built automations live in `automations.yaml`; toggle YAML mode in the editor.

## Trigger catalog (`- trigger: <type>`)
- **state** — entity changes; `from`/`to`/`not_from`/`not_to`, `attribute`, `for:` (hold — *not* persisted across restart). Bare `entity_id` fires on attribute changes too.
- **numeric_state** — value **crosses** `above`/`below` (equality excluded); `for`, `value_template`, threshold can reference another numeric entity.
- **time** — `at:` a time / input_datetime / timestamp sensor; `weekday:`.
- **time_pattern** — `hours/minutes/seconds`, `/5` = divisible-by, `*` = any.
- **sun** — `event: sunset|sunrise` + `offset`; docs recommend **elevation** via numeric_state for twilight.
- **mqtt** — `topic`, `payload`, `value_template` (topic/payload templated only at setup).
- **event** — `event_type` (+ `event_data`, `context`).
- **homeassistant** — `event: start|shutdown` (use for startup automations; shutdown gets ~20s).
- **template** — fires when a Jinja template flips false→true; `for`.
- **webhook** — POST/PUT/GET to `/api/webhook/<id>`; `local_only: true` default; data in `trigger.data`/`trigger.json`/`trigger.query`. Treat the ID as a password; never for safety-critical actions.
- **zone / geo_location** — person/tracker enter/leave a zone (needs GPS).
- **calendar** — event start/end + offset. **tag** — NFC scan. **device** — integration device events (build in UI, copy YAML). **conversation** — Assist sentence match (alternates `(a|b)`, optionals `[..]`, `{wildcards}`→`trigger.slots`).
- Cross-cutting: `id:` (→ `trigger.id` / `trigger` condition), `variables:`, `enabled: false`.

## Condition catalog (default AND; all see CURRENT state)
`and`/`or`/`not` (logical) · `state` (`for`, `match: any`, list, `attribute`) · `numeric_state` (`above`/`below` strict) · `template` (shorthand bare `"{{ }}"`) · `time` (`after`/`before`/`weekday`, can span midnight) · `sun` (`above_horizon`/`before: sunset`±offset) · `trigger` (`id`) · `zone`. Conditions can be embedded as action steps (false stops the sequence).

## Automation modes
| Mode | Behavior when re-triggered mid-run |
|------|-----------------------------------|
| `single` (default) | ignore new run + warn |
| `restart` | stop current, start fresh |
| `queued` | run after current finishes (in order); `max:` |
| `parallel` | run concurrently; `max:` (default 10) |
`max_exceeded:` log level (set `silent` to ignore). Throttle = `single` + `max_exceeded: silent` + trailing `delay`; serialize device access = `queued`.

## Script syntax (shared by automation actions & scripts)
- **action** — `action: light.turn_on`, `target:`, `data:`; shorthand scene `- scene: scene.movie`.
- **variables** — set/override vars for later templates.
- **condition** — inline test (stops the sequence/branch/iteration if false).
- **delay** — `"00:01:30"` or `{minutes: 5}` (templatable).
- **wait_template** — wait until template true (re-eval on referenced-entity change; `now()` won't re-trigger).
- **wait_for_trigger** — wait for any trigger; `timeout:` + `continue_on_timeout`; result in `wait.*`.
- **repeat** — `count:` / `for_each:` (item `repeat.item`) / `while:` / `until:`; loop var `repeat.{first,index,last}`.
- **if / then / else**, **choose** (if/elif/else: list of `conditions`+`sequence` + `default`), **sequence** (group), **parallel** (concurrent — no order guarantee; name vars distinctly), **stop** (`response_variable`, `error: true`), **event** (fire custom event), `continue_on_error: true`, `enabled: false`, `alias:`.

## Scripts, scenes, helpers, blueprints
- **Script** — `script:` → named entries with `sequence:` (omit wrapper for one action); `fields:` for callable inputs; same `mode`/`max` as automations; no trigger (called manually/automation/dashboard/Assist).
- **Scene** — snapshot of entity states; UI editor; `scene.turn_on` (with `transition`), `scene.create` for dynamic snapshots.
- **Helpers** — `input_boolean`, `input_number`, `input_text`, `input_datetime`, `input_select`, `input_button`, `counter`, `timer`, `schedule`, plus `template`, `group`, `min_max`, `threshold`, `derivative`, `utility_meter`, `statistics`, `trend`, `tod`, `bayesian`. First-class entities (usable in triggers/conditions/actions/templates and as dynamic thresholds).
- **Blueprint** — parameterized automation/script/template: `blueprint:` block (`name`, `domain`, `input:` each with a **selector**), body references `!input name`. Imported by URL from the forum; updating the blueprint updates all instances on reload. Start here as a beginner.

## Jinja2 templating
Delimiters `{{ expr }}` / `{% stmt %}`. **Every state is text → cast it.**
```jinja
{{ states('sensor.temperature') | float(0) }}
{{ is_state('binary_sensor.door', 'on') }}
{{ state_attr('light.kitchen', 'brightness') }}
{% if has_value('sensor.power') and states('sensor.power')|float(0) > 1000 %}High{% endif %}
{{ now().strftime('%H:%M') }}
{{ trigger.to_state.name }}            {# in automations #}
{{ area_entities('Living Room') | select('is_state','on') | list }}
```
- **State fns:** `states()`, `states.domain`, `state_attr()`, `is_state()`, `is_state_attr()`, `has_value()`, `this` (template entities), `trigger` (automations).
- **Org lookups:** `area_entities`/`device_entities`/`label_entities`/`floor_entities`/`integration_entities` (+ reverse).
- **Dates:** `now()`, `as_timestamp()`, `timestamp_custom`, `strftime`.
- **Where:** action `data`/`target`, `value_template`/`wait_template`, template triggers/conditions, **template entities** (`template:` → sensors/binary_sensors/lights), MQTT `value_template`, dashboard cards, notifications. **Limited templates** (no live entities, eval once) in trigger `topic`/`event_type`/`webhook_id` and `trigger_variables`.
- **Gotchas:** cast text with `float/int` + fallback; states > 255 chars must go in an attribute; debug in Developer Tools > Template; `now()` in `wait_template` won't re-trigger (use a Time/Date sensor).
