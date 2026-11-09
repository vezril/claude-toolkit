# Using plug-ins

## Where plug-ins live

Most installers choose the folder for you. Check here when a host can't find something, or when
an installer asks.

**VST3** (Steinberg's documented locations) `[VERIFIED]`:

| OS | Global (all users) | Per user |
|---|---|---|
| macOS | `/Library/Audio/Plug-Ins/VST3/` (also `/Network/Library/Audio/Plug-Ins/VST3/`) | `~/Library/Audio/Plug-Ins/VST3/` |
| Windows | `C:\Program Files\Common Files\VST3\` (32-bit plug-ins on 64-bit Windows: `C:\Program Files (x86)\Common Files\VST3\`) | `%LOCALAPPDATA%\Programs\Common\VST3\` (documented as mainly for development) |
| Linux | `/usr/lib/vst3/`, `/usr/local/lib/vst3/` (and the `lib64` variants) | `~/.vst3/` |

A host may also look in its own application folder. When the same plug-in (the same processor
UID) is found in two places, the host should use the first one in its search order. So an old
copy in a higher-priority folder can hide a new install.

**VST2** has no standard folder on Windows. Common choices are `C:\Program Files\VSTPlugins\`,
`C:\Program Files\Steinberg\VSTPlugins\` and `C:\Program Files\Common Files\VST2\`. Whichever
folder you use, the host has to be told to scan it. On macOS it's `/Library/Audio/Plug-Ins/VST/`
or `~/Library/Audio/Plug-Ins/VST/`.

**AU:** `/Library/Audio/Plug-Ins/Components/` or `~/Library/Audio/Plug-Ins/Components/`.

**CLAP:** `/Library/Audio/Plug-Ins/CLAP/` and `~/Library/Audio/Plug-Ins/CLAP/` on macOS;
`C:\Program Files\Common Files\CLAP\` and `%LOCALAPPDATA%\Programs\Common\CLAP\` on Windows;
`~/.clap/` and `/usr/lib/clap/` on Linux `[CHECK]` (the CLAP headers).

## Apple Silicon, Rosetta and universal binaries

- A host running natively on an M-series Mac loads only plug-ins with an `arm64` slice. An
  Intel-only (`x86_64`) plug-in needs the host started under Rosetta: in the Finder, select the
  app, press **Cmd-I**, and tick **Open using Rosetta**. That's all or nothing for the session,
  and everything then runs translated.
- To check a plug-in's architectures, point `lipo` at the binary inside the bundle:

  ```bash
  lipo -archs "/Library/Audio/Plug-Ins/VST3/Name.vst3/Contents/MacOS/Name"
  ```

  `x86_64 arm64` means universal; `x86_64` alone means it needs Rosetta.
- **Rosetta is going away.** Apple has said macOS 27 is the last release with general Rosetta
  support, and Steinberg repeats that for Cubase `[CHECK]`. An Intel-only plug-in, or a VST2
  that Cubase loads only under Rosetta, has no future on Apple Silicon. Look for a native VST3,
  AU or CLAP version now.

## Gatekeeper and the quarantine flag (macOS)

An unsigned or un-notarized plug-in downloaded from the internet can be blocked from loading,
with a dialog saying macOS can't check it, or it can just fail silently in the scan.

1. Prefer the vendor's signed installer or a current version.
2. If you trust the source, try to open or scan once, then go to **System Settings → Privacy &
   Security** and choose **Open Anyway**.
3. As a last resort, and only for software from the vendor's own site, clear the quarantine
   flag on that one bundle:

   ```bash
   xattr -dr com.apple.quarantine "/Library/Audio/Plug-Ins/VST3/Name.vst3"
   ```

Never do this for a "cracked" or re-packaged plug-in. Those are a common malware route.

## Scanning, caches and blocklists

Hosts scan plug-ins once and cache the result. A plug-in that crashed or hung during a scan
usually lands on a blocklist and stays hidden until you reactivate it.

- **Cubase:** Studio → VST Plug-in Manager. The Blocklist lists plug-ins it won't load;
  reactivate from there after updating the plug-in. See [[cubase-13]].
- **Logic:** Plug-in Manager, with Reset & Rescan for a failed AU.
- **Reaper, Live, Bitwig, FL Studio:** each has a rescan or clear-cache option in its plug-in
  preferences. Use a full rescan, not an incremental one, after replacing a plug-in.

## Licence managers

Many commercial plug-ins only load after an activation step: iLok License Manager (PACE), Native
Access, Steinberg Activation Manager, Waves Central, Arturia Software Center, and others. A
plug-in that scans fine but loads as a silent or demo instance is usually unlicensed on this
machine. Machine limits and offline activation vary by vendor; check the vendor's page. Never
help get around activation.

## CPU, latency and delay compensation

- **Buffer size is the main latency knob.** One buffer of 256 samples at 48 kHz is about 5.3 ms
  (256 ÷ 48,000). Total round-trip latency adds the input and output buffers plus driver and
  converter latency, so the real figure is larger. Track at a small buffer; mix at a large one.
- **Plug-ins add their own latency** (lookahead limiters, linear-phase EQ, some amp sims,
  oversampling). The host compensates by delaying everything else (plug-in delay compensation,
  PDC). That's fine when mixing and painful when monitoring through the plug-in while recording.
  Bypass high-latency plug-ins while tracking, or use the host's "constrain delay compensation"
  option.
- **One track's chain runs on one core.** A heavy instrument plus a long insert chain on a
  single track can drop out while total CPU looks low. Split the chain, freeze or render the
  track, or raise the buffer.
- **Oversampling and voice count** are the usual CPU multipliers inside a plug-in. Lower them
  while writing; raise them for the final render if the plug-in allows separate render quality.

## Troubleshooting order

When a plug-in doesn't appear or crashes, stop at the first step that fails:

1. **Format:** does this host load this format? (`formats-and-hosts.md`)
2. **Folder:** is the file in a folder the host scans, and is there an old copy elsewhere that
   wins?
3. **Architecture:** on Apple Silicon, does the binary have an `arm64` slice (`lipo -archs`)?
4. **Rescan:** has the host fully rescanned since the install?
5. **Blocklist:** did a crash at scan put it on the host's blocklist?
6. **Gatekeeper:** is macOS blocking an unsigned bundle?
7. **Licence:** is it activated on this machine?
8. **Validate:** run `pluginval` (Tracktion's free cross-format validator) on it, or Steinberg's
   `validator` for VST3. A failure here is the vendor's bug: send them the log.
9. **Update or roll back:** check the vendor's compatibility notes for the host and OS version.
