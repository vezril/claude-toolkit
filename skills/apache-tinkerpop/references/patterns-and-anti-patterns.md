# Gremlin patterns and anti-patterns

Based on TinkerPop's *Recipes* document (fetched 2026-09) plus common practice.

## Recipes

**Get or create (idempotent write).** Prefer `mergeV`/`mergeE` (see `gremlin-steps.md`). The pre-3.6 idiom, still useful on older providers:
```groovy
g.V().has('person','email','a@x.io').fold().
  coalesce(unfold(), addV('person').property('email','a@x.io')).
  property(single, 'lastSeen', '2026-09-21')
```

**Shortest path (unweighted):**
```groovy
g.V(startId).repeat(out().simplePath()).until(hasId(endId)).path().limit(1)
```
Add a depth guard on large graphs: `.until(hasId(endId).or().loops().is(gte(6)))`, then filter for the target. For weighted shortest paths, use a provider's algorithm (`shortestPath()` step on some providers, or OLAP).

**Cycle detection** (cycles of length 3 back to the start):
```groovy
g.V().as('a').repeat(out().simplePath()).times(2).
  where(out().as('a')).path().
  dedup().by(unfold().order().by(id).dedup().fold())
```

**Pagination:** stable order first, then `range`:
```groovy
g.V().hasLabel('product').order().by('sku').range(40, 60).valueMap('sku','name')
```
Deep offsets still scan everything before them. For large result sets, use keyset pagination (`has('sku', gt(lastSku)).order().by('sku').limit(20)`).

**Recommendation (collaborative filtering):**
```groovy
g.V(userId).out('bought').aggregate('mine').
  in('bought').where(neq(userId)).            // similar users
  out('bought').where(without('mine')).       // their items I don't have
  groupCount().order(local).by(values, desc).limit(local, 10)
```

**Tree / hierarchy:** get descendants with `repeat(out('child')).emit()`. Get the root with `repeat(in('child')).until(__.not(__.in('child')))`. Use `tree()` for a nested map.

**Duplicate detection:** `group().by(project('a','b').by('email').by('name')).unfold().where(select(values).count(local).is(gt(1)))`. For duplicate edges, group by `[outV, label, inV]`.

**Moving an edge:** read its properties, `addE` the new edge with them, then `drop()` the old one, all in one transaction.

Other recipes cover **centrality** (degree, betweenness, closeness, eigenvector, PageRank; OLTP versions are fine on small graphs, and big graphs need OLAP or a provider algorithm), **connected components** (`connectedComponent()` step, OLAP), **collections**, **if-then grouping**, **looping**, **element existence**, **operating on dropped elements**, **traversal-induced values**, and **OLAP with Spark**.

## The official anti-patterns

1. **Long traversals.** Huge single traversals (a thousand chained `addV` calls, for example) are hard to read, compile and debug, and they can exceed request limits. Batch them into reasonable chunks, or use the provider's bulk loader.
2. **Unspecified keys and labels.** `g.V().has('name','x')` and `out()` without a label make the engine consider everything. Always name labels and keys.
3. **Unnecessary steps.** For example `values('x').fold().unfold()`, or `select` after `project` when `project` already shaped the result.
4. **Unspecified label in a global vertex lookup.** `g.V().has('email', x)` can't use a label-scoped index. Write `g.V().has('person','email',x)`.
5. **Steps instead of tokens.** Prefer `by(T.id)`/`by(T.label)` tokens and simple `by('key')` over sub-traversals where they do the same thing.
6. **`has()` with traversal arguments.** The `has(key, traversal)` form was removed in 3.8.0. Filter with `where()` instead.

## Performance habits

- `profile()` before and after every optimization. Watch **traverser counts** exploding at `out()` steps: that's fan-out through a supernode (see [[graph-databases]]).
- Filter early: push `has()` next to the start, and filter edges by label and properties (`outE('rated').has(...)`) before hopping.
- Project only what you need (`project`/`values`), not whole `valueMap()`s of wide vertices. Over the network, elements come back as **references** (id and label) by default, so projecting is also the only way to get properties reliably.
- Put `dedup()` early in expanding traversals, and `limit()` on exploratory queries.
- Use `aggregate` + `without` for "not already seen" filters, rather than repeated sub-traversals.
- Keep write transactions small, and retry on the provider's conflict exception.

## Gremlin ↔ Cypher quick map

| Intent | Gremlin | Cypher |
|---|---|---|
| Lookup | `g.V().has('Person','name','Al')` | `MATCH (p:Person {name:'Al'})` |
| One hop | `.out('KNOWS')` | `-[:KNOWS]->(f)` |
| 1–3 hops | `.repeat(out('KNOWS')).times(3).emit()` | `-[:KNOWS*1..3]->(f)` |
| Filter on hop | `.where(values('age').is(gt(30)))` | `WHERE f.age > 30` |
| Shape result | `.project('n','a').by('name').by('age')` | `RETURN f.name AS n, f.age AS a` |
| Count by key | `.groupCount().by('city')` | `RETURN f.city, count(*)` |
| Upsert | `mergeV([(T.label):'P', id:1])` | `MERGE (:P {id:1})` |
| Optional | `.optional(out('HAS'))` / `coalesce` | `OPTIONAL MATCH` |

Gremlin is imperative (you choose the walk order), while Cypher is declarative (the planner chooses). Porting in either direction means rethinking the start point and the hop order, not just translating syntax.
