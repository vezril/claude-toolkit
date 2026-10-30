## Context

The vault steps have been routed but empty since `add-delivery-flow`.
`extend-vault-graphrag-projects` specifies the memory model and the recall algorithm but is
unimplemented. This change implements both, and changes one of the parent change's conclusions.

Facts that shaped it, all verified rather than assumed:

- The target vault was `/Volumes/Private/Amazon RAG`, an AFP mount from
  `mimir.experimentalneutron.com`. It held `Isengard.md`, `Welcome.md`, an empty `Untitled.md`
  and `.obsidian/` — no graph structure at all. "The vault exists" was true; "the graph exists"
  was not. **Superseded by D3a:** the vault is now a local git clone at `~/Obsidian/Amazon RAG`
  with the NAS hosting the canonical bare repo, because reading the mount directly stopped the
  flow dead whenever the laptop left the home network.
- `Atlas/RAG` in the parent change's task 0.2 is a *different* vault's graph root. Nothing in
  this one conflicts, because there is nothing in this one.
- The recall algorithm as specified contains no judgement: fixed integer weights, a fixed
  threshold, date tie-breaking, fixed caps, frontmatter-only reads, and an explicit prohibition
  on advice.
- `vault-graphrag`'s own position is "schema first, index later… `rg` + YAML parsing are the
  query engine" — i.e. the skill already expects plain-text tooling, not inference.

## Goals / Non-Goals

**Goals:**
- Give the pipeline memory that is reproducible and costs nothing per run.
- Make a dead mount loud rather than silently equivalent to an empty result.
- Scaffold the real vault so the first run has somewhere to read from and write to.
- Land the parent change's schema deltas as documentation that matches the implementation.

**Non-Goals:**
- Embeddings or any index. The schema is the contract; traversal has not failed yet.
- The `iris` backend.
- Certifying `vault-update`, or seeding real decision notes from Olympus ADRs.
- Changing incident recall or anything the private defect-flow repo depends on.

## Decisions

**D1 — Recall is a script, which amends the parent change's task 3.4.**
That task says to certify delivery recall to the Stage 3 bar via `prompt-edd`. I think that is
the wrong instrument, and the reason is in the spec itself: *"score each candidate as 3 per same
project, plus 3 per shared service/component link, plus 2 per shared domain (3 in implementation
mode), plus 1 per keyword hit… drop candidates scoring below 3, break ties by date… cap at 5
decisions, 5 deliveries, 3 lessons and 3 patterns."* That is an arithmetic function with a
deterministic sort.

A prompt implementing it needs an eval suite, ≥3 criteria, a load-bearing map, an iteration log
and three consecutive runs ≥95% — to approximate, with a 5% error budget, something Python does
exactly and for free. Worse, it would be a *node*: a non-deterministic step whose output the
next step consumes, which under Stage 4 then needs its own edge. As a script it is an edge: it
either computes the specified score or its tests fail.

What this gives up: a prompt could notice relevance the scoring misses. That is real, and it is
why the output's coverage section reports everything scanned and everything dropped — a human
reading a thin `project-context` can see what was considered. If traversal provably fails to
surface things people needed, that is the evidence for adding a semantic layer, and the schema
is unchanged by it. Don't reach for inference before traversal has been shown to fail.

The parent change's eval fixture becomes this change's test fixture, and the asserts get
stricter: exact scores and exact membership instead of a pass rate.

**D2 — `project-context.json` is the contract; the `.md` is a rendering.**
The vault spec names `project-context.md`; the delivery-flow routing table has always named
`project-context.json`. Both are right for their own context, and the resolution is to emit
both: the JSON is what `breakdown` and `propose` consume and what the edge validates, the
markdown is what a human reads. Prose that a node consumes is exactly what Stage 4 rule 1
forbids, so the JSON cannot be dropped in favour of the markdown.

**D3a — The vault is a local git clone; the NAS hosts the canonical bare repo. Revised
2026-10-28, and it supersedes the premise of D3 below while keeping its reasoning.**

D3 assumed the vault was read straight off an AFP mount. That failed the first real test of it:
away from the home network, the mount is gone, recall exits 3, and the whole flow stops — the
NAS being unreachable is not a good enough reason to stop work. Worse, it had already dropped
mid-session once while *at* home.

So `vault.path` now names a git work tree on the laptop, and the NAS hosts the canonical repo as
`origin`. **In the event that repo is GitBucket rather than a bare repo over ssh** (resolved
2026-10-28): ssh to mimir refused the laptop's key, and a GitBucket instance was already running
on the same NAS, so it serves the same purpose over HTTP with a token and needs neither an ssh
key nor the AFP mount. The constraint the original decision cared about is unchanged — the
remote is on hardware Calvin owns, not a third party's. The cost is that the transport is plain
HTTP on the LAN; recorded as a residual in tasks 3.6c rather than waved away. Git rather than a synced directory, because two Macs editing the same decision note is
exactly what last-writer-wins would destroy silently, and because a decision's history is part
of the audit trail this project exists to produce.

