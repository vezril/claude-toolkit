---
name: game-audio
description: Game audio — sound design, music, and audio programming/DSP for games — distilled from *The Audio Programming Book* (Boulanger & Lazzarini) and applied through Godot's audio system. Covers digital audio fundamentals (sampling rate, bit depth, PCM, the Nyquist limit, buffers/latency), synthesis (oscillators, envelopes/ADSR, additive/subtractive/FM) and sample playback, DSP effects (gain, filters, delay, reverb, distortion, dynamics), spatial/3D audio (panning, attenuation/falloff, doppler, occlusion, HRTF), interactive & adaptive music (layering/vertical remixing, horizontal re-sequencing, transitions/stingers), mixing (buses, ducking, sidechain, mastering, loudness), procedural/generative audio, and the engine/middleware view (audio buses & AudioStreamPlayers in Godot; FMOD/Wwise for bigger projects). Use when implementing game sound/music, designing an adaptive music system, programming DSP/synthesis, setting up spatial audio or a mix bus structure, or reducing audio latency. Builds on information-theory/game-math (signals) and pairs with godot (audio buses), game-design (feel), and game-graphics (juice).
---

# Game Audio

**Sound, music, and audio programming** for games — the most under-appreciated half of game feel. From **Richard Boulanger & Victor Lazzarini's *The Audio Programming Book*** (DSP/synthesis foundations) applied through [[godot]]'s audio system. Sound is half the experience: it carries feedback, atmosphere, and a huge share of "juice."

Cross-links: [[godot]] (audio buses, `AudioStreamPlayer`), [[game-design]] (audio as feedback & feel), [[game-graphics]] (juice — audio + visual together), [[information-theory]] / [[game-math]] (audio is signal processing).

## Digital audio fundamentals

- **Sound = a waveform**; digitized by **sampling** at a **sample rate** (44.1/48 kHz) with a **bit depth** (16/24-bit) → **PCM** samples. The **Nyquist limit**: you can represent frequencies up to half the sample rate (so 48 kHz → up to 24 kHz); above it **aliases** ([[information-theory]] sampling theorem).
- **Buffers & latency** — audio is processed in blocks; smaller buffers = lower latency but more CPU/risk of dropouts. Game audio must stay low-latency so a sound fires *with* the action (feel).
- **Channels** (mono/stereo/surround) and formats (WAV/PCM uncompressed for SFX, OGG/MP3 compressed for music).

## Synthesis & sample playback

- **Sample playback** — the common case: trigger recorded one-shots/loops; pitch-shift for variety; round-robin & randomized pitch/volume to avoid the "machine-gun" repetition effect.
- **Synthesis** (when you generate sound): **oscillators** (sine/saw/square/noise), **envelopes** (**ADSR** — attack/decay/sustain/release shape a sound's amplitude over time), and methods — **additive** (sum harmonics), **subtractive** (filter a rich source), **FM** (modulate frequency). Foundations from the *Audio Programming Book* (C/Csound). Useful for retro/chiptune and procedural SFX.

## DSP effects

Process samples in the signal chain: **gain/volume**, **filters** (low/high/band-pass — shape tone, simulate muffling/occlusion), **delay/echo**, **reverb** (space/room simulation — the biggest atmosphere tool), **distortion/overdrive**, **EQ**, and **dynamics** (compressor/limiter to control level, **gate**). Order in the chain matters. ([[godot]] provides these as **bus effects**.)

## Spatial / 3D audio

Place sound in the world:
- **Panning** (stereo position) and **distance attenuation** (falloff curves — linear/inverse/log) so far sounds are quieter.
- **3D positional audio** (`AudioStreamPlayer3D`): doppler shift for moving sources, **occlusion/obstruction** (filter sounds behind walls — low-pass), reverb zones per area.
- **HRTF/binaural** for headphone immersion. Spatial audio is a gameplay cue (footsteps tell you where the enemy is).

## Interactive & adaptive music

Music that responds to gameplay — the craft that separates game audio from linear media:
- **Vertical remixing (layering)** — add/remove stems (drums, strings, tension layer) based on state (combat intensity, health) over the same loop.
- **Horizontal re-sequencing** — switch between musical sections/loops based on state, with musical **transitions** (quantized to the beat/bar) and **stingers** (short musical hits on events).
- **Transitions** must be musical (wait for a bar boundary) to avoid jarring cuts. Middleware (FMOD/Wwise) specializes in this; achievable in [[godot]] with multiple streams + bus automation.

## Mixing & mastering

- **Audio buses** — route sounds into groups (SFX / Music / Voice / UI / Master) for independent volume, effects, and player-facing sliders ([[godot]] bus layout).
- **Ducking / sidechain** — automatically lower music/SFX when dialogue plays (clarity).
- **Loudness/mastering** — consistent perceived loudness (target LUFS), avoid clipping with a limiter on the master, leave headroom.
- **Prioritization/voice limiting** — cap simultaneous voices; steal the quietest/least-important when over budget.

## Procedural & generative audio

Generate or modulate sound at runtime: parameterized SFX (engine pitch by RPM), procedural ambiences, generative/algorithmic music, physical-modeling for impacts. Ties to synthesis above and [[procedural-generation]].

## The engine / middleware view

- **[[godot]]:** `AudioStreamPlayer` (non-positional/UI/music), `AudioStreamPlayer2D`/`3D` (spatial), the **Audio Bus** layout (Audio panel) with per-bus effects, `AudioStreamRandomizer` for variation. Good for most projects.
- **Middleware (FMOD / Wwise)** — industry-standard for large/complex projects: designer-driven adaptive music, event systems, profiling, mixing — integrated via plugins. Reach for it when the engine's audio isn't enough.

## Anti-patterns

- **Repetition fatigue** — the same SFX clip every time (machine-gun effect); fix with pitch/volume randomization & round-robin.
- Treating audio as an **afterthought** — it's half of feel/feedback ([[game-design]]).
- **High latency** (big buffers / firing on the wrong frame) so sounds lag the action.
- **No bus structure** — every sound at master level → no mixing, no player volume controls, no ducking.
- **Jarring music transitions** (cutting mid-bar) instead of quantized/transitional changes.
- **Clipping**/no headroom; no voice-limit (audio chaos + CPU spikes) when many sounds play.
- Aliasing from ignoring **Nyquist** in synthesis; hand-rolling DSP when bus effects/middleware suffice.

## Always-apply

1. Mind the **signal basics** (sample rate, bit depth, Nyquist, buffer latency); keep audio low-latency to the action.
2. **Randomize** repeated SFX (pitch/volume/round-robin) to avoid fatigue; sound is **feedback & feel** — design it in.
3. Build a **bus structure** (SFX/Music/Voice/UI/Master) with effects, ducking, and player volume; master with headroom (no clipping).
4. Use **spatial audio** as a gameplay cue; make music **adaptive** (vertical/horizontal) with musical transitions.
5. Use [[godot]]'s audio system by default; reach for **FMOD/Wwise** for complex adaptive needs.

## Related

- [[godot]] — AudioStreamPlayer(2D/3D), audio buses & effects, randomizer.
- [[game-design]] — audio as feedback and the feel of actions; [[game-graphics]] — audio + visual juice together.
- [[information-theory]] / [[game-math]] — sampling, signals, DSP foundations.
- [[procedural-generation]] — generative/procedural audio.
- Sources: *The Audio Programming Book* (Richard Boulanger & Victor Lazzarini); Godot audio docs; FMOD/Wwise practice.
