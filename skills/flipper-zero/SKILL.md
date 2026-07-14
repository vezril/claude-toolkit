---
name: flipper-zero
description: "Operating the Flipper Zero — the portable multi-tool for pentesters and hardware hobbyists (STM32WB55 dual-core; a digital-dolphin pet on top of Sub-GHz radio, 13.56 MHz NFC, 125 kHz RFID, infrared, iButton/1-Wire, GPIO, BadUSB, and U2F). A query-answering reference distilled from the official docs (docs.flipper.net/zero, fetched 2026-07) via multi-agent research. Covers the hardware/tech-specs (CC1101 Sub-GHz at 20 dBm, ST25R3916 NFC, 13 GPIO pins at 3.3V, 128x64 LCD, 2100 mAh, BLE 5.4, USB-C), the physical controls and button combos (power/reboot/DFU), the Dolphin XP/leveling system, firmware update channels (Release/RC/Dev) via qFlipper and the mobile app, the microSD layout, and the serial CLI (230400 baud; storage/subghz/nfc/rfid/ir/ikey/gpio/loader/log commands). Details each subsystem: Sub-GHz (Read vs Read RAW, the frequency-by-region transmit limits, modulations AM650/AM270/FM238/FM476, the static-vs-dynamic/rolling-code boundary the firmware enforces, supported vendors, add-manually virtual remotes); NFC (card types, reading UID/SAK/ATQA, MIFARE Classic key recovery via mfkey32, magic cards for UID cloning, unlock-with-password, and the crypto limits — cannot clone bank/DESFire cards); 125 kHz RFID (the LF-vs-HF distinction from NFC, EM4100/HID/Indala protocols, T5577 rewritable blanks, animal microchips); Infrared (learn/universal remotes, NEC/RC5/RC6/Sony, the mobile remotes library); iButton (Dallas/Cyfral/Metakom 1-Wire, writable blanks); BadUSB (DuckyScript HID injection over USB/BLE); U2F (FIDO 2FA token); GPIO pinout & modules; the Video Game Module (RP2040); and the apps ecosystem (.fap files, Flipper Lab, the API-version-mismatch gotcha, the Controllers/HID app). Use to answer specific Flipper Zero questions — a menu option's meaning, capturing/replaying a signal, reading or cloning a card, running a universal remote, a CLI command, flashing firmware, why a saved remote won't transmit, an app that won't load — or to plan an authorized RF/access-control assessment. Dual-use security hardware: read/receive broadly to learn; the official firmware enforces region TX limits and blocks rolling-code replay by design — only act on devices/systems you own or are explicitly authorized to test. Siblings: hackrf-one, portapack-mayhem, wifi-pineapple."
argument-hint: "[your Flipper Zero question]"
license: MIT
---

# Flipper Zero

The **Flipper Zero** is a pocket **multi-tool for pentesters and hardware hobbyists** — an STM32WB55 dual-core board wrapped in a Tamagotchi-style dolphin pet, exposing a suite of RF and wired-protocol tools as main-menu apps: **Sub-GHz radio, 13.56 MHz NFC, 125 kHz RFID, Infrared, iButton (1-Wire), GPIO, BadUSB, and U2F**. This skill answers questions about operating it, distilled from the official docs.

> ## Two rules first
>
> **1. Reading is broad; transmitting/injecting is bounded — by law and by the firmware itself.** Reading and receiving across these subsystems to learn is generally fine. But the official firmware **enforces region-specific Sub-GHz transmit limits** and **blocks saving/replaying rolling-code (dynamic) remotes** *on purpose* — those are regulatory/legal boundaries (FCC/ISED/CE), not bugs. Cloning an access card or replaying a gate remote you don't own, or using **BadUSB** against a machine you don't control, can be illegal. **I'll explain how each feature works and flag the legal line — I won't help clone credentials, replay signals, or inject payloads against systems you don't own or aren't authorized to test.**
>
> **2. This skill documents the OFFICIAL firmware.** Third-party firmwares (Unleashed/RogueMaster/Momentum) exist that remove the TX limits and rolling-code blocks; I note the landscape and the legal caveat but don't document bypassing regulatory limits.

Load a reference for depth:

- **[references/hardware-basics-cli.md](references/hardware-basics-cli.md)** — full tech specs, the physical controls & **button combos** (power/reboot/DFU), the **Dolphin** XP system, power/battery, the microSD, firmware **channels** (Release/RC/Dev) via qFlipper vs the mobile app, and the **serial CLI** command list.
- **[references/sub-ghz-nfc-rfid.md](references/sub-ghz-nfc-rfid.md)** — the three core wireless subsystems: **Sub-GHz** (Read vs RAW, the region TX-frequency table, modulations, the static-vs-rolling-code boundary, vendors), **NFC** (card types, **mfkey32**, **magic cards**, crypto limits), and **125 kHz RFID** (the LF-vs-HF distinction, T5577 writing, animal chips).
- **[references/infrared-ibutton-badusb-gpio-apps.md](references/infrared-ibutton-badusb-gpio-apps.md)** — **Infrared** (learn/universal remotes), **iButton** (1-Wire keys), **BadUSB** (DuckyScript), **U2F**, **GPIO** & modules, the **Video Game Module**, and the **apps ecosystem** (`.fap`, Flipper Lab, the API-mismatch gotcha, Controllers app).

