# Unleashed — install, update, build, config, key combos

Source: DarkFlippers/unleashed-firmware `dev` docs (`ReadMe.md`, `HowToInstall.md`, `OTA.md`, `HowToBuild.md`, `fbt.md`, `HardwareTargets.md`, `FAQ.md`, `KeyCombo.md`, `DangerousSettings.md`, `CustomFlipperName.md`) — fetched 2026-07. Facts not stated in these docs are flagged `[GK]` (general knowledge).

## What it is

Unleashed is a **fork of the official Flipper Zero firmware (OFW)** by the **DarkFlippers** team (lead @xMasterX), self-described as "the most stable custom build," staying API-compatible with OFW while adding features. **"This project is developed independently and is not affiliated with Flipper Devices,"** and its own guardrail is stated once: **"intended solely for experimental purposes and is not meant for any illegal activities."** Channels: releases `t.me/unleashed_fw`, dev `t.me/kotnehleb`, Discord `discord.unleashedflip.com`.

## The build variants

- **Base build** — firmware only.
- **`e` build ("extra")** — firmware **plus the extra apps pack pre-loaded** (the apps live at `github.com/xMasterX/all-the-plugins`). The `e` suffix on a release filename is the tell. *(Earlier I guessed `_c`; the docs use `e`.)*
- Release artifact name: `flipper-z-f7-update-<version>.tgz`.

## Installing (you must have a microSD inserted; first-timers flash OFW once first)

1. **Unleashed Web Installer** — `web.unleashedflip.com` in a **Chromium** browser → pick Release/Dev → Install. The primary path.
2. **Flipper Lab Web Updater** — from a GitHub release, "Install via Web Updater" → Connect → Install. *(The official mobile-app "update" channel isn't used; you go through a Web Updater or a Custom channel.)*
3. **iOS app** — download the `.tgz` → open in Files → share to the Flipper app → green **Update**. (Docs note: an iOS error may show but the update still succeeds.)
4. **Android app** — set Update channel to **Custom**, pick the `.tgz`, Update (or use "Install via Web Updater").
5. **qFlipper ≥ 1.2.0** — **Install from file** → select the `.tgz`.
6. **Manual/offline** — extract the `.tgz`, copy the folder to the SD `update/` dir, open the `update.fuf` in the on-device file browser, start.

## OTA / self-update mechanics

The updater boots a special image into **RAM** with full flash access, in three stages: **Backup** (`/int` internal storage → tarred to SD), **Update** (executes an Update manifest — a Flipper File Format key-value file with `Filetype/Version/Info/Target/Loader/Loader CRC` mandatory, `Radio*`/`Resources` optional; swaps the radio stack via Core2 **FUS**, validates Option Bytes, CRC32-checks then flashes the `.dfu`), **Restore** (`/int` restored, resources unpacked to SD). Failures report `[XX-YY]` error codes.

## Building from source

**fbt** (Flipper Build Tool, a SCons wrapper) is the entry point — only **git** is required; it auto-downloads toolchains. **uFBT** (`pip install ufbt`) builds/debugs a single app.

```bash
git clone --recursive https://github.com/DarkFlippers/unleashed-firmware.git
./fbt COMPACT=1 DEBUG=0 updater_package         # full package → dist/flipper-z-f7-update-*.tgz
./fbt COMPACT=1 DEBUG=0 launch_app APPSRC=applications_user/<app>   # build+run one app over USB
git submodule update --init --recursive          # if submodules are missing
```

Flags: `COMPACT=1`, `DEBUG=0`, `VERBOSE=1`. Targets: `fw_dist`, `fap_dist` (external plugins), `flash`/`flash_usb` (SWD/USB), `debug` (build+flash+GDB), `cli`. VS Code: `./fbt vscode_dist` (optionally `LANG_SERVER=clangd`). Hardware debug needs a probe (Wi-Fi Devboard / ST-Link / J-Link). **Hardware target** is **f7** (the production Flipper Zero, STM32WB55 `[GK]`); non-default via `TARGET_HW=<n>` (there's no `--target` flag).

## Key combos (reset / DFU)

| Combo | Action |
|---|---|
| Hold **Left + Back** a few seconds | Hardware reset (reboot a frozen Flipper) |
| Disconnect power, hold **Back** alone **30 s** | Hardware power reset |
| Press **Left** during boot | Software DFU (Flipper bootloader) |
| Press **OK** during boot | Hardware DFU (ST ROM bootloader) |
| **Left+Back** → release Back (blue LED/DFU) → release Left | Reset + Software DFU |
| Power-off, hold **Up + Back ~5 s** → hold **Right** | PIN/config reset (SD files preserved) |

Screenshots are taken over CLI/qFlipper, not a button combo.

## DangerousSettings — the hardware-limit unlock (separate from region unlock!)

Two different things, commonly conflated:
- **Region locks** are **off by default** in Unleashed (software — lets you *select* frequencies stock would region-restrict).
- **DangerousSettings** is a **separate** switch that extends the **CC1101 past its hardware spec**. Edit `subghz/assets/dangerous_settings` on the SD, change `false`→`true`. It widens the ranges to ~281–361 / ~378–481 / ~749–962 MHz. The docs warn verbatim: **"Transmitting on frequencies that outside of hardware specs can damage your hardware"** — neither Flipper Devices nor the developers take responsibility for damage. Most users never need it.

## Custom Flipper name

Settings → Desktop → Change Flipper Name → type → Save (auto-reboots on exit; blank = revert to default). Stored on the **microSD**, so it survives firmware updates. Shows in device info + passport. Practical limit ~8 chars `[GK]`.

## CLI & common troubleshooting (from the FAQ)

- **CLI access:** `lab.flipper.net/cli` (Chromium + USB, close qFlipper first); PuTTY on the COM port @ **115200**; `screen <tty> 115200` on macOS/Linux; iOS has no USB serial (set Log Level = Debug, use `log`).
- **Slow/laggy:** use a quality branded microSD; Settings → System → Log Level = None, Debug = OFF, Heap Trace = None; charge it.
- **Backlight dead after install:** you enabled the RGB-mod setting — disable at Settings → LCD & Notifications → RGB mod settings (only enable with the physical mod).
- **App won't run after update:** API-version mismatch — update the app pack (or firmware) so their API versions match; the `e` build keeps them aligned.
- **Bluetooth won't connect:** Forget on both sides (app, phone BT, and Flipper Settings → Bluetooth → Forget all devices), then re-pair.
- **Won't connect to a web tool:** close every other qFlipper / Flipper Lab tab first.
- **Community file repos:** `UberGuidoZ/Flipper`, `Flipper-IRDB`, and `djsime1/awesome-flipperzero` (aggregates asset/animation packs).
