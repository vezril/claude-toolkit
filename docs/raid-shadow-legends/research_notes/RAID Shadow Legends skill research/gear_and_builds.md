# RAID: Shadow Legends — Gear System (Artifacts & Accessories) and Build Construction

Research date: 2026-11-07. Sources fetched in this session are cited inline. Many fan pages (fandom wiki, Plarium support centre) returned 402/403 to the fetcher, so exact numeric stat tables could not be verified this session; those are flagged in Gaps, and the values commonly quoted there come from prior knowledge and are marked as unverified.

## 1. Slots, main stats, rank/rarity, upgrade mechanics and main-stat values

### Takeaway
Six artifacts (Weapon, Helmet, Shield, Gloves/Gauntlets, Chestplate, Boots) plus three accessories (Ring, Amulet, Banner). Weapon, Helmet and Shield have fixed flat main stats (ATK / HP / DEF). Gloves, Chest and Boots vary, and they are where a build gets its key stat: C.RATE/C.DMG on gloves, ACC/RES on chest, SPD on boots. Rank (stars) sets how big the stats are. Rarity sets how many substats a piece starts with. Every 4 levels (4/8/12/16) a substat is added or upgraded.

### Cited Findings
- Main stat by slot: Weapon = ATK (flat); Helmet = HP (flat); Shield = DEF (flat); Gauntlets = HP, HP%, ATK, ATK%, DEF, DEF%, C.RATE, C.DMG; Chestplate = HP, HP%, ATK, ATK%, DEF, DEF%, ACC, RES; Boots = HP, HP%, ATK, ATK%, DEF, DEF%, SPD; Ring = HP, ATK, DEF (flat); Amulet = HP, ATK, DEF, C.DMG; Banner = HP, ATK, DEF, ACC, RES — [Ayumilove Artifact & Accessory Guide, updated 2026-09-13](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- Weapon, Helmet and Shield always have flat primary stats. Gauntlets, Chestplate and Boots can roll flat or % primaries — [BlueStacks gearing guide](https://www.bluestacks.com/blog/game-guides/raid-shadow-legends/rsl-optimizing-gear-en.html) / [Gamer Empire](https://gamerempire.net/raid-shadow-legends-artifacts-guide/)
- Boots are the only artifact that can have SPD as a primary stat — [search summary of Gamer Empire / HellHades](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)
- Comment-level rules on the Ayumilove guide: C.RATE/C.DMG primaries appear only on gloves (among the six artifacts; the amulet can also carry C.DMG). A ring cannot carry a flat substat that matches its flat primary. Shields can have flat HP substats and helmets flat DEF substats — [Ayumilove guide comments](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- Starting substats by rarity: Common 0, Uncommon 1, Rare 2, Epic 3, Legendary 4. Mythical also starts with 4, with one substat already pre-upgraded (Ayumilove comments say the pre-upgraded substat shows highlighted in red) — [Plarium support (via search summary)](https://raid-support.plarium.com/hc/en-us/articles/360014657140-Basic-Guide-Gear-Overview); [Ayumilove](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- Max artifact level is 16. At levels 4, 8, 12 and 16 an artifact gains a new substat, or upgrades an existing one if it already has 4. Upgrading costs Silver and raises the primary stat on every level — [Gamer Empire](https://gamerempire.net/raid-shadow-legends-artifacts-guide/); [RaidWiki, 2026-10-23](https://raidwiki.com/news/raid-shadow-legends-artifacts-guide/)
- Rank (stars) is innate and never changes. It sets both the base (level 0) and the maximum (level 16) of the main stat. Worked example: 3★ boots with DEF% go from 4% at +0 to 30% at +16, and 4★ boots go from 6% to 40% — [Gamer Empire](https://gamerempire.net/raid-shadow-legends-artifacts-guide/)
- A reader comment on Ayumilove says 6★ C.DMG gloves give 80% C.DMG at +16 — [Ayumilove comments](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/) (user comment, not official)
- **Gear Ascension** (added Dec 2022): a piece can be ascended up to its rank (a 4★ piece up to 4 times). Ascension uses Oils/Extracts, not Silver. The first ascension adds a bonus "Ascension stat" and each later level raises it — [HellHades Artifact & Accessory Ascension guide, 2024-08-14](https://hellhades.com/artifact-and-accessory-ascension-guide/); [HellHades Do's and Don'ts, 2022-12-09](https://hellhades.com/the-dos-and-donts-of-artifact-ascension-raid-shadow-legends/); [Plarium support: Gear Ascension](https://raid-support.plarium.com/hc/en-us/articles/6918467444380-Guide-Gear-Ascension)
- 2025 V10.50 (2025-06-05) added the Oil & Extract Mixer, which merges low-tier ascension resources into higher tiers. V11.50 (2026-05-06) extended it to convert Superior Oils/Extracts — [Ayumilove 2025 patch notes](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [Ayumilove 2026 patch notes](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- QoL timeline: V10.60.5 (2025-08-21) made gear removal free (no Silver). V10.60 (2025-08-06) added a substat-upgrade filter. V11.00 (2025-12-10) raised artifact/accessory storage to 2000 each, and V11.70 (2026-08-05) raised it to 2200. V10.40 (2025-04-02) added Artifact Quick Craft (multi-craft a set with auto-sell). V10.55 (2025-07-03) and V11.80 (2026-10-08) reworked artifact chests toward higher rank/rarity — [Ayumilove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [Ayumilove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- **Anomalous Accessories** (V11.70, 2026-08-05) replace the usual flat HP/ATK/DEF substats with unique bonuses — [Ayumilove 2026 patch notes](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)

### Inferences
- For a recommender, the build-defining "variable slot" choices are Gloves (C.RATE / C.DMG / ATK% / HP% / DEF%), Chest (ATK% / HP% / DEF% / ACC / RES), Boots (SPD almost always), Amulet (C.DMG for nukers, otherwise matching flat stat) and Banner (ACC for debuffers, RES for defensive picks, flat stat otherwise).
- Since a 6★ main stat is about 25% larger than a 4★'s (the 30% to 40% DEF% scale from 3★ to 4★ suggests roughly +10 percentage points per rank for % stats), rank matters most on the three variable slots and boots.

### Gaps
- **Exact +16 main-stat tables for 5★ and 6★ could not be verified.** The Plarium support centre and fandom wiki blocked the fetcher, and fan pages omit the tables. The values widely quoted in the community, from prior knowledge and unverified this session, are below. Treat them as approximate and confirm in game:
  - 6★ +16: ATK 265 / HP 4,020 / DEF 265 (flat main stats); ATK%/HP%/DEF% 60%; C.RATE 60%; C.DMG 80% (matches the Ayumilove comment above); SPD 45; ACC 96; RES 96.
  - 5★ +16: ATK 225 / HP ~3,480 / DEF 225; % stats 50%; C.RATE 50%; C.DMG 65%; SPD 40; ACC 78; RES 78.
- The Ayumilove page that seemed to give 5★ to 6★ base values (300 to 400 ATK, etc.) is about a different game (Awaken Chaos Era) and must NOT be used — [ayumilove.net/?p=70426](https://ayumilove.net/?p=70426).
- Which stat is chosen for the Ascension bonus, and its magnitudes, were not extracted.

## 2. Substats, rolls, glyphs and upgrade rules of thumb

### Takeaway
Substat roll sizes scale with rank, not rarity. Rarity only decides how many substats start revealed, and so how many of the 4 upgrade rolls land on existing stats. Glyphs (Enchanting) add a random value within the glyph's rank range to one substat. Glyphs do not stack: a higher roll replaces a lower one. The consensus on levelling is to check rolls at +8/+12 and sell anything that isn't rolling into useful stats. Speed substats are the main thing that keeps a piece.

### Cited Findings
- Uncommon-or-better artifacts reaching a level where a Common would reveal a new substat instead boost one of their existing revealed substats — [search summary, Gamer Empire](https://gamerempire.net/raid-shadow-legends-artifacts-guide/)
- Rank affects the value of both the primary stat and the substats. Higher rank means larger stats — [Plarium support (via search summary)](https://raid-support.plarium.com/hc/en-us/articles/360014657140-Basic-Guide-Gear-Overview)
- Glyphs: each glyph improves one substat. Higher-rank glyphs have higher value ranges. Every value in a glyph's range has equal probability. Re-enchanting does not add values together but replaces a smaller value with a larger one. Rank 6 artifacts show coloured "MAX!" indicators for the highest value a Rank 6 glyph of each rarity can reach. Higher-rank glyphs can still raise an already-"maxed" substat if their range allows — [Plarium support: Glyphs (via search summary)](https://raid-support.plarium.com/hc/en-us/articles/360014708619-Glyphs)
- Ayumilove reader reply: glyphs do not stack, each stat is overwritten by a higher value up to a cap set by glyph rank — [Ayumilove](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- Fandom wiki snippet: Speed glyphs can raise a SPD substat by about +1 to +16 across all glyph ranks/rarities (the snippet text also contains a "DEF" typo, so treat it with care) — [RAID fandom: Enchanting Artifacts](https://raidshadowlegends.fandom.com/wiki/Enchanting_Artifacts)
- Shadowlegends.wiki describes glyphs as "nine types, six ranks" — [shadowlegends.wiki, 2026-10-19](https://shadowlegends.wiki/artifacts.html)
- HellHades levelling rule of thumb: roll Rare gear to +8; if it rolled well, take it to +12 looking for the next stat. There should be no flat-stat rolls, or at most one, by then. As a starting point, one 4 is OK, but two or more is not good enough — [HellHades (search snippet)](https://hellhades.com/?p=25622)
- HellHades on Speed: an item with one SPD roll might be useful; one with three or four SPD rolls can be account-defining — [HellHades: How Speed Works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)
- Chaos Ore (HellHades): use it only on items that already have 3–4 rolls into a substat. It can change substat and main-stat values — [HellHades Chaos Ore guide](https://hellhades.com/?p=23905)
- Mythical gear: Ayumilove comments say Mythical rank items come from high Hydra difficulty (one claim says level 45 Hydra; unverified) — [Ayumilove comments](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- RaidWiki general advice (2026): prioritise useful stats over set names, compare substats before upgrading, and don't sink heavy Silver into every new drop — [RaidWiki](https://raidwiki.com/news/raid-shadow-legends-artifacts-guide/)

### Inferences
- A practical "level or sell" heuristic a skill can apply:
  1. Keep 6★ and 5★ Legendary/Epic pieces with SPD in the substats, or with the right % primary on a variable slot.
  2. Level to +4/+8. Sell if rolls went to flat stats (flat ATK/HP/DEF) or off-role stats.
  3. Take pieces to +12 when two or more rolls have landed in useful stats. Take them to +16 when the main stat matters (variable slots, boots, accessories with ACC/C.DMG) or when the piece is for an end-game champion.
  4. Use glyphs on SPD first. Use Chaos Ore only on 3–4-roll pieces.
  This matches the HellHades guidance cited above.
- Because a Legendary has its 4 substats revealed at +0, every one of its +4/8/12/16 rolls is an upgrade to an existing stat. That makes Legendaries the highest-variance pieces and the best candidates for "SPD substat or sell".

### Gaps
- **Per-rank substat roll ranges were not found in a fetchable primary source.** Commonly quoted values, from prior knowledge and unverified: 6★ SPD substat ~4–6 per roll and 5★ ~3–5; 6★ % stats ~5–6% per roll; 6★ C.RATE ~4–6%; 6★ C.DMG ~4–7%; ACC/RES ~8–10 at 6★. Verify before quoting.
- **Exact glyph range tables per glyph rank and rarity** (e.g. Legendary 6★ SPD glyph max) were not retrieved: the fandom page returned 402 and the Plarium support page 403.
- The 2025-08 "Gear Filter can now filter by Substat upgrades" (V10.60) suggests the game tracks roll counts per substat, but how the UI shows them was not confirmed.

## 3. Complete artifact and accessory set list, bonuses and farm locations

### Takeaway
There are about 60 artifact sets (Ayumilove lists every one with tier and source; HellHades ranks "over 50 artifact sets and 5 accessory sets") plus 5 classic accessory sets. They fall into: 2-piece stat sets, 4-piece proc sets, forge-crafted sets, Clan Boss / Arena reward sets, and the newer **variable sets** (1–9 pieces counting both artifacts and accessories). Variable sets dominate the top tiers. 2025–2026 additions and reworks: Mercurial (new, Dec 2025), Chronophage rebalance (Sep 2025), and Swift Parry/Deflection reworked into variable sets (Mar 2026).

### Cited Findings
Primary source for every row below: [Ayumilove Artifact & Accessory Guide (updated 2026-09-13)](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/). Bonuses are paraphrased. "Tier" is Ayumilove's tier (SS > S > A > B > C > F).

**Basic 2-piece stat sets**
| Set | Bonus | Source | Ayumilove tier |
|---|---|---|---|
| Life | +15% HP | Ice Golem's Peak; Campaign 1 (Kaerok Castle) | F |
| Offense | +15% ATK | Ice Golem; C2 Sewers of Arnoc | F |
| Defense | +15% DEF | Ice Golem; C3 Catacombs of Narbuk | C |
| Critical Rate | +12% C.RATE | Ice Golem; C4 Durham Forest | C |
| Accuracy | +40 ACC | Dragon's Lair; C5 Felwin's Gate | A |
| Speed | +12% SPD | Dragon; C6 Palace of Aravia | S |
| Resistance | +40 RES | Ice Golem; C7 Tilshire | B |
| Critical Damage | +20% C.DMG | Fire Knight's Castle | B |
| Retaliation | 15% counterattack chance when hit (stacks) | Ice Golem; C10 Godfrey's Crossing | S |

**Classic 4-piece proc sets (dungeons/campaign)**
| Set | Bonus | Source | Tier |
|---|---|---|---|
| Lifesteal | heal 30% of damage dealt | Dragon; C8 Valdemar Strait | B |
| Destroy | reduce target MAX HP by 40% of damage dealt (cap 8% per skill, 40% of original max HP overall) | Dragon; C9 The Deadlands | C |
| Fury | damage bonus as HP falls (+10/+25/+50%) | Fire Knight; C11 Hallowed Halls | B |
| Curing | +20% healing done; also restores destroyed HP equal to the bonus heal | Fire Knight; C12 Brimstone Path | B |
| Reflex | 40% chance to cut a random skill cooldown by 1 | Ice Golem | S |
| Cursed | 50% chance to place a 2-turn Hex on attack | Ice Golem | A |
| Toxic | 75% chance of a 2.5% Poison for 2 turns on attack | Dragon | A |
| Frost | 20% chance to Freeze an attacker for 1 turn | Dragon | C |
| Daze | 25% chance of a 1-turn Sleep on attack | (not stated; classically Dragon) | F |
| Immunity | Block Debuffs for 2 turns at each round start | Fire Knight | B |
| Avenging | 45% counterattack chance when debuffed | Dragon | C |
| Shield | all allies get a Shield of 30% of the wearer's max HP for 3 turns each round | Fire Knight | A |
| Stalwart | -30% AoE damage taken | Dragon | A |
| Frenzy | +5% Turn Meter per debuff received | Fire Knight | F |
| Regeneration | heal 15% max HP at turn start | Fire Knight | S |
| Stun | 18% chance of a 1-turn Stun on attack | Fire Knight | A |
| Savage | ignore 25% DEF | Fire Knight | S |
| Taunting | 30% chance of a 1-turn Provoke on attack | Ice Golem | A |
| Relentless | 18% extra-turn chance (chance falls 45% per consecutive extra turn) | Tournament rewards (top placements, e.g. Champion Chase) | A |

**Clan Boss / Arena reward sets (2-piece)**
| Set | Bonus | Source | Tier |
|---|---|---|---|
| Cruel | +15% ATK, ignore 5% DEF | Clan Boss daily chests | S |
| Immortal | +15% HP, heal 3% HP per turn (stacks) | Clan Boss daily chests | A |
| Divine Life / Offense / Critical Rate / Speed | +15% HP / +15% ATK / +12% C.RATE / +12% SPD, each plus a 15% self-Shield for 3 turns (stacking two Divine sets gives no extra shield, per a commenter) | Classic Arena weekly rewards | B / C / C / S |

**Forge-crafted sets** (forge materials come from Doom Tower bosses, Faction Wars, Arena and events)
| Set | Pieces | Bonus | Forge source | Tier |
|---|---|---|---|---|
| Resilience | 2 | +10% HP, +10% DEF | Faction Wars | A |
| Perception | 2 | +40 ACC, +5% SPD | Faction Wars | S |
| Fatal | 2 | +15% ATK, +5% C.RATE | Kuldath the Magma Dragon (DT) | A |
| Untouchable | 4 | Block Debuffs 2 turns, +40 RES | Borgoth the Scarab King (DT) | A |
| Affinitybreaker | 4 | +30% C.DMG, 50% chance to turn weak hits into crits | Agreth the Nether Spider (DT) | C |
| Frostbite | 2 | 15% chance to block Freeze, 10% chance to Freeze attackers | Sorath the Frost Spider (DT) | C |
| Guardian | 4 | absorbs 10% of allies' incoming damage, heals 10% per turn | Grythion (DT) | S |
| Bloodthirst | 4 | +12% C.RATE, heal 30% of damage dealt | Iragoth (DT) | B |
| Lethal | 4 | +25% ignore DEF, +10% C.RATE | Astranyx (DT) | S |
| Fortitude | 2 | +10% DEF, +40 RES | Bommal (DT) | A |
| Bolster | 4 | 30% ally Shield for 3 turns, wearer heals 10% per turn | Forge Pass | S |
| Defiant | 2 | +10% DEF, -15% AoE damage | Forge Pass | S |
| Killstroke | 2 | +20% C.DMG, +5% SPD | Clan Shop; Forge Pass | A |
| Righteous | 2 | +10% SPD, +40 RES | Forge Pass; "Call of the Arbiter" | A |
| Instinct | 4 | +12% SPD, ignore 20% DEF (one commenter said 15%; ~Apr 2022) | Forge Pass | B |

**Live Arena 2-piece sets** (reworked to 2-piece in Patch 8.40, 2024-04-04)
| Set | Bonus | Source | Tier |
|---|---|---|---|
| Impulse | +12% SPD, 12% chance to cut a random skill cooldown by 1 | Live Arena chests | S |
| Zeal | +20% C.DMG, damage bonus scaling with the wearer's HP | Live Arena chests | S |

**Variable sets (1–9 pieces; artifacts and accessories both count)**
| Set | Theme / key bonuses | Source | Tier |
|---|---|---|---|
| Stoneskin | Stone Skin buff, RES, HP, DEF (the page's per-piece values conflict internally) | Hydra Clan Boss chests | SS |
| Protection | RES, HP, SPD; chance to place Protected buffs | Hydra chests | A |
| Supersonic | SPD, RES, HP, Turn Meter effects | Cursed City | SS |
| Merciless | ATK, C.DMG, SPD, 35% ignore DEF, cooldown-reduction and Extra Turn chances | Cursed City | SS |
| Slayer | C.RATE/C.DMG, SPD, AoE-focused effects | Forge Pass | S |
| Feral | ACC, SPD, Block Debuffs at 4 pieces, ally damage boost (added to the guide 2024-08-10) | Siege | SS |
| Pinpoint | ACC, SPD, Intercept stacks each round | Event dungeon | SS |
| Stonecleaver | ATK, C.DMG, SPD, ignore DEF, bonus damage vs Stoneskin | Live Arena seasonal league | SS |
| Rebirth | SPD, RES; HP/Turn Meter/cooldown effects for revived allies | Live Arena seasonal league | S |
| Chronophage | RES, SPD, "Immutable" stacks that block cooldown increases | Event dungeon | A |
| Mercurial | RES, HP, SPD, Total Guard stacks | Grim Forest | SS (the Ayumilove tier-list anchor for it points at Merciless, an apparent page error) |
| Swift Parry | SPD, C.DMG, HP, Unkillable chance, 50% ignore DEF at 9 pieces | Live Arena weekly rewards; Forge | B |
| Deflection | ACC, SPD, deflect debuffs onto the attacker, Block Debuffs each round | Live Arena weekly rewards; Forge | B |

**Dated set additions and reworks (2023–2026)**
- 2023-06-15 (Patch 7.21): Retaliation, Fury, Curing, Cursed, Avenging and Frenzy reworked — [Ayumilove](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- 2024-04-04 (Patch 8.40): Impulse and Zeal became 2-piece sets — [Ayumilove](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- 2024-08-10: Feral set added to the guide — [Ayumilove](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- 2025-09-04 (V10.70.2): Chronophage rebalanced to 1pc +20 RES; 2pc +10% SPD; 3pc +20 RES; 4pc 1 Immutable stack; 5pc +10% SPD; 6pc 2 Immutable stacks; 7pc +20 RES; 8pc +12% SPD; 9pc 3 Immutable stacks. Immutable now fully blocks any cooldown increase — [Ayumilove 2025 patch notes](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/) (the summariser labelled it an "accessory" set, which is wrong: it is a variable set)
- 2025-12-10 (V11.00): **Mercurial** added (Grim Forest, variable set), up to +15% HP, +40 RES, +32% SPD and 3 Total Guard stacks. Each stack blocks one instance of incoming damage — [Ayumilove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)
- 2026-03-04 (V11.30): **Swift Parry** and **Deflection** (Platinum League sets) became variable sets. Swift Parry totals about +30% C.DMG, +28% SPD, +25% HP, a 50% Unkillable chance, 15% less damage taken and +50% ignore DEF. The old version was 4pc: +18% SPD, +30% C.DMG, and a chance of Unkillable on a fatal hit. Deflection totals about +60 ACC, +32% SPD, a 35% chance to deflect a debuff onto the attacker, and Block Debuffs at round start. Platinum Classic Arena chests now include artifacts/accessories — [Ayumilove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- 2026-07-02 (V11.65): Mercurial double-Total-Guard bug fixed. 2026-09-02 (V11.75): Total Guard nerfed. Provoke now bypasses Total Guard, and a Provoked champion can't apply or refresh stacks at turn start — [Ayumilove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)

**Accessory sets (Ring/Amulet/Banner; 1/2/3 pieces)**
| Set | Bonus per 1/2/3 | Source |
|---|---|---|
| Refresh | 5/10/15% chance a skill doesn't go on cooldown | Bazaar (Classic Arena) |
| Cleansing | 8/16/24% chance to remove 1 random debuff each turn | Bazaar |
| Bloodshield | Shield = 5/10/15% of damage dealt (AoE gives 75% less) | CvC tournament |
| Reaction | 25/50/75% chance to turn crits into normal hits when attacked before the wearer's first turn | CvC tournament |
| Revenge | 5/10/15% counterattack chance when hit | Clan Shop |
— [Ayumilove](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/). HellHades also counts 5 accessory sets — [HellHades Artifact Tier List, 2026-08-04](https://hellhades.com/raid/artifact-tier-list/)

### Inferences
- The user's list names "Divine sets", "Pinpoint/Stoneskin/Rebirth/Chronophage/Zeal/Supersonic/Slayer/Killstroke/Mercurial". All are covered above. Sets they didn't name but which exist: Taunting, Instinct, Righteous, Impulse, Fatal, Frostbite, Affinitybreaker, Immunity, Destroy, Stonecleaver.
- Farming summary for recommendations:
  - Dragon: SPD, ACC, Lifesteal, Destroy, Toxic, Frost, Avenging, Stalwart (and classically Daze).
  - Ice Golem: Life, Offense, DEF, C.RATE, RES, Retaliation, Reflex, Cursed, Taunting.
  - Fire Knight: C.DMG, Fury, Curing, Immunity, Shield, Frenzy, Regeneration, Stun, Savage.
  - Cursed City: Supersonic, Merciless.
  - Hydra: Stoneskin, Protection.
  - Siege: Feral.
  - Grim Forest: Mercurial.
  - Forge (Doom Tower / Faction Wars / Forge Pass): the forge sets.
  - Live Arena: Impulse, Zeal, Stonecleaver, Rebirth, Swift Parry, Deflection.
  - Clan Boss chests: Cruel, Immortal.
  - Classic Arena: Divine sets, and Refresh/Cleansing accessories.
- Variable sets let a build mix in 2-piece stat sets: a 6-piece variable set uses 6 slots and leaves 3 for something else. Recommenders should express builds as "N pieces of X + 2-piece Y" rather than assuming 4+2.

### Gaps
- Exact per-piece breakdowns for most variable sets (Supersonic, Merciless, Feral, Pinpoint, Stonecleaver, Rebirth, Slayer, Protection, Stoneskin, Mercurial, the reworked Swift Parry/Deflection) were not captured. The pages were truncated or listed only totals. The Stoneskin per-piece values on Ayumilove are internally inconsistent.
- HellHades' tier list rendered without set names in the fetcher, so a HellHades vs Ayumilove tier comparison could not be made.
- Dungeon sources for the newest farmable variable sets (e.g. which Grim Forest/Cursed City stages) are only as specific as "Cursed City" / "Grim Forest".
- No set additions in 2026 beyond the reworks were found; the 2026 patch page was truncated after ~100k characters (V11.10/V11.20 not read).

## 4. Ayumilove build-guide format, and reliability vs HellHades and DeadwoodJedi

### Takeaway
An Ayumilove champion page is a fixed template: a metadata header, per-content star ratings, skills, then a "build guide" block. That block holds artifact set lists split PvE / PvP / both, the main stat per variable slot, a stat priority grouped by role, relics, then mastery tables split PvP / PvE. Ayumilove is broad and frequently updated but aggregates community submissions. HellHades and DeadwoodJedi are the analytic references for exact tunes and stat targets.

### Cited Findings
- Champion page structure, as seen on the Arbiter page (updated 2026-10-18), top to bottom:
  1. Header: name, faction, rarity, role, affinity, rank, usability, tome count.
  2. Ability identifiers.
  3. "Obtain from".
  4. Blessing recommendations: four blessings tagged by 1–6★ awakening.
  5. Grinding ratings: Campaign, Arena Defense, Arena Offense, Clan Boss (Demon Lord, Hydra, Chimera), Faction Wars.
  6. Dungeon ratings: normal and Hard versions per dungeon.
  7. Potion keep ratings.
  8. Doom Tower ratings, per floor and boss.
  9. Overview and skills, with per-level upgrades and multipliers.
  10. Build guide: recommended artifacts in PvE, PvP and "PvE & PvP" lists; stat allocation per slot (gloves/chest/boots/ring/amulet/banner); stat priority grouped by role (e.g. Debuffer / Buffer / Buffer & Debuffer, stats in descending order); relics split the same way; skill tags.
  11. Masteries: separate PvP (Arena, Doom Tower, Faction Wars) and PvE (Campaign, Clan Boss, Dungeons) tables, numbered entries under the Offense / Defense / Support trees.
  12. A narrative "all-rounder" build with an equipment image.
  13. Lore, champion update history, videos, comments.
  Ratings are on a 5-star scale shown as filled/empty stars — [Ayumilove: Arbiter guide](https://ayumilove.net/raid-shadow-legends-arbiter-skill-mastery-equip-guide/)
- Format of a recommended-artifacts line: several set names, comma-separated, on one row per mode (PvE row vs PvP row). It is a menu of acceptable sets, not one prescribed loadout — [Ayumilove: Arbiter guide](https://ayumilove.net/raid-shadow-legends-arbiter-skill-mastery-equip-guide/)
- Ayumilove's set tier list contains at least one evident error (Mercurial's tier-list link points to the Merciless anchor) and an internally inconsistent Stoneskin per-piece listing — [Ayumilove artifact guide](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- Much of Ayumilove's detail on set sources, mechanics and Curing interactions comes from reader comments and the site owner's replies — [Ayumilove artifact guide comments](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)
- DeadwoodJedi's speed-tune pages list a speed range per champion, the sync turn (e.g. UNM syncs turn 7, NM turn 6 for one tower tune), skill setup per difficulty, and affinity-specific speed adjustments (e.g. a Spirit-affinity fast tower at 218, up to 222). All speeds are **true speed**, not the in-game displayed value, and the pages link the DWJ Clan Boss calculator — [DeadwoodJedi Basic tune](https://deadwoodjedi.com/speed-tunes/basic/); [DWJ Fast Tower Skullcrusher](https://deadwoodjedi.com/speed-tunes/fast-tower-skullcrusher-unkillable-copy/); [DWJ speed-tunes search results](https://deadwoodjedi.com/?p=2462)
- HellHades publishes the Artifact Tier List (updated 2026-08-04; 50+ sets, 5 accessory sets), the Optimiser, and boss guides with RES-based ACC calculations (e.g. Hydra) — [HellHades tier list](https://hellhades.com/raid/artifact-tier-list/); [HellHades Hydra guide](https://hellhades.com/getting-started-with-hydra-clan-boss-in-raid-shadow-legends/)

### Inferences
- How to read an Ayumilove page for a skill:
  1. Take the PvE or PvP set row matching the user's content as a candidate pool.
  2. Read the "stat allocation" lines for gloves/chest/boots/ring/amulet/banner as main-stat targets.
  3. Map the role-grouped stat priority onto the substats to roll for.
  4. Use the per-content ratings to decide whether the champion is worth investing gear in for that mode at all.
- Ayumilove gives *which* stats and sets. It rarely gives *how much* (exact ACC/SPD numbers). Cross-check thresholds with HellHades (stage RES tools, optimiser) and DeadwoodJedi (true-speed tunes). The sites differ in kind rather than conflicting: Ayumilove is a wide, community-aggregated catalogue; HellHades is curated, opinionated tier rankings and tools; DeadwoodJedi is precise speed tunes and calculators.

### Gaps
- No head-to-head study of build agreement between Ayumilove, HellHades and DWJ was found. No source compared their stat targets directly, so "do they agree?" cannot be answered with citations.
- The Ayumilove champion page was read for structure only, so no reproduction is included. Whether every champion page uses exactly this template, or only recent ones, was not verified.

## 5. Build archetypes and stat thresholds per game mode

### Takeaway
Archetypes: **nukers** (ATK% or HP%/DEF% scalers, C.RATE capped at 100%, then C.DMG), **debuffers** (ACC first, set by the content's boss RES, then SPD), **supports/tanks** (SPD, then HP%/DEF%, often RES). Cited ACC targets: Clan Boss UNM 230+ on debuffers, Hydra Normal at least 215 (head RES 140), Doom Tower Sorath at least 250. Speed tunes use *true* speed from DWJ.

### Cited Findings
- Clan Boss UNM: 230+ ACC on all debuffers (InTeleria, June 2026) — [InTeleria speed-tuned CB teams](https://www.inteleria.com/raid-speed-tuned-clan-boss-teams/)
- Hydra (Normal): the highest head RES was 140, so HellHades recommended at least 215 ACC. Head affinities, and so the targets, change with rotation. The guide is ~2.5 years old, and HellHades points to its Stages Tool for current numbers — [HellHades: Getting started with Hydra](https://hellhades.com/getting-started-with-hydra-clan-boss-in-raid-shadow-legends/)
- Doom Tower Sorath (Frost Spider): aim for at least 250 ACC — [InTeleria Doom Tower guide](https://www.inteleria.com/doom-tower/) (reliability unclear)
- Doom Tower rotates bosses, so ACC needs shift with the current floor bosses — [InTeleria Doom Tower guide](https://www.inteleria.com/doom-tower/)
- Speed tunes: DWJ's basic tune is a 1:1 ratio tune that underlies all others. Listed speeds are true speeds, and set bonuses add decimals, so use the calculator to convert displayed speed to true speed — [DeadwoodJedi Basic tune](https://deadwoodjedi.com/speed-tunes/basic/); [InTeleria CB teams](https://www.inteleria.com/raid-speed-tuned-clan-boss-teams/)
- Speed is the top stat for most roles. Multi-roll SPD pieces are "account-defining" — [HellHades: How Speed Works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)

### Inferences
- Archetype stat templates a skill can use (synthesis of the sources above plus slot rules from section 1):
  - **Nuker (ATK-based)**: Gloves C.RATE (or C.DMG if C.RATE is already capped from substats/sets), Chest ATK%, Boots SPD, Amulet C.DMG, Banner ATK. Aim for 100% C.RATE, then maximise C.DMG and ATK. Sets: Savage/Lethal/Merciless/Cruel/Killstroke/Zeal/Stonecleaver/Slayer.
  - **Nuker (HP- or DEF-based scaler)**: same, but with HP%/DEF% on the chest and HP/DEF on the banner.
  - **Debuffer**: Chest ACC (or HP%/DEF% if ACC is met from substats/banner), Banner ACC, Boots SPD, Gloves HP%/DEF%. Meet the ACC threshold first (above), then SPD. Sets: Perception/Accuracy/Feral/Pinpoint/Speed/Reflex/Deflection.
  - **Support / tank**: Boots SPD, Chest/Gloves HP% or DEF%, Banner HP/DEF/RES. Sets: Speed/Supersonic/Stoneskin/Mercurial/Protection/Resilience/Defiant/Bolster/Immortal/Regeneration/Guardian.
- ACC thresholds scale with boss RES. A rough rule from the Hydra example: about head RES + 75. That fits the 215 = 140 + 75 example; it is an inference from one data point, not a published formula.

### Gaps
- No fetchable source was found for ACC targets for Dragon, Spider (e.g. stage 20/25 or Hard), Fire Knight, Ice Golem, Hydra UNM/Nightmare, Chimera, or Doom Tower Hard bosses beyond Sorath. Commonly repeated community figures (Clan Boss UNM ~225–250, Spider 20 ~200+, Dragon 20 ~200+, Doom Tower Hard 250+) are prior knowledge and unverified here.
- No sourced HP/DEF survival thresholds per mode (e.g. "40k+ HP for Hard DT") were found.
- Specific UNM tune speed bands (e.g. Budget Unkillable ~171–174 / 176–178) are on DWJ's site but were not extracted this session.

## 6. Gear tools: in-game Auto-Equip/loadouts and third-party optimisers

### Takeaway
Plarium added native **Auto-Equip for artifacts and accessories in V11.50 (2026-05-06)**. The HellHades Optimiser (premium) reads account data through an extractor and runs a constrained search. Users set minimum stat targets and required/excluded sets, and results are ranked by priorities such as "highest damage", "highest overall" or effective HP. The exact scoring formula is not published.

### Cited Findings
- V11.50 (2026-05-06) added Auto-Equip for Artifacts and Accessories, plus new gear filters — [Ayumilove 2026 patch notes](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- HellHades Optimiser: reads account data the game writes, collected by the HH Artifact Extractor running alongside the game, and changes nothing in game. Search runs on HellHades servers or the user's GPU. Users set minimum stat targets; builds below them fail, and the top-ranked combination is shown — [HellHades: How to use the Artefact Optimizer (2021-01-06)](https://hellhades.com/how-to-use-the-artefact-optimizer-for-raid-shadow-legends/)
- Optimiser options: require or exclude sets; include equipped gear; exclude gear on locked champions (overridable); minimum artifact level filter; "assume level 16" to evaluate maxed primaries; "hero to max level" to evaluate as a 6★ level-60 champion. Ranking priorities are labelled "highest damage" and "highest overall", with optional optimisation for Effective HP or damage. A Skills tab compares damage output between builds. The formula is not described — [HellHades: Understanding the Gear Optimiser (2021-06-26, Optimiser 3.0)](https://hellhades.com/understanding-the-hellhades-gear-optimiser/)
- Default stat importance in the HH optimiser is now 0 ("not important"), so users must assign stat priorities — [HellHades search snippet](https://hellhades.com/how-to-use-the-artefact-optimizer-for-raid-shadow-legends/)
- The HH optimiser needs a paid membership, and users report extractor update and connection errors after game patches — [HellHades optimizer comments](https://hellhades.com/how-to-use-the-artefact-optimizer-for-raid-shadow-legends/comment-page-5/)
- Gear filter improvements: substat-upgrade filter (V10.60, 2025-08-06), Quick Craft auto-sell (V10.40, 2025-04-02) — [Ayumilove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)

### Inferences
- The HH optimiser's objective is effectively: hard constraints (min stats, set rules, artifact pool), then rank the feasible builds by a user-weighted stat score or a modelled output (damage / EHP). A skill that recommends gear can copy this: take thresholds from section 5 as constraints, then maximise the role's priority stats.
- In-game Auto-Equip (2026) is new, and its objective function is undocumented in the sources found. Treat it as a baseline and refine by hand or with an optimiser.

### Gaps
- **Raid Toolkit** (the open-source account extractor/SDK) was not covered by any fetched source. Its current status and how it relates to HH could not be verified.
- In-game **loadouts / gear presets** were not found in the 2025–2026 patch notes read (the 2026 page was truncated, and V11.10/V11.20 were not read). Whether a preset system exists and when it was added is unverified.
- The objective and weighting used by in-game Auto-Equip (V11.50) were not found.
- The HH optimiser docs date from 2021. Current (2025–2026) optimiser features may differ.
