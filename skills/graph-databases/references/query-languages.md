# Graph query languages

Status as of 2026-09. Examples use a small social/org graph: `Person` nodes with `name`, `KNOWS` and `REPORTS_TO` relationships, and `Company` nodes linked by `WORKS_AT {since}`.

## Standards map

| Language | Model | Style | Standard / owner | Status |
|---|---|---|---|---|
| **GQL** | LPG | declarative | ISO/IEC 39075:2024 | Published 2024-04-12. Implementations are converging on it |
| **SQL/PGQ** | LPG view over tables | declarative, inside SQL | ISO/IEC 9075-16:2023 (SQL:2023 Part 16) | Oracle 23ai, Spanner Graph. PostgreSQL 19 reverted it (2026-09-07) |
| **Cypher / openCypher** | LPG | declarative | Neo4j; openCypher (2015) | The de facto LPG language. Neo4j Cypher 25 is moving toward GQL |
| **Gremlin** | LPG | imperative traversal | Apache TinkerPop | Stable 3.8.x; 4.0 in beta |
| **SPARQL** | RDF | declarative | W3C | 1.1 is a Recommendation; 1.2 is a Working Draft |
| AQL, GSQL, nGQL, PGQL, DQL… | various | various | single vendor | Lock-in. Prefer standards unless the product earns it |

GQL and SQL/PGQ share the same **graph pattern matching** sub-language, so a `MATCH` pattern you learn once carries between them. GQL is intended as the superset.

## Cypher / GQL

```cypher
// Pattern: nodes in (), relationships in -[]->, labels after :
MATCH (p:Person {name: 'Alice'})-[:WORKS_AT]->(c:Company)
RETURN c.name

// Filter on a relationship property
MATCH (p:Person)-[w:WORKS_AT]->(c:Company)
WHERE w.since >= 2020
RETURN p.name, c.name

// Variable-length: Alice's whole management chain. ALWAYS bound it.
MATCH (:Person {name: 'Alice'})-[:REPORTS_TO*1..10]->(boss)
RETURN boss.name

// GQL / Cypher 5+ quantified path pattern (the standard form of the same)
MATCH (:Person {name: 'Alice'})-[:REPORTS_TO]->{1,10}(boss)
RETURN boss.name

// Shortest path
MATCH p = SHORTEST 1 (a:Person {name: 'Alice'})-[:KNOWS]-+(b:Person {name: 'Bob'})
RETURN length(p)
// (older Cypher: MATCH p = shortestPath((a)-[:KNOWS*..15]-(b)))

// Friends-of-friends who aren't already friends, ranked by mutual friends
MATCH (me:Person {name: 'Alice'})-[:KNOWS]-(f)-[:KNOWS]-(fof)
WHERE fof <> me AND NOT (me)-[:KNOWS]-(fof)
RETURN fof.name, count(DISTINCT f) AS mutual
ORDER BY mutual DESC LIMIT 10

// Writes: MERGE is get-or-create on the whole pattern
MERGE (p:Person {email: $email})
  ON CREATE SET p.name = $name
MERGE (c:Company {domain: $domain})
MERGE (p)-[:WORKS_AT {since: $since}]->(c)
```

Traps:
- **`MERGE` matches the whole pattern.** `MERGE (a)-[:R]->(b:Company {name:'X'})` creates a *new* `Company` if the full path doesn't exist. MERGE nodes separately first, then the relationship.
- **Unbounded `*`** can explode combinatorially. Always give an upper bound.
- **Cartesian products:** two disconnected patterns in one `MATCH` multiply their rows. Connect them or use `WITH` stages.
- **Pass values as parameters (`$email`), never by string concatenation.** That's both the query-plan cache and injection safety (see [[secure-coding]]).
- **Uniqueness semantics differ:** Cypher doesn't reuse a *relationship* within one pattern match, while GQL's match modes (`WALK`, `TRAIL`, `ACYCLIC`, `SIMPLE`) make this explicit. Results can differ when porting.
- Direction in `MATCH`: `-[:KNOWS]-` ignores direction. Use it for symmetric relationships stored once.

## SQL/PGQ

Declare a graph over existing tables, then query it inside SQL:

