# Setup and troubleshooting

Menu paths are quoted from the Cubase Pro 13.0.30 Operation Manual. The manual writes
Windows-style paths; on macOS, Preferences is under the Cubase menu.

## Licensing

Cubase 12 and later activate through the **Steinberg Activation Manager**, signed in with a
Steinberg ID; the USB eLicenser is gone `[CHECK]` (Steinberg's licensing pages; the Operation
Manual doesn't cover activation). Activation limits and moving a licence between computers are
on Steinberg's support pages. Never ask for, or type in, a Steinberg ID password, and never help
get around activation.

## System requirements and macOS versions

At launch, Cubase 13 supported Windows 10 and 11, and macOS 12 Monterey and 13 Ventura. Later
13.0.x updates added Sonoma `[CHECK]` (Steinberg's system requirements and compatibility pages;
retailer listings disagree). For a macOS released after Cubase 13 stopped being updated, check
Steinberg's compatibility page before promising it works.

## The audio system

1. **Studio > Studio Setup**, then **Audio System** in the Devices list.
2. Choose the driver:
   - **Windows:** the interface maker's own ASIO driver. If there isn't one, Cubase's **Generic
     Low Latency ASIO Driver** works, with more latency. The manual is clear that a
     hardware-specific ASIO driver is more efficient.
   - **macOS:** the interface's Core Audio device. Well-written Core Audio drivers give very
     low latency. Some extra features (the ASIO Positioning Protocol) exist only with ASIO.
3. **Buffer size** is set in the driver's control panel (from the same page). Small for
   recording; large for mixing.
4. **Studio > Audio Connections** sets up the input and output buses. A missing input is usually
   a bus that was never created here, not a driver fault.

On macOS, Cubase also needs microphone permission (System Settings > Privacy & Security >
Microphone) to receive any audio input, including a USB interface.

## Performance: ASIO-Guard and the Audio Performance panel

The Audio System page holds the relevant switches:

- **Activate Multi Processing** spreads the load over all CPU cores.
- **Activate ASIO-Guard** (needs Multi Processing) processes in advance whatever doesn't have
  to be live. **ASIO-Guard Level** trades stability against latency and memory: higher is more
  stable, with more ASIO-Guard latency. Tracks that are record-enabled or being monitored live
  have to run in the real-time path, outside ASIO-Guard.
- **Activate Steinberg Audio Power Scheme** (Windows) turns off power saving that hurts
  real-time processing. It only helps at very low latencies and raises power use.
- VST 2 plug-ins are always processed at 32-bit precision.

Read the **Audio Performance** panel when there are dropouts:

| Meter | Means | If it's high |
|---|---|---|
| **ASIO-Guard** | Average load of the processing done in advance | More cores, freeze tracks, larger ASIO-Guard level |
| **Peak** | Load in the real-time path | Raise the buffer, take heavy plug-ins off record-enabled or monitored tracks, freeze |
| **Processing Overload** indicator | Dropouts happened (over 100% load, or the engine restarted) | Cut active effects, EQ modules and simultaneous channels, or turn on ASIO-Guard |
| **Disk Cache** | Disk transfer load | Faster drive; fewer simultaneous tracks |

## Plug-ins: the VST Plug-in Manager

**Studio > VST Plug-in Manager** lists effects and instruments:

- **Collections:** the active collection decides what the effect and instrument selectors show.
  Make your own to hide what you never use.
- **Blocklist:** plug-ins that are installed but **not loaded**, because they may make Cubase
  unstable or crash it. A plug-in that crashed during the scan lands here. Update it, then
  reactivate it from the Blocklist.
- **VST 2 Plug-in Path Settings:** the folders Cubase scans for VST 2 plug-ins. VST 3 plug-ins
  are found in the standard VST3 folders ([[vst-plugins]]).
- **Plug-in Report:** saves a text file with system and plug-in information for support.

### Apple Silicon, Rosetta and VST2

- Cubase 13 on an Apple Silicon Mac starts **natively**, and then loads **only native VST 3
  plug-ins**. VST 2 can't be enabled in native mode `[VERIFIED]` (Steinberg help centre and FAQ).
- To load VST 2 or Intel-only plug-ins, run Cubase under **Rosetta**: select the Cubase 13 app in
  the Finder, press Cmd-I, tick **Open using Rosetta**. Everything then runs translated, which
  costs CPU.
- Steinberg lists VST 2 as not officially supported, even where it loads, and Rosetta is being
  withdrawn after macOS 27 `[CHECK]`. Move projects to VST 3 versions now (see "Moving a project
  from VST2 to VST3" in [[vst-plugins]]).

## When Cubase won't start or behaves strangely

1. **Safe Start Mode:** quit Cubase, then launch it while holding **Ctrl/Cmd + Alt/Opt +
   Shift**. The dialog has two sections:
   - **Preferences:** *Use current program preferences*, *Disable program preferences* (start
     with factory settings and keep yours on disk), or *Delete program preferences* (can't be
     undone, and affects **every** Cubase version installed). Try *Disable* first. If Cubase
     then works, the preferences were the problem.
   - **Plug-Ins:** *Deactivate all third-party plug-ins*. The manual names a third-party
     plug-in as the most likely cause when Cubase won't start or a project won't load.
2. **Plug-in suspects:** if Cubase crashes while scanning, check the Blocklist, then move
   recently installed plug-ins out of the VST folders and restart.
3. **A project that crashes on load:** start in Safe Start Mode with third-party plug-ins
   deactivated, then open it. If it's damaged, open an automatic backup from the project folder
   (named `<project name>-xx.bak`, where xx counts up) or an earlier File > Save New Version
   copy.
4. **Collect the Plug-in Report** before contacting Steinberg or a plug-in vendor.
