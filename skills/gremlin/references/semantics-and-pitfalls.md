# Gremlin semantics and pitfalls

The things that make a query return nothing, too much, or the wrong shape.

## Laziness and terminal steps

- A traversal is a plan. It runs when iterated: `toList()`, `next()`, `iterate()`, `hasNext()`, `tryNext()`, or implicitly in the Console.
- **Writes need `iterate()`** in application code. In the Console they "work" because it auto-iterates.
- `next()` on an empty traversal throws. Use `tryNext()` (Optional) or `hasNext()` first. `next(n)` returns up to n.
- Reusing a traversal object after iterating it doesn't re-run it. Build a new one from `g`.

## Traversers, bulk and duplicates

- Each hop multiplies traversers: 3 friends, each with 3 friends, gives 9 traversers, including duplicates and yourself. `dedup()` after expanding hops, and `where(neq('me'))` to drop the start vertex.
- Traversers with the same object can be **bulked** (counted once, weighted). `count()` respects bulk. From 3.8.0, `local()` splits bulked traversers, which can change results inside `local` compared to 3.7.
- `simplePath()` removes paths that revisit an element. You need it for cycles, and it costs path tracking.

## Scope: global vs local

- Most reducing steps are **global**: `count()`, `order()`, `limit()`, `dedup()`, `sum()` and friends operate across *all* traversers.
- The `local` scope (or `local(…)`) applies them **per object**, typically inside a collection or map: `order(local)`, `limit(local, 3)`, `count(local)`, `unfold()` then `local(...)`.
- Classic bug: `g.V().hasLabel('person').out('KNOWS').limit(2)` gives 2 friends *in total*. For "2 friends *each*", write `g.V().hasLabel('person').local(out('KNOWS').limit(2))`.

## Labels, `select` and `Pop`

- `as('x')` labels the object at that step. `select('x')` retrieves it later, and `select('x','y')` returns a map.
- If a label was set multiple times (inside `repeat`, say), `select` returns according to `Pop`: `first`, `last` (the default behaviour in most cases), `all` (a list) or `mixed`. Be explicit (`select(last, 'x')`) when labels repeat.
- `select(keys)` / `select(values)` project map entries (`order(local).by(values, desc)` sorts a map by value).
- `where(neq('me'))` compares the current object to the object labeled `me`, and `where('a', eq('b'))` compares two labels.

## `by()` modulators

- The meaning of `by()` depends on the step it modulates: `order().by(key, desc)`, `group().by(keyFn).by(valueFn)`, `project('a','b').by(x).by(y)` (one per key, in order), `path().by('name')` (round-robin across path elements), `dedup().by('email')`.
- A **`by('prop')` on an element missing that property** is an *unproductive* `by()`. Since 3.6 that generally filters the traverser out of `order`, `dedup` and similar steps rather than throwing (older versions threw), and the exact behaviour of `project`/`group` has shifted between versions. Don't rely on it: write `by(coalesce(values('p'), constant(default)))` whenever absence is possible.

## Missing properties, null and types

- There's a difference between a **missing property** and **null**. Most providers don't store nulls (Cosmos DB rejects them). Setting a property to null removes it on TinkerGraph-like providers. So model "unknown" as *absent* and test for it with `hasNot('p')` or `not(has('p'))`.
- `values('p')` on an element without `p` emits nothing. That silently shortens lists, so `count()` counts only the elements that have `p`.
- **Comparisons across incompatible types** (a string vs a number in `lt`) don't match; they aren't errors. Since 3.6, Gremlin uses ternary predicate logic in which an "error" state resolves to *false* in a filter. `has('age', gt(30))` silently drops elements whose `age` was stored as a string. Keep property types consistent per key and cast at load time.
- `NaN` is never equal to itself. Numbers compare across numeric types (`1` == `1L` == `1.0`), with type promotion in math and aggregation.
- `order()` imposes a total order across types (so mixed-type sorts don't throw), but mixing types in a sort key is still a data bug.

## Cardinality

- The provider sets the default: TinkerGraph `single`, **Neptune `set`**, Cosmos DB `list` (`set` unsupported).
- `property('k', v)` without a cardinality can **append** a second value on set/list providers. Always write `property(single,'k',v)` for scalar attributes in portable code.
- Multi-valued properties make `values('k')` emit several rows, and `valueMap()` always returns lists. Use `elementMap()` to unwrap single values, or `project(...).by('k')`, which takes the first value.

## `has` vs `where` vs `filter`

- `has(...)` tests element properties and is the step providers push down into indexes. Prefer it.
- `where(traversal)` tests whether a sub-traversal produces something (`where(out('BOUGHT'))`). `where(P)` compares to labels.
- `filter(traversal)` is the general form of `where(traversal)`. `not(t)` negates it.
- `has(key, traversal)` was **removed in 3.8.0**. Use `where(values(key).…)`.

## Branching gotchas

- `choose(pred, a, b)` evaluates `pred` as a traversal. Anything produced counts as true.
- **3.8.0:** `choose(...).option(...)` runs only the **first** matching option, and unmatched traversers pass through unchanged. 3.7 behaved differently for overlapping options.
- `coalesce` returns the first *non-empty* branch. `union` returns all of them. `optional(t)` is `coalesce(t, identity())`.
- `repeat` placement matters: `until` *before* `repeat` is while-do (it can emit the start), and after it is do-while. `emit()` before `repeat` includes the start vertex. From 3.8.0, `limit`, `range` and `skip` inside `repeat` count per iteration.

## Remote results are references

Over a driver connection, a returned `Vertex` or `Edge` carries only `id` and `label` (TinkerPop 3.7's `materializeProperties` isn't supported everywhere; Neptune ignores it). Always project what you need. Returning `g.V(id).next()` and reading properties client-side is the most common remote-Gremlin bug.

## Reading `profile()`

- Each row is a step with **traverser count**, **element count**, **time** and **% duration**.
- **Huge counts at an `out()`/`both()` step** means fan-out (a supernode, or a missing label or filter). Filter the edge first, or specialise the relationship type.
- **A start step with full-graph counts** means the anchor didn't use an index: an unlabeled `has`, a non-indexed key, or a predicate the index can't serve (for example `TextP.containing` on a composite index).
- **A `RepeatStep` dominating** means an unbounded or too-deep loop. Add bounds, `simplePath()` and `dedup()`.
- Provider equivalents: Neptune `/gremlin/profile` and `/gremlin/explain`, Cosmos DB `executionProfile()`, JanusGraph `profile()` with index annotations.
