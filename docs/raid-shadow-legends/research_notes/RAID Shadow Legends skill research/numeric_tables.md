# RAID: Shadow Legends — exact numeric tables (verification pass)

Research date: 2026-11-07. Method: the RAID fandom wiki (`raid-shadow-legends.fandom.com`) was read through its MediaWiki API (`action=query&prop=revisions&rvprop=content|timestamp`), which returns the last revision timestamp quoted below. The wiki is thin and mostly last edited in 2022, so most of its tables predate recent reworks. The official Plarium support pages (`raid-support.plarium.com`, `plariumplay-support.plarium.com`) returned HTTP 403 to fetches. HellHades, AyumiLove and GamerEmpire were checked as text.

**Overall verdict:** of the nine targets, only the **mercy thresholds** (AyumiLove, Sept 2026), **Great Hall table** (wiki, 2022), **glyph ranges, partial** (wiki, 2022), **upgrade success chances** (wiki, 2022, crowd-sampled), **affinity hit numbers** (HellHades, Oct 2026) and **arena tier structure and reset rules** (wiki, 2022) came back with citable numbers. **Main-stat tables by rank, substat roll ranges, arena point thresholds and weekly rewards, the DEF formula as an official figure, the turn-meter tick formula, and mastery scroll costs were NOT verified.** Leave them out of the skill, or label them "unverified, check in-game".

## Artifact/accessory main-stat values by rank (start and +16)

### Takeaway
No source reachable as text gave the full main-stat table by star rank. The only verified data point is DEF% boots at 3★ and 4★. The wiki's artifact pages contain no stat values.

