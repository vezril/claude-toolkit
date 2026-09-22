# Gremlin step catalogue

Examples are in Groovy/Java syntax (the Gremlin Console). GLVs differ only in idiom: Python uses `has_label`, `and_`, `or_`, `not_`, `in_`, `as_`, `is_` to avoid keywords, and JavaScript/.NET use camelCase or PascalCase. Import `__`, `P`, `TextP`, `T`, `Merge`, `Direction`, `Cardinality` and `Order` statically.

## Start steps (on `g`)

| Step | Purpose |
|---|---|
| `V(ids…)` / `E(ids…)` | start at vertices or edges (all of them if there are no IDs, which is a scan) |
| `addV(label)` / `addE(label)` | create an element. `addE` needs `from()`/`to()` |
| `mergeV(map)` / `mergeE(map)` | upsert (below) |
| `inject(values…)` | start from arbitrary values |
| `union(t…)` | start from several child traversals (a start step since 3.7) |
| `call(service, params)` | a provider-defined service or procedure (3.6+) |

## Navigation

| Vertex → vertex | Vertex → edge | Edge → vertex |
|---|---|---|
| `out(labels)`, `in(labels)`, `both(labels)` | `outE`, `inE`, `bothE` | `outV`, `inV`, `bothV`, `otherV` |

Filter edges on their properties with `outE('rated').has('stars', gte(4)).inV()`.

## Filters

- `has(key, value|P)`, `has(label, key, value)`, `hasLabel`, `hasId`, `hasKey`, `hasValue`, `hasNot(key)`
- `where(traversal)`, `where(P)` with `as()` labels (e.g. `where(neq('a'))`)
- `is(P)` filters the current value: `count().is(gt(10))`
- `and(t…)`, `or(t…)`, `not(t)`, `filter(t)`
- `dedup()` / `dedup().by(key)`, `range(lo,hi)`, `limit(n)`, `skip(n)`, `tail(n)`, `coin(p)`, `sample(n)`
- `simplePath()` (no repeated elements), `cyclicPath()`

**Predicates.**
- `P`: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `between(lo,hi)` (lo inclusive, hi exclusive), `inside`, `outside`, `within(…)`, `without(…)`, and `.and()` / `.or()` to combine
- `TextP`: `startingWith`, `endingWith`, `containing`, and their `not…` forms, plus `regex` (3.6+)

## Maps and projections

- **Values:** `values(keys)`, `valueMap(keys)` (multi-values come back as lists; `.with(WithOptions.tokens)` adds id and label), `elementMap(keys)` (flat, includes id, label and edge endpoints), `propertyMap()`, `properties()`, `key()`, `value()`, `id()`, `label()`, `element()`, `constant(x)`.
- **Shaping results:**
  - `project('a','b').by(...).by(...)`: build a map from the current element. This is the idiomatic result shape.
  - `select('a','b')`: read values labeled earlier with `as()`
  - `path()` with `by()` per element, and `tree()`
- **Aggregates:** `count()`, `sum()`, `min()`, `max()`, `mean()`, `fold()` / `unfold()`, `group().by(k).by(v)`, `groupCount().by(k)`, `order().by(k, desc)`. Add `local` scope to operate *inside* a collection: `order(local)`, `limit(local, n)`, `count(local)`.
- **`math('_ * 2 + a')`** for arithmetic over the current value and labels.
- **String steps** (3.7+): `asString`, `toUpper`, `toLower`, `trim`/`lTrim`/`rTrim`, `substring`, `split`, `replace`, `concat`, `length`, and `format('%{name} is %{age}')`.
- **Date and number steps:** `asDate`, `dateAdd`, `dateDiff` (returns **milliseconds** from 3.8.0, seconds before), `asNumber`, and 3.8's type predicates and number-conversion steps.

## Branching and looping

