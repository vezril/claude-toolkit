# PvP and clan competition

PvP advice from before 2025 is history. Date every meta claim.

## Classic Arena

**How it runs:**

- Asynchronous. Each player sets one defense team.
- Weekly reset: Monday 08:00 UTC.
- Tokens regenerate at 1 per hour, up to 10.
- Fewer than 20 offense battles in a week drops you one tier. 30 days without offense makes you
  Unranked.

**Platinum:**

- The top 500 worldwide. Since 10.80.0 its cutoff has been Sunday 21:00 UTC.
- The only source of the Swift Parry and Deflection gear.

**Rewards.** Wins pay Great Hall medals and Magisteel; Bronze, Silver and Gold tiers pay their
matching medals. The file's `arenaLeague` gives the tier (e.g. `GoldIV`).

**Unknown numbers.** Per-tier point thresholds, weekly reward tables and tier stat bonuses are
`[UNVERIFIED]`. Gold V appears as both 3,200 and 3,500 points `[CHECK IN-GAME]`.

**Archetypes** (HellHades, March 2026):

| Archetype | Shape | Notes |
|---|---|---|
| Speed | Booster, SPD aura lead, control, nuker | The right start for new players |
| Blender | AoE damage team | |
| Go-2nd | Stoneskin, Chronophage, Feral or Mercurial | Beats speed teams |
| Cut-in | Supersonic | Beats boosters |
| Stall / revive | Revivers and sustain | |

Speed matters less in Platinum. Arbiter's +30% SPD aura is Arena-only and doesn't apply in
Siege.

**Ayumilove's free-to-play team:** High Khatun or Spirithost, then Warmaiden, Kael or Athel,
and Berserker.

## Tag Team Arena

Three defense teams, and you win two of three. Unlocks at level 35. There's no Gold V or
Platinum. It pays Gold Bars for skill tomes, fragments and Forge materials, and its tokens are a
Clan vs Clan point source.

## Live Arena

**Format.** A real-time draft: alternating picks, one ban each, then leaders. From Gold
upward every pick must be unique.

**Seasons `[VERIFIED, Mar 2025]`:**

- Unlocks at Gold I (2,700 points). Seasons run four weeks on, two off.
- A win is +9 season points and a loss −3.
- The top milestone is 1,320 points, for 100 Mythical relic fragments, then a chest every 175
  points.
- 10 free battles a day; after 3 losses you're served a bot.

**Rewards:** Area Bonus medals, plus the Zeal, Impulse, Stonecleaver and Rebirth sets.

**Meta, early 2026: Mercurial.**

- A 9-piece Mercurial set gives 3 Total Guard stacks at round start. Each stack blocks damage,
  debuffs, CC or buff removal.
- **Counters:** multi-hit skills, counterattacks, Reflect, ally attacks, Increase Skill
  Cooldown. Since V11.75, Provoke also bypasses Total Guard.
- **Highlighted core:** Bayek on Mercurial with Fabian, Galleus and Karnage. Nais the
  Shadowthief was also prominent.
- **Typical bans:** Arbiter against speed teams, Fabian against cut-in teams.

Treat all of this as dated and check for nerfs.

**Not captured:** pick order, timers, and how opponent speed is shown.

## Siege

**Schedule** (Patch 9.0, July 2024). Runs every two weeks: 12 days of prep, then a two-day
battle on Tuesday and Wednesday.

**Entry requirements:** 15 members at level 45, 50 activity stars, 5 defense teams.

**The map:**

- A Stronghold.
- Defense Towers holding 2–4 teams each.
- 18 Posts, each with 3 random Conditions.
- Mana Shrines, which have decided recent wars.

**Winning.** You need more Victory Medals than the other clan, plus the enemy Stronghold.

**It rewards breadth.** "You can't plug in 350-speed Arbiter and call it a day". One clan used
47 champions across 20 battles.

**Rewards:** Authoratrix Lamasu fragments (scaled by Siege tier), the Feral set, and the best
source of clan relic fragments.

## Clan vs Clan

Runs about every second week, and the doubled activities rotate. Save books, ascensions, 6★
rankings, Great Hall medals and Tag Team tokens for the tournament window. HellHades' point
values date from 2021, so point the player to the in-game Objectives tab.

## The Great Hall ("Affinity Bonuses")

Classic Arena medals buy permanent bonuses per affinity:

- HP%, ATK%, DEF%, C.DMG, RES and ACC, but **no SPD or C.RATE**.
- 10 levels per track, 24 tracks, so 240 levels total.
- Unlocks at level 6. Upgrades can't be undone.

The wiki's 2022 table `[CHECK IN-GAME]`:

- Level 10 gives 20% HP/ATK/DEF, 25% C.DMG, and 80 RES and ACC.
- Costs run Bronze for levels 1–3, Silver for 4–6, and Gold for 7–10.
- 1 Gold = 2 Silver; 1 Silver = 2 Bronze.

**Priority.** Every source starts with **ACC** on the affinities of the player's debuffers.
HellHades' Clan Boss advice is then DEF. Past that, sources differ, so tie it to the player's
team.

The parser's `summary.greatHall` shows the levels per affinity and stat, and the total. The
HellHades end-game marker is about 180+.
