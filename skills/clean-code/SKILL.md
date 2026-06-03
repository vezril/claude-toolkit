---
name: clean-code
description: Principles for writing readable, maintainable code, distilled from Robert C. Martin's *Clean Code* (2008) — meaningful names; small single-purpose functions (one thing, one level of abstraction, few arguments, no side effects, command-query separation); comments as a last resort; consistent formatting; error handling with exceptions instead of codes and no null; clean boundaries around third-party code; small cohesive classes (SRP); separating construction from use (DI); and the catalog of code smells & heuristics. Use whenever writing, reviewing, refactoring, or cleaning up code for readability and maintainability — naming things, breaking up a long function or class, deciding whether a comment is needed, structuring error handling, reducing coupling, or spotting code smells — even if "Clean Code" isn't named. Language-agnostic principles with Scala/FP notes; defers testing depth to the tdd skill, OO patterns to design-patterns, and Java specifics to modern-java.
---

# Clean Code

How to write code that is **readable and cheap to change**, distilled from Robert C. Martin's *Clean Code* (2008). The premise: code is read far more than written (most cost is maintenance), so optimizing for the reader is the highest-leverage thing you can do. Clean code does one thing well, reads like prose, and reveals intent.

This skill states the principles **language-agnostically** with Scala/FP notes (the book's examples are Java). It complements rather than duplicates: defer testing discipline to [[tdd]], object/structural patterns to [[design-patterns]], and Java-version idioms to [[modern-java]]; the [[functional-programming]] skill shares many of the same instincts. Where Martin's 2008 advice is debated or can be over-applied, this skill says so — *principles over rules*.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Otherwise this is the default style.

## The mindset

- **Code is communication.** Write for the next person (often you in six months). Clarity beats cleverness.
- **The Boy Scout Rule:** leave the code a little cleaner than you found it. Continuous small improvements beat the mythical "grand redesign."
- **Distinguish what changes for what reason** (this is the thread tying names, functions, classes, and SRP together) — and isolate it.

## Highest-impact principles (apply by default)

1. **Intention-revealing names.** A name should say why it exists, what it does, how it's used; if it needs a comment to explain, rename it. Avoid disinformation, noise words, encodings (Hungarian/type prefixes), and single letters outside tiny scopes. Pick one word per concept and use it consistently.
2. **Small functions that do one thing** at a single level of abstraction. Extract until each function has one reason to change; prefer descriptive names over comments. Keep the argument count low (0–2 ideal); a `boolean`/flag argument usually means the function does two things — split it.
3. **No side effects / command-query separation.** A function either *does* something (command) or *answers* something (query), not both, and does only what its name says. Avoid output arguments (return a value, or model the result as data).
4. **Comments are a last resort, not a virtue.** Prefer expressing intent in code; a comment often marks a failure to do so. Keep the legitimate ones (legal, intent, warnings, `TODO`, public-API docs, amplification); delete commented-out code, redundant/misleading comments, and changelog comments (that's what version control is for).
5. **Errors as exceptions, not return codes; don't return or pass `null`.** Write the `try/catch/finally` first; throw exceptions defined in terms of the caller's needs; return empty collections / a Null Object / `Optional` instead of `null`. Keep error handling separate from happy-path logic.
6. **Small, cohesive classes with a single responsibility.** A class should have one reason to change; high cohesion (methods use most fields) signals it's focused. Many small classes beat a few god classes.
7. **Separate construction from use.** Wire dependencies at a startup/`main` boundary (factories, dependency injection) so business logic doesn't `new` its own collaborators — this is what makes code testable and changeable.
8. **Consistent formatting & the newspaper metaphor.** Read top-to-bottom from high-level to detail; keep related things vertically close, callers above callees; agree on team formatting and let a tool enforce it.

## Scala / FP notes

Clean Code is written in mutable, OO Java; many of its goals are *defaults* in [[functional-programming]] / [[scala]] and a few of its examples are dated:
- **"No side effects" and command-query separation** are purity by another name — pure functions over immutable data achieve them structurally (see [[functional-programming]]).
- **"Don't return null"** → `Option`/`Either`; **"errors as values"** is often cleaner than exceptions for *expected* failures (Scala/FP), while Martin's exceptions-over-codes still holds for truly exceptional conditions.
- **Objects vs data structures / the data-object anti-symmetry** maps onto sealed-ADT-plus-pattern-match (easy to add operations) vs polymorphic objects (easy to add types) — the expression problem from [[design-patterns]].
- **Small functions + one level of abstraction** = composing small total functions; **SRP/cohesion** = tightly-typed modules.
- The book's mutable-state concurrency chapter is superseded for this stack by message-passing/streams (see the [[akka]] skills).

## Balanced critique (apply judgment, not dogma)

The principles are sound; some rules are over-applied or debated — flag these:
- **Function size can be taken too far.** Extracting every few lines into a named method can *hurt* readability (ping-pong between tiny functions, lost locality, names that just restate code). Extract when it clarifies a concept or removes duplication, not to hit a line count. The "ideal of 2–4 lines" is aspirational, not a target.
- **Comments aren't failures by default.** *Why*-comments (rationale, trade-offs, non-obvious constraints, links to a ticket/spec) are valuable and can't be expressed in code; the book's stance is best read as "don't comment *what* the code already says," not "comments are bad."
- **Some examples are dated** (mutable beans, inheritance-heavy OO, Java-3/4-era idioms); take the principle, not the literal style — prefer immutability and composition ([[functional-programming]], [[modern-java]]).
- **SRP is widely misread.** "One reason to change" means one *axis of change / one actor*, not "one method/verb." Don't shatter a cohesive class into anemic fragments.
- **Don't dogmatically forbid `else`/`switch`.** Prefer polymorphism/ADTs where they genuinely reduce branching, but a clear `switch`/`match` on a closed set is often the *cleanest* option.

The throughline: optimize for the reader and for change; reach for a rule because it makes *this* code clearer, and stop when it doesn't.

## Anti-patterns / smells (flag in review)

A short list; the full catalog is in `references/smells-and-heuristics.md`:
- Unclear/misleading names; functions that do several things or mix abstraction levels; long argument lists and flag arguments; output arguments.
- Comments that compensate for bad code; commented-out code; redundant/obsolete comments.
- Returning/passing `null`; error codes; error handling tangled with logic; swallowed exceptions.
- God classes; low cohesion; feature envy; Law-of-Demeter "train wrecks" (`a.getB().getC().doThing()`); duplication (DRY); dead code; magic numbers; inconsistent conventions.

## How to use this skill

- **`references/names-functions-comments-formatting.md`** — Chapters 2–5 in depth (naming rules; functions: small/one-thing/stepdown/arguments/side-effects/CQS/DRY; good vs bad comments; vertical & horizontal formatting).
- **`references/errors-objects-classes-systems.md`** — Chapters 6–8, 10–13 (objects vs data structures & Law of Demeter; error handling; clean boundaries & learning tests; classes/SRP/cohesion; systems/DI; emergent design — Kent Beck's four rules of simple design; concurrency principles).
- **`references/smells-and-heuristics.md`** — the Chapter 17 catalog (Comments, Environment, Functions, General G1–G36, Names, Tests) as a reviewer's checklist.

## Related

- [[tdd]] — clean tests (F.I.R.S.T, one concept per test) and the discipline that keeps code clean; this skill defers testing depth there.
- [[design-patterns]] — the OO/structural patterns behind "separate construction from use," polymorphism-over-conditionals, and the expression problem.
- [[modern-java]] — Java-21 idioms (records, sealed types, `Optional`) that realize several Clean Code goals more directly than the 2008 examples.
- [[functional-programming]], [[scala]] — purity, immutability, and ADTs that achieve "no side effects," "don't return null," and small composable functions structurally.
- Source: *Clean Code: A Handbook of Agile Software Craftsmanship*, Robert C. Martin (Prentice Hall, 2008). Principles quoted faithfully; the Scala/FP notes and balanced critique are added for this repo.