```sql
CREATE PROPERTY GRAPH org
  VERTEX TABLES (
    employee KEY (empno) LABEL person,
    company  KEY (id)    LABEL company
  )
  EDGE TABLES (
    employee AS reports_to
      SOURCE KEY (empno) REFERENCES employee (empno)
      DESTINATION KEY (mgr) REFERENCES employee (empno)
      LABEL reports_to,
    employment
      SOURCE KEY (empno) REFERENCES employee (empno)
      DESTINATION KEY (company_id) REFERENCES company (id)
      LABEL works_at
  );

SELECT * FROM GRAPH_TABLE (org
  MATCH (e IS person WHERE e.name = 'JONES') -[IS reports_to]->{1,5} (m IS person)
  COLUMNS (m.name AS manager_name)
);
```

- The graph is **metadata over tables**, like a view: no data copy, and the SQL engine plans it as joins. You get existing transactions, backups and security. Performance is whatever those joins cost.
- Read-only by standard. Writes go through normal SQL DML on the tables (Spanner Graph also supports only table-based DML).
- The keywords `VERTEX TABLES` and `NODE TABLES` are both accepted by the standard. Products differ on which they show.

## Gremlin

```groovy
// Friends' names
g.V().has('Person','name','Alice').out('KNOWS').values('name')

// Management chain, bounded
g.V().has('Person','name','Alice').
  repeat(out('REPORTS_TO')).times(10).emit().
  values('name')

// Friends-of-friends not already friends, with mutual count
g.V().has('Person','name','Alice').as('me').
  out('KNOWS').aggregate('friends').
  out('KNOWS').where(neq('me')).where(without('friends')).
  groupCount().by('name').
  order(local).by(values, desc).limit(local, 10)

// Shortest path (unweighted)
g.V().has('Person','name','Alice').
  repeat(both('KNOWS').simplePath()).until(has('name','Bob')).
  path().limit(1)
```

- It's a **traversal machine**: you describe *how* to walk, step by step. It's powerful and composable, and it's easy to write something correct but slow.
- It's portable across TinkerPop providers (JanusGraph, Neptune, Cosmos DB's Gremlin API, and others), but each provider supports a different subset of steps. Check the provider's compatibility notes.
- Use `simplePath()` to avoid cycles, `times()` or `until()` plus `loops()` to bound `repeat`, and `profile()` to read the plan.

## SPARQL

```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX ex:   <http://example.org/>

# Friends' names
SELECT ?name WHERE {
  ?me foaf:name "Alice" ;
      foaf:knows ?f .
  ?f  foaf:name ?name .
}

# Whole management chain: property paths (+ = one or more)
SELECT ?bossName WHERE {
  ?me foaf:name "Alice" ;
      ex:reportsTo+ ?boss .
  ?boss foaf:name ?bossName .
}

# Optional data and filtering
SELECT ?p ?email WHERE {
  ?p a foaf:Person .
  OPTIONAL { ?p foaf:mbox ?email }
  FILTER NOT EXISTS { ?p ex:deactivated true }
}
```

- `CONSTRUCT` returns a new graph, `ASK` returns a boolean, `DESCRIBE` returns everything about a resource, and `SERVICE` federates a query to another endpoint.
- Property paths (`+`, `*`, `/`, `|`, `^`) test reachability. They don't return the path itself.
- **SPARQL 1.2** (Working Draft, 2026) adds triple-term support to match RDF 1.2. Don't rely on it in production until your store documents it.

## Translating between languages

| Concept | Cypher/GQL | SQL/PGQ | Gremlin | SPARQL |
|---|---|---|---|---|
| Start point | `MATCH (n:L {k:v})` | `MATCH (n IS l WHERE n.k = v)` | `g.V().has('L','k',v)` | `?n a :L ; :k v` |
| One hop out | `-[:T]->` | `-[IS t]->` | `.out('T')` | `?n :t ?m` |
| Either direction | `-[:T]-` | `-[IS t]-` | `.both('T')` | `?n :t\|^:t ?m` |
| 1..k hops | `-[:T]->{1,k}` / `*1..k` | `-[IS t]->{1,k}` | `repeat(out('T')).times(k).emit()` | `:t+` (unbounded only) |
| Edge property | `[r:T] … r.p` | `[r IS t] … r.p` | `outE('T').values('p')` | reification / triple term |
| Aggregate | `count()`, `collect()` | SQL aggregates on `COLUMNS` | `groupCount()`, `fold()` | `GROUP BY`, `COUNT` |
