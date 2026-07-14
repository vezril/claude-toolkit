# HackRF One — hardware, RF specs, gain, sampling

Source: hackrf.readthedocs.io `/hackrf_one`, `/hardware_components`, `/setting_gain`, `/sampling_rate` — fetched 2026-07. HackRF One is Great Scott Gadgets' open-source **half-duplex** SDR transceiver.

## Headline specs

| Spec | Value |
|---|---|
| Operating frequency | **1 MHz – 6 GHz** |
| Sample rate | **2 – 20 Msps** (quadrature / complex), default 10 Msps |
| Resolution | **8-bit** (quadrature I/Q) |
| Duplex | **Half-duplex** — transmit *or* receive, never both at once |
| Interface | High-Speed USB 2.0 (USB Micro-B), USB bus-powered |
| Antenna connector | SMA female, **50 Ω** |
| Antenna port power (bias tee) | Software-controlled, **max 50 mA at 3.0–3.3 V** |
| Clock | SMA female **clock in and out** for synchronization (10 MHz) |
| **Max input power** | **−5 dBm** |

> ⚠️ **The −5 dBm rule is the one that kills boards.** "Exceeding −5 dBm can result in permanent damage." That's ~0.3 mW — very little. Anything near a transmitter, a strong broadcast tower, or a TX antenna in the same room can exceed it. Use attenuation and keep TX/RX antennas apart. There is **no input protection you can rely on**.

## The half-duplex + 8-bit reality (why HackRF behaves as it does)

- **Half-duplex** means no simultaneous TX and RX. You cannot listen while you transmit; full-duplex work needs two radios (or a different SDR like a USRP/BladeRF).
- **8-bit ADC** (~48 dB of dynamic range before processing gain) is coarse compared to 12–16-bit SDRs (RTL-SDR is 8-bit too; Airspy/SDRplay are 12-bit). It means gain staging matters a lot — a strong and a weak signal in the same capture will fight for those 8 bits. Set gain to fill the range without clipping.
- **Zero-IF / quadrature** architecture is why you get the **DC spike** at center frequency (see the troubleshooting reference) and I/Q imbalance images. These are architectural, not defects.

## Transmit power (varies wildly by band)

Output is **not flat** across the range. Approximate max TX power: **5–15 dBm** at lower frequencies, dropping to **−10 to 0 dBm** at 4–6 GHz. Best performance is **2170–2740 MHz (13–15 dBm)**. HackRF is a *test-equipment-grade* transmitter — low power, not clean enough for on-air service without filtering. **Its output is rich in harmonics and spurs; transmitting without a band-pass/low-pass filter splatters energy across other bands.**

## The RF signal chain (major ICs)

Receive and transmit share a chain built from:

- **MAX2837** — 2.3–2.7 GHz transceiver / baseband (the tunable IF stage; MAX2839 substitutes on r9, MAX2831 on HackRF Pro). Provides the **baseband filter**.
- **MAX5864** — 8-bit **ADC/DAC** (the sampler; its lower spec limit is why <8 Msps is discouraged).
- **RFFC5072** — wideband **mixer/synthesizer** that translates the 0–6 GHz RF to/from the MAX2837's ~2.6 GHz IF.
- **Si5351C** — clock generator (derives sample and reference clocks; the bias tee / CLKIN / CLKOUT hang off this).
- **LPC4320/4330** — ARM Cortex-M4 + M0 MCU running the firmware; moves samples over USB via SGPIO.
- **CoolRunner-II CPLD** — the SGPIO glue between MCU and MAX5864 (its gateware is what `hackrf_cpldjtag` flashes; HackRF Pro uses an ice40 FPGA instead).
- **W25Q80BV** — 8-Mbit SPI flash holding the firmware image.

**RX path:** antenna → RF amp (optional) → RFFC5072 mixer → MAX2837 (IF + baseband filter + LNA/VGA) → MAX5864 ADC → CPLD/SGPIO → MCU → USB.
**TX path:** the reverse — USB → MCU → MAX5864 DAC → MAX2837 → mixer → RF amp (optional) → antenna.

## Gain stages — the three RX knobs (and two TX knobs)

Getting gain right is *the* skill for 8-bit RX. Three cascaded analog stages on receive:

| Stage | Flag | Range | Steps | Notes |
|---|---|---|---|---|
| **RF amp** ("amp") | `-a 0\|1` | ~**11 dB** on / 0 off | on/off | Front-end LNA. Enable only for weak signals; it also amplifies noise and can overload. |
| **IF / LNA gain** | `-l` | **0–40 dB** | **8 dB** | Coarse. In the MAX2837 front end. |
| **Baseband / VGA gain** | `-g` | **0–62 dB** | **2 dB** | Fine. After the baseband filter. |

**Transmit** has two: the **RF amp** (`-a`, ~11 dB on/off) and the **TX VGA (IF) gain** (`-x`, **0–47 dB, 1 dB steps**).

**Recommended RX starting point (from the docs):** `RF amp = 0 (off)`, `IF/LNA = 16`, `baseband/VGA = 16`. Then:
- **Too little gain** → the signal is buried in the noise floor.
- **Too much gain** → distortion, spurious tones, and images (ADC clipping). If you see harmonics/artifacts that move when you change gain, back off.
- **Order of adjustment:** turn the RF amp on only if a weak signal needs it; otherwise raise LNA then VGA until the signal is well above the noise floor but the waterfall isn't saturating.

## Sampling rate & baseband filter

- **Don't go below 8 Msps.** The MAX5864 ADC/DAC "lacks specifications for operation below 8 MHz," so behavior is unpredictable. The MAX2837's **minimum baseband filter is 1.75 MHz**, which at a 2 Msps rate only gives ~4 dB attenuation at ±1 MHz and ~33 dB at ±2 MHz — aliasing leaks in.
- **To actually work at a low effective rate**, sample at **8 Msps and decimate** in software (e.g. a GNU Radio 4:1 decimation block with a sharp complex low-pass < 1 MHz cutoff). Oversampling + decimation also buys you processing gain against the 8-bit floor.
- **Usable bandwidth < sample rate.** The band edges roll off; treat the clean portion as roughly the baseband-filter width, centered.
- **Baseband filter bandwidths** (MAX2837, settable with `-b` in Hz): **1.75 / 2.5 / 3.5 / 5 / 5.5 / 6 / 7 / 8 / 9 / 10 / 12 / 14 / 15 / 20 / 24 / 28 MHz**. If you don't set `-b`, the tools auto-select **≤ 0.75 × sample_rate**.

## Clock, bias tee, external sync

- **Bias tee** (`-p 1` on the tools): feeds **3.0–3.3 V, max 50 mA** up the antenna coax to power an external LNA/amp. Off by default; don't enable it into something that isn't expecting DC.
- **CLKIN / CLKOUT** (SMA): feed HackRF a **10 MHz** reference (or take its clock out) to phase-align multiple units or discipline it to a GPSDO for frequency accuracy. Managed with `hackrf_clock`.
- **Frequency accuracy** comes from the onboard crystal (tens of ppm). For precise work, correct with `-C <ppm>` (transfer) or supply an external 10 MHz reference.
