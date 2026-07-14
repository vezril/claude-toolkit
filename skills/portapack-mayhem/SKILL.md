---
name: portapack-mayhem
description: "Operating a HackRF One running PortaPack Mayhem firmware — the open-source, standalone touchscreen firmware (PortaPack → Havoc → Mayhem lineage) that turns a HackRF One + PortaPack into a computer-free RF tool. A query-answering reference distilled from the official wiki (github.com/portapack-mayhem/mayhem-firmware/wiki) + README, fetched 2026-07. Covers the hardware stack (PortaPack H1/H2/H2+/H4M models and compatibility, the H3-is-incompatible warning, HackRF One R1–R10C + HackRF Pro clock differences), power/battery per model, first-steps, firmware update (the three methods: hackrf_spiflash in HackRF mode, the hackrf.app WebUSB site, and the on-device Flash Utility; stable vs nightly; the .bin-vs-.ppfw.tar and SD-content-must-match-firmware rules), the SD card layout (CAPTURES/PLAYLIST/FREQMAN/APPS/SETTINGS folders, FAT32), the UI and the controls common to every app (frequency entry + digit mode, step sizes, IF bandwidth per modulation, the AMP/LNA/VGA gain stages and Satu% overload), the ~90-app catalog by category (Receivers, Transmitters, Transceivers, Recon, Capture, Replay, Looking Glass, Utilities, Games, Settings) with the flagship capture→replay IQ workflow (C16/C8 format, the ≤500 kHz-for-reliable-replay bandwidth rule, dropped samples, .PPL playlists), the Recon scanner and Looking Glass wideband waterfall, the antenna-length calculator, key Settings (TX Limit, reference source, converter, freq correction), and troubleshooting (won't boot, SD/version mismatch, clones, DC spike, cables, DFU recovery). Use to answer specific Mayhem/PortaPack questions — a control's meaning, gain staging, capturing and replaying a signal, running Recon, flashing firmware, an app's purpose, fixing a boot/SD problem — or to plan an on-device SDR capture/analysis. Dual-use RF hardware: receive broadly to learn; TRANSMIT (Replay, Jammer, the OOK/BLE/spoof apps) only on bands/power you are licensed or explicitly authorized to use. Sibling of the hackrf-one skill (the SDR + host tooling underneath)."
argument-hint: "[your PortaPack Mayhem question]"
license: MIT
---

# PortaPack Mayhem

**PortaPack Mayhem** is open-source firmware that turns a **HackRF One** SDR plus a **PortaPack** add-on (touchscreen + knob + buttons + audio) into a **standalone, computer-free RF instrument** — receive, decode, capture, and (where legal) transmit, all from the handheld device. Lineage: PortaPack (Jared Boone) → Havoc (furrtek) → **Mayhem** (community, GPL-2.0). This skill answers questions about operating it, distilled from the official wiki and README.

> ## Two rules first
>
> **1. TX is legally gated; RX generally isn't.** The wiki says it plainly: assume **transmitting is not legal** unless you're in an **ISM band within power limits** or hold an **amateur licence** for that spectrum. Mayhem ships apps (Replay, Jammer, GPS-Sim, BLESpam, the OOK/sub-GHz and spoofing family) that are trivially illegal to use against systems you don't own. **I'll explain the mechanics and always flag the legal line — I won't help jam, spoof, or interfere with systems you're not authorized to touch.** Set the **TX Limit** (Settings) as a guardrail, and use a dummy load / shielded setup for legitimate TX testing.
>
> **2. The LNA is fragile — −5 dBm max input.** Never hot-swap the antenna, never TX without an antenna, don't touch an exposed antenna while receiving (static), and don't RX near strong transmitters. A killed preamp is a repair, not a setting.

Load a reference for depth:

- **[references/hardware-getting-started.md](references/hardware-getting-started.md)** — PortaPack models (H1/H2/H2+/H4M) + **compatibility traps** (H3 is incompatible; clones), HackRF One revisions (R1–R10C, Pro), power/battery, **firmware update (three methods + the SD-content-must-match rule)**, the SD card layout, care/safety, and legality.
- **[references/ui-and-controls.md](references/ui-and-controls.md)** — the screen/menus, **frequency entry & digit mode**, step sizes, IF bandwidth per modulation, the **AMP/LNA/VGA gain staging** (+ Satu% overload), and the Settings worth knowing (TX Limit, reference source, converter, freq correct, calibration).
- **[references/apps-catalog.md](references/apps-catalog.md)** — the ~90-app catalog by category, and the flagship apps in depth: **Capture → Replay** (C16/C8, the ≤500 kHz replay rule, `.PPL` playlists), **Recon** (scanner), **Looking Glass** (wideband waterfall), and the antenna calculator.

