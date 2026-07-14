# PortaPack Mayhem — the app catalog

Source: Mayhem wiki app pages (*Applications*, *Receivers*, *Transmitters*, *Recon*, *Capture*, *Replay*, *Looking-Glass*, *Utilities*, *Games*, and the per-app pages) — fetched 2026-07. ~90 apps ship across the categories; the whole wiki has a page per app if you need one specific tool. Below: the map, then the flagship apps in depth.

## The categories (main menu)

**Receivers · Transmitters · Transceivers · Recon · Capture · Replay · Remote · Looking Glass · Utilities · Games · Settings · HackRF.** Icon color = maturity (green solid → yellow → orange beta → red destructive).

## Receivers (decode/listen)

`Audio` (AM/NFM/WFM radio) · `Radio` · `ADS-B` (aircraft) · `AIS Boats` · `APRS RX` · `POCSAG` (pagers) · `TPMS RX` (tyre sensors) · `ERT` (utility meters) · `Tetra RX` · `Flex RX` · `AFSK` · `RTTY RX` · `Morse RX` · `SSTV RX` · `WeatherFax` · `Radiosonde` (weather balloons) · `NOAA`/`Meteor` (weather sats) · `Weather` (sensors) · `ACARS` (aircraft msgs) · `BLE RX` (Bluetooth LE) · `NRF` (nRF24) · `ProtoView`/`SubGhzD`/`SubCar` (sub-GHz protocol viewers) · `EPIRB RX` · `VOR RX` (nav) · `Analog TV` · `Detector` · `Fox-Hunt` · `FPV-Detect` · `Scanner` · `Search` · `Level`/`Time Sink`/`gfxEQ` (signal tools). Most receivers log to their SD folder and share the common frequency/gain UI (see [ui-and-controls.md](ui-and-controls.md)).

## Transmitters (⚠ legality applies to all of these)

`Soundboard` · `Microphone`/`Mic TX` · `Morse TX` · `RDS` (FM radio-data) · `SSTV` · `POCSAG TX` · `RTTY TX` · `APRS TX` · `ADS-B TX` · `AIS` · `P25 TX` · `MDC-1200` · `TEDI/LCR` · `Signal gen` · `Spectrum Painter` (draw an image into the waterfall) · `GPS Sim` · `Jammer` · the **sub-GHz / OOK replay family**: `OOK`, `OOK Editor`, `OOK Brute`, `Key fob TX`, `KeeLoq TX`, `Security+ TX`, `FlipperTX`, `TouchTunes`, `BHT`, `Hopper`, `TPMS TX`, `Flex TX`, `2-Tone`, `SAME TX` (EAS), `EPIRB TX` · **BLE spoof/spam**: `BLE TX`, `BLESpam`, `Burger Pager`, `CVS Spam`, `Adult Toys`, `LGE Tool`. Several of these exist to demonstrate protocol weaknesses; using them against systems you don't own is illegal — see the legality note in the hardware reference.

## Transceivers

`Microphone Transceiver` (push-to-talk voice) · `KISS TNC` (AX.25 packet TNC over USB).

## The flagship trio: Capture → Replay, and Recon

These are what most people buy the device for.

### Capture (record IQ)

Records raw IQ to the SD card as **`.C16`** (complex 16-bit signed, little-endian — default) or **`.C8`** (complex 8-bit, smaller/faster), with a matching **`.TXT`** holding center frequency + bandwidth. Controls: frequency, step, **gain (AMP/LNA/VGA)**, **Rate** (sample rate = capture bandwidth, 12.5k–5500k), **Format** (C16/C8), **Trim** (auto-trim to the signal — irreversible; prefer the IQ Trim utility if unsure).

> **The bandwidth rule that makes replay work:** for *reliable replay*, capture at **≤ 500 kHz** (green "REC" icon) — that's the write speed common SD cards sustain (>2 MB/s at C16). 600 kHz–1.25 MHz needs a fast card (>3–5 MB/s) and may drop M4 samples. **Above 1.25 MHz (yellow icon) the file has periodic sample drops** — fine for spectrum inspection in inspectrum/Audacity, **not** for replay (playback runs short/"sped up"). Watch **% Dropped Samples** while recording; drop C16→C8 to halve the required write speed. If you have a GPS module attached, captures get `_GEO` appended and embed location metadata — strip it before sharing.

