# HellHades / Raid Extractor / Raid Toolkit account-export format

Research date: 2026-11-07. The schema below comes from reading the C# source of the two
public exporter generations, downloaded from GitHub and inspected line by line. Field names
in `code` were copied from `[JsonProperty("...")]` attributes or from the serializer settings,
so they are **verified** unless they are marked *(inferred)*.

Primary source files:
- Gen 1, the legacy standalone exporter: [LukeCroteau/RaidExtractor](https://github.com/LukeCroteau/RaidExtractor). The model is in [`RaidExtractor.Core/AccountDumpClient.cs`](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/AccountDumpClient.cs), the mapping in [`RaidExtractor.Core/Extractor.cs`](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs), the enums in [`RaidExtractor.Core/Native/*.cs`](https://github.com/LukeCroteau/RaidExtractor/tree/master/RaidExtractor.Core/Native), the serializer settings in [`RaidExtractor/Program.cs`](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor/Program.cs), and the static data in [`hero_types.json`](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/hero_types.json) and [`multipliers.json`](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/multipliers.json).
- Gen 2, the RTK-backed exporter: [raid-toolkit/extractor](https://github.com/raid-toolkit/extractor) ([`Program.cs`](https://github.com/raid-toolkit/extractor/blob/main/Program.cs)). The dump model and its mapping live in [raid-toolkit/account-extension](https://github.com/raid-toolkit/account-extension): [`DataModel/GameData/AccountDumpClient.cs`](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/AccountDumpClient.cs), [`Account/API/Extractor.cs`](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs) and [`Account/ModelExtensions.cs`](https://github.com/raid-toolkit/account-extension/blob/main/Account/ModelExtensions.cs).

---

## Q1. What are the tools, who makes them, and are they maintained?

### Takeaway
There are three generations or families of tool. Gen 1 is LukeCroteau's open-source RaidExtractor (2020–2021, archived), which wrote `artifacts.json`. Gen 2 is the same extractor rebuilt on the open-source Raid Toolkit (RTK) SDK, and it writes the same `artifacts.json` shape with `"fileVersion": "1.3"`. The third is HellHades' own closed-source "HellHades Extractor", a desktop app that uploads data straight to the HellHades Optimiser rather than producing a documented local file. The public GitHub activity for RTK and its extractor stopped in early 2024.

### Cited Findings
- The original RaidExtractor is "A tool made to extract information from the windows version of 'Raid: Shadow Legends'". Its README says it supports game v.253 and announces: "RAIDEXTRACTOR IS BEING DEPRECATED... We've worked really hard to integrate RaidExtractor into the Raid Toolkit family", pointing to raid-toolkit/extractor. — [LukeCroteau/RaidExtractor README](https://github.com/LukeCroteau/RaidExtractor)
- The GitHub API reports LukeCroteau/RaidExtractor as `archived: true`, last pushed 2021-11-07. It required .NET Framework 4.8. — [GitHub repo](https://github.com/LukeCroteau/RaidExtractor)
- Gen 1 exits with an error if the game version is unknown. The source calls `StaticDataHandler.Instance.FindDataForRaidVersion(runningVersion)` against hard-coded memory offsets in `datavalues.json`. Users reported the error "Raid has been updated and needs a newer version of RaidExtractor". — [Extractor.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs); [HellHades comment thread](https://hellhades.com/how-to-use-the-artefact-optimizer-for-raid-shadow-legends/comment-page-3/)
- The Gen 2 README says: "This tool has been migrated to use the Raid Toolkit SDK and requires it to be installed first. This allows the application to continue working, even if the game version is updated!" It requires .NET Core 5.0. Its last release was v1.0.9.17823 on 2022-01-17 and its last push was 2023-01-16. — [raid-toolkit/extractor](https://github.com/raid-toolkit/extractor); [releases](https://github.com/raid-toolkit/extractor/releases)
- RTK describes itself as "a set of tools and libraries that allow developers to write tools and scripts for Raid: Shadow Legends without needing to worry about game updates, memory addressing". It "will automatically update itself when the game updates… by dynamically generating a .NET assembly used to read the game objects on the fly", and it uses components based on Il2CppDumper. — [raid-toolkit-sdk README](https://github.com/raid-toolkit/raid-toolkit-sdk)
- The RTK Service "will run in the background on your system and watch for Raid processes… keep scanning and updating your account data, storing it on your computer… available even when the game isn't running". — [raid-toolkit-sdk README](https://github.com/raid-toolkit/raid-toolkit-sdk)
- Latest RTK SDK release: v2.8.22.23238 on 2024-02-10. Latest account-extension release: v2.9.0.6 on 2024-02-01, described as "Moved Account extension to its own repository, updated to work with RTK v3.x.x APIs". — [raid-toolkit-sdk releases](https://github.com/raid-toolkit/raid-toolkit-sdk/releases); [account-extension CHANGES.md](https://github.com/raid-toolkit/account-extension/blob/main/CHANGES.md)
- RTK ships client libraries on NuGet (`Raid.Client`), npm (`@raid-toolkit/webclient`) and PyPI (`raidtoolkit`). Its docs site lists one extension, "Nag me not!". — [raidtoolkit.com](https://raidtoolkit.com/); [raid-toolkit-sdk README](https://github.com/raid-toolkit/raid-toolkit-sdk)
- RTK is "currently not a 'signed application'… you'll have to trust the developer(s) of this tool", and its docs walk users through clicking past browser warnings with "Keep anyway". — [RTK Security Notice source](https://github.com/raid-toolkit/raid-toolkit.github.io/blob/HEAD/pages/installation/security.md)
- The HellHades extractor reads "your Raid account that is open in Plarium Play". It needs Windows 10 or later, or macOS Catalina or later, and "Bluestacks will not work". Its "Upload to Website" button "will extract the information from the game, upload it to your account on the optimiser server and open the optimiser website", and there is a "Live Update" option. — [HellHades Optimizer Troubleshooting Guide](https://hellhades.com/hellhades-optimizer-troubleshooting-guide/)
- HellHades' disclaimer says the "Raid Extractor Tool" was "developed by a third party" and "has no connection with HH Gaming Web Services Ltd, Plarium or Raid: Shadow Legends". — [hellhades.com/disclaimer](https://hellhades.com/disclaimer/)
- Raid Optimiser 3.0 (15 Aug 2023) added Remote Extraction, where the user types their Raid username, password and 2FA code into the HellHades site and "our servers… extract the data from your account". HellHades says "We do not store any login credentials". — [Raid Optimiser 3.0 announcement](https://hellhades.com/?p=40767)
- The 1 Aug 2024 optimiser update added in-game Auto Equipping and Auto Selling. Per a staff reply on that post, these require "the HellHades extractor on Windows and be in your Roster Screen". — [Optimiser update post](https://hellhades.com/optimiser-update-biggest-changes-ever/comment-page-1/)
- Other consumers of the `artifacts.json` export, as listed in the extractor READMEs:
  - Brago: "Basic Raid Gear Observer. Recommends artifacts to sell and enchant"
  - Raid Tools (raidtools.club)
  - Raidtool Calculator: an Excel sheet that generates Clan Boss timings
  - RaidChamps: sort and filter champions, view skills, and share teams with total stats, sets, masteries and auras

  — [raid-toolkit/extractor README](https://github.com/raid-toolkit/extractor)

### Inferences
- **The HellHades extractor is not the same binary as RaidExtractor or RTK.** It is HellHades' own closed app, which uploads to their server. The old January 2021 optimiser workflow consumed RaidExtractor's `artifacts.json`. A skill should therefore target the open `artifacts.json` format (Gen 1 and Gen 2). It should not count on a local file from the current HellHades extractor unless the user supplies one.
- The Troubleshooting Guide says the HellHades optimiser "will not write those builds back". The August 2024 post then added auto-equip and auto-sell. The guide is older and now out of date: the current HellHades extractor does write to the game.
- RTK had no public commits after February 2024, so it may have broken on later game versions. Its self-regenerating reader design was meant to survive minor patches. I found no evidence in either direction for 2025–2026.

### Gaps
- I found no 2025–2026 release notes, changelog or version for the HellHades extractor. Whether it can export a local JSON file, and what schema that file would use, is undocumented in public. This needs a sample file from a user.
- I could not confirm from public sources whether RTK still works with the 2025–2026 game client.
- The "LukeCreed" name in the brief is really **LukeCroteau**. I found no separate project under the name LukeCreed.

---

## Q2. What is the file type, top-level structure and exact schema?

### Takeaway
The export is a single UTF-8 JSON object, pretty-printed by Newtonsoft.Json with camelCase keys. It is named `artifacts.json` by default, or written as a `.zip` that contains `artifacts.json`. The top-level keys are `artifacts[]`, `heroes[]`, `arenaLeague`, `greatHall`, `shards` and `stagePresets`. Gen 2 adds `fileVersion` ("1.3"), `id`, `name`, `lastUpdated` and `factionGuardians`. Champions link to gear through `heroes[].artifacts`, an array of artifact `id`s. Artifacts carry no owner field.

### Cited Findings
- Command-line flags: `--nogui`/`-g`, `-o <path>` and `-t zip|json` (default `json`). With no other parameters the tool "will create an *artifacts.json* file right where the application is run". — [RaidExtractor README](https://github.com/LukeCroteau/RaidExtractor)
- The zip mode writes an entry named `artifacts.json` (`archive.CreateEntry("artifacts.json")`). — [raid-toolkit/extractor Program.cs](https://github.com/raid-toolkit/extractor/blob/main/Program.cs)
- Serializer: `JsonConvert.SerializeObject(dump, Formatting.Indented, SerializerSettings)` with `CamelCaseNamingStrategy { ProcessDictionaryKeys = true, OverrideSpecifiedNames = false }`. Both generations use this. — [Gen 1 Program.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor/Program.cs); [Gen 2 Program.cs](https://github.com/raid-toolkit/extractor/blob/main/Program.cs)
- Gen 2 takes the dump from RTK: `client.AccountApi.GetAccounts()`, then `GetAccountDump(accounts[0].Id)`. Only the **first** account is exported. — [Gen 2 Program.cs](https://github.com/raid-toolkit/extractor/blob/main/Program.cs)

#### Top level (`AccountDump`)

| key | type | Gen 1 | Gen 2 | notes |
|---|---|---|---|---|
| `fileVersion` | string | declared, **never set**, so it is absent from the file | `"1.3"` (default value) | Use it as the version discriminator |
| `id` | string | — | yes | RTK account id |
| `name` | string | — | yes | In-game account or player name |
| `lastUpdated` | string | — | ISO-8601 (`ToString("o")`) | |
| `artifacts` | `Artifact[]` | yes | yes | Gen 1 sorts by `id` |
| `heroes` | `Hero[]` | yes | yes | Gen 2 leaves out deleted heroes |
| `arenaLeague` | string | yes | yes (Classic Arena) | Enum name, e.g. `"GoldIV"` |
| `greatHall` | object: affinity → (stat → int level) | yes | yes | Keys are camelCased |
| `factionGuardians` | object: faction → (rarity → int count) | — | yes | Count of assigned guardian heroes |
| `shards` | object: shardType → `{count, summonData[]}` | yes (with pull data) | yes (`summonData` always empty) | |
| `stagePresets` | object: stageId (string key) → int[] hero ids | yes | yes | The "Last Champions" battle presets |

— [Gen 1 AccountDumpClient.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/AccountDumpClient.cs); [Gen 2 AccountDumpClient.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/AccountDumpClient.cs); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)

#### `artifacts[]` (`Artifact`). The same fields appear in Gen 1 and Gen 2.

| key | type | notes |
|---|---|---|
| `id` | int (required) | Unique artifact instance id |
| `sellPrice` | int | Silver received when sold |
| `price` | int | |
| `level` | int | Enhancement level, 0–16 |
| `isActivated` | bool | |
| `kind` | string | Slot enum name (see Q3) |
| `rank` | string | `"One"`…`"Six"` (stars) |
| `rarity` | string | `"Common"`…`"Legendary"` (Gen 2 can also emit `"Mythical"`, *inferred*, see Q3) |
| `setKind` | string | Internal set enum name, e.g. `"AttackSpeed"` for the Speed set |
| `isSeen` | bool | |
| `failedUpgrades` | int | |
| `primaryBonus` | `ArtifactBonus` | Main stat |
| `secondaryBonuses` | `ArtifactBonus[]` | Substats |
| `requiredFraction` | string, optional | Faction lock for accessories. Omitted when there is none |

#### `ArtifactBonus`

| key | type | notes |
|---|---|---|
| `kind` | string | Stat enum name (`"Health"`, `"Attack"`, `"Defense"`, `"Speed"`, `"Resistance"`, `"Accuracy"`, `"CriticalChance"`, `"CriticalDamage"`, `"CriticalHeal"`) |
| `isAbsolute` | bool | **true = flat, false = percentage** |
| `value` | number | Rolled value (see Q3 for scale) |
| `enhancement` | number | **Glyph bonus**. Gen 2 sets `Enhancement = (float)bonus.GlyphPower`; Gen 1 reads `PowerUpValue` |
| `level` | int | Number of rolls into this substat. 0 on the primary |

#### `heroes[]` (`Hero`)

| key | type | Gen | notes |
|---|---|---|---|
| `id` | int | 1, 2 | Hero **instance** id, which artifacts link to |
| `typeId` | int | 1, 2 | Champion type id. Encodes the champion and its ascension (Q3) |
| `grade` | string | 1, 2 | `"Stars1"`…`"Stars6"` = rank (stars) |
| `level` | int | 1, 2 | |
| `empowerLevel` | int | **2 only** | Empowerment |
| `experience`, `fullExperience` | int | 1, 2 | |
| `locked` | bool | 1, 2 | |
| `inStorage` | bool | 1, 2 | Vault. Gen 2 maps `hero.InVault`; deep vault is not exported |
| `isGuardian` | bool | **2 only** | Assigned as a faction guardian in the Academy |
| `marker` | string | 1, 2 | In-game marker or tag enum name |
| `artifacts` | int[] | 1, 2 | **Ids of equipped artifacts.** Omitted when nothing is equipped |
| `fraction` | string | 1, 2 | Faction enum name (from static data) |
| `rarity`, `role`, `element` | string | 1, 2 | From static data. `element` is the affinity |
| `awakenLevel` | int | 1, 2 | **Ascension stars** = `typeId % 10` (despite the name) |
| `name` | string | 1, 2 | Champion display name (English default) |
| `health`, `attack`, `defense`, `speed`, `resistance`, `accuracy`, `criticalChance`, `criticalDamage`, `criticalHeal` | number | 1, 2 | **Base stats for this rank and level only. No gear, masteries, Great Hall or ascension bonuses** (Q4) |
| `masteries` | int[] | 1, 2 | Mastery ids (see the MasteryKindId table in Q3) |
| `assignedMasteryScrolls`, `unassignedMasteryScrolls`, `totalMasteryScrolls` | object string → int, nullable | **2 only** | Scroll counts by scroll type |
| `skills` | `{id, typeId, level}[]` | 1, 2 | Skill book level per skill |

— [Gen 1 AccountDumpClient.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/AccountDumpClient.cs); [Gen 2 AccountDumpClient.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/AccountDumpClient.cs); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)

- How heroes link to artifacts in Gen 1: the extractor walks the game's `UserArtifactData.ArtifactDataByHeroId` dictionary and sets `hero.Artifacts = arts`, a list of artifact ids. Gen 2 uses `Artifacts = hero.EquippedArtifactIds?.Values.ToArray()`. In the RTK model `EquippedArtifactIds` is `IReadOnlyDictionary<string,int>` keyed by slot, but the export flattens it to values only. — [Gen 1 Extractor.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)
- `ShardInfo` = `{count:int, summonData: ShardSummonInfo[]}`, and `ShardSummonInfo` = `{rarity:string, pullCount:int, lastHeroId:int}`. Gen 2 always writes `SummonData = new()`, which is empty. — same sources

### Inferences
- **Version detection:** `fileVersion` absent means Gen 1. `"1.3"` means Gen 2, which also has `empowerLevel`/`isGuardian`/`id`/`name`. A defensive parser should treat every non-required key as optional, because `NullValueHandling.Ignore` drops null keys.
- To find a gear's owner, build a reverse index from `heroes[].artifacts`. An artifact absent from every hero's list is in the inventory, unequipped.
- The flat `artifacts` array loses the slot key. Recover the slot by looking up each artifact's own `kind`.
- **JSON-level key casing** *(inferred from the Newtonsoft settings)*: dictionary keys come out camelCase, for example `greatHall: {"magic": {"health": 10, "criticalDamage": 5}}`, `shards: {"mystery": {...}, "ancient": {...}}`, and `stagePresets` keys as numeric strings. String **values** such as `kind`/`setKind`/`grade` keep the PascalCase enum names, because the naming strategy does not touch values.

### Gaps
- I found no real sample `artifacts.json` file in a public repo or issue within the time budget. The casing of dictionary keys above follows from the serializer config and has not been observed in a file.
- The rest of the HellHades in-house upload payload is not public.

---

## Q3. How are the enums encoded (sets, slots, stats, rarities, factions, affinities, ranks, type ids, masteries, value scale)?

### Takeaway
All enums are serialized as **C# enum member names (strings)**, never as integers. The exceptions are `typeId`, the skill ids and the mastery ids, which are raw integers. Percentage stats are stored as **fractions** (0.15 = 15%), while flat stats are absolute numbers, with `isAbsolute` telling them apart. A champion's `typeId` = `baseId + ascension`. Since `baseId` is a multiple of 10, `typeId // 10 * 10` gives the champion and `typeId % 10` gives the ascension level.

### Cited Findings
- **Value scale.** Gen 1 computes `Value = (float)Math.Round(bonusValueStruct.Value / (double)uint.MaxValue, 2)`. Gen 2 uses `AsDouble(Fixed num) => Math.Round(num.m_rawValue / (double)uint.MaxValue, 2)`. The game stores a 32.32 fixed-point number, so a 15% roll becomes `0.15` and a flat 250 HP becomes `250.0`. Both are **rounded to 2 decimals**, which collapses small percentages such as 4.6% into 0.05. — [Gen 1 Extractor.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs); [Gen 2 ModelExtensions.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/ModelExtensions.cs)
- **Slot (`kind`) / `ArtifactKindId`**: UnknownArtifact=0, Helmet=1, Chest=2, Gloves=3, Boots=4, Weapon=5, Shield=6, Ring=7, Cloak=8 (= Amulet), Banner=9, UnknownAccessory=10. — [ArtifactKindId.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/ArtifactKindId.cs); [RTK ArtifactKindId.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/Enums/ArtifactKindId.cs)
- **Rank / `ArtifactRankId`**: Unknown=0, One…Six = 1…6. **Rarity / `ArtifactRarityId`**: Unknown=0, Common=1, Uncommon=2, Rare=3, Epic=4, Legendary=5. — [ArtifactRankId.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/ArtifactRankId.cs); [ArtifactRarityId.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/ArtifactRarityId.cs)
- **Stat / `StatKindId`**: Health=1, Attack=2, Defense=3, Speed=4, Resistance=5, Accuracy=6, CriticalChance=7, CriticalDamage=8, CriticalHeal=9. RTK's Node client adds `IgnoreDefense`. — [StatKindId.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/StatKindId.cs); [RTK Enums.ts](https://github.com/raid-toolkit/account-extension/blob/main/Client/Node/src/Types/Enums.ts)
- **Set / `ArtifactSetKindId`**, the Gen 1 table as of 2021, with internal names:
  - 0 None
  - 1 Hp
  - 2 AttackPower
  - 3 Defense
  - 4 AttackSpeed
  - 5 CriticalChance
  - 6 CriticalDamage
  - 7 Accuracy
  - 8 Resistance
  - 9 LifeDrain
  - 10 DamageIncreaseOnHpDecrease
  - 11 SleepChance
  - 12 BlockHealChance
  - 13 FreezeRateOnDamageReceived
  - 14 Stamina
  - 15 Heal
  - 16 BlockDebuff
  - 17 Shield
  - 18 GetExtraTurn
  - 19 IgnoreDefense
  - 20 DecreaseMaxHp
  - 21 StunChance
  - 22 DotRate
  - 23 ProvokeChance
  - 24 Counterattack
  - 25 CounterattackOnCrit
  - 26 AoeDamageDecrease
  - 27 CooldownReductionChance
  - 28 CriticalHealMultiplier
  - 29 AttackPowerAndIgnoreDefense
  - 30 HpAndHeal
  - 31 ShieldAndAttackPower
  - 32 ShieldAndCriticalChance
  - 33 ShieldAndHp
  - 34 ShieldAndSpeed
  - 35 UnkillableAndSpdAndCrDmg
  - 36 BlockReflectDebuffAndHpAndDef
  - 37 HpAndDefence
  - 38 AccuracyAndSpeed
  - 39 CritDmgAndTransformWeekIntoCritHit
  - 40 ResistanceAndBlockDebuff
  - 41 AttackAndCritRate
  - 42 FreezeResistAndRate
  - 43 CritRateAndLifeDrain
  - 44 PassiveShareDamageAndHeal
  - Accessory sets: 1000 IgnoreCooldown, 1001 RemoveDebuff, 1002 ShieldAccessory, 1003 ChangeHitType

  — [ArtifactSetKindId.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/ArtifactSetKindId.cs)
- Gen 2 writes `SetKind = artifact.SetKindId?.ToString()`, taken from the game's own model. RTK also exposes static `ArtifactSetKind {setKindId, artifactCount, name (LocalizedText), statBonuses[], skillBonus, shortDescription, longDescription}` through its StaticData API, and this carries the display names. — [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs); [ArtifactSetKind.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/StaticData/ArtifactSetKind.cs)
- **Faction (`fraction`, `requiredFraction`) / `HeroFraction`**:
  - Unknown=0
  - BannerLords=1
  - HighElves=2
  - SacredOrder=3
  - CovenOfMagi=4
  - OgrynTribes=5
  - LizardMen=6
  - Skinwalkers=7
  - Orcs=8
  - Demonspawn=9
  - UndeadHordes=10
  - DarkElves=11
  - KnightsRevenant=12
  - Barbarians=13
  - NyresanElves=14
  - Samurai=15
  - Dwarves=16

  RTK uses the same list, including the "Fraction" misspelling of Faction. — [HeroFraction.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/HeroFraction.cs); [RTK HeroFaction.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/Enums/HeroFaction.cs)
- **Affinity (`element`) / `Element`**: Magic=1, Force=2, Spirit=3, Void=4. **Hero rarity**: Common=1…Legendary=5, and RTK's Node enum adds `Mythic`. **Grade**: Stars1…Stars6. **Role**: Attack=0, Defense=1, Health=2 (HP role), Support=3, Evolve=4, Xp=5 (food). — [Element.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/Element.cs); [HeroRole.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/HeroRole.cs); [RTK Enums.ts](https://github.com/raid-toolkit/account-extension/blob/main/Client/Node/src/Types/Enums.ts)
- **Arena league**: None=0, BronzeI–IV=1–4, SilverI–IV=11–14, GoldI–IV=21–24, Platinum=30. **ShardType**: Mystery=1, Ancient=3, Sacred=5, Void=6. — [ArenaLeagueId.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/ArenaLeagueId.cs); [ShardType.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Native/ShardType.cs)
- **Mastery ids** (`MasteryKindId`) are six-digit integers 5001xx (Offense tree), 5002xx (Defense) and 5003xx (Support). Examples: 500112 BladeDisciple, 500161 Warmaster, 500163 GiantSlayer, 500164 FlawlessExecution, 500261 IronSkin, 500262 Bulwark, 500344 EvilEye, 500353 Sniper, 500354 MasterHexer, 500361 ElixirofLife, 500364 EagleEye. Full 66-entry table: — [MasteryKindId.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/MasteryKindId.cs)
- **Type-id lookup table.** Gen 1 bundles `hero_types.json`, a list of 4,748 entries with fields `fraction, rarity, role, element, awakeLevel, isAwakeSupported, isAwakable, awakenHeroId, id, baseId, isBaseType, isBoss, isChecked, isLocationOnly, isMaxAwakened, onQuarantine, summonWeight, unAwakenHeroId, health, attack, defense, speed, resistance, accuracy, criticalChance, criticalDamage, criticalHeal, name, avatarName`. Example: `{"id":10,"baseId":10,"name":"Vergis","rarity":"Epic","fraction":"HighElves","element":"Spirit","health":87,"attack":79,"defense":109,"speed":98,...}`. — [hero_types.json](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/hero_types.json)
- I checked the encoding myself: for all 4,748 entries in that file, `id == baseId + awakeLevel`; `baseId % 10 == 0` always holds; `awakeLevel` runs 0–6; there are 332 `isBoss` entries and 684 distinct non-boss base ids (as of late 2021). Gen 2 sets `AwakenLevel = heroType.TypeId % 10`, which confirms it. — [hero_types.json](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/hero_types.json); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)

### Inferences
- **Do not map `setKind` by integer.** The file holds names. Champions and sets released after 2021, such as newer factions, mythical champions and sets past id 44, will appear under internal names that the Gen 1 table lacks. A skill needs an internal-name → display-name map that tolerates unknown values. Some well-known pairs, which are community knowledge and *not verified from source*:
  - `AttackSpeed` = Speed
  - `GetExtraTurn` = Relentless
  - `LifeDrain` = Lifesteal
  - `HpAndHeal` = Immortal
  - `IgnoreDefense` = Cruel
  - `DecreaseMaxHp` = Destroy
  - `ShieldAndSpeed` = Swift Parry? — *verify*
- To tell flat from % stats: `isAbsolute: true` with kind `Health`/`Attack`/`Defense` is flat HP/ATK/DEF. `isAbsolute: false` is HP%/ATK%/DEF%. Speed, Accuracy and Resistance are always flat (`isAbsolute: true`) with integer-like values. CriticalChance/CriticalDamage are % (`isAbsolute: false`, value 0.05 = 5%). The last two points are *inferred from game mechanics*, so check them against a real file.
- A substat's effective value = `value + enhancement`, where `enhancement` is the glyph.
- `hero_types.json` is a late-2021 snapshot. For current champion names, RTK's StaticData API (`HeroType`, with `LocalizedText` names) is the live source. Otherwise the skill needs its own up-to-date typeId → name table. Note that the export already contains `name` for each hero, which covers names in most cases.

### Gaps
- I did not verify the integer values of set ids added after 2021 (for example the set for Mythical-era releases), the post-2021 factions (for example Sylvan Watchers), or whether RTK emits `"Mythical"` or `"Mythic"` as a hero or artifact rarity string. RTK's Node enum says `Mythic`. I also did not verify how the game currently names rarity 6.

---

## Q4. What is included beyond IDs (names, stats, skills, masteries, blessings, empowerment, ascension, resources, Great Hall)?

### Takeaway
Included: names; faction, affinity and role; **base** stats only; skill levels; mastery ids; ascension (via `typeId % 10`); Great Hall levels; shard counts; arena league; and stage presets. Gen 2 adds empowerment, faction-guardian status and mastery-scroll counts. **Not included:** blessings, double ascension (awaken rank), artifact ascension, total or geared stats, silver/gems/energy/books, and Black Market items. RTK's richer internal model has some of these, but the `artifacts.json` dump drops them.

### Cited Findings
- **Hero stats are base stats only.** Gen 1 copies static-type stats and then applies a rank/level multiplier: `hero.Attack = Math.Round(hero.Attack * multiplier.Multiplier)`, `hero.Health = Math.Round(hero.Health * multiplier.Multiplier) * 15`. Gen 2 does the same from `heroType.Forms[0].UnscaledStats` and does **not** use the type's ascension form or the gear. HP is stored internally divided by 15. — [Gen 1 Extractor.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)
- `multipliers.json` has 210 entries `{stars:"StarsN", level, multiplier}`. The last one is `{"stars":"Stars6","level":60,"multiplier":11.0117}`. — [multipliers.json](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/multipliers.json)
- RTK's internal `Hero` model has `rank`, `awakenRank`, `blessing`, `blessingResetUsed`, `inDeepVault`, `equippedArtifactIds` (keyed by slot), `skillLevelsByTypeId` and `deleted`. `ModelExtensions` maps `AwakenRank = hero.DoubleAscendData?.Grade`, `Blessing = hero.DoubleAscendData?.BlessingId`. **None of these are copied into the `AccountDump`.** — [RTK Hero.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/Hero.cs); [ModelExtensions.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/ModelExtensions.cs); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)
- RTK's internal `Artifact` has `ascendLevel` and `ascendBonus` (artifact ascension) plus `revision`. The dump does not copy them. — [RTK Artifact.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/Artifact.cs)
- RTK's `Resources` model has `shards`, `market` (Black Market) and `basic` (`IReadOnlyDictionary<string,double>`, presumably silver, gems and so on). The dump exports only `Shards` as `{count, summonData: []}`. — [RTK Resources.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/Resources.cs); [Gen 2 Extractor.cs](https://github.com/raid-toolkit/account-extension/blob/main/Account/API/Extractor.cs)
- The Great Hall is exported as levels per affinity per stat (`Dictionary<Element, Dictionary<StatKindId,int>>`), read from `UserVillageData.CapitolBonusLevelByStatByElement`. — [Gen 1 Extractor.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs)

### Inferences
- A skill that wants **total stats** has to compute them as: base (from the file) + ascension form delta + artifact main and substats (plus glyphs) + set bonuses + Great Hall + masteries + arena bonus. That needs static tables for set bonuses and Great Hall per-level values, which the file does not carry. The HellHades Optimiser and RaidChamps already do this.
- To recommend books, the skill compares `skills[].level` with each skill's max level. The max level is not in the file and needs static skill data, such as RTK's `SkillType` (it has `skillBonuses` per BREAKING.md v3.0.0).
- Blessings and double ascension are absent from the file. A skill must ask the user for them rather than assume none.

### Gaps
- I have no direct evidence of the exact string keys RTK uses for `Resources.basic` or for the mastery-scroll dictionaries. Those were not inspected.

---

## Q5. What do existing tools do with the export? (Recommendation heuristics)

### Takeaway
The existing tools fall into four groups: gear optimizers (HellHades), sell/enhance triage (Brago), roster browsers and team sharers (RaidChamps, Raid Tools), and speed-tune calculators (the Raidtool Calculator for Clan Boss). HellHades ranks builds by stat priority, by predicted damage or by effective HP, and it costs the gear swaps in silver.

### Cited Findings
- HellHades Optimiser 3.0 produces "recommended builds for champions" and a Team Optimiser. Results are ranked by mode: **Balanced** by stat priorities, **Damage** by predicted damage change, and **Survival** by Effective HP change. Results include a **Silver Swap cost** estimate. Optimisation costs tokens (5 per champion, 15 per team; free users get 75 a week). — [Raid Optimiser 3.0 announcement](https://hellhades.com/?p=40767)
- The August 2024 update added Auto Equipping ("with the click of a button") and Auto Selling of an imported sell list. Account sharing lets helpers build a sell list, but they "can't pull the trigger on your gear and sell it for you". — [Optimiser update post](https://hellhades.com/optimiser-update-biggest-changes-ever/comment-page-1/)
- Brago "Recommends artifacts to sell and enchant". RaidChamps shows champion statuses and skills, and shares teams "including all their total stats, artifacts, completed sets, masteries and leader's aura". The Raidtool Calculator "attempts to generate Clan Boss timings". — [raid-toolkit/extractor README](https://github.com/raid-toolkit/extractor)

### Inferences
Heuristics a skill could derive from the file alone, without memory access:
- **Sell candidates:** low `rank` and `rarity` items with low `level`; items with no speed substat; primaries that do not suit their slot. Use `sellPrice` for the silver value.
- **Enhance candidates:** items at 12+ whose roll count (`level` per substat) went into useful stats. Speed boots, and Speed-set (`AttackSpeed`) pieces with high speed substat values.
- **Investment gaps:**
  - Heroes at 6 stars (`grade == "Stars6"`) with an empty `masteries` list
  - Skills below max level
  - Heroes with no `artifacts` equipped
  - Low `awakenLevel` (ascension) on key champions
  - Great Hall levels below 10 per affinity and stat
  - Unpulled shard counts
- **Champion priorities** still need outside tier and usage data, such as HellHades tier lists, keyed by name or typeId.

### Gaps
- The HellHades "Account Analysis" or progression-recommendation features, raid.gg and raidoptimiser.com were not verified in this pass. I found no primary documentation of any progression-recommendation algorithm.

---

## Q6. What are the risks, ToS position, privacy, and what should a skill do and avoid?

### Takeaway
Both open exporters read game memory: Gen 1 through `OpenProcess(ProcessAccessFlags.Read)` and `ReadProcessMemory`, and Gen 2 through RTK's background service. I found no explicit Plarium statement in 2025–2026 that allows or bans these tools. The only "allowed" claim is a HellHades-authored 2022 paraphrase. The export contains no credentials. A Gen 2 file does contain the account `id` and player `name`. The highest-risk practices belong to the wider ecosystem, not to the file: the HellHades remote extraction asks for game passwords and 2FA codes, and the 2024 HellHades extractor writes to the game (auto-equip and auto-sell).

### Cited Findings
- Gen 1 opens the game process read-only: `NativeWrapper.OpenProcess(ProcessAccessFlags.Read, true, process.Id)`, then many `ReadProcessMemory` calls, finding `GameAssembly.dll` by module name. No `WriteProcessMemory` call exists in Extractor.cs. — [Gen 1 Extractor.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/Extractor.cs)
- RTK describes its goal as building "applications which read from process memory". It is unsigned. — [raid-toolkit-sdk README](https://github.com/raid-toolkit/raid-toolkit-sdk); [RTK Security Notice](https://github.com/raid-toolkit/raid-toolkit.github.io/blob/HEAD/pages/installation/security.md)
- A HellHades guide (January 2022) says Plarium "has stated in the past" that tools such as auto clickers are allowed "as long as they don't provide complete automatic upgrades of accounts". It lists the HellHades Optimiser as okay. This is a secondary, self-interested source, and I found no Plarium primary statement. — [HellHades Raid guide (tips, cheats and strategies)](https://hellhades.com/raid-shadow-legends-guide-tips-cheats-and-strategies/)
- The HellHades disclaimer says HH is not responsible for "any damages or losses to your Raid: Shadow Legends account". It also tells users not to share their login details with anyone, even though the HellHades Remote Extraction itself asks for them. — [hellhades.com/disclaimer](https://hellhades.com/disclaimer/); [Raid Optimiser 3.0](https://hellhades.com/?p=40767)
- Plarium's general Terms of Use are at plarium.com/en/legal/terms-of-use. The in-game rules for other Plarium titles (Vikings, Throne) forbid playing "by means that go beyond the usual game process" and allow bans at Plarium's "sole discretion". I found no Raid-specific clause on extractors. — [Plarium Vikings in-game rules](https://vikingsweb-support.plarium.com/js/en/pages/in-game-rules); [Plarium Throne rules](https://support-portal.plarium.com/en/throne/faq/ingame-rules)
- A HellHades forum reply says the extractor only accesses account data, not the login password. — [HellHades optimiser beta FAQ comments](https://hellhades.com/raid-optimiser-beta-phase-1-faq/comment-page-1/)
- Gen 2 dump fields `id` (RTK account id) and `name` (account name) are set from `accountFacet.Id` / `accountFacet.Name`. `stagePresets` and `shards.summonData[].lastHeroId` contain only in-game ids. Neither model has a token, email or password field. — [Gen 2 AccountDumpClient.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/AccountDumpClient.cs); [Gen 1 AccountDumpClient.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/AccountDumpClient.cs)
- Gen 1's generated `AccountClient` has `_baseUrl = "http://localhost:5000"`. It is an NSwag stub and there is no remote upload endpoint. — [Gen 1 AccountDumpClient.cs](https://github.com/LukeCroteau/RaidExtractor/blob/master/RaidExtractor.Core/AccountDumpClient.cs)

### Inferences
What a skill should do and avoid:
- **Only parse a file the user provides.** It should never tell the user to install or run memory readers, never write to the game, and never automate equipping or selling. If the user asks about tools, say that using them is the user's decision and carries ToS risk, since no current Plarium approval is documented.
- **Never ask for or accept Plarium login credentials or 2FA codes.** That includes the remote-extraction pattern.
- **Treat the file as personal data.** Redact `id`/`name` from any output or logs, and do not upload the file anywhere.
- **Detect the version:** no `fileVersion` means Gen 1; `"1.3"` means Gen 2. A zip means opening the `artifacts.json` entry inside it. Tolerate missing keys and unknown enum strings.
- State plainly that the hero stats are base-only, and that blessings and double ascension are absent, so recommendations do not overstate what the file shows.

### Gaps
- I found no primary Plarium statement from 2023–2026 on RTK, the HellHades extractor or memory readers. I also found no reports of bans tied to these tools. Plarium's current Terms of Use text was not retrieved.
- I did not retrieve RTK's privacy policy page, `pages/information/Privacy.md`, so its contents are unknown.
