---
name: gremlin
description: "Writing Gremlin queries well: the hands-on query-language skill, as opposed to the TinkerPop framework. Covers composing a traversal (anchor, navigate, filter, shape, terminate), idiomatic result shaping with project/select/valueMap/elementMap, and a task cookbook: CRUD, mergeV/mergeE upserts and batch writes via inject().unfold(), n-hop neighbourhoods, degree and fan-out, paths and shortest paths, top-k, pagination, grouping and aggregation, conditional logic, string and date handling, deletes. Also covers the semantics that cause wrong answers: laziness and forgotten iterate(), traverser bulk, global vs local scope, as()/select() labels and Pop, path memory, by() targets, missing properties vs null, cross-type comparisons, cardinality, remote results being references. Includes a per-language syntax table (Groovy/Java, Python's as_/in_/and_/not_/is_ renames, JavaScript's in_/from_/with_, .NET and Go PascalCase), testing queries against TinkerGraph and Gremlin Server in Docker, reading profile() output, Gremlint formatting, and provider dialects that change how the same query behaves (Amazon Neptune, Azure Cosmos DB, JanusGraph, TinkerGraph). Use when writing, reviewing, debugging, optimizing, testing or porting a Gremlin query, translating Cypher or SQL to Gremlin, or when a traversal returns nothing, too much, the wrong shape, or runs slowly — even if the user just pastes a g.V()… line. For TinkerPop architecture, Gremlin Server configuration, drivers, serialization and 3.8/4.0 upgrades, see apache-tinkerpop."
license: MIT
---

# Gremlin: writing queries

This is the working skill for **authoring Gremlin**. The framework around it (architecture, Gremlin Server, drivers, serialization, strategies, the 3.8 and 4.0 upgrade notes) is in [[apache-tinkerpop]], and its `references/gremlin-steps.md` is the step catalogue this skill assumes. Cross-links:
- [[graph-databases]]: whether a graph fits, modeling, and Gremlin vs Cypher/GQL/SPARQL.
- [[aws-neptune]]: the most common managed Gremlin target.
- [[opencypher]]: the declarative alternative, for translating Cypher in either direction.
- [[functional-programming]]: Gremlin is a lazy, composable pipeline.
- [[secure-coding]]: never build scripts from user input.
- [[tdd]]: test queries like code.

Grounded in the TinkerPop reference and recipes, the Azure Cosmos DB Gremlin compatibility page and JanusGraph's indexing docs (fetched 2026-09).

## The shape of a good traversal

```
g.V()…              1. ANCHOR     an id, or label + indexed key:    g.V(id) · g.V().has('person','email',e)
   .out('KNOWS')…   2. NAVIGATE   labeled hops; filter edges before crossing them: outE('RATED').has('stars',gte(4)).inV()
   .has(…).dedup()  3. FILTER     as early as possible; dedup before fan-out
   .project(…)…     4. SHAPE      exactly the fields the caller needs
   .toList()        5. TERMINATE  toList / next / iterate (writes!)
```

Read every query in these five parts. Most bugs and slow queries are a missing or misplaced part: no anchor (a scan), unlabeled hops (fan-out), late filters, returning whole elements (references, or huge maps), or no terminal step (nothing happened).

## Result shaping: pick one on purpose

| You want | Use | Note |
|---|---|---|
| a list of one property | `values('name')` | multi-valued properties emit one row per value |
| a flat record per element | `elementMap('name','age')` | includes id and label; single values unwrapped |
| a named record with computed fields | `project('name','friends').by('name').by(out('KNOWS').count())` | **the default choice for APIs** |
| values labeled earlier | `as('a')…as('b')…select('a','b').by('name')` | cross-step joins |
| all properties as lists | `valueMap()` / `valueMap(true)` / `.with(WithOptions.tokens)` | values are **lists**, which surprises everyone |
| the route taken | `path().by('name')` | costs memory. Use only when you need the path |

## Idioms worth knowing by heart

