---
name: flipper-unleashed
description: "Operating a Flipper Zero running the Unleashed Firmware — the community fork (DarkFlippers/@xMasterX) of the official Flipper firmware that removes the stock Sub-GHz region locks, adds many rolling-code and extra protocols, and bundles an expanded app pack. A query-answering reference distilled from the Unleashed docs (github.com/DarkFlippers/unleashed-firmware, dev branch) via multi-agent research, fetched 2026-07. Assumes familiarity with the base device (see the flipper-zero skill) and documents ONLY what Unleashed changes/adds. Covers: what Unleashed is and how it differs from stock; the build variants (base vs the `e`/extra-apps build); installation (web.unleashedflip.com Web Installer, Flipper Lab Web Updater, the app .tgz Custom channel, qFlipper install-from-file, manual update/ folder) and the RAM-based OTA self-update; the fbt/ufbt build system, hardware target f7, and VS Code; the Sub-GHz feature set that defines the fork — custom frequencies and hopper via subghz/assets/setting_user, the much larger static + dynamic/KeeLoq protocol table with save/send for rolling codes, the Sub-GHz Remote Prog manual-binding forms (FIX/COUNTER/SEED fields), the .txt map-file multi-button remote plugin, Counter Mode for rolling-code counter control, and LFRFID raw capture; DangerousSettings (the SEPARATE switch that extends the CC1101 past hardware limits — can damage hardware — distinct from the region-lock removal that's on by default); the extra bundled apps (Sub-GHz Bruteforce, LFRFID/iButton Fuzzers, EMV, NFC parsers, BadKB); the .fap app loader and application.fam manifest; universal IR remotes and .ir capture; expansion modules (the UART protocol, nRF24L01+ wiring with Sniffer/Mouse-Jacker, the Wi-Fi devboard for debugging); NFC/RFID notes (Picopass/Seader, T5577, Amiibo NTAG215, bank-card limits); key combos; custom name; and CLI/troubleshooting. Use to answer specific Unleashed questions — an install method, why an app won't load after update, adding a custom Sub-GHz frequency, what the `e` build is, a map-file format, Counter Mode, DangerousSettings, a manifest field. Unleashed intentionally removes the firmware guardrails, so the legal responsibility for what you transmit and which systems you touch is ENTIRELY the operator's — only act on equipment/bands you own or are authorized to use; this skill documents the firmware, not how to defeat access control you don't own. Sibling of flipper-zero, hackrf-one, portapack-mayhem."
argument-hint: "[your Unleashed / Flipper Zero question]"
license: MIT
---

# Flipper Zero — Unleashed Firmware

**Unleashed** is a community **fork of the official Flipper Zero firmware** (by the DarkFlippers team, lead @xMasterX) — "the most stable custom build," API-compatible with stock but with the **Sub-GHz region locks removed, many extra protocols (including rolling-code save/send), and an expanded app pack**. This skill documents **what Unleashed changes and adds**; for the base device and its subsystems, use the **[[flipper-zero]]** skill — everything there still applies.

> ## Read this first — the guardrails are off, so the responsibility is yours
>
> Stock Flipper firmware enforces region-specific Sub-GHz TX limits and blocks saving/replaying rolling-code remotes **on purpose** — those are regulatory/legal boundaries. **Unleashed removes them.** That means the firmware will happily let you transmit outside your legal bands or replay signals it shouldn't, and **nothing but your own judgment (and the CC1101's hardware limits) stops you.** Legal transmit bands and power are jurisdiction-specific (FCC/ISED/CE/…); cloning access credentials or replaying a remote for a system you don't own can be a crime. Unleashed's own stated boundary: *"intended solely for experimental purposes and is not meant for any illegal activities."*
>
> **I document how Unleashed's features work and flag the legal line; I won't provide walkthroughs for defeating access control, jamming, or transmitting where it's prohibited.** Operate only on equipment and frequencies you own or are explicitly authorized to test. There are **two separate unlocks** — don't confuse them (below).

Load a reference for depth:

- **[references/install-build-config.md](references/install-build-config.md)** — the `e` vs base build, **install methods** (Web Installer / Web Updater / app `.tgz` / qFlipper / manual), the RAM-based **OTA**, the **fbt/ufbt** build system, **key combos** (reset/DFU), **DangerousSettings**, custom name, CLI, and FAQ troubleshooting.
- **[references/subghz.md](references/subghz.md)** — the defining feature set: **custom frequencies/hopper** (`setting_user`), the expanded **static + dynamic/KeeLoq** protocol table, **Sub-GHz Remote Prog** (FIX/COUNTER/SEED binding forms), the **`.txt` map-file** multi-button remote, **Counter Mode**, and LFRFID raw capture — with the docs' own warnings and the honest "you can't clone your own car key" limit.
- **[references/apps-ir-modules.md](references/apps-ir-modules.md)** — the extra bundled apps, the **`.fap` loader + `application.fam` manifest**, universal **IR remotes** & `.ir` capture, **expansion modules** (UART protocol, **nRF24L01+** wiring, the **Wi-Fi devboard** for debugging), NFC/RFID notes (Picopass/Seader, T5577, Amiibo), and misc apps.