## The mental model

- **It's a front-end for many protocols, not one radio.** Each app is a different transceiver: Sub-GHz (CC1101, 300–928 MHz), NFC (13.56 MHz), RFID (125 kHz), IR (940/950 nm), iButton (1-Wire contact). Match the tool to the target's technology.
- **125 kHz RFID ≠ 13.56 MHz NFC.** Separate antennas, separate apps, separate security models — LF RFID is usually weakly secured (easy to clone), HF NFC often isn't. Conflating them is the most common beginner error.
- **Read is broad; save/replay is gated.** For Sub-GHz, a **static** (fixed-code) remote can be captured and replayed; a **dynamic (rolling-code)** remote can be *decoded but not saved* — the firmware disables it. For NFC, you can read UID/data and emulate simple cards, but **cannot clone bank/DESFire/secured cards** (real crypto).
- **The SD card holds everything** (keys, cards, remotes, `.fap` apps, payloads) and **is required**. Apps are `.fap` files tied to a firmware **API version** — mismatches are the #1 "app won't load" cause.
- **The Dolphin is cosmetic.** XP/levels/mood are a usage game (3 levels, capped daily XP); they don't unlock functionality.

## Fast answers

| Question | Answer |
|---|---|
| Power on / hard-reboot? | Hold **Back** 3 s to power on; hold **Back** 30 s to hard-reboot; **Left+Back** 5 s = normal reboot. |
| Capture & replay a remote? | Sub-GHz → **Read** (static) → Save → Saved → **SEND**. Rolling-code remotes decode but **can't be saved**. |
| "Signal can't be saved / transmission restricted"? | It's a **dynamic/rolling-code** protocol, or a frequency **outside your region's TX range** — both are firmware-enforced. |
| Clone an access fob? | 125 kHz LF → Read → write to a **T5577** blank. NFC (13.56) → read; MIFARE Classic keys via **mfkey32**; UID clone needs a **magic card**. |
| Read a bank card / transit card? | Reads UID and some data; **cannot clone/emulate** a working bank card (EMV/DESFire crypto). |
| Universal TV-off remote? | Infrared → **Universal Remotes** → TV. |
| App won't load? | **API-version mismatch** — update firmware or the app so their API versions match. |
| Use it as a 2FA key? | **U2F** app over USB — a legit defensive use. |

## Gotchas

- **The rolling-code wall is by design.** If Flipper decodes a remote but greys out Save, it's a dynamic protocol — not a bug, and not something the official firmware will clone.
- **Region TX limits are real.** "Transmission on this frequency is restricted in your region" means exactly that; the allowed ranges are per-region (see the table in the RF reference).
- **LF vs HF card confusion.** If a card doesn't read under NFC, it may be a 125 kHz card — try the **125 kHz RFID** app instead (and vice-versa).
- **Screen streaming is qFlipper, not the mobile app.** The mobile app does Archive / IR library / mfkey32; qFlipper does firmware/files/screenshots/repair.
- **GPIO is 3.3 V logic.** 5 V-tolerant on input, but drive logic at 3.3 V; the +5 V rail is off by default. Verify exact pin numbers against the on-device pinout diagram.
- **`.fap` apps are firmware-version-locked.** Install from the official catalog (auto-rebuilt) to avoid API mismatches; side-loaded `.fap`s from the wrong firmware won't run.
- **Animal chips read at reduced range** — they're 134.2 kHz, the antenna is tuned for 125 kHz; read-only, no emulation.

## Related

- [[hackrf-one]] — a far more capable *raw SDR* (1 MHz–6 GHz, arbitrary IQ) where Flipper's Sub-GHz is fixed-function; reach for HackRF when you need real signal capture/analysis beyond known remote protocols.
- [[portapack-mayhem]] — the HackRF's standalone-firmware analog; often cross-shopped with the Flipper as "the other handheld RF tool."
- [[wifi-pineapple]] — the toolkit's Wi-Fi-specific auditing appliance; the Flipper's Wi-Fi needs the ESP32 dev-board module, which is out of scope here.
- [[network-security]] · [[secure-coding]] — the defensive context for RF/access-control/HID work and handling captured credentials responsibly.
- [[information-theory]] — modulation, bandwidth, and coding fundamentals under the Sub-GHz/RFID/NFC layers.

Sources: docs.flipper.net/zero — `/development/hardware/tech-specs`, `/basics/*`, `/qflipper`, `/mobile-app`, `/development/cli`, `/sub-ghz/*`, `/nfc/*`, `/rfid/*`, `/infrared/*`, `/ibutton/*`, `/bad-usb`, `/u2f`, `/gpio-and-modules`, `/apps/*`, `/development`, `/video-game-module/*` — fetched 2026-07 via parallel research agents. A few facts (NFC crypto limits, EM4305 pet-chip silicon, the `.fap`/uFBT naming, custom-firmware names) are established community knowledge flagged as such in the references, not quotable from these doc pages. Firmware behavior and regional TX rules evolve and vary by jurisdiction — verify against the live docs and your local law.
