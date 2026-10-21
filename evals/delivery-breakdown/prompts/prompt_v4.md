Break this work item down into epics, stories and acceptance criteria.

## Output
Reply with raw JSON and nothing else. The first character of your reply is `{` and the last is `}`: no preamble, no commentary, no code fence. Your reply is written straight to `breakdown.json` and parsed by `json.loads` with no cleanup step, so a fence is a parse error and the step fails.

Use exactly this shape, with exactly these keys and no others:

```
{
  "item": string,                       the item's key, copied exactly
  "epics": [
    {
      "id": "E1",                       E followed by digits
      "title": string,
      "stories": [
        {
          "id": "S1",                   S followed by digits
          "statement": string,
          "domains": [string],
          "acceptance_criteria": [
            {"id": "AC1", "given": string, "when": string, "then": string}
          ]
        }
      ]
    }
  ]
}
```

Every epic has at least one story, every story at least one acceptance criterion. Ids match those patterns exactly: `E1`, `S1`, `AC1` — no prefixes, no dots, no `EPIC-1`.

## Domains
A story's `domains` says which kinds of work it touches, using only these words:
`ux`, `frontend`, `backend`, `contracts`, `infra`, `data`, `mobile`, `docs`.

Draw them from the `domains` the triage artifact already found: a story may touch fewer than
triage listed, never more. A technology is not a domain — authentication, clustering and
logging are `backend` or `infra` work, not domains of their own.

## Covering the item
Work through the item and account for everything it asks for. Every change it names — each
field, each screen, each endpoint, each toggle, each stated rule about how something must
behave — belongs to some story. A detail mentioned once in passing still counts: if the item
says the work must be idempotent, or that a component becomes a client component, that is a
story or an acceptance criterion, not something to leave out because it is small.

Within a story, no two acceptance criteria assert the same outcome. If two criteria would end
with the same `then`, they are one criterion, or one of them is testing something you have not
said yet.
