# Sources and what was checked

Checked 2026-11-08.

## The authority

**Cubase Pro 13.0.30 Operation Manual** (English PDF, from steinberg.help). Every menu path,
window name, option name and the New Features list in this skill were checked against it. The
manual writes Windows-style menu paths; on macOS, Preferences is under the Cubase menu. The
separate **Plug-in Reference** (stock plug-ins in detail) was not read; claims about stock
plug-ins beyond the New Features list are labelled `[CHECK]`.

The New Features list, by version (from the manual):

| Version | Features |
|---|---|
| 13.0.0 | VocalChain; the Channel tab; Range editing in the MIDI editors; the MixConsole overhaul; the Visibility tab; Chord Pads redesign; Vocoder; Black Valve; VoxComp; EQ-P1A; EQ-M5; TestGenerator; adjustable left-zone width; extended track import; mono/stereo switching; track versions for video; renaming several events; playback start modes; marker track improvements; Sampler Control (Spectral modes, envelope editor, 20-step history); Ambisonics and head-tracking improvements; step input; Tap Tempo; the Key Commands dialog; Frequency 2 gain range; MIDI effects overhaul; HALion Sonic 7; SpectraLayers One 10; Windows multi-window handling; mouse-wheel zoom; Add Track improvements; Range to hitpoint; removing MIDI Remote mappings by right-click |
| 13.0.10 | Replacing audio in selected video files; bypass in Direct Offline Processing |
| 13.0.20 | Tap Tempo modes |
| 13.0.30 | Hub Quit button (Windows); project files over 2 GB; range-limited tempo and signature track import; track name font weight (Windows) |

Later 13.0.x updates (after 13.0.30) were not checked.

## Other claims

| Claim | Label | Source |
|---|---|---|
| Released 2 November 2023 | `[VERIFIED]` | KVR and press coverage, 2023-11-02 |
| Cubase 14 (Nov 2024) and 15 (Nov 2025) followed | `[CHECK]` | Press coverage and forum threads |
| Launch OS support: Windows 10/11, macOS 12/13; later updates added Sonoma | `[CHECK]` | Steinberg product info and retailer listings, which disagree in places |
| Apple Silicon native mode is VST 3 only; VST 2 needs Rosetta; VST 2 is not officially supported | `[VERIFIED]` | Steinberg help centre and FAQ |
| Rosetta ends after macOS 27 | `[CHECK]` | Steinberg help centre, repeating Apple |
| Licensing through Steinberg Activation Manager since Cubase 12 | `[CHECK]` | Steinberg licensing pages (not in the Operation Manual) |
| Which features are Pro-only | `[CHECK]` | Steinberg's edition comparison chart; not in the Pro manual |
| Bundled instruments and Iconica Sketch | `[CHECK]` | 13.0.0 press coverage |
| MIDI Remote scripting in JavaScript | `[CHECK]` | Steinberg's MIDI Remote API documentation |
| Streaming loudness levels (about −14 LUFS) and −1 dBTP headroom | `[CHECK]` | Platform policies, which change |
| EBU R 128 broadcast target of −23 LUFS | `[VERIFIED]` | EBU R 128 |

## Where to look next

- Operation manuals and the Plug-in Reference: https://www.steinberg.help/
- Steinberg help centre (known issues, compatibility): https://helpcenter.steinberg.de/
- System requirements: https://www.steinberg.net/system-requirements
