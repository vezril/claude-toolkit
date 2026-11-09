# Dungeons and other PvE

## Keep and resource dungeons

**From stage 21 up**, every classic boss caps Max-HP damage at 10% of its HP and halves Turn
Meter reduction. That favours HP Burn, poison, and Decrease DEF + Weaken over Max-HP nukers and
meter control.

**Hard modes** arrived in Patch 6.51.1 (2023-03-09). They use "Tainted" bosses, can drop
Mythical artifacts, and several scale with Awakening. The Hard stage count, commonly said to be
10, is `[UNVERIFIED]`.

| Dungeon | Stages | Drops | The solve | Sourced numbers |
|---|---|---|---|---|
| Dragon's Lair (Hellrazor) | 25 + Hard | Speed, ACC, Lifesteal and others (see gear-and-sets) | Decrease ATK; burst the purple bar before Scorch | ~300 RES cited for stage 20 `[CHECK IN-GAME]` |
| Ice Golem's Peak (Klyssus) | 25 + Hard | Reflex, Retaliation, Cursed and others | Block Revive, or poison/HP Burn to avoid triggering thresholds | HellHades rates it Hard |
| Fire Knight's Castle (Fyro) | 25 + Hard | Savage, Regeneration, Stun and others | Multi-hit A1s to break a shield needing 12 hits at stages 21–25 | Rated Very Hard |
| Spider's Den (Skavag) | 25 + Hard | All accessories | AoE nuke early; HP Burn at 21–25 | ACC ≈ RES + 25 (cap 225); RES ≈ boss ACC + 100 (cap 300); stage 20 has 200/200 `[VERIFIED]` |
| Minotaur's Labyrinth | 15 | Mastery scrolls | Cleanse or block the Hex | Stages 11–15 most efficient. Super Raids since V10.60; spare scrolls redirect to other champions since V11.40 |
| Iron Twins Fortress | 15; affinity changes daily | Soul Coins / Essence (Awakening) | Single-hit nukes; Decrease SPD; poison is 90% less effective | SPD/ACC/RES bands below `[VERIFIED]` |
| Sand Devil's Necropolis (Al-Naemeh) | 25 (level 38) | Artifact Oil (gear ascension) | Mechanics not retrieved | Stage 7 Lesser, 24 Greater, 25 Superior Oil. Rebalanced June 2024 |
| Phantom Shogun's Grove (Akumori) | 25 (level 38) | Accessory Extract; Chaos Powder at 25 | Awakened champions; Affinitybreaker; cleanse the spreading Enfeeble | 350 base SPD; Arbiter for the opener |

**Iron Twins stat bands** are the cleanest stage picker in the game. Compare them with the
roster's SPD/ACC/RES:

| Stages | SPD | ACC | RES |
|---|---|---|---|
| 1–6 | 150 | 150 | 205 |
| 7–12 | 220 | 275 | 355 |
| 13–15 | 250 | 375 | 505 |

A 50% Increase ACC or Decrease ACC cuts the ACC and RES requirements by a third to a half.

**Potion Keeps** (Arcane, Magic, Force, Spirit, Void) supply the potions for ascension, and
their Super Raids have been permanent since V11.40. Their stage tables and open days weren't
retrieved, so ask the player or check in-game.

**Kuldath is a Doom Tower boss, not a dungeon.**

## Doom Tower

**Structure.** 120 floors plus 12 secret rooms, in each of Normal and Hard. A boss guards every
10th floor. The tower resets every 30 days on a three-rotation boss cycle.

**Keys.** Golden Keys open floors; Silver Keys open secret rooms and boss replays. Both cap at
10, reset at 00:00 UTC, and are spent only on a clear.

**Secret rooms.** First clears give Epic fragments on Normal and Legendary fragments on Hard.

| Boss | Rotation(s) | Solve | Forge set |
|---|---|---|---|
| Kuldath, Magma Dragon | 1, 2 | Provoke, to control his Hex | Fatal |
| Agreth, Nether Spider | 1, 2 | Cleansing (RES and Block Debuffs don't help; its poisons can't be resisted) | Affinitybreaker |
| Sorath, Frost Spider | 1 | HP Burn on revive, or Block Revive | Frostbite |
| Borgoth, Scarab King | 1, 3 | Max-HP destruction plus Shields (Urost can solo-farm) | Untouchable |
| Iragoth, Eternal Dragon | 2 | A1-only play, or high RES | Bloodthirst |
| Grythion, Celestial Griffin | 2, 3 | A fast kill before the enrage | Guardian |
| Bommal, Dreadhorn | 3 | Decrease ACC | Fortitude |
| Astranyx, Dark Fae | 3 | Mirror-aware team. Hard wants SPD 250+, ACC 355+, RES 375+; Holsring, Hegemon, Gnut and Acrizia cited | Lethal |

