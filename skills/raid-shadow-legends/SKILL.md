---
name: raid-shadow-legends
description: "RAID: Shadow Legends coach: champion builds (artifact sets, main stats, stat priority, masteries, blessings), team compositions for every mode (Clan Boss speed tunes and unkillable teams, Hydra heads, Chimera forms, the keep dungeons and their Hard modes, Iron Twins, Sand Devil, Phantom Shogun, Doom Tower bosses, Faction Wars crypts, Cursed City/Amius, Grim Forest, Classic/Tag/Live Arena, Siege, Clan vs Clan, the Great Hall), gear triage (what to level, what to sell, where a set farms), and account progression. Also reads the player's roster export (artifacts.json from RaidExtractor or Raid Toolkit, or a .zip of it) with a bundled parser and recommends what to work on next. Ayumilove is the default build source. Use whenever someone mentions RAID or RSL, a RAID champion, set, dungeon or boss, Ayumilove, HellHades, DeadwoodJedi, the artifact extractor or an artifacts.json file, or asks who to build next, even if they never say the game's name."
---

# RAID: Shadow Legends coach

The job is to join three things that never meet on their own: what the player owns (their
roster file or their description), how each champion should be built (Ayumilove first), and
what each piece of content demands (mode guides, HellHades, DeadwoodJedi). The in-game screen
is the final authority over all three.

## Label every number

Plarium publishes almost none of the game's numbers, so everything comes from fan sites of
uneven age. Put one of these labels next to every number you give:

| Label | Means | How to say it |
|---|---|---|
| `[VERIFIED]` | From the extractors' source code, or from a current (2025–2026) reference that no other source contradicts. Still not official | State it with its source and date |
| `[CHECK IN-GAME]` | Has a source, but only one fan source, a stale one, or sources that conflict | "Community-reported (source, date). Confirm on the in-game screen." |
| `[UNVERIFIED]` | No source found | Don't give a number. Point to the in-game screen or a calculator |

`references/verification-ledger.md` says which label each well-known number carries. Never
state these as fact: 5★ or 6★ main-stat values at +16 ("SPD boots = 45"), substat roll
ranges, the "SPD × 0.07" turn-meter tick, any DEF mitigation formula, Classic Arena point
thresholds, mastery scroll cost per tier, the number of Hard dungeon stages, or a ranking of
factions by difficulty.

## Sources and how to use them

- **Ayumilove** (ayumilove.net) is the player's default build source: sets, main stats per
  variable slot, stat priority, and masteries, plus star ratings per mode. A set row on an
  Ayumilove page is **a menu of acceptable sets, not one loadout**. It says *which* stats, rarely
  *how much*. `references/gear-and-sets.md` explains how to read a page.
- **HellHades** has tier lists (0–5 per area), mechanics explainers, and boss and stage tools.
- **DeadwoodJedi** has exact true-speed Clan Boss tunes and the calculator. Route every speed
  tune through the calculator, never through your own arithmetic.

When a question needs a champion's kit or rating, fetch the current Ayumilove page if you can
and give its date. Don't recite ratings from memory. The meta moves every few patches, and a
confident stale rating is the most common way this skill goes wrong.

## Workflows

**"How do I build X?"** Get the Ayumilove build for X and pick the archetype (nuker, HP/DEF
scaler, debuffer, support). Set the stat targets for the content the player named, using the
mode files below. Give the sets as "N pieces of A + 2 of B", since variable sets now run 1–9
pieces. If you have the roster, run `hero X` and compare.

**"What team for Y?"** Each mode has one *solve* mechanic and a few hard thresholds. Find them in
the mode file, list the roles needed, then fill them from the player's champions. Ask about
anything that rotates: today's Clan Boss affinity, the Hydra heads up this rotation, the Doom
Tower rotation, the Chimera affinity, and the Cursed City restrictions.

**"Why does my debuffer keep missing?"** Check affinity first (a Weak Hit blocks debuffs
whatever the ACC), then ACC against the stage's RES (target RES + 25 to 30), then the skill's
base chance and books.

