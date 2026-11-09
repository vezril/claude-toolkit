# Writing a VST 3 plug-in

Everything below comes from Steinberg's VST 3 developer portal
(steinbergmedia.github.io/vst3_dev_portal), checked 2026-11-08 against SDK 3.8, unless it
carries a label. Interface names are exact; check signatures against the headers in
`pluginterfaces/vst/`.

## The shape of a plug-in

A VST 3 plug-in is a **module** (the `.vst3` bundle) that exports a **factory**
(`GetPluginFactory`, `IPluginFactory`/`2`/`3`). The factory describes one or more classes,
each with a class ID (a 128-bit FUID), a category and subcategories (`"Fx|EQ"`,
`"Instrument|Synth"`), which hosts use to sort their browsers.

An effect or instrument is **two components**:

| Part | Interfaces | Owns | Runs on |
|---|---|---|---|
| **Processor** | `IComponent` + `IAudioProcessor` (helper: `AudioEffect`) | The DSP and the authoritative state | Audio thread for `process` and `setProcessing`; UI thread for the rest |
| **Edit controller** | `IEditController` (helpers: `EditController`, `EditControllerEx1`) | Parameter descriptions, the editor (`IPlugView`), GUI-only state | UI thread |

Keep them separate and set the `kDistributable` flag in the processor's class info, so a host
may run them in different processes or on different machines. A single class implementing both
is allowed but discouraged. The host connects them through `IConnectionPoint`; private messages
use `IMessage` and `IAttributeList`. Don't assume the connection is direct, and **never send a
message from inside `process`**.

## Lifecycle

1. `initialize(context)` once; the context should implement `IHostApplication`. `setIoMode`
   comes before it.
2. `setupProcessing(ProcessSetup)`: sample rate, maximum block size, 32- or 64-bit samples
   (`canProcessSampleSize`), real-time or offline mode. **Allocate everything here**, sized to
   the maximum block.
3. `setBusArrangements(...)`: the host proposes a channel layout. Accept it or return
   `kResultFalse`, and the host asks for your default.
4. `setActive(true)`: configuration is finished. Nothing above may change while active.
5. `setProcessing(true)`: reset the DSP state (delay lines, filters, envelopes). Then
   `process` calls start.
6. Teardown runs the reverse: `setProcessing(false)`, `setActive(false)`, `terminate()`.

## Parameters

- Every parameter crossing the host boundary is a **normalized double between 0 and 1**
  (`ParamValue`), identified by a `ParamID` (a 32-bit integer).
- **A `ParamID` is forever.** Projects and automation lanes store it. Renumber one and every saved
  session silently points at the wrong control. Add new IDs; never reuse or reorder old ones.
- The controller converts between normalized and real values (`normalizedParamToPlain`,
  `plainParamToNormalized`, `getParamStringByValue`). `stepCount` > 0 makes it discrete (a
  switch or a menu).
- Flags: `kCanAutomate` for anything a user should automate; `kIsBypass` on exactly one
  parameter (hosts wire their bypass button to it); `kIsReadOnly` for meters and other
  processor-to-host output; `kIsHidden`; `kIsProgramChange`.
- **User edits from your editor** go to the host through `IComponentHandler`: `beginEdit`,
  `performEdit` (any number), `endEdit`, in that order, on the UI thread. `IComponentHandler2`
  adds `startGroupEdit` and `finishGroupEdit` for several parameters moved together. The host
  records automation and forwards the change to the processor. **The processor learns about
  GUI edits and automation the same way**, through `process`.

## process()

All data arrives in `ProcessData`:

- `numSamples` is between 1 and the maximum block size, **or 0**: a call with zero samples and
  zero buses only flushes parameter changes. Handle it without touching buffers.
- `inputs` / `outputs` are `AudioBusBuffers` per bus (`channelBuffers32` or `channelBuffers64`,
  plus `silenceFlags`). Buffers are supplied for every bus you declared, including inactive ones,
  but the pointers can be null. Skip deactivated buses.