## The mental model

- **Mayhem = the HackRF, minus the computer.** Same 1 MHz–6 GHz half-duplex 8-bit SDR as the [[hackrf-one]] skill, but driven from the touchscreen instead of host tools. Anything about the radio itself (specs, gain physics, the DC spike, `hackrf_spiflash`) is shared with that skill; this skill is the *on-device firmware* on top.
- **The SD card is half the firmware.** Captures, playlists, frequency databases, external apps, per-app settings, world maps — all live there. **Its content must match the firmware version** or apps go missing. FAT32, branded card.
- **Three gain knobs, one skill.** AMP (0/+14 dB) · LNA (0–40/8 dB) · VGA (0–62/2 dB). Start AMP off / LNA 16 / VGA 16; too much gain saturates the 8-bit ADC (broadband noise across the waterfall — watch **Satu%**).
- **Capture→Replay is the flagship, and it has a bandwidth rule.** Record IQ at **≤500 kHz** for reliable replay; wider captures drop samples and replay short/sped-up. Rolling-code targets won't replay — by design.
- **App icon color = maturity** (green solid → yellow → orange beta → 🔴 destructive).

## Fast answers

| Question | Answer |
|---|---|
| Power on/off? | H1: plug/unplug USB. H2/H2+: hold/click the knob. H4M: USB-C + power switch. |
| Update firmware? | `.ppfw.tar` via **Flash Utility** (on-device) or **hackrf.app** (WebUSB); `.bin` via `hackrf_spiflash` in HackRF mode for first-flash/recovery. **Match SD content to the version.** |
| Apps greyed out after update? | SD-card `APPS/` content doesn't match the firmware version. Re-copy the release's SD content. |
| Capture a signal to replay? | Capture app, **≤500 kHz** bandwidth, C16; then Replay the `.C16`. |
| Set the frequency precisely? | Long-press Select for **digit mode**, or short-press for the keypad. |
| Big spike in the middle? | DC offset (zero-IF artifact) — normal, ignore it. |
| Which PortaPack to buy? | H4M (recommended). **Never H3** — incompatible. |

## Gotchas

- **SD content version mismatch** is the cause of most "app missing / read error / greyed out" reports. Always update SD content with the firmware.
- **Clones vary wildly.** H3 (all variants) is unsupported; "H2+" ≠ "H2 Plus"; sellers swap chips silently. If you *paid for the firmware*, you were scammed — Mayhem is free.
- **Capture above ~1.25 MHz drops samples** — usable for spectrum inspection, not replay. Watch % Dropped Samples; use C8 to ease SD write speed.
- **Replay playlist delays block the UI thread** — a long delay looks like a freeze with no exit but reset.
- **Bad USB cables and cheap SD cards** cause a huge share of "won't flash / won't boot / can't record" issues; the wiki's stock advice is literally "try 5 different cables" and use a branded FAT32 card.
- **DFU only loads to RAM.** After a DFU recovery you must `hackrf_spiflash` the `.bin` to persist, or it reverts on next boot.
- **`hackrf_info` says "not manufactured by Great Scott Gadgets"** → you have a HackRF clone, not an original.

## Related

- [[hackrf-one]] — the SDR and host-side tooling *underneath* Mayhem (specs, gain physics, `hackrf_transfer`/`hackrf_sweep`, host SDR software). Read alongside this for anything about the radio itself.
- [[wifi-pineapple]] — the toolkit's other dual-use RF/wireless auditing device; same authorized-use-only discipline.
- [[network-security]] · [[secure-coding]] — the security context for RF work and handling captured data responsibly.
- [[information-theory]] — sampling, bandwidth, dynamic range, Nyquist (why the ≤500 kHz capture rule and 8-bit gain staging matter).

Sources: github.com/portapack-mayhem/mayhem-firmware — the **wiki** (PortaPack-Versions, Features, First-steps, Powering-the-PortaPack, Update-firmware, SD-Card-Content, Usage-cautions, Intended-Use-and-Legality, Main-Controls, User-interface, Settings, Applications and the per-app pages incl. Recon/Capture/Replay/Looking-Glass/Antennas) and the repo **README** — fetched 2026-07. Fast-moving community project: firmware filenames, app names, and version-specific behavior change between releases; verify against the wiki and your installed version. Regulatory rules are yours to check for your jurisdiction.
