# PortaPack Mayhem — hardware, power, firmware, SD card, safety

Source: the Mayhem wiki (github.com/portapack-mayhem/mayhem-firmware/wiki) — pages *PortaPack-Versions*, *Features*, *First-steps*, *Powering-the-PortaPack*, *Update-firmware*, *SD-Card-Content*, *Usage-cautions*, *Intended-Use-and-Legality* — and the repo README, fetched 2026-07.

## What Mayhem is

PortaPack Mayhem is **firmware** for the **PortaPack** — a touchscreen + buttons + audio add-on board that mounts on a **HackRF One** SDR and makes it a **standalone, computer-free** RF instrument. Lineage: **PortaPack** (Jared Boone / ShareBrained) → **Havoc** (furrtek) → **Mayhem** (community). GPL-2.0. It bundles the HackRF firmware, so *you don't separately flash HackRF firmware*.

## The hardware stack (two boards)

**The SDR (HackRF One)** — 1 MHz–6 GHz, half-duplex, 2–20 Msps, 8-bit. Revisions matter mainly for the clock:

| Board | Notes |
|---|---|
| HackRF One **R1–R8** | Original (Si5351C). CLKIN/CLKOUT user-configurable 4 kHz–60 MHz via Settings → Radio. |
| HackRF One **R9** | Si5351A clock — **fixed 10 MHz**, software on/off only. |
| HackRF One **R10C** | R9 with a **USB-C** connector (OpenSourceSDRLab, bundled with H4M). Detected as R9. |
| **HackRF Pro** | GSG's 2025 upgrade: 100 kHz–6 GHz, TCXO, iCE40 FPGA, up to 40 Msps (4-bit) / 16-bit extended precision. Mayhem supports it (PRALINE target). |

Max RX power **−5 dBm** (up to +10 dBm safe only with the RX amp disabled); exceeding risks permanent LNA damage. TX power is uneven by band (5–15 dBm low, 13–15 dBm at 2.15–2.75 GHz, down to −10–0 dBm at 4–6 GHz).

**The interface (PortaPack)** — many clones exist; compatibility varies:

| Model | Screen | Power on/off | Battery |
|---|---|---|---|
| **H1** (R1/R2) | 2.4" | Instant on USB plug; off = unplug | none (USB only) |
| **H2 / H2M** | 3.2" | **Hold** middle button (knob) a few seconds | optional LiPo, Micro-USB charge |
| **H2+** (R2–R5) | 3.2" | Most: **click** knob on, **double-click** off | optional LiPo |
| **H4 / H4M** | 3.2" | **USB-C**, dedicated power switch | optional LiPo, on-screen % |

> ⚠️ **Buyer/compat traps (from the wiki):** all **H3** variants are **incompatible — never buy them**. "H2+" and "H2 Plus" are *different* devices despite the name. Clone makers swap components without notice, so confirm latest-release compatibility with the seller. If a listing ships its own old firmware or custom install steps, it's probably **not** mainline-compatible. **H4M** is the recommended current model. If you *paid for the firmware itself, you were scammed* — Mayhem is free.

## Powering & battery (H2)

H2 + HackRF draws ~250 mA idle to ~550 mA peak (audio, RX). A 2500 mAh LiPo → ~4–5 h runtime; charges in 3–4 h (cable quality matters). Some H2 units emit RF interference *while charging* from the onboard charger IC — a TP4056 swap fixes it. Standby draw is tiny (~52 µA), so you needn't disconnect the battery.

## First steps (do these before anything else)

1. **Identify your exact model** (Settings, the wiki version table) — it dictates flashing and power behavior.
2. **Prepare the SD card** — FAT32 (or exFAT), branded/quality card. Many features need it.
3. **Read the safety + legality notes below.**
4. Power on per your model, and confirm the main menu appears.

## Firmware update (three methods)

Get firmware from the GitHub **releases** page — **stable** (`releases/latest`) or **nightly**. Two artifacts matter: the firmware itself, and `..._COPY_TO_SDCARD.(zip/7z)` (the SD-card content). **You need a working Mayhem device to use methods 2 and 3.**

1. **HackRF mode + `hackrf_spiflash`** (classic / recovery): on the PortaPack pick "HackRF" mode, then on the host `hackrf_spiflash -w portapack-h1_h2-mayhem.bin`, reboot. First-flash and recovery path. Windows has `mayhem_flasher.bat`.
2. **[hackrf.app](https://hackrf.app) website** (WebUSB): stay in Mayhem mode, connect a **data** USB cable, "Manage Firmware" → pick version. Only for stable ≥ v2.0.1 / recent nightlies. Also updates external apps.
3. **Flash Utility app** (offline, on-device): copy firmware to SD, run Utilities → Flash Utility. `.bin` = flash only (first-flash/recovery); **`.ppfw.tar` = flash + external SD apps (preferred)**.

> **The #1 upgrade gotcha:** **SD-card content must match the firmware version.** External apps (`.ppma` in `APPS/`) only run if their version equals the running firmware — mismatch = missing/greyed-out apps. When downgrading, match SD content too. Mayhem contains HackRF firmware; don't flash HackRF firmware separately. You essentially can't brick it — DFU recovery always exists (but DFU only loads to RAM; you must then `hackrf_spiflash` to persist).

## SD card layout

FAT32/exFAT, extract the release's SD content to the **root** (not a subfolder, not the .zip itself). Key folders:

| Folder | Holds |
|---|---|
| `APPS` | External apps (`.ppma`) offloaded from flash |
| `CAPTURES` | IQ captures (`.C16`/`.C8` + `.TXT` metadata) from Capture |
| `PLAYLIST` | `.PPL` playlists for Replay |
| `FREQMAN` | Frequency database files (loaded by many apps) |
| `FIRMWARE` | `.bin` update files |
| `SETTINGS` | Per-app `.ini` config (e.g. `rx_capture.ini`, `tx_replay.ini`) |
| `LOOKINGGLASS` | Scan-range preset `.TXT` (ranges ≥240 MHz wide, from 10 MHz) |
| `WHIPCALC` | `ANTENNAS.TXT` for the antenna calculator |
| `ADSB`/`AIS`/`APRS`/`AUDIO`/`BLERX`/`BLETX`/`GPS`/`LOGS`/`DEBUG` | app data & logs |

## Care & usage cautions (the LNA is fragile)

- **Never hot-swap the antenna** (connect/disconnect with power on).
- **Never transmit without an antenna** connected.
- **Don't touch an antenna's exposed metal** while receiving — static can kill the LNA.
- **Don't receive near high-power transmitters**, even off your tuned frequency.
- Diagnostic for a suspected-dead LNA: listen to local broadcast with AMP on *and* off; capture+replay a non-rolling-code signal both ways. A damaged preamp IC is replaceable (wiki: *preamplifier-ic-replacement*).

## Legality (read before you transmit)

The wiki is explicit and I'll echo it: **this is not legal advice — check your jurisdiction.** Receiving is legal in most places; **transmitting should be assumed *not* legal** unless it's an **ISM band within power limits**, or you hold an **amateur licence** for that spectrum and stay within its terms. Transmitting to cause interference (jamming, spoofing) is illegal essentially everywhere. Only act on devices/systems you own or are explicitly authorized to test. Mayhem includes a **TX Limit** setting (Settings) to cap the allowed transmit frequency as a guardrail — set it. The firmware ships apps (Jammer, GPS-Sim, BLESpam, TouchTunes, various spoofers) that are trivially illegal to use against systems you don't own; the responsibility is entirely yours.
