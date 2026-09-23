# Functions, operators, and keywords (Cypher 9)

Most functions return `null` when an argument is `null`. The exceptions and the functions that raise errors are marked with **bold**. Function names are shown in the style guide's camelCase. Engines generally match them case-insensitively.

## Predicate

| Function | Returns | Notes |
|---|---|---|
| `exists(n.prop)` | Boolean | true if the property exists on the node, relationship or map. The glossary also lists `exists(pattern)`. Neo4j 5 removed the property form, so `n.prop IS NOT NULL` is portable |

## Scalar

| Function | Returns | Notes |
|---|---|---|
| `coalesce(e1, e2, …)` | type of the first non-null value | null only if all arguments are null |
| `startNode(r)` / `endNode(r)` | Node | null → null |
| `head(list)` / `last(list)` | element | null for an empty list or a null element |
| `id(n\|r)` | Integer | internal and implementation-specific. Don't persist it or use it as a business key |
| `length(path)` | Integer | number of relationships |
| `properties(n\|r\|map)` | Map | a map comes back unchanged |
| `size(list)` / `size(string)` | Integer | element count / string length |
| `size(pattern)` | Integer | number of matching subgraphs, e.g. `size((a)-->()-->())`. v9 only. Portable: `size([(a)-->()-->(x) \| x])` |
| `timestamp()` | Integer | ms since the Unix epoch. **The same value for the whole query** |
| `toBoolean(s)` | Boolean | booleans pass through. **An unparseable string gives null**, not an error (`'TRUE'` → true) |
| `toFloat(x)` | Float | integer or string. **Unparseable → null** |
| `toInteger(x)` | Integer | float or string. **Unparseable → null**. Use it for list indexes from floats |
| `type(r)` | String | the relationship type name |

## Aggregating

(The empty-input defaults and their contradictions are in `types-null-and-semantics.md`.)

| Function | Returns | Notes |
|---|---|---|
| `count(*)` / `count(expr)` / `count(DISTINCT expr)` | Integer | `*` counts rows. `expr` skips nulls. `count(null)` → 0 |
| `sum(expr)` | Integer or Float | nulls skipped. `sum(null)` → 0 |
| `avg(expr)` | Integer or Float | nulls skipped. `avg(null)` → null |
| `min(expr)` / `max(expr)` | property type or list | orderability: lists < strings < numbers. Nulls skipped |
| `collect(expr)` | List | nulls skipped. `collect(null)` → `[]`. Sort beforehand with `WITH … ORDER BY` |
| `percentileCont(expr, p)` | Float | linear interpolation. p is 0.0–1.0 |
| `percentileDisc(expr, p)` | Integer or Float | nearest value (rounding) |
| `stDev(expr)` | Float | sample (N−1). `stDev(null)` → 0 |
| `stDevP(expr)` | Float | population (N). `stDevP(null)` → 0 |

The semantics chapter spells these `stdev`, `stdevp`, `percentile_disc` and `percentile_cont`. The function chapter's camelCase names are the ones engines implement.

## List

| Function | Returns | Notes |
|---|---|---|
| `keys(n\|r\|map)` | List of String | property names |
| `labels(n)` | List of String | |
| `nodes(path)` / `relationships(path)` | List | |
| `range(start, end [, step])` | List of Integer | **inclusive**. Default step 1. `range(2, 18, 3)` → `[2,5,8,11,14,17]` |
| `reverse(list)` | List | keeps null elements |
| `tail(list)` | List | everything but the first element |

## Numeric

These **raise an error on non-numeric input**.

| Function | Returns | Notes |
|---|---|---|
| `abs(x)` | same type as x | |
| `ceil(x)` / `floor(x)` / `round(x)` | **Float** | `round(3.14)` → `3.0`. Wrap in `toInteger()` for an integer |
| `rand()` | Float | uniform over [0, 1) |
| `sign(x)` | Integer | -1, 0, 1 |

