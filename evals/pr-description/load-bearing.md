# Load-bearing map: pr-description (v7)

This file is documentation, not part of the prompt. The certified prompt is `skills/pr-description/SKILL.md`, byte-identical to `prompts/prompt_v7.md`, and that's what the suite runs.

Every instruction maps to the criterion it serves and the evidence that proves it. Criteria: **contract** (the reply is exactly the four-section description), **coverage** (every changed file and key change is there), **fidelity** (nothing invented), **risk** (the door is called right and the blast radius is named), **brevity** (each section stays inside v7's stated length limits, so a reviewer who scans still reaches the Merge danger section).

| # | Instruction | Serves | Proven by |
|---|-------------|--------|-----------|
| 1 | Role: a reviewer reads it before the diff, so it has to be accurate | fidelity | motivates rules 9, 10, 17–19 |
| 2 | Role: report what the diff shows; don't guess at things it doesn't say | fidelity | case-06 v1 (Sonnet invented how the JS client parses), case-10 |
| 3 | Task: run `git diff main...HEAD` and read the commit subjects | coverage | every case; the harness supplies both, since the eval has no git |
| 4 | Task: write it in the format below | contract | every case |
| 5 | Context: the description is used as the PR body exactly as written | contract | the why behind rule 16; Sonnet preambles in v1 |
| 6 | Context: reviewers use Changes to find their way, so each bullet points at its file | coverage | the why behind rule 13 |
| 7 | `## What`: one sentence | contract | one-sentence check, every case |
| 8 | `## Why`: brief context | contract | empty-Why check, every case |
| 9 | Why is taken only from the diff, commit messages and code comments | fidelity | case-10: v3 3/3 fail → v4 3/3 pass |
| 10 | No stated reason → say what kind of change it is and stop | fidelity | case-10 (Dependabot bump) |
| 11 | Changes: bullet points of the specific changes made | contract, coverage | bullet-only check; fact groups |
| 12 | Group related changes together | brevity, coverage | measurable from v7: the five-bullet cap (26) plus the every-file rule (13) cannot both hold on case-06 or case-07 without grouping. Unmapped in v1–v6 |
| 13 | Each bullet names its file(s) and what changed; every changed file appears | coverage | v2 → v3: Haiku coverage 20/30 → 30/30, Sonnet 27/30 → 30/30 |
| 14 | A new file says what it contains | coverage | case-07 (new service-docs spec: OpenAPI / Swagger), case-04 |
| 15 | Mention files deleted or renamed | coverage | case-01 (deleted file), case-07 (five renames) |
| 16 | Reply is only the description: first line `## What`, last line the Blast radius line, no preamble, notes, sign-off or fence; Changes only bullets | contract | v1 → v2: Sonnet contract 25/30 → 30/30; v6 Haiku contract misses when the heading is dropped |
| 17 | Name files the way the diff headers do; a class name isn't a file | fidelity | case-08 (`PostgresFlyerLedger.scala`, still 1 of 3 on Haiku in v5) |
| 18 | Copy versions, numbers and identifiers exactly | fidelity | case-07 v1 ("OpenAPI 3" became "3.0"), case-10 versions |
| 19 | Don't guess what a release includes; no issue numbers, tickets or results the diff doesn't show | fidelity | case-10 v1–v3 ("typically include … security updates") |
| 20 | `## Merge danger`: **Door:** one-way or two-way, with one sentence why, from the diff | risk | v5 → v6 on the 11-case suite: risk 0/33 → 33/33 on both models |
| 21 | **Blast radius:** who or what is affected if the change is wrong, named from the diff | risk | same; every case needs one radius keyword from its expected file |
| 22 | One-way only if a revert wouldn't undo it (dropped data, removed public contract, published release); everything else two-way | risk | case-11-drop-notes one-way 12/12; the other ten cases two-way 120/120 |
| 23 | Context: a reviewer scans before they have context and skips what looks long, so the limits are part of the format | brevity | the why behind 24–28; motivates the section-by-section caps |
| 24 | `## What` is one sentence, 25 words or fewer | brevity | v6's own 66 outputs: median 23–25 words, p90 32, max 37 |
| 25 | `## Why` is at most two sentences | brevity | v6: median 2 sentences, p90 3–4, max 4 |
| 26 | `## Changes` has at most five bullets; one bullet may cover several files and every changed file still appears | brevity, coverage | v6: median 3–4 bullets, p90 6, max 8; bites on case-06 and case-07 (6 files each), which is what forces grouping |
| 27 | Each bullet is one line of 25 words or fewer; no sub-bullets | brevity | v6: median 20–25 words, p75 29, **max 84** — the dominant violation |
| 28 | The **Door:** and **Blast radius:** lines are one sentence each | brevity | v6: median 1 sentence each, p90 2, max 3 |
| 29 | State what changed, not how much it improves things; no graded adjectives (`comprehensive`, `robust`, `significantly`, …) | brevity | banned-list check; a graded adjective is a claim the diff has to back |

29 of 29 instructions are load-bearing (100%).

**Instruction 12 (grouping) became measurable in v7**, so the v6 exception is gone. Nothing measured grouping while the bullet count was unbounded; the five-bullet cap in instruction 26 is what gives it teeth, because the two six-file cases cannot satisfy both the cap and the every-file rule without grouping. The honest note it carried in v6 — "nothing in the suite measures grouping, and I'd rather report that than invent a mapping" — is kept here as the record of why it was unmapped for five versions.

## How the brevity caps were set

From data, not taste. Each cap sits at or just above the **median of v6's own 66 unconstrained outputs**, so it is a real constraint that the long tail violates badly rather than a limit the model already respects. v6 scores **1/33 on brevity on both models** — close to the flat zero a genuinely absent behaviour should score, which is what makes this criterion load-bearing rather than decorative.

The bullet cap was 20 words in the first draft and is 25 here. At 20 it sat *below* the median and was the dominant failure on 26–32 of 33 cases; on a six-file case it also pushed against `coverage`, which requires every changed file to appear. A cap meetable only by dropping a file would have traded one criterion for another, which is the failure this whole file exists to make visible.

`asserts/brevity.selftest.js` is the mutation test, run before any model call: the assert accepts a hand-written reference answer and fails on each of eight defects with the right reason (9/9).
