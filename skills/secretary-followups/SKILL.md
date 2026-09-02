---
name: secretary-followups
description: "Track commitments and waiting-on threads in the secretary's L1 state, and surface what needs Calvin today. Captures a commitment when he mentions one, dedupes against existing entries so repeated cold runs never double-write, closes items by moving them rather than deleting, and nudges threads that have gone quiet past their window. Use when Calvin mentions owing someone something, asks what he owes or is waiting on, or when a scheduled secretary run needs the follow-up section of the brief. Phase 1 of the secretary: zero external dependencies, pure L1 file state."
---

# Follow-ups (commitments and waiting-on)

The secretary's memory. Everything here is plain markdown in
`~/Code/secretary/state/`, git-tracked, and read fresh on every run — because scheduled runs
are cold sessions that share nothing.

`policy.md` governs. L1 writes are `auto`; closing something the agent *inferred* is done is
`report`; deleting is `never`.

## The two files

**`state/commitments.md`** — things Calvin owes someone (or himself).

```
## Send Marc the camper wiring diagram
- who: Marc Tremblay
- opened: 2026-09-02
- due: 2026-09-05
- source: conversation 2026-09-02
- status: open
- notes: he asked twice
```

**`state/waiting-on.md`** — the ball is in someone else's court.

```
## Quote for the concrete pad
- who: campground office
- since: 2026-08-28
- nudge-after: 7
- source: conversation 2026-08-28
- status: waiting
```

## Capturing

When Calvin says something that is a commitment, write it. Signals: "I need to", "I told X
I'd", "I owe", "remind me to", "I'll get back to".

- **Record what he said, don't upgrade it.** "I should probably email Marc sometime" is a real
  commitment with `due: none` — not a Friday deadline you invented. A due date exists only if
  he gave one or it's unambiguous from context ("before the weekend").
- **`who` matters.** A commitment to another person outranks one to himself, because someone
  else is blocked on it. If it's to himself, `who: self`.
- **Always fill `source`** — where it came from and when. Without it, a future run can't judge
  whether the entry is still real.
- If he mentions something ambiguous, capture it as a commitment with a note rather than
  asking mid-flow. He can correct it; a dropped commitment can't be corrected.

## Dedupe — the cold-session rule

**Before writing any entry, read the file and check whether it's already there.** Two runs an
hour apart must not produce two copies. Match on `who` plus the substance of the description,
not on exact string equality — "send Marc the diagram" and "email Marc the wiring diagram" are
the same commitment.

If it exists: update it (a new due date, a note that he chased again), don't duplicate it.
If it exists in `## Closed` and he's clearly raised it again, reopen it rather than adding a
second copy — and note the reopen date.

## Surfacing

What comes back, ordered by what actually needs him:

1. **Overdue** — `due` in the past, still open. Lead with these.
2. **Due today or tomorrow.**
3. **Waiting-on past its window** — `since` + `nudge-after` days has elapsed. These are the
   easiest thing to lose entirely, which is the whole reason the file exists.
4. **Everything else open** — only if he asked for the full list. It does not go in a brief.

Compute all of this **from the dates in the file against today**, never from a memory of the
last run. That is what makes a missed or duplicated run harmless.

Keep it short. One line per item: what, who, and how overdue. No status commentary, no
encouragement, no "you've got this".

## Closing

- Calvin says it's done → move the block to `## Closed`, set `status: closed`, add the date.
  `auto`.
- The agent *infers* it's done from context → same move, and **say so in the brief**. That's
  `report` in policy, and it exists so a wrong inference is visible instead of silent.
- **Never delete a block.** Closing is a move. If an entry turns out to be nonsense, move it
  to `## Closed` with a note saying why — don't erase it.

## Always-apply defaults

1. **Read L1 first, write L1 last.** One coherent write per run.
2. **Idempotent always.** Dedupe before writing; compute urgency from stored dates.
3. **Never invent a date, a person, or a commitment.** If it wasn't said, it isn't state.
4. **A quiet result is a real result.** "Nothing overdue, two things waiting" is a good
   answer. Don't manufacture activity to look useful.
5. **Facts in `people/`, never inference.** What was said and agreed — not what it meant.

## Anti-patterns

- Duplicate entries from a re-run: the failure this skill exists to prevent.
- "Since last run" logic of any kind.
- Upgrading a vague intention into a dated deadline.
- Deleting entries, or silently closing something on a guess.
- Dumping the entire open list into a morning brief.
- Nagging: repeating the same overdue item with escalating language across runs.

## Related

- [[morning]] — the brief this feeds.
- [[calvin-voice]] — for drafting anything he'll actually send.
