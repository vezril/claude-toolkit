# Items 49–77: Method design, general programming, exceptions

Effective Java 3rd ed., Items 49–77, faithful to Bloch and updated for Java 21.

## Contents

- Methods (49–56)
- General Programming (57–68)
- Exceptions (69–77)

---

## Methods

**49. Check parameters for validity.** Validate at the start of each public/protected method; document the constraints and the exception thrown (`@throws`). Use `Objects.requireNonNull`, and `Objects.checkIndex`/`checkFromToIndex` for ranges. Fail fast with a clear message. For private methods, use `assert`.

**50. Make defensive copies when needed.** If a class holds a mutable component supplied by or returned to a client, copy it on the way in *and* out — otherwise the client can violate your invariants. Copy *before* validation; don't use `clone` on a type that could be subclassed maliciously. (Immutable components need no copying — another reason to prefer immutability.)

**51. Design method signatures carefully.** Choose intention-revealing names; don't over-provide convenience methods; keep parameter lists short (≤ ~3); prefer interfaces and enums for parameter types; prefer two-element enums to `boolean` params.

**52. Use overloading judiciously.** Overloading is resolved at compile time by static type, which surprises people. Avoid two overloads with the same arg count where a single argument could match both; when in doubt, give methods different names.

**53. Use varargs judiciously.** Great for variable argument counts, but every call allocates an array. For a method requiring ≥1 argument, take the first explicitly then varargs. Consider the `(int, int...)`-style overloads for hot, low-arity paths.

**54. Return empty collections or arrays, not nulls.** Null returns force special-casing on callers and breed NPEs. Return `Collections.emptyList()`/`List.of()` or a zero-length array (cache the empty array).

**55. Return optionals judiciously.** Use `Optional<T>` for a scalar result that may be absent and where the caller must handle it. **Never** return `Optional` for collections (return empty instead), and **never** use `Optional` for fields or parameters. Consume with `orElse`/`orElseGet`/`orElseThrow`/`map`/`ifPresent` — not `get()`. Avoid boxing: use `OptionalInt`/`OptionalLong`/`OptionalDouble`.

**56. Write doc comments for all exposed API elements.** Javadoc every exported class, interface, method, field. Document the contract: preconditions (`@param`, `@throws`), postconditions (`@return`), and side effects; describe *what*, not *how*. Use `{@code}`, `@implSpec` for inheritance contracts.

## General programming

**57. Minimize the scope of local variables.** Declare each variable where first used, with an initializer; prefer `for` (incl. for-each) over `while` because the loop variable's scope is the loop. **Modern: `var` keeps declarations tight when the type is obvious.**

**58. Prefer for-each loops to traditional `for` loops.** Clearer and immune to index/iterator bugs; use the classic form only when you need the index or to modify the collection while traversing.

**59. Know and use the libraries.** Reuse `java.util`, `java.util.concurrent`, `java.time`, etc. — they're correct, fast, and maintained. E.g. use `ThreadLocalRandom`, not a hand-rolled RNG. Don't reinvent the wheel.

**60. Avoid `float` and `double` where exact answers are required.** They can't represent decimal fractions exactly — never use them for money. Use **`BigDecimal`**, or `int`/`long` (e.g. cents).

**61. Prefer primitive types to boxed primitives.** Boxing costs allocations and introduces `==` identity bugs and NPE-on-unbox. Use primitives by default; use boxed types only as type parameters, in collections, and where nullability is needed.

**62. Avoid strings where other types are more appropriate.** Don't use `String` for what should be a number, enum, or aggregate type. Strings as poor substitutes for real types cause bugs.

**63. Beware the performance of string concatenation.** Repeated `+` in a loop is O(n²). Use **`StringBuilder`** (or `String.join`/`Collectors.joining`/streams).

**64. Refer to objects by their interfaces.** Declare variables, params, returns, fields with the interface type (`List`, `Map`) not the implementation (`ArrayList`, `HashMap`). Flexible; swap implementations freely. (If no suitable interface, use the least specific class that works.)

**65. Prefer interfaces to reflection.** Reflection is powerful but costly and unsafe (loses compile-time checks). When you must instantiate reflectively, do so reflectively but **access via an interface/superclass** known at compile time.

**66. Use native methods judiciously.** JNI is rarely worth it for performance now and adds portability/safety risks; use it only for platform-specific facilities or proven-critical native libraries.

**67. Optimize judiciously.** Write good, clear programs first; don't sacrifice sound architecture for speed. Measure before and after optimizing (profilers, JMH). "Premature optimization is the root of all evil" — but design APIs that don't *preclude* performance.

**68. Adhere to generally accepted naming conventions.** Packages lowercase dotted; classes/interfaces `CamelCase`; methods/fields `camelCase`; constants `UPPER_SNAKE`; type params single letters (`T`, `E`, `K`, `V`). Follow library precedent for method names (`getX`, `toX`, `asX`, `valueOf`).

## Exceptions

**69. Use exceptions only for exceptional conditions.** Never for ordinary control flow; don't force clients to use exceptions for control flow (provide a state-testing method or an `Optional`/distinguished return).

**70. Use checked exceptions for recoverable conditions and runtime exceptions for programming errors.** Checked = the caller can reasonably recover; unchecked (`RuntimeException`) = precondition violations/bugs. Don't define new `Error` subclasses.

**71. Avoid unnecessary use of checked exceptions.** They burden callers and don't compose with streams/lambdas. If recovery isn't realistic, use an unchecked exception; consider returning `Optional` or splitting into a state-testing method + an unchecked-throwing action.

**72. Favor the use of standard exceptions.** Reuse `IllegalArgumentException`, `IllegalStateException`, `NullPointerException`, `IndexOutOfBoundsException`, `UnsupportedOperationException`, `ConcurrentModificationException`. Don't invent equivalents.

**73. Throw exceptions appropriate to the abstraction.** Don't leak low-level exceptions from a higher-level API; translate (exception translation), optionally chaining the cause (`new HighLevelException(cause)`). Better still, prevent the lower-level failure.

**74. Document all exceptions thrown by each method.** `@throws` for every checked exception (don't use a blanket `throws Exception`), and document unchecked exceptions (preconditions) too, without listing them in the method's `throws` clause.

**75. Include failure-capture information in detail messages.** Put the values of all parameters/fields that contributed to the failure in the exception message (not in the user-facing UI) so a stack trace is diagnosable.

**76. Strive for failure atomicity.** A failed method call should leave the object in its pre-call state — validate before mutating, operate on a copy, or order computation so failure precedes mutation. (Immutable objects are failure-atomic for free.)

**77. Don't ignore exceptions.** Never leave a `catch` block empty. If you genuinely must ignore one, comment why and name the variable `ignored`.
