# The roster file (artifacts.json)

## Which tools write it

| Tool | Writes | Status |
|---|---|---|
| RaidExtractor (LukeCroteau), "Gen 1" | `artifacts.json`, **no `fileVersion` key** | Archived; last push 2021-11 |
| Raid Toolkit extractor, "Gen 2" | `artifacts.json` with `"fileVersion": "1.3"`, or a .zip holding it | Last release Jan 2022; RTK last pushed Feb 2024. May break on new clients |
| HellHades extractor | Uploads to the HellHades optimiser. **No local file documented** | Closed source; writes to the game (auto-equip/sell) since Aug 2024 |

If a player gives you a HellHades file that isn't `artifacts.json`, the parser fails cleanly
because it has no top-level `heroes`/`artifacts` list. Ask for a small sample with the account
id and name removed, or work from a typed roster. Don't guess at its schema.

## Schema `[VERIFIED]` from the extractors' C# source

The file is a single UTF-8 JSON object, written by Newtonsoft with camelCase keys. String enum
values keep their PascalCase C# names.

| Level | Keys |
|---|---|
| Top | `fileVersion` (Gen 2), `id`, `name` (Gen 2, **personal data**), `lastUpdated` (Gen 2), `artifacts[]`, `heroes[]`, `arenaLeague`, `greatHall`, `factionGuardians` (Gen 2), `shards`, `stagePresets` |
| Artifact | `id`, `kind` (slot), `rank` ("One"…"Six"), `rarity`, `setKind`, `level` (0–16), `primaryBonus`, `secondaryBonuses[]`, `requiredFraction` (optional faction lock), `sellPrice`, `price`, `failedUpgrades`, `isActivated`, `isSeen` |
| Bonus | `kind` (stat), `isAbsolute` (true = flat), `value`, `enhancement` (glyph), `level` (rolls into this substat; 0 on the main stat) |
| Hero | `id`, `typeId`, `name`, `grade` ("Stars1"…"Stars6"), `level`, `empowerLevel` (Gen 2), `awakenLevel`, `fraction`, `rarity`, `role`, `element`, `artifacts[]` (equipped ids), `masteries[]`, `skills[]{id,typeId,level}`, `inStorage`, `isGuardian` (Gen 2), `marker`, `locked`, base stats, mastery-scroll maps (Gen 2) |

Gen 2 exports **only the first account** on the machine.

## Encoding rules

1. **Percent stats are fractions.** A value of 0.15 means 15%, and values are rounded to 2
   decimals, so 4.6% reads as 5%. Flat stats are plain numbers. `isAbsolute` tells them apart.
   The parser multiplies percents by 100 and labels HP%/ATK%/DEF% separately from flat. A
   "percent" above 1 is assumed already a percent and flagged.
2. **typeId encodes the champion and its ascension.** `typeId // 10 * 10` is the champion and
   `typeId % 10` is the **ascension** stars. This was checked against all 4,748 entries of the
   bundled `hero_types.json`. Despite its name, the `awakenLevel` field is ascension, not
   Awakening.
3. **Hero stats are base stats only**, scaled for rank and level. Gear, masteries, the Great
   Hall and the ascension form are not included. (One research note said "final stats"; the
   source code says base.)
4. **Ownership is one-way.** Heroes list their artifact ids, and artifacts have no owner field.
   The parser builds the reverse index; anything unlisted is inventory.
5. **Set names are internal and drift.** No public file pairs internal names with in-game
   names, so the parser's table is inferred (high confidence for classic sets, medium for
   Savage/Cruel, Stoneskin, Perception, Frostbite and Bloodthirst). Sets released after January
   2024 (Mercurial, Chronophage, Supersonic, Feral, Zeal, Rebirth, Merciless, Slayer…) appear
   as raw strings with `"mapping": "unmapped"`. Show them raw and ask.
6. **Enum spellings.**
   - Rarity is `Mythical` in C# and `Mythic` in the TypeScript client; the parser normalises
     both to `Mythical`.
   - The amulet slot is `Cloak`.
   - Factions are `fraction` (sic).
   - The parser maps two newer factions by inference: `Samurai` → Shadowkin and
     `NyresanElves` → Sylvan Watchers. It marks them `factionMapping: inferred`.
   - Roles `Evolve` and `Xp` are fodder and food, and the parser leaves them out of champion
     counts.
7. **Mastery ids** are `500<tree><tier><n>`: tree 1 Offense, 2 Defense, 3 Support. Names come
   from Raid Toolkit's `MasteryKindId` enum (MIT).

## What is missing, so ask

- Blessings, Awakening rank (double ascension), artifact ascension, relics.
- Silver, gems, energy, books, potions. Only shard counts are exported.
- Skill max levels: the file holds current book levels per skill `typeId`, so a book gap needs
  the champion page.
- True in-game total stats.
- Content cleared, and the clan's Clan Boss, Hydra and Chimera difficulty.

## Parser output, field by field

**`summary`**

| Field | What it holds |
|---|---|
| `source` | Generation |
| `redacted` | Which account keys were dropped |
| `counts` | Champions, food, rarity and star breakdown, 6★ level 60, artifacts, unequipped |
| `stageSignal` | A roster-only hint; the player's clears decide the real stage |
| `greatHall` | Levels per affinity/stat, and the total |
| `shards` | Count per shard type |
| `unassignedMasteryScrolls` | Gen 2 only |
| `investmentGaps.sixStarLevel60WithoutAllMasteries` | Built champions with fewer than 15 masteries |
| `investmentGaps.ascensionBelowRank` | Level 50+ champions whose ascension is below their rank |
| `investmentGaps.builtWithEmptySlots` | Built champions with empty artifact slots |
| `blindSpots`, `warnings` | Read these aloud when they change a conclusion |

**`heroes`** gives one row per champion: stars, level, ascension, empower, masteries, sets,
empty slots, and approximate SPD/ACC. These rows are the cheap first pass for team building.

**`hero NAME`** returns everything for one champion, including each equipped piece's main stat
and substats with glyph and roll counts. It returns every copy if the player owns duplicates.

`approxStats` is base + gear main stats and substats + glyphs. **It excludes** set bonuses,
masteries, the Great Hall, ascension, blessings and empowerment, so it undercounts. Compare it
with a threshold only as "at least this much". Ask for the in-game number before calling a
threshold met or missed.

**`gear`**

| List | What it holds |
|---|---|
| `topSpeedSubstatPieces` | Pieces ranked by SPD substat, glyph included |
| `speedUpgradeCandidates` | 5★+ pieces below +16 with SPD subs |
| `speedBoots` | Boots with a SPD main stat; unequipped first |
| `sellCandidates` | The 2021 rule set, with a reason per piece |

**`factions`** gives each faction's owned count, "ready" count (5★+ and level 50+, a rough bar)
and whether it can field five.

## Handling

- Run with `python3 -I`, and keep the file outside the repo. Never commit a player's file.
- Don't quote the raw file's top-level `id` or `name`. Hero names are fine.
- Join champions to outside data (Ayumilove pages, HellHades tier list) by `name`. Use the
  parser's `nameKey` for fuzzy matching. Public typeId tables are 2–6 years stale.
