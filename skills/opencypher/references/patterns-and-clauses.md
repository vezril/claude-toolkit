# Patterns and clauses (Cypher 9)

## Property graph model

- A **property graph** is a directed, vertex-labeled, edge-labeled multigraph with self-edges, where edges have their own identity.
- **Node**: may have a set of labels and a set of properties. It can exist on its own.
- **Relationship**: directed, connecting exactly two nodes (source → target). It has **exactly one type** and a set of properties. Direction is always stored. Leaving it out in a query just ignores it.
- **Path**: alternating nodes and relationships that starts and ends at a node. The smallest path is a single node (length 0). Length = number of relationships.
- **Property value**: a scalar (number, string, boolean) or a homogeneous list of one scalar type. Maps and mixed lists can't be stored, and neither can `null`. Byte arrays pass through but have no literal form.
- Labels and types are **tokens**, not values. You can't compute them (`n:$label` is invalid).

## Pattern syntax

| Pattern | Meaning |
|---|---|
| `(a)` | a node, bound to `a` |
| `()` | an anonymous node |
| `(a:User:Admin)` | a node with both labels |
| `(a {name: 'Andres', sport: 'BJJ'})` | property equality constraints (in CREATE, the values to set) |
| `(a)-[]->(b)`, `(a)-->(b)` | a directed relationship a → b |
| `(a)-[]-(b)`, `(a)--(b)` | either direction |
| `(a)-[r:TYPE]->(b)` | a typed relationship bound to `r` |
| `(a)-[:T1\|T2]->(b)` | either type. **MATCH and expressions only** |
| `(a)-[{blocked: false}]->(b)` | relationship property constraint |
| `(a)-[*2]->(b)` | exactly two hops, same as `(a)-->()-->(b)` |
| `(a)-[*3..5]->(b)`, `*3..`, `*..5`, `*` | variable length. Min defaults to 1, max to unbounded |
| `(a)-[:KNOWS*1..2]-(b)` | typed variable length |
| `(a)-[*0..1]-(b)` | zero-length allowed, so `b` can be `a` itself (matches even if the type is unused) |
| `p = (a)-[*3..5]->(b)` | named path. Allowed in MATCH, CREATE and MERGE, not in pattern expressions |
| `shortestPath((a)-[*..15]-(b))` | one shortest path. Type, direction, max hops and following `WHERE` predicates all apply |
| `allShortestPaths((a)-[*]-(b))` | every path of the minimum length |

- `CREATE (n $props)` is the **only** place a whole-map parameter can supply pattern properties. MATCH and MERGE need the property names at compile time.
- Variable-length patterns and type alternation can't be used in `CREATE` or `MERGE`.
- If a relationship variable is already bound and the pattern has no direction, it matches **both ways**. `MATCH (a)-[r]-(b) WHERE id(r) = 0` returns two rows with a and b swapped.

### Uniqueness (relationship isomorphism)

Within **one pattern** (one `MATCH`, commas included), a graph relationship can be bound to at most one relationship pattern. Nodes can repeat.

```cypher
// Doesn't return Adam: r1 and r2 can't both be the Adam–Pernilla edge
MATCH (user:User {name: 'Adam'})-[r1:FRIEND]-()-[r2:FRIEND]-(fof)
RETURN fof.name

// Does return Adam: two MATCH clauses are two patterns, so the edge can be reused
MATCH (user:User {name: 'Adam'})-[:FRIEND]-(friend)
MATCH (friend)-[:FRIEND]-(fof)
RETURN fof.name
```

To retrace relationships inside a variable-length search, split it the same way: `MATCH (a)-[r]->(b) MATCH p = (a)-[*]->(c)`.

## Clause catalogue

| Category | Clauses |
|---|---|
| Reading | `MATCH`, `OPTIONAL MATCH`, `MANDATORY MATCH` (proposal) |
| Projecting | `RETURN … [AS]`, `WITH … [AS]`, `UNWIND … AS` |
| Reading sub-clauses | `WHERE`, `ORDER BY [ASC[ENDING] \| DESC[ENDING]]`, `SKIP`, `LIMIT` |
| Writing | `CREATE`, `DELETE`, `DETACH DELETE`, `SET`, `REMOVE` |
| Read/write | `MERGE`, `CALL […YIELD]` |
| Set operations | `UNION`, `UNION ALL` |

### MATCH

- It's the main way to bind variables. As the first clause, the engine chooses how to find starting points (a scan, a label lookup or an index). Later `MATCH` clauses extend from what's already bound.
- `WHERE` predicates are part of the pattern. They can be evaluated before, during or after matching.
- Get by id: `MATCH (n) WHERE id(n) = 0` / `WHERE id(n) IN [0, 3, 5]`. Implementation-specific. Avoid it in application logic.
- Backtick names with spaces or symbols: ``-[r:`TYPE WITH SPACE`]->``. Style says avoid needing it.

