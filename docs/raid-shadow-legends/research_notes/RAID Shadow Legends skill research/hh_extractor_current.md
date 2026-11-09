# Current HellHades Artifact Extractor output, Raid Toolkit enums, and HellHades recommendation heuristics

Research date: 2026-11-07. Budget-limited pass (about 22 tool calls). GitHub data came from the unauthenticated GitHub REST API and raw.githubusercontent.com. Code search needs authentication, so it was not available.

## Q1. Does the current HellHades extractor save or export a local file, and in what shape?

### Takeaway
None of the HellHades documentation I found describes saving the account to a local file (JSON, CSV or zip). Every documented path is "Upload to Website", which goes to the HellHades optimiser server, or "Remote Extraction", which runs on HellHades' servers with your game login. The Optimiser also documents no "export account" or "download data" feature. Treat the HH extractor as a closed pipe into raidoptimiser.hellhades.com. For a local file, the skill should rely on the open `artifacts.json` (RaidExtractor / Raid Toolkit, `fileVersion` "1.3") or on the RTK account-extension API.

### Cited Findings
- HellHades' troubleshooting guide (by Saphyrra, dated 2024-12-17) says the optimiser "works by reading your Raid account that is open in Plarium Play". It also says "when you upload to website from the extractor, this effectively replaces your account info in the optimiser". It mentions no Save-to-file, Export or JSON option. — [HellHades Optimizer Troubleshooting Guide](https://hellhades.com/hellhades-optimizer-troubleshooting-guide/)
- The same guide gives a Mac version (Catalina 10.15.7+, open to every membership tier). Auto-Equip and Auto-Sell are Windows-only. Live updates use a `--pid` launch argument, which the guide says "Upload to Website" does not handle well. — [Troubleshooting Guide](https://hellhades.com/hellhades-optimizer-troubleshooting-guide/)
- Remote Extraction (Optimiser 3.0, 2023-08-15) works like this: you log into the Optimiser, open Manage Account, choose Remote Extraction, and enter your Raid login and 2FA code. The job runs in a queue on HellHades' servers. HellHades says the website "forgets any login details provided" once it finishes. The article mentions no file import or export. — [Introducing Raid Optimiser 3.0](https://hellhades.com/introducting-raid-optimiser-3-0-now-with-mobile-and-remote-support/)
- A Plarium forum thread questions whether remote extraction complies with Plarium's terms, and notes that Plarium does not support it. — [Plarium forum: HH Raid Optimizer – Remote Extraction](https://forum.plarium.com/en/raid-shadow-legends/674_game-discussion/1446860_hh-raid-optimizer---remote-extraction/)
- The 2021 how-to guide tells users to press "upload to the website" after logging in with HellHades credentials. The only file it mentions is the extractor itself, which "will download a zip file". In other words the zip is the installer, not a data export. — [How to use the Artifact Optimizer (2021-01-06)](https://hellhades.com/how-to-use-the-artefact-optimizer-for-raid-shadow-legends/)
- The 2024-08-01 "biggest changes" update covers Auto Equip, Auto Sell (filter, build a sell list, review, import to game), Account Sharing (a share link, and others can draft a sell list but not sell), and saved presets (5 per champion free, 10 premium). It describes no data export. Every in-game action needs "the Extractor open and be on your Roster Screen". — [Optimiser Update – Biggest Changes Ever](https://hellhades.com/optimiser-update-biggest-changes-ever/)
- The open-source RaidExtractor's non-GUI mode writes `artifacts.json` in the working directory. The repository is archived and points users to Raid Toolkit. — [LukeCroteau/RaidExtractor](https://github.com/LukeCroteau/RaidExtractor)
- The current Raid Toolkit account-extension still ships the same `AccountDump` schema, with `FileVersion = "1.3"`. Top-level keys are `fileVersion, id, name, artifacts, heroes, arenaLeague, greatHall, factionGuardians, shards, stagePresets, lastUpdated`. Note that `factionGuardians` and `lastUpdated` are in addition to the keys already known. Fields beyond the known set:
  - Artifact: `id, sellPrice, price, level, isActivated, isSeen, failedUpgrades, requiredFraction`.
  - Hero: `id, level, empowerLevel, experience, fullExperience, locked, inStorage, isGuardian, marker, fraction, rarity, role, element, name`, final stats (`health, accuracy, attack, defense, criticalChance, criticalDamage, criticalHeal, resistance, speed`), and `assignedMasteryScrolls / unassignedMasteryScrolls / totalMasteryScrolls`.
  - Skill: `{id, typeId, level}`.
  - Shards: `{count, summonData[{rarity, pullCount, lastHeroId}]}`.

  Source file: `DataModel/GameData/AccountDumpClient.cs` on `main` at the latest repo commit 66b7bc3399 (2024-02-01). — [raid-toolkit/account-extension AccountDumpClient.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/AccountDumpClient.cs)
- Repository activity in the raid-toolkit org, from the GitHub API:
  - `raid-toolkit-sdk` last pushed 2024-02-10.
  - `account-extension` last pushed 2024-02-13.
  - `extractor` last pushed 2023-01-16.

  None is archived, but none has been pushed in over two and a half years as of this research. — [GitHub API: raid-toolkit org repos](https://api.github.com/orgs/raid-toolkit/repos)

### Inferences
- (Inferred) The HH extractor probably uses its own upload payload. Nothing public documents it, and no sample of an HH export turned up. Do not assume the HH extractor's data matches the `artifacts.json` shape.
- (Inferred) Raid Toolkit has been quiet since early 2024, so a fresh game client may break its extraction. A skill that takes `artifacts.json` should tolerate unknown `setKind` strings and missing fields rather than reject the file.
- (Inferred) The workable local inputs for a skill are, in order: (1) `artifacts.json` from RaidExtractor or Raid Toolkit; (2) a manual or CSV roster the user types up; (3) at most, champion names copied from the HH Optimiser screens. HH offers no machine-readable export to build on.

### Gaps
- I found no public sample or schema of an HH extractor upload, and no confirmation either way of a hidden "save to file" option in the current HH extractor UI. Settling that needs a screenshot or a run of the current installer.
- I could not reach the Optimiser web app (raidoptimiser.hellhades.com) docs or FAQ directly. A fetch of hellhades.com/raid/optimiser/ returned an image.
- I did not search YouTube video descriptions or r/RaidShadowLegends threads. The Reddit query returned no Reddit results.

## Q2. Newest RTK enums: ArtifactSetKind, ArtifactRarity, StatKindId, and in-game names

### Takeaway
Two places define the enums, and they disagree in small ways.

- The C# `DataModel/Enums` defines `ArtifactRarityId` (it includes `Mythical = 6`), `StatKindId` (1 to 9, without IgnoreDefense), `ArtifactKindId` and `ArtifactRankId`.
- The Node client's TypeScript defines a full `ArtifactSetKindId` string enum with 62 values plus `None`, a `StatKindId` that adds `IgnoreDefense`, and a `Rarity` enum that uses `Mythic` rather than `Mythical`.

All of it dates from late January 2024. Newer sets are absent: Mercurial, Chronophage, Supersonic, Feral, Zeal, Rebirth, Merciless, Slayer and others. The C# model types `SetKindId` as a free string, and the RTK static data carries a localized `name` for each set kind. So when data comes from RTK, the in-game name comes from the game at runtime rather than from a hard-coded table.

### Cited Findings
- `DataModel/Enums/ArtifactRarityId.cs`: `Unknown=0, Common=1, Uncommon=2, Rare=3, Epic=4, Legendary=5, Mythical=6`. — [account-extension ArtifactRarityId.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/Enums/ArtifactRarityId.cs)
- `DataModel/Enums/StatKindId.cs`: `Health=1, Attack=2, Defense=3, Speed=4, Resistance=5, Accuracy=6, CriticalChance=7, CriticalDamage=8, CriticalHeal=9`. — [account-extension StatKindId.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/Enums/StatKindId.cs)
- `DataModel/Enums/ArtifactKindId.cs`: `UnknownArtifact=0, Helmet=1, Chest=2, Gloves=3, Boots=4, Weapon=5, Shield=6, Ring=7, Cloak=8, Banner=9, UnknownAccessory=10`. Cloak is the amulet slot and Banner the banner slot. The game calls Weapon/Helmet/Shield the "top row" and Gloves/Chest/Boots the "bottom row" (the row grouping is my addition, not in the file). `ArtifactRankId` runs `One..Six`, which are star ranks. — [account-extension ArtifactKindId.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/Enums/ArtifactKindId.cs)
- `DataModel/StaticData/ArtifactSetKind.cs` has the fields `setKindId: string, artifactCount: int, name: LocalizedText, statBonuses: StatBonus[], skillBonus?: int, shortDescription, longDescription`. Because `artifactCount` is a field, the set size (2, 4 or 9 pieces, say) comes from static data. — [account-extension ArtifactSetKind.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/StaticData/ArtifactSetKind.cs)
- The full set list is `Client/Node/src/Types/Artifacts.ts` → `export enum ArtifactSetKindId`. It was introduced and last touched in commit 647e7e112fad369b8cae1949148c1d9b2f267b9d ("add build and client sdks", 2024-01-31). The values, in file order: `None, Hp, AttackPower, Defense, AttackSpeed, CriticalChance, CriticalDamage, Accuracy, Resistance, LifeDrain, DamageIncreaseOnHpDecrease, SleepChance, BlockHealChance, FreezeRateOnDamageReceived, Stamina, Heal, BlockDebuff, Shield, GetExtraTurn, IgnoreDefense, DecreaseMaxHp, StunChance, DotRate, ProvokeChance, Counterattack, CounterattackOnCrit, AoeDamageDecrease, CooldownReductionChance, CriticalHealMultiplier, AttackPowerAndIgnoreDefense, HpAndHeal, ShieldAndAttackPower, ShieldAndCriticalChance, ShieldAndHp, ShieldAndSpeed, UnkillableAndSpdAndCrDmg, BlockReflectDebuffAndHpAndDef, HpAndDefence, AccuracyAndSpeed, CritDmgAndTransformWeekIntoCritHit, ResistanceAndBlockDebuff, AttackAndCritRate, FreezeResistAndRate, CritRateAndLifeDrain, PassiveShareDamageAndHeal, ResistAndDef, CritRateAndIgnoreDefMultiplier, BuffChanceResHpSpd, StoneSkinHpResDef, CritDamageAndSpeed, SpeedAndIgnoreDefMultiplier, ShieldAndHp2, DefAndAoeDamageReduce, SpeedAndCdReductionChance, CritDmgAndDmgIncreaseOnHpIncrease, IncreaseStaminaAndSpdAndAcc, CritDmgAndIgnoreDefAndCdReductionChance, SpeedAndResistance, IgnoreCooldown, RemoveDebuff, ShieldAccessory, ChangeHitType, CounterattackAccessory`. Note the in-game typos "Week" (for Weak) and "Defence". — [account-extension Artifacts.ts](https://github.com/raid-toolkit/account-extension/blob/main/Client/Node/src/Types/Artifacts.ts)
- `Client/Node/src/Types/Enums.ts` (same commit 647e7e1, 2024-01-31) contains:
  - `Rarity { Common, Uncommon, Rare, Epic, Legendary, Mythic }`
  - `StatKindId { Health, Attack, Defense, Speed, Resistance, Accuracy, CriticalChance, CriticalDamage, CriticalHeal, IgnoreDefense }`
  - `DifficultyId { Normal, Hard, Brutal, Insane, None }`
  - `Affinity`, `Faction` and `HeroRole` enums

  — [account-extension Enums.ts](https://github.com/raid-toolkit/account-extension/blob/main/Client/Node/src/Types/Enums.ts)
- Sources on the newer sets: HellHades has guide pages for the Mercurial set (Grim Forest; its 9-piece bonus grants Total Guard) and the Chronophage set (Event Dungeon; full set +60 RES, +32% SPD, Immutable stacks). Neither name appears in the RTK enum. — [HellHades Mercurial set](https://hellhades.com/mercurial-artifact-set/); [HellHades Chronophage set](https://hellhades.com/chronophage-artifact-set/)

### Inferences
- (Inferred) The mapping from internal names to in-game names below was not verified against a primary source this pass. I found no file that pairs them. Only the runtime `name` LocalizedText carries the official names. My confidence in each group differs:
  - **High confidence (classic sets):** Hp=Life, AttackPower=Offense, Defense=Defense, AttackSpeed=Speed, CriticalChance=Critical Rate (C.RATE), CriticalDamage=Critical Damage, Accuracy=Accuracy, Resistance=Resistance, LifeDrain=Lifesteal, DamageIncreaseOnHpDecrease=Fury, SleepChance=Daze, BlockHealChance=Cursed, FreezeRateOnDamageReceived=Frost, Stamina=Frenzy, Heal=Regeneration, BlockDebuff=Immunity, Shield=Shield, GetExtraTurn=Relentless, IgnoreDefense=Savage, DecreaseMaxHp=Destroy, StunChance=Stun, DotRate=Toxic, ProvokeChance=Taunting, Counterattack=Retaliation, CounterattackOnCrit=Avenging, AoeDamageDecrease=Stalwart, CooldownReductionChance=Reflex, CriticalHealMultiplier=Curing, AttackPowerAndIgnoreDefense=Cruel, HpAndHeal=Immortal, ShieldAndAttackPower=Divine Offense, ShieldAndCriticalChance=Divine Critical Rate, ShieldAndHp=Divine Life, ShieldAndSpeed=Divine Speed.
  - **Medium confidence:** StoneSkinHpResDef=Stoneskin (the name nearly says so), AccuracyAndSpeed=Perception, FreezeResistAndRate=Frostbite, CritRateAndLifeDrain=Bloodthirst.
  - **Unresolved, do not hard-code without verification:** the other hybrid and accessory values (UnkillableAndSpdAndCrDmg, BlockReflectDebuffAndHpAndDef, HpAndDefence, CritDmgAndTransformWeekIntoCritHit, ResistanceAndBlockDebuff, AttackAndCritRate, PassiveShareDamageAndHeal, ResistAndDef, CritRateAndIgnoreDefMultiplier, BuffChanceResHpSpd, CritDamageAndSpeed, SpeedAndIgnoreDefMultiplier, ShieldAndHp2, DefAndAoeDamageReduce, SpeedAndCdReductionChance, CritDmgAndDmgIncreaseOnHpIncrease, IncreaseStaminaAndSpdAndAcc, CritDmgAndIgnoreDefAndCdReductionChance, SpeedAndResistance, IgnoreCooldown, RemoveDebuff, ShieldAccessory, ChangeHitType, CounterattackAccessory).
- (Inferred) Sets released after January 2024 (Mercurial, Chronophage, Supersonic, Feral, Zeal, Rebirth, Merciless, Slayer and so on) will show up in a fresh extraction under new internal strings this enum does not know. The skill should show unknown `setKind` strings as given, and resolve names from the extraction's static data if it is present.
- (Inferred) The rarity name differs across sources: C# says `Mythical`, the TypeScript says `Mythic`, and `artifacts.json` writes the string form. Normalize both to one value.
- (Inferred) A substat `kind` of IgnoreDefense can appear (Node `StatKindId`) even though the C# enum stops at 9. Accept it.

### Gaps
- I found no primary file that maps internal set names to in-game names. Commits in `raid-toolkit-sdk` and `Il2CppDumper` after February 2024 were not checked, but the repos show no pushes since then. Unauthenticated code search was blocked, so I could not run a GitHub-wide search for strings like `Mercurial` or `Chronophage` in a set enum.

## Q3. HellHades recommendation features and documented heuristics

### Takeaway
HellHades publishes only a few explicit heuristics, and its tools encode most of them as user-tuned filters and sliders rather than a stated formula.

- **What exists:** a public champion tier list rated 0 to 5 per content area; a separate damage grade (Weak, Average, Strong, Godlike); premium "Artifact Ratings"; Auto-Sell driven by "advanced filtering"; and a stat-importance slider (0 to 16) for each stat in the gear optimiser.
- **What doesn't:** I found no automated "Account Analysis" tool feature. "Account assessment" is a paid human coaching product.
- **Next-build advice:** "who to build next" lives in articles such as "Who should I 60 next?", not in a tool.

### Cited Findings
- The tier list (page timestamp 2026-05-26) uses a 0 to 5 scale per area. The columns are:
  - **Overall group:** Overall, Demon Lord (Clan Boss), Hydra, Chimera, Amius, Grim Forest, Leshun, Draugnell, Isheth, Maximoz, Tauraze, Mimic, Phrygius.
  - **Dungeons:** Spider, Dragon, Fire Knight, Ice Golem, Iron Twins, Sand Devil, Shogun.
  - **Hard modes:** Spider, Dragon, Fire Knight, Ice Golem.
  - **Other:** Arena, Roles.
  - **Doom Tower bosses:** Kuldath, Agreth, Borgoth, Sorath, Grythion, Iragoth, Bommal, Fae.

  The page says the list helps "get an overall understanding" and that the information "is not set in stone". It does not explain how the Overall score is computed. It shows champions by name only, with no numeric IDs and no API endpoint. — [HellHades Raid Tier List](https://hellhades.com/raid/tier-list/)
- Damage is graded Weak, Average, Strong or Godlike from a ranking sorted strongest to weakest, recalculated with each new batch of champions. — [How Damage is Graded](https://hellhades.com/how-damage-is-graded/) (summarized via search result; page not fetched directly)
- Artifact Ratings are a premium feature, alongside the Skills Tab and Team Suggestion Details. The optimiser offers three build modes: Balanced, Damage and Survivability. — [Troubleshooting Guide](https://hellhades.com/hellhades-optimizer-troubleshooting-guide/)
- Auto-Sell works this way: filter gear with "advanced filtering options", add it to a sell list, review it, then sell in-game. A share link can let others draft a sell list. The filter criteria are not published. — [Optimiser Update – Biggest Changes Ever (2024-08-01)](https://hellhades.com/optimiser-update-biggest-changes-ever/)
- The stat-importance sliders tell the optimiser which substats you want. Importance 16 searches for "godlike" rolls. Rough speed guidance: speed 100 to 200 needs about 1 to 6 importance, 200 to 300 about 7 to 12. — [How to use the Artifact Optimizer](https://hellhades.com/how-to-use-the-artefact-optimizer-for-raid-shadow-legends/) (via search summary)
- Sell rules attributed collectively to "HellHades, MurderInc, and Chosen" (community post by kfishkin, 2021-03-21):
  - Atk% gloves.
  - Epic or legendary pieces with no speed substat.
  - Epic boots without a speed main stat.
  - Crit Damage gloves with no SPD or C.RATE substat.
  - Defensive boots with no speed substat.
  - ATK amulets.
  - Defensive rings without 2 good substats.
  - Defensive rings without defensive substats.
  - Non-legendary rings with 2 bad substats.
  - Anything under 5 stars.
  - Bottom-row pieces with a flat HP, ATK or DEF main stat.

  Refinements from redafcb10 (2021-03-23):
  - Sell top-row rare pieces with a flat substat.
  - Keep Atk% gloves on speed sets that have speed subs.
  - Keep speed-set pieces with speed subs as arena-lead candidates.

  — [RaidExtractor Discussion #42](https://github.com/LukeCroteau/RaidExtractor/discussions/42)
- HellHades sells a £25 account assessment in which a coach points out what is holding you back. The coaches use the Optimiser plus their own game knowledge. Customer reviews mention advice on who to max or 6-star next. — [HellHades Account Takeovers & Coaching](https://accounts.hellhades.com/takeovers/); [product page](https://accounts.hellhades.com/product/raid-shadow-legends-account-takeovers-and-coaching/)
- The HellHades homepage lists a guide titled "Who should I 60 Next?" (per search summary). — [HellHades home](https://hellhades.com/)
- The open-beta post lists a roadmap that includes a team builder/planner and a clan boss team builder. — [Raid Optimiser Tool Now in Open Beta](https://hellhades.com/raid-optimiser-tool-now-in-open-beta/)

### Inferences
- (Inferred) For a "what to work on next" ranking, the closest documented HH-style signals are:
  1. A champion's per-area tier rating (0 to 5), weighted toward the areas the user is stuck in. HH itself says to adjust ratings to your own account and progress.
  2. Whether the champion is already built (level, rank, ascension, masteries, gear).
  3. Gear quality from the sell heuristics above: a speed substat is the dominant criterion; main stats should be percent, not flat; legendary or 6-star preferred.

  HH does not publish its Artifact Ratings or Auto-Sell scoring formulas. A skill must state its own rubric and say it is not HH's.
- (Inferred) The 2021 sell rules predate mythical champions, accessory and hybrid sets, and newer artifact mechanics such as gear ascension. Present them as a starting heuristic only.

### Gaps
- I found no official HH documentation of the Artifact Ratings formula, the "Account Analysis" mentioned in the assignment, or Team Suggestion logic. They may exist inside the logged-in Optimiser or on YouTube, neither of which I could reach this pass.
- I did not fetch the "Who should I 60 next?" article, so I cannot cite its specific criteria.

## Q4. A public mapping from champion typeId to name and ratings

### Takeaway
I found no current public mapping from typeId to name to HH rating. HH's tier list is keyed by champion name only. The community static-data repositories are keyed by name, and their last pushes run from late 2020 to mid-2022. The authoritative typeId-to-name source is the game's own static data, read at runtime through RTK (`StaticDataApi` / `HeroType`) or a tool like zerfl/StaticRaidExtraction. Joining extracted heroes to HH ratings therefore means matching on champion name. RTK's dump carries `name` on each hero, and the skill should normalize names before matching.

### Cited Findings
- The RaidExtractor/RTK `Hero` record includes `typeId` and a `name` string, plus `fraction`, `rarity`, `role` and `element` as string enums. A name-based join to tier lists is therefore possible without a separate ID table. — [AccountDumpClient.cs](https://github.com/raid-toolkit/account-extension/blob/main/DataModel/GameData/AccountDumpClient.cs)
- RTK exposes static data through an API: `Account/API/StaticDataApi.cs`, `DataModel/APIs/IStaticDataApi.cs`, `Client/Node/src/Types/HeroType.ts` and `Client/Python/src/raidtoolkit/StaticDataApi.py`. These files appear in the repository tree; I did not read their contents. — [raid-toolkit/account-extension](https://github.com/raid-toolkit/account-extension)
- zerfl/StaticRaidExtraction injects a DLL into the game to write `hero_types` and `static_data` files. It needs a Visual Studio 2019 build. Last pushed 2021-10-22. — [zerfl/StaticRaidExtraction](https://github.com/zerfl/StaticRaidExtraction); [GitHub API](https://api.github.com/repos/zerfl/StaticRaidExtraction)
- Freshness of the community datasets, from the GitHub API:
  - Goctionni/raid-data: `champion-details/<Name>.json`, keyed by name, last pushed 2020-11-04.
  - PatPat1567/RaidShadowLegendsData: same layout, last pushed 2021-04-11. Its README calls it unmaintained.
  - raidchamps/static-data: credits PatPat1567, Ayumilove, RaidChamps and HellHades, carries a "Keep up to date" todo, last pushed 2022-07-28.

  — [Goctionni/raid-data](https://github.com/Goctionni/raid-data); [PatPat1567/RaidShadowLegendsData](https://github.com/PatPat1567/RaidShadowLegendsData); [raidchamps/static-data](https://github.com/raidchamps/static-data)
- The HH tier list page shows no champion numeric IDs or API/JSON endpoints. — [HellHades Raid Tier List](https://hellhades.com/raid/tier-list/)

### Inferences
- (Inferred) Every public typeId or champion dataset I found is two to six years stale. Champions released since then will be missing. A skill should take the name from the extraction itself (the `name` field) and treat typeId as opaque.
- (Inferred) Ratings have to come from a source the user can check. Options are HH's tier list by name, entered by hand or snapshotted with attribution and a date, or the user's own judgment. Bundling HH ratings into the skill would go stale and may raise reuse and licensing questions.
- (Inferred, from general game knowledge and not verified this pass) In RaidExtractor-era data, typeIds look like base id × 10 + ascension/grade digit. If true, `typeId // 10` would identify the champion. Verify on a real dump before relying on it.

### Gaps
- I did not read RTK's `HeroType.ts` or `StaticDataApi` contents, so the exact static-data field names are unconfirmed.
- I found no HellHades public API, and the tier-list page shows no endpoint. If one exists behind the page's JavaScript or the Optimiser, it is undocumented.
