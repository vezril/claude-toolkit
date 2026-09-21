# Load-bearing map: pr-description (v5)

This file is documentation, not part of the prompt. The certified prompt is `skills/pr-description/SKILL.md`, byte-identical to `prompts/prompt_v5.md`, and that's what the suite runs.

Every instruction maps to the criterion it serves and the evidence that proves it. Criteria: **contract** (the reply is exactly the three-section description), **coverage** (every changed file and key change is there), **fidelity** (nothing invented).

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
| 12 | Group related changes together | none | not measured by any assert; kept because it makes multi-file PRs readable. Counted as not load-bearing |
| 13 | Each bullet names its file(s) and what changed; every changed file appears | coverage | v2 → v3: Haiku coverage 20/30 → 30/30, Sonnet 27/30 → 30/30 |
| 14 | A new file says what it contains | coverage | case-07 (new service-docs spec: OpenAPI / Swagger), case-04 |
| 15 | Mention files deleted or renamed | coverage | case-01 (deleted file), case-07 (five renames) |
| 16 | Reply is only the description: first line `## What`, no preamble, notes, sign-off or fence; Changes only bullets | contract | v1 → v2: Sonnet contract 25/30 → 30/30 |
| 17 | Name files the way the diff headers do; a class name isn't a file | fidelity | case-08 (`PostgresFlyerLedger.scala`, still 1 of 3 on Haiku in v5) |
| 18 | Copy versions, numbers and identifiers exactly | fidelity | case-07 v1 ("OpenAPI 3" became "3.0"), case-10 versions |
| 19 | Don't guess what a release includes; no issue numbers, tickets or results the diff doesn't show | fidelity | case-10 v1–v3 ("typically include … security updates") |

18 of 19 instructions are load-bearing (94.7%). Instruction 12 is the honest exception: nothing in the suite measures grouping, and I'd rather report that than invent a mapping.
