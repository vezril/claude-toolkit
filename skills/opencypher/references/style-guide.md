# The openCypher Style Guide

The guide has **rules**, which are formatting only and never change semantics, and **recommendations**, which affect the schema and so the semantics. When two rules conflict and neither says which wins, **the one listed later applies**. The recommendations can't be applied after the fact: renaming labels or types means refactoring the graph, not just the queries. The goal is queries people can share with little friction, and consistent, portable use across implementations.

## Rules

### Indentation and line breaks

1. **Start each clause on a new line.**
   ```cypher
   // Bad
   MATCH (n) WHERE n.name CONTAINS 's' RETURN n.name
   // Good
   MATCH (n)
   WHERE n.name CONTAINS 's'
   RETURN n.name
   ```
   a. **Indent `ON CREATE` / `ON MATCH` by two spaces.**
   b. **Put `ON CREATE` before `ON MATCH`.**
   ```cypher
   MERGE (a:A)-[:T]-(b:B)
     ON CREATE SET a.name = 'me'
     ON MATCH SET b.name = 'you'
   RETURN a.prop
   ```
2. **Subqueries.** Start on a new line after `{`, indent two extra spaces, and put the closing `}` on its own line.
   ```cypher
   MATCH (a:A)
   WHERE EXISTS {
     MATCH (a)-->(b:B)
     WHERE b.prop = $param
   }
   RETURN a.foo
   ```
   a. **The simplified subquery form stays on one line**: `WHERE EXISTS { (a)-->(b:B) }`.

   `EXISTS { }` isn't in the Cypher 9 reference, so these two rules apply to engines that support subqueries. On a strict v9 engine, write `WHERE (a)-->(:B)`.

### Meta-characters

1. **Single quotes for string literals**: `RETURN 'Cypher'`.
   a. The exception: if the string contains a single quote, use whichever quoting needs fewer escapes. On a tie, prefer single quotes.
   ```cypher
   // Bad
   RETURN 'Cypher\'s a nice language', "Mats' quote: \"statement\""
   // Good
   RETURN "Cypher's a nice language", 'Mats\' quote: "statement"'
   ```
2. **Avoid identifiers that need backticks.** Write `(node:NonSpacedLabel {property: 42})`, not ``(`odd-ch@racter$`:`Spaced Label` {`&property`: 42})``.
3. **No semicolon at the end of a statement.** `RETURN 1`, not `RETURN 1;`.

### Casing

1. **Keywords in upper case**: `MATCH`, `WHERE`, `STARTS WITH`, `RETURN`.
2. **`null` in lower case.**
3. **`true` / `false` in lower case.**
4. **camelCase starting lower case** for functions, properties, variables and parameters.
   ```cypher
   // Bad
   CREATE (N {Prop: 0})
   WITH RAND() AS Rand, $pArAm AS MAP
   RETURN Rand, MAP.property_key, Count(N)
   // Good
   CREATE (n {prop: 0})
   WITH rand() AS rand, $param AS map
   RETURN rand, map.propertyKey, count(n)
   ```

### Patterns

1. **When a pattern wraps, break after an arrow, not before it.**
   ```cypher
   MATCH (:Person)-->(vehicle:Car)-->(:Company)<--
         (:Country)
   ```
2. **Use anonymous nodes and relationships when the variable isn't used**: `(:End {prop: 3})`, not `(b:End {prop: 3})` with `b` unused.
3. **Chain patterns instead of repeating a variable.** Write `(:Person)-->(vehicle:Car)-->(:Company)`, not `(:Person)-->(vehicle:Car), (vehicle:Car)-->(:Company)`.
4. **Named nodes before anonymous nodes.** `MATCH (manufacturer:Company)<--(vehicle:Car)<--()`.
5. **Anchor nodes at the start of the MATCH.** The anchor is the node your `WHERE` constrains: `MATCH (manufacturer:Company)<--(vehicle:Car)<--(:Person) WHERE manufacturer.foundedYear < 2000`.
6. **Prefer outgoing (left-to-right) relationships.** `(:Person)-->(vehicle:Car)-->(:Company)<--(:Country)`, rather than starting from `(:Country)-->…<--…`.

   Rules 5 and 6 can conflict. Rule 5's own "Good" example uses incoming arrows to keep the anchor first, while rule 6 prefers outgoing. Under the guide's precedence rule, the later rule (6) wins when both can't hold, but the guide's example shows the authors accept anchor-first too. Pick one convention for the codebase and apply it consistently.

