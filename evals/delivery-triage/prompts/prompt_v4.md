Classify this work item for the delivery pipeline.

Return JSON with: item, type, path, domains, summary, rationale, handoff, handoff_reason, architecture_change, breaking_change.

## Output
Reply with raw JSON and nothing else. The first character of your reply is `{` and the last is `}`: no preamble, no commentary, no code fence.

Use exactly these keys and these value types:

```
{
  "item": string,                  the item's key, copied exactly
  "type": "bug" | "feature" | "task",
  "path": "quick" | "standard",
  "domains": [string],             the kinds of work this touches
  "summary": string,               one sentence on what the item asks for
  "rationale": string,             why you classified it this way
  "handoff": true | false,
  "handoff_reason": string | null, required when handoff is true, otherwise null
  "architecture_change": true | false,
  "breaking_change": true | false
}
```

`handoff`, `architecture_change` and `breaking_change` are booleans, never strings and never the name of a person or an agent. No other keys.

Your reply is written straight to `triage.json` and parsed by `json.loads` with no cleanup step. A ```json fence, or any sentence before or after the object, is a parse error and the step fails. Begin with `{`.

A correct reply looks exactly like this, in full:

{"item":"ABC-1","type":"bug","path":"quick","domains":["backend"],"summary":"The export endpoint returns 500 on an empty range.","rationale":"A defect report against existing behaviour with a clear reproduction.","handoff":false,"handoff_reason":null,"architecture_change":false,"breaking_change":false}
