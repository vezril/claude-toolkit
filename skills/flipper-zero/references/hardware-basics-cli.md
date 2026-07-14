# Flipper Zero — hardware, basics, firmware, CLI

Source: docs.flipper.net/zero (`/development/hardware/tech-specs`, `/basics/*`, `/qflipper`, `/mobile-app`, `/development/cli`) — fetched 2026-07.

## Tech specs

| Subsystem | Detail |
|---|---|
| **MCU** | STM32WB55RG — app core ARM Cortex-M4 @ **64 MHz**, radio core Cortex-M0+ @ **32 MHz**; **1024 KB** flash, **256 KB** SRAM (shared) |
| **Sub-GHz radio** | **CC1101** transceiver, TX up to **20 dBm**, bands 300–348 / 387–464 / 779–928 MHz (315/433/868/915 region-dependent) |
| **NFC** | **ST25R3916**, **13.56 MHz** — ISO-14443A/B, MIFARE Classic/Ultralight/DESFire, FeliCa, HID iCLASS, NFC Forum |
| **125 kHz RFID** | LF antenna, AM/OOK — EM4100, HID H10301, Indala, Kantech, ioProx, AWID, FDX-A/B, … |
| **Infrared** | RX 950 nm @ **38 kHz** carrier; TX 940 nm, 0–2 MHz carrier, **300 mW** (3 LEDs) |
| **iButton** | 1-Wire — Dallas DS199x/DS1971, Cyfral, Metakom (via GPIO pin 17) |
| **GPIO** | **13 usable I/O**, **3.3 V** CMOS logic (5 V-tolerant input), up to **20 mA/pin** |
| **Display** | 128×64 monochrome LCD, 1.4", ST7567 (SPI) |
| **Battery** | LiPo **2100 mAh**, up to ~28 days standby; USB-C **5 V/1 A**, ~2 h to full |
| **Connectivity** | USB **Type-C** 2.0 (12 Mbps); **Bluetooth LE 5.4** |
| **Storage** | microSD up to 256 GB (2–32 GB recommended), FAT12/16/32/exFAT (on-device format = FAT32) |

## Physical controls & button combos

- **D-pad** (Up/Down/Left/Right) navigates menus and on-screen keyboards; **Left/Right** switch between options on a screen. **OK** = launch/confirm. **Back** = quit/go back (hold to power actions).
- **Power on:** hold **Back** ~3 s.
- **Power off:** Settings → Power → Power off (confirm Right). (Hold-Back also powers off from on.)
- **Normal reboot:** hold **Left + Back** for **5 s**.
- **Hard reboot** (frozen device, resets power circuit): hold **Back** for **30 s**.
- **DFU / recovery mode:** hold **Left + Back** 5 s, release Back but keep **Left** held until the **blue LED** lights.
- **Left-handed mode:** Settings → System → hand orientation.

## Desktop, lock, Dolphin

- **Desktop** shows the dolphin + a status bar (battery, SD mount, BLE, lock, mute, module/USB). **OK** → main menu; **Up** → lock menu; **hold Down** → device info; **Left/Right** → customizable quick-apps.
- **Lock:** via Up menu — lock controls (**unlock = press Back three times**), PIN lock, dummy/"gaming" mode, mute.
- **Dolphin (the mascot/XP pet):** **3 levels** — 300 XP → L2, 1800 XP → L3. XP is capped at **20 XP per app per day, 140 XP/day total** (1–3 XP per action). Mood tracks how often you use it. The **Passport** screen shows name/level/mood.
- **Archive** app lists all saved items (keys, cards, remotes) by type.

## Power & SD card

- Runtime up to ~1 month; charges over USB-C at 5 V/1 A in ~2 h. Consumption ~30 mA idle (no backlight) → ~400 mA (backlight + transceiver) → up to 2 A with an external module.
- **microSD is required** for keys/cards/remotes/databases. Insert pins-up until it clicks. **Always unmount before removing** (Settings → Storage → Unmount) to avoid corruption. Format via Settings → Storage → Format (FAT32).

## Firmware update & channels

Two update tools: the **Flipper Mobile App** (Bluetooth; iOS/Android) and **qFlipper** (USB desktop; Win 10/11, macOS 10.14+, Linux AppImage). Three release channels:

- **Release** — stable, recommended.
- **Release Candidate (RC)** — in QA validation; becomes Release after testing.
- **Development (Dev)** — built per-commit, newest features, **may freeze or corrupt data**.

Mobile: enable BT both sides → connect/pair (enter the code shown on-device) → pick channel → Update (~10 min). qFlipper: connect USB → Advanced controls → pick version → Update.

**qFlipper** also does file management (drag-drop to the SD), **screenshots/screen capture** (this is a qFlipper feature, *not* the mobile app), backup/restore, and **repair of corrupted firmware** (recovery mode). The **mobile app** adds the **Archive**, the **IR Remotes Library**, and **Tools → mfkey32**.

## Serial CLI

Access over USB serial at **230400 baud**, three ways:
- **Flipper Lab** web CLI — lab.flipper.net (Chromium + Web Serial).
- **Web Serial Terminal** — googlechromelabs.github.io/serial-terminal.
- **Native** — macOS/Linux `screen /dev/cu.usbmodemflip_<name>` or `minicom`; Windows PuTTY on the COM port @ 230400.

Useful commands:

| Command | Purpose |
|---|---|
| `help` / `?` | List commands |
| `device_info` / `!` | Device + firmware info |
| `power off\|reboot` | Power control (and GPIO voltage) |
| `storage` | Filesystem — `info/list/tree/read/write/copy/rename/remove/mkdir/md5/stat/extract` (`/ext`=SD, `/int`=internal) |
| `loader` | List/open/close apps |
| `log <level>` | Live system log (error/warn/info/debug/trace) |
| `nfc` · `subghz` · `ir` · `rfid` · `ikey` | Per-subsystem read/emulate/TX sub-shells (`subghz chat <freq_hz> <0/1>` for the local text chat) |
| `gpio` | `gpio mode/set/read <pin> <0/1>` |
| `i2c` / `onewire` | Bus scans |
| `led r/g/b/bl <0-255>` · `vibro <1/0>` · `buzzer freq <hz> <dur>` | Peripherals |
| `js <file>` | Run a JavaScript (mJS) script |
| `crypto` | Encrypt/decrypt with the secure-enclave keys |
| `update` / `factory_reset` | Firmware update-backup-restore / factory reset |
