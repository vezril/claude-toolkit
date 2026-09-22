# Gremlin cookbook

Groovy/Java syntax (see `glv-syntax.md` for other languages). Assume `import static …__.*`, `P.*`, `T`, `Merge`, `Direction` and `Order`. The sample schema: `person(email, name, age)`, `product(sku, name, price)`, `(person)-[KNOWS {since}]->(person)`, `(person)-[BOUGHT {at, qty}]->(product)`.

## Reads

```groovy
// By ID / by key
g.V('p1').elementMap()
g.V().has('person','email','a@x.io').elementMap('name','age')

// Existence check (cheap)
g.V().has('person','email','a@x.io').hasNext()          // in code
g.V().has('person','email','a@x.io').limit(1).count()   // as a value

// Several keys at once
g.V().has('person','email', within('a@x.io','b@x.io')).values('name')

// Range and text filters
g.V().has('product','price', between(10, 50)).has('name', TextP.containing('lamp')).values('sku')

// Properties that may be missing
g.V('p1').project('name','nick').by('name').by(coalesce(values('nickname'), constant('')))
g.V().hasLabel('person').hasNot('email')                 // people with no email
```

## Neighbourhoods and degree

```groovy
g.V('p1').out('KNOWS').values('name')                                  // direct
g.V('p1').both('KNOWS').dedup().values('name')                         // undirected
g.V('p1').as('me').out('KNOWS').out('KNOWS').where(neq('me')).dedup()  // 2-hop, excluding me
// note: where(neq('x')) compares to the step LABELED 'x', not to an id; for ids use not(hasId('p1'))

// Filter on the edge before crossing it
g.V('p1').outE('BOUGHT').has('at', gte('2026-01-01')).inV().values('sku')

// Degree and top connected nodes (watch supernodes)
g.V('p1').both('KNOWS').count()
g.V().hasLabel('person').order().by(both('KNOWS').count(), desc).limit(10).
  project('name','degree').by('name').by(both('KNOWS').count())
```

## Paths

```groovy
// Unweighted shortest path, depth-guarded
g.V('p1').repeat(both('KNOWS').simplePath()).
  until(hasId('p9').or().loops().is(gte(6))).
  hasId('p9').path().by('name').limit(1)

// All simple paths up to 4 hops
g.V('p1').repeat(out('KNOWS').simplePath()).emit().times(4).hasId('p9').path().by('name')

// Weighted path cost with sack (sum of edge weights along a path)
g.withSack(0).V('a').repeat(outE('ROAD').sack(sum).by('km').inV().simplePath()).
  until(hasId('z')).limit(5).project('path','km').by(path().by(id)).by(sack())
```
For a true weighted shortest path on big graphs, use the provider's algorithm (Neptune Analytics, OLAP, or a provider `shortestPath` step) rather than enumerating paths.

## Aggregation

```groovy
g.V().hasLabel('person').groupCount().by('city')                         // counts per key
g.V().hasLabel('person').group().by('city').by(values('age').mean())    // avg age per city
g.V().hasLabel('person').group().by('city').by(values('name').fold())   // names per city
g.V('p1').out('BOUGHT').values('price').sum()
g.V('p1').outE('BOUGHT').group().by(inV().values('sku')).by(values('qty').sum())

// Top-k from a map
g.V().hasLabel('product').groupCount().by('category').
  order(local).by(values, desc).limit(local, 5)

// Several aggregates in one pass
g.V().hasLabel('product').fold().project('n','avg','max').
  by(count(local)).by(unfold().values('price').mean()).by(unfold().values('price').max())
```

## Ordering and pagination

```groovy
g.V().hasLabel('product').order().by('price', desc).by('sku').range(20, 40).elementMap('sku','price')
// Keyset pagination (scales; range() still scans the skipped rows)
g.V().hasLabel('product').has('sku', gt(lastSku)).order().by('sku').limit(20).values('sku')
// Total alongside a page
g.V().hasLabel('product').fold().project('total','page').
  by(count(local)).by(unfold().order().by('sku').range(0,20).values('sku').fold())
```

## Conditional logic

```groovy
g.V('p1').choose(values('age').is(gte(18)), constant('adult'), constant('minor'))
g.V().hasLabel('person').project('name','tier').by('name').
  by(choose(values('spend').is(gte(1000)), constant('gold'), constant('std')))
g.V('p1').coalesce(out('MANAGER'), out('TEAM').out('LEAD'), constant('none'))   // first that exists
g.V('p1').optional(out('SPOUSE')).values('name')                                // self if absent
```

## Writes

```groovy
// Create
g.addV('person').property(T.id,'p1').property('email','a@x.io').property('name','Ada').iterate()
g.addE('KNOWS').from(__.V('p1')).to(__.V('p2')).property('since',2026).iterate()

// Upserts (3.6+)
g.mergeV([(T.label):'person', email:'a@x.io']).
  option(Merge.onCreate, [name:'Ada', createdAt:'2026-09-21']).
  option(Merge.onMatch,  [lastSeen:'2026-09-21']).iterate()
g.mergeE([(T.label):'KNOWS', (Direction.from):'p1', (Direction.to):'p2']).
  option(Merge.onCreate, [since:2026]).iterate()

// Pre-3.6 get-or-create
g.V().has('person','email','a@x.io').fold().
  coalesce(unfold(), addV('person').property('email','a@x.io')).iterate()

// Update: always say the cardinality where a provider defaults to set/list
g.V('p1').property(single,'age',37).iterate()

// Batch writes: one request, many rows (keep batches to hundreds, not millions)
g.inject([[(T.label):'person', email:'a@x.io', name:'Ada'],
          [(T.label):'person', email:'b@x.io', name:'Bo']]).unfold().mergeV().iterate()

g.inject([[(T.label):'KNOWS', (Direction.from):'p1', (Direction.to):'p2', since:2026],
          [(T.label):'KNOWS', (Direction.from):'p2', (Direction.to):'p3', since:2025]]).unfold().mergeE().iterate()
// Note: every key in the map (including since) is part of the match. Put create-only values in option(Merge.onCreate, ...)
// by using a traversal per row, or send one mergeE per row in small client-side batches.
```

## Deletes

```groovy
g.V('p1').drop().iterate()                                   // vertex + its edges
g.V('p1').outE('KNOWS').where(inV().hasId('p2')).drop().iterate()
g.V('p1').properties('nickname').drop().iterate()             // one property
g.V().hasLabel('temp').limit(10000).drop().iterate()          // chunk big deletes; loop until 0
```

## Strings, dates and numbers (3.7+/3.8)

```groovy
g.V().hasLabel('person').values('name').toUpper()
g.V().hasLabel('person').project('slug').by(values('name').toLower().replace(' ', '-'))
g.V('p1').format('%{name} (%{age})')
g.V('o1').values('placedAt').asDate().dateAdd(DT.day, 30)     // due date
g.V('o1').project('ms').by(values('shippedAt').asDate().dateDiff(__.values('placedAt').asDate()))  // ms in 3.8
g.inject('42').asNumber()
```
String and date steps need a provider on 3.7+. Older providers and Cosmos DB don't have them, so do the transformation client-side.

## Subgraphs and export

```groovy
// Edge-induced subgraph around a vertex (embedded/Console; remote returns a Graph only on some providers)
g.V('p1').bothE('KNOWS').subgraph('sg').otherV().bothE('KNOWS').subgraph('sg').cap('sg').next()
// Portable alternative: return the edges as data
g.V('p1').bothE('KNOWS').project('from','to','since').by(outV().id()).by(inV().id()).by('since')
```
