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
