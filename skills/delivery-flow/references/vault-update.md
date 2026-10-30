---
name: vault-update
description: "Write what this item delivered into the project's knowledge graph — one delivery note, the entity stubs it needs, and links to the decisions it followed. Emits vault-updated.json."
---

# Update the project memory

**This prompt is not yet certified.** `vault-update` is listed in `allow_uncertified`, every run
traces `certified: false`, and those runs are excluded from the certified-only end-to-end rate.

You are the one genuinely generative step in the memory path. Recall is a script, because
scoring notes is arithmetic. Writing a note that a colleague will thank you for in six months
is not, which is why this is a node.

## Inputs

`item.json`, `triage.json`, `proposal.json`, `implementation.json`, `verify.json`,
`pr-opened.json`, and the vault binding (`vault.path`, `vault.graph_root`, `vault.binding`).

## What to write

**One `delivery` note**, upserted by ticket key at `<graph_root>/deliveries/<ITEM-KEY>.md`. If a
note for that key exists, **edit its fields** — never create `<ITEM-KEY> 1.md`.

Its frontmatter is the retrieval surface, and three fields carry almost all of the value:

- `goal` — one line: what this delivered, and for whom.
- `approach` — one line: how, at the level a future reader actually needs.
- `outcome` — one line: what happened, including if it went badly.

**Write these for someone who has ten seconds.** Recall shows them verbatim and shows nothing
else from the note, so a `goal` of "implemented the ticket" makes the note worthless while
costing exactly as much to store. No ticket-speak, no restating the title.

Also set `project`, `status` (`in-progress` | `shipped` | `reverted`), `date`, `domains` from
triage, `services` as `[[entity]]` links, `decisions` as `[[slug]]` links to decisions this
followed, and `refs.pr` / `refs.ticket`. Then the body: `## What shipped`, and
`## Notes for next time` when there is something real to say.

## What you may and may not mint

- **You may** create missing `project` and service/component entity stubs that your links need.
  A dangling wikilink is invisible to recall, so a stub is better than a broken edge.
- **You may not invent a decision note.** Only write one when the proposal recorded an actual
  accepted design decision, and then **link** the OpenSpec change or PR rather than copying it.
  The repo is the source of truth; the vault holds the index and the one-liners.
- **You may not edit someone else's notes beyond adding links.** Incident notes, lessons and
  other projects' notes are not yours to rewrite.

## Rules

- **Basenames are globally unique across the vault** — Obsidian resolves `[[links]]` by
  basename. On a collision, yield: `<ITEM-KEY> (delivery).md` plus an `aliases` entry.
- **One line means one line.** A `goal` spanning three sentences breaks the recall output's
  shape and its line cap.
- **Never write outside `vault.graph_root`**, and never delete or move an existing note.
- **Record `status: reverted` honestly** if the change was rolled back. A memory that only
  remembers successes is worse than none, because it reads as though nothing ever fails.

Finish by writing `vault-updated.json` (the note paths you wrote or edited, the stubs you
minted, the decisions you linked) and its sentinel.
