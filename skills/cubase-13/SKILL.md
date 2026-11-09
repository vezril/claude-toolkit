---
name: cubase-13
description: "Steinberg Cubase 13 (Pro, Artist, Elements; 13.0.x, released November 2023): setup and troubleshooting (activation, the audio system, ASIO and Core Audio, ASIO-Guard and the Audio Performance panel, the VST Plug-in Manager and Blocklist, Apple Silicon versus Rosetta and VST2, Safe Start mode), recording and editing (inputs, monitoring and latency, takes, lanes and comping, AudioWarp, hitpoints, VariAudio, Direct Offline Processing), MIDI and composition (Key, Drum and Score editors, drum maps, Expression Maps, Note Expression, the chord track, Chord Pads and Chord Assistant, MIDI effects, the Logical Editor, MIDI Remote), mixing and mastering (the MixConsole, the new Channel tab, groups, FX channels, VCAs, side-chains, Direct Routing, Control Room, the stock plug-ins including VocalChain, EBU R128 loudness, Export Audio Mixdown, Render in Place), and testing VST 3 plug-ins you write. Use whenever someone works in Cubase or asks how to do something in it."
---

# Cubase 13

Cubase 13 is Steinberg's DAW, released 2 November 2023 in three editions (Pro, Artist,
Elements). Its 13.0.x updates ran through 2024. Cubase 14 (November 2024) and 15 (November 2025)
have followed `[CHECK]`, so check the version before assuming a feature: some answers here are
wrong for 12 and some are out of date for 14.

The authority for everything in this skill is the **Cubase Pro 13.0.30 Operation Manual** (the
PDF on steinberg.help), plus the separate Plug-in Reference. `references/sources.md` says
what was checked there and what wasn't.

## Before answering, establish

1. **Edition: Pro, Artist or Elements** (or the bundled AI/LE). Pro has everything; Artist and
   Elements leave features out and Elements caps track counts. If an answer depends on a
   feature that may be Pro-only, say so and point to Steinberg's edition comparison chart. Don't
   guess which edition has it.
2. **Exact version** (the About Cubase window, e.g. 13.0.41: the Help menu on Windows, the Cubase menu on macOS). Several features arrived in point
   releases (`references/sources.md` lists them).
3. **OS and chip.** Windows versus macOS changes the driver (ASIO versus Core Audio), the
   modifier keys (Ctrl/Alt versus Cmd/Opt), and the Preferences menu (Edit > Preferences on
   Windows, Cubase > Preferences on macOS). On an Apple Silicon Mac, native versus Rosetta
   decides whether VST2 plug-ins load at all.
4. **The audio interface and its buffer size,** for anything about latency, dropouts or recording.

## Always apply

- **Give menu paths exactly as the manual writes them** (Studio > Studio Setup, File > Export >
  Audio Mixdown). If you aren't sure of a path, name the window and say where it's documented,
  rather than inventing one.
- **Prefer non-destructive routes.** Cubase usually has one: Direct Offline Processing keeps an
  editable process list; render to new tracks and disable the originals rather than deleting
  them; save a new project version (File > Save New Version) before big edits.
- **Plug-in problems go through the VST Plug-in Manager first** (Studio > VST Plug-in Manager),
  then [[vst-plugins]] for anything format- or OS-level.
- **Loudness is a target you choose, not a setting.** Cubase 13's Export Audio Mixdown has no
  loudness-normalize option. You reach a LUFS target with the master chain and the loudness
  meter. Streaming platforms' normalization levels are their policies: give them as `[CHECK]`.
- **Don't help bypass licensing** (Steinberg Activation Manager), and never ask for a Steinberg
  ID password.

## Workflows

| They ask about | Read |
|---|---|
| Installing, activating, audio setup, dropouts, crashes on start, missing plug-ins, Apple Silicon and VST2 | `references/setup-and-troubleshooting.md` |
| Recording audio, monitoring, latency while tracking, takes and comping, timing and pitch editing | `references/recording-and-editing.md` |
| MIDI editing, drum maps, articulations, chords, MIDI controllers, the bundled instruments | `references/midi-and-composition.md` |
| MixConsole, routing, buses and side-chains, the stock plug-ins, metering, export, stems, mastering | `references/mixing-and-mastering.md` |
| Testing a VST 3 plug-in they are writing, in Cubase | `references/developing-plugins-in-cubase.md` |
| What changed in 13, or whether a claim was checked | `references/sources.md` |

## What's new in 13 (so you don't send someone to a 12 tutorial)

From the manual's New Features list:

- **13.0.0:**
  - VocalChain, VoxComp, Black Valve, EQ-P1A, EQ-M5, the Vocoder (returning) and an improved
    TestGenerator.
  - The new **Channel tab** in the Project window, and a **MixConsole overhaul**.
  - The **Range Selection tool in the Key and Drum Editors**, and the **Visibility tab** for
    editing several MIDI parts.
  - Redesigned **Chord Pads**.
  - Mono/stereo switching for audio, group and FX tracks; track versions on video tracks;
    renaming several events at once; playback start modes.
  - Spectral AudioWarp modes in Sampler Control; Tap Tempo on the Transport.
  - A new Key Commands dialog; overhauled MIDI effects.
  - HALion Sonic 7, and SpectraLayers One 10.
- **13.0.10:** replace the audio in selected video files; bypass a process in Direct Offline
  Processing to audition.
- **13.0.20:** Tap Tempo modes.
- **13.0.30:** project files over 2 GB; range-limited tempo and signature track import.