- `choose(pred, t1, t2)` is if/else. `choose(t).option(v1, t1).option(v2, t2).option(none, t3)` is a switch. **3.8.0:** only the *first* matching option runs, and an unmatched traverser passes through.
- `coalesce(t1, t2, …)`: the first child traversal that produces anything.
- `optional(t)`: `t`'s result if any, otherwise the current traverser.
- `union(t1, t2)`: all children, results concatenated.
- `local(t)`: run `t` per object. From 3.8.0, bulked traversers are split so this is truly per object.
- `repeat(t)`:
  - `.times(n)` for a fixed count
  - `.until(cond)` before `repeat` for a while-do, or after it for a do-while
  - `.emit()` / `.emit(cond)` to output intermediate results
  - `loops()` gives the depth
  - 3.8.0 made `limit`/`range`/`skip` inside `repeat` track per iteration, and disallows `cap()`/`inject()` inside it
- `match(as('a').out().as('b'), …)`: declarative pattern matching. Usually slower than an explicit traversal, so profile it.

## Side effects and mutation

- `property([cardinality,] key, value)`. Cardinality is `single` (replace), `set` (add if absent) or `list` (append). The default is **provider-defined**: TinkerGraph uses `single`, Neptune uses `set`. Meta-properties: `property('name','marko','acl','public')` on providers that support them.
- `addE('knows').from(__.V(a)).to(__.V(b))` (or `from('labelA')` with `as()`).
- `drop()` removes elements or properties. `sideEffect(t)`, `aggregate('x')` (eager; `store()` and `aggregate(Scope)` were **removed in 3.8.0**), `cap('x')`, `subgraph('sg')`, `sack()` with `withSack(init)`.

### mergeV / mergeE (upserts, 3.6+)

```groovy
// Vertex: match on label + key properties; set extra properties only on create or match
g.mergeV([(T.label): 'person', email: 'a@x.io']).
    option(Merge.onCreate, [name: 'Ada', created: '2026-09-21']).
    option(Merge.onMatch,  [lastSeen: '2026-09-21'])

// Edge: endpoints by ID via Direction keys; the label and properties form the match key
g.mergeE([(T.label): 'knows', (Direction.from): 'p1', (Direction.to): 'p2']).
    option(Merge.onCreate, [since: 2026])

// Edge with endpoints resolved from earlier steps
g.V('p1').as('a').V('p2').as('b').
  mergeE([(T.label): 'knows', (Direction.from): Merge.outV, (Direction.to): Merge.inV]).
    option(Merge.outV, select('a')).option(Merge.inV, select('b'))
```

- The match map is the identity. `onCreate` values are added on insert, and `onMatch` values are applied to an existing element.
- Inside `onMatch`, multi-valued providers may append rather than replace, depending on cardinality defaults. Specify cardinality where the provider supports it.
- **3.8.0:** a mid-traversal `mergeV`/`mergeE` now outputs the **created or matched element**, not the incoming traverser.

## Terminal and introspection steps

`next()`, `next(n)`, `tryNext()` (Optional), `hasNext()`, `toList()`, `toSet()`, `iterate()` (for writes), `explain()` (the strategy-rewritten plan), `profile()` (per-step time, traverser and element counts).

## Traversal strategies

Apply them with `g.withStrategies(...)` / `g.withoutStrategies(...)` (grammar support for the latter since 3.8.0).

| Strategy | Use |
|---|---|
| `PartitionStrategy` | multi-tenancy: writes stamp a partition key, and reads see only chosen partitions |
| `SubgraphStrategy` | restrict traversals to vertices, edges or properties matching filters |
| `ReadOnlyStrategy` | reject mutating steps, for read-only endpoints and roles |
| `ElementIdStrategy` | map a property to element IDs on graphs without user-supplied IDs |
| `EventStrategy` | callbacks on mutations |
| `SeedStrategy` | deterministic `coin`, `sample` and `shuffle` |
| `EdgeLabelVerificationStrategy`, `VertexProgramDenyStrategy`, … | verification guards |

Optimization strategies (step folding, `has()` push-down into indexes, and so on) are applied automatically, and providers add their own. `explain()` shows the result.
