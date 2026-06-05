---
name: home-assistant
description: Home Assistant — the open-source, local-first home automation platform — distilled from the official docs (home-assistant.io). Covers the core model (integrations, devices, entities & the state machine, states vs attributes, domains, actions/services, the event bus, areas/floors/labels/zones), install types (Home Assistant OS — recommended — vs Container; Supervised/Core as advanced), configuration (configuration.yaml vs UI config & .storage, secrets, !include/packages/splitting, customize, reload vs restart, config check), automations (triggers/conditions/actions and automation modes single/restart/queued/parallel), scripts/scenes/helpers/blueprints, Jinja2 templating, dashboards (Lovelace), the device ecosystems (Zigbee/ZHA & Zigbee2MQTT, Z-Wave JS, Matter/Thread, MQTT/Mosquitto, ESPHome, Bluetooth), add-ons/apps & Supervisor, recorder/history/logbook & long-term statistics, voice (Assist), energy, backups, and remote access/security (Nabu Casa, TLS, VPN, IoT segmentation). Use when configuring or troubleshooting Home Assistant, writing automations/scripts/templates, choosing integrations or device protocols, structuring config, securing remote access, or extending HA. Pairs with network-engineering/network-security (IoT VLANs/remote access), docker (Container install), python (custom components), and secure-coding.
---

# Home Assistant

The open-source, **local-first** home-automation platform — from the official docs (home-assistant.io/docs). HA runs on **your** hardware so the home keeps working offline and your data stays home; it's a project of the **Open Home Foundation** (values: privacy, choice, sustainability), sponsored by Nabu Casa, Apache-2.0 core.

Cross-links: [[network-engineering]] / [[network-security]] (IoT VLAN segmentation, secure remote access — your pfSense/Omada setup), [[docker]] (the Container install), [[python]] (custom components, the dev model), [[secure-coding]] (webhooks/remote exposure), [[site-reliability-engineering]] (backups, ops).

## The core model (learn this first)

HA is built from a small set of concepts — get them straight and everything else follows:

- **Integration** — *"pieces of software that allow Home Assistant to connect to other software and platforms."* Each is a Python component. Two flavors: **integration domains** (provide their own functionality — Hue, Matter, ZHA) and **entity domains** (building blocks others use — `light`, `switch`, `sensor`, `climate`).
- **Device** — *"a logical grouping for one or more entities,"* usually one physical thing (a motion sensor device exposes motion + temperature + lux entities).
- **Entity** — *"a sensor, actor, or function… Entities have states."* The basic data unit; lives in a device. Entity ID = `<domain>.<object_id>` (e.g. `light.bed_light`).
- **State & attributes** — *"the state object is the current representation of the entity… Each entity has exactly one state… entities can store attributes related to that state."* For "light on at 50% orange": **state** = `on`; **attributes** = brightness/color. **Every state is text** — `states('sensor.x')` returns `'22.5'`, so `| float(0)` before math. Special states: `unknown`, `unavailable`. State object fields: `state`, `last_changed`, `last_updated`, `last_reported`, `attributes`, `context`.
- **Domain** — the prefix before the `.`; all entities/actions belong to one (`light`, `binary_sensor`, `cover`, `media_player`, …).
- **Action** (formerly **service**) — `<domain>.<name>` (e.g. `light.turn_on`) with a `target:` (entity/device/area/label/floor id) and `data:` (params). The docs/UI now say **action**; "service" persists in legacy YAML, `service_data`, and the `call_service` event — know both terms.
- **Event bus** — *"the core of Home Assistant… allows any integration to fire or listen for events."* All entities emit `state_changed`; automations and integrations react. **Context** links cause→effect (what triggered what).
- **Organize early:** **areas** (one per device — used as automation targets and auto dashboards), **floors** (group areas), **labels** (many-to-many cross-cutting targets), **zones** (GPS regions). Good areas/naming make targeting and dashboards scale.

## Install types

- **Home Assistant OS (HAOS)** — *the recommended type:* an embedded OS bundling Core + **Supervisor** + **apps (add-ons)**, with one-click updates and UI backups. Run on a Pi/Green/Yellow/VM/x86. Config at `/config`.
- **Container** — Core in Docker (any OCI runtime). You own updates/OS; **no add-ons**, and some integrations needing apps (**Thread, Z-Wave**) aren't out-of-the-box. Pairs with [[docker]].
- **Supervised / Core (venv)** — historical/advanced (Supervisor on your own Debian / bare Python, no add-ons).

