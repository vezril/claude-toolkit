# Delivery recall — "what has this project already decided, built and learned?"

Incident recall asks *have we seen this bug before*. Delivery recall asks the question that
comes up before building something: *what did we settle, ship and learn here already*. Same
graph, different traversal, different weights.

**The script is normative.** `scripts/delivery-flow/vault-recall.py` is the definition; this
page explains it. If the two disagree, the script is right and this page is stale — file that
as a bug rather than reasoning from the prose.

## Why this is code and not a prompt

The algorithm below is arithmetic: fixed integer weights, a fixed threshold, a date tie-break,
fixed caps, and a prohibition on saying anything the notes do not. There is no judgement step in
it.

Implemented as a prompt it would need a `prompt-edd` package — an eval suite, three consecutive
runs at ≥95%, a load-bearing map, an iteration log — to approximate, with a 5% error budget, a
calculation Python performs exactly. It would also be a *node*: a non-deterministic step whose
output a later node consumes, which under Stage 4 then needs a deterministic edge of its own to
police it. As a script it **is** the edge: it either computes the specified score or its tests
fail.

This is a deliberate departure from `extend-vault-graphrag-projects` task 3.4, which planned to
certify recall at Stage 3. The reasoning is recorded in
`openspec/changes/add-vault-delivery-memory/design.md` D1, and the eval fixture that change
specified became the script's test fixture with stricter asserts: exact scores and exact
membership instead of a pass rate.

**What that gives up:** a model might notice relevance the schema never anticipated. That is
real and unfixed. It is why every run reports its full search coverage — a thin result with the
scan behind it is honest, and a human can see what was considered and rejected. If traversal
provably misses things people needed, that is the evidence for adding a semantic layer, and the
note schema would not have to change to get one. Don't reach for inference before traversal has
been shown to fail.

## Inputs and call points

Two call points, both emitting into the calling pipeline's item directory:

| Mode | Keyed on | Writes |
|---|---|---|
| `solutioning` | the item | `project-context.json` + `project-context.md` |
| `implementation` | one story | `project-context-<story>.json` + `.md` |

The implementation call never overwrites the solutioning output. Inputs are `item.json`,
`triage.json` and the binding (`vault.binding`, `vault.path`, `vault.graph_root`,
`vault.backend`).

## Scoring

Every candidate note in `decisions/`, `deliveries/`, `lessons/` and `patterns/` is scored from
its **frontmatter only**:

| Signal | Weight |
|---|---|
| same `project` as the binding | **+3** |
| each shared service or component link | **+3** |
| each shared domain | **+2** at solutioning, **+3** at implementation |
| each keyword hit in the note's payload lines | **+1** |

Then: **drop below 3**, sort by score descending, **tie-break by date (newest first)** and then
by name, and cap at **5 decisions, 5 deliveries, 3 lessons, 3 patterns**.

The threshold is what makes a single keyword hit insufficient. One shared word with a note from
another project scores 1 and vanishes; the same note in this project scores 4 and appears. That
asymmetry is the whole point of the `project` field.

Weights live as constants at the top of the script. They came from the parent change's
specification, not from measurement, so they are expected to be retuned once there are real
recalls to judge — the spec's scenarios are encoded as tests, so retuning is a visible change
rather than a quiet drift.

### Keywords are defined, not improvised

A point per keyword hit means the keyword set decides results, so it is specified: the item's
**title and summary**, lowercased, split on non-alphanumerics, with a stop list applied and
tokens shorter than **4 characters** dropped, deduplicated and sorted. The exact set used
appears in the output's coverage section, because an unreproducible scoring input would undo
the entire argument for doing this in code.

### Payload lines, per type

Only these fields are read for keyword matching, and only these are shown in the output:

| Type | Payload |
|---|---|
| decision | `context`, `decision`, `consequences`, `status` |
| delivery | `goal`, `approach`, `outcome`, `status` |
| lesson | `lesson`, `practice`, `why` |
| pattern | `shape`, `detection`, `mitigation` |

Note bodies are never read. A narrative cannot leak into a machine-consumed artifact, and a
long note is not more findable than a short one — only a better-written payload is.

## Only accepted decisions are in force

A decision scoring above the threshold whose `status` is not `accepted` is **not** listed under
decisions in force. It appears in the coverage section instead, named with its `superseded_by`
replacement. Visible, traceable, and impossible to quote back as current.

## Unreachable is not empty

Checked **before** scanning: does the graph root exist, is it a directory, is it readable.

| State | Exit | Artifact |
|---|---|---|
| graph root missing / not a directory / unreadable | **3** | none |
| reachable, nothing above threshold | **0** | written, `matched: false`, coverage populated |
| unimplemented `vault.backend` | **2** | none |

This distinction is the reason the check exists. A missing graph root makes scanning find
nothing — identical at the output to a vault with no relevant notes. Conflating them means a run
proceeds with no memory, looks successful in the trace, and nobody learns the memory step was
dead. "No memory was applied" and "memory was consulted and had nothing" are different facts
about a run.

## Freshness, now that the vault is local

The vault is a **local git clone**; the canonical bare repo lives on the NAS. Reading it off the
network share meant recall failed outright whenever the laptop left the home network, and the
share being down is not a good enough reason to stop work.

That removes one failure and introduces a quieter one: a clone can be weeks behind without
looking it, so recall could serve stale memory as current — a silent wrong answer, which is
worse than the loud one above. So every run reports its sync state in the `vault` section of
`project-context.json` and in the trace:

| Field | Means |
|---|---|
| `tracked` | the vault is a git work tree at all |
| `head`, `head_date`, `dirty` | the local tip, and whether notes are uncommitted |
| `upstream`, `remote` | what it tracks; `null` ahead/behind where nothing is tracked |
| `ahead`, `behind` | local commits not on the remote, and vice versa |
| `last_sync`, `days_since_sync` | when this clone last **fetched** |
| `stale` | `days_since_sync` exceeds `punch_out.vault_staleness_days` (14 default) |

Three rules worth remembering:

- **Staleness is the last fetch, not the last push.** A push proves the remote was reachable but
  teaches this clone nothing, so a laptop that pushed an hour ago can still be a month behind
  what another machine decided.
- **Recall makes no network call.** A step that hung on an unreachable remote would reinstate
  the dependency the local clone removes.
- **`null` is not `0`.** A branch tracking no upstream reports unknown counts rather than
  claiming agreement nobody observed.

A stale run still exits 0 — blocking offline work would defeat the point — but the rendered
`project-context.md` opens with a stale-memory warning above any recalled content.

## Output

`project-context.json` is the contract (schema: `schemas/project-context.schema.json`), and what
downstream steps consume. `project-context.md` is the same content for a human, capped at 80
lines. Both carry a mandatory **Search coverage** section: the entities, keywords and domains
used, notes scanned per folder, candidates dropped below the threshold, candidates dropped to
the caps, and superseded decisions skipped with their replacements.

Each match shows its payload lines verbatim plus its `[[wikilink]]`, and its score — the score
is included so a thin or surprising result can be audited rather than trusted.

## Facts, not recommendations

The output states what the graph holds and never what the item should do. With a script this
holds by construction rather than by instruction: there is no generative step that could offer
an opinion. A reader deciding whether a decision still applies is doing a human's job, and
recall's contribution is putting the decision in front of them.