### OPTIONAL MATCH

- Like MATCH, but when **the whole pattern** fails to match, the new variables are `null` instead of the row disappearing. It's the outer join.
- Properties of a `null` element are `null` (`x.name`).
- Its own `WHERE` is evaluated **during** optional matching. The row survives with nulls. Moving the predicate to a later `WITH … WHERE` removes the row.
- A later `MATCH` on a `null`-bound variable eliminates the row.

### MANDATORY MATCH (proposal)

It behaves like `MATCH` but **fails the query** when nothing matches, with an error naming the failing clause. It's meant for "this id must exist" lookups, so bad input fails loudly instead of returning an empty result that looks legitimate. It can't be combined with `OPTIONAL` in one clause. The proposal suggests putting all `MANDATORY MATCH` clauses first. `MANDATORY` is on v9's reserved-for-future list, so **most engines don't have it**. The portable pattern is to have the application check for zero rows, or run a separate lookup.

### RETURN

- It returns nodes, relationships, properties or any expression: literals, predicates, pattern expressions (v9 only).
- `RETURN *` returns every variable in scope, including named paths.
- `AS` renames a column. ``AS `odd name` `` is allowed but discouraged.
- A missing property gives `null`.
- `RETURN DISTINCT` deduplicates whole rows, using equivalence semantics.
- Aggregating: non-aggregate items are the grouping keys (see below).
- Required at the end of any read-only query. Optional after writes.

### WITH

- It projects like RETURN (with `AS`, `DISTINCT`, aggregation, `ORDER BY`, `SKIP`, `LIMIT`, `WHERE`) and then continues the query.
- **Only listed variables survive.** Everything else is out of scope afterwards. `WITH *` carries everything.
- Uses:
  - **Filter on aggregates.** `WITH otherPerson, count(*) AS foaf WHERE foaf > 1`.
  - **Sort before `collect`.** `WITH n ORDER BY n.name DESC LIMIT 3 RETURN collect(n.name)`.
  - **Limit branching.** `MATCH … WITH m ORDER BY m.name DESC LIMIT 1 MATCH (m)--(o)` stops a fan-out early.
  - **Switch write → read.** It's required between a writing part and a following reading part.

### UNWIND

- It turns a list into rows: `UNWIND [1, 2, 3] AS x`. A new name is required.
- An empty list (or `null`) produces **zero rows** and wipes the row out, so everything downstream disappears. Use `UNWIND CASE WHEN list = [] THEN [null] ELSE list END AS x` to keep the row.
- Deduplicate: `WITH [1, 1, 2, 2] AS coll UNWIND coll AS x WITH DISTINCT x RETURN collect(x)`.
- Batch writes from a list parameter: `UNWIND $events AS event MERGE (y:Year {year: event.year}) MERGE (y)<-[:IN]-(e:Event {id: event.id})`.

### WHERE

It attaches to `MATCH`, `OPTIONAL MATCH` or `WITH` (and `START`, a legacy clause).

- **Boolean logic**: `AND`, `OR`, `XOR`, `NOT`, with null following three-valued logic.
- **Label test**: `WHERE n:Swedish`.
- **Property / relationship property**: `WHERE n.age < 30`, `WHERE k.since < 2000`.
- **Dynamic key**: `WHERE n[toLower(propname)] < 30`.
- **Existence**: `exists(n.belt)` (v9), or `n.belt IS NOT NULL`.
- **Strings**: `STARTS WITH`, `ENDS WITH` and `CONTAINS` are **case-sensitive**. Negate with `WHERE NOT n.name ENDS WITH 's'`. Lowercase both sides for case-insensitive matching (`toLower(n.name) CONTAINS toLower($q)`). Cypher 9 has no regex operator (`=~` is a Neo4j extension).
- **Pattern predicates**: `WHERE (tobias)<--(others)`, `WHERE NOT (p)-->(peter)`, `WHERE (n)-[:KNOWS]-({name: 'Tobias'})`.
  - A single path only, no commas (combine with `AND`).
  - **Can't introduce new variables.**
  - `MATCH (a)-[*]->(b)` produces one row per path. `WHERE (a)-[*]->(b)` only keeps or drops the existing row.