## The mental model

- **Unleashed = stock + guardrails removed + more protocols/apps.** The device, menus, and subsystems are the same ([[flipper-zero]]); Unleashed changes *policy* (region unlock, rolling-code save/send) and *breadth* (protocol table, app pack), not the underlying radios.
- **Two different frequency unlocks — keep them straight.** (1) **Region locks are off by default** — software; lets you *select* frequencies stock would block. (2) **DangerousSettings** is a *separate* opt-in file switch that pushes the **CC1101 past its hardware spec** and **can physically damage the radio** — most users never touch it.
- **The `e` build bundles the apps.** Base = firmware only; the **`e` ("extra")** release ships the app pack (`xMasterX/all-the-plugins`) pre-loaded. If an app is missing, you likely have the base build or an API-version mismatch.
- **Rolling-code features are for receivers you can re-enroll, not vehicles.** Counter Mode / Remote Prog let a remote you've *enrolled* coexist with the original on a fixed receiver (gate/barrier). Reading a car key desyncs it and needs dealer tools to fix — the FAQ says so plainly.
- **It's still a Flipper.** NFC crypto limits, the LF-vs-HF distinction, BadUSB scope, the SD-card/`.fap` model — all identical to stock. Unleashed doesn't break bank cards or DESFire.

## Fast answers

| Question | Answer |
|---|---|
| Which build should I have? | The **`e`** release — firmware + extra apps. |
| Install / update? | `web.unleashedflip.com` (Chromium), or qFlipper "Install from file" with the `.tgz`, or the app's **Custom** update channel. |
| Add a custom Sub-GHz frequency? | Edit `subghz/assets/setting_user` (rename off `.example`): `Frequency: 928000000` / `Hopper_frequency: …`. |
| Unlock frequencies beyond hardware spec? | **DangerousSettings** (`subghz/assets/dangerous_settings`, false→true) — **can damage the radio**; rarely needed. |
| Build a multi-button remote? | A `.txt` map in `subghz_remote/` (UP/DOWN/LEFT/RIGHT/OK → `.sub` paths + labels). |
| Clone my own car key? | **No** — rolling-code read desyncs it; re-pairing needs dealer tools. |
| App won't load after update? | API-version mismatch — align the app pack with the firmware (the `e` build keeps them matched). |

## Gotchas

- **Region-off ≠ DangerousSettings.** Everyday use never needs the dangerous switch; enabling it risks hardware damage for frequencies almost nobody needs.
- **The legal load moved to you.** Stock stops illegal TX for you; Unleashed doesn't. "It let me transmit" is not "it was legal."
- **`e` vs base confusion** is the usual "why is app X missing." Check your build and API version.
- **Counter Mode is experimental and receiver-specific** — the docs warn against using it on equipment you can't re-enroll.
- **CLI baud is 115200** in the Unleashed FAQ's examples (PuTTY/screen). Close other qFlipper/Flipper-Lab tabs before a web tool will connect.
- **The Wi-Fi devboard here is for debugging** (DAP Link / Black Magic), not Wi-Fi attacks — Marauder-style ESP32 work is separate third-party firmware, out of scope.

## Related

- [[flipper-zero]] — **read this first.** The base device, all subsystems (Sub-GHz/NFC/RFID/IR/iButton/GPIO/BadUSB/U2F), controls, and the official-firmware behavior Unleashed modifies.
- [[hackrf-one]] · [[portapack-mayhem]] — the raw-SDR alternatives when you need real signal capture/analysis beyond known remote protocols.
- [[wifi-pineapple]] — the Wi-Fi-specific auditing sibling; same authorized-use-only discipline.
- [[network-security]] · [[secure-coding]] — the defensive context for RF/access-control work and handling captured data responsibly.

Sources: github.com/DarkFlippers/unleashed-firmware `dev` — `ReadMe.md` and `documentation/` (HowToInstall, OTA, HowToBuild, fbt, HardwareTargets, FAQ, KeyCombo, DangerousSettings, CustomFlipperName, SubGHzSettings, SubGHzSupportedSystems, SubGHzRemoteProg, SubGHzRemotePlugin, SubGHzCounterMode, LFRFIDRaw, AppsOnSDCard, AppManifests, UniversalRemotes, InfraredCaptures, ExpansionModules, NRF24, devboard/, MultiConverter, BarcodeGenerator, SentrySafe) — fetched 2026-07 via parallel research agents. A few facts (f7 = STM32WB55, the exact `/ext/apps` tree, the ESP32-S2 devboard chip, the ~8-char name limit) are general knowledge flagged in the references, not quotable from these docs. Custom firmware and regional RF law both change — verify against the live repo and your local regulations. Unleashed is unaffiliated with Flipper Devices.
