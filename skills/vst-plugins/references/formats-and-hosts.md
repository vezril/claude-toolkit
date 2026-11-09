# Formats and hosts

## The formats

| Format | Owner | File on disk | Status (checked 2026-11) |
|---|---|---|---|
| **VST2** | Steinberg | `.dll` (Windows), `.vst` bundle (macOS), `.so` (Linux) | Legacy. SDK no longer distributed and no new licences since October 2018 `[CHECK]` (forum and press reports; Steinberg's own statement is the 2018 announcement). Still loaded by many hosts |
| **VST3** | Steinberg | `.vst3` bundle (a folder) on every platform | Current. SDK under the **MIT licence since 3.8.0** (released 2025-10-20, announced 2025-10-29) `[VERIFIED]` |
| **AU (AUv2)** | Apple | `.component` bundle, macOS only | Current on macOS. Required by Logic Pro and GarageBand |
| **AUv3** | Apple | App extension inside an app; macOS and iOS | Current. The only plug-in format on iOS/iPadOS hosts |
| **AAX** | Avid | `.aaxplugin` bundle | Pro Tools only. Needs Avid's developer program and PACE signing to run in release Pro Tools |
| **CLAP** | Bitwig + u-he (open, MIT) | `.clap` (a bundle on macOS, a shared library elsewhere) | Released 2022. Open standard, no licence agreement. Host support still growing |
| **LV2** | Open (ISC) | `.lv2` folder | Mostly the Linux ecosystem (Ardour, Carla, Reaper) |

The **legacy single-file `.vst3` on Windows** (a renamed DLL) has been deprecated since VST
3.6.10; the current format is the folder bundle. Old installers still produce it, and hosts
still load it `[VERIFIED]`.

## Which host loads which

Format support is the claim most likely to have changed since this was written. Confirm with
the host's current manual or release notes before relying on a row.

| Host | Loads | Notes |
|---|---|---|
| **Cubase / Nuendo** | VST3; VST2 on Windows and Intel Macs, and on Apple Silicon **only under Rosetta** | No AU. No CLAP through Cubase 15, per users reading the release notes `[CHECK]`. See [[cubase-13]] |
| **Logic Pro, GarageBand, MainStage** | AU / AUv3 only | A VST-only plug-in is invisible here. `auval` validates |
| **Pro Tools** | AAX only | |
| **Ableton Live** | VST2, VST3, AU (macOS) | No CLAP `[CHECK]` |
| **Reaper** | VST2, VST3, AU, CLAP, LV2, JSFX | The most permissive host; good for testing |
| **Bitwig Studio** | CLAP, VST2, VST3 | CLAP's co-author. Runs plug-ins in separate processes (sandboxing), so one crash doesn't take down the session |
| **FL Studio, Studio One** | VST2, VST3, AU (macOS); CLAP reported in recent versions | `[CHECK]` the CLAP support and from which version |

## Choosing a format

**As a user:** install the VST3 version unless the host needs something else (AU for Logic, AAX for
Pro Tools). Install VST2 only if the host can't load VST3 or an old project needs it. Installing
several formats of the same plug-in is harmless, but it duplicates entries in the browser; most
hosts let you hide one.

**As a developer:** VST3 + AU + CLAP from one codebase covers every mainstream host except Pro
Tools. Add AAX only if Pro Tools users are a target, because of the program and signing
overhead. Don't start a new VST2 product.

## Moving a project from VST2 to VST3

A host can only swap a VST2 instance for its VST3 successor if the developer declared the link.
The VST3 plug-in lists the VST2 IDs it replaces, in the `Compatibility` section of
`moduleinfo.json` (or through `IPluginCompatibility`). When it does, Cubase and other VST3 hosts
load the VST3 version in place of the VST2 one and keep the settings `[CHECK]`. When it doesn't,
the project opens with the plug-in missing: re-insert the VST3 version and recreate the
settings, or keep a machine or Rosetta setup that still loads the VST2.

Before removing VST2 plug-ins from a Mac, open the important old projects once with the VST3
versions installed, and see which slots come up empty.
