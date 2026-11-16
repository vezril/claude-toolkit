# Testing your own VST 3 plug-in in Cubase

Cubase is the VST reference host: Steinberg writes both, and it exercises parts of VST 3 that
other hosts skip (Note Expression, side-chain buses, surround and ambisonic layouts,
`IMidiMapping`). How to write the plug-in is in [[vst-plugins]]; this is how to get it into
Cubase and debug it there.

## Getting Cubase to load a build

1. **Build VST 3, for the architecture Cubase runs as.** On an Apple Silicon Mac, Cubase 13
   runs natively and loads only native VST 3. An x86_64-only debug build won't appear unless
   Cubase is under Rosetta. Build arm64 (or universal) and check with `lipo -archs`.
2. **Put it in a scanned folder.** The VST 3 SDK's CMake build can link the built bundle into
   your user VST3 folder (`~/Library/Audio/Plug-Ins/VST3/` on macOS) `[CHECK]` (the SDK's CMake
   options). Otherwise copy it there. Remove old copies elsewhere: the first plug-in found with
   a given class ID wins.
3. **Rescan.** Cubase scans at startup. After changing class IDs, categories or
   `moduleinfo.json`, restart Cubase so it rescans.
4. **Blocklist.** A build that crashed or hung during the scan is moved to the Blocklist in
   Studio > VST Plug-in Manager and stays there. Fix the crash, then reactivate it from the
   Blocklist. The validator usually reproduces a scan crash faster than Cubase does.

## Debugging inside Cubase

- **Attach a debugger** to the running Cubase process (Xcode: Debug > Attach to Process;
  Visual Studio: Debug > Attach to Process), or set Cubase as the executable for your plug-in
  target so the debugger launches it. Set breakpoints in `initialize`, `setupProcessing`,
  `setState` and the editor; be careful breaking in `process`, because the audio engine times
  out and may restart.
- **macOS:** a debugger can attach to a signed host only if its hardened runtime allows it.
  If attaching fails, debug in the SDK's VST3PluginTestHost or EditorHost first, or in a host
  built for debugging `[CHECK]`.
- **Start clean:** Safe Start Mode (hold Ctrl/Cmd + Alt/Opt + Shift at launch) can deactivate
  all third-party plug-ins, which gets you back in after a plug-in crash at startup.
- **Plug-in Report** (in the VST Plug-in Manager) records what Cubase sees for your plug-in:
  version, path, categories.

## What to exercise in Cubase specifically

| Area | How to test it in Cubase |
|---|---|
| **Automation** | Write automation in each mode (Touch, Auto-Latch, Cross-Over), including fast curves, and check sample accuracy by rendering |
| **State** | Save, close and reopen the project; save and load a preset; duplicate the track; undo after a parameter change |
| **Offline render** | Export Audio Mixdown and Render in Place (offline, faster than real time); compare with real-time playback |
| **Latency** | Change the latency at run time (`restartComponent(kLatencyChanged)`) and check that delay compensation follows; try Constrain Delay Compensation |
| **Bypass** | Cubase's bypass button drives your `kIsBypass` parameter; check there's no click or time shift |
| **Side-chain** | Activate the side-chain input and route a track to it |
| **Layouts** | Insert on mono, stereo and surround channels; switch a track between mono and stereo (new in 13) |
| **MIDI** | Mod wheel and pitch bend through `IMidiMapping`; Note Expression from the Key Editor; an instrument on several MIDI channels |
| **ASIO-Guard** | Play with ASIO-Guard on (large, ahead-of-time blocks) and record-enable the track (real-time path, small blocks): your `process` must handle both |
| **Sample rates and block sizes** | Change the project rate and the buffer; `setupProcessing` must reallocate everything |

## Cubase-specific extras

- **Track name and colour:** a plug-in can be told its channel's name and colour through VST
  3's channel context interface (`IInfoListener`) `[CHECK]` (the VST 3 API docs).
- **Quick Controls and MIDI Remote** reach your plug-in through its automatable parameters:
  give parameters short, clear titles and units, and use `kCanAutomate` deliberately.
- **Free Cubase versions for testing:** Cubase LE and AI come with many audio interfaces, and
  Steinberg offers trials of the full editions. That's enough to check a user's bug report in
  the edition they have.
