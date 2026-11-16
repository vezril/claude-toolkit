# Gear and sets

## Slots and main stats `[VERIFIED]`

| Slot | Main stat |
|---|---|
| Weapon | Flat ATK only |
| Helmet | Flat HP only |
| Shield | Flat DEF only |
| Gloves | C.RATE, C.DMG, ATK%, HP%, DEF%, or flat |
| Chest | ACC, RES, ATK%, HP%, DEF%, or flat |
| Boots | **SPD**, ATK%, HP%, DEF%, or flat. The only slot where SPD can be a main stat |
| Ring | Flat stats |
| Amulet (`Cloak` in the file) | C.DMG or flat |
| Banner | ACC, RES or flat |

Gloves, Chest and Boots are the "bottom row". A flat main stat there is almost always a sell.

**Rarity** sets the number of starting substats: Common 0, Uncommon 1, Rare 2, Epic 3,
Legendary 4, and Mythical 4 with one already upgraded. **Rank** (stars) sets the size of every
value. Levels run to +16, and a substat is added or upgraded at +4, +8, +12 and +16.

**Values you can't quote.** The full 5★/6★ main-stat table and the substat roll ranges are
`[UNVERIFIED]`. The only sourced data point is DEF% boots (4%→30% at 3★, 6%→40% at 4★). An
Ayumilove page that looks like a 5★–6★ table is about a different game, Awaken Chaos Era, so
don't use it. With a roster file you don't need the tables: judge a piece by its actual values,
the number of rolls that went into useful stats (`rolls` in the parser output), and its rank.

**Gear Ascension** (Dec 2022) adds a bonus stat. It needs Rank 4+ and level 12+ gear and costs
Oils (Sand Devil) and Extracts (Phantom Shogun), not Silver. It is **not in the roster file**.

**Glyphs** replace rather than stack, and every value in a glyph's range is equally likely. The
ranges themselves are `[CHECK IN-GAME]`. In the file a glyph is `enhancement`, and the parser's
`total` already includes it.

## Levelling rules

These are HellHades' operational rules, safe to repeat:

- Take Rare gear to +8. Continue to +12 only if it rolled into useful stats.
- One useful SPD roll is useful. Three or four SPD rolls make a piece "account-defining": level
  it, glyph it, and plan builds around it.
- Chaos Ore only goes on pieces with 3–4 rolls in one substat.
- Upgrade odds fall steeply toward +16 `[CHECK IN-GAME]`, so don't push junk to 16.

**Sell triage.** The parser's `sellCandidates` uses a 2021 community rule set (HellHades,
MurderInc, Chosen):

- under 5★
- Epic or Legendary with no SPD substat
- a flat main on the bottom row

It only flags unequipped, non-Mythical pieces. Present the list as a starting point, because
the rules predate variable sets and gear ascension. Keep a speed-set piece with SPD subs as a
possible arena-lead piece even if a rule flags it.

## Where each set farms

From Ayumilove's artifact guide, updated 2026-09-13. Use it to turn "I need set X" into "farm
Y".

| Source | Sets |
|---|---|
| Dragon's Lair | Speed, Accuracy, Lifesteal, Destroy, Toxic, Frost, Daze, Avenging, Stalwart |
| Ice Golem's Peak | Life, Offense, Defense, Critical Rate, Resistance, Retaliation, Reflex, Cursed, Taunting |
| Fire Knight's Castle | Critical Damage, Fury, Curing, Immunity, Shield, Frenzy, Regeneration, Stun, Savage |
| Spider's Den | Accessories (all classic accessory sets) |
| Clan Boss chests | Cruel, Immortal |
| Classic Arena | Divine Life / Offense / Critical Rate / Speed; Refresh and Cleansing accessories (Bazaar) |
| Forge, from Doom Tower boss materials | Fatal, Untouchable, Affinitybreaker, Frostbite, Guardian, Bloodthirst, Lethal, Fortitude |
| Forge, from Faction Wars / Forge Pass | Resilience, Perception; Bolster, Defiant, Killstroke, Righteous, Instinct, Slayer |
| Live Arena | Impulse, Zeal (2-piece since 8.40); Stonecleaver, Rebirth (seasonal); Swift Parry, Deflection (variable since V11.30) |
| Hydra chests | Stoneskin, Protection (variable) |
| Cursed City | Supersonic, Merciless (variable) |
| Siege | Feral (variable) |
| Grim Forest | Mercurial (variable, V11.00) |
| Event dungeons | Pinpoint, Chronophage (variable) |
| Champion Proving Grounds | Anomalous Accessories (V11.70; the mode itself is unconfirmed) |

