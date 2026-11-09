# Sources and how sure each claim is

Checked 2026-11-08. Re-check anything here before quoting it as current.

| Claim | Label | Source |
|---|---|---|
| VST 3 SDK is MIT from 3.8.0; the GPLv3 and proprietary options are gone | `[VERIFIED]` | Steinberg developer portal, "VST 3 License" and "What is the VST 3 SDK"; Steinberg press release, 2025-10-29; SDK 3.8.0 forum release post (dated 2025-10-20) |
| VST name and logo optional; trademark guidelines apply if used | `[VERIFIED]` | Steinberg developer portal |
| SDK 3.8 adds `IMidiMapping2` and `IMidiLearn2` (MIDI 2.0) and ships VSTGUI 4.15 | `[VERIFIED]` | Press coverage of the 3.8 release (Sound On Sound, CDM, heise, 2025-10/11) consistent with the portal |
| ASIO SDK now also GPLv3 | `[CHECK]` | Press coverage (heise, Libre Arts, Nov 2025) |
| VST2 SDK withdrawn and no new licences from October 2018 | `[CHECK]` | Many developer forum threads (JUCE, KVR, Renoise) quoting Steinberg's 2018 notice |
| Processor/controller split, lifecycle, parameter, event, bus, state and threading rules | `[VERIFIED]` | Steinberg developer portal, API documentation index |
| VST3 install folders per OS and the first-found rule | `[VERIFIED]` | Steinberg developer portal, "Plug-in Locations" |
| `.vst3` bundle layout, Windows architecture folders, `moduleinfo.json`, Snapshots; single-file `.vst3` deprecated since 3.6.10 | `[VERIFIED]` | Steinberg developer portal, "Plug-in Format Structure" |
| SDK tools (validator, test hosts, Project Generator, wrappers) and supported platforms/compilers | `[VERIFIED]` | Steinberg developer portal, "What is the VST 3 SDK" |
| Cubase loads VST2 on Apple Silicon only under Rosetta; native mode is VST3 only | `[VERIFIED]` | Steinberg FAQ and help-centre articles |
| Rosetta ends after macOS 27 | `[CHECK]` | Apple's WWDC 2025 announcement as repeated by Steinberg's help centre |
| Cubase has no CLAP support through version 15 | `[CHECK]` | User reports of the Cubase 15 release notes (Steinberg forum, KVR, Nov 2025) |
| JUCE 8 tiers and revenue caps | `[CHECK]` | JUCE forum summaries of the JUCE 8 EULA (2024–2025). The EULA text governs |
| Host format support table | `[CHECK]` | Vendor documentation as generally known; host support changes with each release |
| CLAP folder locations | `[CHECK]` | CLAP headers (`entry.h`) |

Where to look when something here goes stale:

- Steinberg VST 3 developer portal: https://steinbergmedia.github.io/vst3_dev_portal/
- VST 3 SDK on GitHub: https://github.com/steinbergmedia/vst3sdk
- CLAP: https://github.com/free-audio/clap
- JUCE licence: https://juce.com/legal/
- Apple notarization: https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
