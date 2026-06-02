---
name: functional-programming
description: Functional programming discipline — pure functions, immutability, total functions, algebraic data types, making illegal states unrepresentable, and a pure core with effects pushed to the edge. Use when designing or reviewing code that should be functional, modeling a domain with ADTs and smart constructors, choosing how to represent errors (Either vs exceptions), deciding whether a function needs an Either wrapper, eliminating var/mutable state/imperative loops, or separating pure logic from IO/side effects. Default style in the scala-bioinformatics project (Scala + Cats Effect). Apply even when not named explicitly — any work introducing a domain type, algorithm, or effectful boundary should follow these principles.
---

# Functional Programming

Build programs out of **pure functions over immutable data**, model the domain so illegal states can't be represented, and keep effects at the edges. These principles are language-agnostic; the examples are Scala because that's this project's stack.

If the user's explicit instructions conflict with this skill, the user wins. Otherwise this is the default style.

## Purity

A pure function: same input → same output, every time, with no observable side effects (no mutation of shared state, no IO, no clock/random reads, no throwing for control flow).

- **No `var`, no mutable collections, no imperative loops.** Use `foldLeft`, `map`, `flatMap`, `collect`, recursion, or comprehensions instead. Review every function for these before declaring it done.
- **Accumulate with `foldLeft`** when building up a result; **`map`/`flatMap` + `mkString`/`toVector`** when producing a new collection. Example: counting bases is a `foldLeft` over the sequence into a result record using `.copy`; transcribing is a `flatMap` producing a new string.
- Purity makes code trivially testable (no setup/teardown, no mocks) and safe to reason about locally. This is *why* the [[tdd]] cycle is cheap here.

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

Structure the program as a **pure functional core** wrapped by a thin **effectful shell**.

- Domain types and algorithms are pure — no `IO`, no IO, no side effects. They're just data and total/fallible functions over it.
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

## Composition

Prefer composing small functions over one big procedure. Dispatch through the ADT (`fromChar` → pattern match → `toChar`) rather than reaching for raw primitives. Build pipelines with `map`/`flatMap`/`fold`. A function should read as a transformation of values, not a sequence of mutations.

## Anti-patterns

- `var`, mutable collections, imperative `while`/`for`-with-side-effects loops — replace with folds/recursion/comprehensions.
- `Either` (or `Option`) wrapping a function that can't actually fail — keep total functions total.
- Throwing exceptions for expected/validation failures — return error values.
- Validating the same data repeatedly instead of once at the boundary, then trusting the type.
- A shared supertype that merges genuinely distinct domains (DNA vs RNA) — keep them independent.
- Business logic leaking into the `IO` shell, or `IO`/side effects leaking into the core.
- Speculative generality — modeling cases or parameters no requirement (and no [[tdd]] test) demands.

## Related

- [[tdd]] — pure, total functions are the easiest things in the world to test.
- [[scala]] — the concrete language mechanics (sealed ADTs, `sealed abstract case class`, value classes, `Either`, Cats Effect `IO`) used to express these principles.
- `scala-bio-framework` — project-specific application.
