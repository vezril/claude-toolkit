---
name: functional-programming
description: Functional programming discipline — separating actions, calculations, and data (ACD); pure functions, immutability via copy-on-write and defensive copying; total functions; algebraic data types; making illegal states unrepresentable; stratified design; and a pure core / onion architecture with effects pushed to the edge. Use when designing or reviewing code that should be functional, classifying code as action/calculation/data, extracting a calculation out of an action, minimizing implicit inputs/outputs, choosing an immutability discipline, organizing code into layers (stratified/onion architecture), modeling a domain with ADTs and smart constructors, choosing how to represent errors (Either vs exceptions), deciding whether a function needs an Either wrapper, eliminating var/mutable state/imperative loops, or separating pure logic from IO/side effects. Default style in the scala-bioinformatics project (Scala + Cats Effect). Apply even when not named explicitly — any work introducing a domain type, algorithm, or effectful boundary should follow these principles.
---

# Functional Programming

Build programs out of **pure functions over immutable data**, model the domain so illegal states can't be represented, and keep effects at the edges. These principles are language-agnostic; the examples are Scala because that's this project's stack.

If the user's explicit instructions conflict with this skill, the user wins. Otherwise this is the default style.

## The core lens: actions, calculations, data

Every piece of code is one of three things. Classify before you design, and the right structure usually follows:

- **Data** — inert facts about events: a parsed record, a count, an email address. No behavior, just values. Easiest to understand, store, and compare.
- **Calculations** — pure computations from input to output (a.k.a. pure functions). Same input → same output, no side effects. *Referentially transparent*: a call can be replaced by its result without changing the program. This is exactly what *Purity* (below) describes.
- **Actions** — anything that depends on *when* or *how many times* it runs: IO, reading the clock/random, mutation, network, printing. These are the hard part; everything that touches them becomes an action too.

Prefer the cheapest category that does the job: **push actions toward calculations, and calculations toward data** where you can. An action that only needs its inputs made explicit can often become a calculation; a calculation whose results are finite and fixed can sometimes become a lookup table (data). The whole skill is, in effect, techniques for shrinking the action surface and growing the pure, data-driven core.

