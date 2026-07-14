---
name: hackrf-one
description: "Operating the HackRF One — Great Scott Gadgets' open-source, half-duplex software-defined radio (SDR) transceiver — for receiving, analyzing, and (where legally authorized) transmitting RF. A query-answering reference distilled from the official docs (hackrf.readthedocs.io, fetched 2026-07) plus the tools' own usage() source. Covers the specs (1 MHz–6 GHz, 2–20 Msps quadrature, 8-bit, half-duplex, −5 dBm max input), the RF signal chain and ICs (MAX2837 transceiver, MAX5864 ADC/DAC, RFFC5072 mixer, Si5351C clock, LPC43xx MCU, CoolRunner-II CPLD), the three RX gain stages (RF amp -a, LNA/IF -l 0–40 dB/8 dB, VGA/baseband -g 0–62 dB/2 dB) and TX gain (-x 0–47 dB/1 dB), sample-rate & baseband-filter choice (why <8 Msps is discouraged; the 1.75–28 MHz filter set), the command-line tools (hackrf_info, hackrf_transfer with every flag, hackrf_sweep spectrum analyzer, hackrf_clock, hackrf_operacake, hackrf_spiflash/DFU firmware recovery, hackrf_cpldjtag, hackrf_debug), the 8-bit signed I/Q file format, install (apt/brew/source, libhackrf, udev), the SDR software ecosystem (GNU Radio/gr-osmosdr, SoapySDR, GQRX, SDR#, URH, inspectrum), the DC-offset spike and ADC-overload artifacts, troubleshooting device-not-found, the bias tee and external 10 MHz clock sync, and the Opera Cake antenna switch. Use to answer specific HackRF One questions — a flag's meaning, gain staging, capturing/replaying I/Q, running a sweep, flashing firmware, choosing SDR software, fixing a DC spike — or to plan an SDR capture/analysis workflow. Dual-use RF hardware: RECEIVE broadly for learning, but TRANSMIT only on bands/power you are licensed or legally authorized to use."
argument-hint: "[your HackRF One question]"
license: MIT
---

# HackRF One

The **HackRF One** (Great Scott Gadgets) is an open-source **software-defined radio**: a wideband **half-duplex transceiver** covering **1 MHz – 6 GHz**, sampling **2–20 Msps** of **8-bit** quadrature I/Q over USB. It's a general-purpose RF front end — the DSP happens in software on the host (GNU Radio, GQRX, URH, or your own code). This skill answers questions about operating it, distilled from the official docs and the tools' source.

> ## Two rules before anything else
>
> **1. Receiving is broad; transmitting is legally gated.** Listening across the spectrum for learning is generally fine in most places, but **the airwaves are regulated** — transmitting on a given frequency and power almost always requires a licence (amateur/ham, or a band-specific authorization) or is outright illegal (cellular, aviation, GPS, public-safety, licensed broadcast). HackRF makes it *trivial* to transmit somewhere you shouldn't; the responsibility is yours. **When a question involves TX, I'll answer the mechanics and flag the legal constraint — I won't help jam, spoof, or interfere with systems you don't own or aren't authorized to test.** For legitimate TX, use a dummy load or a shielded/Faraday setup, a band-pass filter (HackRF output is harmonic-rich), and your own licensed band.
>
> **2. −5 dBm max input — exceeding it permanently damages the board.** That's ~0.3 mW. Keep it away from transmitters and strong sources; attenuate when in doubt. There's no protection to fall back on.

Load a reference for depth:

- **[references/hardware-and-specs.md](references/hardware-and-specs.md)** — full specs, the half-duplex/8-bit consequences, the RF signal chain & ICs, TX power by band, the **three gain stages** and how to stage them, sample-rate & baseband-filter selection, the bias tee and external clock.
- **[references/tools-and-cli.md](references/tools-and-cli.md)** — every command-line tool with complete flags (`hackrf_transfer`, `hackrf_sweep`, `hackrf_clock`, `hackrf_operacake`, `hackrf_spiflash`, …), the **8-bit signed I/Q** format, worked recipes, capture-size math, install & udev.
- **[references/firmware-software-troubleshooting.md](references/firmware-software-troubleshooting.md)** — firmware update & **DFU recovery**, the SDR software ecosystem (what to use for what), the **DC-offset spike** and ADC-overload artifacts, device-not-found troubleshooting, Opera Cake.

