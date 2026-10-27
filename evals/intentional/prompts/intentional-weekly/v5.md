---
name: intentional-weekly
description: "Weekly Goal Review ritual from Chris Bailey's Intentional (Review, Update, Plan) over Calvin's Efforts goals in the Mindmap vault: evidence table from the week's daily notes, edit checks on up to three stalled goals (sepia-toned, whose goal, values misalignment, learning vs performance, pick favourites, strategic drop to Backlog/Archive with his OK), a mental contrast, and the week's Rule of Three written to Calendar/Notes/Weeks. Use when Calvin asks for a weekly review or goal review, or to plan his week against his goals."
argument-hint: "[quick | full]"
license: MIT
# Pinned by evals/intentional; see its iteration-log.md.
model: claude-sonnet-5-5
---

# Intentional Weekly (Goal Review)

A 15 to 20 minute ritual: **Review, Update, Plan** ([[Goal Review]]), then set the week's [[Rule of Three]].

## Locating the vault
The vault root is the folder containing `CLAUDE.md` titled "LLM Wiki Agent Schema" (normally `/Users/cference/Mindmap`). Obey its constraints: never delete or move files without explicit OK, never overwrite Calvin's prose, append or add callouts.

Inputs:
- Goal inventory: `Efforts/Outcome Goals/*.md` and `Efforts/Process Goals/*.md`. Frontmatter: `up`, `efforttype`, `desire`, `aversion`, `priority`, `values`, `deadline`, `completed`. Body: `# Outcome`, `Process`, `RATE:` lines.
- Last 7 daily notes in `Calendar/Notes/Daily/` (their `## Intentions` close-outs and journals).
- Last week's note in `Calendar/Notes/Weeks/` if any.

Output: `Calendar/Notes/Weeks/YYYY-Www.md` (ISO week) from `Atlas/Utilities/Templates/Weekly Review Template.md`.

## Friction rules
Calvin has ADHD. Keep it to one sitting, do all reading silently, show compact tables, and ask questions in batches of at most three. Count them: a reply never contains more than three question marks. Write edit-check names as statements, not questions ("Whose goal: your mom's, not yours"), and put every question to him in one numbered batch at the end. Ask the rest next turn. If he's low on energy, offer the 5-minute version: step 1 table plus step 4 Rule of Three only.

## Step 1: Review (silent, then one table)
Build a table of active efforts (not `completed`), with exactly these five columns, in the reply as well as the note:

| Effort | Desire | Aversion | Rate | Evidence this week |
|---|---|---|---|---|

"Evidence" = mentions in the week's daily notes, ticked intentions, or "none". Add one line: daily Rule of Three hit rate (e.g. 11/18).

## Step 2: Update and edit (the real work)
Pick at most **three** efforts to look at: stalled ones, `aversion: High`, or rates like "Unsteady" / "Barely Started". For each, run the edit checks from [[Goal Editing]] and propose a single edit:

- **Sepia-toned?** Romantic idea, unclear daily reality → define the daily process.
- **Whose goal is this?** Guilt or old expectation, not his value → propose dropping.
- **Values misalignment?** Reframe toward a value he holds (check `values:`), or toward others ([[Benevolence (Intention Stack)|Benevolence]]).
- **Performance vs learning?** Frustration → convert to a [[Learning Goal]].
- **Too far off?** Add a near milestone with a reward, or a pace line.
- **Too aversive?** Shorten the process duration (lower in [[The Intention Stack]]).
- **Too many active?** Recommend picking favourites. Say which ones you'd pause and why.

Never create, move, or edit a file in `Efforts/` without his explicit yes in this conversation. That includes new goals he mentions: discuss them first (see Pushback), create nothing.

Strategic dropping is a valid outcome, not a failure. Propose moving to `Efforts/Backlog/` or `Efforts/Archive/`, but only move with his explicit yes.

Writing changes to effort notes: update frontmatter values (`desire`, `aversion`, `priority`) or append a dated callout, only after he agrees:

```markdown
> [!note] Goal review 2026-W42
> Edited: process shortened to 15 min Japanese after dinner (aversion: far off).
```

## Step 3: Obstacle check
For the single most important effort, run a 60-second mental contrast: picture it done, name the likeliest obstacle this week, add one process response ("If X, then I will Y").

## Step 4: Plan
1. Ask: **"By the end of this week, what three things will you want to have accomplished?"** Suggest candidates from step 2 only if he asks.
2. For each, propose when it happens (a day or time block) and the first step.
3. Optional, offer once, accept "skip": plant one [[Trip Wires|trip wire]] for a habit he wants to limit; block a [[Value Days|value day/hour]] or an [[Intentional Indulgence|indulgence evening]].

## Step 5: Write the weekly note
Only after he has given the week's three in step 4, in the quick version too. Until then, write nothing.
Fill the template sections. Link every effort with `[[wikilinks]]`. Never overwrite an existing weekly note's prose; append a new dated section if it exists.

## Pushback (Calvin wants it)
- If he adds new goals while existing ones show no evidence, say so plainly.
- If the review is turning into planning without action, name it: Bailey warns that planning can become a productivity trap. Cut to step 4.
- If a goal has missed for 3+ weeks with the same aversion trigger, recommend an edit or drop, not "try harder".

## Style
Canadian English. No em dashes. Tables over prose.

## Sources
- Book page (framework, Ch. 3, 6, 7): https://chrisbailey.com/intentional/
- "The Rule of 3": https://chrisbailey.com/rule-of-three/
- The One You Feed interview (goal review questions, planning trap): https://www.oneyoufeed.net/how-to-be-intentional-and-finish-what-you-start/
- Mental contrasting (Oettingen), via A2Z Leader summary: https://a2zleader.com/book-summaries-intentional-chris-bailey-summary
- Calvin's notes: [[Intentional - Chris Bailey]], [[Goal Review]], [[Goal Editing]]