### Replay (transmit an IQ file — ⚠ TX legality)

Transmits `.C16`/`.C8`/`.CU8` files over the air, singly or as a **`.PPL` playlist** (plain-text, comma-delimited: `ABSOLUTE_PATH,DELAY_MS`, `#` comments). Controls: per-track frequency (editable, not saved), **TX gain 0–47**, **TX amp 0/14**, **Loop** (default on). New captures added to an empty list auto-create `PLAY_XXXX.PPL` in `PLAYLIST/`; save with the 💾 button. Fallback if a capture lacks `.TXT` metadata: assumes the current TX frequency and **500 kHz** sample rate.

> ⚠️ The inter-track delay is a **blocking sleep on the UI thread** — a long delay makes the device look frozen with no way out but reset. And this is transmitting: only on bands/power you're licensed for.

The canonical workflow: **Capture** a non-rolling-code signal (≤500 kHz) → **Replay** it. Rolling-code systems (modern car keys, most garage doors post-~2010) won't work by replay — that's by design.

### Recon (automated scanning)

A rework of the older **Scanner** app: sweeps a set of frequencies (from a `FREQMAN` file or a range) and **pauses on any frequency whose signal beats the SQUELCH threshold**. Modes: **RECON** (walk a frequency list), **SCAN**, **MANUAL-S**. In AM/NFM/WFM, stats update every 100 ms → up to ~10 freq/s; in **SPEC** mode, ~10/s (12.5k–1500k) down to ~3/s (3–5 MHz). Color-coded lock/wait states, configurable wait modes and lock counts, continuous vs sparse matching, and (nightly) repeater handling. It's the tool for "what's transmitting around me."

## Looking Glass (wideband spectrum)

A wide-band scrolling **waterfall** — the HackRF steps through a large range in slices; each full sweep adds a row (wide ranges → slow, may look frozen; keep the span small). Presets load from `.TXT` files in `LOOKINGGLASS/` (ranges ≥240 MHz wide, from 10 MHz). Controls: **MIN/MAX** (+ range lock), **PRESET**, **LNA/VGA/AMP**, **FILTER** (OFF/MID/HIGH smoothing), **F-/S-** (fast-inaccurate vs slow-accurate scan), display modes **SPECTR** (waterfall) / **LIVE-V** / **PEAK-V** (power bars), **RES** (FFT resolution 2–128, default 32), a **MARKER** you can jump-to-Audio from, and a **BEEP** squelch (−100…+20 dB). Great for spotting local RF activity across a broad span.

## Utilities

`File manager` · `Freq manager` (edit the FREQMAN frequency DB) · `Flash Utility` (on-device firmware flashing) · `SD over USB` (mount SD to a PC) · `IQ Trim` (trim captures non-destructively) · `Antenna length` (the calculator — see below) · `Waterfall Designer` · `Wav Viewer` · `Playlist Editor` · `Notepad` · `Calculator` · `Stopwatch`/`Metronome` · `Tuner` · `Rand Pwd` · `WardriveMap` · `Wipe SD card` (🔴 destructive) · `Debug` menu (Audio/Buttons/Touch tests, Memory/SD/Temperature, Reboot). `Cart Lock` and similar are novelty/utility tools.

### Antenna length calculator

Computes the matched antenna length for a frequency in metric + imperial, and — reading `WHIPCALC/ANTENNAS.TXT` — tells you **how many telescopic elements to extend** for each saved antenna (falls back to built-in ANT500 if the file is absent). Wave options: Full, 1/2 (dipole), **1/4 (default whip)**, 3/8, 5/8 (VHF/UHF gain), etc. File format: `label,elem1_mm,elem2_mm,...` (each value = fully-extended length of that section). **A matched antenna is critical** — a grossly mismatched one during high-power TX can damage the equipment.

## Games

`Doom` · `2048` · `Snake` · `Tetris` · `Breakout` · `Space Invaders` · `Pac-Man` · `Blackjack` · `Battleship` · `Dino` · `Digital Rain` · `Morse P`. (Yes, it runs Doom.)

## Remote

A configurable button-grid that fires saved TX actions — a custom remote control built from your captured/defined signals.
