---
name: post-summary
description: "Write the comment that goes back on the tracker item — what was done, where it is, and what is still open. Emits post.md."
---

# Write the post-back

**This prompt is not yet certified.** `post-summary` must be listed in `allow_uncertified` for
the flow to run it, every run is traced `certified: false`, and those runs are excluded from the
certified-only end-to-end rate. Do not cite a `full`-profile success rate as a Stage 4 number
while this node lacks a `prompt-edd` package. Editing this file does not un-certify anything,
because there is nothing to un-certify yet.

## Who reads this

The person who filed the ticket, in their tracker, where `tracker.external: true` means it is
very likely **not your organisation's**. They did not ask for a development diary. They asked
whether their problem is fixed, and they need enough to verify that themselves.

Write for someone who knows the product and does not know this pipeline.

## Inputs

You are given, and may read nothing else:

- `item.json` — the ticket as the tracker holds it, including any issue it references
- `implementation.json` — what was changed, which files, which tests, and any recorded caveats
- `verify.json` — the test and protected-path results
- `challenge-implementation.json` — the adversarial verdict on the implementation
- `pr-opened.json` and `pr.md` — where the change now lives
- `carry_forward` — findings from a `WEAKENED` verdict that you are required to address

You do not get the conversation that produced any of them. Everything you assert has to be
traceable to one of these files.

## What to produce

A single file, `post.md`, in the item's delivery directory.

**Do not write a sentinel.** `write-sentinel.py` derives its counts from an artifact's schema,
and the terminal prose artifacts — `post.md`, `pr.md`, `summary.md` — have none, so it exits 2
with "no schema for post.md". That is the tool being correct, not a misconfiguration: a sentinel
is a node's claim about counts a schema defines, and there is nothing countable here. Writing the
file is the whole of the step.

Cover these, in this order, and nothing else:

1. **What was wrong**, in one sentence, in the reporter's terms — not the code's.
2. **What changed**, naming the files and the actual change. A one-line fix should read as a
   one-line fix; do not inflate it.
3. **How it was verified.** Name the tests that now cover it and say what the suite did. If any
   test in the change passes against the unfixed code, say so and say what it does guard —
   `implementation.json` records this, and omitting it overstates the evidence.
4. **Where the change is** — the branch and the PR link from `pr-opened.json`, verbatim.
5. **What is still open**, if anything: out-of-scope follow-ups the work uncovered, caveats from
   `verify.json`, and anything the reporter has to do. Name them plainly enough that the reporter
   can raise a ticket from the sentence alone.

If an item in 3 or 5 is empty, leave the whole point out rather than writing "none".

## Format, which the adapter enforces

`post.md` is **plain text split into paragraphs by blank lines**, because the tracker adapter
converts each blank-line-separated block into one paragraph and discards everything else.
Markdown does not survive the trip:

- no headings, no bullet or numbered lists, no tables, no code fences, no bold or italics;
- a URL on its own is fine — write it bare, not as a link;
- one blank line between paragraphs, and no trailing blank line.

A list written as markdown arrives as one run-on paragraph with stray hyphens in it. Where you
need to enumerate, use a sentence.

Four short paragraphs is a good length. Eight is too many.

## The rules

- **Never claim a test result you were not given.** `verify.json` and `implementation.json` are
  the only sources for what passed. A suite that did not run green is reported as it is, with
  the reason — a reporter who later finds out is owed better.
- **Say "we" about the change, never name the tooling.** No mention of this pipeline, its steps,
  its artifacts, punch-outs, decisions, verdicts, agents, models, retries, costs, the vault, or
  how long anything took. None of it is the reporter's business and some of it is confidential.
- **No speculation and no promises.** Do not commit to dates, future tickets, or releases. "This
  needs its own ticket" is a fact about scope; "we will fix this next sprint" is a commitment you
  cannot make on someone else's backlog.
- **Address the carry-forward findings.** A `WEAKENED` verdict means the implementation record was
  right but incomplete. Where a finding changes what the reporter should believe about the
  evidence, it belongs in the comment; where it does not, leave it out. Silently dropping one
  that does is the failure this step is most prone to.
- **Nothing is checked after you.** `post.md` has no schema and no prose edge, so no gate will
  catch a wrong link or an inflated claim. The next thing that happens is the adapter posting
  this, unedited, to someone else's tracker.

## Judgement

- **Lead with the answer.** The first sentence says whether the reported problem is fixed.
- **Prefer the reporter's words.** They wrote a reproduction; mirror its vocabulary rather than
  renaming their concepts to match the code's.
- **Shorter is more credible.** A four-paragraph comment that cites a PR and two test names reads
  as finished work. A fifteen-paragraph one reads as justification.
