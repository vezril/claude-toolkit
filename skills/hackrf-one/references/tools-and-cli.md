# HackRF One — the command-line tools

Source: hackrf.readthedocs.io `/hackrf_tools`, `/installing_hackrf_software`, plus the tools' own `usage()` in greatscottgadgets/hackrf `host/hackrf-tools/src/*.c` — fetched 2026-07. These ship in the **HackRF Tools** package on top of **libhackrf** (the low-level library other SDR software links against).

## The toolset at a glance

| Tool | Does |
|---|---|
| `hackrf_info` | Read device info — serial number, board ID, firmware & API version. First thing to run. |
| `hackrf_transfer` | Receive to / transmit from a file of **8-bit signed I/Q** samples. The workhorse. |
| `hackrf_sweep` | Command-line **spectrum analyzer** — sweep a wide range, emit power-per-bin. |
| `hackrf_clock` | Read/write clock input & output (CLKIN/CLKOUT, references, triggers). |
| `hackrf_operacake` | Configure an **Opera Cake** antenna switch. |
| `hackrf_spiflash` | Write firmware to SPI flash. |
| `hackrf_cpldjtag` | Flash the CPLD gateware (`.xsvf`) — needed only on old firmware. |
| `hackrf_debug` | Read/write registers & low-level config for debugging. |

## `hackrf_info` — verify the device

Prints per-board: serial number, board ID, firmware version, part ID, and supported API. If it says **"No HackRF boards found"** or errors, stop and fix that before anything else (see the troubleshooting reference). Run it first, always.

## `hackrf_transfer` — RX/TX to files

The sample file is **interleaved 8-bit signed I/Q** (`int8` I, `int8` Q, repeating). Every flag (authoritative, from source `usage()`):

```
-d serial_number   # target a specific HackRF by serial
-r <filename>      # RECEIVE into file  ('-' = stdout)
-t <filename>      # TRANSMIT from file ('-' = stdin)
-w                 # RX into a WAV file with auto name (SDR# compatibility)
-f freq_hz         # center frequency in Hz (1 MHz–6 GHz supported)
-i if_freq_hz      # explicit IF frequency (advanced/manual tuning)
-o lo_freq_hz      # explicit front-end LO frequency (advanced/manual tuning)
-m image_reject    # image-reject filter: 0=bypass, 1=low-pass, 2=high-pass
-a amp_enable      # RX/TX RF amplifier: 1=enable, 0=disable  (~11 dB)
-p antenna_enable  # bias-tee antenna port power: 1=enable, 0=disable (3.0–3.3 V)
-l gain_db         # RX LNA (IF) gain, 0–40 dB, 8 dB steps
-g gain_db         # RX VGA (baseband) gain, 0–62 dB, 2 dB steps
-x gain_db         # TX VGA (IF) gain, 0–47 dB, 1 dB steps
-s sample_rate_hz  # sample rate in Hz (2–20 MHz supported, default 10 MHz)
-F                 # force parameters outside supported ranges (use with care)
-n num_samples     # number of samples to transfer (default: unlimited)
-S buf_size        # enable receive streaming with the given buffer size
-B                 # print buffer statistics during transfer
-c amplitude       # CW (constant carrier) source, amplitude 0–127 (DC value to DAC)
-R                 # repeat TX mode — loop the TX file (default off)
-b bw_hz           # baseband filter bandwidth in Hz (see the valid set below)
-C ppm             # correct internal crystal clock error, in ppm
-H                 # synchronize RX/TX to an external trigger input
```

Valid `-b` bandwidths: **1.75 / 2.5 / 3.5 / 5 / 5.5 / 6 / 7 / 8 / 9 / 10 / 12 / 14 / 15 / 20 / 24 / 28 MHz**. Omit it and the tool picks **≤ 0.75 × sample_rate**.

### Worked recipes