### Spacing

1. **Literal maps**: no space after `{`, none before `:`, one after `:`, none before `,`, one after `,`, none before `}`. So `{key1: 'value', key2: 42}`, not `{ key1 :'value' ,key2  :  42 }`.
2. **No padding inside parameter braces**: `{param}`, not `{ param }`. This rule is about **deprecated** parameter syntax. Use `$param`.
3. **One space between label/type and a property map**: `(p:Person {property: -1})-[:KNOWS {since: 2016}]->()`.
4. **No spaces inside patterns**: `(:Person)-->(:Vehicle)`, not `(:Person) --> (:Vehicle)`.
5. **Spaces around operators**: `p = (s)-->(e)`, `s.name <> e.name`.
6. **No spaces in label predicates**: `(person:Person:Owner)`.
7. **A space after each comma**: `MATCH (), ()`, `['a', 'b', 3.14]`, `RETURN list, 2, 3, 4`.
8. **No padding inside function parentheses**: `split('original', 'i')`.
9. **Padding inside simple subquery braces**: `EXISTS { (a)-->(b:B) }`, not `EXISTS {(a)-->(b:B)}`.

## Recommendations

- **In prose**, use monospace and the styling rules. Write labels and types with their colon (`:Label`, `:REL_TYPE`) and functions in lower camelCase with empty parentheses (`shortestPath()`).
- **Files** of Cypher statements use the `.cypher` extension.

### Graph modeling

1. **Labels are single nouns**: `:Employee`, not `:IsEmployed`.
2. **Labels in PascalCase** (upper camel case): `:EditorInChief`, `:Employee`, not `:editor_in_chief` or `:EMPLOYEE`.
3. **Relationship types in UPPER_SNAKE_CASE**: `:OWNS_VEHICLE`, not `:ownsVehicle`.

## Naming summary

| Element | Convention | Example |
|---|---|---|
| Keyword | UPPER | `OPTIONAL MATCH` |
| Label | PascalCase singular noun | `:CreditCard` |
| Relationship type | UPPER_SNAKE verb phrase | `:PAID_WITH` |
| Property key | camelCase | `createdAt` |
| Variable | camelCase | `cardHolder` |
| Parameter | camelCase | `$accountId` |
| Function | camelCase | `toLower()` |
| Literals | lower | `null`, `true`, `false` |

## Inconsistencies in the guide itself

- The casing rule's "Good" example writes `WITH null AS n1, null as n2`, with a lowercase `as`. That breaks rule 2.3.1. Keywords are upper case: `AS`.
- The spacing rule for `{param}` describes syntax the guide itself calls deprecated.
- The subquery rules (2.1.2, 2.5.9) format `EXISTS { … }`, which the Cypher 9 reference doesn't define. The guide tracks a newer language than the reference.

## Formatting checklist (for reviews)

- [ ] One clause per line. `ON CREATE`/`ON MATCH` indented two spaces, CREATE first.
- [ ] Keywords upper case. `null`/`true`/`false` lower case.
- [ ] camelCase variables, properties, parameters and functions. PascalCase labels. UPPER_SNAKE types.
- [ ] Single-quoted strings, unless that needs more escaping.
- [ ] No trailing `;`, no backtick-requiring names.
- [ ] Anchor first. Named nodes before anonymous ones. Outgoing arrows. Chained patterns. Anonymous elements for unused parts.
- [ ] Map, comma, operator and pattern spacing as above.
- [ ] `$param` everywhere. No string-built values.
