# Smells & heuristics — reviewer's checklist

*Clean Code* (Martin, 2008), Chapter 17 — the full catalog, as a code-review checklist. IDs are Martin's. Java-specific items defer to [[modern-java]]; test items defer to [[tdd]].

## Comments

- **C1 Inappropriate Information** — comments holding info better kept elsewhere (change history, authors, tickets) → use VCS / issue tracker.
- **C2 Obsolete Comment** — a comment that's drifted from the code; delete or update.
- **C3 Redundant Comment** — restates what the code already says.
- **C4 Poorly Written Comment** — if you write one, make it good: clear, brief, correct.
- **C5 Commented-Out Code** — delete it; VCS remembers.

## Environment

- **E1 Build Requires More Than One Step** — one command to check out and build.
- **E2 Tests Require More Than One Step** — one command to run all tests.

## Functions

- **F1 Too Many Arguments** — 0–2 ideal; 3+ needs justification; wrap related args in an object.
- **F2 Output Arguments** — counterintuitive; return a value / new state instead.
- **F3 Flag Arguments** — a boolean arg means the function does two things; split it.
- **F4 Dead Function** — delete uncalled methods.

## General

- **G1 Multiple Languages in One Source File** — minimize (e.g. HTML+JS+SQL+Java in one file).
- **G2 Obvious Behavior Is Unimplemented** — follow the Principle of Least Surprise; implement what the name implies.
- **G3 Incorrect Behavior at the Boundaries** — don't rely on intuition; test every boundary/edge case.
- **G4 Overridden Safeties** — don't turn off warnings/failing tests/compiler checks.
- **G5 Duplication** — the prime smell (DRY); extract; consider polymorphism/template-method for structural duplication.
- **G6 Code at Wrong Level of Abstraction** — keep high-level concepts and low-level details in separate places; don't leak details into a general interface.
- **G7 Base Classes Depending on Their Derivatives** — a base class shouldn't know about subclasses.
- **G8 Too Much Information** — keep interfaces small and tight; expose little (low coupling).
- **G9 Dead Code** — unreachable/never-true branches; remove.
- **G10 Vertical Separation** — declare variables/functions close to where they're used.
- **G11 Inconsistency** — do similar things the same way; honor conventions/the Principle of Least Surprise.
- **G12 Clutter** — remove empty constructors, unused vars, dead functions, pointless comments.
- **G13 Artificial Coupling** — don't couple things that don't depend on each other (e.g. dumping constants in an unrelated class).
- **G14 Feature Envy** — a method more interested in another class's data than its own; move it (or the data).
- **G15 Selector Arguments** — flag/selector args; prefer multiple functions.
- **G16 Obscured Intent** — code so terse/dense its purpose is hidden; be expressive.
- **G17 Misplaced Responsibility** — put code where a reader would expect it; name-driven placement.
- **G18 Inappropriate Static** — static methods that should be instance (polymorphic) methods.
- **G19 Use Explanatory Variables** — break expressions into well-named intermediate variables.
- **G20 Function Names Should Say What They Do** — if you must look at the body to know what a call does, rename.
- **G21 Understand the Algorithm** — actually understand it (don't fiddle until tests pass); refactor to make it obvious.
- **G22 Make Logical Dependencies Physical** — if A depends on B, make it explicit (ask B), don't assume shared knowledge.
- **G23 Prefer Polymorphism to If/Else or Switch/Case** — for repeated type-switches. *(But a single switch/ADT match over a closed set is fine — see [[design-patterns]].)*
- **G24 Follow Standard Conventions** — team conventions, consistently, tool-enforced.
- **G25 Replace Magic Numbers with Named Constants** — (and magic strings); names over literals.
- **G26 Be Precise** — don't be lazy about decisions (nulls, concurrency, rounding, locking); handle the case.
- **G27 Structure over Convention** — enforce design decisions with structure (types) over naming conventions where possible.
- **G28 Encapsulate Conditionals** — extract a predicate into a well-named function (`shouldBeDeleted(timer)`).
- **G29 Avoid Negative Conditionals** — positives are easier to read (`isReady` over `!isNotReady`).
- **G30 Functions Should Do One Thing** — split functions that do several.
- **G31 Hidden Temporal Couplings** — make required call order explicit (pass the result of step 1 into step 2).
- **G32 Don't Be Arbitrary** — structure should communicate; have a reason for where things live.
- **G33 Encapsulate Boundary Conditions** — put `+1`/`-1` edge logic in one place/variable.
- **G34 Functions Should Descend Only One Level of Abstraction** — statements one level below the function's name.
- **G35 Keep Configurable Data at High Levels** — config constants belong near the top, passed down.
- **G36 Avoid Transitive Navigation** — the Law of Demeter; don't write "train wrecks" (`a.getB().getC()`).

## Names

- **N1 Choose Descriptive Names** — names carry ~90% of readability; choose carefully and change freely.
- **N2 Choose Names at the Appropriate Level of Abstraction** — name by concept, not implementation.
- **N3 Use Standard Nomenclature Where Possible** — leverage known patterns/conventions in names.
- **N4 Unambiguous Names** — no names that could mean two things.
- **N5 Use Long Names for Long Scopes** — short names for tiny scopes, descriptive names for wide ones.
- **N6 Avoid Encodings** — no Hungarian/type/prefix encodings.
- **N7 Names Should Describe Side-Effects** — name what a function actually does (`createOrReturnOos`, not `getOos`).

## Java *(defer to [[modern-java]])*

- **J1 Avoid Long Import Lists by Using Wildcards.** **J2 Don't Inherit Constants** (import statically instead). **J3 Constants versus Enums** — prefer enums.

## Tests *(defer to [[tdd]])*

- **T1 Insufficient Tests** — test everything that could break. **T2 Use a Coverage Tool.** **T3 Don't Skip Trivial Tests.** **T4 An Ignored Test Is a Question about an Ambiguity.** **T5 Test Boundary Conditions.** **T6 Exhaustively Test Near Bugs** (bugs cluster). **T7 Patterns of Failure Are Revealing.** **T8 Test Coverage Patterns Can Be Revealing.** **T9 Tests Should Be Fast.**

---

Use this as a checklist when reviewing or refactoring — but apply judgment: each item is a *smell* (a prompt to look), not an automatic defect. Fix when it makes the code clearer for the reader and cheaper to change.