**Variable sets** count both artifacts and accessories, from 1 to 9 pieces. Express builds as
"N pieces of X + a 2-piece Y", not as the old 4+2.

**Dated changes:**

| Patch | Change |
|---|---|
| 7.21 (2023) | Proc sets reworked (Retaliation, Fury, Curing and others) |
| 8.40 | Impulse and Zeal became 2-piece |
| Aug 2024 | Feral added |
| V10.70.2 | Chronophage rebalanced |
| V11.00 | Mercurial added |
| V11.30 | Swift Parry and Deflection became variable |
| V11.75 | Mercurial's Total Guard nerfed; Provoke bypasses it |

**Known errors on Ayumilove:** its tier list's Mercurial anchor points at Merciless, and its
Stoneskin per-piece values contradict each other.

**The parser's set names are inferred** (see `roster-file.md`). Classic sets are high
confidence. Savage/Cruel, Stoneskin, Perception, Frostbite and Bloodthirst are medium.
Post-January-2024 sets show up as raw internal strings.

## Archetype templates

These are a synthesis of slot rules and stat priorities, not quoted prescriptions. An Ayumilove
page for the specific champion overrides them.

| Archetype | Gloves | Chest | Boots | Amulet / Banner | Priority |
|---|---|---|---|---|---|
| ATK nuker | C.RATE (C.DMG once crit is capped) | ATK% | SPD | C.DMG / ATK | 100% C.RATE, then C.DMG and ATK |
| HP or DEF scaler | C.RATE | HP% / DEF% | SPD | C.DMG / HP or DEF | Same, on the scaling stat |
| Debuffer | HP% / DEF% | ACC (or a % stat once ACC is met) | SPD | flat / ACC | ACC to the threshold, then SPD |
| Support / tank | HP% / DEF% | HP% / DEF% / RES | SPD | flat / HP, DEF or RES | SPD, then survivability |

## Reading an Ayumilove champion page

The pages follow a fixed template; the Arbiter page, updated 2026-10-18, is an example. In order:

1. Header: faction, rarity, role, affinity.
2. Blessing recommendations.
3. 5-star ratings per mode: campaign, Arena offense and defense, each clan boss, Faction Wars,
   each dungeon and its Hard version, the Potion Keeps, Doom Tower floors and bosses.
4. Skills with multipliers.
5. The **build block**: set lists split into PvE, PvP and "PvE & PvP"; the main stat for each
   variable slot; stat priority grouped by role; and relics.
6. **Masteries**: separate PvP and PvE tables.

Rules for using it:

- A set row is **a menu**: any listed set works. Pick the one the player can actually assemble
  from their inventory (`gear` and `hero` outputs).
- The page gives *which* stats, rarely *how much*. Take the thresholds from the mode files.
- Pages carry an "updated" date. Give it, and prefer the current page over memory.
- Don't copy page text into answers. Summarise it and link the page.

## Third-party optimisers

The HellHades optimiser lets you set minimum stats, require or exclude sets, and choose which
gear it may use. It ranks by "highest damage", "highest overall" or effective HP, and its
scoring formula is unpublished. In-game Auto-Equip (V11.50) is Plarium's own feature and is
fine to suggest. Never suggest third-party tools that write to the game.
