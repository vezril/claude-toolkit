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
  "domains": [string],             the kinds of work this touches, from the list below
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

## Domains
`domains` uses only these words. Pick every one the work touches, and nothing else — an
empty array is the right answer when the item names no work you can place.

- `ux` — what a person sees and operates: screens, navigation, layout, copy, visual assets
- `frontend` — browser application code where the concern is the code rather than the design
- `backend` — services, APIs, domain logic, persistence
- `contracts` — shared interface definitions other services compile against
- `infra` — build, CI, containers, charts, deployment, observability plumbing
- `data` — schemas, migrations, pipelines, analytics
- `mobile` — iOS or Android applications
- `docs` — documentation written for people

A technology is not a domain: Pekko clustering, authentication and logging are all `backend`
or `infra` work, not domains of their own.

## The three flags
Each flag is false unless its own test is met. They are independent: a large change can set
none of them.

- `architecture_change` — true when the change moves a boundary: a new or removed service, a
  new runtime topology (clustering, sharding, a queue between services), or a change to how
  services find or authenticate to each other. Adding an endpoint, a dependency, logging or
  metrics *inside* one service is not an architecture change, however much code it touches.
- `breaking_change` — true when something that works today stops working unless its caller
  changes: a removed or renamed field, changed semantics, an incompatible migration. A change
  the item describes as backward compatible, or that ships behind a default-off switch or a
  compatibility mode, is not breaking.
- `handoff` — true when the item cannot be scoped from what it says: it proposes a whole new
  service with a sentence of description, or it asks for contradictory things, or the decision
  is someone's to make rather than yours. A large, well-described change is not a handoff. When
  `handoff` is true, give the reason and leave `domains` empty — do not guess the shape of work
  you are handing back.
