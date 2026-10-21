# Load-bearing map: delivery-breakdown (v6)

Documentation, not part of the prompt. The certified prompt is
`skills/delivery-flow/references/breakdown.md`, byte-identical to `prompts/prompt_v6.md`.

Criteria: **schema** (raw JSON conforming to `breakdown.schema.json`), **coverage** (every
deliverable the item asks for appears), **acceptance** (criteria distinct, specific, observable),
**scope** (right item key, domains within triage's, nothing invented, reviewable size).

| # | Instruction | Serves | Proven by |
|---|-------------|--------|-----------|
| 1 | Role: planning node; turns an item into the unit implementers build from | coverage | frames the task |
| 2 | Role: plan what the item asks for; don't design the solution or add unrequested work | scope | v1 scope 16/18, invented work in the misses |
| 3 | Task: read the item and its triage artifact | scope | domains rule depends on triage being read |
| 4 | Context: parsed by `json.loads` with no cleanup step | schema | v5 → v6: moving this away from the rule cost 7 of 18 runs |
| 5 | Context: stories are dispatched by `domains`; criteria become the tests | domains, acceptance | motivates instructions 10 and 13 |
| 6 | Raw JSON, first character `{`, no fence, with the parse-error consequence beside it | schema | v1 → v2 (0 → 16/18), v5 → v6 (restored to 18/18) |
| 7 | The exact shape with exactly these keys | schema | v1 emitted free-form shapes |
| 8 | Id patterns `E1`, `S1`, `AC1`, no prefixes or dots | schema | schema validation, every case |
| 9 | A worked example of the opening | schema | triage's v4; holds Sonnet at 18/18 here |
| 10 | Account for everything the item names, including a detail mentioned once | coverage | v3 → v4: "client component", "idempotent" misses |
| 11 | Name things the way the item names them; don't introduce files or services | scope | v1 scope failures; 18/18 from v3 |
| 12 | Every epic has a story, every story a criterion; not one giant story, not one per line | scope | story counts stay 3–10 per case |
| 13 | Domains from the eight roster words, drawn from triage's set, never more | scope | v2 → v3: `security` invented, then 18/18 |
| 14 | A technology is not a domain | scope | same run: clustering and auth tagged as domains |
| 15 | `then` states an observable outcome; "it works" is not one | acceptance | the vague-outcome check, every case |
| 16 | Criteria may share an outcome when preconditions differ; what they may not be is the same criterion twice | acceptance | v4: the assert correction, auth-tenancy |

16 of 16 instructions load-bearing (100%).
