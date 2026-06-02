---
name: scala
description: Scala 2.13 idioms and gotchas learned in practice — sealed-trait ADTs, value classes, companion-object factories, the smart-constructor invariant pattern (sealed abstract case class), exhaustive pattern matching, Either/Option, foldLeft/map/flatMap over loops, Cats Effect 3 IO/IOApp, and ScalaTest AnyFunSpec. Use when writing or reviewing Scala code, defining a case class with an invariant, choosing between a value class and a plain class, fixing the Scala 2.13 private-constructor apply leak, structuring a Cats Effect program, or writing ScalaTest specs. Primary language of the scala-bioinformatics project (Scala 2.13.18). Apply even when not named explicitly for any .scala work in this codebase.
---

# Scala (2.13) Idioms

Practical Scala 2.13 patterns and the gotchas that actually bit this project. The stack is **Scala 2.13.18, Cats Effect 3.5.x, ScalaTest 3.2.x (AnyFunSpec), SBT 1.10.x**, JVM Java 26 (Corretto). Pinned to Scala 2.13 (not Scala 3) for now.

If the user's explicit instructions conflict with this skill, the user wins.

## Sealed-trait ADTs

A closed set of variants → `sealed trait` + `case object`/`final case class`. Sealing means the compiler can warn on non-exhaustive matches:

```scala
sealed trait DnaNucleotide
object DnaNucleotide {
  case object A extends DnaNucleotide
  case object C extends DnaNucleotide
  case object G extends DnaNucleotide
  case object T extends DnaNucleotide
}
```

- Put the variants **inside the companion object** so they're namespaced (`DnaNucleotide.A`).
- Use `case object` for no-data variants, `final case class` for variants carrying data (typical for error ADTs: `final case class InvalidCharacter(ch: Char) extends SequenceError`).
- Pattern-match exhaustively; let the compiler tell you when a new variant breaks a match. Treat non-exhaustive-match warnings as errors to fix, not noise.

## Companion objects as factories

The companion object holds smart constructors and the small surface a type needs — e.g. for an alphabet: `validChars: Set[Char]`, `fromChar: Char => Option[N]`, `toChar: N => Char`. Lift a raw `Char` into the ADT with `fromChar`, match on the ADT, lower back with `toChar` — never sprinkle raw char literals through algorithms.

## Value classes for zero-overhead wrappers

A single-field wrapper that's just a validated `String`/`Int` can extend `AnyVal` to avoid allocation:

```scala
final class DnaString private (val value: String) extends AnyVal
object DnaString {
  def from(s: String): Either[SequenceError, DnaString] = ...
  private[bio] def unsafeFrom(s: String): DnaString = new DnaString(s)
}
```

- `private` constructor + `from`/`unsafeFrom` factories are the only construction paths.
- `private[bio]` scopes `unsafeFrom` to the `bio` package — trusted internal use that skips re-validation.

## The 2.13 smart-constructor gotcha: `sealed abstract case class`

**This is the most important Scala-specific lesson in the project.** When a multi-field `case class` needs a smart-constructor invariant, do **NOT** write `final case class Foo private (...)`. Scala 2.13 synthesizes a **public `apply`** on the companion regardless of constructor visibility, so `Foo(...)` bypasses your validation — and `copy` leaks too. The fix:

```scala
sealed abstract case class Population(
    homozygousDominant: Int,
    heterozygous: Int,
    homozygousRecessive: Int
) {
  def total: Int = homozygousDominant + heterozygous + homozygousRecessive
}

object Population {
  def from(k: Int, m: Int, n: Int): Either[PopulationError, Population] =
    if (invalid) Left(...)
    else Right(new Population(k, m, n) {})   // anonymous subclass — only buildable here
}
```

Why it works: `sealed` confines subclassing to this file; `abstract` suppresses synthesis of `apply` **and** `copy`; the anonymous subclass `{}` is the sole construction path and exists only inside the file. `equals`/`hashCode`/`toString` are still synthesized, so it still behaves like a case class everywhere else.

Lock the guarantee in with tests (see [[tdd]]):

```scala
assertDoesNotCompile("""bio.domain.Population(2, 2, 2)""")
assertDoesNotCompile("""bio.domain.Population.from(2,2,2).toOption.get.copy(homozygousDominant = 99)""")
```

