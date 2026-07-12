# PineAP, Recon, Handshakes, Campaigns — the core workflow

Source: documentation.hak5.org/wifi-pineapple/ui-overview (fetched 2026-07). Exact toggle/field names preserved. **Authorized targets only — set the filters first.**

## UI & Dashboard

- Management UI at `http://172.16.42.1:1471` (port **1471** required; omitting it yields a blank page). Login `root` + setup password.
- **Title bar:** firmware version, Notifications, Informational Messages, **Web Terminal** ("a fully featured Bash shell" in-browser — no SSH needed), context menu. Notifications have five levels: Info / Warning / Error / Success / Unknown. Informational Messages flag misconfigurations and suggest fixes.
- **Sidebar:** system + downloaded modules; **Show More** expands full names.
- **Dashboard cards:** Status (CPU, RAM, Disk, Client Stats) · **Connected Clients** (MAC, IP, Connected Time; per-client **Kick**) · Notifications · **Campaigns** (status/name/type + enable-disable toggles) · **Wireless Landscape** (latest-recon at-a-glance).

## PineAP — rogue-AP / client-association engine

The heart of the device: creates access points to engage target clients.

**Three daemon modes:**
- **Passive** — collects nearby AP data; accepts connections to Open/WPA/Enterprise SSIDs; does **not** advertise other APs.
- **Active** — collects AP data; **actively advertises all impersonated SSIDs**; answers permitted client probe requests (Karma-style).
- **Advanced** — hand-configure the individual toggles below.

**Event/behavior toggles (exact names):**
- **PineAP Event Logging** — log probe requests, associations, disassociations to the system event log.
- **Notifications** — UI notification when a client connects/disconnects.
- **SSID Pool Capture** — auto-add discovered SSIDs (from sniffed probe requests + recon) into the pool.
- **Broadcast SSID Pool** — advertise the collected SSIDs; single BSSID, or a pseudo-random BSSID per SSID.

**SSID Impersonation Pool** — the networks to advertise; populated manually or automatically (with SSID Pool Capture on). Advertised SSIDs appear in nearby devices' network lists.

**Target-facing AP modes:**
- **Basic Open AP** — one visible or hidden unencrypted network.
- **Impersonate All Networks** — respond for all SSIDs permitted by the filter config (the Karma catch-all, still filter-bounded).

**The two Filters — the scoping mechanism:**

| Filter | Allow mode | Deny mode |
|---|---|---|
| **Client Filter** | only listed MACs may connect | all MACs except listed |
| **SSID Filter** | only listed SSIDs permitted | all SSIDs except listed |

**Two-gate rule:** a client connects only if the SSID is in the pool AND permitted by the SSID filter, AND its MAC is permitted by the client filter. Use allow-lists to keep an engagement inside its authorized scope.

**Evil WPA / Evil Enterprise (advanced):**
- **Evil WPA** — impersonate WPA/WPA2; capture **partial handshakes** (even when the client can't fully authenticate), exported as PCAP or hashcat format for offline cracking.
- **Evil Enterprise (WPA-EAP)** — needs generated SSL certs; three auth methods: **Any** (accepts all; captures MSCHAPv2 hashes or GTC creds), **MSCHAPv2** (captures challenge hashes without completing auth), **GTC** (captures plaintext username/password).

**Client tabs:** **Connected Clients** (MAC, IP, associated SSID, manual kick) · **Previous Clients** (historical associations).

## Recon — wireless scanning

- At-a-glance current wireless landscape: discovered APs + their associated clients, plus independently discovered clients. Per network (tagged from beacon packets): encryption/security, channel, traffic data, signal strength, associated clients.
- **AP↔client view:** expand a row with **+** (collapse **−**); Recon Settings **"Expand all client lists"** auto-expands.
- **Search/display:** Search filters by SSID / BSSID / MAC; sortable columns; **Page Size** control.
- **Recon Settings** (gear on the Settings card): scan location, displayed columns, **"Highlight Active Devices"** (configurable activity time + color).
- **Actions on a selected AP/client** (side menu): **Capture Handshakes**, **Clone**, **add MAC to Filters**, **Deauthenticate** — plus **Deauthenticate All Clients**. Limitations noted for **MFP** (802.11w management-frame protection) and **DFS** channels.
- The docs do **not** expose explicit continuous-vs-one-off toggles or a scan-duration/dwell/band setting — Recon is a live, continuously-updated landscape.

## Handshakes (WPA/WPA2)

Capture methods:
- **Automatic** — handshakes are part of normal join/refresh traffic; collected during recon scans.
- **Directed** — select a target, choose **Capture Handshakes**; the device parks on the target's channel and waits for handshake packets.
- **Deauth-triggered** — **Deauthenticate All Clients** or a specific client forces reconnection, increasing capture odds.
- **Evil WPA** — captures partial handshakes a client presents even without full auth.

Handshakes tab: listed in **PCAP** and **Hashcat 22000** formats, labeled by source (**Recon Capture** vs **Evil WPA/2 Twin**). **The device captures + stores; cracking is done offline** — download the PCAP/Hashcat-22000 and crack on your own hardware (hashcat). (The pages don't spell out on-disk file paths or PMKID as a named feature.)

## Campaigns — repeatable engagements

A Campaign combines recon + PineAP mimicry + automated reporting into one repeatable config.

**Three modes:**
1. **Reconnaissance – Monitor Only** — passively observe client/AP activity in a defined region.
2. **Client Device Assessment – Passive** — passive PineAP; mimic APs only when directly requested; finds devices vulnerable to basic rogue-AP/evil-twin.
3. **Client Device Assessment – Active** — active PineAP broadcasting a (dynamically updatable) SSID pool; finds devices susceptible to advanced attacks.

**Management:** a table (status, name, creation date, type) with enable/disable toggles and an edit/delete menu. Each campaign is a **shell script**, editable via a dedicated script editor. Campaigns live in **`/etc/pineapple/campaigns/`**; base template **`/etc/pineapple/campaign-template.sh`**.

**Reporting:** stored/delivered to local disk (**`/root/loot/`**), **Cloud C²**, or **email (configured SMTP)**. Formats **JSON** (tooling) or **HTML** (tables + optional base64-embedded handshake downloads). Download/delete from the **Reports** tab.