This classification drives the architecture: calculations and data form the pure core (the onion's inner layers — see *Pure core, effectful shell*), actions live at the edge.

## Purity

A pure function: same input → same output, every time, with no observable side effects (no mutation of shared state, no IO, no clock/random reads, no throwing for control flow).

- **No `var`, no mutable collections, no imperative loops.** Use `foldLeft`, `map`, `flatMap`, `collect`, recursion, or comprehensions instead. Review every function for these before declaring it done.
- **Accumulate with `foldLeft`** when building up a result; **`map`/`flatMap` + `mkString`/`toVector`** when producing a new collection. Example: counting bases is a `foldLeft` over the sequence into a result record using `.copy`; transcribing is a `flatMap` producing a new string.
- Purity makes code trivially testable (no setup/teardown, no mocks) and safe to reason about locally. This is *why* the [[tdd]] cycle is cheap here.

## Extracting calculations from actions

When logic is tangled inside an action, pull the decision-making out into a calculation that the action merely calls. The mechanical move: identify what the code reads and what it writes, turn the reads into explicit parameters and the writes into a returned value, and the body becomes pure.

**Minimize implicit inputs and outputs.** An implicit input is anything a function depends on that isn't an argument (a global, the clock, shared mutable state); an implicit output is any effect other than the return value (mutating an argument, writing a global, printing). Every implicit in/out is what makes a function an action and makes it hard to test and reuse. Convert them to explicit arguments and return values until nothing is left — at which point the function *is* a calculation.

- Fewer implicit inputs/outputs → more reusable (callers control everything via arguments) and more testable (call it, check the return value).
- This is the same principle as a smart constructor taking a raw value and returning a result, rather than reaching out to read or mutate something on the side.

## Immutability discipline

Calculations require immutable data. Two complementary disciplines keep data immutable even in a language that allows mutation:

**Copy-on-write** — for data you own. To "modify" immutable data, do three steps: (1) make a copy, (2) modify the copy, (3) return the copy. The original is never touched, so a write becomes a read — and a read of immutable data is a calculation. In Scala this is mostly free: persistent collections (`Vector`, `Map`, `List`) and `case class` `.copy` already return new values via structural sharing rather than mutating; the discipline is simply to *never* reach for a mutable collection or `var`. See [[scala]] for the mechanics.

**Defensive copying** — for data crossing a boundary with code you don't trust to respect immutability (legacy code, a mutable Java/3rd-party API). Two rules: (1) **deep-copy data as it leaves** your code into untrusted code, and (2) **deep-copy data as it enters** from untrusted code. Then nothing they hold can mutate your values and nothing they hand you can be mutated under you. Deep copies are more expensive than the shallow copies of copy-on-write, so reserve defensive copying for the trust boundary; use copy-on-write everywhere inside it. In a fully immutable Scala core you rarely need it — it's the escape hatch at the edge.

## Total functions: don't wrap what can't fail

A **total** function has a defined output for every input of its type. If the input type already guarantees validity, the function cannot fail — so return the bare result, not `Either`/`Option`.

- If `transcribe` takes a validated `DnaString`, its output is always a valid `RnaString`. Return `RnaString`, **not** `Either[Error, RnaString]`. Adding an error channel "just in case" forces every caller to handle an impossible case and lies about the contract.
- The place for `Either` is the **boundary** where untrusted data enters (a smart constructor parsing a raw `String`). Once past that boundary, the type system carries the guarantee and downstream functions stay total.
- Likewise pick the tightest result type: a count with only a trivial "non-negative" invariant can be a bare `BigInt`; a probability constrained to `[0,1]` deserves its own validated value type.

## Make illegal states unrepresentable

Push invariants into types so bad values can't be built, rather than checking at every use site.

### Algebraic data types (ADTs) for closed alphabets

A fixed set of cases → a **sealed trait + case objects**. The compiler then enforces exhaustive pattern matching, so adding a case surfaces every site that must handle it:

```scala
sealed trait DnaNucleotide
object DnaNucleotide {
  case object A extends DnaNucleotide
  case object C extends DnaNucleotide
  case object G extends DnaNucleotide
  case object T extends DnaNucleotide
}
```

Keep genuinely distinct things as **distinct types**. DNA and RNA nucleotides do *not* share a parent trait — a shared `Nucleotide` would let `T` slip into an RNA context and defeat the point. Independence at the type level is a feature, not duplication.

### Smart constructors for validated data

A type with an invariant exposes a private constructor and a `from` that validates and returns `Either[Error, T]`:

```scala
sealed abstract case class UnrootedBinaryTreesProblem(taxa: Vector[String])

object UnrootedBinaryTreesProblem {
  def from(taxa: Vector[String]): Either[UnrootedBinaryTreesProblemError, UnrootedBinaryTreesProblem] =
    if (taxa.size < 3)      Left(...TooFewTaxa(taxa.size, 3))
    else if (taxa.size > 10) Left(...TooManyTaxa(taxa.size, 10))
    else firstDuplicate(taxa) match {
      case Some(name) => Left(...DuplicateTaxon(name))
      case None       => Right(new UnrootedBinaryTreesProblem(taxa) {})
    }
}
```

- Validate **at the boundary, once**. After `from` succeeds, the value is trusted everywhere — no re-checking.
- **First failure wins**, in a documented order. Each failure path is a behavior the [[tdd]] tests should cover.
- For a trusted internal path where validity is guaranteed by construction (e.g. the output of a total transform fed straight into a wrapper), provide an `unsafeFrom` that skips re-validation — and document *why* the value is known valid.

## Errors as values, not exceptions

Model expected failures as data: `Either[Error, T]` for fallible construction, `Option[T]` for "absent". Errors themselves are ADTs — a sealed hierarchy of named cases carrying the offending data:

```scala
sealed trait UnrootedBinaryTreesProblemError
object UnrootedBinaryTreesProblemError {
  final case class TooFewTaxa(count: Int, min: Int)   extends UnrootedBinaryTreesProblemError
  final case class TooManyTaxa(count: Int, max: Int)  extends UnrootedBinaryTreesProblemError
  final case class DuplicateTaxon(name: String)       extends UnrootedBinaryTreesProblemError
}
```

- Reserve thrown exceptions for truly unrecoverable, programmer-error situations — not for validation or expected branches.
- Don't pre-split error types speculatively. Share one error type until cases genuinely diverge in meaning, then split.

## Pure core, effectful shell

Structure the program as a **pure functional core** wrapped by a thin **effectful shell**. This is the **onion architecture**: concentric layers where actions live only on the outside and everything calls inward.

- **Interaction layer** (outer) — the actions: IO, file/network reads, printing, the clock. The Cats Effect `IOApp` entry point and per-task runners.
- **Domain layer** (middle) — calculations that encode the business rules: pure domain types and the total/fallible functions over them.
- **Language layer** (inner) — general utilities and the language/library primitives the domain is built from.

Three rules make it work: interaction with the world happens *only* in the interaction layer; layers call *inward* toward the center; a layer never knows about the layers outside it. Contrast the traditional layered architecture (web → domain → database), where the database sits at the bottom and therefore *everything above it is an action* — that's why it isn't functional. Putting calculations at the center, with actions as a thin outer rind, is what gives a functional architecture its prominent pure core.

- Domain types and algorithms are pure — no `IO`, no side effects. They're just data and total/fallible functions over it.
- All effects (reading files, printing, the clock) live at the boundary — here, the Cats Effect `IOApp` entry point and the per-problem runners that do `IO.blocking` reads and `IO.println`:

```scala
def solve(): IO[Unit] =
  for {
    raw     <- IO.blocking(new String(Files.readAllBytes(Paths.get(DataPath))))
    taxa     = raw.split("\\s+").iterator.filter(_.nonEmpty).toVector
    result   = UnrootedBinaryTreesProblem.from(taxa).left.map(_.toString)
    _       <- result match {
                 case Left(err)      => IO.println(err)
                 case Right(problem) => IO.println(enumerate(problem).format)
               }
  } yield ()
```

- The shell parses input → calls the pure core → renders/prints the result. Keep logic *out* of the shell; keep effects *out* of the core.
- No bare `println` — console output goes through `IO.println` (or the project's IO equivalent) so it stays in the effect type.

## Stratified design

Organize functions into layers by **rate of change** and level of detail, so each function is built only from functions roughly one level of abstraction below it. Read as a call graph, well-stratified code forms comfortable layers rather than one function reaching across many levels at once. Four patterns to aim for:

1. **Straightforward implementations** — a function should read at a single, consistent level of detail; its body shouldn't mix high-level intent with low-level fiddling. If it does, extract the low-level part into a helper one layer down.
2. **Abstraction barrier** — a small set of functions that lets callers operate on a structure (e.g. a cart) without knowing its representation. Above the barrier you forget the implementation; below it you forget who calls you. This lets you swap the underlying data structure without touching callers.
3. **Minimal interface** — define new operations in terms of the existing minimal set rather than growing the barrier; keep the core interface small so there's less to maintain and reason about.
4. **Comfortable layers** — stop refactoring when the layers are good enough to work in comfortably; don't abstract for its own sake.

What the call graph tells you: **code near the top is easiest to change** (little is built on it) — put fast-changing business rules there. **Code near the bottom is more reused and more depended-upon** — keep it stable and test it most thoroughly. This dovetails with keeping stable, total primitives (see *Total functions*) at the bottom, and with the onion layering above.

## Composition

Prefer composing small functions over one big procedure. Dispatch through the ADT (`fromChar` → pattern match → `toChar`) rather than reaching for raw primitives. Build pipelines with `map`/`flatMap`/`fold`. A function should read as a transformation of values, not a sequence of mutations.

## Theoretical foundation: the λ-calculus

These practices aren't arbitrary — they fall out of the **λ-calculus**, Church's model of computation and the formal basis of functional programming (see [[lambda-calculus]]). The connections worth knowing:

- **Referential transparency = confluent reduction.** "Same input → same output, replace a call with its result" is the Church–Rosser property: a term has at most one normal form, reached by reducing (β) in any order. Purity is what lets you treat code as λ-terms you can substitute freely.
- **Currying and partial application** come straight from λ-calculus, where every function is unary and multi-argument functions are nested abstractions (`λx.λy.E`). Scala's `=>` is an abstraction; a call is application.
- **Recursion is a fixed point.** Named/`letrec` recursion is sugar over the Y/fixed-point combinator; this is why structural/total recursion (and termination) deserve care.
- **Laziness vs strictness = normal order vs applicative order** — the same evaluation-order distinction, with the same trade (normal order terminates more often, applicative order is usually cheaper).
- **ADTs and "illegal states unrepresentable"** are the typed layer (simply-typed λ-calculus → Hindley–Milner): types rule out ill-formed terms and, in the simply-typed fragment, guarantee termination.

You don't need the theory to apply the discipline, but it explains *why* the discipline is sound. Reach for [[lambda-calculus]] when you want the underlying model.

## Anti-patterns

- `var`, mutable collections, imperative `while`/`for`-with-side-effects loops — replace with folds/recursion/comprehensions.
- `Either` (or `Option`) wrapping a function that can't actually fail — keep total functions total.
- Throwing exceptions for expected/validation failures — return error values.
- Validating the same data repeatedly instead of once at the boundary, then trusting the type.
- A shared supertype that merges genuinely distinct domains (DNA vs RNA) — keep them independent.
- Business logic leaking into the `IO` shell, or `IO`/side effects leaking into the core.
- Implicit inputs/outputs (globals, hidden mutation, side-effecting reads) where an explicit argument/return would make the function a calculation.
- An action doing work that could be extracted into a calculation and merely called from the action.
- Mutating data in place instead of copy-on-write; reaching for deep/defensive copies *inside* your trusted core where copy-on-write suffices.
- Functions that span multiple levels of abstraction at once, or growing an abstraction barrier instead of building on its minimal interface.
- Speculative generality — modeling cases or parameters no requirement (and no [[tdd]] test) demands.

## Related

- [[lambda-calculus]] — the formal model underneath: reduction, currying, fixed-point recursion, normal vs applicative order, and typed encodings.
- [[tdd]] — pure, total functions are the easiest things in the world to test.
- [[scala]] — the concrete language mechanics (sealed ADTs, `sealed abstract case class`, value classes, `Either`, copy-on-write via persistent collections, Cats Effect `IO`) used to express these principles.
- `scala-bio-framework` — project-specific application.
- *Grokking Simplicity* (Eric Normand) — source of the actions/calculations/data lens, copy-on-write & defensive copying disciplines, stratified design, and the onion architecture framing in this skill.
