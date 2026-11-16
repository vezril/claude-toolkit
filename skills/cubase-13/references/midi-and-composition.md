# MIDI and composition

## The editors

| Editor | Use it for |
|---|---|
| **Key Editor** | Piano-roll note editing, the controller lanes (velocity, CC, pitch bend, aftertouch), Note Expression. In 13 it gained the **Range Selection tool** and the **Visibility tab**, which shows several parts or tracks at once and switches between them |
| **Drum Editor** | Drum parts by sound rather than by pitch, with a **drum map**. Also gained the Range tool and the Visibility tab in 13 |
| **Score Editor** | Notation. The complete notation feature set is a Pro feature; Steinberg's dedicated notation program is Dorico |
| **List Editor** | Every event as a row, for exact values and odd events (SysEx, program changes) |
| **In-Place Editor** | Quick note edits inside the Project window track |

**Step input** and **MIDI input** (play notes to enter or change them) were improved in 13: you
can change note lengths as you go and stack voices.

## Drum maps

A drum map gives each pitch a name, a display order, an output note and a quantize value, so
the Drum Editor shows "Kick, Snare, Hat" instead of "C1, D1, F#1". Open it from the Map pop-up
menu in the Drum Editor or the track Inspector (Drum Map Setup). Most drum instruments ship
maps (Groove Agent SE's are built in); for others, build one from the instrument's key chart and
save it.

## Expression Maps (articulations)

Expression Maps switch articulations on orchestral libraries from the notes themselves, instead
of separate tracks or keyswitch notes in the part.

- Open **MIDI > Expression Map Setup** (or from the Expression Map section of the track
  Inspector).
- Each **sound slot** combines articulations and sends an **output mapping**: a keyswitch, a
  program change, a controller value or a MIDI channel change, whatever the library expects.
- Articulations are **Directions** (valid from where they're placed until the next direction,
  e.g. pizzicato) or **Attributes** (valid for single notes, e.g. staccato or an accent).
- Many libraries publish Cubase expression maps; import them rather than building from scratch.

## Note Expression

Per-note controller data (volume, pan, tuning and more) that belongs to one note and moves
with it, edited in the Key Editor. It needs an instrument that supports VST 3 Note Expression
(HALion and HALion Sonic do). Existing MIDI controller data can be converted with MIDI > Note
Expression > Convert to Note Expression.

## Chords

- **Chord track:** chord events for the song's harmony. Other tracks can **follow** it (MIDI
  is re-voiced when you change a chord), and VariAudio audio can follow too.
- **Chord Assistant:** suggests chords for the selected chord event, from simple to complex.
- **Chord Pads** (redesigned in 13, with new presets): play chords from single keys, try
  progressions and voicings, and drag the result to a track.
- 13 also added a chord list alongside the Circle of Fifths in the chord editing tools `[CHECK]`
  (press coverage of the 13.0.0 release).

## MIDI effects and the Logical Editor

- **MIDI effects** (inserts on MIDI and instrument tracks; the UI was overhauled in 13):
  arpeggiators, chorder, quantizer, transformer, the Beat Designer step sequencer and others.
  They change what's sent to the instrument without rewriting the notes. Use MIDI > Merge MIDI
  in Loop to make the result permanent.
- **Logical Editor** (MIDI > Logical Editor > Setup): find-and-change rules over MIDI events
  ("all notes below C2 with velocity under 40 → delete"). The **Project Logical Editor**
  (Project > Project Logical Editor > Setup) does the same over tracks and events in the whole
  project. Save useful rules as presets and give them key commands.
- **Quantize:** the Quantize panel holds grid, swing, iterative strength and groove presets.
  Quantize note lengths and ends separately when needed.

## MIDI Remote (hardware controllers)

**Studio > MIDI Remote Manager.** Cubase 12 and later use MIDI Remote for controllers:

- Many controllers have a ready script and work when detected.
- For anything else, build a surface in the **MIDI Controller Surface Editor** (draw knobs,
  faders and pads, then move each control to learn it), and map it with the **Mapping Assistant**.
- Advanced mapping uses scripts (JavaScript; the MIDI Remote Script Console helps debug them)
  `[CHECK]` (Steinberg's MIDI Remote API docs).
- In 13 you can remove a mapping with a right-click.

The older Generic Remote still exists for legacy setups.

## Instruments and content in 13

HALion Sonic 7, Groove Agent SE (drums), Retrologue and Padshop (synths), the Sampler Track
(with new Spectral AudioWarp modes in 13), and Iconica Sketch (an orchestral library for HALion)
`[CHECK]` (13.0.0 press coverage; bundles differ by edition).
