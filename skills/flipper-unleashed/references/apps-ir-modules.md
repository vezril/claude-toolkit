# Unleashed — apps, infrared, expansion modules, NFC/RFID notes

Source: DarkFlippers/unleashed-firmware `dev` docs (`AppsOnSDCard.md`, `AppManifests.md`, `UniversalRemotes.md`, `InfraredCaptures.md`, `ExpansionModules.md`, `NRF24.md`, devboard/, `MultiConverter.md`, `BarcodeGenerator.md`, `SentrySafe.md`) + `FAQ.md` — fetched 2026-07. `[GK]` = general knowledge, not in these docs.

## The extra apps Unleashed bundles

Beyond OFW, Unleashed (especially the **`e` build**) ships/enables extras — from the README + FAQ: **Sub-GHz Bruteforce** plugin, **Sub-GHz Remote** plugin, enhanced **Frequency Analyzer**, expanded **universal IR remotes**, **LFRFID** and **iButton Fuzzer** plugins, **EMV** protocol support + multiple **NFC card parsers**, and **BadKB** (BadUSB over Bluetooth). The full app set is maintained separately at `github.com/xMasterX/all-the-plugins`.

## App files & the loader

A **FAP** ("Flipper Application Package") is an ELF executable + metadata/resources, built with `fbt`; external app source lives in `applications_user/` with an `application.fam` manifest whose `apptype = FlipperAppType.EXTERNAL`. Build with `./fbt fap_<APPID>` (one), `./fbt launch APPSRC=<path>` (build+deploy over USB), or `./fbt faps` (all).

The MCU can't run code straight from SD, so the **App Loader** copies the FAP SD→RAM, verifies compatibility, resolves imported symbols against a **symbol table**, applies relocations, and starts it — so a FAP has less heap than a built-in app, and needs a **matching major API version** to load. On-SD, built FAPs sit under `/ext/apps/<category>/` with data in `/ext/apps_data/`, category from the manifest's `fap_category` `[GK for the exact tree]`.

## `application.fam` manifest

`App()` calls with build-time properties. **Required:** `appid`, `apptype` (a `FlipperAppType`: SERVICE / SYSTEM / APP / PLUGIN / DEBUG / ARCHIVE / SETTINGS / STARTUP / EXTERNAL / METAPACKAGE). Common optional: `name`, `entry_point` (C fn; C++ needs `extern "C"`), `requires`/`conflicts`/`provides`, `stack_size` (bytes — too little crashes, too much steals heap), `icon`, `order`, `targets` (default `["all"]`), `cdefines`, `sdk_headers`, `resources`. **External-app (FAP) specific:** `sources` (default `["*.c*"]`, `!`-prefix excludes), `fap_version`, `fap_icon` (1-bit 10×10 PNG), `fap_category` (→ SD path), `fap_description`, `fap_author`, `fap_weburl`, `fap_icon_assets`, `fap_libs`/`fap_private_libs`, `fap_extbuild`, `fal_embedded` (PLUGIN only). Example:

```python
App(
    appid="bt_settings",
    name="Bluetooth",
    apptype=FlipperAppType.SETTINGS,
    entry_point="bt_settings_app",
    stack_size=1 * 1024,
    requires=["bt", "gui"],
    order=10,
)
```

## Infrared: universal remotes & captures

**Universal remote assets** live in `applications/main/infrared/resources/infrared/assets/` — `tv.ir`, `audio.ir`, `ac.ir`, `projector.ir`. The **button names must match exactly** for the universal remote to find them:
- **TV:** `Power, Mute, Vol_up, Vol_dn, Ch_next, Ch_prev`
- **Audio:** `Power, Play, Pause, Vol_up, Vol_dn, Next, Prev, Mute`
- **Projector:** `Power, Mute, Vol_up, Vol_dn`
- **AC:** `Off, Dh, Cool_hi, Cool_lo, Heat_hi, Heat_lo` (record `*_lo` at 23 °C, `*_hi` at the extremes; ACs track state, so capture full mode sets and an explicit `Off`).

Contribute by appending to the end of the `.ir` file, prefixed with `# Model: <name>`, via PR. **Capturing:** use **quick button presses (don't hold)**; a clean capture is ~100 samples. `.ir` files store signals as **`parsed`** (recognized: `protocol`/`address`/`command`, e.g. NEC) or **`raw`** (frequency + timing samples for unrecognized signals).

## Expansion modules & external radios

**Expansion Module Protocol** — a byte-oriented UART protocol over GPIO. Pins: **USART** Tx/Rx = 13/14, **LPUART** Tx/Rx = 15/16. Initial connection is always **9600 baud** then negotiated. Frames: Heartbeat `0x01` (250 ms idle timeout), Status `0x02`, Baud `0x03`, Control `0x04` (start/stop RPC, enable/disable OTG), Data `0x05` (≤64 bytes). Enable in **Settings → Expansion Modules** (pick the Listen UART).

**nRF24L01+** (2.4 GHz) over GPIO SPI — wiring (Flipper → nRF24): MOSI 2→6, MISO 3→7, CSN 4→4, SCK 5→5, CE 6→3, GND 8→1, 3V3 9→2. Apps: **NRF24 Sniffer/Scanner** (find addresses), **Mouse Jacker** (acts via BadUSB files), NRF24 Driver. Add a 3.3–10 µF cap across VCC/GND if flaky. Docs' verbatim line: *"for educational purposes only… only use these apps on your own equipment."*

**Wi-Fi Developer Board** — plugs into the expansion slot for **debugging** (DAP Link / Black Magic modes) and reading logs, over USB-C or Wi-Fi. Flash it with uFBT (`pipx install ufbt`, board in bootloader mode, `python3 -m ufbt devboard_flash`). Power off the Flipper before connecting (shared power can corrupt the SD). *(The board is the official ESP32-S2 devboard `[GK]`; these docs cover debugging, **not** Marauder/Wi-Fi-attack firmware, which is separate third-party firmware.)*

## NFC / RFID notes (from the FAQ)

- **Bank cards:** cannot clone/emulate or act as a POS. **MIFARE DESFire / Ultralight C:** "no available attacks for this card currently." **Amiibo:** only **NTAG215** supported.
- **MIFARE Ultralight** password: scan → hold to reader to grab the password → scan again.
- **HID iCLASS / Picopass:** use the Picopass plugin; a 26-bit Picopass can downgrade to H10301 LF RFID; emulation + personalization-mode write supported; the **Seader** app + a **SAM** expansion board reads more secure HID cards.
- **LF RFID cloning** targets **T5577** rewritable chips (standard chips are read-only); T5577 can emulate other tags.

## Misc apps (each by its community author)

- **MultiConverter** (theisolinearchip) — on-device converter: number systems (dec/hex/bin), temperature (C/F/K), distance, angle. `#` toggles unit-select; long-press `0`/`1` = negative/decimal.
- **BarcodeGenerator** (McAzzaMan) — **UPC-A only** so far; OK enters edit, Left/Right pick a digit, Up/Down change it.
- **SentrySafe** (H4ckd4ddy) — a plugin that opens certain SentrySafe/Master Lock electronic safes via a documented hardware vulnerability (wiring: Flipper GPIO 8/GND → safe black wire, GPIO 15/C1 → safe green wire). **Only for a safe you own or are explicitly authorized to open** — the doc itself carries no legal disclaimer, so treat this as own-property-only.
