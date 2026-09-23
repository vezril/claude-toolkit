---
name: opencypher
description: "Writing openCypher queries: the hands-on Cypher 9 language skill, distilled from the openCypher Cypher Query Language Reference v9 and the openCypher Cypher Style Guide. Covers the property graph model; patterns (node, relationship, label, property, type alternation, variable-length *min..max, zero-length, named paths, shortestPath/allShortestPaths) and relationship uniqueness within one MATCH; the query-part model (clauses as table-to-table functions, WITH as the barrier for aggregation filters and read/write switching, eager clause-by-clause state visibility); every clause (MATCH, OPTIONAL MATCH, MANDATORY MATCH as a proposal, RETURN, WITH, UNWIND, WHERE, ORDER BY, SKIP, LIMIT, CREATE, DELETE/DETACH DELETE, SET/+=, REMOVE, MERGE, CALL…YIELD, UNION/UNION ALL); types and coercion, lists/slicing/list and pattern comprehension, map projection; three-valued null logic and IN; comparability vs equality vs orderability vs equivalence and how aggregation uses them; CASE simple vs generic; parameters ($param, and what can't be parameterized); the full function catalogue with null and error behaviour; reserved words; and the style guide's formatting and naming rules (UPPER keywords, lower null/true/false, camelCase variables and properties, PascalCase labels, UPPER_SNAKE relationship types, single quotes, no semicolons, anchors first, outgoing arrows). It also flags where the two documents contradict themselves or each other, and where Cypher 9 differs from what Neo4j 5, Neptune and GQL accept today. Use when writing, reviewing, formatting, debugging or explaining a Cypher/openCypher query, designing labels and relationship types, translating SQL or Gremlin to Cypher, or when a query returns nothing, too many rows, duplicates or unexpected nulls, even if the user just pastes a MATCH (…) line."
license: MIT
---

# openCypher (Cypher 9)

This is the working skill for **writing Cypher**. It comes from two openCypher documents: the **Cypher Query Language Reference, Version 9** (Apache 2.0), which defines the language, and the **Cypher Style Guide**, which says how to write it readably. Cypher 9 is the openCypher baseline that Neo4j 3.x–4.x, Amazon Neptune, Memgraph, Apache AGE, FalkorDB and others implement or extend.

Cross-links:
- [[graph-databases]]: whether a graph fits, modeling, the landscape, and Cypher vs GQL / SQL-PGQ / Gremlin / SPARQL.
- [[gremlin]]: the imperative alternative, for translating queries in either direction.
- [[aws-neptune]]: Neptune's openCypher dialect and its gaps (no APOC, string IDs, one graph per cluster).
- [[nx-neptune]]: runs `CALL neptune.algo.*` openCypher on Neptune Analytics.

## The mental model

```
Query       = one or more query PARTS, then an optional final RETURN
Query part  = reading clauses (MATCH / OPTIONAL MATCH / UNWIND / CALL)
              and/or writing clauses (CREATE / MERGE / SET / DELETE / REMOVE)
Each clause = function(table of variable bindings) -> table
              (rows are unordered maps; nothing is ordered unless ORDER BY says so)
WITH        = the barrier between parts: projects, aggregates, filters, reorders, and
              is the ONLY place a variable crosses into the next part
RETURN      = the full stop. Mandatory for read-only queries, optional after writes
Eagerness   = each clause sees every change made by earlier clauses and none made by later ones
```

Read → write needs no `WITH`, because the switch is implicit. Anything else, such as filtering on an aggregate or reading after a write, needs an explicit `WITH`.

## Non-negotiables

