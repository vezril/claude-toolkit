# Mechanics and progression

## Combat

**Damage is a product, not a sum.** HellHades' community model multiplies these factors in
turn:

- the scaling stat: ATK, or HP or DEF for champions that scale on those
- the skill multiplier
- the book bonus
- the crit multiplier, (1 + C.DMG)
- masteries
- affinity
- buffs and passives
- DEF mitigation

Because it's a product, the weakest factor gains the most per point. That's why 100% C.RATE
plus high C.DMG, with Decrease DEF and Weaken on the target, beats stacking ATK. Decrease DEF
and Weaken multiply each other rather than overlapping. Damage-reduction passives also stack
multiplicatively. Describe DEF qualitatively, with diminishing returns. **Don't compute
damage after DEF.** No formula is verified.

**Landing debuffs** `[VERIFIED]`:

- Equal ACC and RES lands about 90% of debuffs.
- ACC 30 above RES lands about 97%.
- RES 100 above ACC resists about 90%.
- Unless a skill says "cannot be resisted", there is always at least a 3% chance it's resisted.

The skill's own chance is rolled before ACC vs RES. The default target is **the target's RES +
25 to 30**. Specific modes repeat this margin:

- Chimera: ACC above its RES by 25; RES above its ACC by 125 to resist it.
- Spider: about RES + 25, capped at 225.

**Affinity** `[CHECK IN-GAME]`. Magic beats Spirit, Spirit beats Force, and Force beats Magic.
Void is neutral.

- **Strong side:** +15% C.RATE and a 30% chance of a Strong Hit, worth +30% (non-crits only).
- **Weak side:** −20% damage and a 35% chance of a Weak Hit, a further −30% that **also blocks
  that hit's debuffs regardless of ACC**.
- **Skills with no damage** skip the Weak Hit check.

For a debuffer that "keeps missing", check in this order: affinity, then ACC vs the stage's RES,
then the skill's base chance and books.

**Speed.** The turn meter fills in proportion to SPD, and whoever is furthest past 100% acts
first. Set bonuses create hidden decimal speed, so two champions showing the same SPD can act in
different orders. DeadwoodJedi therefore lists **true speed** and converts with its calculator.
There is no speed cap; Arena speeds around 350 are normal. **Never simulate turn order
yourself.** Send tunes to the DeadwoodJedi calculator, which also warns against turn-meter and
cooldown masteries in fixed tunes (Cycle of Magic, Lasting Gifts).

## Buffs and debuffs `[VERIFIED]` (Ayumilove)

| Effect | Value | Effect | Value |
|---|---|---|---|
| Decrease DEF | −30% / −60% | Increase ATK | +25% / +50% |
| Weaken | +15% / +25% damage taken | Increase DEF | +30% / +60% |
| Decrease ATK | −25% / −50% | Increase SPD | +15% / +30% (doesn't stack) |
| Decrease SPD | −15% / −30% | Increase C.RATE / C.DMG | +15% / +30% |
| Poison | 2.5% / 5% max HP per tick | Strengthen | −15% / −25% damage taken |
| HP Burn | 3% max HP, one per champion | Ally Protection | 25% / 50% redirected |

Patch changes that invalidate older guides:

- **Total Guard:** each stack blocks one instance of damage, debuffs, CC or buff removal.
  Bosses ignore it, and since V11.75 (2026-09-02) Provoke bypasses it.
- **Intercept** blocks crowd control.
- **Immutable** blocks cooldown increases, fully so since V10.70.2.
- **Keen Sight** arrived in V11.85 (2026-10-22).
- **Boss immunities:** Berserk since V10.10; Ensnare, Fatigue and Hunter's Gaze since V10.90
  (2025-11-12).

## Masteries

There are three trees: Offense, Defense and Support. A champion uses two trees, for 15
masteries in total. A full set costs 100 Basic, 600 Advanced and 950 Divine scrolls, which come
from Minotaur. The first reset is free; later resets cost 150 gems `[VERIFIED]`. Cost per
individual mastery is `[UNVERIFIED]`.

The four that carry PvE:

- **Warmaster:** a 60% chance to deal 10% of the target's max HP, 4% against bosses, once per
  skill.
- **Giant Slayer:** a 30% chance *per hit* to deal 7.5%, 3% against bosses. It suits multi-hit
  skills.
- **Lore of Steel:** multiplies basic set bonuses by 1.15. It goes on supports and set-reliant
  builds.
- **Eagle-Eye:** +50 ACC.

Hydra caps Warmaster and Giant Slayer at 50,000 per hit.

The roster parser decodes mastery ids. The id is `500<tree><tier><n>`, with tree 1 Offense, 2
Defense and 3 Support. So 500161 is Warmaster, Offense tier 6.

## Champion progression

Each layer is costed separately, cheapest first:

1. **Rank** caps the level at 10/20/30/40/50/60 for ranks 1–6. Ranking up takes same-rank
   fodder (1 for R2, up to 5 for R6) and resets the champion to level 1. Legendaries start at
   R5 and Mythicals at R6 `[VERIFIED]`.
2. **Ascension** uses affinity potions from the Potion Keeps, which have had permanent Super
   Raids since V11.40. The roster file's `typeId % 10` gives the ascension stars.
3. **Masteries**, as above.
4. **Books** on the skills that carry a debuff chance or a cooldown. Legendaries use tomes.
5. **Gear** tuned to the content's thresholds.
6. **Awakening** (Souls, from account level 42) and **Blessings** (five Divinities, with levels
   tied to Awakening). Both arrived in Patch 6.0 (Sept 2022). **Neither is in the roster file.**
7. **Empowerment** spends duplicates over four levels `[CHECK IN-GAME]` totals. New in V11.90:
   a Legendary can be Unempowered with one coin a month; the coin doesn't carry over, and the
   copies come back at R5 level 1.

Account-wide layers: the **Great Hall**, now called "Affinity Bonuses" (see `pvp.md`), and the
**Faction Guardians**.

HellHades' early rule: get the starter to level 60 before ranking anyone else.

## Economy and bottlenecks

- **Early:** energy, XP and Silver.
- **Mid:** books, mastery scrolls, SPD and ACC gear, Legendaries.
- **Late:** 6★ gear rolls, Souls and duplicates.

**Mercy** `[CHECK IN-GAME]`, from Ayumilove (Sep 2026). Each shard type and rarity has its own
counter. Other fan sources disagree, and Plarium has published nothing.

| Shard | Threshold | Then per pull |
|---|---|---|
| Ancient / Void Epic | 20 | +2% |
| Ancient / Void Legendary | 200 | +5% |
| Sacred Legendary | 12 | +2% |
| Primal Legendary | 75 | +1% |
| Primal Mythical | 200 | +10% |

Base rates (same source): Ancient and Void are 0.5% Legendary and 8% Epic; Sacred is 6%
Legendary; Primal is 1% Legendary and 0.5% Mythical. Saving shards for boosted events pays;
V11.75 raised regular boosts to 15x. **Never promise a guaranteed pull.**

**Recent quality-of-life changes:**

| Patch / date | Change |
|---|---|
| Feb 2025 | Campaign Super Raids |
| Mar 2025 | Background multi-battle |
| V10.60.5 | Removing gear became free |
| V11.40 | Potion Keep Super Raids made permanent |
| V11.50 (2026-05-06) | In-game Auto-Equip |
| V11.70 | Storage raised to 2,200; Anomalous Accessories added |
