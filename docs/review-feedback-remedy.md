# What the review feedback says, and what to change

Source: two review docs on `awslabs/nx-neptune` PRs #654 (2 comments) and #678 (6 comments,
one of them unanswered since 2026-11-19). Eight findings, every one rated **major**, numbered
`major-9` through `major-18` — so the count runs across PRs and this is the tail of a longer
series, not two bad days.

The findings are not scattered. They fall into three classes, and the class tells you which
part of the pipeline failed.

## Class A — assumptions about an external API, never checked (4 of 8)

`major-12`, `major-9`, and the hedge in `major-16` and `major-17`. Four of the eight *Required*
lines literally begin with **"Confirm"**:

- "Confirm `StartImportTask` accepts a non-empty graph, or reset before every form."
- "Confirm `DeleteGraph` returns `ConflictException` for a protected graph, or clear protection."
- "Confirm A's `on_created` cannot follow B's record, or write only when `graph_id` is empty."
- "Confirm `on_created` cannot fire during either gather, or compare `current.graph_id != p.graph_id`."

That is a reviewer saying: *you built on a precondition you never established, and I can't tell
from here whether it holds.* The code may well be correct. It isn't **shown** to be, so the
burden lands on the reviewer, who then has to write the comment.

Two of these have real consequences if the assumption is wrong: a misread trust rejection
(`major-12`) and a 600-second hang followed by a failure (`major-9`).

## Class B — concurrent mutation of a shared row (3 of 8)

`major-14`, `major-16`, `major-17`. All three are the same shape: a callback fires at a moment
nobody modelled, and the write that follows isn't guarded.

- `major-16`: a stale run's `update(graph_id=...)` overwrites the new owner's reference. The
  orphaned graph **keeps billing**. That is a lost update — the fix is write-if-empty or
  compare-and-set.
- `major-17`: a gather re-read skips children whose `graph_id` looks stale, and runs once, so
  graphs recorded during the second gather are never re-read.
- `major-14`: a sync callback loops on `time.sleep` for up to 600 s while it is being called
  from async code, so the event loop stalls and **every proxy request blocks**.

## Class C — a test and a doc that don't check what they claim (2 of 8)

- `major-15` is our own recurring defect, in a client PR: *"making it unconditional still
  passes."* The test never reaches the conditional write it is named for. That is a surviving
  mutant, by definition — present, successful, checking nothing.
- `major-11` is the doc version: the README and a test's skip reason both say the graph is
  **not** reset, and the code path resets it with `skipSnapshot=True`. The prose describes
  behaviour the code contradicts, and the behaviour is destructive.

## What to change, and how much each actually buys

### 1. A mutation gate on new tests — catches `major-15` mechanically

This is the only finding in the set a script can catch outright, and the finding states the
test for us: mutate the production line a new test claims to cover, and the test must fail.
Every test added in a diff, every mutant killed, or the step reports which ones survived.

We already run exactly this technique twice — `evals/sdlc-implementation`'s `green` criterion
applies a hidden reference implementation, and the new provider tests mutation-prove all seven
of their asserts. The move is to point it at the client diff instead of at our fixtures, in the
`verify` step where the test command already runs.

**Honest scope: 1 of 8.** It is still the best single change here, because it needs no model
judgement and it cannot drift.

**Built.** `scripts/delivery-flow/mutation-gate.py`, recorded in `verify.json` under
`mutation`, config in `skills/delivery-flow/references/config.md`. Confirmed on a synthetic
repo reproducing the finding: the inert test leaves four survivors including the literal
`if True:` mutant the comment named, and a test that reaches the branch kills all four. Off by
default, Python-only.

One follow-on belongs with item 2 rather than here: the review node already receives
`verify.json`, but nothing in its prompt tells it that `mutation.survived[]` is a finding to
report. Adding that is a prompt change to a certified step, so it rides with the re-iteration
below.

### 2. Eight eval cases in `evals/delivery-review`, then iterate the review prompt

The review node exists and is certified (8 cases, 99.1% on its own suite), and it did not catch
any of these. That is not a reason to distrust the certification — it means the suite does not
contain these shapes. A certified prompt is certified against its suite and nothing else.

So: add all eight as cases, run the current prompt as the baseline, and iterate. Expect the
baseline to score badly on Class A, since nothing in the review prompt currently asks "what
does this change assume about an API it does not own?"

This needs a **new criterion**, because the existing four don't cover it: *every external-API
precondition the diff relies on is either tested, documented, or named as an open question.*
Class A is half the findings and it is a single missing instruction.

**One constraint:** `claude-toolkit` is public and these are client review docs. The cases go in
as synthetic fixtures that preserve the defect shape (sync sleep called from async; lost update
on a shared row; a test that cannot reach its branch; a README that contradicts a destructive
path) with the client's names, links and code removed. The real documents stay in
`claude-toolkit-private`.

### 3. A linter closes the easy half of Class B, but not this instance

Ruff's `ASYNC` rules flag a blocking `time.sleep` inside an `async def`, and that is worth
turning on. It would **not** have caught `major-14`: `_delete_orphaned_graph` is a sync
function, and the problem is that it's reached from async code. Transitive blocking is a call
graph question, not a lint.

So the linter is cheap insurance against the direct form, and the transitive form belongs with
the review node's eval cases in item 2. I'd rather say that than claim a gate that wouldn't
have fired.

### 4. Make the PR description state its assumptions

Class A costs the reviewer four comments asking what the change relies on. A PR body that
listed those preconditions up front — *this assumes `StartImportTask` accepts a non-empty
graph; untested* — converts four review comments into four lines the author already wrote.

`pr-description` is certified at v6, so this is a prompt change that needs re-certification
rather than an edit. Sequence it after item 2, since the review node's new criterion defines
what an "assumption" is and the two should agree.

## What this does not fix

Nothing here makes the underlying code correct. Classes A and B are both *"we did not model
concurrency and we did not verify the API contract"*, and the fix for the eight open comments
is eight code changes in `nx-neptune`, including the one that has been waiting since
2026-11-19. The pipeline work stops the ninth and tenth, not these.

## Order

1. Mutation gate in `verify` (deterministic, catches `major-15`, no certification needed).
2. Eight synthetic cases + the fifth criterion in `evals/delivery-review`; baseline, then
   iterate under `prompt-edd`.
3. Ruff `ASYNC` on in the client repo — **Calvin's call, it's a client-repo CI change.**
4. `pr-description` v7 with an assumptions section, re-certified.
