# PortaPack Mayhem — the UI and the controls common to every app

Source: Mayhem wiki *Main-Controls*, *User-interface*, *main-menu*, *title-bar*, *Settings*, *Text-Entry*, *SD-Over-USB* — fetched 2026-07.

## Physical controls

- **Encoder dial (knob)** — rotate to change the focused value by the step size; press = Select. On H2/H2+/H4M the knob also powers on/off (see hardware ref).
- **D-pad / buttons** — Up/Down/Left/Right move focus (and adjust digits in digit mode); a **Select** button; on some models a dedicated back/power.
- **Touchscreen** — resistive; tap fields, use on-screen keypads. If touch is off/erratic, calibrate (Settings → Calibration / Touchscreen Threshold).

## Screen anatomy

- **Title bar** (top): clock, SD-card indicator, battery, and a **sleep/backlight** control; also the per-app status icons.
- **Main menu**: the category grid — **Receivers, Transmitters, Transceivers, Recon, Capture, Replay, Remote, Looking Glass, Utilities, Games, Settings, HackRF**. Icon **color = maturity**: green = solid, yellow = missing features, orange = beta/unreliable, **red = destructive** (e.g. Wipe SD).

## Frequency entry (the control you use most)

With the frequency field focused, three ways to set it:
- **Encoder** — moves by the current **step size**.
- **Short-press Select** — opens the keypad for direct entry.
- **Long-press Select** — toggles **digit mode**: Left/Right pick a digit, Up/Down (or encoder) change it; long-press again to exit. Digit positions: 1 GHz · 100 MHz · 10 MHz · 1 MHz · **.** · 100 kHz · 10 kHz · 1 kHz · 100 Hz.

**Step sizes** (secondary option when frequency is focused): `10Hz · 50Hz · 0.1kHz · 1kHz · 5kHz(SA AM) · 6.25kHz(NFM) · 8.33kHz(AIR) · 9kHz(EU AM) · 10kHz(US AM) · 12.5kHz(NFM) · 15kHz(HFM) · 25kHz · 30kHz(OIRT) · 50kHz(FM1) · 100kHz(FM2) · 250kHz · 500kHz(WFM) · 1MHz`.

## Bandwidth / IF filter (per modulation)

The IF filter selects the FIR applied to the signal; options depend on the mode:
- **AM:** `DSB 9k`, `DSB 6k` (double-sideband), `USB+3k`, `LSB-3k` (single-sideband), `CW` (200 Hz filter @ 700 Hz).
- **NFM:** `8k5`, `11k`, `12k5` (standard 12.5 kHz channels), `16k` (25 kHz spacing).
- **WFM:** `80k`, `180k`, `200k` (full stereo broadcast).

## Gain staging (the core RX skill on an 8-bit ADC)

Three RX stages, shown across every receiver app:

| UI label | Stage | Range | Step |
|---|---|---|---|
| **AMP** | RF amplifier at the antenna port | 0 or **+14 dB** | on/off (shown `0`/`1`) |
| **LNA** | IF / low-noise amp | 0–40 dB | 8 dB |
| **VGA** | baseband variable-gain amp | 0–62 dB | 2 dB |

**Start at AMP off, LNA 16, VGA 16**; raise LNA and VGA roughly together until the signal is clear. Enable **AMP only for very weak signals** — it hurts SNR if the noise floor is already high or a strong signal is present. **Too much gain → ADC saturation**, seen as broadband noise / spurs across the waterfall; the **Satu%** readout (DFU overlay) shows saturation live to help dial it in. **TX gain:** AMP (0/+14 dB) + **Gain** (TX VGA, 0–47 dB, 1 dB steps).

## Settings worth knowing

Settings is itself an app; highlights:
- **TX Limit** — caps the maximum transmit frequency. A legal/safety guardrail — set it.
- **Radio** → **Reference Source** — internal / external / portapack clock; set to External/portapack when using an external 10 MHz reference or GPS (also the fix when GPS-Sim/BLE "don't work").
- **Freq. Correct** — crystal ppm correction for frequency accuracy.
- **Converter** — offset for up/down-converters (e.g. HF converters), so displayed freq matches actual.
- **Calibration / Touchscreen Threshold** — fix dead/erratic touch (there's an auto-threshold routine).
- **Config Mode**, **Splash**, **Theme/Menu Color**, **Display** (backlight timeout), **Encoder Dial** (sensitivity/rate), **Battery**, **App Manager** (hide apps), **Stealth Mode** (blank screen on TX).

## Text & file entry, and SD-over-USB

- **Text Entry** — on-screen keyboard for filenames, SSIDs, messages; encoder or touch.
- **SD over USB** (Utilities) — exposes the SD card to a host PC as mass storage without removing it. If the PC doesn't see it, check the troubleshooting notes (cables/drivers). Note some clones/cards misbehave here.
- Many apps read/write a per-app `.ini` under `SETTINGS/` — you can pre-edit defaults there (e.g. `rx_capture.ini`).