Sources disagree on which boss sits in which rotation, so **ask which rotation is live**.
InTeleria's "250 ACC for Sorath" is `[CHECK IN-GAME]`. Doom Tower farming follows the forge
set the player wants.

## Faction Wars

**Structure.** Each faction crypt has 21 stages, with Crypt Keeper bosses at 7, 14 and 21.

**Stars:** 1★ for a clear, 2★ with at least three champions alive, 3★ with all five alive.

**Rewards:**

- Full 3★ on Normal unlocks **Lydia the Deathsiren**.
- Full Hard unlocks the Mythical **Polara Fireheart**.

**Hard mode** was added in V10.45 (2025-05-13) and eased twice: V11.80 lowered enemy stats on
stages 1–21, and V11.90 relaxed four challenge conditions.

**The roster file is unusually useful here.** The parser's `factions` output shows how many
"ready" champions each faction has, so the skill can say which crypts can field five and which
can't. It can't tell whether those five include the counter role; check that against this
table:

| Keeper | Threat | Counter | Stage-21 boss in |
|---|---|---|---|
| Red / Dueler | Stuns all but one with unresistable Stun and True Fear | Block Debuffs or cleanse, plus a healer | Dwarves, Lizardmen, Undead Hordes, Shadowkin |
| Purple / Mirrorer | Fear, buff steal, HP swap every 12 turns | High RES; kill the minions, then burst | Skinwalkers, Knights Revenant, Orcs |
| Blue / Protector | Minions hit based on the target's HP | Control the minions but don't kill them | Banner Lords, Sacred Order |
| Yellow / Disruptor | Provoke, True Fear, Freeze passive | Block Debuffs, cleanse or RES | High Elves, Barbarians, Demonspawn |
| Green / Incinerator | Poison, Turn Meter reduction, HP Burn | Block Debuffs, cleanse, a strong healer | Ogryn Tribes, Dark Elves, Sylvan Watchers |

No sourced ranking of the hardest factions exists `[UNVERIFIED]`. Difficulty is roster-
dependent, which is exactly what the `factions` output shows.

## Rotating endgame modes

**Cursed City** (Patch 8.0, level 52):

- 101 floors per difficulty, with monthly-rotating champion restrictions (ask what they are).
- The end boss is the Mythical **Amius**. Amius Hard has 450 RES and needs about 500 ACC
  `[VERIFIED]`.
- Drops the Supersonic and Merciless sets.

**Grim Forest** (V11.00, 2025-12-10, level 55):

- A roguelite deck mode of 400+ stages that reshuffles every 30 days, with 30 Distorted Energy a
  day.
- Hard needs 40 champions across two decks. The Normal deck size is given as both 10 and 20,
  unresolved.
- The final boss Leshun is easy alone and hard with its four guardians alive.
- Rewards: Anaxia the Reborn fragments, the Mercurial set, Bloodbriar relics.
- It's a breadth test, so a roster with many mid-built champions does better than one with a
  few maxed.

**Champion Proving Grounds:** a 27-stage rotating dungeon that drops Anomalous Accessories. It's
described only by an undated test-server article, so label it unconfirmed.

## Campaign farming

- **Brutal 12-3** is still the standard XP and Silver stage.
- Energy per run: 4 / 6 / 8 / 16 for Normal / Hard / Brutal / Nightmare.
- XP is split evenly across the team, so the advice is one farmer plus food.
- Campaign Hard Mode now exists; the research didn't find whether a better XP stage has
  emerged, so ask what the player farms.
- Removing gear is free since V10.60.5, which makes farmer swaps costless.
- Super Raids (Feb 2025), background multi-battle (Mar 2025) and Platinum/Diamond Raid Cards
  (Apr 2026) cut the grind.

The common food farmers (Kael, Gorgorab, Lord Shazar, Ninja) and the Chicken/XP Brew
mechanics weren't confirmed in this research. Hedge any claim about them.
