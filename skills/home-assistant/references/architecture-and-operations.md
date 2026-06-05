# Home Assistant — architecture, install & operations

Install types, config structure, device ecosystems, data layer, and remote-access/security (HA docs).

## Install types
| Type | What | Updates | Add-ons | Notes |
|------|------|---------|---------|-------|
| **HAOS** (recommended) | embedded OS = Core + Supervisor + apps | one-click (Supervisor) | **yes** | Pi/Green/Yellow/VM/x86; UI backups; config `/config` |
| **Container** | Core in Docker (any OCI) | you do it | **no** | bring your own OS; Thread/Z-Wave (app-based) not OOTB |
| Supervised | Supervisor+add-ons on your Debian | mixed | yes | advanced/historical |
| Core | bare Python venv | manual | no | advanced/historical |

First-party hardware: Green (plug-and-play), Yellow (CM4 + radio), Connect ZBT-1/2 (Zigbee/Thread), Connect ZWA-2 (Z-Wave), Voice PE. Release cadence: monthly `YYYY.M.patch`.

## Configuration & structure
- `configuration.yaml` (main) + `default_config:` (pulls the standard bundle). Most integrations via **UI config flow** → stored in hidden **`.storage/`** JSON (don't edit by hand).
- **Secrets:** `!secret key` from `secrets.yaml` (not encrypted — protect/back up).
- **Splitting:** `!include f.yaml`; `!include_dir_list` (list, 1/ file), `!include_dir_named` (dict by filename), `!include_dir_merge_list` (merge lists), `!include_dir_merge_named` (merge dicts). Dir files must end `.yaml`. Labeled duplicate keys: `automation manual: !include_dir_merge_list automations/` alongside `automation ui: !include automations.yaml`.
- **Packages:** `homeassistant: packages: !include_dir_named packages/` — bundle a feature's automations+scripts+helpers+sensors in one file.
- **customize:** `homeassistant: customize: !include customize.yaml` to override entity attributes.
- **Core block:** `homeassistant:` → name, latitude/longitude, `unit_system`, `time_zone`.
- **Reload vs restart:** most domains reload live (Developer Tools > YAML; Settings > Restart > Quick reload). Config check runs on reload/restart, or `check_config`. Edit via Studio Code Server / File editor apps (HAOS) or the mounted folder (Container). Find the config dir under Settings > System > Repairs > ⋮ > System information.

## Device ecosystems
- **Zigbee:** **ZHA** (native, needs a coordinator radio) or **Zigbee2MQTT** (app → MQTT, widest device support). One per radio. Avoid running both on one stick.
- **Z-Wave:** **Z-Wave JS** via the Z-Wave JS UI app + controller stick. App-based (not OOTB on Container).
- **Matter/Thread:** Matter (IP, cross-vendor) over Thread (mesh, needs a Border Router). Thread app-based (not OOTB on Container).
- **MQTT:** broker (the **Mosquitto** add-on); **MQTT Discovery** auto-registers entities; birth/last-will; TLS. Backbone for ESPHome/Zigbee2MQTT/Tasmota/Node-RED.
- **ESPHome:** firmware for ESP32/ESP8266; YAML device configs; native API or MQTT; the ESPHome add-on builds/flashes. DIY sensors & Voice PE.
- **Bluetooth:** native + ESPHome BLE proxies for presence/sensors.
- IoT-class labels (Local Push/Poll, Cloud Push/Poll) tell you offline-dependence; prefer **local**.

## Add-ons / apps (HAOS/Supervised only)
Store under Settings > Apps. Home-lab staples: **Mosquitto** (MQTT), **Zigbee2MQTT**, **ESPHome**, **Node-RED**, **Studio Code Server**, **Samba**, **Z-Wave JS UI**, **MariaDB**, **InfluxDB**+**Grafana**, **Duck DNS** (Let's Encrypt + DDNS), **AdGuard**. On Container, run these as separate Docker containers ([[docker]]).

## Data layer — recorder / history / logbook
- **Recorder** = the DB (enabled via `history`). Default **SQLite** (`/config/home-assistant_v2.db`); MariaDB ≥10.3 / MySQL ≥8 / PostgreSQL ≥12 via `db_url` (no history migration on switch).
- Tune: `purge_keep_days` (default 10), `auto_purge`, `commit_interval` (**raise to ~30s on SD cards** to cut wear), `include`/`exclude` (domains/entities/globs/events — drop noisy entities like `sun.sun`). Actions: `recorder.purge`, `recorder.purge_entities`, `recorder.disable`/`enable`. Keep ≥1.5× DB size free.
- **Long-term statistics:** entities with `state_class` (measurement/total/total_increasing) → 5-min then hourly aggregates, kept forever; power Statistic/Statistics-graph cards and the **Energy** dashboard.
- **History** = past-state graphs; **Logbook/Activity** = human-readable events. Recorder excludes affect both.

## Backups (the #1 best practice)
HAOS: Settings > System > Backups — automatable, upload to Google Drive / Nabu Casa / network storage. **Back up before every update.** Container: back up the config folder (and DB) yourself.

## Remote access & security
- **Options (docs' order):** **Home Assistant Cloud / Nabu Casa** (easiest secure remote access, funds the project) → **TLS via Duck DNS + Let's Encrypt** → **VPN (WireGuard)** / SSH tunnel → reverse proxy (NGINX, common community route).
- **Harden:** monthly updates; **MFA/TOTP**; `secrets.yaml`; SSH key-only + `PermitRootLogin no` (Container/host); host hardening (CIS).
- **Webhooks** are auth'd only by an unguessable ID, `local_only` by default — never expose for locks/garage/safety; treat the ID as a secret.
- **Trusted networks** auth provider auto-logs-in by LAN IP — restrict to trusted ranges only.
- **IoT segmentation** (your pfSense/Omada): put smart devices on a separate **VLAN/SSID**, block their inbound and restrict outbound internet (many phone home), and allow only the cross-VLAN flows HA needs (e.g. HA → IoT VLAN for control, mDNS reflection for discovery). See [[network-engineering]] / [[network-security]].

## Extending HA
Power ladder: UI automations → blueprints → scripts/templates → **Node-RED / pyscript** → **custom integrations**. Custom components = Python in `custom_components/<domain>/` (`manifest.json`, `__init__.py`, platforms), often via **HACS** ([[python]]). APIs: **REST** (`/api/`, long-lived access token from Profile), **WebSocket** (real-time subscriptions/commands), **webhooks** (lightweight inbound trigger).