1. **`WHERE` belongs to the clause right before it.** On `MATCH`/`OPTIONAL MATCH`, `WHERE` is part of the pattern, not a filter applied afterwards. On `OPTIONAL MATCH`, a condition in its own `WHERE` keeps the outer row and gives you `null`s. The same condition in a later `WITH … WHERE` drops the row. Put each predicate with the `MATCH` it constrains.
2. **Filter aggregates through `WITH`.** `MATCH … WITH n, count(m) AS c WHERE c > 3 RETURN …`. There's no `HAVING`. Grouping keys are **implicit**: every non-aggregate expression in the projection is a key. Adding a column to `RETURN` silently changes the grouping.
3. **A relationship is used at most once in each `MATCH` pattern.** A friends-of-friends pattern never returns the start person, because the edge back is already used. Split it into two `MATCH` clauses to allow reuse. A comma inside one `MATCH` is still one pattern, so uniqueness still applies.
4. **`null` is "unknown", not a value.** `null = null` is `null`. Anything that isn't `true` is dropped by `WHERE`. `2 IN [1, null]` is `null`, not `false`. `NOT (x = null)` is still `null`. Test with `IS NULL` / `IS NOT NULL`. A missing property reads as `null`, and properties can't store `null`: setting a property to `null` removes it.
5. **The simple `CASE` form compares values, it doesn't test conditions.** `CASE n.age WHEN n.age IS NULL THEN -1 …` compares `n.age` with a boolean and never matches. Conditions need the generic form: `CASE WHEN n.age IS NULL THEN -1 ELSE n.age - 10 END`.
6. **`MERGE` is all-or-nothing, for the whole pattern.** `MERGE (a)-[:R]->(b:B {k: 1})` with `a` bound creates a new `b` every time the *whole* path is missing, even when a matching `B` exists. MERGE the nodes first, then the relationship. Pattern properties must match **exactly**. MERGE can't take a map parameter (`MERGE (n $props)` is invalid). Write `{name: $p.name}`. An undirected MERGE creates the relationship in an arbitrary direction.
7. **Parameterize values, never structure.** `$param` works for literals, expressions, SKIP/LIMIT and ids. It **can't** be used for labels, relationship types or property keys (`n.$key` is invalid). Only `CREATE (n $props)` accepts a whole-map parameter. Never build values into the query by string concatenation. That's an injection risk and it defeats plan caching.
8. **`SET n = map` replaces all properties. `SET n += map` merges them.** `SET a = b` copies b's properties and deletes all of a's others. A `null` value in a `+=` map deletes that key.
9. **You can't `DELETE` a node that still has relationships.** Delete the relationships first, or use `DETACH DELETE`. After a `DELETE`, returning the deleted element gives you an invalid reference.
10. **Bound variable-length paths, and put anchors first.** `-[*]-` explores unbounded paths. Give an upper bound (`*..5`) and start from a selective, labeled, property-constrained anchor. Properties on a var-length pattern (`[* {blocked: false}]`) apply to **every** relationship in the path. Var-length patterns can't be used in `CREATE` or `MERGE`.
11. **Don't rely on `id()`.** Ids are implementation-internal and can be reused after deletion. Model your own key property (a constraint or unique index, depending on the product).
12. **Order is undefined without `ORDER BY`.** SKIP/LIMIT without ORDER BY returns arbitrary rows. To sort a `collect()`, run `WITH … ORDER BY … LIMIT …` before it. `null` sorts **last ascending** and **first descending**.

## Quick reference

| Need | Cypher 9 |
|---|---|
| Anchor + expand | `MATCH (p:Person {name: $name})-[:KNOWS]->(f:Person)` |
| Either type | `-[:ACTED_IN\|DIRECTED]->`. Only in MATCH or expressions, never CREATE/MERGE |
| 1 to 3 hops | `-[:KNOWS*1..3]-`; fixed `*2`; open `*3..`, `*..5`; zero-length `*0..1` includes the start node |
| Path + parts | `MATCH p = (a)-[*..4]->(b) RETURN nodes(p), relationships(p), length(p)` |
| Shortest | `MATCH (a…), (b…), p = shortestPath((a)-[*..15]-(b))`; `allShortestPaths(…)` |
| Outer join | `OPTIONAL MATCH (a)-[r:R]->(x)` gives `x`/`r` as `null` when nothing matches |
| Existence filter | `WHERE (a)-[:R]->(:B)` / `WHERE NOT (a)-->(b)` (one path, no new variables) |
| Property exists | `WHERE exists(n.prop)` (v9) or `WHERE n.prop IS NOT NULL` (portable) |
| Top-N then expand | `MATCH … WITH m ORDER BY m.score DESC LIMIT 10 MATCH (m)-->(x) RETURN …` |
| Batch write | `UNWIND $rows AS row MERGE (n:Label {key: row.key}) SET n += row.props` |
| Upsert | `MERGE (n:L {key: $k}) ON CREATE SET n.created = timestamp() ON MATCH SET n.seen = timestamp()` |
| Shape output | `RETURN p {.name, .age, friends: collect(f {.name})}` (map projection) |
| List ops | `[x IN list WHERE x > 0 \| x * 2]`, `list[1..3]`, `list[-1]`, `range(0, 10, 2)` |
| Nested collect | `[(a)-->(b:Movie) \| b.year]` (pattern comprehension) |
| Chained compare | `WHERE 21 < n.age <= 30` |
| Union | `… RETURN x AS v UNION [ALL] … RETURN y AS v` (same column names, same count) |
| Procedure | `CALL ns.proc($a) YIELD out AS o WHERE o > 1 RETURN o` |
| Pin version | Prefix the query with `CYPHER 9` |

