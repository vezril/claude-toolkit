# Items 26–48: Generics, enums & annotations, lambdas & streams

Effective Java 3rd ed., Items 26–48, faithful to Bloch and updated for Java 21.

## Contents

- Generics (26–33)
- Enums and Annotations (34–41)
- Lambdas and Streams (42–48)

---

## Generics

**26. Don't use raw types.** `List` (raw) defeats generic type checking; use `List<String>` or `List<?>` (unbounded wildcard) when the element type is unknown. Raw types exist only for migration compatibility.

**27. Eliminate every unchecked warning.** Each one is a potential `ClassCastException`. Fix it; if you've proven it safe and can't remove it, suppress with `@SuppressWarnings("unchecked")` on the **narrowest** scope plus a comment explaining why it's safe.

**28. Prefer lists to arrays.** Arrays are covariant and reified; generics are invariant and erased — they mix badly (`new List<String>[]` is illegal). Prefer `List<E>` over `E[]`; you get compile-time type safety.

**29. Favor generic types.** Parameterize your own types instead of using `Object` and casting. Compile-time safety, no casts for clients.

**30. Favor generic methods.** Make methods generic rather than requiring casts. The type inference usually makes calls clean. (Generic singleton factory and recursive type bounds, e.g. `<T extends Comparable<T>>`, are useful idioms.)

**31. Use bounded wildcards to increase API flexibility.** **PECS — Producer `extends`, Consumer `super`.** A parameter that produces `T`s is `? extends T`; one that consumes `T`s is `? super T`. Makes APIs far more flexible. Don't use a wildcard as a return type.

**32. Combine generics and varargs judiciously.** Generic varargs create unsafe heap pollution. If your generic-varargs method is safe (doesn't store or expose the array), annotate it `@SafeVarargs`; otherwise prefer a `List` parameter.

**33. Consider typesafe heterogeneous containers.** When you need a container keyed by type, use `Class<T>` as the key (`Map<Class<?>, Object>` with `cast`) for type-safe per-type values.

## Enums and annotations

**34. Use enums instead of `int` constants.** Type-safe, namespaced, printable, and they can carry data and behavior (constant-specific methods). The single biggest readability/safety win in this chapter.

**35. Use instance fields instead of ordinals.** Never derive logic from `ordinal()`; store needed values in explicit fields.

**36. Use `EnumSet` instead of bit fields.** `EnumSet` is as compact and fast as bit flags but type-safe and readable.

**37. Use `EnumMap` instead of ordinal indexing.** Don't index arrays by `ordinal()`; use `EnumMap` (or nested `EnumMap`/streams) for enum-keyed data.

**38. Emulate extensible enums with interfaces.** Enums can't be extended, but they can implement an interface; clients depend on the interface, allowing multiple enum implementations (e.g. an operations API).

**39. Prefer annotations to naming patterns.** Don't encode meaning in names (like JUnit 3's `testXxx`); use annotations the framework reads reflectively.

**40. Consistently use the `@Override` annotation.** Let the compiler catch methods you meant to override but didn't (signature typos). Use it on every override.

**41. Use marker interfaces to define types.** A marker interface (e.g. `Serializable`) defines a type and enables compile-time checks; prefer it over a marker annotation when you want a type. Marker annotations suit non-type program elements.

## Lambdas and streams (Java 8+)

**42. Prefer lambdas to anonymous classes.** For function objects, lambdas are far more concise. Keep them short (a line or few); omit parameter types unless they aid clarity. Lambdas lack names/`this` to the instance — use an anonymous class only when you need those.

**43. Prefer method references to lambdas.** When a lambda just calls an existing method, a method reference (`Integer::parseInt`, `String::toLowerCase`, `this::method`) is usually clearer — but stick with the lambda when it reads better.

**44. Favor the use of standard functional interfaces.** Use `java.util.function` (`Function`, `Predicate`, `Supplier`, `Consumer`, `BiFunction`, `UnaryOperator`, etc.) instead of inventing your own. Define a custom functional interface only for a meaningful contract or extra methods; annotate it `@FunctionalInterface`.

**45. Use streams judiciously.** Streams shine for transforming/filtering/aggregating sequences, but overuse hurts readability. Don't force everything into one giant pipeline; mix with loops where clearer. Avoid streams of `char` (broken). Name intermediate variables and lambda params well.

**46. Prefer side-effect-free functions in streams.** The stream paradigm is functional: build results with **collectors** (`toList`, `groupingBy`, `toMap`, `joining`), not by mutating external state in `forEach`. `forEach` is for *reporting* a result, not computing it. **Modern: use `Stream.toList()`** (Java 16+) for an unmodifiable list.

**47. Prefer `Collection` to `Stream` as a return type.** A `Collection` (or subtype) serves both stream and for-each callers; return `Stream` only when the sequence is best consumed as a stream and can't be a collection cheaply.

**48. Use caution when making streams parallel.** `parallel()` rarely helps and often hurts or breaks correctness (especially with stateful/ordered ops or `limit`). Parallelize only with measurement, typically over `ArrayList`/`arrays`/`IntStream.range`/`ConcurrentHashMap` with cheap, associative operations.
