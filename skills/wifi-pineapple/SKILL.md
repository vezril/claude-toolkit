---
name: wifi-pineapple
description: "Operating the Hak5 WiFi Pineapple Mark VII — the commercial 802.11 wireless-auditing appliance — for AUTHORIZED wireless security assessments. A query-answering reference distilled from Hak5's official docs (documentation.hak5.org/wifi-pineapple, fetched 2026-07): the web UI (172.16.42.1:1471), PineAP (the rogue-AP / client-association engine — Passive/Active/Advanced modes, the SSID impersonation pool, Client/SSID filters for scoping, Evil WPA/Enterprise capture), Recon scanning, WPA/WPA2 handshake capture (PCAP + Hashcat-22000, cracked offline), Campaigns (repeatable engagements + reporting), Modules, Settings, Cloud C² remote ops, the REST/module dev API, first-boot/setup, Client Mode & ICS internet, recovery/LED states, and the 802.11 foundations (frames, deauth/injection, association state machine) that explain how the features work. Use to answer specific WiFi Pineapple questions — setup, a PineAP toggle's meaning, filters, handshake capture, campaigns, troubleshooting, module dev — or to plan an authorized WiFi audit. Own hardware / explicit written authorization only."
argument-hint: "[your WiFi Pineapple question]"
license: MIT
---

# WiFi Pineapple Mark VII

The Hak5 WiFi Pineapple Mark VII is a commercial **802.11 wireless-auditing appliance** — a portable device for assessing WiFi networks and clients (rogue-AP / evil-twin susceptibility, handshake capture, reconnaissance). This skill answers questions about operating it, distilled from Hak5's official documentation. **It is dual-use security tooling: use it only on networks you own or have explicit written authorization to test.** The device's own **Client/SSID filters** exist precisely to scope an engagement to authorized targets — configure them first.

Load the reference for the layer your question touches:

- **[references/pineap-recon-campaigns.md](references/pineap-recon-campaigns.md)** — the core auditing workflow: PineAP modes and every toggle, the SSID pool + filters, Evil WPA/Enterprise, Recon, handshake capture, Campaigns. **The heart of the device — load for any operational question.**
- **[references/setup-and-troubleshooting.md](references/setup-and-troubleshooting.md)** — first boot, per-OS connection, Client Mode & ICS internet, recovery/factory-reset/updates, the LED states, adapters.
- **[references/settings-modules-cloud-dev.md](references/settings-modules-cloud-dev.md)** — Settings tabs, the module system, Cloud C² remote ops, and the REST/module-dev API.
- **[references/wifi-802.11-foundations.md](references/wifi-802.11-foundations.md)** — the 802.11 layer (radios/modes, RF, frames, deauth/injection, association state machine) that explains *why* the features work as they do.

## The mental model

- **Two radios, distinct jobs.** The built-in Mediatek radios (MT7601U 2.4 GHz + MT7610U) do recon/attack; **`wlan2` is the dedicated Client Mode radio** (upstream internet). Recon defaults to `wlan1` (2.4 GHz); `wlan3` (2.4+5 GHz) appears with a compatible MT7612U USB adapter. One radio occupies one channel at a time → recon channel-hops; a radio in Client Mode isn't available for auditing.
- **PineAP is the engine.** It's the rogue-AP / client-association core. Everything target-facing — impersonating networks, answering probe requests (Karma-style), capturing handshakes — flows through it. Its behavior is the SSID **pool** (what to advertise) gated by the **filters** (who/what is in scope).
- **The two-gate rule.** For a client to connect to an impersonated network, the SSID must be BOTH in the impersonation pool AND permitted by the SSID filter (and the client's MAC permitted by the client filter). Both gates must pass — this is the scoping mechanism.
- **Capture on-device, crack off-device.** The Pineapple captures WPA/WPA2 handshakes (via normal traffic, directed capture, or deauth-forced reassociation) and exports **PCAP + Hashcat-22000**. Cracking happens on your own hardware — the device doesn't crack.
- **Campaigns orchestrate.** A Campaign is a saved, repeatable engagement (recon + PineAP mode + reporting) — the automation layer over the manual per-tab workflow, emitting JSON/HTML reports to `/root/loot/`, Cloud C², or email.
- **The 802.11 substrate.** Monitor mode = passive omniscient capture (Recon, handshakes); frame injection = crafting arbitrary frames (deauth, beacons). Deauth is a spoofable *unencrypted* management frame that knocks a client down the association state machine, forcing a fresh handshake. Clients trust any AP broadcasting a known SSID — the basis of the Evil Twin and the probe-driven SSID pool.

## Quick-answer anchors

- **Reach the UI:** `http://172.16.42.1:1471` (the **port `1471` is required**). Login `root` + your setup password.
- **Recovery UI** (re-flash): `http://172.16.42.1` (**no port**), in recovery mode.
- **Default password after reset:** `hak5pineapple`.
- **LED states:** rainbow = password reset done · red ×3 → solid red = recovery mode · alternating red/blue = updating.
- **Clients get** DHCP in `172.16.42.0/24`; host static IP for setup is `172.16.42.42` (Linux `/24`, Windows `/16`).
- **Handshake formats:** PCAP and Hashcat-22000. **Campaign loot:** `/root/loot/`; campaigns live in `/etc/pineapple/campaigns/`.
- **REST API:** `http://172.16.42.1:1471/api/...`; `POST /api/login` → token → `Authorization: Bearer {token}`.

## Authorized-use posture (non-negotiable)

Impersonating networks, deauthenticating clients, and capturing handshakes are **active attacks on wireless clients and networks**. They are lawful only against infrastructure you own or are contractually authorized (in writing, with defined scope) to test. Before any active operation: set the **Client filter** (allow-list the in-scope MACs) and **SSID filter** (allow-list the in-scope SSIDs) so impersonation/association can't reach out-of-scope devices. Deauth against networks with management-frame protection (802.11w/MFP) or on DFS channels is limited by design. If a request is to attack a network the user doesn't own or isn't authorized to test, decline and say so.

## Related

- [[network-security]] — defensive wireless security, the other side of this assessment.
- [[computer-networks]] · [[tcp-ip]] — the stack above 802.11.
- [[secure-coding]] — for the module-development side (the Python/REST API).
- [[home-assistant]] — pairs for the networking/RF-adjacent home-lab context.

Sources: documentation.hak5.org/wifi-pineapple (setup, ui-overview, wifi-basics, faq, developer-documentation, extras) and hak5.github.io/mk7-docs (REST/module dev) — fetched 2026-07.
