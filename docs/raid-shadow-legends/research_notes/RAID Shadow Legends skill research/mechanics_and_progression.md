# RAID: Shadow Legends — Core Mechanics and Account Progression (research notes, as of Nov 2026)

Research date: 2026-11-07. The latest patch found is **V11.90 (HellHades write-up dated 2026-11-03)**. Before it came V11.85 (2026-10-22) and V11.80 (2026-10-08). Most mechanics explainers (damage, ACC/RES, masteries) are old community articles from 2020–2023, sometimes re-dated. Plarium has never published the damage or mitigation formulas, so those numbers are community-derived. Where only a fan site gives a number, that is noted.

**Source quality key:** HellHades (hellhades.com) and AyumiLove (ayumilove.net, the user's main source) are fan or creator sites. Neither is official, but both are the community standard. Plarium forum posts are player-written unless they are in the News section. I could not reach Reddit with my tools. DeadwoodJedi only came up for its Clan Boss calculator and speed-tune pages.

---

## 1. Stats and core combat mechanics (what each stat does, ACC vs RES, the damage formula and DEF, crit, speed and turn meter, affinities)

### Takeaway
Damage is a chain of multipliers: the scaling stat (ATK, or HP/DEF for champions that scale on those) × skill multiplier × book bonus × (1 + C.DMG on a crit) × masteries × buffs/debuffs × affinity, then DEF mitigation last. To land a debuff, a champion's ACC should be about 30 points above the target's RES. At equal ACC and RES the land rate is about 90%. There is always a 3% resist floor unless the skill says it cannot be resisted. Speed fills the turn meter in proportion to SPD, and overflow past 100% decides who acts first. Affinities follow Magic > Spirit > Force > Magic, with Void neutral. Attacking into a bad matchup carries a 35% chance of a Weak Hit, which blocks the attack's debuffs entirely. This is the most common hidden reason a build fails.

### Cited Findings
**Damage formula**
- HellHades' damage chain: "Total ATK (or HP or DEF for HP or DEF champions) x Skill Multiplier x Increase Damage from Books x Crit Multiplier x Mastery Bonuses x Chance of Affinity Bonus x Buffs x Passives x Defense Mitigation". Crit multiplier is "100% + Crit Damage % assuming you always crit". Article originally published 2021-01-09, so it predates later systems such as Blessings and Relics. — [HellHades: How your damage is actually calculated](https://hellhades.com/how-your-damage-is-actually-calculated-in-raid-shadow-legends/)
- Worked example from that article (Kael, A2, 100% crit vs Void): "3,000 x 2.8 x 4.65 x 1.2 = 46,872 (Damage before Mitigation)". Weaken (25%) is a flat +25% damage taken. Bad-El's passive is a flat +20% against poisoned enemies. A 50% Increase ATK raises total ATK by 50%. — [HellHades](https://hellhades.com/how-your-damage-is-actually-calculated-in-raid-shadow-legends/)
- HellHades says DEF mitigation "is a little harder to explain" and does not give a closed formula in the text I retrieved. A search-engine summary said the article's spreadsheet lets damage fall to roughly 15% of the pre-mitigation value at high DEF, but I could not confirm that in the page text. — [HellHades](https://hellhades.com/how-your-damage-is-actually-calculated-in-raid-shadow-legends/)
- Damage-reduction passives stack **multiplicatively**, not additively. A damage-reduction champion's position in the lineup can decide whether their passive applies to damage redirected by Ally Protection. — [HellHades: Ally Protection](https://hellhades.com/ally-protection-in-raid-shadow-legends/)
- 2025–2026 Ignore-DEF counters: the Winter's Warden passive "reduces certain Ignore DEF effects" (V11.00, 2025-12-10) — [AyumiLove Patch Notes 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/). The Platinum-tier Deflection set (V11.30, 2026-03-04) makes "Ignore DEF effects are 10% less effective (5% for Bosses)". The Fortify buff cuts enemy Ignore DEF by 15%/25%. The Shatter buff grants +7.5%/15% Ignore DEF. — [AyumiLove Patch Notes 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/); [AyumiLove Buffs & Debuffs](https://ayumilove.net/raid-shadow-legends-buffs-debuffs-guide/)

**ACC vs RES (debuff landing)**
- At equal ACC and RES the attacker lands about 90% of the time (10% resisted). With ACC 30 above RES, about 97%. With RES 100 above ACC, the defender resists about 90%. With RES 150 above ACC, about 97%. "Unless an ability specifically states that it 'cannot be resisted', there is always a 3% chance for a resist" — [HellHades: Buffs, Debuffs and Instant Effects](https://hellhades.com/?p=2223)
- The skill's own listed chance (e.g. "50% chance to place") is checked first, then ACC vs RES. Weak Hits block debuffs no matter how much ACC the champion has (see Affinities). — [HellHades: How affinity works](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- Player rule of thumb: aim for +25 over enemy RES for about 96–97% land rate. — [Plarium forum: Accuracy vs Resistance](https://forum.plarium.com/raid-shadow-legends/674_game-discussion/1605789_accuracy-vs-resistance) (player opinion)
- Low-confidence rule from a secondary site: "ACC ≥ RES + 50" means a high land chance. This conflicts with HellHades' finer curve. — [gameslearningsociety](https://www.gameslearningsociety.org/wiki/how-important-is-accuracy-in-raid/)
- Stage-specific enemy RES values can be looked up in HellHades' Raid Stages tool. — [HellHades: Buffs, Debuffs and Instant Effects](https://hellhades.com/?p=2223)
- Since 2025-11-12 (V10.90), bosses are immune to Ensnare, Fatigue and Hunter's Gaze. — [AyumiLove Patch Notes 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)
- One 2026 rebalance makes ACC irrelevant for a specific champion: Danag Skullreap's debuffs "cannot be resisted, if this Champion's C.DMG is higher than the target's" (V11.70, 2026-08-05). — [AyumiLove Patch Notes 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)

**Speed and turn meter**
- The turn meter fills according to SPD: a 200-SPD champion fills about twice as fast as a 100-SPD one. When several champions are ready at once, the one furthest past 100% acts first. The overflow is real but the UI hides it. Set bonuses produce hidden decimal SPD, so two champions with the same displayed SPD can differ. HellHades' page is dated 2026-09-27. — [HellHades: How speed works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)
- Total SPD = base + gear (flat and %) + mastery SPD. Per AyumiLove, Increase SPD is +15% or +30% of total SPD, does not stack, and there is "not speed cap implemented in the game" (Arena speeds of about 350 are used). — [AyumiLove: Increase Speed list](https://ayumilove.net/?p=41741)
- Auras raise the base SPD of eligible champions from the start of battle. Each aura has a location scope: Arena only, Dungeons/Doom Tower/Faction Wars, or all battles. — [HellHades: How speed works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)
- The game simulates in "ticks", filling every champion's meter on each tick. This description comes from a player, not an official source. — [Plarium forum: How do speed and turn meter actually work](https://forum.plarium.com/raid-shadow-legends/674_game-discussion/614896_how-do-speed-and-turnmeter-actually-work-exactly)
- Clan Boss speed tunes such as 4:3 (four champion turns per three boss turns) depend on every team member's speed, and the DeadwoodJedi calculator is the standard tool. DWJ warns against masteries that alter turn meter or cooldowns in fixed tunes, such as Cycle of Magic and Lasting Gifts. — [DeadwoodJedi CB calculator guide](https://deadwoodjedi.com/clan-boss-calculator-guide/); [BlueStacks speed-tuned CB](https://www.bluestacks.com/blog/game-guides/raid-shadow-legends/rsl-speed-tuned-clan-boss-team-en.html)

**Affinities**
- Magic beats Spirit, Spirit beats Force, Force beats Magic. Same affinity is neutral. Void is neutral against everything, including Void. — [HellHades: How affinity works (2026-10-29)](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- **Advantage:** +15% C.RATE and a 30% chance of a Strong Hit (+30% damage). Strong Hits only happen on non-crits. — [HellHades](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- **Disadvantage:** −20% damage, a 35% chance of a Weak Hit (a further −30% damage), and a Weak Hit "prevents debuffs ... from being placed, regardless of how much ACC". Debuffs applied by skills with no damage component skip the Weak Hit check. — [HellHades](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- Sources disagree on whether Weak Hits also cut crit chance. One secondary guide says −15% crit chance, while HellHades lists no crit penalty for the disadvantaged side. — [web summary of HellHades/secondary affinity guides](https://hellhades.com/guide-to-affinity-raid-shadow-legends/); [HellHades 2026](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)
- Demon Lord (Clan Boss) has a base 15% C.RATE. HellHades (2026) says "Once the boss drops below 50% HP, its Affinity can change". This is new to me, so it should be verified. The traditional model is that the boss's affinity rotates daily. — [HellHades](https://hellhades.com/how-affinity-works-in-raid-shadow-legends/)

**Stat descriptions (general)**
- Great Hall / Affinity Bonus stats are HP, ATK, DEF, C.DMG, RES and ACC, which tells you which stats are scaled from base. — [Plarium forum: Basic guide to Great Hall](https://forum.plarium.com/raid-shadow-legends/673_guides-and-tutorials/594610_basic-guide-great-hall)
- ACC raises the odds of landing debuffs and RES raises the odds of resisting them. — [gamerempire stats guide](https://gamerempire.net/raid-shadow-legends-stats-guide/)

### Inferences
- **Diagnosing a failing debuffer:** check (a) affinity first, since Weak Hits block debuffs outright and no ACC fixes that, (b) ACC versus the stage's RES (target RES + about 30), then (c) the skill's base chance, which Sniper, Fearsome Presence, books and sets can raise.
- Because the damage chain is multiplicative, the lowest factor gives the most per point. That is why a 100% crit plus high C.DMG plus Decrease DEF/Weaken setup beats stacking ATK alone. Decrease DEF works through mitigation and Weaken scales final damage, so they multiply each other rather than overlapping.
- Unsourced common knowledge, not verified in this pass: C.RATE is effectively capped at 100%, so crit beyond 100% is wasted outside special passives. SPD-based champions and HP/DEF scalers ignore ATK. Treat these as background knowledge.

### Gaps
- **No verifiable DEF mitigation formula found.** HellHades omits it in the retrieved text, and no official source exists. I could not verify the commonly cited community constants (e.g. a DEF/(DEF+K) curve) and have not reported any.
- **"Turn meter fills at SPD × 0.07 per tick"** is not confirmed by any source I retrieved. It is widely repeated in the community and used by speed-tune calculators, but neither HellHades nor AyumiLove states it on the pages I read. Treat it as an unverified community model.
- No source confirmed how ties are broken when two champions have exactly the same meter.
- No source confirmed how ACC/RES are scaled for bosses. It is generally believed bosses have fixed high RES per stage.

---

## 2. Buffs, debuffs and turn-meter manipulation

### Takeaway
Most buffs and debuffs have two tiers. The key values: Decrease DEF 30/60%, Weaken 15/25%, Decrease ATK 25/50%, Decrease SPD 15/30%, Poison 2.5/5% max HP per tick, HP Burn 3% max HP, Increase ATK 25/50%, Increase DEF 30/60%, Increase SPD 15/30%, Increase C.RATE 15/30%, Increase C.DMG 15/30%, Strengthen 15/25%, Ally Protection 25/50%. Hard CC (Stun, Freeze, Sleep, Fear, Provoke) stops turns. The 2024–2026 patches added counters: Total Guard, Intercept, Immutable, Keen Sight, and boss immunities.

### Cited Findings (all values from the AyumiLove Buffs & Debuffs guide unless another source is cited — [AyumiLove](https://ayumilove.net/raid-shadow-legends-buffs-debuffs-guide/))
**Buffs**
- Increase ATK +25%/50%. Increase DEF +30%/60%. Increase SPD +15%/30%. Increase C.RATE +15%/30%. Increase C.DMG +15%/30%. Increase ACC +25%/50%. Increase RES +25%/50%.
- Strengthen: −15%/25% damage taken. Ally Protection: 25%/50% of direct damage is redirected to the caster (not self-damage or Poison). Counterattack: strikes back with the A1 at 75% damage, once per multi-hit attack. Reflect Damage: 15%/30%. Continuous Heal: 7.5%/15% max HP per turn. Revive on Death: 30% HP, 0% TM.
- Unkillable: cannot drop below 1 HP. Block Damage: immune to all damage. Block Debuffs: immune to debuffs, but instant effects such as TM reduction still apply. Shield: absorbs damage, and shield damage does not count for Lifesteal.
- Veil: cannot be single-targeted, is lost when attacking, and takes −7.5% AoE damage. Perfect Veil: not lost on attack, −15% AoE damage.
- Newer buffs: Fervor (+10% damage dealt, −10% taken), Fortify (−15%/25% enemy Ignore DEF), Shatter (+7.5%/15% Ignore DEF), Intercept (each stack blocks one CC attempt), Immutable (each stack blocks one cooldown increase; since V10.70.2, 2025-09-04, each stack fully blocks a cooldown increase — [AyumiLove 2025 notes](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)), Total Guard (blocks one instance of damage per stack; bosses ignore it), Taunt (Provoke takes priority over it), Stone Skin, Bone Armor, Life Barrier, Magma Shield, Stormcall, Lightning Orb.
- Total Guard rebalance (V11.75, 2026-09-02): "the Provoke debuff will bypass Total Guard", and Provoked champions cannot gain new Total Guard stacks at the start of their turn. — [AyumiLove Patch Notes 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- New Keen Sight buff (V11.85, 2026-10-22): attacks "always hit their intended target". — [AyumiLove Patch Notes 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)

**Debuffs**
- Decrease DEF −30%/60%. Weaken +15%/25% damage taken. Decrease ATK −25%/50%. Decrease SPD −15%/30%. Decrease ACC −25%/50%. Decrease RES −25%/50%. Decrease C.RATE / C.DMG −15%/30%.
- Poison: 2.5%/5% of max HP at the start of the target's turn. Poison Sensitivity: +25%/50% poison damage taken. HP Burn: 3% max HP to the target and its allies at turn start, one per champion. Bomb: DEF-ignoring damage when it expires. Hex: the target takes 2% (AoE) or 10% (single-target) damage when its allies are hit. Necrosis: 5% max HP per stack. Smite: the target takes 25% of its max HP when it uses an active skill.
- Hard CC: Stun (cannot act, cooldowns don't tick). Freeze (cannot act, takes 75% of incoming damage). Sleep (removed by any damage). Fear (50% chance a skill misfires and the turn is lost). True Fear (as Fear, and the failed skill also goes on cooldown). Provoke (A1 only, on the caster). Petrification (clears buffs, skips turn, takes 40% damage, +300% Bomb damage). Sheep (only the Sheep skill can be used). Fatigue (Sleep after an active skill).
- Control and anti-sustain: Block Buffs, Block Active Skills, Block Passive Skills, Block Revive, Heal Reduction (50%/100%), Leech (attackers heal 18%), Enfeeble (weak hits only), Ensnare (−50%/100% TM gain), Entangle, Nullify, Seal / Master Seal (blocks set and mastery effects, or also Blessings), Siphon, Berserk (+50% damage dealt and taken), Hunter's Gaze, Infest (50% of the dead target's max HP to the others, capped at 10% max HP on bosses), Delay.
- In 2025, a new "Activate" effect (V10.45, 2025-05-13) instantly triggers Poison/HP Burn damage. — [AyumiLove Patch Notes 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)
- Boss immunity change (V10.90, 2025-11-12): bosses are immune to Ensnare, Fatigue and Hunter's Gaze. — [AyumiLove Patch Notes 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)
- Champion AI Vol. 4 (V11.90, Nov 2026) improves auto-play targeting of [Infest]-debuffed enemies and debuff-spread skills. — [HellHades Update 11.90](https://hellhades.com/raid-update-11-90-unempowerment-wishlist-boost-ai-changes)

**Turn-meter manipulation**
- Instant effects: TM Boost (fills a share of the ally meter, e.g. Arbiter), TM Reduction (e.g. Lyssandra, Deacon Armstrong), full deplete, and Instant Turn / Extra Turn. — [HellHades: How speed works](https://hellhades.com/how-speed-works-in-raid-shadow-legends/)
- Block Debuffs does not stop instant TM reductions. Stone Skin does make the target immune to Decrease Turn Meter. — [AyumiLove Buffs & Debuffs](https://ayumilove.net/raid-shadow-legends-buffs-debuffs-guide/)
- Mastery TM effects: Timely Intervention (+20% TM when an ally drops below 25% HP), Evil Eye (−20% single-target / −5% AoE TM on the first A1 hit), Arcane Celerity (30% chance of +10% TM when the champion's debuff expires), Cycle of Revenge (50% chance of +15% TM when an ally is crit), Oppressor (+2.5% TM fill rate per active debuff, max 10%). — [AyumiLove Mastery Guide](https://ayumilove.net/raid-shadow-legends-champion-mastery-guide/)

### Inferences
- For Clan Boss and high-HP bosses, the stable damage plan is Decrease DEF 60% + Weaken 25% + poisons/HP Burn (percent max HP, independent of ATK) + Warmaster/Giant Slayer. Decrease ATK 50% is the standard survival tool.
- The 2025–2026 additions (Total Guard, Intercept, Immutable, Keen Sight, boss immunity to Hunter's Gaze, Ensnare and Fatigue) mean older guides that rely on those effects against bosses may be outdated.

### Gaps
- No source confirmed the buff/debuff slot cap. The commonly cited cap of 10 debuffs is only implied by an AyumiLove example. I found no official list of which debuffs each boss (Clan Boss, Hydra, Dragon, etc.) is immune to, beyond the V10.90 change.
- Polymorph is mentioned but not defined in the source.

---

## 3. Champion progression systems

### Takeaway
A champion's power comes from several layers, in roughly this order of impact: Rank (1–6★; 6★ needed for level 60 and full masteries) → Level 60 → Ascension (potions; some champions get a 6★ ascension stat bonus) → Skill books (Tomes for Legendary/Mythical) → Masteries (3 trees, pick 2, 15 masteries, scrolls from Minotaur) → Gear and Relics → Awakening + Blessing (Souls, from account level 42) → Empowerment (duplicates, 4 levels) → account-wide Great Hall and Faction Guardians. New in Nov 2026 (V11.90): Legendaries can be Unempowered once a month.

### Cited Findings
**Rarity and rank**
- Level cap by rank is 10/20/30/40/50/60 for ranks 1–6. Ranking up needs N fodder champions of the same rank (1×R1 → R2, 2×R2 → R3, 3×R3 → R4, 4×R4 → R5, 5×R5 → R6), and the champion drops to level 1 after ranking up. Chickens can replace fodder. Legendaries start at Rank 5 and Mythicals at Rank 6. Skill tomes must match rarity. — [HellHades New Player Guide (2024-09-30)](https://hellhades.com/raid/new-player-guide/)
- Rank caps level, and ranking up resets the champion to level 1. A commenter says XP requirements were raised by about 25–33%, so older run counts may be outdated. — [AyumiLove Leveling Guide](https://ayumilove.net/raid-shadow-legends-champion-leveling-guide/)
- Tavern QoL (V11.90): Instant Upgrade no longer selects max-level champions as food by default. — [HellHades 11.90](https://hellhades.com/raid-update-11-90-unempowerment-wishlist-boost-ai-changes)

**Ascension**
- Uses Potions from the matching affinity's Potion Keep. Since V8.50, several Ascension levels can be done at once with a slider or MAX. — [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/); [Sportskeeda 8.50 patch summary](https://www.sportskeeda.com/esports/news-raid-shadow-legends-update-8-50-0-patch-notes-improvements-champion-rebalance-and-more)
- Permanent Super Raids in Potion Keeps since V11.40 (2026-04-01). — [AyumiLove Patch Notes 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Some champions get a champion-specific "6★ Ascension bonus". Examples: Ash'Nar Dragonsoul's changed to SPD +10 (V10.40, 2025-04-02) and Androc (Alt Form) to +5 SPD (V10.55, 2025-07-03). — [AyumiLove Patch Notes 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)

**Masteries** — [AyumiLove Champion Mastery Guide](https://ayumilove.net/raid-shadow-legends-champion-mastery-guide/)
- Three trees: Offense, Defense, Support. Each has 6 tiers (Tier 1 has 2 masteries, the others 4), 22 per tree. You can activate 2 trees and pick up to 15 masteries.
- Scrolls per champion: 100 Basic (5 masteries), 600 Advanced (6 masteries), 950 Divine (4 masteries). Each scroll type unlocks after the previous one is full. Scrolls come from Minotaur's Labyrinth; stages 11–15 give the best energy-to-scroll ratio, with a team of at least level 50.
- Reset: the first is free, then 150 gems each. A gem-bought full mastery set costs about 800 gems, which AyumiLove suggests only for a level-60 champion used everywhere. HellHades also advises spending your first 800 gems on masteries for your starter or first 6★. — [AyumiLove](https://ayumilove.net/raid-shadow-legends-champion-mastery-guide/); [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/)
- Minotaur sequences end automatically once all champions are at max scroll count (V10.60, 2025-08-06). Unneeded scrolls now go to another champion (V11.40, 2026-04-01). — [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Key mastery effects:
  - **Warmaster** (T6 Offense): 60% chance of bonus damage equal to 10% of target max HP (4% vs bosses), once per skill.
  - **Giant Slayer** (T6 Offense): 30% chance per hit of 7.5% max HP (3% vs bosses). Best on multi-hit skills.
  - **Helmsmasher**: 50% chance to ignore 25% of DEF, additive with skill Ignore DEF.
  - **Flawless Execution** +20% C.DMG. **Keen Strike** +10% C.DMG. **Bring It Down** +6% damage vs higher-max-HP targets. **Methodical** +2% per A1 use, max 10%. **Kill Streak** +6% (Arena/Siege) or +3%, max 12%. **Single Out** +8% vs targets under 40% HP. **Ruthless Ambush** +8% on the first hit against each enemy. **Heart of Glory** +5% at full HP. **Stoked to Fury** +4% per debuff on self, max 12%.
  - **Lore of Steel**: basic artifact set bonuses ×1.15 (a 12% Speed set becomes 13.8%). Shield effects are not boosted.
  - **Cycle of Magic**: 5% chance each turn to cut a random cooldown by 1. **Cycle of Violence**: 30% chance to cut a cooldown by 1 when a skill deals over 30% of the target's max HP. **Lasting Gifts**: 30% chance to extend a buff by 1 turn (not Block Damage, Unkillable or Revive). **Master Hexer**: 30% chance to extend a non-CC debuff by 1 turn.
  - Accuracy masteries: **Eagle-Eye** +50 ACC, **Pinpoint Accuracy** +10 ACC, **Swarm Smiter** +4 ACC per living enemy (max 16). **Sniper** +5% debuff placement chance (non-CC). **Fearsome Presence** +5% CC placement chance.
  - Defense: **Iron Skin** +200 DEF. **Elixir of Life** +3000 HP. **Delay Death**: 0.75% less damage per hit from the same enemy, max 6%. **Retribution**: 50% chance to counterattack after losing 25%+ HP in one skill. **Deterrence**: 20% chance to counter when an ally is CC'd. **Wisdom of Battle**: 30% chance of Block Debuffs when CC expires. **Bloodthirst**: heal 10% on kill. **Spirit Haste**: +8 SPD per dead ally (max 24). **Whirlwind of Death**: +6 SPD per kill (max 18).
  - AyumiLove recommends Warmaster and Methodical for Clan Boss and dungeon bosses, and Blastproof (PvE) or Improved Parry (Arena / solo dungeon) for defense.
- Warmaster versus Giant Slayer: Warmaster for 1–2 hit skills and bosses. Giant Slayer for champions whose A1 and other skills are multi-hit. An early guide's Giant Slayer numbers were corrected to 7.5%/3%. — [HellHades Masteries](https://hellhades.com/masteries-what-are-they-and-why-are-they-so-important/)

**Awakening and Blessings**
- Both were introduced in Patch 6.0 (Sept 2022). Awakening unlocks at account level 42 with the Altar of Souls. It uses champion-specific Perfect or Split Souls, from Soulstones (Mortal / Immortal / Eternal) or the Soul Merchant (Soul Essence). Soulstones are bought with Soul Coins (from Iron Twins, selling souls, and so on), and summoning souls also costs Silver. There are 6 Awakening levels. — [HellHades Awakening preview](https://hellhades.com/raid-shadow-legends-awakening-preview-core-mechanics/); [AyumiLove Altar of Souls](https://ayumilove.net/raid-shadow-legends-altar-of-souls-guide); [web summary of the onechilledgamer awakening guide](https://onechilledgamer.com/raid-shadow-legends-champion-awakening-guide)
- Soulstone rates as listed in a possibly dated guide: Mortal 1★ 47.75%, 2★ 34%, 3★ 12%, 4★ 4%, 5★ 1.5%, 6★ 0.75%. Immortal 3★ 50%, 4★ 32%, 5★ 12%, 6★ 6%. Eternal 5★ 75%, 6★ 25%. — [web summary of awakening guides](https://onechilledgamer.com/raid-shadow-legends-champion-awakening-guide) (fan source)
- Wishlist Perfect Soul chance went from 8x to 10x (V11.65, 2026-07-02). A Wishlist Boost event (V11.90, Nov 2026) gives "x15 chance of summoning Souls from their Wishlist" across all Soulstone types, from level 42. — [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/); [HellHades 11.90](https://hellhades.com/raid-update-11-90-unempowerment-wishlist-boost-ai-changes)
- Blessings need Awakening level 1 or higher. Each Blessing has 6 levels tied automatically to Awakening level, and some have "Mid Awakening" (3+) or "High Awakening" (5+) effects. Patch 8.20 added rarity-scaled stat bonuses. The Divinities are Light, Dark, War, Chaos and Harmony, each with Rare/Epic/Legendary blessings. Rares can only use Rare blessings, Epics can use Epic or Rare, and Legendaries can use any. The first swap is free and later swaps cost gems (cheaper within the same Divinity). Page updated 2026-09-13. — [AyumiLove Blessings Guide](https://ayumilove.net/raid-shadow-legends-champion-blessings-guide/)
- AyumiLove's Boss/Dungeon blessing tiers: **S** Brimstone, Cruelty, Crushing Rend, Phantom Touch, Nature's Wrath. **A** Heavencast, Hero's Soul, Intimidating Presence, Miracle Heal, Soul Reap, Temporal Chains, Ward of the Fallen. Arena tiers: **S** Intimidating Presence, Life Harvest, Polymorph, Temporal Chains, Ward of the Fallen. — [AyumiLove Blessings Guide](https://ayumilove.net/raid-shadow-legends-champion-blessings-guide/)
- The February 2023 rebalance changed 11 Blessings, and Brimstone and Phantom Touch now need higher Awakening. Carapace was replaced by Emergency Heal in Patch 8.20 (from an AyumiLove commenter). — [HellHades Blessings Rebalance](https://hellhades.com/blessings-rebalance-raid-shadow-legends/); [AyumiLove](https://ayumilove.net/raid-shadow-legends-champion-blessings-guide/)

**Empowerment**
- Epic, Legendary and Mythical champions can be Empowered 4 times, each level costing duplicates. One-off champions use designated surrogates. Fan-site totals: Legendary/Mythical HP/ATK/DEF +40%, ACC/RES +40, SPD +15, C.DMG +30%, C.RATE +10%. Epic HP/ATK/DEF +40%, ACC/RES +40, SPD +10, C.DMG +15%, C.RATE +5%. — [AyumiLove Empowerment Guide](https://ayumilove.net/raid-shadow-legends-champion-empowerment-guide/) (verify in-game)
- **Unempowerment (V11.90, Nov 2026)** is Legendary only and costs 1 Unempowerment Coin. You hold at most one coin, it refreshes monthly and does not carry over. The champion keeps its level, rank, ascension, masteries and gear. The returned duplicates come back at Rank 5, Level 1, and do not count as new acquisitions for events or tournaments. — [HellHades 11.90](https://hellhades.com/raid-update-11-90-unempowerment-wishlist-boost-ai-changes)

**Great Hall / Affinity Bonuses, Area Bonuses, Arena**
- The Great Hall unlocks at level 6. Classic Arena medals buy permanent per-affinity bonuses to HP, ATK, DEF, C.DMG, RES and ACC, applied to base stats, ranks 0–10. Purchases cannot be reverted. — [Plarium forum Great Hall](https://forum.plarium.com/raid-shadow-legends/673_guides-and-tutorials/594610_basic-guide-great-hall); [onechilledgamer](https://onechilledgamer.com/raid-shadow-legends-great-hall-guide)
- One guide's priority order: ACC → C.DMG → RES → DEF → HP → ATK. — [gamerempire Great Hall](https://gamerempire.net/raid-shadow-legends-great-hall-guide/)
- HellHades (2023): the Great Hall is now called "Affinity Bonuses". The separate "Area Bonuses" use Live Arena crests and do not boost champions directly. — [HellHades Area Bonuses](https://hellhades.com/how-to-use-area-bonuses-in-raid-shadow-legends/)
- HellHades lists Great Hall above level 180 as an end-game marker. — [HellHades Stage of Progress](https://hellhades.com/defining-your-stage-of-raid-shadow-legends-and-progress-priorities/)

**Faction Guardians**
- Duplicate champions are slotted as Guardians to boost all other champions of the same faction and rarity. Only Legendary, Epic and Rare champions qualify, with 5 slots per rarity per faction (a French-language fan source). Bonuses are %HP, %ATK, %DEF, ACC, RES and SPD. To empower a champion you must temporarily remove it from Guardian duty. — [alucare Guardian Ring](https://www.alucare.fr/en/ring-de-gardien-raid-shadow-legends/); [AyumiLove Empowerment comments](https://ayumilove.net/raid-shadow-legends-champion-empowerment-guide/)

**Gear (relevant 2025–2026 changes)**
- Removing gear no longer costs Silver (V10.60.5, 2025-08-21). Auto-Equip (V11.50, 2026-05-06). Anomalous Accessories with unique substats, Coalescence (faction) Relics, and artifact/accessory storage up to 2200 each (V11.70, 2026-08-05). Artifact Chests give better rank and rarity (V11.80). — [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Artifacts have 1–6 stars and five rarities, and reach 4 substats at +16. Example set bonuses: Life +15% HP, Crit Damage +20% C.DMG, Speed +12% SPD. — [web summaries of artifact guides](https://ayumilove.net/raid-shadow-legends-artifact-and-accessory-guide/); [HellHades Artifact Tier List](https://hellhades.com/?p=2996)

### Inferences
- Upgrade order for a single champion, from cost and impact: 6★ + level 60 → full masteries (the T6 damage mastery or Lore of Steel/Cycle of Magic for supports) → books on the skills that matter (debuff chance and cooldown first) → gear tuned to stat thresholds (SPD, ACC versus target RES, crit 100%) → Awakening/Blessing → Empowerment. Great Hall ACC/C.DMG is the best account-wide medal spend.
- Unempowerment lowers the risk of "wrong champion empowered" mistakes for Legendaries, but only one per month.

### Gaps
- **"Arena gear bonuses"** (stat bonuses on gear from Classic Arena tier): I found no source confirming this system or giving values. It may be a misremembering of the Great Hall or Area Bonuses. Flag for the user.
- I found no exact Great Hall per-level percentages or medal costs per level, and no exact Faction Guardian per-slot values.
- No source gave the potion counts per Ascension level, or the exact book counts per skill (both depend on the champion).
- Relics as a system (introduced around 2024) are only touched on here. Another researcher may cover gear and relics.

---

## 4. Resource economy and bottlenecks

### Takeaway
The early bottlenecks are energy, XP/food, and Silver, the last of which is "hard to get early and hard to keep". The mid-game bottlenecks are skill books/tomes, masteries/scrolls, good speed/ACC gear, and Legendaries (shard luck plus mercy). The late game is limited by gear quality (6★ Legendary rolls, Fire Knight/Ice Golem/Hydra/Chimera sets), Souls for Awakening, and duplicates for Empowerment. Summoning is boosted around events (2x/15x), and mercy counters are per shard type.

### Cited Findings
- Energy regenerates passively (cap 130 at max level per HellHades). Every run costs energy whether you win or lose, so don't farm content you can't reliably clear. Early energy should go to campaign for XP. Energy refills cost 40 gems. The Gem Mine pays back in about 100 days. Don't buy shards with gems. — [HellHades New Player Guide (2024-09-30)](https://hellhades.com/raid/new-player-guide/)
- Silver: the main income is selling accessories (and artifacts). Campaign 12-3 is good early because its shields sell well, and Spider 20+ is a strong accessory/silver farm later. Only upgrade gear during Artifact Enhancement events. Buying silver with cash is not recommended. — [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/)
- Gems come from daily quests, events, Clan Boss and some Doom Tower stages. Spend them on the Gem Mine, energy refills, or the first full mastery set. — [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/)
- Mercy (pity) counters are separate for Ancient, Void and Sacred shards. Mystery shards have no mercy. Fan sources disagree on the thresholds: Ancient Legendary is put at 150, 120–150, or 200 pulls; Void at about 110, 200, or 90 (older HellHades); Sacred Legendary at 12 or 20. One source says the Epic mercy on Ancients starts after 20 pulls at +2% per shard. Pulling a Legendary resets only that shard type's counter. — [web summary of mercy guides incl. AyumiLove](https://ayumilove.net/raid-shadow-legends-mercy-system-explained/); [BlueStacks pity guide](https://www.bluestacks.com/blog/game-guides/raid-shadow-legends/rsl-pity-system-guide-en.html); [HellHades: When to pull shards](https://hellhades.com/when-is-the-best-time-to-pull-shards-in-raid-shadow-legends/) — **the exact numbers are unverified and the sources conflict.**
- Summon Boost (V11.75, 2026-09-02): regular boosts went from 10x to 15x, and Progressive Chance boosts from 15x/20x/25x to 20x/25x/30x. — [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Primal Shards exist (Mythical-focused). V10.90 (2025-11-12) added Top-500 Live Arena season rewards that include a Primal and a Void Shard. Raid Card chests (V11.40) include Void and Primal shards. — [HellHades: Primal Shards are live](https://hellhades.com/primal-shards-are-live-raid-shadow-legends/); [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Fusions: V11.30 (2026-03-04) included a "Fusion Champion change" (no details visible). — [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Collection and storage: summons can go to the Collection or the Reserve Vault, which holds 600, expandable to 1200 (V10.70, 2025-09-02). — [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)
- Soul economy: Soul Coins from Iron Twins and from selling souls. Mortal/Immortal Soulstones also yield Soul Coins at the Altar. — [web summary of Altar of Souls guides](https://ayumilove.net/raid-shadow-legends-altar-of-souls-guide)
- Clan Boss: a Chest Rewards tab was added (V10.55, 2025-07-03). The Hydra Clan Quest now only needs you to "last 100 turns". — [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/)
- Siege: Tiers 7 and 8 added (V10.55), with more than 5,000 points needed to stay in matchmaking (V11.60). — [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)
- Automation that lowers the time bottleneck: Background Multi-Battles (V11.60), Doom Tower Background Auto-Climb on regular floors (V11.50), Chimera Quick Battle (V11.65), training queue raised from 20 to 60 (V11.65), and Platinum/Diamond Raid Cards with extra Multi-Battle attempts and Sparring Pit XP (V11.40). — [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/)

### Inferences
- The 2025–2026 changes (free gear removal, Auto-Equip, background battles, larger vaults) have eased the friction and time bottlenecks. The core resource bottlenecks (energy, silver, books, Legendary luck, souls) are unchanged.
- When advising, recommend saving shards for 2x/15x summon events and tracking mercy per shard type, but don't promise specific mercy thresholds.

### Gaps
- No source confirmed the current energy cap or regen rate (HellHades' "130 at max level" may be dated). I found no official mercy numbers, no current Clan Boss chest contents per difficulty, and no tournament point values.
- I couldn't reach Reddit, so "what experienced players say" relies on HellHades' articles and their stage definitions.

---

## 5. Recommended progression roadmap (new and mid accounts)

### Takeaway
The community-standard path: pick a starter (Kael is the consensus) and get it to 60 to farm campaign → use Arbiter Missions as the roadmap → build more 6★ champions and a Clan Boss team (AoE Decrease DEF, Decrease ATK, a healer, poison/damage, speed boost) → Spider 10–15 for silver/gear and Dragon 15–17 → Brutal/Nightmare CB top chest → Faction Wars early stages, Doom Tower Normal → late game: UNM CB, dungeons 20 on fast farm, Fire Knight/Ice Golem/Hydra/Chimera, Doom Tower Hard, Faction Wars 18–21 for Lydia/glyphs.

### Cited Findings
- **Starter:** choose from Galek, Athel, Elhain, or Kael. Kael is "widely considered the best" for poison. A newer HellHades article says a new account's first 6★ should be picked from the full roster, since promo codes and events may give better options. — [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/); [HellHades: Strongest new player start](https://hellhades.com/the-strongest-new-player-start-raid-has-ever-offered/)
- Promo codes must be used before level 15 and within 72 hours of account creation. — [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/)
- "Get Your Starter to Level 60 – This is your first major goal to enable campaign farming. Don't bother ranking up other champions until this is done." — [HellHades 10 Early Game Tips](https://hellhades.com/10-early-game-progression-tips-in-raid/)
- Arbiter Missions are the roadmap for new accounts. They give the Legendary Arbiter, and Ramantu and Marius missions follow. — [HellHades New Player Guide](https://hellhades.com/raid/new-player-guide/)
- **HellHades' stage definitions** (originally published 2020-11-30, so older; the content list predates Hydra, Chimera and newer modes) — [HellHades: Defining your stage of progress](https://hellhades.com/defining-your-stage-of-raid-shadow-legends-and-progress-priorities/):
  - *Early:* 0–2 6★ champions. Priorities: "Getting more 6 star champions and building out a Clan Boss team". 3–5★ Speed/Perception/Lifesteal gear. Warmaiden (AoE Decrease DEF) as a farmer and helper.
  - *Mid:* 5–10 level-60 champions. Brutal/Nightmare CB top chest daily. Dragon 15–17 and Spider 10 (ideally 15). The first Faction Wars bosses. Silver/early Gold Arena. Start Doom Tower Normal. Move to 6★ gear with SPD/ACC.
  - *Late:* NM and UNM CB top chests daily. Dungeons 20 in under 3–4 minutes. Faction Wars stage 18 daily in every faction (6★ glyphs). Doom Tower Normal each rotation and start Hard. Drop Lifesteal for Perception/Speed/Lethal/Savage/Immunity.
  - *End:* dungeons 20/24/25 in under 2–3 minutes, a one-key UNM CB, all of Doom Tower Normal and Hard with most secret rooms, Gold Arena, Great Hall 180+, Faction Wars fully done with Lydia, possibly Platinum Arena. Energy goes mostly to Fire Knight.
  - Clan Boss team roles to prioritize for level 60: an AoE Decrease DEF champion, a Decrease ATK champion, a healer/support (e.g. Apothecary), a damage dealer (usually the starter), debuff/control (e.g. Gnarlhorn), and a speed booster.
- Spider stage 10 is an efficient early target, and Demon Lord is a priority because higher difficulties pay shards, tomes and gems. Poison champions (Kael, Venomage) and Decrease DEF/Decrease ATK are core for bosses. — [HellHades early-game articles (search summary)](https://hellhades.com/getting-started-in-raid-shadow-legends/); [HellHades Nub's Top 50 Tips](https://hellhades.com/nubs-top-50-tips-for-new-players-in-raid-shadow-legends/)
- **New content that changes the late-game map (2025–2026):** Campaign Hard Mode (V10.45, 2025-05-13). Faction Wars Hard Mode (HellHades prep guide 2025-05-23; enemy HP/ATK/DEF rebalanced for stages 1–21 in V11.80, 2026-10-08). Chimera (rebalanced V10.55). Grim Forest, an "expansive new game mode" with branching paths and new bosses (V11.00, 2025-12-10). Chaos Awakes event dungeon (V10.50). Siege Tiers 7–8. Frontier Events announced (V11.75). — [AyumiLove 2025](https://ayumilove.net/raid-shadow-legends-patch-notes-2025/); [AyumiLove 2026](https://ayumilove.net/raid-shadow-legends-patch-notes-2026/); [HellHades: Prepare for Hard Mode FW](https://hellhades.com/how-to-prepare-for-hard-mode-faction-wars-in-raid/)
- Advanced Quests' "Go" button now jumps to the latest available dungeon stage (V11.90). — [HellHades 11.90](https://hellhades.com/raid-update-11-90-unempowerment-wishlist-boost-ai-changes)

### Inferences
- A sensible advising sequence for the skill:
  1. Starter to 60 and Arbiter missions.
  2. A food-farming setup (starter on campaign; 12-3 is also good for silver from shields).
  3. 4–5 6★ champions covering CB roles (Decrease DEF, Decrease ATK, heal, poison).
  4. Clan Boss Brutal/NM, then speed-tuned UNM (DeadwoodJedi tunes).
  5. Spider and Dragon toward 20. Fire Knight and Ice Golem once there is enough damage/TM control and Freeze/Provoke resistance.
  6. Faction Wars, starting with the factions that have built champions.
  7. Doom Tower Normal → Hard.
  8. Hydra and Chimera through clan play.
  9. Grim Forest, Hard campaign and FW Hard for end-game accounts.
- This matches the "build a farmer, then a CB team, then dungeon teams" heuristic. HellHades frames it as "6★ count + CB team" first rather than as a strict farmer/CB/dungeon order.

### Gaps
- The HellHades stage article is from 2020. I found no 2025–2026 roadmap that places Hydra, Chimera, Grim Forest, Campaign Hard or FW Hard in the progression ladder. The milestone placement of those modes is my inference.
- Stage numbers of 12-3 and Dragon/Spider 20 come from older guides. Campaign Hard Mode (2025) may have changed the best farming stage. I couldn't verify a current "best XP stage" recommendation.
- I could not reach DeadwoodJedi's roadmap pages or the r/RaidShadowLegends wiki.
