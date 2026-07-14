# Flipper Zero — Infrared, iButton, BadUSB, U2F, GPIO, apps

Source: docs.flipper.net/zero `/infrared/*`, `/ibutton/*`, `/bad-usb`, `/u2f`, `/gpio-and-modules`, `/apps/*`, `/development`, `/video-game-module/*` — fetched 2026-07.

## Infrared

**Three TX LEDs + one RX sensor** behind an IR-transparent window (the three-LED array gives wide, strong coverage). RX decodes at a **38 kHz** carrier. For TVs, ACs, audio, projectors, and other IR appliances. GPIO can drive an external IR LED for more range.

- **Learn a remote:** Infrared → Learn New Remote → aim the source remote at the RX and press a button. **Known protocols** (NEC, RC5, RC6, Samsung, Sony SIRC) auto-decode and show the name; **unknown** signals are stored **RAW** (verbatim pulse/space timing). Save → name the button; the first button creates a virtual remote, add more with ➕. Manage via Saved Remotes.
- **Universal remotes** (brute-force libraries): built-in **TV** (`tv.ir`), **Audio** (`audio.ir`), **Projector** (`projector.ir`), **Air conditioner** (`ac.ir`). Flipper plays an entire dictionary of protocols/commands until the device reacts (or the dictionary ends). Infrared → Universal Remotes → category → button.
- **Mobile Remotes Library:** the app pulls the right IR signals from a community GitHub database (Tools → Remotes Library → device type → brand → test → Save). Faster than universal brute-force once you've identified the exact remote.

## iButton (1-Wire contact keys)

**1-Wire** over the three pogo pins on the front pad (left data + middle GND for read/write; right data for emulation; data also on GPIO pin 17). Key families: **Dallas, Cyfral, Metakom**.

- **Read:** iButton → Read → touch key to the data+GND pins. Captures the **UID**; a few Dallas types (DS1992/DS1996/DS1971) also expose **memory**, everything else is UID-only. Save via More → Save. Read fails on poor contact, unsupported protocol, or a **CRC error** (corrupt Dallas UID).
- **Write / emulate:** write UID to blank keys — **RW1990, TM1990, TM08V2** (all DS1990-compatible), **RW2004** (DS1990/DS1992). **Memory** writing only works **between matching Dallas types** (DS1992→DS1992, etc.). Emulate from a saved key (Flipper acts as slave to a reader). Saved → key → "Write ID" or "Full write on same type."
- **Add Manually:** pick protocol (Dallas DS1990/1992/1996/1971, Cyfral, Metakom), enter the UID in hex.

## BadUSB (HID injection)

Flipper impersonates a **USB/BLE HID keyboard**, so a payload can type anything a person with physical access could — the docs' own framing: *"change system settings, open backdoors, retrieve data, initiate reverse shells."* Scripts use an **extended DuckyScript** compatible with **Rubber Ducky 1.0** (REM, DELAY, DEFAULT_DELAY, STRING, ENTER, GUI/WINDOWS, CTRL/ALT/SHIFT, arrows, F-keys) plus Flipper extras (alt+numpad input, `SYSRQ`). Payloads are plain `.txt` files in **`SD/badusb/`** (upload via qFlipper or the app).

- **Over USB:** close qFlipper → Bad USB → pick payload → confirm the **USB logo** → set keyboard layout (US default) → plug in → OK to run.
- **Over Bluetooth:** enable BT → Bad USB → payload → confirm the **BLE logo** → pair from the target → run.

This is the app that most directly does something *to another computer* — only run payloads against machines you own or are authorized to test.

## U2F / FIDO security key

Flipper acts as a **USB U2F/FIDO second-factor token** (like a YubiKey) over USB HID. Register: close qFlipper → connect USB → Main Menu → U2F ("connected") → add a security key in the web account (Google, GitHub, X, Facebook, …) → press **OK** on the Flipper to confirm. Authenticate: after your password, press **OK** on the Flipper. A genuinely defensive use of the device.

## GPIO & modules

