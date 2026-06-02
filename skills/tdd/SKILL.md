---
name: tdd
description: Test-Driven Development discipline — strict Red-Green-Refactor with a confirmed failing test before any implementation. Use whenever adding or changing behavior in code (a new function, algorithm, domain type, bug fix, or edge case), when the user asks to "write tests", "do TDD", or work "test-first", and as the default workflow in the scala-bioinformatics project where TDD is non-negotiable. Covers how to confirm a real Red, writing the smallest Green, refactoring only after Green, structuring tests with describe/it (ScalaTest AnyFunSpec), pinning compile-time invariants with assertDoesNotCompile, and sequencing tasks.md in strict test→implementation→refactor order. Apply even when not named explicitly.
---

# Test-Driven Development

The unit of work is the **Red-Green-Refactor cycle**, not the finished feature. Every new behavior starts with a failing test. This is a hard requirement in the scala-bioinformatics project and a strong default everywhere else.

If the user's explicit instructions conflict with this skill, the user wins. Otherwise treat the cycle below as the playbook.

## The cycle

For **each individual behavior** (not each feature — each observable behavior):

1. **Red — write the failing test first.**
   - Write one test that names the behavior you're about to add.
   - Run the test suite and *confirm it fails*. Do not skip this — an unconfirmed Red is not Red.
   - The failure mode matters. Acceptable Red: an assertion failure, or a compile error like `not found: value X` / `not a member of`. **Not** acceptable: a green run (the test is vacuous or already covered), or a failure unrelated to what you're testing (a typo, a missing import elsewhere). If the failure is for the wrong reason, fix the test until it fails for the *right* reason.

2. **Green — smallest implementation that passes.**
   - Write the least code that makes the failing test pass. No speculative generality, no extra parameters "for later", no handling cases no test demands.
   - Run the suite. Confirm the new test passes *and* nothing else broke.

3. **Refactor — only once Green.**
   - Now improve names, remove duplication, tighten types — with the safety net of passing tests.
   - Re-run the suite after refactoring to confirm still Green.
   - Refactoring without a green bar is just editing. Don't refactor in Red.

Then repeat for the next behavior. Small cycles beat big ones — if a test requires a lot of code to go green, the step was too large; split it.

## Running the suite efficiently

- Run after **every** step (Red, Green, Refactor). The cycle's value comes from the fast feedback.
- You don't need the full output each time — `sbt test` piped to `tail -15` (or `tail -8`) is usually enough to read pass/fail and the count. Read the full output when something fails unexpectedly.
- To run a single suite while iterating: `sbt "testOnly *YourSpec"`. Run the whole suite before declaring done.

## Structuring the tests

The project uses ScalaTest `AnyFunSpec` with `describe` / `it` nesting (it mirrors Given/When/Then):

```scala
class EnumerateUnrootedBinaryTreesSpec extends AnyFunSpec with Matchers {
  describe("EnumerateUnrootedBinaryTrees.enumerate") {
    it("produces the single tree for three taxa") {
      trees("dog", "cat", "mouse") shouldBe Vector("((cat,mouse))dog;")
    }
  }
}
```

- **`describe`** names the unit under test (object/method). **`it`** states one behavior as a sentence — "produces X for Y", "fails when Z".
- One assertion-focused behavior per `it`. If a test name needs "and", it's probably two tests.
- Pull shared fixture construction into a small private helper (e.g. a `trees(...)` builder) so each `it` reads as input → expected output.
- **Cover the canonical sample first** (e.g. the Rosalind worked example), then the edges: empty input, minimum/maximum size, duplicates, boundary values, the first-failure-wins ordering of a validator.

## Test the contract, including what must *not* compile

When a type's invariant is enforced at compile time (e.g. a smart-constructor-only ADT that must not leak a public `apply`/`copy`), pin that with `assertDoesNotCompile` so a regression fails the suite:

```scala
it("cannot be constructed via a public companion apply") {
  assertDoesNotCompile("""bio.domain.Population(2, 2, 2)""")
}
it("does not expose a public copy method") {
  assertDoesNotCompile(
    """bio.domain.Population.from(2, 2, 2).toOption.get.copy(homozygousDominant = 99)"""
  )
}
```

Treat a compile-time guarantee as behavior worth a test, just like a runtime result.

## Error and validation paths are behaviors too

A smart constructor that returns `Either[Error, T]` has as many behaviors as it has failure cases, plus the success case. Write a Red test for each: each distinct error case, and the "first failure wins" ordering when several inputs are invalid at once.

## Sequencing work: tasks.md in strict TDD order

When planning a change (e.g. via the OpenSpec workflow), the task list must sequence **test → Red confirmation → implementation → Green confirmation → refactor** for each behavior, grouped by type first (domain ADT, then error, then algorithm). Don't write a task that says "implement and test X" as one step — that collapses the cycle. The archived changes under `openspec/changes/archive/` are the canonical templates.

## Anti-patterns

- **Skipping the Red step** — writing test and implementation together. You lose the proof the test can fail, which is most of its value.
- **Unconfirmed Red** — assuming a test fails without running it.
- **Red for the wrong reason** — a failure from an unrelated typo isn't a real Red.
- **Refactoring on a red bar** — only refactor with all tests green.
- **Over-shooting Green** — implementing untested generality. If no test demands it, don't write it.
- **One mega-test** — a single `it` asserting five things. Split so each failure points at one behavior.
- **Testing implementation details** — assert observable outputs/contracts, not private internals.

## Related

- [[functional-programming]] — pure, total functions are trivially testable: same input → same output, no setup/teardown.
- [[scala]] — the language idioms (`AnyFunSpec`, `assertDoesNotCompile`, smart constructors) these tests exercise.
- `scala-bio-framework` — project-specific application of this cycle.