## Style in one screen (openCypher Style Guide)

```cypher
MATCH (manufacturer:Company {country: $country})<-[:MADE_BY]-(vehicle:Car)
WHERE manufacturer.foundedYear < 2000
  AND vehicle.mileage IS NOT NULL
WITH manufacturer, count(vehicle) AS fleetSize
MERGE (manufacturer)-[:HAS_STATS]->(stats:Stats)
  ON CREATE SET stats.fleetSize = fleetSize
  ON MATCH SET stats.fleetSize = fleetSize
RETURN manufacturer.name, fleetSize
ORDER BY fleetSize DESC
```

- **Layout.** Each clause starts a new line. Indent `ON CREATE` / `ON MATCH` by two spaces, `ON CREATE` first. No trailing `;`. Files use `.cypher`.
- **Case.** `UPPER` keywords. `null`, `true`, `false` in lowercase. camelCase for variables, properties, parameters and functions. **PascalCase singular-noun labels** (`:EditorInChief`). **UPPER_SNAKE relationship types** (`:OWNS_VEHICLE`).
- **Strings.** Single quotes, unless that needs more escapes than double quotes would (`"Cypher's"`).
- **Backticks.** Avoid names that need them.
- **Patterns.** Anchor and named nodes first. Prefer left-to-right (outgoing) arrows. Chain patterns instead of repeating a variable. Use anonymous `()`/`[]` for anything you don't reference. When wrapping, break **after** an arrow.
- **Spacing.** `{key: 'v', k2: 42}`. `(p:Person {k: 1})` with one space before the map. No spaces inside patterns (`(a)-->(b)`) or label lists (`:A:B`). Spaces around operators (`p = …`, `a <> b`). A space after commas. No padding inside `f(x)`.

Full rules with bad/good pairs are in `references/style-guide.md`.

## Cypher 9 vs what engines accept now

These notes come from outside the two PDFs. Check them against your engine's manual.

- **`{param}`** is the old parameter syntax, and the style guide still mentions it. Use **`$param`**, which v9 already specifies. Modern Neo4j rejects `{param}`.
- **`exists(n.prop)`** is v9. Neo4j 5 removed it, so use `n.prop IS NOT NULL`, which works everywhere.
- **Pattern expressions as values** (`RETURN (a)-->()`, `size((a)-->())`) are v9. Neo4j 5 only allows patterns as predicates. Use pattern comprehension, `size([(a)-->(b) | b])`, or `COUNT { }` where the engine has it.
- **`EXISTS { … }` subqueries**, which the style guide formats, **aren't in the v9 reference**. They're a later extension (Neo4j 4+). On a strict v9 engine, use a pattern predicate.
- **`[:A|:B]`** (repeating the colon) is legacy. Write `[:A|B]`.
- **`MANDATORY MATCH`** is a documented *proposal*. `MANDATORY` is on v9's "reserved for future use" list. Most engines don't implement it.
- **`db.labels()`, `dbms.procedures()`** and similar in the reference's CALL examples are Neo4j procedures. The procedures available differ by product (Neptune: `neptune.*`).
- **GQL** (ISO/IEC 39075:2024) is Cypher-derived but not identical. See [[graph-databases]].

## References

- `references/patterns-and-clauses.md`: pattern syntax and uniqueness, then every clause in detail (semantics, scoping, gotchas, examples), and state visibility between clauses.
- `references/types-null-and-semantics.md`: the type system and coercion, lists, maps and projections, null logic tables, comparability / equality / orderability / equivalence, aggregation rules, and where the reference contradicts itself.
- `references/functions.md`: every built-in function with its return type and null / error behaviour, plus operators, literals, escapes, comments and reserved words.
- `references/style-guide.md`: all style-guide rules and modeling recommendations with bad/good examples, plus the guide's own inconsistencies.
