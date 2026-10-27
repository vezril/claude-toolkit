# The trace

`delivery/<ITEM-KEY>/trace.jsonl`, one JSON object per line, appended by hooks rather than
written by steps. It answers the question Stage 4 actually asks: which step produced which
output, on which model, at what cost — and when something failed, where it started.

## Records

A **step record** (written by `trace-step.py` on SubagentStop):

```json
{"ts": "…", "item": "DEM-12", "step": "breakdown", "agent": "general-purpose",
 "session_id": "…", "agent_id": "…", "model": "claude-sonnet-5",
 "input_tokens": 14230, "output_tokens": 1870,
 "cache_creation_tokens": 0, "cache_read_tokens": 12000,
 "api_equivalent_cost_usd": 0.0472, "artifact": "breakdown.json",
 "certified": true, "model_conformant": true}
```

An **edge record** (written by `check-edge.py` on PostToolUse, pass or fail):

```json
{"ts": "…", "item": "DEM-12", "step": "breakdown", "artifact": "breakdown.json",
 "hook": "check-edge",
 "edge": {"name": "parse+schema+sentinel+counts+input-contract", "exit": 1,
          "summary": "sentinel claims stories=8 but the file holds 5"}}
```

A **verdict record**, one per challenge run:

```json
{"ts": "…", "item": "DEM-12", "step": "challenge-breakdown",
 "artifact": "challenge-breakdown.json", "target": "breakdown.json", "verdict": "REFUTED"}
```

The challenge artifact on disk is only the latest verdict; the trace is every one of them.
That is what lets `flow-status.py` and `check-punch-out.py` agree on when a rerun has
become a punch-out — two refutations of the same target, counted from here rather than from
a file that gets overwritten.

## Reading it

- **Token counts come from Claude Code's own transcripts**, never from an agent reporting
  its own usage. Usage is counted once per `message.id`, because a transcript repeats the
  same usage object on every content block of one API message — summing lines overcounts
  several-fold.
- **Cost is `api_equivalent_cost_usd`**: the step's tokens priced at published API list
  rates from `pricing.yaml`. Under a subscription that is not money billed, and the report
  labels it so. A model missing from the table records `null` and `pricing_missing: true`
  rather than a guess.
- **`model_conformant: false`** means the step ran on a heavier model than its registry tier
  — worth knowing, since it is how a Sonnet-tiered pipeline quietly becomes an Opus one.
- **The latest edge per artifact wins.** That is how a rerun clears a failure, and how
  `flow-status.py` decides whether the flow may advance.
- **Edge records are also the write ledger**, and their order is what tells a current
  challenge from a stale one: a target whose last edge record sits after its challenge's
  was written again after it was attacked, so that verdict no longer applies.

`delivery-report.py` rolls this up: outcome and cost per item, distribution per step and
model, and the weekly end-to-end rate — reported both excluding punch-outs and counting them
as unsuccessful, since which one the certification wants is still an open question.
