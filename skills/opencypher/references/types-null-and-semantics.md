# Types, null, and value semantics (Cypher 9)

## Types

| Category | Types | Returnable | As parameter | Storable as property | Has a literal |
|---|---|---|---|---|---|
| Property | `NUMBER` (`INTEGER`, `FLOAT` = IEEE-754 64-bit), `STRING` (Unicode), `BOOLEAN` | yes | yes | yes, plus homogeneous lists of these | yes |
| Structural | `NODE` (id, labels, property map), `RELATIONSHIP` (id, type, property map, start and end ids), `PATH` | yes | **no** | no | no |
| Composite | `LIST OF T` (heterogeneous, ordered), `MAP` (string keys, any values) | yes | yes | no (except homogeneous scalar lists) | yes |

- "Numeric" means `INTEGER` or `FLOAT`.
- `WHERE` predicates are really `BOOLEAN?`, because of ternary logic.
- Labels aren't values. They're pattern syntax.
- Composite values can contain `null`.
- **Coercions** (the only two): `INTEGER → FLOAT`, and `LIST OF NUMBER → LIST OF FLOAT` when storing a mixed number list as a property. Everything else is explicit: `list[toInteger(1.5)]`.

## Literals and escapes

- **Integer**: `13`, `-40000`; hex `0xFC3A9`; octal `01372`.
- **Float**: `3.14`, `6.022E23`.
- **String**: `'Hello'` or `"World"`. Escapes are `\t \b \n \r \f \' \" \\`, `\uxxxx` (UTF-16) and `\Uxxxxxxxx` (UTF-32).
- **Boolean**: `true`/`false`. `TRUE`/`FALSE` parse, but the style guide says lowercase. `null` is the null literal.
- **List**: `[1, 'a', n.prop, $p, []]`. **Map**: `{key: 'v', nested: {x: 1}}`.
- Variables and property names are case-sensitive. They use letters, digits and `_`, and must start with a letter. Otherwise backtick them. Parameter names can't start with a digit or a currency symbol, though `$0` style positional parameters are listed as valid.

## Lists

- `range(start, end [, step])` is **inclusive** at both ends: `range(0, 10)` has 11 elements.
- **Index**: `list[3]`. Negative counts from the end (`range(0, 10)[-3]` → 8). An out-of-bounds single index gives **`null`**.
- **Slice**: `list[a..b]` includes a and excludes b. Either side can be omitted. Negatives are allowed (`[0..-5]`, `[-5..]`, `[..4]`). An out-of-bounds slice is **truncated**, not an error (`range(0,10)[5..15]` → `[5..10]`).
- `size(list)`, `head`, `last`, `tail`, `reverse`. Concatenate with `+`. Test membership with `IN`.
- **List comprehension**: `[x IN list WHERE pred | expr]`. Either the `WHERE` part or the `| expr` part may be left out.
- **Pattern comprehension**: `[(a)-[]->(b) WHERE b:Movie | b.year]`. It matches like MATCH, filters like WHERE and projects each match. The `WHERE` is optional. It's a way to collect related data without changing row count.

## Maps

- **Literal**: `{key: 'Value', listKey: [{inner: 'Map1'}]}`. Access: `m.key`, `m.person.name`, `m['key']`. Dynamic property on nodes: `n['rating_' + category.name]`.
- **Map projection**: `var {elements}`, with four kinds of element:
  - `.name`: property selector
  - `key: expr`: literal entry, any expression (including `collect(movie {.title})`)
  - `nrOfMovies`: variable selector, where the key is the variable's name
  - `.*`: all properties
  ```cypher
  MATCH (actor:Person {name: 'Charlie Sheen'})-[:ACTED_IN]->(movie:Movie)
  RETURN actor {.name, .realName, movies: collect(movie {.title, .year})}
  ```
  If `var` is `null`, the whole projection is `null`. A selected property that doesn't exist projects as `null` (`actor {.*, .age}` → `age: null`).
- `keys(m)` and `properties(n)` return the key list and the property map.

## null

`null` means a missing or unknown value.

