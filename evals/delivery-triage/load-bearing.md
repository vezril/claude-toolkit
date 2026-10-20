# Load-bearing map: delivery-triage (v8)

Documentation, not part of the prompt. The certified prompt is
`skills/delivery-flow/references/triage.md`, byte-identical to `prompts/prompt_v8.md`.

Criteria: **schema** (raw JSON conforming to `triage.schema.json`), **classification** (type,
path and the three flags), **domains** (exact set from the roster vocabulary), **grounding**
(summary and rationale describe this item and invent nothing).

| # | Instruction | Serves | Proven by |
|---|-------------|--------|-----------|
| 1 | Role: first node of a pipeline, classifying what the item says | classification | frames the whole task |
| 2 | Role: not planning the work, not judging the idea | grounding | keeps rationale about the item, v1 → v8 at 30/30 |
| 3 | Task: read the item and write the triage artifact | schema | every case |
| 4 | Context: parsed by `json.loads` with no cleanup step | schema | v2 → v3: the consequence that finally framed the no-fence rule |
| 5 | Context: later steps branch on these fields; a guess sends work to the wrong place | classification, domains | motivates the vocabulary and flag rules |
| 6 | Reply with raw JSON, first character `{`, last `}`, no fence | schema | v1 → v2: Sonnet 0/30 → 30/30 |
| 7 | The exact key list with value types | schema | v1 emitted free-form keys; v2+ exact |
| 8 | The three flags are booleans, never a string or an agent's name | schema, classification | v1 returned `handoff: "solution-architect"` |
| 9 | A worked example of a complete reply | schema | v4 (Haiku 0 → 4/30); on Sonnet it holds 30/30 from v2 |
| 10 | bug / feature / task definitions | classification | case-04 (logging as a task), case-08 (bump), case-09 (defect) |
| 11 | `path` follows from `type`, no size judgement | classification | v6 → v7: a small UI feature was called `quick` |
| 12 | The eight-word domain vocabulary with definitions | domains | v4 → v5: 0 → 12/30, and invented words stopped |
| 13 | UI work is `ux`, never `ux` + `frontend` | domains | v5/v6: `frontend` added beside `ux` 6 times |
| 14 | A service's own config, including operational config, is `backend` | domains | v6 → v7: structured-logging |
| 15 | A service's own API surface is `backend`, not `contracts` | domains | v6: auth-tenancy gained `contracts` |
| 16 | `data` is analytics and pipelines; an app's own schema is `backend` | domains | v5/v6: pantry item gained `data` |
| 17 | An empty `domains` array is a legal answer | domains | case-10, paired with instruction 20 |
| 18 | A technology is not a domain | domains | v4 → v5: "pekko-cluster", "multi-tenancy" stopped appearing |
| 19 | `architecture_change`: boundary moves, including a proposed new service and a cross-cutting layer; not an endpoint or dependency inside one service | classification | v5/v6 over-fired on a metrics endpoint; v6 then under-fired on a new service |
| 20 | `breaking_change`: only when a caller must change; backward-compatible or default-off is not breaking | classification | case-03 (explicitly backward compatible) |
| 21 | `handoff`: only when the item cannot be scoped; a large well-described change is not one; leave `domains` empty | classification, domains | v5/v6: clustering and auth were called handoffs |
| 22 | Summary and rationale use the item's own words; name nothing it doesn't mention | grounding | 30/30 from v4 onward |
| 23 | The rationale says what in the item drove the call | grounding | case-09's generic rationale in v6 |

23 of 23 instructions load-bearing (100%). Every line maps to a criterion and to a run where it
moved, or to a case it holds.
