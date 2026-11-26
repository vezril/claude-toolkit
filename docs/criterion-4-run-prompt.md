# The prompt for collecting criterion 4 evidence

Paste the block below into a **fresh Claude Code session opened in
`/Users/mferecal/Code/nx-neptune`**. The cwd is the whole point: `hooks/trace-step.py` records
step records only when the session is working in the delivery repo, so a session rooted
anywhere else produces a run with no evidence and no way to tell from the outside.

---

```
Collect Stage 4 criterion 4 evidence: certified triage-profile delivery-flow runs.

Read the `delivery-flow` skill first. It owns sequence and state; you own none of it.

## The one rule that matters

**STOP when `flow-status.py` says the triage profile is finished.** The profile ends at
`report` / `outcome.json`. Do not continue into `propose`, `implementation`, `open-pr` or
`post-summary` — those nodes are uncertified, and a run that touches them cannot count toward
the rate no matter how well it went. This is exactly how AN-3702 was lost: 232 recorded steps,
profile `triage`, and zero of it usable because it ran on past the terminus.

Continuing into the next profile is a separate invocation, and nobody is asking for one.

## What to run, per ticket

1. `python3 /Users/mferecal/Code/claude-toolkit/scripts/delivery-flow/ensure-worktree.py <KEY>`
   — idempotent; run it again on every resumption. **Never work around a refusal from it.**
2. `python3 /Users/mferecal/Code/claude-toolkit/scripts/delivery-flow/flow-status.py <KEY>`
   — it prints `Next: <step>` or `BLOCKED — <reason>`. Do what it says, one step per loop.
3. Repeat 2 until it reports the profile finished.
4. Close the run:
   `python3 /Users/mferecal/Code/claude-toolkit/scripts/delivery-flow/write-outcome.py <KEY> --replay`

   **`--replay` is required here** and is not optional bookkeeping. These are tickets already
   closed in Jira, so the runs are replays; the report discloses the replay share of the
   denominator, and an undisclosed replay padding a success rate is the kind of thing that
   sinks a submission.

## Which tickets

Pick **5 to 10** closed tickets from the project. Five is the gate's stated minimum
denominator; more is better and the rate is per-run, so a failure is still useful evidence.

Already used, do not reuse: AN-3664, AN-3665, AN-3666, AN-3667, AN-3669, AN-3702, AN-3703,
AN-3749, and anything under a `DISCARDED-` prefix in the artifacts root.

Find candidates with the tracker adapter, not with an MCP connector:
`python3 /Users/mferecal/Code/claude-toolkit/scripts/delivery-flow/adapters/jira.py related <KEY>`
or ask Calvin for the keys. A bug or task takes the quick path and skips the breakdown — that
is correct and comes from `triage.json`, not from your judgement.

## Things that will tempt you, and the answers

- **A failed edge** — rerun the producing step with the edge report, at most 3 times. Never
  hand-edit an artifact to get past one: the trace compares shas, and a corrected artifact marks
  the run `failed` with reason `manual-correction`. A failed run honestly recorded is worth more
  than a laundered one.
- **A punch-out** — stop, name the file (`delivery/<KEY>/punch-out-<n>.md`), and tell Calvin.
  Decisions are his and only his. A punched-out run is a legitimate terminal outcome; it is not
  a problem you fix.
- **A REFUTED challenge** — `flow-status.py` applies the routing. Twice on the same target is a
  punch-out, not a third attempt.
- **A WEAKENED challenge** — proceeds. The findings come back under `carry_forward` and the
  consuming step must address each one.
- **An uncertified step appearing in the chain** — that means you have left the profile. Go
  back and check what produced the artifact that is not in the triage slice.

## Reporting

Follow `writing-for-adhd` for every message to Calvin: four sentences at the outside, name the
path instead of pasting the artifact, one decision per message, end on one concrete next action.

When the batch is done, run
`python3 /Users/mferecal/Code/claude-toolkit/scripts/delivery-flow/check-submission.py`
from `/Users/mferecal/Code/nx-neptune` and report the single line of its verdict plus the count
of certified terminal runs. That script is the gate; your own read of whether it went well is
not evidence.
```

---

## Why this session can't do it

`hooks/trace-step.py:106-109` resolves the repo from the hook payload's `cwd` and returns
early when that repo has not opted into the workflow. A session rooted in `claude-toolkit`
drives the steps fine and records nothing, which is the honest behaviour and also why the
evidence has to be gathered from a session rooted in the delivery repo.