## The mental model

- **HackRF is a front end, not an application.** It moves raw I/Q between the antenna and USB; everything meaningful (demodulation, decoding, display) happens in host software. Pick the software for the job (see the ecosystem table).
- **Half-duplex, 8-bit, zero-IF — internalize the consequences.** No simultaneous TX+RX. Only 8 bits of dynamic range, so **gain staging is the core skill**. The zero-IF architecture is *why* you get the DC spike and I/Q images — expected, not broken.
- **Wide coverage ≠ great performance everywhere.** 1 MHz–6 GHz is general-coverage; a resonant antenna for your target band and correct gain beat the stock ANT500 whip. TX power is low and uneven across bands.
- **The three CLI tools cover most workflows:** `hackrf_info` (verify) → `hackrf_sweep` (find the energy) → `hackrf_transfer` (capture/replay I/Q). Live listening and decoding are third-party software.

## First contact

```bash
hackrf_info        # serial, board id, firmware/API version — run this first
```
No output / "No HackRF boards found" → it's almost always the **USB cable** (charge-only cables have no data lines) or **permissions** (udev). See troubleshooting.

## Cheat-sheet

| Want to… | Do |
|---|---|
| Verify the device | `hackrf_info` |
| See where signals are (2.4 GHz) | `hackrf_sweep -f 2400:2500 -w 1000000` |
| Capture I/Q to a file | `hackrf_transfer -r out.iq -f <hz> -s 8000000 -l 32 -g 24 -n <samples>` |
| Stream I/Q to a decoder | `hackrf_transfer -r - -f <hz> -s 8000000 \| your_tool` |
| Replay / transmit a file (licensed band!) | `hackrf_transfer -t in.iq -f <hz> -s 8000000 -x 20` |
| Power an external LNA up the coax | add `-p 1` (bias tee, 3.0–3.3 V, 50 mA) |
| Update firmware | `hackrf_spiflash -w hackrf_one_usb.bin` (then RESET) |

**Gain starting point (RX):** RF amp off (`-a 0`), `-l 16`, `-g 16`; raise until the signal clears the noise floor but the waterfall isn't saturating. **File size:** 8-bit I/Q = 2 bytes/sample → 10 Msps ≈ 20 MB/s.

## Gotchas

- **The center spike isn't a signal.** It's the DC offset from zero-IF sampling. Ignore it, offset-tune around it, or DC-block it — don't chase it.
- **Artifacts that move when you change gain = ADC overload.** Turn the amp off and reduce LNA/VGA. More gain is not more signal past the clip point.
- **Match host tools to firmware.** A version mismatch amplifies the DC spike and hides features; `hackrf_info` shows both versions.
- **Don't sample below 8 Msps.** The ADC is unspecified there and the baseband filter can't keep aliases out — oversample at ≥8 Msps and decimate in software instead.
- **Transmitting without a filter splatters.** HackRF's output is rich in harmonics/spurs; a band-pass/low-pass filter is mandatory for any real on-air TX.
- **`-F` forces out-of-range parameters.** It exists; it doesn't make the hardware good outside spec. Know why you're using it.

## Related

- [[wifi-pineapple]] — the toolkit's other dual-use RF/wireless auditing device (802.11-specific appliance); same "authorized use only" discipline.
- [[network-security]] · [[secure-coding]] — the security context for RF/wireless work and handling captured data responsibly.
- [[information-theory]] — the signal/noise, bandwidth, and channel-capacity fundamentals under SDR (sampling, dynamic range, Nyquist).
- [[python]] — host-side I/Q processing and automation (NumPy on the 8-bit I/Q stream, driving the tools).

Sources: hackrf.readthedocs.io — `/hackrf_one`, `/hardware_components`, `/setting_gain`, `/sampling_rate`, `/hackrf_tools`, `/installing_hackrf_software`, `/updating_firmware`, `/software_support`, `/troubleshooting`, `/opera_cake` — plus the tools' `usage()` in github.com/greatscottgadgets/hackrf (`host/hackrf-tools/src/`). Fetched 2026-07. HackRF is open hardware under a permissive licence; verify current firmware filenames and regulatory rules for your jurisdiction before relying on them.
