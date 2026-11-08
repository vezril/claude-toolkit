# Verification ledger

Check this before quoting a number. Researched 2026-11-07, through patch V11.90. "Verified"
still means fan or source-code evidence. Plarium publishes almost nothing, and its support pages
refused automated fetches.

| Number | Label | Source |
|---|---|---|
| Export schema, enum encodings, the typeId rule, percent-as-fraction | `[VERIFIED]` | Extractor C# source (RaidExtractor, Raid Toolkit account-extension) |
| HellHades account data: integer enums for slot, stat, rank, rarity, role, affinity, sets 0–44/1000–1003, factions 1–16 | `[VERIFIED]` against a real file (Nov 2026) | RaidExtractor C# enums; slot × main-stat pairs; faction ids × champion names |
| HellHades faction 17 = Argonites; set ids 60/62/65 | `[UNVERIFIED]`: the faction is inferred; the sets are unknown, shown as `set #N` | Champions filed under 17; the optimiser's `guardians` keys |
| ACC vs RES: ~90% land at parity, ~97% at ACC +30, 3% floor resist | `[VERIFIED]` | HellHades, Buffs/Debuffs/Instant Effects |
| Buff/debuff tier values (Decrease DEF 30/60 etc.) | `[VERIFIED]` | Ayumilove Buffs & Debuffs guide |
| Mastery scroll totals (100 Basic / 600 Advanced / 950 Divine); reset 150 gems after the first | `[VERIFIED]` | Ayumilove Mastery guide |
| Warmaster 60% for 10% max HP (4% bosses); Giant Slayer 30% per hit for 7.5% (3% bosses) | `[VERIFIED]` | Ayumilove, HellHades |
| Clan Boss top-chest thresholds | `[VERIFIED]` (two sources agree) | Ayumilove, DeadwoodJedi |
| Hydra caps and chests; Chimera stat table and chests; Iron Twins bands; Spider rules; Amius stats | `[VERIFIED]` (one current source) | Ayumilove mode guides, Oct 2026 |
| DeadwoodJedi tune speeds | `[VERIFIED as published]`; confirm in the calculator | DeadwoodJedi |
| Live Arena: +9 / −3, 1,320-point top milestone, 10 free fights a day | `[VERIFIED, Mar 2025]` | HellHades |
| Rank level caps, fodder counts, Legendaries start R5, Mythicals R6 | `[VERIFIED]` | HellHades New Player Guide |
| Rarity sets starting substats (Common 0 … Legendary 4, Mythical 4 with one pre-upgraded); rolls at +4/8/12/16 | `[VERIFIED]` | Ayumilove, GamerEmpire |
| Affinity: +15% C.RATE and 30% Strong Hit (+30%); −20% and 35% Weak Hit (−30%, blocks debuffs) | `[CHECK IN-GAME]` | HellHades 2026; older sources differ |
| Clan Boss minimum stats per difficulty | `[CHECK IN-GAME]` (guidance) | Ayumilove |
| How Clan Boss affinity changes (Void at reset, switches below 50% HP?) | `[CHECK IN-GAME]` (sources conflict) | Fandom wiki + HellHades vs DeadwoodJedi per-day advice |
| Great Hall table (L10 = 20% HP/ATK/DEF, 25% C.DMG, 80 RES/ACC; 240 levels total) | `[CHECK IN-GAME]` (2022) | Fandom wiki |
| Glyph ranges; upgrade success odds (77% at 4→5 … 5% at 15→16) | `[CHECK IN-GAME]` (stub page, small samples) | Fandom wiki |
| Mercy thresholds (Ancient/Void Legendary 200, Sacred 12, Primal Legendary 75 / Mythical 200) | `[CHECK IN-GAME]` (fan sources conflict) | Ayumilove Sep 2026 vs BlueStacks |
| Empowerment totals (e.g. Legendary +40% HP/ATK/DEF, +15 SPD) | `[CHECK IN-GAME]` | Ayumilove, own caveat |
| Hydra Normal 215 ACC; Sorath 250 ACC; CvC point values; Gold V threshold (3,200 or 3,500) | `[CHECK IN-GAME]` (stale or low reliability) | HellHades 2021–23, InTeleria |
| Main-stat value of DEF% boots: 4%→30% at 3★, 6%→40% at 4★ | `[CHECK IN-GAME]` (only data point, 2022) | GamerEmpire |
| DEF mitigation approximation 1 − 0.85 × (1 − e^(−2·DEF/3000)) | `[UNVERIFIED]` community fit | HellHades comment snippet |
| 5★/6★ main stats at +16; substat roll ranges; Mythical start values | `[UNVERIFIED]` — never state | None found |
| "SPD × 0.07 per tick" turn-meter fill | `[UNVERIFIED]` — never state | None found |
| Classic Arena tier thresholds, weekly rewards, tier stat bonuses | `[UNVERIFIED]` — never state | None found |
| Mastery cost per tier; Hard dungeon stage count; faction difficulty ranking | `[UNVERIFIED]` — never state | None found |

## Things that go stale fastest

- **Champion ratings and PvP meta.** PvP advice from before 2025 is history: Mercurial reshaped
  Live Arena in early 2026, and V11.75 let Provoke bypass Total Guard.
- **Hydra damage plans.** Shield-scaling teams have been nerfed twice (Corpulent Cadaver,
  Yannica). The Titus Blackplume team is current as of September 2025.
- **The extractor itself.** No Raid Toolkit repository has been pushed since February 2024, so
  extraction may break on new clients, and newer sets arrive as unmapped names.

When a player's in-game screen disagrees with this table, the screen wins. Say so, and suggest
they note the corrected number.