- `inputParameterChanges` (`IParameterChanges`) holds one `IParamValueQueue` per changed
  parameter, each with (sample offset, value) points, so automation is sample-accurate. At a
  minimum, take the last point; better, ramp between points.
- `outputParameterChanges` carries processor-to-host values (meters, gain reduction). They
  reach the controller via `setParamNormalized`.
- `inputEvents` (`IEventList`): note on/off, poly pressure, Note Expression values.
- `processContext` carries tempo, time signature, musical position and transport state. It can
  be null, and each field is valid only if its flag in `state` is set.

```cpp
tresult PLUGIN_API MyProcessor::process (Vst::ProcessData& data)
{
    if (auto* changes = data.inputParameterChanges)
    {
        for (int32 i = 0, n = changes->getParameterCount (); i < n; ++i)
        {
            auto* queue = changes->getParameterData (i);
            if (!queue || queue->getPointCount () == 0)
                continue;
            int32 offset;
            Vst::ParamValue value;
            if (queue->getPoint (queue->getPointCount () - 1, offset, value) != kResultTrue)
                continue;
            if (queue->getParameterId () == kGainId)
                gainTarget = value;   // smoothed toward per sample below; no allocation, no locks
        }
    }
    if (data.numSamples == 0 || data.numOutputs == 0)
        return kResultOk;             // parameter flush only
    // ... DSP on data.outputs[0].channelBuffers32, ramping gain toward gainTarget ...
    return kResultOk;
}
```

## MIDI, notes and Note Expression

- **There are no MIDI CC events in VST 3.** An instrument that wants the mod wheel, pitch bend
  or aftertouch implements `IMidiMapping::getMidiControllerAssignment` on the **controller**,
  mapping each controller number to a `ParamID`. The host then sends those as parameter
  changes. SDK 3.8 adds `IMidiMapping2` and `IMidiLearn2` for MIDI 2.0.
- Notes arrive as `NoteOnEvent` / `NoteOffEvent` with a `noteId`, so per-note expression can
  target one voice. `INoteExpressionController` declares the expression types (tuning, volume,
  pan, brightness...). Cubase is the reference host for Note Expression.
- An instrument declares an **event input bus**; to send MIDI out, declare an event output bus
  (`LegacyMIDICCOutEvent` carries CCs out).

## Buses, side-chains and layouts

- Declare audio buses in `initialize` with `addAudioInput` / `addAudioOutput` and a
  `SpeakerArrangement`. Bus 0 is `kMain`; a side-chain is a second input bus of type `kAux`,
  usually inactive until the user routes something to it.
- Support the layouts you can actually process (mono, stereo, surround or ambisonics) and
  refuse the rest in `setBusArrangements`.

## State and versioning

- **Processor** `getState` / `setState`: the full DSP state. This is what a project saves.
- **Controller** `setComponentState`: the host passes the processor's state to the controller
  after loading, so the controller can sync its parameters. Don't call back into the handler while
  doing it.
- **Controller** `getState` / `setState`: GUI-only things (editor size, the selected tab).
- **Write a version number first** in every stream, and read old versions forever. A plug-in that
  can't open last year's projects loses its users' work. Use `IBStreamer` for endian-safe
  reads and writes.

## Latency, tail and bypass

- Report processing latency in `getLatencySamples`. If it changes (an oversampling or lookahead
  switch), call `IComponentHandler::restartComponent(kLatencyChanged)` from the controller; the
  host deactivates, re-reads and reactivates.
- Report the tail in `getTailSamples` (reverb and delay ring-out; `kNoTail`, `kInfiniteTail`),
  so hosts don't cut it off when rendering.
- When bypassed through the `kIsBypass` parameter, keep passing audio **delayed by the reported
  latency** and crossfade the switch, or bypassing shifts the track in time and clicks.

## The real-time rules

