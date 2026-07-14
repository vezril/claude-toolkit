# HackRF One — firmware, the SDR software ecosystem, troubleshooting

Source: hackrf.readthedocs.io `/updating_firmware`, `/software_support`, `/troubleshooting`, `/opera_cake` — fetched 2026-07.

## Firmware & CPLD updates

Host tools and device firmware should be **version-matched** — a mismatch causes odd behavior (amplified DC spike, missing features). Check with `hackrf_info`; update if the tools are newer.

**Normal update (device boots and enumerates):**
```bash
hackrf_spiflash -w hackrf_one_usb.bin      # write firmware to SPI flash
# then press RESET, or unplug/replug
```
The `.bin` image lives in the `firmware-bin/` directory of the latest release package (or build from source). Use the file named for your board — `hackrf_one_usb.bin` for HackRF One. **Only `.bin` files go to SPI flash.**

**DFU mode** (for recovery, or a first-ever flash): hold the **DFU** button while powering on *or* while pressing and releasing **RESET**, then release DFU. On HackRF One the **3V3 LED** lights to confirm DFU mode.

**Recovery (SPI flash damaged / empty):**
```bash
sudo apt install dfu-util
# 1. enter DFU mode (above), then load firmware into RAM over DFU:
dfu-util --device 1fc9:000c --alt 0 --download hackrf_one_usb.dfu
# 2. now that it runs, write the .bin to SPI flash so it persists:
hackrf_spiflash -w hackrf_one_usb.bin
```
**Only `.dfu` files are used in DFU mode**, never `.bin`. (`1fc9:000c` is the DFU USB ID.)

**CPLD** only needs flashing on firmware **older than 2021.03.1**:
```bash
hackrf_cpldjtag -x firmware/cpld/sgpio_if/default.xsvf   # 3 blinking LEDs = success
```

## The SDR software ecosystem (what actually uses the HackRF)

The CLI tools are for capture/replay/sweep; for live listening, decoding, and analysis you use third-party software that links **libhackrf** (often via **SoapySDR/SoapyHackRF** or **gr-osmosdr**):

| Software | For |
|---|---|
| **GNU Radio** (+ `gr-osmosdr`) | The signal-processing toolkit — build flowgraphs (GNU Radio Companion) for demod/decode/custom DSP. The serious platform. |
| **SoapySDR / SoapyHackRF** | Vendor-neutral SDR abstraction; the bridge many apps use to reach the HackRF. |
| **GQRX** | Cross-platform receiver + waterfall — the easy "just listen" app (Linux/macOS). |
| **SDR#** (SDRSharp) | Windows receiver; HackRF via nightly/plugin. |
| **SDRangel / SDR Console** | Full-featured multi-mode RX (and TX on SDRangel). |
| **CubicSDR** | Cross-platform waterfall receiver (via SoapySDR). |
| **Universal Radio Hacker (URH)** | Analyze/decode/replay digital protocols — great for reverse-engineering ISM-band devices. |
| **inspectrum** | Offline visual analysis of a captured I/Q file (find bursts, measure symbol rate). |
| **SigDigger** | Cross-platform signal analyzer (via SoapyHackRF). |
| **QSpectrumAnalyzer / Spectrum Analyzer GUI** | Front-ends for `hackrf_sweep`'s wideband output. |
| **Baudline** | Signal/FFT analysis of captured data. |

Rule of thumb: **`hackrf_sweep`** to find *where* the energy is → **GQRX/SDR#** to listen and identify → **`hackrf_transfer -r`** to capture I/Q → **inspectrum/URH/GNU Radio** to decode offline.

## Troubleshooting

**"No HackRF boards found" / not detected:**
1. `lsusb` (Linux) / Device Manager (Windows) / System Report (macOS) — does the OS see it at all?
2. **Cable** — a charge-only USB cable has no data lines. Swap it. This is the #1 cause.
3. **Permissions** — non-root USB access needs udev rules (see the tools reference); test with `sudo hackrf_info` to confirm it's a permissions issue.
4. **VM / WSL** — you must pass the USB device through to the guest.
5. **DFU test** — boot into DFU mode; if it enumerates there, the firmware image is the problem — reflash.
6. **PortaPack** users: make sure "HackRF" mode is selected.

**Big spike in the center of the spectrum (at every tuned frequency):** that's the **DC offset**, an artifact of the zero-IF/quadrature architecture — the average (DC) value of the I/Q stream, not a real signal. An old `gr-osmosdr` against newer firmware makes it worse (version-match). Three responses:
- **Ignore it** — fine for many uses.
- **Offset-tune** — tune a few hundred kHz off your target so the signal of interest sits away from 0 Hz, then shift it back in software.
- **DC removal** — a software DC-block, though it also notches real signals near 0 Hz.

**Distortion / phantom signals / images that move with gain:** you're overloading the 8-bit ADC. Turn the RF amp off, drop LNA then VGA until the artifacts vanish (see the gain section in the hardware reference). Also suspect a too-strong nearby source — add attenuation.

**Dropped samples ("U"/"O" overrun markers):** the host can't keep up — use a faster disk/SSD, a lower sample rate, USB 3 port (still USB-2 speed but better hubs), and close other USB load.

**Poor sensitivity / nothing received:** confirm antenna is for the band, gains aren't all at 0, the bias tee isn't wrongly on/off for your setup, and you're within 1 MHz–6 GHz. Remember HackRF is a *general-coverage* radio — a resonant antenna for your target band beats the stock ANT500 telescoping whip.

## Opera Cake (antenna switch add-on)

An 8-port RF switch board (ports A0–A3, B0–B3) that rides on the HackRF expansion header, letting one HackRF select among antennas/filters automatically. Driven by `hackrf_operacake` in **manual**, **frequency** (port per band), or **time** (dwell N samples per port) mode — useful for scanning multiple antennas or auto-switching band-pass filters during a `hackrf_sweep`. See the tools reference for the flags.