## Logarithmic

These **raise an error on non-numeric input**.

| Function | Returns | Notes |
|---|---|---|
| `e()` | Float | 2.718… |
| `exp(x)` | Float | eˣ |
| `log(x)` / `log10(x)` | Float | `log(0)` → **null** |
| `sqrt(x)` | Float | a negative argument gives **null** |

## Trigonometric (radians)

| Function | Notes |
|---|---|
| `sin`, `cos`, `tan`, `cot` | `cot(0)` → null |
| `asin`, `acos` | an argument outside [-1, 1] gives null |
| `atan(x)`, `atan2(y, x)` | |
| `degrees(rad)`, `radians(deg)`, `pi()` | |

## String

These **raise an error on non-string input**, except `toString`.

| Function | Returns | Notes |
|---|---|---|
| `left(s, n)` / `right(s, n)` | String | `left(null, n)` → null, but **`left(s, null)` raises an error**. A non-positive n raises an error. An n longer than the string returns the whole string |
| `lTrim(s)` / `rTrim(s)` / `trim(s)` | String | whitespace only |
| `replace(s, search, repl)` | String | replaces every occurrence. Any null argument → null |
| `reverse(s)` | String | |
| `split(s, delim)` | List of String | a null argument → null |
| `substring(s, start [, len])` | String | **zero-based**. With no len, runs to the end. **A null or negative start or len raises an error**. len 0 gives `''` |
| `toLower(s)` / `toUpper(s)` | String | use on both sides for case-insensitive matching |
| `toString(x)` | String | integer, float, boolean or string. `toString(true)` → `'true'` |

## User-defined

- Called like built-ins, with a namespace: `org.opencypher.function.example.join(collect(n.name))`.
- User-defined aggregates work the same way.
- They must return values within Cypher's type system. What's available depends on the engine: APOC on Neo4j, none on Neptune.

## Operators

| Group | Operators | Notes |
|---|---|---|
| General | `DISTINCT`, `.` (property), `[]` (dynamic property or subscript) | `n['rating_' + c.name]` |
| Arithmetic | `+ - * / % ^`, unary `-` | **`^` always returns Float** (`2 ^ 3` → `8.0`). Integer vs float division isn't specified in v9, so check your engine |
| Comparison | `= <> < > <= >=`, `IS NULL`, `IS NOT NULL` | chains: `a < b <= c` means `a < b AND b <= c`, with no a–c comparison implied |
| String comparison | `STARTS WITH`, `ENDS WITH`, `CONTAINS` | case-sensitive |
| Boolean | `AND OR XOR NOT` | three-valued |
| String | `+` concatenation | |
| List | `+` concatenation, `IN`, `[i]`, `[a..b]` | |

## Comments

`// to end of line` and `/* multi-line */`. `//` inside a string literal is text, not a comment.

## Reserved words

You can't use these as variable, function or parameter names unless they're backticked.

- **Clauses**: CREATE, DELETE, DETACH, EXISTS, MATCH, MERGE, OPTIONAL, REMOVE, RETURN, SET, UNION, UNWIND, WITH
- **Sub-clauses**: LIMIT, ORDER, SKIP, WHERE
- **Modifiers**: ASC, ASCENDING, BY, DESC, DESCENDING, ON
- **Expressions**: ALL, CASE, ELSE, END, THEN, WHEN
- **Operators**: AND, AS, CONTAINS, DISTINCT, ENDS, IN, IS, NOT, OR, STARTS, XOR
- **Literals**: false, null, true
- **Reserved for future use**: ADD, CONSTRAINT, DO, DROP, FOR, MANDATORY, OF, REQUIRE, SCALAR, UNIQUE

The style guide's own opening example, ``MATCH (null)-[:merge]->(true) WITH null.delete AS foreach, `true`.false AS null …``, shows why these shouldn't be identifiers even where an engine tolerates them.