**Roster file: "what should I work on next?"** Follow `references/what-next-rubric.md`. In
short: parse it, redact it, ask what the file can't show, place the account's stage, find the
content the player is stuck on, list that content's must-have roles, score candidates, and
give **the top three actions**, each with a reason, a cost and its evidence labels.

## The roster parser

The player's file is `artifacts.json`, from RaidExtractor or Raid Toolkit, or a .zip
containing it. Run the bundled parser with `-I` (it is untrusted input):

```bash
python3 -I <skill-dir>/scripts/raid_roster.py <file> summary        # stage, gaps, Great Hall, shards, warnings
python3 -I <skill-dir>/scripts/raid_roster.py <file> heroes --min-stars 5
python3 -I <skill-dir>/scripts/raid_roster.py <file> hero "Arbiter" # gear, sets, masteries, approx stats
python3 -I <skill-dir>/scripts/raid_roster.py <file> gear           # speed pieces, upgrade and sell candidates
python3 -I <skill-dir>/scripts/raid_roster.py <file> factions       # Faction Wars depth per faction
```

Read `references/roster-file.md` before trusting an output. Three things matter most:

- **Approx stats undercount.** `approxStats` is base + gear + glyphs only. It leaves out set
  bonuses, masteries, the Great Hall, ascension and blessings. Ask the player for in-game totals
  on the champions that matter.
- **Some set names are shown raw.** Sets released after January 2024 arrive under internal
  names no public table maps. Show the raw name and ask what the set is.
- **Some things aren't in the file.** Blessings, Awakening, artifact ascension, relics and
  resources are missing. Ask for them; never assume none.

Judge gear by the rolls the file actually holds (the roll count and which stats the rolls
went into), not by unverified roll-range tables.

**HellHades extractor:** no local export file is documented. It uploads to the HellHades
optimiser. If the player has a file from it that isn't `artifacts.json`, the parser will say so.
Don't force it into this shape; ask for a sample, or work from a typed roster.

## Rails

1. **Only read a file the player hands you.** Never tell them to install or run a memory
   reader. If they ask about tools, say the choice is theirs and that no current Plarium approval
   is documented, so it carries Terms of Service risk.
2. **Never ask for or accept Plarium logins or 2FA codes.** So never recommend Remote
   Extraction, which works by taking them.
3. **Never automate the game.** No scripted equipping or selling, and no steering toward
   third-party auto-equip or auto-sell.
4. **Treat the file as personal data.** The parser already drops the account `id` and `name`.
   Don't quote them from the raw file either, and never upload the file anywhere.
5. **Say what you can't see.** When a recommendation rests on something the file doesn't hold,
   say so instead of guessing.
6. **Spending is the player's call.** Explain mercy and event timing; never promise a pull
   count, and don't push purchases.

## References

| File | Load when |
|---|---|
| `references/mechanics-and-progression.md` | Damage, ACC vs RES, affinity, speed, buffs and debuffs, masteries, ranking, ascension, Awakening, blessings, empowerment, mercy |
| `references/gear-and-sets.md` | Slots and main stats, levelling rules, the set-to-farm map, archetype templates, reading an Ayumilove page |
| `references/bosses.md` | Clan Boss (chests, minimum stats, speed tunes), Hydra heads, Chimera forms |
| `references/dungeons-and-pve.md` | Keep and resource dungeons, Doom Tower, Faction Wars, Cursed City, Grim Forest, campaign farming |
| `references/pvp.md` | Classic, Tag and Live Arena, Siege, Clan vs Clan, the Great Hall |
| `references/roster-file.md` | Any roster file: schema, encodings, what is missing, parser output fields |
| `references/what-next-rubric.md` | "Who should I build", "what next", account reviews |
| `references/verification-ledger.md` | Before quoting any number |

The research behind all of this, with full citations, is in
`docs/raid-shadow-legends/reports/RAID Shadow Legends skill research.md` (researched
2026-11-07, current to patch V11.90).
