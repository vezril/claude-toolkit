# Settings, Modules, Cloud C², and the dev/REST API

Sources: documentation.hak5.org/wifi-pineapple/ui-overview (modules, settings, cloud-c) + developer-documentation, and hak5.github.io/mk7-docs for the real API/module depth (the docs-site dev page is now just a pointer to it). Fetched 2026-07.

## Settings (tabs)

- **Main:** Password, Timezone, **Button script**, filesystem/USB device viewing, Software updates, UI theme, **Cloud C² configuration**.
- **Networking:** **Client Mode** (connect as a normal client) · **Recon Interfaces** — default **`wlan1`** (2.4 GHz), **`wlan3`** available with a compatible USB adapter (2.4+5 GHz) · **USB Ethernet** (DHCP or static).
- **WiFi:** reconfigure the **Management Network** (management AP).
- **LEDs:** per-RGB color across four functions — **Default Off, Default On, Heartbeat, Network device**.
- **Advanced:** Beta **update channels** · **Censorship Mode** (obfuscate MACs/SSIDs/identifiable info) · **Cartography Mode** (network-topology / connected-clients visualization) · **Hotkeys** (single-press nav) · **Management Access** (restrict by interface type) · **Hostname**.
- **Help:** Help & Information · **Diagnostics file** generation · Licenses.

> Note: settings.md does **not** document a regulatory-domain/region+channel control, MAC-address viewing, CPU/RAM/disk resource monitoring, reboot/shutdown, factory reset from the UI, or DNS/gateway/ICS-interface config on that page — don't assert those as UI settings.

## Modules

- **What they are:** web-UI apps (mostly **community-contributed**) that wrap CLI tools in a GUI.
- **Two views:** the **Main Modules page** (installed modules as cards — click to open, trash icon to uninstall) and the **Modules tab** (available + updatable modules, each showing name/description/version/size/author + Install/Update).
- Approved community modules come from the WiFi Pineapple **module download site**, installable directly from the management UI.
- **Packages tab** (adjacent): CLI utilities + drivers when no module exists, used via SSH or the **Web Terminal** (backtick key or terminal icon).
- modules.md names no specific modules and no internal-vs-external install-location detail.

## Cloud C²

- **What it is:** a **self-hosted** web-based command-and-control suite for Hak5 gear — "pentest from anywhere." For remote engagements.
- **Connect:** (1) create the device in your Cloud C² instance; (2) download its configuration file from the C² server; (3) on the Pineapple, **Settings → Cloud C² card → "Choose File"** → upload it.
- **During C² operation:** the local UI is **paused**; temporarily re-enable via **"Access UI"** ("Local UI Bypass") to make local changes.
- **Remote capabilities:** start/stop recon scans, configure filters, view recon operations, central config/oversight.
- **Disconnect:** **"Remove Configuration & Reboot"**, or in Local UI Bypass use **"Remove Configuration File"** in the Cloud C² card.

## Developer / REST API (hak5.github.io/mk7-docs)

The docs-site developer-resources page now points to **https://hak5.github.io/mk7-docs/** for REST API, Python API, and module development.

**Module structure** (Angular UI + Python backend, under `projects/YourModuleName/src/`):
- **`module.json`** — metadata: `name`, `title`, `description`, `version`, `author` (bump `version` per release). *(The UI page/older refs call it `module.info`; the GitHub dev docs use `module.json`.)*
- `module.svg` (icon); Angular files `public-api.ts`, `lib/*.module.ts`, `lib/components/*.component.{html,ts,css}`, `lib/services/api.service.ts`, `assets/`.
- **`module.py`** — Python backend using the `pineapple.modules` library:
  ```python
  from pineapple.modules import Module, Request
  module = Module('ModuleName', logging.DEBUG)

  @module.handles_action('action_name')
  def handler_function(request: Request):
      return response_data

  if __name__ == '__main__':
      module.start()
  ```
  Handlers receive a `Request` (frontend data) and return a response. Python API areas: Helpers, Jobs, Logger, Modules.
- **Frontend → backend** via the Angular `ApiService`:
  ```typescript
  this.API.request({ module: 'ModuleName', action: 'action_name', custom_param: value },
                   (response) => { /* handle */ })
  ```
- **Build/package:** `build.sh` compiles the Angular project and can package a `.tar.gz` for install via the Management UI.

**REST API** (what the UI itself uses): served at **`http://172.16.42.1:1471/api/...`**; endpoint groups — Authentication, Notifications, Dashboard, Campaigns, PineAP, Recon, Settings, Modules, Generic.

**Auth (token):** `POST /api/login` with `{"username","password"}` → `{"token"}`. Every request needs a valid token via header **`Authorization: Bearer {token}`**.

**Contributing a module:** fork + clone **github.com/hak5/mk7-modules/** → develop per the Mark VII module docs → open a **Pull Request** → approved PRs are added to the module download site (installable from the device UI).

## Extras (hardware add-ons)

- **MK7 LED Mod** — add-on board with fun LEDs; proceeds support Kismet development.
- **MK7 Kismet Case** — a Kismet Special Edition enclosure for the Mark VII; supports Kismet development.
