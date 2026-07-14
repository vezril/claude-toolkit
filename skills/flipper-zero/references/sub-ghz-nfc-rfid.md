# Flipper Zero — Sub-GHz, NFC, and 125 kHz RFID

Source: docs.flipper.net/zero `/sub-ghz/*`, `/nfc/*`, `/rfid/*` — fetched 2026-07. These three wireless read/save/emulate subsystems are the core of the device. **Two different radios you must not conflate: 125 kHz RFID (low-frequency) and 13.56 MHz NFC (high-frequency) are separate antennas and separate apps.**

---

## Sub-GHz (300–928 MHz radio remotes)

**CC1101 transceiver + antenna, ~50 m max range.** For gates, barriers, garage doors, radio locks, RF switches, doorbells, smart lights. **Receives** across all three bands (300–348 / 387–464 / 779–928 MHz); **transmits only on the region's civilian-approved ranges** (below).

**App functions:** **Read** (decode against known protocols) · **Read RAW** (record the raw waveform, decoded or not) · **Saved** (emulate/rename) · **Add Manually** (build a virtual remote) · **Frequency Analyzer** (find a remote's frequency — hold the remote near the Flipper and press its button) · **Region Information** · **Radio Settings** (internal vs external antenna).

**Modulations:** **AM650** (default) · AM270 · FM238 · FM476. Change frequency/modulation with Left/Right in the config menu. Default remote frequency is **433.92 MHz**.

**Read vs Read RAW:**
- **Read** — demodulates and decodes against known protocols; if recognized *and static*, you can save and retransmit. Flow: Sub-GHz → Read → press the remote button → OK → Save → name.
- **Read RAW** — records the literal waveform "like a dictaphone," no protocol understanding; use it for unknown protocols or later analysis. Flow: Read RAW → REC → press button → STOP → SAVE. An **RSSI threshold** sets the minimum strength to record.
- **Replay:** Saved → select → SEND (transmits once).

### Static vs dynamic (rolling-code) — the boundary the firmware enforces

The supported-vendors page splits every protocol into two classes:
- **Static / unlocked** — fixed code, same every press. Flipper can **decode, save, and playback**. A captured static remote replays and works.
- **Dynamic / locked** — encrypted rolling code. Flipper can **decode** it, but **"for security reasons, the save function is disabled."** It cannot clone or replay these.

So honestly: a fixed-code gate remote can be captured and replayed; a **rolling-code remote (KeeLoq, Somfy RTS/AES, Security+, etc.) can be received and identified but not saved/replayed** — both because a replayed old code is rejected by the receiver (the counter advanced) *and* because the official firmware blocks the save. (The docs say "static/dynamic"; "rolling code / KeeLoq / AES" are the underlying mechanisms, not the docs' wording.)

### Transmit-allowed frequencies by region

Reception spans all bands; **transmission is limited to the region's civilian ranges**, and transmitting outside them shows *"transmission on this frequency is restricted in your region."*

| Region | Allowed TX ranges (MHz) |
|---|---|
| Europe / Africa / Central Asia | 433.05–434.79, 868.15–868.55 |
| Americas (US/CA/BR/AU/NZ…) | 915.00–928.00, 433.05–434.79 |
| Taiwan | 304.50–321.95, 433.075–434.775, 915.00–927.95 |
| Singapore | 300.00–300.30, 312–316, 433.50–434.79, 444.40–444.80 |
| China | 314–316, 430–432, 433.05–434.79 |
| India / Israel | 433.05–434.79 |
| UAE | 420–440 |
| Philippines | 430–440 |
| Rest of World | 312.00–315.25, 920.50–923.50 |

### Add Manually — virtual remotes

Sub-GHz → Add Manually → pick protocol → name → Save; then put the receiver in pairing mode and SEND. Selectable protocols include **Princeton (433)**, **Nice FLO 12/24bit (433.92)**, **CAME 12/24bit / TWEE (433.92)**, **Linear 300**, **Gate TX (433.92)** — all static — and **Doorhan 315/433**, **Liftmaster 315/390**, **Security+2.0 (310/315/390)** — dynamic.

**Supported vendors:** ~60 static families (Princeton, Nice FLO, CAME 12/24, Chamberlain, Holtek, Hormann HSM, Linear, Marantec, Prastel, Tedsen, Legrand, …) and ~60 dynamic/rolling families (Alutech, AN-Motors, BFT, CAME Atomo, Chamberlain Security+, FAAC SLH, Nice FLOR-S, Somfy Keytis/Telis RTS, Sommer, Starline, Doorhan, …). Static = clonable; dynamic = decode-only.

---

## NFC (13.56 MHz)

**ST25R3916, 13.56 MHz HF antenna** (separate from the 125 kHz LF antenna). Reads UID/SAK/ATQA and stored data, then saves and emulates cards. Menu: **Read · Extract MF Keys · Saved · Extra Actions · Add Manually**. Hold the card to the **back** of the Flipper.

**What it can and can't do (be honest about the crypto):**
- Reads **ISO-14443A** cards (MIFARE Classic/Ultralight/DESFire, NTAG) and the UID of ISO-14443B / bank (EMV) cards. It can display some EMV fields but **cannot clone or emulate a working bank card** — dynamic EMV cryptograms aren't breakable.
- **MIFARE DESFire / SEOS / iCLASS SE** use AES/3DES mutual auth — Flipper reads UID/structure but **cannot recover keys or clone** them.
- Key recovery is limited to **MIFARE Classic's weak Crypto-1**. *(The crypto-limit specifics above are established Flipper behavior, not spelled out on these doc pages.)*

**Read flow:** NFC → Read → hold card to the back → More → Save. For an unknown card or missing keys you get **UID/SAK/ATQA only**; a **full MIFARE Classic read needs every sector key** (32 keys for 1K, 80 for 4K, 10 for Mini). Add keys via Extra Actions → user dictionary.

**mfkey32 (MIFARE Classic key recovery):** recovers Crypto-1 keys from a **reader's** authentication nonces. Emulate the (saved or blank) card at the target reader, tap it repeatedly until **10 nonce pairs** are collected, then compute the keys via the **mobile app (Tools → mfkey32)**, **Flipper Lab (NFC Tools)**, or the **on-device mfkey app** (minutes). Recovered keys go into the user dictionary. *(Separate from `nested`/`hardnested`, which run automatically during a card read and need no reader.)*

**Magic cards** (UID-rewritable "Chinese magic" cards) let you write a cloned UID+data — normally block-0/UID is permanent. Generations: **Gen1a** (Classic 1K), **Gen2** (1K/4K, normal write commands), **Gen4 "Ultimate"** (most Classic/Ultralight/NTAG types; password-auth first). Flow: read+save the original → Apps → NFC → NFC Magic → Check → Write → hold the magic card. (Wipe resets it.)

**Unlock with Password** (MIFARE Ultralight / NTAG page-locked cards): sniff the password by emulating near the reader, **generate** it from UID (supported for Toys-to-Life and Xiaomi air-purifier cards), or enter a known hex password. **Add Manually** builds a virtual card from UID/ATQA/SAK.

---

## 125 kHz RFID (low-frequency)

**Dedicated 125 kHz LF antenna at the back** (part of the dual-band antenna, distinct from NFC). Per the docs: *"unlike NFC cards, LF RFID cards don't usually provide high levels of security"* — which is why cloning LF access fobs is often trivial where NFC isn't. Menu: **Read · Saved · Add Manually · Extra Actions**.

**Read:** 125 kHz RFID → Read → hold card to the back. The Flipper **auto-switches ASK/PSK coding every ~3 s** to detect the protocol (EM4100, HID H10301, Indala, AWID, IoProx, …); some cards take up to ~10 s. If auto-detect fails, force ASK or PSK in Extra Actions. Save via More → Save; emulate from Saved → Emulate.

**Write to T5577 (rewritable blanks):** most stock cards are read-only or protected, so cloning targets a **T5577** blank (card/fob/sticker/microchip form). Saved or Add-Manually cards can be written — all supported LF protocols. Flow: Saved → select → Write → hold the Flipper's back to the T5577. Writing to a read-only card may falsely "succeed" if the data already matches; failures usually mean the T5577 is password-protected or you're writing to a genuine read-only card.

**Add Manually:** pick one of **26 protocols** (EM4100 and /32 /16 variants, HID H10301 / Generic Prox / Ext, Indala, Kantech, AWID, Farpointe, Pyramid, Viking, Jablotron, Paradox, Keri, Gallagher, NexWatch, Securakey, …), enter the ID in **hex**, save.

**Animal microchips:** reads **FDX-B** (15-digit ISO — first 3 digits = ISO-3166 country code, incl. thermo/temperature chips) and **FDX-A** (10-digit, non-ISO). **Read-only scanner** — no write/emulate. Pet chips run at **134.2 kHz** while the antenna is tuned for 125 kHz, so Flipper reads across ~110–140 kHz but at **reduced range** (~10 mm). *(The EM4305 silicon often cited for pet chips is community knowledge, not named in the official docs.)*