For a **value class** (single field, `extends AnyVal`) the `private` constructor is enough — the leak above bites multi-field `case class`es. Use `sealed abstract case class` specifically when you need a `case class` with an invariant.

## Either / Option, no exceptions for expected failures

- Fallible construction returns `Either[Error, T]`; "maybe absent" returns `Option[T]`.
- Transform without unwrapping: `.map`, `.flatMap`, `.left.map` (rewrite the error side), `.getOrElse`. In a test fixture where the value is known valid, `.getOrElse(sys.error("invalid fixture"))` is fine.
- `match` on `Either`/`Option` at the boundary where you finally act on the result.

## Prefer expressions and combinators over loops

No `var`, no mutable collections, no imperative loops in normal code. Idioms:

```scala
// accumulate into a result with foldLeft + copy
seq.foldLeft(Counts(0,0,0,0)) { (acc, ch) => ... acc.copy(a = acc.a + 1) }

// produce a new sequence with flatMap + mkString
dna.value.iterator.flatMap(c => fromChar(c).map(toRna).map(toChar)).mkString

// range fold for numeric series (per-step modulo to stay in Int)
(3 to (2 * n - 5) by 2).foldLeft(1)((acc, k) => (acc * k) % Modulus)
```

Mind numeric width: use per-step modulo and check the worst-case intermediate against `Int.MaxValue`; reach for `BigInt` when a count can exceed it.

## Cats Effect 3: `IOApp` shell

Effects live in `IO`, at the edge. The entry point is an `IOApp`; per-task runners build an `IO[Unit]` with a for-comprehension:

```scala
object Main extends IOApp {
  def run(args: List[String]): IO[ExitCode] =
    SomeProblem.solve().as(ExitCode.Success)
}

def solve(): IO[Unit] =
  for {
    raw   <- IO.blocking(new String(Files.readAllBytes(Paths.get(DataPath))))
    parsed = parsePure(raw)               // pure step: `=`, not `<-`
    _     <- IO.println(renderPure(parsed))
  } yield ()
```

- `IO.blocking { ... }` for blocking IO (file reads); `IO.println` for output — never bare `println`.
- In a for-comprehension, bind effects with `<-` and pure intermediates with `=`.
- Keep logic in pure functions; the `IO` block only sequences effects (see [[functional-programming]]).
- `build.sbt` carries `javaOptions += "-Dcats.effect.warnOnNonMainThreadDetected=false"` to silence a CE3 virtual-thread warning on the newer JVM — don't remove it.

## ScalaTest: AnyFunSpec

```scala
class FooSpec extends AnyFunSpec with Matchers {
  describe("Foo.bar") {
    it("does the thing for the canonical case") {
      Foo.bar(input) shouldBe expected
    }
  }
}
```

- `describe` = unit under test; `it` = one behavior as a sentence.
- Matchers: `shouldBe`, `should contain theSameElementsAs`, `should have size`, `should endWith`, `shouldBe a [Type]`.
- `assertDoesNotCompile("""...""")` to assert a compile-time guarantee holds (the apply/copy leak tests above).
- Run all: `sbt test`; one suite: `sbt "testOnly *FooSpec"`. `tail -15` the output to read pass/fail quickly.

## SBT notes

- Single root project, no submodules. Sources under `src/main/scala`, tests mirror under `src/test/scala`.
- If `sbt` isn't installed, `brew install sbt` (pulls openjdk + transitive deps; takes a few minutes). Ask before assuming a package manager.

## Anti-patterns

- `final case class Foo private (...)` for an invariant-bearing multi-field type — the `apply`/`copy` leak. Use `sealed abstract case class`.
- Raw `Char`/primitive literals in logic instead of going through the ADT (`fromChar`/`toChar`).
- `var`, mutable collections, `while` loops — use folds/recursion/comprehensions.
- Bare `println` / throwing exceptions for expected failures — use `IO.println` / `Either`.
- Non-exhaustive matches left unaddressed — fix the warning.
- Reaching for Scala 3 syntax — this project is pinned to 2.13.

## Related

- [[functional-programming]] — the principles these idioms serve (purity, total functions, illegal states unrepresentable).
- [[tdd]] — Red-Green-Refactor with AnyFunSpec, including `assertDoesNotCompile`.
- `scala-bio-framework` — how these idioms are applied to the bioinformatics domain specifically.