- **Type test**: `WHERE type(r) STARTS WITH 'K'`.
- **Lists**: `WHERE a.name IN ['Peter', 'Tobias']`.
- **Missing-property defaults**:
  - `n.belt = 'white'` is effectively false when the property is missing (it's null).
  - `n.belt = 'white' OR n.belt IS NULL` treats missing as a match.
- **Ranges**: `a.name >= 'Peter'`, `a.name > 'Andres' AND a.name < 'Tobias'`, `21 < n.age <= 30`.

### ORDER BY

- It follows RETURN or WITH. Ascending by default. `DESC`/`DESCENDING`. Multiple keys break ties left to right.
- `null`s sort last ascending and first descending.
- **Scope rules:**
  - After an **aggregating or DISTINCT** projection, only projected variables can be used.
  - Otherwise, variables from before the projection are also available.
  - A projection that shadows an existing name exposes only the new binding.
  - An aggregate in ORDER BY must also appear in the projection. ORDER BY can't change results, only their order.
- The Clauses chapter says you "cannot sort on nodes or relationships". The comparability chapter *defines* an order for them. Sort on properties to be portable.

### SKIP / LIMIT

- They accept any expression that evaluates to a **positive integer** and doesn't refer to variables (`SKIP toInteger(3*rand()) + 1` is legal). Parameters work: `SKIP $s LIMIT $l`.
- Without ORDER BY, which rows you get is arbitrary.

### CREATE

- Examples:
  - `CREATE (n)`, `CREATE (n), (m)`, `CREATE (n:Person:Swedish {name: 'Andres'})`, `CREATE (a {name: 'Andres'}) RETURN a`.
  - A relationship between bound nodes: `MATCH (a:Person {name: 'A'}), (b:Person {name: 'B'}) CREATE (a)-[r:RELTYPE {name: a.name + '<->' + b.name}]->(b)`.
  - A full path: `CREATE p = (andres {name: 'Andres'})-[:WORKS_AT]->(neo)<-[:WORKS_AT]-(michael {name: 'Michael'})`. Every element not already bound is created.
  - Map parameter: `CREATE (n:Person $props)`. For many: `UNWIND $props AS map CREATE (n) SET n = map`.
- A relationship needs **exactly one type and a direction**.
- CREATE never checks for existing data, so repeated runs duplicate it. Use MERGE for idempotence.

### DELETE / DETACH DELETE

- `MATCH (n:Useless) DELETE n` fails if `n` has any relationships.
- `DETACH DELETE n` removes the node and all its relationships.
- `MATCH (n {name: 'Andres'})-[r:KNOWS]->() DELETE r` deletes relationships only.
- `MATCH (n) DETACH DELETE n` wipes the graph. The reference says it's for small data sets only. Batch large deletes.
- Removing properties and labels is `REMOVE`, not `DELETE`.

### SET

| Form | Effect |
|---|---|
| `SET n.surname = 'Taylor'` | set or overwrite one property |
| `SET n.position = 'Dev', n.surname = 'Taylor'` | several at once |
| `SET n.name = null` | **removes** the property (handy when the value comes from a parameter) |
| `SET n = $props` / `SET at = pn` | **replace all** properties (others are deleted) |
| `SET n += {hungry: true, position: 'Entrepreneur'}` | merge: add or overwrite listed keys, keep the rest. A `null` value removes that key |
| `SET n:German`, `SET n:Swedish:Bossman` | add labels. Idempotent |

### REMOVE

`REMOVE andres.age` removes a property. `REMOVE n:German`, `REMOVE n:German:Swedish` remove labels. Removing a label the node doesn't have does nothing.

### MERGE

MERGE means "match this whole pattern, or create it".

- **Single node.** `MERGE (robert:Critic)`. `MERGE (michael:Person {name: 'Michael Douglas'})` matches the existing node. `MERGE (charlie {name: 'Charlie Sheen', age: 10})` **creates a new node** if any listed property doesn't match exactly.
- **Per-row derived.** `MATCH (person:Person) MERGE (city:City {name: person.bornIn})` gives one City per distinct value. Later rows match the node an earlier row created.
- **Relationship between bound nodes.** `MATCH (a…), (b…) MERGE (a)-[r:ACTED_IN]->(b)`. Relationship MERGE needs its endpoints bound, usually by a preceding MATCH or MERGE.
- **All-or-nothing.** `MERGE (oliver)-[:DIRECTED]->(movie:Movie)<-[:ACTED_IN]-(reiner)` creates a **new** movie when the full shape is missing, even if each person has movies.
  - Split the pattern to reuse parts: `MERGE (city:City {name: person.bornIn}) MERGE (person)-[:BORN_IN]->(city)`.
  - Compare `MERGE (person)-[:HAS_CHAUFFEUR]->(c:Chauffeur {name: person.chauffeurName})`. That creates a chauffeur per person, even for duplicate names. That's correct when same-named chauffeurs are different people, and wrong when they aren't.
- **Undirected.** `MERGE (a)-[r:KNOWS]-(b)` matches either direction and creates one in an arbitrary direction.
- **Map parameters aren't supported.** Use `MERGE (p:Person {name: $param.name, role: $param.role})`. Better: merge on the key only, then `SET p += $param`.
- **`ON CREATE SET` / `ON MATCH SET`.** The v9 reference's MERGE chapter doesn't document these (only the `ON` keyword is reserved). The style guide uses them, and they're universally implemented:
  ```cypher
  MERGE (n:Person {id: $id})
    ON CREATE SET n.created = timestamp()
    ON MATCH SET n.lastSeen = timestamp()
  ```
- **Concurrency.** MERGE isn't a uniqueness guarantee on its own. Two concurrent MERGEs can both create. Back the key with the engine's uniqueness constraint or index. That's outside Cypher 9, which has `CONSTRAINT`/`UNIQUE` only as reserved words.

### CALL … YIELD

- `CALL db.labels` is a **standalone** call. The whole query is just `CALL`. Arguments can be omitted, in which case parameters with matching names are used, and every output field is returned.
- **Inside a larger query**, you must list the arguments and `YIELD` the fields: `CALL db.labels() YIELD label RETURN count(label)`. Rename with `YIELD propertyKey AS prop`. Filter with `YIELD … WHERE …`.
- Arguments can be literals, parameters or a mix. Trailing arguments may use the procedure's defaults.
- Quoted names work: ``CALL `db`.`labels` ``.
- A yielded variable **can't shadow** an existing binding.
- A **VOID** procedure returns nothing and doesn't allow `YIELD`. Mid-query it passes rows through like `WITH *`.
- To inspect signatures, the example uses `CALL dbms.procedures() YIELD name, signature` (Neo4j).
- The reference's note "This clause cannot be combined with other clauses" contradicts its own YIELD examples. Read it as applying to the argument-less standalone form.
- **User-defined functions** are called like built-ins, namespaced: `RETURN org.opencypher.function.example.join(collect(n.name))`. Aggregating UDFs work the same way.

### UNION / UNION ALL

- Every branch must return the **same number of columns with the same names** (alias them).
- `UNION` removes duplicates. `UNION ALL` keeps them.
- Updates run in order: later branches see writes from earlier branches.

## State visibility between clauses

- Each clause logically consumes **all** of its input before producing output (eager semantics). It sees the changes made by earlier clauses and by itself, and none from later clauses.
- `MATCH (a) CREATE ()` terminates. The MATCH doesn't see nodes created afterwards.
- Worked example, starting with 2 nodes. `MATCH () CREATE () WITH * MATCH () CREATE ()`:
  - The first MATCH gives 2 rows, and CREATE makes 2 nodes (4 now).
  - `WITH *` passes on 2 rows. The second MATCH sees 4 nodes, so 2 × 4 = **8 rows**, and CREATE makes 8.
  - Total: 12 nodes, 10 created.
  - Every clause multiplies rows, so a MATCH over the whole graph after a write multiplies work.
- In `CREATE (a:X) RETURN a UNION MATCH (x:X) …`, the second branch sees the node the first created.
- This isn't about concurrency. It defines single-query semantics.

## Aggregation and grouping (quick rules)

- Keys are the non-aggregate expressions in the same RETURN or WITH. `RETURN n, count(*)` counts per `n`.
- `count(*)` counts rows, including ones with nulls. `count(expr)` counts non-null values. `count(DISTINCT x)` deduplicates first.
- Aggregates ignore `null` inputs. Details and the empty-input defaults are in `types-null-and-semantics.md`.
- To sort by an aggregate, project it (with an alias) and `ORDER BY` the alias.

## Query versioning

`CYPHER 9` at the start of a query forces Cypher 9 semantics on an engine that supports multiple versions.

## Idioms and anti-patterns

| Instead of | Write | Why |
|---|---|---|
| `MATCH (a), (b) WHERE a.id = 1 AND b.id = 2` with no labels | `MATCH (a:User {id: 1}), (b:User {id: 2})` | labels let the engine use an index instead of scanning |
| `MATCH (a)-[*]-(b)` | `MATCH (a)-[:KNOWS*..4]-(b)` | an unbounded search can explode |
| `MATCH (a:A), (b:B)` without a join predicate | join through a pattern or a predicate | a Cartesian product: rows(A) × rows(B) |
| `MERGE (a:A {k: 1})-[:R]->(b:B {k: 2})` | `MERGE (a:A {k: 1}) MERGE (b:B {k: 2}) MERGE (a)-[:R]->(b)` | whole-pattern MERGE duplicates nodes |
| `WHERE x = null` | `WHERE x IS NULL` | `= null` is always `null` |
| `OPTIONAL MATCH (a)-->(b) WITH a, b WHERE b.flag` | put `WHERE b.flag` on the OPTIONAL MATCH | a later WHERE removes the rows you wanted to keep |
| String-built queries with values | `$params` | injection risk and no plan reuse |
| `RETURN n, m.x, count(*)` when you meant per `n` | drop `m.x` or aggregate it | every non-aggregate column becomes a key |
| `SKIP 100 LIMIT 10` with no ORDER BY | add `ORDER BY` on a unique key | pages would be arbitrary and overlap |