The audio thread has a deadline every block. Inside `process` (and anything it calls):

- **No heap allocation or freeing**: no `new`, `malloc`, growing `std::vector`, or
  `std::string` building. Allocate in `setupProcessing` / `setActive`.
- **No locks** that the UI thread can hold: no `std::mutex`, no waiting. Use atomics for single
  values and a lock-free single-producer/single-consumer FIFO for anything larger (UI to audio
  and back).
- **No I/O or system calls**: no files, network, logging, `printf`, or message sending.
- **No unbounded work**: no loops whose length depends on user data or UI state.
- **Denormals:** set flush-to-zero and denormals-are-zero for the block (MXCSR on x86, FPCR on
  Arm), or feedback filters and reverbs spike the CPU as they decay to silence.
- **Smooth parameter changes** (one-pole or linear ramps), or automation zippers.

Most "crackles at low buffer sizes" and "CPU spikes when I move a knob" bugs break one of these.

## The editor

`IEditController::createView("editor")` returns an `IPlugView`. VSTGUI (in the SDK, with a
drag-and-drop UIDescription editor) is the default toolkit, but any can be used. Resize through
`IPlugFrame::resizeView`; support HiDPI on Windows with `IPlugViewContentScaleSupport`. The
editor only ever changes parameters through the edit calls above. It never touches the
processor directly.

## The SDK's tools

| Tool | Use it for |
|---|---|
| **validator** (command line, source included) | Conformity tests. Run it on every build: `validator path/to/MyPlugin.vst3` |
| **VST3PluginTestHost** (macOS, Windows) | Loading, automating and stress-testing in a minimal host |
| **EditorHost** | Opening just the editor |
| **VST3 Inspector** | Seeing what a scan of the VST 3 folder reports |
| **Project Generator** (macOS, Windows) | A new CMake project with a processor, controller and IDs |
| **Wrappers** | AU, AUv3 and AAX from the same VST 3 code |

The SDK builds with CMake. Platforms supported by SDK 3.8: Windows 11 (x86, x86_64, arm64,
arm64EC) and Windows 8.1/10 (x86, x86_64) with MSVC 2019–2026; macOS 10.14–26 (Intel and Apple
Silicon) with Xcode 10–26.5; iOS 13–26; Linux (Ubuntu 24.04 LTS) with GCC 13.3+.

## The bundle

```
MyPlugin.vst3/
└── Contents/
    ├── Info.plist, PkgInfo        (macOS)
    ├── MacOS/MyPlugin             (macOS: universal Mach-O)
    ├── x86_64-win/MyPlugin.vst3   (Windows: a DLL per architecture; arm64x-win is recommended for Windows on Arm)
    ├── x86_64-linux/MyPlugin.so   (Linux)
    └── Resources/
        ├── moduleinfo.json
        └── Snapshots/             (browser thumbnails: <class-ID>_snapshot.png and _snapshot_2.0x.png)
```

`moduleinfo.json` describes the module's classes so hosts can scan without loading the binary,
and lists the VST2 IDs a plug-in replaces (its `Compatibility` section). The SDK's build
generates it; regenerate it whenever classes or IDs change.

## Release checklist

- [ ] The validator passes; `pluginval` passes at a high strictness level.
- [ ] Tested in at least two hosts (Cubase plus Reaper or Bitwig), at several buffer sizes and
      sample rates, with offline rendering.
- [ ] Old project states load (keep a folder of saved states from every release).
- [ ] ParamIDs unchanged since the last release; new parameters appended.
- [ ] Latency and tail reported; bypass is latency-aligned.
- [ ] macOS: universal binary (`lipo -archs`), signed with Developer ID and the hardened
      runtime, notarized and stapled (`frameworks-and-licensing.md`).
- [ ] Installs to the standard folders (`using-plugins.md`); `moduleinfo.json` current.
- [ ] Trademark use follows Steinberg's VST usage guidelines if you show the VST name or logo.