```groovy
// Upsert a vertex (3.6+)
g.mergeV([(T.label):'person', email:'a@x.io']).option(Merge.onCreate, [name:'Ada'])

// Batch upsert: one round trip, many rows
g.inject([[(T.label):'person', email:'a@x.io'], [(T.label):'person', email:'b@x.io']]).unfold().mergeV()

// Neighbours I'm not already connected to
g.V(me).as('me').out('KNOWS').aggregate('f').out('KNOWS').where(neq('me')).where(without('f')).dedup()

// Degree without materialising neighbours
g.V(id).project('out','in').by(outE().count()).by(inE().count())

// Bounded n-hop neighbourhood with depth
g.V(id).repeat(both().simplePath()).emit().times(3).dedup().
  project('id','depth').by(id).by(path().count(local).math('_ - 1'))

// Default when a property is missing
g.V(id).project('nick').by(coalesce(values('nickname'), constant('n/a')))

// Top 10 by a count
g.V().hasLabel('product').order().by(inE('BOUGHT').count(), desc).limit(10).values('sku')

// Conditional write
g.V(id).choose(has('status','active'), property(single,'lastSeen','2026-09-21'), constant('skipped'))
```

The full cookbook is in `references/cookbook.md`.

## Non-negotiables

1. **Anchor on an index.** Make the first `has()` label-scoped and hit an indexed key (JanusGraph composite or mixed index; Cosmos DB indexes everything; Neptune starts best from IDs). Enable scan protection where the provider offers it (JanusGraph `query.force-index`).
2. **End writes with `iterate()`** (or `next()`/`toList()`). A mutation traversal without a terminal step is a silent no-op in code (the Console auto-iterates, so it works there and fails in the app).
3. **Bound loops and fan-out:** `times(n)` or `until(… or loops().is(gte(n)))`, `simplePath()`, and `dedup()` before the next hop. Put `limit()` on anything exploratory.
4. **Shape results explicitly.** Over a remote connection, elements are **references** (id and label only). Use `project`, `elementMap` or `values`, never "return the vertex and read its properties".
5. **Upsert, don't `addV` in a retry loop.** Use `mergeV`/`mergeE`, or `fold().coalesce(unfold(), addV(…))` on providers without merge steps, and supply IDs where the provider allows.
6. **Traversals, not string concatenation.** Build them with a GLV, or pass parameters. If a provider only accepts scripts (Cosmos DB), escape and validate every interpolated value. A script is code.
7. **Check the provider's dialect** for cardinality defaults, ID types, unsupported steps and transactions before trusting a query that worked on TinkerGraph (`references/provider-dialects.md`).
8. **`profile()` before optimizing.** Look for the step where traverser counts explode or index use disappears (for example, a mid-traversal `V()` on Cosmos DB).

## Testing queries

- Iterate fast in the **Gremlin Console** with `TinkerFactory.createModern()` (the 6-vertex "modern" toy graph) or the Air Routes dataset (3.8+).
- For automated tests, run **Gremlin Server with TinkerGraph** in a container (`docker run -p 8182:8182 tinkerpop/gremlin-server:<version matching your driver>`). Seed it per test with `inject(...).unfold().mergeV()` or `addV` chains, and assert on shaped results (`project` maps), not on element objects.
- TinkerGraph tests prove **query logic, not provider behaviour**. Keep a small suite that also runs against the real provider (cardinality, IDs, unsupported steps, performance).
- Format long queries with **Gremlint** (the official formatter; an MCP server ships with 3.8.1). Use one step per line inside nested traversals so reviews read cleanly.

## References

- `references/cookbook.md`: task-by-task queries (reads, writes, batch writes, paths, aggregation, pagination, strings and dates, deletes, subgraphs).
- `references/semantics-and-pitfalls.md`: laziness, bulk, scopes, labels and `Pop`, `by()` behaviour, missing properties and null, comparisons across types, cardinality, `where` vs `has`, and how to read `profile()`.
- `references/glv-syntax.md`: the same queries in Groovy/Java, Python, JavaScript, .NET and Go, plus the renamed-step table and import boilerplate.
- `references/provider-dialects.md`: Neptune, Cosmos DB, JanusGraph and TinkerGraph differences that change results or performance.