### Cited Findings
- DEF% boots main stat: 3★ starts at 4% and reaches 30% at +16; 4★ starts at 6% and reaches 40% at +16. The page was last modified 2022-11-28. — [GamerEmpire, Artifacts Guide](https://gamerempire.net/raid-shadow-legends-artifacts-guide/)
- The star count sets both the base and the maximum value of the main stat. — [GamerEmpire, Artifacts Guide](https://gamerempire.net/raid-shadow-legends-artifacts-guide/)
- Locked main stats: Weapon is always ATK (substats can't be DEF/DEF%), Helmet is always HP, Shield is always DEF (substats can't be ATK/ATK%). Gauntlet main stat can't be SPD, RES or ACC. Chestplate main stat can't be C.RATE or C.DMG. Boots main stat can't be C.RATE, C.DMG, RES or ACC. (Wiki revision 2022-11-02.) — [Fandom wiki, General Artifacts](https://raid-shadow-legends.fandom.com/wiki/General_Artifacts)
- SPD is only possible as a main stat on boots. — [Plarium forum, artifacts priority stats](https://forum.plarium.com/en/raid-shadow-legends/674_game-discussion/196222_artifacts-priority-stats)
- Artifacts upgrade from level 1 to 16. A substat is revealed or boosted at +4, +8, +12 and +16. (Wiki revision 2022-12-10.) — [Fandom wiki, Upgrading Artifacts](https://raid-shadow-legends.fandom.com/wiki/Upgrading_Artifacts)
- Gear of Rank 4 or higher and at least level 12 can be Ascended (Plarium official guide, as quoted in a search snippet; the page itself returned 403). — [Plarium support, Basic Guide: Gear Overview](https://plariumplay-support.plarium.com/hc/en-us/articles/8020641151516-Basic-Guide-Gear-Overview)
- The AyumiLove Artifact and Accessory Guide (updated 2026-09-13) has no main-stat values. It gives the number of unlockable substats by rarity: Uncommon 1, Rare 2, Epic 3, Legendary 4. — [AyumiLove, Artifact and Accessory Guide](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/)

### Inferences
- The 3★→4★ DEF% step (30% → 40% max) implies each rank adds roughly 10 points to % main stats at +16. It is not safe to extrapolate 5★/6★ values from this.
- Ascension (an added stat layer from 2023–2024) means any older main-stat table describes only the base artifact, not an ascended one.

### Gaps
- The full table (1★–6★ start and +16 values for flat/% ATK, HP and DEF, plus SPD, C.RATE, C.DMG, ACC and RES) was not found in any fetchable text source. Values often quoted from memory (for example 6★ SPD boots = 45) could not be verified and should not be stated as fact. Likely sources if a later pass has browser access: the Plarium "Basic Guide: Gear Overview" (403 to fetch), the HellHades Artifact Guide, or the in-game artifact info screen.

## Substat starting values and per-roll ranges by rank and rarity (incl. Mythical)

### Takeaway
Not verified. No fetched source gave substat roll ranges. The only figures are anecdotal (one 5★ SPD roll "may give 10"). The wiki's Mythical page says the Mythical artifact start values are "??".

### Cited Findings
- Each artifact can roll into its SPD substat several times while upgrading. One roll can be useful, while three or four rolls can be "account-defining" (HellHades, published 2026-09-27; no ranges given). — [HellHades, How Speed Works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)
- Anecdote (Plarium forum, ~2022): one SPD roll on a 5★ item "may give 10", with +4 more achievable with glyphs. — [Plarium forum, gear primary and sub stats](https://forum.plarium.com/raid-shadow-legends/674_game-discussion/195301_gear-primary-and-sub-stats)
- The wiki's Mythical page (revision 2024-02-27) lists Mythical artifacts as "Start with ??". It has no numbers. — [Fandom wiki, Mythical](https://raid-shadow-legends.fandom.com/wiki/Mythical)
- A reworked piece keeps its rarity, level, rank and substat roll counts, but loses glyph bonuses. Each piece can be reworked once with Chaos Ore (5★/6★, Epic/Legendary variants). (Wiki revision 2022-09-14.) — [Fandom wiki, Artifact Reworking](https://raid-shadow-legends.fandom.com/wiki/Artifact_Reworking)

### Gaps
- Starting substat values and per-roll ranges by rank and rarity for SPD, ACC, C.RATE, C.DMG, %ATK/HP/DEF and RES were not found. The Mythical rarity is undocumented on the wiki.

## Glyph value ranges by rank and stat

### Takeaway
The wiki has partial glyph data (revisions Nov–Dec 2022). It gives the overall range per glyph type and a few per-level ranges. The SPD "+1 to +16" figure is internally inconsistent: the line names the DEF substat, not SPD. Treat the overall ranges with caution.

### Cited Findings
- Overall glyph ranges: ATK (flat) +4 to +40; ATK% +1 to +16; HP (flat) +75 to +750; HP% +1 to +16; DEF (flat) +75 to +750; DEF% +1 to +16; SPD +1 to +16; RES +1 to +16; ACC +1 to +16. (Revision 2022-12-18. The page is marked a stub, and the SPD line is mis-worded as "substat for DEF".) — [Fandom wiki, Enchanting Artifacts](https://raid-shadow-legends.fandom.com/wiki/Enchanting_Artifacts)
- Per-level ranges on the same page: DEF (flat) level 1 = 4–5 (this contradicts the "+75" flat-DEF minimum above); DEF% level 1 = 1–2; SPD level 1 = 1, level 2 = 1–2; RES level 1 = 1–2, level 2 = 2–3. — [Fandom wiki, Enchanting Artifacts](https://raid-shadow-legends.fandom.com/wiki/Enchanting_Artifacts)
- ATK glyph by level: L1 = +4 or +5 (costs 1,500 Silver to apply); L2 = +4 to +10 (costs 4,000 Silver); L3 = +6 to +15; L4 = +8 to +20. A glyph always gives at least its minimum. Re-applying to a substat already enchanted near the glyph's floor can fail to raise it. (Revision 2022-11-06.) — [Fandom wiki, ATK Glyph](https://raid-shadow-legends.fandom.com/wiki/ATK_Glyph)
- Glyph names: Attack (ATK), Strike (ATK%), Health (HP), Vitality (HP%), Defense (DEF), Endurance (DEF%), Haste (SPD), Resistance (RES), Precision (ACC). C.RATE and C.DMG glyphs exist (icons listed) but have no ranges given. — [Fandom wiki, Glyphs](https://raid-shadow-legends.fandom.com/wiki/Glyphs)

### Inferences
- The wiki is keyed by glyph "level" (rank), not by rarity. If glyphs now also have rarity tiers, the wiki predates that.
- The flat-HP and flat-DEF "+75 to +750" ranges look wrong next to the ATK range of +4 to +40 and DEF level 1 = 4–5. Do not use them without in-game confirmation.

### Gaps
- Glyph ranges by rarity, C.RATE and C.DMG glyph ranges, and levels 3–6 for most stats.

## Great Hall (affinity bonuses): stat per level, cost, maximum

### Takeaway
The wiki has a full 10-level table (revision 2022-08-08). Bonuses are per affinity, cost the same for every affinity, and cover HP%, ATK%, DEF%, C.DMG%, RES and ACC only, with no SPD or C.RATE. Max level 10 gives 20% HP/ATK/DEF, 25% C.DMG and 80 RES/ACC. No newer source confirms or contradicts this, so flag it as possibly pre-rework.

### Cited Findings
- Great Hall table, as rank: cost | HP% / ATK% / DEF% | C.DMG% | RES | ACC (revision 2022-08-08) — [Fandom wiki, Great Hall](https://raid-shadow-legends.fandom.com/wiki/Great_Hall)
  - 1: 50 Bronze | 2% | 2% | 5 | 5
  - 2: 150 Bronze | 3% | 4% | 10 | 10
  - 3: 300 Bronze | 4% | 6% | 15 | 15
  - 4: 400 Silver | 6% | 8% | 20 | 20
  - 5: 500 Silver | 8% | 10% | 30 | 30
  - 6: 600 Silver | 10% | 12% | 40 | 40
  - 7: 700 Gold | 12% | 15% | 50 | 50
  - 8: 800 Gold | 14% | 18% | 60 | 60
  - 9: 900 Gold | 17% | 21% | 70 | 70
  - 10: 1,000 Gold | 20% | 25% | 80 | 80
- Each bonus applies to champions of one affinity, and the cost per level is the same for every affinity. Bronze-medal costs can be paid with Silver at 1 Silver = 2 Bronze. SPD and C.RATE are not offered. — [Fandom wiki, Great Hall](https://raid-shadow-legends.fandom.com/wiki/Great_Hall)
- Medal exchange: 1 Silver = 2 Bronze and 1 Gold = 2 Silver (HellHades, 2021-01-28). — [HellHades, Understanding the Arena](https://hellhades.com/understanding-the-arena-and-the-benefits-it-can-bring/)
- The Classic Arena is the only way to earn medals for the Great Hall. — [HellHades, Understanding the Arena](https://hellhades.com/understanding-the-arena-and-the-benefits-it-can-bring/)

### Inferences
- If the table is current, maxing one stat for one affinity costs 50+150+300 Bronze, then 400+500+600 Silver, then 700+800+900+1,000 Gold. That is 6 stats × 4 affinities = 24 tracks.

### Gaps
- No 2024–2026 source confirms the table. The costs in particular look low and should be checked in-game.

## Classic Arena: tier point thresholds and weekly rewards

### Takeaway
The tier structure and rules are documented, but point thresholds and per-tier weekly rewards were not found in any fetchable source. The official Plarium support article returned 403.

### Cited Findings
- Tiers, ascending: Unranked; Bronze I–IV; Silver I–IV; Gold I–IV; Platinum (the wiki says Platinum I–IV; HellHades 2021 says Platinum has no sub-tiers). Gaining or losing points moves a player only one adjacent tier at a time. (Wiki revision 2022-09-05.) — [Fandom wiki, Arena](https://raid-shadow-legends.fandom.com/wiki/Arena); [HellHades, Understanding the Arena](https://hellhades.com/understanding-the-arena-and-the-benefits-it-can-bring/)
- A search summary of a HellHades post said Gold V was added later. This was not fetched or verified. — [WebSearch summary, HellHades](https://hellhades.com/understanding-the-arena-and-the-benefits-it-can-bring/)
- The weekly ranking period ends every Monday at 08:00 UTC, and rewards depend on the tier held at that moment. A player with fewer than 20 offense battles in the period is demoted one tier after rewards are paid. After 30 days without offense battles a player becomes Unranked and restarts at Bronze I. — [Fandom wiki, Arena](https://raid-shadow-legends.fandom.com/wiki/Arena)
- Tokens regenerate 1 per hour, up to 10 held. The opponent list can be refreshed for 5 Gems, or free every 15 minutes. Defense teams have up to 4 champions. The arena unlocks at player level 6. — [Fandom wiki, Arena](https://raid-shadow-legends.fandom.com/wiki/Arena)
- Medals by tier: Bronze tier gives Bronze medals, Silver tier gives Silver, Gold and Platinum give Gold. — [Fandom wiki, Arena](https://raid-shadow-legends.fandom.com/wiki/Arena)
- Each tier gives permanent global HP/ATK/DEF bonuses to all champions. The wiki's "Classic Arena Tier Stat Bonuses" page (revision 2022-08-08) leaves the values blank. — [Fandom wiki, Classic Arena Tier Stat Bonuses](https://raid-shadow-legends.fandom.com/wiki/Classic_Arena_Tier_Stat_Bonuses)
- Arena chests contain random Gems, XP Brews, Shards and Divine artifacts (Divine Offense, Crit Rate, Life and Speed sets: 2-piece gives a 15% Max HP shield for 3 turns plus ATK +15% / C.RATE +12% / HP +15% / SPD +12%). — [Fandom wiki, Arena](https://raid-shadow-legends.fandom.com/wiki/Arena)

### Gaps
- Point thresholds from Bronze I to Platinum, and weekly chest contents per tier. Official source: [Plarium support, Classic Arena](https://raid-support.plarium.com/hc/en-us/articles/360014642780-Classic-Arena) (403 to automated fetch). The tier stat-bonus values are also missing.

## Clan Boss: daily affinity rotation and the 50% HP switch

### Takeaway
No fetched source documents a fixed weekly affinity order. The wiki (last revision 2025-10-26) and HellHades (2020 and 2026-10-29) all describe the boss changing affinity once it drops below 50% HP. The wiki says each day starts as Void at 10:00 UTC, and the new affinity holds until the next reset. This conflict is unresolved: see Gaps.

### Cited Findings
- The Clan Boss resets every day at 10:00 UTC with full HP and VOID affinity. Once it reaches 50% HP it switches to a different affinity for the next and all later battles until the next 10:00 UTC reset. Defeated bosses pay two chests instead of one. A player gains 1 key every 6 hours, up to 2 held. Difficulties run Easy, Normal, Hard, Brutal, Nightmare and Ultra-Nightmare. (Wiki revision 2025-10-26. The edit date doesn't mean every sentence is current; the page is marked a stub.) — [Fandom wiki, Clan Boss](https://raid-shadow-legends.fandom.com/wiki/Clan_Boss)
- Gathering Fury: from turn 10 the boss's damage increases every turn, by more from turn 20. From turn 50 it ignores Block Damage and Unkillable and applies Block Revive to champions it kills. — [Fandom wiki, Clan Boss](https://raid-shadow-legends.fandom.com/wiki/Clan_Boss)
- HellHades (published 2026-10-29): the Demon Lord's affinity "can change" once it drops below 50% HP. No daily schedule is given. — [HellHades, How Affinity Works](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- HellHades Clan Boss guide (~2020): at 50% health the boss switches to Force, Magic or Spirit and stays on it until server reset. — [HellHades, Guide to Clan Boss](https://hellhades.com/?p=2137)
- Affinity numbers (HellHades, 2026-10-29): attacking a target your affinity is strong against gives +15% C.RATE and a 30% chance of a Strong Hit (+30% damage, only on non-crits). Attacking a target your affinity is weak against reduces damage by 20%, with a 35% chance of a Weak Hit (a further −30% damage, and debuffs tied to that hit can't be placed). — [HellHades, How Affinity Works](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- Other bosses do use fixed rotations: Chimera runs a 28-day cycle (Ram, Lion and Viper share one affinity, Ultimate Form uses another), and Hydra uses monthly rotations with weekly resets. — [AyumiLove, Chimera Clan Boss Guide](https://ayumilove.net/raid-shadow-legends-chimera-clan-boss-guide/) (search snippet, page not fetched)

### Inferences
- Every source agrees that the Demon Lord changes affinity at the 50% HP mark, so a fixed day-by-day rotation is not supported by any source fetched here. The "fixed weekly order" claim should be dropped, or marked unverified, unless an in-game or Plarium source turns up.
- The affinity numbers HellHades gives (+15% C.RATE, −20% base damage) differ from widely repeated community descriptions. They are the newest source found, but they should be checked against the in-game Affinity help screen before being stated as fact.

### Gaps
- Whether the Demon Lord now follows a published day-by-day affinity calendar (reportedly the case in later versions), and whether the 50% switch still exists in 2026. No official Plarium page could be fetched.

## Mercy (pity) thresholds for Ancient, Void, Sacred and Primal

### Takeaway
The most current text source is AyumiLove (updated 2026-09-13), which gives one consistent table covering all four shard types, Primal Mythical included. It is a fan site with no Plarium citation, but it is the most complete and recent source found. Older figures that conflict with it (Ancient Legendary +0.5%/pull, Sacred mercy at 20, no Primal mercy) appear only in search snippets.

### Cited Findings
- Mercy table, as shard and rarity: threshold (summons without that rarity) → increase per summon after it (AyumiLove, updated 2026-09-13) — [AyumiLove, Mercy System Explained](https://ayumilove.net/raid-shadow-legends-mercy-system-explained/)
  - Ancient Epic: 20 → +2%
  - Ancient Legendary: 200 → +5%
  - Void Epic: 20 → +2%
  - Void Legendary: 200 → +5%
  - Sacred Legendary: 12 → +2%
  - Primal Legendary: 75 → +1%
  - Primal Mythical: 200 → +10%
- Each increase is added to the base rate directly (for example Sacred goes 6% → 8% → 10%). Every shard type has its own counters, and the Epic and Legendary counters are separate, as are Primal's Legendary and Mythical counters. A counter resets when that rarity is pulled. — [AyumiLove, Mercy System Explained](https://ayumilove.net/raid-shadow-legends-mercy-system-explained/)
- Base rates on the same page: Ancient and Void are 91.5% Rare, 8% Epic and 0.5% Legendary. Sacred is 94% Epic and 6% Legendary. Primal is 82.5% Rare, 16% Epic, 1% Legendary and 0.5% Mythical. — [AyumiLove, Mercy System Explained](https://ayumilove.net/raid-shadow-legends-mercy-system-explained/)
- Conflicting snippets (not verified): BlueStacks and Inteleria are reported to give different increments (for example +0.5% per pull for Ancient Legendary) and different "guaranteed by" counts (150 Ancient, 20 Sacred). Some sources say Primal has no mercy. — [BlueStacks, Pity System Guide](https://www.bluestacks.com/blog/game-guides/raid-shadow-legends/rsl-pity-system-guide-en.html); [Inteleria, Shard drop rates and pity](https://www.inteleria.com/raid-shard-drop-rates-pity-system/)
- Separate from shard mercy, Relic Crafting is getting a mercy system with Mythical and group mercy, per Update 11.90 coverage. — [HellHades, Update 11.90](https://hellhades.com/raid-shadow-legends-update-11-90-relic-mercy-faction-wars-hard)

### Inferences
- From the AyumiLove numbers: a Sacred Legendary is guaranteed by summon 12 + ceil((100−6)/2) = 59, and an Ancient Legendary by 200 + ceil(99.5/5) = 220. These are arithmetic on a fan-sourced table and are not quoted guarantees.
- Plarium has never published official mercy numbers. All figures are data-mined or community-observed, so the skill should state them as community-reported.

### Gaps
- No official Plarium confirmation. Event multipliers (2x/10x) are reported to leave mercy counters as they are, but this is unverified.

## DEF damage-mitigation formula and turn-meter fill per tick

### Takeaway
No official formula exists. The only DEF formula found is a community approximation, and the turn-meter "SPD × 0.07 per tick" was not documented by any source fetched here.

### Cited Findings
- Pre-mitigation damage = Total ATK (or HP/DEF for scaling skills) × skill multiplier × book bonus × crit multiplier (1 + C.DMG%) × mastery bonuses × affinity × buffs × passives, then × DEF mitigation. The article doesn't define mitigation (HellHades, 2021-01-09). — [HellHades, How your Damage is calculated](https://hellhades.com/how-your-damage-is-actually-calculated-in-raid-shadow-legends/)
- Community approximation of damage taken after DEF: `1 − 0.85 × (1 − EXP(−2 × DEF / 3000))`, which ranges from 100% at 0 DEF to 15% at very high DEF. This is attributed to HellHades material in a search snippet; the fetched article didn't show it, likely because of truncation or a comment. It is fan-derived and not official. — [HellHades, How your Damage is calculated, comment page 2](https://hellhades.com/how-your-damage-is-actually-calculated-in-raid-shadow-legends/comment-page-2/)
- Anecdote: on Doom Tower Normal stage 99, Jizoh has 5,293 DEF, and 60% Decrease DEF reportedly raises damage dealt by about 104%. — [Reddit r/RaidShadowLegends (mirror)](https://axebps-redlib.hf.space/r/RaidShadowLegends/comments/lapfz3/why_decrease_defense_isnt_effective_in_hard_doom)
- The turn meter fills continuously with SPD, and a champion acts at 100%. No tick rate or coefficient is stated (HellHades, 2026-09-27). — [HellHades, How Speed Works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)

### Inferences
- The approximation implies DEF = 3000 gives about `1 − 0.85 × (1 − e^−2)` ≈ 26.5% damage taken. This is arithmetic on an unofficial formula.

### Gaps
- Turn-meter fill per tick (the "SPD × 0.07" figure) was not found in any fetched source. HellHades links a separate "Turn Meter Guide" that wasn't fetched. The DEF formula should be presented as a community approximation only.

## Mastery scroll costs per tier

### Takeaway
Not found. The wiki's mastery pages have no cost table.

### Cited Findings
- Mastery scrolls come from Minotaur's Labyrinth or can be bought with Gems. The guide page has no cost table (wiki revision 2024-02-17). — [Fandom wiki, Champion Mastery Guide](https://raid-shadow-legends.fandom.com/wiki/Champion_Mastery_Guide)

### Gaps
- Scroll cost per mastery tier (Basic, Advanced and Divine, by tier 1–6) is not documented in any fetched source.

## Related: artifact upgrade success chances (bonus finding)

### Takeaway
The wiki has a crowd-sampled table of upgrade success chances by level (revision 2022-11-15). It is based on small samples and is not official.

### Cited Findings
- Success chance per upgrade step: 0→4 100%; 4→5 77%; 5→6 70%; 6→7 65%; 7→8 46%; 8→9 44%; 9→10 36%; 10→11 25%; 11→12 22%; 12→13 21%; 13→14 15%; 14→15 20%; 15→16 5%. The samples are small (for example 15→16 rests on 5 successes in 92 tries). — [Fandom wiki, Upgrade Chance](https://raid-shadow-legends.fandom.com/wiki/Upgrade_Chance)

### Inferences
- Upgrade chances also vary with artifact rank and rarity in-game. This table doesn't say which rank was sampled, so use it only as a rough guide.

### Gaps
- Official per-rank upgrade odds and silver costs.
