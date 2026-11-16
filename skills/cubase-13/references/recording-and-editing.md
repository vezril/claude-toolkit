# Recording and editing audio

## Before recording

1. **Inputs:** Studio > Audio Connections, Inputs tab. Create a mono or stereo input bus for
   each interface input you use, and pick it as the track's input.
2. **Buffer:** drop to a small buffer for tracking (Studio > Studio Setup > Audio System, then
   the driver panel).
3. **Monitoring:** choose one route and stick to it:
   - **Through Cubase** (the track's monitor button): you hear plug-ins, with the round-trip
     latency.
   - **Direct Monitoring** in the interface's own mixer: zero latency, no Cubase plug-ins.
   - **ASIO Direct Monitoring** (Windows ASIO, if the driver supports it): Cubase's monitor
     button switches the interface's direct path.
4. **Latency from plug-ins:** plug-ins with lookahead add delay to what you hear. The
   **Constrain Delay Compensation** button (Project window toolbar) minimizes that while you
   record or play a VST instrument live. Switch it off again to mix.
5. **Adjust for Record Latency** (Preferences, Record page) makes Cubase take plug-in latencies
   into account when placing recordings. Leave it on unless you know why. **Record Shift** moves
   all recordings by a fixed amount, for interfaces that misreport their latency.

## Record modes and takes

- The transport's record modes decide what a new recording does to what's already there, and
  what a cycle recording does with its passes.
- For audio cycle recording, **Keep History** and **Cycle History + Replace** keep every pass as
  a take. For MIDI, **Stacked** and **Mix-Stacked** do the same. Takes sit on the track with the
  last one active and on top.
- **Retrospective Recording** recovers MIDI you played while Cubase wasn't recording.
- **Punch In/Out** limits recording to the locator range; set the pre-roll for a run-up.

## Lanes and comping

1. Turn on **Show Lanes** for the track; each take gets its own lane.
2. Assemble the best performance with the **Comp tool** (or the Object Selection or Range
   tools): click or drag on the take you want in each section, and it becomes the active one
   there.
3. The comp plays as one performance; the other takes stay underneath, so the comp stays
   editable.
4. When it's final, bounce the selection to a single event if you want to tidy up. The
   originals stay in the Pool.

The same lane and comping operations work on overlapping events you placed by hand.

## Timing: hitpoints and AudioWarp

- **Hitpoints** mark transients. Cubase detects them in the Sample Editor; use them to slice,
  to make a groove quantize map, or to quantize audio to the grid.
- **AudioWarp** stretches audio in time: musical mode (audio follows tempo changes), warp
  markers (fix the timing of individual notes), and AudioWarp quantize (move transients to the
  grid without slicing).
- **Range to hitpoint** commands (new in 13) let the Range Selection tool snap to hitpoints.
- For a whole-project timing reference, use the tempo track. Time Warp edits the tempo to fit
  a free performance.

## Pitch: VariAudio

VariAudio, in the Sample Editor, analyses a monophonic recording (a vocal or a solo instrument)
into note segments. Each segment can be moved in pitch, its drift reduced with Straighten Pitch,
shortened, split or re-timed, and you can set a musical scale for snapping.
It is non-destructive until you apply it. Run it on a clean, single-voice take; polyphonic or
reverb-heavy audio gives poor segments. VariAudio's availability varies by edition: check
Steinberg's comparison chart for Artist and Elements.

## Processing and editing

- **Direct Offline Processing** (Audio > Direct Offline Processing): apply processes and
  plug-ins to events, with each step kept in an editable, removable list. You can bypass a
  process to audition without it (from 13.0.10). Prefer this to destructive processing.
- **Range Selection tool:** select time ranges across tracks to cut, copy, delete or render. In
  13 it also works in the Key and Drum Editors.
- **Fades and crossfades:** event handles for fades; crossfades between overlapping events.
- **Render in Place** (Edit > Render in Place > Render, with settings under Render Settings):
  print tracks or a selection, with or without inserts and sends, to new audio. Use it to commit
  CPU-heavy chains and to make stems.
- **Rename Selected Events** (new in 13) renames several events at once.

## Habits that save sessions

- Save a new version before a big edit (File > Save New Version).
- Keep the project and its audio in one project folder. Use Back up Project to collect stray
  files.
- Disable tracks rather than deleting them; disabled tracks cost no CPU.
