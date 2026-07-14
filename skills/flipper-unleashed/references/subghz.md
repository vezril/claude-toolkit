# Unleashed — the Sub-GHz feature set (the defining difference)

Source: DarkFlippers/unleashed-firmware `dev` docs (`SubGHzSettings.md`, `SubGHzSupportedSystems.md`, `SubGHzRemoteProg.md`, `SubGHzRemotePlugin.md`, `SubGHzCounterMode.md`, `LFRFIDRaw.md`) — fetched 2026-07.

> **This is where Unleashed diverges most from stock, and where the legal responsibility is heaviest.** Unleashed removes the stock region-lock and adds save/send for many rolling-code systems the official firmware refuses to. The firmware provides *no* guardrail beyond the CC1101's hardware limits — **which bands and power levels you may legally transmit on is entirely on you, and depends on your jurisdiction. Only operate remotes/receivers you own or are authorized to test.** These notes document the file formats and what the features do; they deliberately do **not** provide walkthroughs for defeating access-control systems you don't own — and the docs' own "don't experiment with equipment you don't have access to" warnings are reproduced below.

## Custom frequencies & hopper (`setting_user`)

File: `subghz/assets/setting_user` on the SD (ships as `.example` — remove the extension to activate).

- Add a main-list frequency: `Frequency: 928000000` (9-digit Hz).
- Add a hopper frequency: `Hopper_frequency: 345000000`.
- `Add_standard_frequencies:` — default `true`; set `false` to use **only** your custom entries (then you must populate both the main and hopper lists yourself).
- Custom entries append after the defaults; the default frequency is the entry the firmware selects on open.

**CC1101 hardware range** (the normal ceiling without DangerousSettings): 300–348, 386–464, 778–928 MHz, plus 350 and 467 MHz. Keep the hopper list short for performance. Default hopper list: `315000000, 390000000, 430500000, 433920000, 434420000, 868350000`. **External CC1101 module** support exists (guide: `github.com/quen0n/flipperzero-ext-cc1101`).

## Supported systems (much larger table than stock)

**Static-code** families include: Ansonic, BETT, CAME 12/24, Chamberlain, Clemsa, Dickert MAHS, Gate TX, Hormann, Mastercode, Megacode, Telcoma/Cardin, Nice Flo, Marantec, Linear/Delta3, Holtek/HT12X, Princeton (PT2262), SMC5326, KeyFinder, plus sensors/smart-home (Intertechno V3, Dooya, Legrand, Honeywell, Magellan) and alarms (Hollarm, GangQi).

**Dynamic / rolling-code** families include: Alutech AT-4N, AN-Motors AT4, Beninca (AES128), BFT Mitto, CAME Atomo/TWEE, Ditec, Nice FloR-S / One, Somfy Keytis/Telis, Security+ 1.0/2.0, Jarolift, Hay21 — plus **KeeLoq** across 60+ manufacturers (DoorHan, FAAC RC/XT, Hormann EcoStar, Sommer, Centurion, Cardin S449, Mhouse, Nice Smilo, and many alarm makers). Support-level notes: iDO is decode-only; Nero Radio is static-mode only. **Unleashed adds full send for many dynamic protocols stock only decodes or ignores.**

## Sub-GHz Remote — Prog (create a new *bound* remote)

Purpose (verbatim): *"many supported systems can be used only from Read mode; Add Manually is used only to make new remotes that can be binded with receiver."* The feature registers a **new remote with the receiver** (like adding a spare factory remote), not a raw clone that would fight the original's counter — the legitimate use is enrolling an additional remote on **your own** gate.

Manual-entry fields (per-protocol Add-Manually forms):
- **FIX** — hex fixed portion; the first digit encodes the button identity.
- **COUNTER / Cnt** — rolling counter value (hex).
- **SEED** — per-button value read from the *original* remote in Read mode; needed to reproduce its rolling sequence.
- **Btn** — button code (from the FIX nibble).
- Reading an existing signal surfaces `Key:` / `Manufacture:` / `Seed:` (protocol-specific frequency & modulation, e.g. FAAC SLH at 868.35/433.92 MHz, AM650).

Documented manual-entry protocols: FAAC SLH (+ "Man." variant), DEA Mio, AN-Motors AT4, Alutech AT4N, Aprimatic, Doorhan, Somfy Telis, BFT Mitto, CAME Atomo, Nice FloR-S. *(File-format level only — the per-receiver binding button sequences are in the upstream doc.)*

## Sub-GHz Remote Plugin (multi-button map)

Builds a D-pad "universal remote" firing saved `.sub` files. Map files are `.txt` in the `subghz_remote/` SD folder:

```
UP: /ext/subghz/Fan1.sub
DOWN: /ext/subghz/Fan2.sub
LEFT: /ext/subghz/Door.sub
RIGHT: /ext/subghz/Garage3.sub
OK: /ext/subghz/Garage3l.sub
ULABEL: Fan ON
DLABEL: Fan OFF
LLABEL: Doorbell
RLABEL: Garage OPEN
OKLABEL: Garage CLOSE
```

Paths can't contain spaces/special chars (hyphens/underscores OK); labels ≤16 chars; multiple maps coexist. A broken config shows *"Config is incorrect. Please configure map."*

## Counter Mode (rolling-code counter control)

Experimental. Controls how the rolling counter increments when replaying a saved dynamic `.sub`, so a remote you've enrolled can **coexist with the original without desync**. Add one line to the `.sub` in `/ext/subghz/`: `CounterMode: X`. Without it, standard +1 increment applies. Per-protocol modes exist for Nice Flor S (0–2), Came Atomo (0–3), Alutech AT-4N (0–2), KeeLoq (0–7), V2 Phoenix (0–2). The doc's **verbatim warning**: *"do not experiment with equipment you don't have access to; if you are not sure what mode works for you and can't reprogram your original remote to the receiver — do not use these modes!!!"*

> **Honest limit (from the FAQ):** you **cannot** meaningfully clone your own car key fob this way — reading a rolling-code car remote causes counter desync/blacklisting, and re-pairing needs dealer tools. Rolling-code counter features are for fixed receivers you can re-enroll (gates, barriers), not vehicles.

## LF RFID raw capture (`LFRFIDRaw`)

For analyzing an unknown 125 kHz card: enable Debug (Settings → System → Debug = ON), then 125 kHz RFID → Extra Actions → **RAW RFID** → name → hold card to the back. Produces two files (one **ASK**, one **PSK**) in the `lfrfid/` SD folder — for analysis and for sharing with developers (GitHub issue + a photo of the card).

## Capturing an unsupported remote (RAW, from the FAQ)

Find the frequency with the **Frequency Analyzer** (hold the remote near the top-left of the Flipper), then **Read RAW** with RSSI Threshold `(----)`, trying modulations AM650 / FM238 / FM476 / FM12K; REC, press each button **5× short then 5× long**, label the files, and submit a GitHub issue with the archive, remote photos, and model info. Analyze pulses at `lab.flipper.net/pulse-plotter`.