**This trades a loud failure for a quiet one, which is the real cost.** D3's insight was that
an unmounted NAS and an empty vault are indistinguishable at the output, so the former must fail
loudly. A local clone is always reachable, so recall always succeeds — and can serve month-old
memory as current, which is a *silent* wrong answer and therefore worse than the failure D3
prevented. The fix is to move the loudness from reachability to freshness: every run reports
HEAD, dirty, ahead/behind, and days since the last fetch, sets `stale` against
`punch_out.vault_staleness_days` (14 by default), and the rendered brief opens with a
stale-memory warning above any recalled content.

Three details that are easy to get wrong and are therefore pinned by tests:

- **Staleness is the last fetch, never the last push.** A push proves the NAS was reachable but
  teaches this clone nothing, so a laptop that pushed an hour ago can still be a month behind
  what the other Mac decided. The first implementation took `max(fetch, push)` and a test caught
  it. `.git/FETCH_HEAD`'s mtime is the signal because fetch alone writes it — the
  remote-tracking ref's reflog is ambiguous, since a push updates that too.
- **No network call in recall.** A step that hung waiting on an unreachable NAS would reinstate
  the dependency this change removes. Every fact comes off the clone's own disk.
- **No upstream means `null`, not `0`.** Reporting zero commits ahead would claim an agreement
  with the NAS that was never observed.

Nothing in the flow pushes. `vault-update` commits, so notes are durable and syncable; the push
is an outward action over a network that may not be there, and it waits for a human.

**Still open:** promoting `stale` from a recorded fact to a derived punch-out trigger. It
belongs there — "memory may be out of date" is exactly a thing a human should acknowledge — but
a punch-out needs a signed decision to clear, and the signing key does not exist yet, so making
it a trigger today would block offline work entirely instead of flagging it. Revisit when the
key exists.

**D3 — Unreachable is exit 3 and no artifact; empty is exit 0 with an artifact.**
This is the decision the parent change asked for (its D7) and the one most likely to be got
wrong. A NAS mount that is not mounted makes the graph root simply absent, and `rg` over a
missing directory finds nothing — the same observable result as a vault with no relevant notes.

So reachability is checked *before* scanning, as a distinct step: does the graph root exist, is
it a directory, is it readable, and does it contain at least the expected folder layout. Failing
that is a remote-style failure (exit 3, matching the adapter convention), the step produces no
artifact, and the flow stops with "the vault is unreachable" rather than proceeding memoryless.
Reachable with nothing matching writes `matched: false` plus the coverage section, exit 0, and
the flow proceeds — a cold start is not an error.

The trace then distinguishes them, which is the whole point: "no memory was applied" and "memory
was consulted and had nothing" are different facts about a run.

**D4 — The scaffold refuses to write outside the configured vault, and never overwrites.**
It creates the graph root and the five folders, one `project` entity for the binding, and the
note templates. Every write is checked to resolve inside `vault.path`; anything already present
is left exactly as it is and reported as skipped. The vault is a human's own notes, and a tool
that reorganizes them is worse than no tool.

**D5 — `vault-update` stays a node, declared uncertified.**
Upserting a delivery note means writing one-line `goal` / `approach` / `outcome` fields that read
usefully in six months. That is generation, and the one part of this that a model should do. It
goes in `allow_uncertified` with `propose`, traces `certified: false`, and is excluded from the
certified-only rate until it has a package.

**D6 — Keyword extraction is specified, not improvised.**
Scoring awards 1 per keyword hit, so what counts as a keyword decides results. Defined as: the
item's title and summary, lowercased, split on non-alphanumerics, with a stop list and tokens of
fewer than four characters dropped, deduped. Written down because an undefined keyword set makes
the "1 per keyword hit" rule unreproducible, and reproducibility is the entire argument for D1.

## Risks / Trade-offs

- **Scoring weights are somebody's guess.** 3/3/2/1 with a threshold of 3 came from the parent
  change, not from measurement. They are constants in one module with the spec's scenarios as
  tests, so they can be retuned against real recalls; the first few runs are the evidence.
- **Disagreeing with the parent change's task 3.4** means a reviewer may expect a certified
  recall prompt and find a tested script. Addressed by stating the reasoning in the submission
  rather than quietly shipping something different.
- **A script cannot notice what the schema did not anticipate.** Mitigated by the coverage
  section, not solved. Accepted deliberately, with the trigger for revisiting written down.
- **The vault is on a NAS**, so recall is only as available as the mount. That is why D3 exists;
  it does not make the mount more reliable.

## Migration Plan

1. Schema and recall script with the synthetic fixture — no real vault needed.
2. Reachability behaviour and its tests, including a deliberately-unmounted path.
3. Scaffold the real vault at `/Volumes/Private/Amazon RAG`, confirm Obsidian still opens it.
4. Documentation: `schema.md`, `delivery-recall.md`, the binding reference.
5. `vault-update` prompt and `allow_uncertified`, then turn `vault.binding` on for one item.

## Open Questions

1. **Which project name is the binding?** `amazon` is the obvious default from the vault's name,
   but the binding appears in every note's frontmatter and renaming later touches every file.
2. **Should the scaffold move the three existing notes** (`Isengard.md`, `Welcome.md`,
   `Untitled.md`) into the graph, or leave them outside it? Leaving them is the default per D4.
3. **Do the retuned weights need a decision**, or can they be adjusted freely once there are real
   recalls to judge? They change which memory reaches a proposal, so they may deserve the same
   "policy, not implementation" treatment as the punch-out ceilings.
