---
name: vst-plugins
description: "Virtual Studio Technology (VST) audio plug-ins, from both sides of the host boundary. Using them: the formats (VST2, VST3, AU/AUv3, AAX, CLAP, LV2) and which hosts load which, install folders per OS, scanning and blocklists, Apple Silicon versus Rosetta, Gatekeeper, licence managers, latency and delay compensation, and a troubleshooting order for a missing or crashing plug-in. Building them: the VST 3 SDK (MIT since 3.8, October 2025), the processor/controller split, normalized parameters and sample-accurate automation, buses, MIDI mapping and Note Expression, state and versioning, latency and bypass, the real-time rules for the audio thread, the validator and test hosts, the .vst3 bundle and moduleinfo.json, frameworks (JUCE, iPlug2, CLAP, nih-plug), wrappers to AU/AAX, and macOS signing and notarization. Use whenever someone installs, troubleshoots, compares or writes an audio plug-in, mentions VST, VST3, .vst3, the Steinberg SDK, JUCE, CLAP, AU or AAX, or asks why a DAW can't see a plug-in."
---

# VST plug-ins: using them and building them

VST is Steinberg's plug-in standard: a host (a DAW such as Cubase, Reaper or Live) loads a
shared library that processes audio or MIDI. There are two audiences for this skill, and most
questions belong to one of them:

- **The user** installs, scans, picks and troubleshoots plug-ins. Start in
  `references/using-plugins.md`.
- **The developer** writes them. Start in `references/vst3-development.md`, then
  `references/frameworks-and-licensing.md`.

`references/formats-and-hosts.md` serves both: it says which format a given host loads, and
that decides almost everything else. For Cubase-specific behaviour (its Plug-in Manager, its
Apple Silicon rules, testing your own plug-in in it), the [[cubase-13]] skill goes deeper.

## Label what you state

Plug-in facts age fast: hosts add and drop formats, SDK licences change, and macOS removes
things. Label claims that could be stale:

| Label | Means |
|---|---|
| `[VERIFIED]` | From the standard's own documentation (Steinberg's VST 3 developer portal, the CLAP repo, Apple's docs) or the host vendor's manual |
| `[CHECK]` | From one secondary source, a forum, or a dated article. Say where and when, and tell the person to confirm |
| `[UNVERIFIED]` | No source found. Don't give the detail; point to where it would be documented |

`references/sources.md` lists what each key claim rests on and when it was checked
(2026-11-08). Host format support is the claim most likely to have moved; when it matters,
check the host's current release notes.

## Always apply

1. **Ask for the host, its version and the OS (with chip) before diagnosing.** "Plug-in not
   showing" has a different answer in Cubase on an M-series Mac (VST3 native only) than in
   Reaper on Windows (anything, if the path is scanned).
2. **Name the format, not just "VST".** A `.vst3` bundle, a VST2 `.dll`/`.vst`, an AU
   `.component` and a `.clap` are different files in different folders. Most "missing plug-in"
   reports are a format the host doesn't load, or a file in the wrong folder.
3. **VST2 is a legacy format.** Steinberg stopped licensing the VST2 SDK in October 2018, and
   Cubase on Apple Silicon loads VST2 only under Rosetta, which Apple is winding down. Steer new
   work and new installs to VST3 (or CLAP/AU where the host prefers them). Never help obtain the
   VST2 SDK from an unofficial copy.
4. **Developers: the audio thread is sacred.** No allocation, locks, file or network I/O,
   logging, or waiting on the UI inside `process`. Check any audio code you write or review
   against the rules in `references/vst3-development.md` before anything else.
5. **Validate before you blame the host.** Run Steinberg's `validator` on a VST 3 build, `auval`
   on an AU, and `clap-validator` on a CLAP before debugging a host-specific crash.
6. **Don't defeat copy protection.** Help with licence managers (iLok, vendor activators) as a
   user would, but never with cracking, keygens, or bypassing activation. Removing the macOS
   quarantine flag is only for software the person bought from the vendor's own site.
7. **Licensing is a fact to check, not a guess.** State the licence of an SDK or framework with
   its date, and for anything commercial, point to the licence text itself.

## Workflows

**"My DAW can't see plug-in X."** Follow the order in `references/using-plugins.md`: right
format for the host → right folder → right architecture (arm64 vs x86_64) → host rescanned →
not on the host's blocklist → not blocked by Gatekeeper or a missing licence. Stop at the first
failure.

**"Which format should I install / ship?"** Read `references/formats-and-hosts.md`. For a user:
VST3 everywhere it's loaded, AU for Logic and GarageBand, AAX for Pro Tools. For a developer:
VST3 + AU + CLAP covers every mainstream host but Pro Tools; AAX needs Avid's developer program.

**"Help me write a plug-in."** Choose the framework first (`frameworks-and-licensing.md`): the raw
VST 3 SDK for VST3 only, JUCE or iPlug2 for several formats from one codebase, CLAP plus wrappers
for a CLAP-first design, nih-plug for Rust. Then build the skeleton from
`vst3-development.md`: parameters, process, state, then the editor. Validate at every step.

**"My plug-in crackles / spikes the CPU."** Usually the real-time rules (allocation or locks in
`process`), denormals, or unsmoothed parameters. Check those before profiling the DSP.

**"Ship it."** The release checklist at the end of `vst3-development.md`: universal binary on
macOS, signed with Developer ID and the hardened runtime, notarized and stapled, installed into
the standard folders, `moduleinfo.json` current, the validator passing.

## References

| File | Load when |
|---|---|
| `references/formats-and-hosts.md` | Which format a host loads, VST2 vs VST3 vs AU vs AAX vs CLAP vs LV2, migration between them |
| `references/using-plugins.md` | Install folders, scanning, blocklists, Apple Silicon and Rosetta, Gatekeeper, licence managers, CPU and latency, troubleshooting |
| `references/vst3-development.md` | Writing a VST 3 plug-in: architecture, parameters, automation, buses, MIDI, state, latency, threading and real-time rules, tools, bundle, release checklist |
| `references/frameworks-and-licensing.md` | Choosing JUCE / iPlug2 / CLAP / nih-plug / the raw SDK, wrappers to AU and AAX, the licences, trademark use, macOS signing and notarization |
| `references/sources.md` | Before stating a licence, a host's format support, or a date |
