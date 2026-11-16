# Mixing and mastering

## Where to mix

- **MixConsole** (F3; Alt/Opt-F3 opens it inside the Project window): the full mixer. It was overhauled in 13 to put
  more focus on the mix. Its left zone controls which channels are visible, holds mix history
  (undo for parameter changes) and MixConsole snapshots.
- **Channel tab** (new in 13): a compact, per-channel mixer in the Project window's left zone.
  It shows the selected track's channel, so you can mix without leaving the arrangement. Every
  audio and MIDI-related track has a channel that can show there.
- **Channel Settings** (the "e" button): one channel's full strip, inserts and sends.

## Routing

| Tool | What it's for |
|---|---|
| **Group channels** | Sum tracks (drums, backing vocals) to process them together |
| **FX channels** | Shared send effects (reverb, delay), fed from sends |
| **VCA faders** | Control several channels' levels together, without summing their audio |
| **Side-chains** | Feed one channel into a plug-in's side-chain input (ducking, keyed gates). Instruments that accept MIDI side-chains are covered under Side-Chaining for VST Instruments |
| **Direct Routing** | Send one channel to several output destinations and switch between them, e.g. for stems or different mix versions |
| **Control Room** | A separate monitoring path (cue mixes for performers, speaker switching, talkback), so what you hear isn't what you export |

Some of these (Control Room and Direct Routing in particular) are commonly listed as Pro-only
`[CHECK]` Steinberg's edition comparison chart.

From 13 you can switch audio, group and FX tracks between mono and stereo after creating them.

## The stock plug-ins worth knowing (13)

New in 13 (each documented in the Plug-in Reference):

- **VocalChain:** modules for cleaning, character and typical vocal effects, in one plug-in.
- **VoxComp:** an adaptive vocal compressor.
- **Black Valve:** a tube compressor. The manual's New Features page repeats VocalChain's
  wording for it by mistake; the Plug-in Reference describes it properly.
- **EQ-P1A** (vintage tube EQ with shelves and a high peak) and **EQ-M5** (vintage tube EQ for
  mids).
- **Vocoder** (returned), and **Frequency 2** (now with an adjustable gain range in its
  display).

Long-standing staples: Frequency 2 (dynamic and linear-phase EQ), the Channel Strip modules,
Squasher and MultibandCompressor, Imager, REVerence and REVelation reverbs, SuperVision metering
`[CHECK]` (the Plug-in Reference, which this skill didn't read; contents vary by edition).

## Metering and loudness

- The **master meter** is a multi-channel true-peak meter.
- The **loudness meter** measures to **EBU R 128**: integrated, short-term and momentary
  loudness, and loudness range.
- Meter scales include Digital, DIN, EBU, British, Nordic, and K-20/K-14/K-12.

**Loudness targets** are something you mix and limit to; Cubase 13 exports at whatever level
the mix is. Common references `[CHECK]` (each platform's current policy):

- Broadcast follows EBU R 128 at **−23 LUFS** integrated.
- Streaming services normalize playback to roughly **−14 LUFS**.
- Most engineers leave about **−1 dBTP** true-peak headroom for lossy encoding.

## Export

**File > Export > Audio Mixdown** opens the Export Audio Mixdown dialog:

- **Channel Selection:** *Single* (one channel, usually the main output) or *Multiple* (stems:
  several groups, FX or tracks at once).
- **File Location** with a naming scheme (attributes such as the channel name), **File
  Format** (type, sample rate, bit depth), **Export Range** (locators or cycle markers),
  **Realtime Export** (for plug-ins or hardware that must run in real time), and *Deactivate
  External MIDI Inputs* during export.
- **Export Queue:** add jobs with different settings and run them in one go.

## Committing and saving CPU

- **Freeze** (Freeze Channel in the Inspector) renders an instrument or a track's inserts to a
  temporary file and unloads them. Unfreeze to edit.
- **Render in Place** (Edit > Render in Place) prints tracks or ranges to new audio tracks. The
  Render Settings choose what's included: Dry (Transfer Channel Settings, so the new track
  keeps the plug-ins live), Channel Settings, Complete Signal Path, or Complete Signal Path +
  Master FX. They also set a tail (so reverbs ring out) and what happens to the source tracks:
  keep, mute, **disable** (frees CPU and RAM like Freeze, and is reversible), or remove. It's
  the better choice when the result is final, or when you're making stems for someone else.

## A short mastering chain in Cubase

On the Stereo Out (or a separate mastering project):

1. Corrective EQ (Frequency 2, linear phase if phase matters).
2. Gentle glue compression or multiband control.
3. Stereo image (Imager), sparingly.
4. A true-peak limiter, set to the ceiling you chose.
5. Watch the integrated loudness on the loudness meter while playing the whole song, not one
   loud chorus.
6. Export at the project's sample rate and 24-bit or 32-bit float. Make delivery formats (MP3,
   16-bit with dither) as separate jobs in the queue.
