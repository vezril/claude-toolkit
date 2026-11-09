# "What should I work on next?"

HellHades publishes the inputs, but not a formula. Its tier list rates champions 0–5 per area
and says the scores are "not set in stone". Its optimiser's scoring is unpublished, and its
"account assessment" is a paid human coaching service. So this skill runs **its own stated
rubric**, and says it isn't HellHades'.

## 1. Intake

Run the parser's `summary`, `heroes --min-stars 4` and `gear`. Then ask for what the file can't
show, in one message, without an interrogation:

- What content are you stuck on, or what's your goal? (e.g. UNM Clan Boss, Dragon 25, Faction
  Wars Hard, Platinum.)
- What have you cleared? Your Clan Boss difficulty, the highest stage in each dungeon, and the
  Doom Tower floor.
- Blessings and Awakening on your key champions. HellHades account data already has
  Awakening and a blessing id, so only ask which blessing an id is.
- Anything rotating that matters: today's Clan Boss affinity, the Hydra heads, the Doom Tower
  rotation.

## 2. Stage

`stageSignal` counts 6★ level-60 champions. Combine it with the player's clears, using
HellHades' stage definitions (2020; the placement of newer modes is inference):

| Stage | Roster | Typical clears |
|---|---|---|
| Early | 0–2 at 6★ | Campaign, low dungeons |
| Mid | 5–10 at level 60 | Brutal/NM Clan Boss, Spider 10–15, Dragon 15–17 |
| Late | More | NM/UNM, dungeons at 20, Faction Wars to 18, Doom Tower Hard begun |
| End | Great Hall 180+ | One-key UNM; Hard modes, Hydra, Chimera, Grim Forest |

## 3. Target content

Use the player's stuck point. If they don't have one, use the next rung of this ladder:

1. A Clan Boss team.
2. Spider and Dragon.
3. Minotaur, for scrolls.
4. Fire Knight and Ice Golem.
5. Faction Wars.
6. Doom Tower.
7. Hydra and Chimera.
8. Grim Forest and the Hard modes.

Clan Boss comes first because its chests pay every day.

## 4. Role gaps

List the target content's must-have tools from the mode files. Examples:

- **Clan Boss:** Decrease ATK, Decrease DEF, poison, and an unkillable pair.
- **Kuldath:** Provoke.
- **Faction Wars:** the per-faction counter.

Mark which owned champions supply each tool, from their kits (looked up by name) and the
`heroes` rows.

## 5. Score candidates

> **Priority = ContentValue × GapFill × Breadth ÷ RemainingCost**

| Term | How to fill it |
|---|---|
| ContentValue | The champion's rating for the target content: Ayumilove stars or HellHades 0–5, **fetched by name and dated, never invented**. If you can't fetch it, say so and ask the player, or rank on GapFill alone |
| GapFill | 1.0 if it fills an empty must-have role, 0.5 if it upgrades a weak holder, 0.1 otherwise |
| Breadth | +0.1 for each other mode the player plays where it is rated 4+ |
| RemainingCost | The steps left. Ranks to 6★ (fodder: 1 for R2 up to 5 for R6) + levels to 60 + ascension (6 − `typeId % 10`) + masteries missing (15 − count) + book gaps + empty or weak gear slots |

The weights are a starting point. Tune them with the player, and say so when you do.

## 6. Champion plan

For the chosen champion, in cost order:

1. 6★ and level 60.
2. Masteries: Warmaster or Giant Slayer for damage, Lore of Steel for supports.
3. Books on the skills with a debuff chance or a cooldown.
4. Gear to the content's thresholds.
5. Awakening and Blessing.
6. Empowerment.

## 7. Gear gap

Compare the champion's Ayumilove build with the archetype template and the content's labelled
thresholds. Use `approxStats` as a floor, and ask for the in-game totals before declaring a
gap.

Then search the inventory: run `gear` for SPD pieces and the right main stats, and `hero` for
what's equipped now. If the inventory can't fill the gap, name the dungeon that farms the
missing set (the set-to-farm map in `gear-and-sets.md`).

## 8. Account levers

- **Great Hall:** ACC on the affinities of the player's debuffers.
- **Unassigned mastery scrolls** (Gen 2 files).
- **Shards:** save them for boosted events. Mercy is `[CHECK IN-GAME]`.
- **Clan vs Clan:** batch ranks, books and medals into the tournament window.
- **The monthly Unempowerment coin** (V11.90).

## 9. Triage

Offer `sellCandidates` as a starting point, with the reason for each piece. Name
`speedUpgradeCandidates` and any 3–4-roll SPD pieces as the gear worth investing in.

## 10. Present

Give **the top three actions**. For each:

- what to do, in one line
- why, naming the gap it fills and the content it unlocks
- the cost, in the player's resources
- the evidence label of every number it rests on

Then one line on what you couldn't see in the file that might change the order. Don't dump the
whole scoring table unless asked; it's the reasoning, not the answer.