- **Produces null**: a missing property, an out-of-bounds index, `head([])`, any comparison with null (`1 < null`), arithmetic with null (`1 + null`), and almost any function given a null argument (`sin(null)`).
- **`null = null` is `null`, and so is `null <> null`.** Only `IS NULL` / `IS NOT NULL` test for null reliably.
- `WHERE` keeps a row only when the predicate is `true`. `null` behaves like false. But `NOT null` is still `null`, so negating a null predicate doesn't bring the row back.

### Three-valued logic

| a | b | a AND b | a OR b | a XOR b | NOT a |
|---|---|---|---|---|---|
| false | false | false | false | false | true |
| false | null | false | null | null | true |
| false | true | false | true | true | true |
| true | false | false | true | true | false |
| true | null | null | true | null | false |
| true | true | true | true | false | false |
| null | false | false | null | null | null |
| null | null | null | null | null | null |
| null | true | null | true | null | null |

### IN with null

| Expression | Result |
|---|---|
| `2 IN [1, 2, 3]` | true |
| `2 IN [1, null, 3]` | **null** |
| `2 IN [1, 2, null]` | true |
| `2 IN [1]` / `2 IN []` | false |
| `null IN [1, 2, 3]` / `null IN [1, null, 3]` | null |
| `null IN []` | false |

So `WHERE NOT x IN list` drops every row where the list has a null and `x` isn't in it. Strip nulls first with `[v IN list WHERE v IS NOT NULL]`.

## Equality, comparison, ordering, grouping

The reference defines four separate concepts. It's the key to understanding why `=`, `ORDER BY` and `DISTINCT` disagree on nulls.

| Concept | Used by | null handling |
|---|---|---|
| **Comparability** | `<` `>` `<=` `>=` | "unknown" null. Any comparison involving null gives null |
| **Equality** | `=` `<>` `IN`, pattern property maps | "unknown" null. `null = null` is null |
| **Orderability** | `ORDER BY`, `min`/`max` | total order. Null sorts last |
| **Equivalence** | `DISTINCT`, grouping keys | "missing" null. **Two nulls are the same group** |

### Comparability

- Values compare only within their type. Integers and floats compare with each other numerically.
- **Numbers.** `+∞` is greater than any other number and `-∞` is less. **NaN is incomparable.**
- **Booleans**: `false < true`.
- **Strings**: dictionary order, and a shorter prefix is smaller (`'a' < 'aa'`).
- **Lists**: pairwise dictionary order, so `[1] < [1, 0]` and `[1] < [1, null]`. If deciding needs a comparison with null, the result is null (`[1, 2] >= [1, null]` → null).
- **Maps**: order is left to the implementation. A map with a null entry is incomparable.
- **Nodes and relationships**: compared by an internal, implementation-specific identity order.
- **Paths**: compared as the list `[n1, r1, n2, …]`.
- **Different types**: incomparable, so the result is `null`. `MATCH (n) WHERE n.prop < 42` never matches a string `prop`.

### Equality

- Same type and same value. Lists must have equal size and pairwise-equal elements (`[3, 4] = [1+2, 8/2]`).
- A path equals the list of its alternating elements.
- **Nulls nested inside collections** count as unknown too: `[null] = [null]` and `{a: null} = {a: null}` are **null** under the v9 "new map equality". The old rule said two missing entries made maps equal, so engines differ here. Don't compare collections that contain nulls.

### Orderability (ascending global order)

```
MAP (regular map) < NODE < RELATIONSHIP < LIST < PATH < STRING < BOOLEAN < NUMBER (NaN after +∞) < null
```

- Within a type, ordering follows comparability, but nulls inside lists order as equivalent. `[null, 1]` sorts before `[null, 2]`.
- Container elements use orderability: `[1, 'foo', 3] < [1, 2, 'bar']` because a string sorts before a number.
- Descending order is the exact reverse, so null comes first.
- Example: `UNWIND [1, true, '', 3.14, {}, [2], null] AS i RETURN i ORDER BY i` gives `{}, [2], '', true, 1, 3.14, null`.
- `max(val)` over `[1, 'a', null, 0.2, 'b', '1', '99']` is **`1`**, because numbers sort above strings. `min` is **`'1'`**, the smallest string, because strings sort below numbers. For lists, `max([[1, 'a', 89], [1, 2]])` is `[1, 2]`, since `2 > 'a'` under orderability.