**18-pin top header**, **3.3 V CMOS logic** (5 V-tolerant on input, but drive logic at 3.3 V), **≤20 mA per pin**; the +3.3 V and +5 V rails each supply ≤1.2 A, total external draw ≤5 W; pins have 51 Ω series resistors + ESD protection. The **+3.3 V rail is on by default; +5 V is off** — enable it in GPIO → "5V on GPIO" (it's also live whenever USB is connected).

Bus assignments (functional groups — reliable; **verify exact pin numbers against the on-device pinout diagram**, which the docs publish only as an image):
- **SPI** — MOSI/MISO/CS/SCK
- **UART (USART1)** — TX / RX
- **I2C** — SCL / SDA (PC0/PC1)
- **SWD debug** — SWCLK / SWDIO (for flashing/debugging the STM32)
- **1-Wire** — iButton data (PB14, pin 17)
- Power/ground: **+5V**, **+3V3**, multiple **GND**

Modules attach here: the Wi-Fi Dev Board (SWD debugging + Wi-Fi attacks via ESP32), prototype boards, and the Video Game Module.

## Video Game Module (VGM)

Official add-on co-developed with Raspberry Pi, built on the **RP2040** MCU; snaps onto the GPIO header (remove any case; ships with a silicone bumper). Adds a **TDK ICM-42688-P 6-axis motion sensor** (gyro/accel — apps Air Arkanoid, Air Mouse) and a **DVI-D video-out** that mirrors the 128×64 screen to a TV. Its own **USB-C** flashes RP2040 firmware (UF2 mode via the boot buttons); it's Pico-compatible for standalone custom firmware with a 14-pin breakout + RGB LED. **Requires Flipper firmware ≥ 0.98.3** — update over Bluetooth first, or you get "video game module not initialized."

## Apps ecosystem

Apps extend the Flipper beyond the built-in tools; installed apps appear under **Main Menu → Apps**. They're a community catalog curated by Flipper Devices.

- **App files are `.fap`** (ELF-based, loaded at runtime from the SD card under `/ext/apps` — not compiled into the base firmware). Each carries a **manifest with its API version**.
- **Install** from **Flipper Lab** (lab.flipper.net, Chromium + Web Serial, over USB) or the **mobile app** (over Bluetooth) — find the app, Install, wait for upload. *(Desktop installs go through Flipper Lab; qFlipper is the firmware/file tool, not the app store.)* Categories span Sub-GHz, NFC, RFID, Infrared, GPIO, iButton, Bluetooth, USB, Games, Media, Tools.
- **The #1 app gotcha — API-version mismatch:** a `.fap` built for a different firmware API version won't load ("manifest invalid", "missing imports", "app is outdated"). Fix by **realigning the two sides** — update the firmware, update the app, or rebuild it against the current SDK. Installing from the official catalog usually avoids this because it auto-rebuilds against current firmware; side-loaded `.fap`s and custom firmware are where it bites. Other install failures: disconnection, insufficient SD space, outdated firmware.
- **Controllers / Remote app:** use the Flipper as an **HID controller** for a PC/phone over **BLE** (Apps → Bluetooth → Remote) or **USB** (Apps → USB → Remote) — Keynote clicker, Keyboard, Media/camera remote, Mouse, TikTok, Mouse Jiggler (anti-sleep).
- **Building apps:** **fBT** (in-tree firmware build tool) and **uFBT** (standalone single-app toolchain, `pip install ufbt`; `ufbt`, `ufbt launch`, `ufbt update`) build `.fap`s in **C** against the **Furi** OS + HAL APIs; an on-device **mJS JavaScript** engine runs lighter scripts without compiling. API reference at developer.flipper.net/flipperzero/doxygen. *(The `.fap`="Flipper Application Package" name and uFBT are widely-used community/tooling knowledge; the fetched dev page is mostly a link hub.)*

## Custom firmware landscape (neutral — this skill documents the OFFICIAL firmware)

Third-party firmwares exist — commonly **Unleashed**, **RogueMaster**, and **Xtreme/Momentum**. At a high level they **unlock region-restricted Sub-GHz TX frequencies** and **remove the transmit blocks on rolling-code / OEM-restricted protocols** that the official firmware refuses to replay. Those limits are a **deliberate regulatory/legal boundary**, not a missing feature: radio transmission is regulated (FCC/ISED/CE-ETSI), and transmitting outside permitted bands/power — or replaying access-control signals you're not authorized to use — **can be illegal**. Custom firmware is also a frequent source of app "API mismatch"/catalog errors (the official troubleshooting fix is literally "install official firmware") and may void support. **This skill deliberately does not document installing custom firmware or bypassing TX limits** — it's noted only so the boundary is clear.