## Configuration

- **`configuration.yaml`** is the main file, but **most integrations are configured in the UI** (config flow), persisted in the hidden **`.storage/`** (JSON — don't hand-edit). `default_config:` pulls in the standard bundle (why modern config files are tiny).
- **`secrets.yaml`** + `!secret key` keeps secrets out of the main file — but it is **not encrypted** (back it up safely).
- **Split & modularize:** `!include file.yaml`, `!include_dir_list/named/merge_list/merge_named dir/`, labeled duplicate keys (`automation manual:` + `automation ui:`), and **packages** (`homeassistant: packages:`) to bundle a feature's automations+scripts+helpers+sensors.
- **`customize:`** overrides entity attributes (friendly_name, icon, device_class) you don't otherwise control.
- **Reload vs restart:** most config reloads without a restart (Developer Tools > YAML, or Settings > Restart > Quick reload); a **config check** runs automatically on reload/restart (or `check_config`). Edit via the Studio Code Server / File editor apps (HAOS) or the mounted folder (Container).

## Automations, scripts, templating

The heart of HA — **trigger → condition → action**, automation **modes**, scripts/scenes/helpers/blueprints, and Jinja2 templating. See `references/automations-and-templating.md` for the full vocabulary. Headlines:

- **Automation** = triggers (OR'd — any fires it) + optional conditions (AND'd) + actions (script syntax). Modes: **single** (default), **restart**, **queued**, **parallel** (`max:`).
- **Triggers**: state, numeric_state (threshold *crossing*), time/time_pattern, sun (prefer elevation), mqtt, event, template, webhook (treat the ID as a secret), zone, calendar, conversation (voice), device, homeassistant. (`for:` doesn't survive a restart.)
- **Conditions** see only the *current* state (race-condition caveat); types: state, numeric_state, template (shorthand `"{{ }}"`), time, sun, trigger, zone, and/or/not.
- **Scripts** = a reusable `sequence` (no trigger); the script syntax (`choose`, `if/then`, `repeat`, `wait_for_trigger`, `delay`, `parallel`, `stop`, `variables`) is shared with automation actions.
- **Scenes** snapshot entity states; **helpers** (`input_*`, `counter`, `timer`, `schedule`, `template`, `group`…) are first-class entities; **blueprints** are parameterized, reusable automations/scripts (start here as a beginner).
- **Templating** = **Jinja2**: `states()`, `is_state()`, `state_attr()`, `now()`, the `trigger` var, area/device/label lookups. Always cast text states with `float/int` + fallback; use `has_value`. Template entities (`template:`) compute new sensors.

## Dashboards (Lovelace)

The UI you and your family see — auto-generated to start; build your own visually (drag-and-drop) or in **YAML mode**. Structure: dashboard → **views** (Sections/Masonry/Panel/Sidebar) → **cards** (~40: entities, tile, gauge, history-graph, picture-glance, thermostat, map, markdown, conditional, stacks…) + badges. **Custom cards** via **HACS** (third-party community store). Pairs with [[ux-design]] for layout.

## Device ecosystems (the home-lab core)

Add via UI config flow (often auto-discovered). Prefer **local** integrations (offline, private) over cloud. The big protocols:

- **Zigbee** — **ZHA** (native, talks to a coordinator radio) *or* **Zigbee2MQTT** (separate app bridging to MQTT, broader device support). Pick one per radio.
- **Z-Wave** — **Z-Wave JS** (via the Z-Wave JS UI app + a controller stick). App-based → not OOTB on Container.
- **Matter / Thread** — Matter (IP, cross-vendor) over **Thread** (low-power mesh, needs a border router). Thread is app-based → not OOTB on Container.
- **MQTT** — generic pub/sub via a broker (the **Mosquitto** add-on); **MQTT Discovery** auto-creates entities. Backbone for ESPHome/Zigbee2MQTT/Tasmota/Node-RED.
- **ESPHome** — OHF firmware for ESP32/ESP8266; YAML-defined local sensors/devices; the DIY-sensor and Voice foundation.
- **Bluetooth** — native + BLE proxies (via ESPHome) for presence/sensors.

## Add-ons / apps & Supervisor

**Apps (add-ons)** are standalone packages — **HAOS/Supervised only**, installed from the store. Staples for a home lab: **Mosquitto** (MQTT), **Zigbee2MQTT**, **ESPHome**, **Node-RED** (visual flows), **Studio Code Server**, **Samba**, **Z-Wave JS UI**, **MariaDB**, **Duck DNS** (TLS), **Grafana/InfluxDB**. On Container you run these as separate Docker containers instead.

## Data, voice, energy, backups

- **Recorder/History/Logbook** — Recorder is the DB (SQLite default; MariaDB/Postgres for scale). Tune `purge_keep_days`, `commit_interval` (raise to ~30s on SD cards), and `include`/`exclude` noisy entities. **Long-term statistics** (entities with `state_class`) power the Statistics cards and Energy.
- **Assist (voice)** — local or Cloud pipeline (wake word → STT → intent → TTS); expose entities, add aliases, `conversation` trigger ties voice → automations.
- **Energy dashboard** — grid/solar/battery/gas/water from statistics-bearing sensors.
- **Backups** — the #1 best practice; UI-managed/automatable on HAOS (back up before every update); Container = back up the config folder.

## Remote access & security

- **Options (docs' order):** **Home Assistant Cloud (Nabu Casa)** — easiest secure remote access (and funds the project); **TLS via Duck DNS + Let's Encrypt**; **VPN** (WireGuard) or SSH tunnel; reverse proxy (NGINX) as a common community route.
- **Harden:** keep HA updated monthly; **MFA/TOTP**; use `secrets.yaml`; **never expose admin/webhooks unauthenticated** to the internet (webhooks are auth'd only by an unguessable ID — `local_only` by default; never use for locks/garage). Trusted-networks auto-login only for trusted LAN ranges.
- **Segment IoT** ([[network-security]]/[[network-engineering]]): put smart devices on a **separate VLAN/SSID**, restrict their internet egress, and allow only the cross-VLAN access HA needs — directly applicable to your pfSense/Omada gear.

## Extending HA

Power ladder (least → most): **UI automations → blueprints → scripts/templates → Node-RED / pyscript → custom integrations**. Custom components are **Python** in `custom_components/<domain>/` (often via HACS). APIs: **REST** (`/api/`, long-lived token), **WebSocket** (real-time subscriptions), **webhooks** (lightweight inbound). ([[python]])

## Anti-patterns

- Editing **`.storage/`** by hand (UI-managed config); over-using YAML when the UI config flow is the supported path.
- Forgetting **state is text** (math on a string) or not handling `unknown`/`unavailable`.
- Cloud integrations where a **local** one exists (breaks offline, leaks data); mixing IoT with trusted devices on one **flat** network.
- Exposing HA/webhooks to the internet **without TLS/auth/MFA**; webhooks for safety-critical actions; reusing a webhook ID from a blog.
- Wrong automation **mode** (e.g. `single` where you needed `restart`); relying on `for:` across restarts; assuming conditions see the trigger's past state (they see *now*).
- No **backups** (or not before updates); recording every noisy entity → bloated DB on an SD card.
- Hand-rolling a custom component when a template/blueprint/Node-RED flow would do.

## Always-apply

1. Think **integration → device → entity → state(+attributes)**; target by **area/label**; remember **state is text** (cast it).
2. **HAOS** unless you have a reason for Container; **UI/config-flow first**, YAML (with `!include`/packages/secrets) where needed.
3. Automations: triggers OR'd, conditions AND'd (see *now*), the right **mode**; start from **blueprints**; secure **webhooks**.
4. Prefer **local** device integrations; **MQTT/ESPHome/Zigbee** for a DIY local stack; **segment IoT** onto its own VLAN.
5. **Back up before every update**, keep HA updated, use **MFA + TLS/Cloud/VPN** for remote access — never raw-expose admin.

## How to use the references

- **`references/automations-and-templating.md`** — the full trigger/condition/action catalog, automation modes, the script syntax (choose/if/repeat/wait/parallel/stop), scenes/helpers/blueprints, and Jinja2 templating patterns.
- **`references/architecture-and-operations.md`** — install types, configuration & splitting/packages, the device ecosystems, add-ons, recorder/statistics tuning, backups, and remote-access/security setups.

## Related

- [[network-engineering]] / [[network-security]] — IoT VLAN segmentation and secure remote access (pfSense/Omada).
- [[docker]] — the Container install and running add-on equivalents as containers.
- [[python]] — custom components and the developer model; [[secure-coding]] — webhook/remote-exposure safety.
- [[site-reliability-engineering]] — backups, monitoring, recorder hygiene; [[ux-design]] — dashboard layout.
- Source: official Home Assistant documentation (home-assistant.io/docs), Open Home Foundation / Apache-2.0.
