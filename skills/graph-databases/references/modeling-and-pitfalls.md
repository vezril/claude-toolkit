# Graph modeling and pitfalls

## A method that works

1. **List the questions.** Write the 5–10 traversals the system must answer, in plain language, with their expected depth and latency ("given a card, find every account within 3 hops that shares a device or address; under 50 ms").
2. **Sketch the whiteboard graph.** Nouns become candidate nodes, verbs become candidate relationships. Draw each question as a path through it.
3. **Decide node vs property vs relationship** for each item (rules below).
4. **Name relationships as specific verbs**, in UPPER_SNAKE (`:DEPENDS_ON`, `:SHIPPED_TO`), with one consistent direction.
5. **Choose entry points and index them.** Every query starts from a lookup, so add a unique constraint on its business key.
6. **Load realistic data, including the skew**, and profile each question (`EXPLAIN`/`PROFILE`, Gremlin `profile()`). The skew is where supernodes show up.
7. **Record the model and why** (an ADR, see [[software-architecture]]), including the questions it was built for.

## Node, property or relationship?

| Make it a… | When | Example |
|---|---|---|
| **Property** | You display or filter on it, and don't traverse through it | `Person.birthYear`, `Order.total` |
| **Node** | It's shared by many entities and you'll ask "who else has this?" | `Address`, `Device`, `IP`, `City`, `Skill` |
| **Relationship** | It connects two entities and is described by a verb | `(:Person)-[:KNOWS]->(:Person)` |
| **Node, promoted from a relationship** | The connection has its own identity, involves more than two parties, has its own relationships, or has history | `(:Person)-[:PLACED]->(:Order)-[:CONTAINS]->(:Product)`; an `Employment` node with `role` and `period` linked to a `Team` |
| **Label** | A small, fixed set of categories you filter on constantly | `:Customer`, `:Vip`, `:Deleted`. Avoid unbounded label sets |

The fraud-detection classic is the "who else has this?" test: an `address` string on 10M accounts can't be traversed, but an `Address` node makes "accounts sharing an address with this one" a two-hop pattern.

## Worked examples

**Fraud ring (first-party fraud):**
```
(:Account)-[:HAS_PHONE]->(:Phone)
(:Account)-[:HAS_ADDRESS]->(:Address)
(:Account)-[:USED_DEVICE]->(:Device)
(:Account)-[:PAID_WITH]->(:Card)
```
The question: connected components of accounts linked through shared identifiers. Traverse at request time from one account, bounded to about 3–4 hops. Compute global components offline (OLAP) and write a `ringId` back onto the nodes.

**Org chart and access:**
```
(:Person)-[:REPORTS_TO]->(:Person)
(:Person)-[:MEMBER_OF]->(:Group)-[:MEMBER_OF]->(:Group)
(:Group)-[:CAN_ACCESS {level}]->(:Resource)
```
"Can Alice access X?" becomes a bounded path over `MEMBER_OF*` then `CAN_ACCESS`. Nested groups are exactly where joins get painful and patterns stay short.

**Service dependency / lineage:**
```
(:Service)-[:DEPENDS_ON]->(:Service)
(:Dataset)-[:DERIVED_FROM {job}]->(:Dataset)
```
Impact analysis is downstream reachability, and root cause is upstream reachability. Cycles exist in real systems, so use path uniqueness (`TRAIL` or `ACYCLIC` in GQL, `simplePath()` in Gremlin).

## Supernodes (dense nodes)

A node with a huge number of relationships: a popular celebrity, a `Country`, a "status" node, a shared `Unknown` address, a default device id.

- **Symptoms:** a traversal that passes *through* the node suddenly touches millions of edges. Writes contend on it.
- **Fixes, roughly in order:**
  1. **Don't model it as a node** if you never traverse through it. Make it a property (`status: 'ACTIVE'`).
  2. **Specialize relationship types** so traversals only follow the slice they need (`:FOLLOWS_2026` vs one giant `:FOLLOWS`, or `:LIVES_IN` vs `:BORN_IN`).
  3. **Bucket or fan out:** intermediate nodes by time or category (`(:Celebrity)-[:FOLLOWERS_BUCKET]->(:Bucket {month})`).
  4. **Stop at it:** add a degree filter to the query and treat high-degree nodes as terminals.
  5. **Clean the data:** placeholder values ("N/A" address, all-zero device id) are the most common accidental supernodes in fraud graphs.

## Time and history

Graphs have no built-in versioning, so pick a scheme deliberately:
- **Validity properties on relationships** (`from`, `to`). Simple, and good for "as of" queries on a few relationship types.
- **State nodes**: `(:Product)-[:HAS_STATE]->(:ProductState {validFrom, validTo, price})` when many attributes change together.
- **Event-sourced source of truth, graph as a projection** (see [[cqrs-event-sourcing]]): rebuild or replay into the graph. This is often the cleanest option when history must be auditable.
- **RDF:** use named graphs per version or source.

## Anti-patterns

- **The relational schema copied into a graph**: join tables become relationships, but nothing else changes, and the queries stay join-shaped. Remodel around the questions.
- **Generic relationships** (`:RELATED_TO {type: 'manager'}`) defeat type-based traversal and indexing. Use specific types.
- **Everything is a node**, including attributes you never traverse. That bloats the graph and slows every hop.
- **Unbounded variable-length paths** in production queries.
- **Storing both directions** of a symmetric relationship. Store once and query undirected.
- **A graph DB as the system of record for set-oriented data** (ledgers, reporting). Keep that relational or columnar, and project the connected part into the graph.
- **OLAP on the OLTP instance:** running PageRank over the live cluster during business hours.
- **Picking on a benchmark you didn't run.** Vendor benchmarks pick favourable queries, so run your top questions on your data.

## Graph vs relational: a decision checklist

Graph is likely worth it if most of these are true:
- [ ] Core queries have variable or unknown depth, or are path or pattern shaped
- [ ] The number of relationship types or their shape changes often
- [ ] You need multi-hop answers at interactive latency
- [ ] The same entities connect in many ways (people, devices, accounts, documents)

Stay relational, or use SQL/PGQ or recursive CTEs, if:
- [ ] Most queries are aggregates, reports or bulk updates
- [ ] Depth is fixed and small (1–2 joins)
- [ ] You need the relational ecosystem (BI, strict schema, mature operations) more than traversal speed
- [ ] You haven't measured a meaningful win on your own queries