### Equivalence

It's equality except that any two nulls are equivalent and any two NaNs are equivalent (but not null with NaN), including inside nested structures. It's reflexive. So `UNWIND [[null], [null]] AS i RETURN DISTINCT i` gives **one row**, and `null` forms its own group key.

### Aggregation semantics

- Group keys are compared by equivalence.
- Each aggregate collects the candidate values for its group and **removes nulls**. `DISTINCT` also removes duplicates under equivalence.
- If the projection has an `ORDER BY`, candidates arrive in that order, which is how `collect` gets sorted.
- Aggregating mixed types, such as summing a number and a string, can raise a runtime error.

| Function | On values | Empty (all null / no rows) |
|---|---|---|
| `count(expr)` | number of non-null values | 0 |
| `count(*)` | number of rows, nulls included | 0 |
| `sum` | sum (Integer or Float) | 0 |
| `avg` | mean (Integer or Float) | **contradictory**: the semantics chapter says 0, the function reference says `avg(null)` is null. Engines return null |
| `min` / `max` | by orderability; never null unless empty | null |
| `collect` | list of non-null values (order = ORDER BY if present) | `[]` |
| `stDev` (sample, N−1) / `stDevP` (population, N) | Float | 0 |
| `percentileCont(expr, p)` (interpolated) / `percentileDisc(expr, p)` (nearest) | p in 0.0–1.0 | **contradictory**: 0 vs null in the two chapters |

## Where the reference contradicts itself

The comparability, equality, orderability and equivalence chapter is written as a **proposal** ("we propose", "should"). Other chapters describe the older behaviour:

| Topic | Proposal chapter | Operators / Clauses chapters |
|---|---|---|
| Comparing incompatible types | returns `null` | "It is an error to compare values that cannot be compared" |
| Ordering mixed types | defined global sort order, never fails | "It is an error to compare other types of values … for ordering" |
| Sorting nodes | nodes have an order | "you cannot sort on nodes or relationships" |
| Map/list equality with nulls | nested nulls give null | old rule: matching missing entries are equal |
| Empty `avg` / `percentile*` | 0 | `avg(null)`/`percentileCont(null, …)` return null |

When code has to be portable, don't depend on any of these. Keep property types consistent, sort on scalar properties, strip nulls from lists before comparing, and `coalesce()` your aggregates.

## CASE

```cypher
// Simple form: compare one value against candidates
CASE n.eyes WHEN 'blue' THEN 1 WHEN 'brown' THEN 2 ELSE 3 END

// Generic form: first predicate that's true wins
CASE WHEN n.eyes = 'blue' THEN 1 WHEN n.age < 40 THEN 2 ELSE 3 END
```

- With no `ELSE` and no match, the result is `null`.
- The trap: `CASE n.age WHEN n.age IS NULL THEN -1 ELSE n.age - 10 END` compares an integer with a boolean, so it never matches, and a null age gives `null`. Use the generic form for conditions.

## Parameters

- `$name` (and `$0`). Supply them as a JSON map beside the query.
- **Allowed**: literals and expressions (`WHERE n.name = $name`, `{name: $name}`, `STARTS WITH $prefix`), whole-map CREATE (`CREATE ($props)`, `CREATE (n:Person $props)`), `SET n = $props` (replaces), `UNWIND $list`, `SKIP $s LIMIT $l`, node and relationship ids, procedure arguments, and (in Neo4j's legacy explicit indexes) index keys.
- **Not allowed**: property keys (`n.$param`), labels, relationship types. They're part of the compiled plan. Pick them in application code from an allow-list, never by interpolating raw input.
- Benefits: no string building, so no injection, and the engine can cache the plan.