```bash
# RX 8 seconds of the 2m ham band region to a file (10 Msps → 8s ≈ 160 MB)
hackrf_transfer -r fm.iq -f 100000000 -s 10000000 -l 24 -g 20 -n 80000000

# RX to stdout and pipe into GNU Radio / a decoder (stream forever)
hackrf_transfer -r - -f 433920000 -s 8000000 -l 32 -g 30 | your_decoder

# Spectrum sweep 2.4 GHz ISR band, 1 MHz bins, print to terminal
hackrf_sweep -f 2400:2500 -w 1000000

# TX a prepared I/Q file once (KNOW THE LAW FIRST — see SKILL.md)
hackrf_transfer -t payload.iq -f 315000000 -s 8000000 -x 20

# Generate a single CW tone (test signal into a dummy load / shielded setup)
hackrf_transfer -c 127 -f 915000000 -s 8000000 -x 10
```

> **File size math:** 8-bit I/Q = **2 bytes/sample**. At 10 Msps that's **20 MB/s** (~1.2 GB/min). Captures fill disks fast; use `-n` to bound them, and a fast SSD to avoid dropped samples ("`U`" overrun markers).

## `hackrf_sweep` — wideband spectrum analyzer

Sweeps across a range far wider than the instantaneous bandwidth and reports FFT power per bin. Flags (from docs):

```
-d serial     # device serial
-a 0|1        # RX RF amp enable
-f min:max    # frequency range in MHz (e.g. -f 2400:2500)
-p 0|1        # antenna port (bias tee) power
-l gain_db    # RX LNA gain, 0–40 dB, 8 dB steps
-g gain_db    # RX VGA gain, 0–62 dB, 2 dB steps
-w bin_width  # FFT bin width in Hz (2445 – 5000000)
-1            # one-shot (single sweep)
-N num        # number of sweeps then exit
-B            # binary output
-I            # binary inverse-FFT output (for a waterfall consumer)
-r filename   # write output to file
```

Output rows are CSV: date, time, hz_low, hz_high, hz_bin_width, num_samples, then one dB value per bin. Pipe `-B`/`-I` binary into a visualizer (e.g. the Spectrum Analyzer GUI, QSpectrumAnalyzer).

## `hackrf_clock` — clock & sync

```
-r <clock_num> / -a   # read one / all clock settings
-i                    # CLKIN status (is an external ref present?)
-o <0|1>              # enable/disable CLKOUT
-d <serial>           # target device
# (HackRF Pro adds -1/-2/-c for the P1/P2 SMA signal routing)
```
Use to confirm an external 10 MHz reference is detected (`-i`) or to fan a clock out to a second HackRF for phase-aligned multi-receiver work.

## `hackrf_operacake` — antenna switch

Opera Cake is an 8-port (A0–A3, B0–B3) RF switch add-on. Modes: **manual**, **frequency** (auto-select a port per band), **time** (dwell N samples per port).

```
-o <n>           # Opera Cake address (default 0)
-m <mode>        # manual | frequency | time
-a <port>        # port connected to A0
-b <port>        # port connected to B0
-f <port:min:max># frequency mode: assign port for min–max MHz (repeatable)
-t <port:dwell>  # time mode: dwell on port for N samples (repeatable)
-w <n>           # default dwell time (samples) for time mode
-l               # list connected Opera Cake boards
-g               # GPIO self-test
```

## Installing the tools

```bash
# Linux
sudo apt install hackrf          # Debian/Ubuntu
sudo dnf install hackrf -y       # Fedora/RHEL
sudo pacman -S hackrf            # Arch
# macOS
brew install hackrf              # (or: sudo port install hackrf)
# Windows: use radioconda, or the GitHub Actions build artifacts
```

**From source** (to match host tools to newer firmware):
```bash
git clone https://github.com/greatscottgadgets/hackrf.git
cd hackrf/host && mkdir build && cd build
cmake .. && make && sudo make install && sudo ldconfig
```

### Non-root access (udev, Linux)

Out of the box a normal user may get USB permission errors from `hackrf_info`. The distro `hackrf` package usually installs udev rules; if not, add a rule granting your user (or the `plugdev` group) access to USB vendor **1d50** (product **6089** for HackRF One; **1fc9:000c** in DFU mode), then replug. `lsusb` should show the device either way.
