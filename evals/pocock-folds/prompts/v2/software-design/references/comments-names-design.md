# Design it twice, comments, names, consistency, obviousness

*A Philosophy of Software Design* (Ousterhout), Chapters 11–18. This is where APoSD most diverges from [[clean-code]] (pro-comments).

## Design it twice (Ch. 11)

For any important decision — a class interface, a module boundary, a key data structure — **design it at least twice**: sketch two or three genuinely different approaches and compare them (interface simplicity, depth, generality, performance). Even for experts, the second design is usually noticeably better, and the comparison sharpens your understanding of the problem. Cheap relative to the cost of living with a bad interface.

## Why write comments — the four excuses (Ch. 12)

APoSD is firmly **pro-comment**; it rebuts the usual objections:
1. *"Good code is self-documenting."* — Largely a myth for non-trivial design. Code can show *what* it does but not *why*, the intent, the contract, the units, the invariants, or cross-module decisions. Abstractions exist precisely so callers needn't read the code — that requires comments.
2. *"I don't have time."* — The investment is small and pays back in reduced confusion; budget it as part of design.
3. *"Comments get out of date."* — Keep them **near the code** they describe and update them with the diff; staleness is a discipline problem, not a reason to omit.
4. *"All the comments I've seen are worthless."* — Because they restated the code. Well-written comments (capturing non-obvious info) are valuable.

The deeper benefit: **comments capture information that was in the designer's head but can't be represented in code** — without them that knowledge is lost.

## Comments should describe what isn't obvious from the code (Ch. 13)

- **Don't repeat the code** — a comment that restates the statement adds nothing. Add information the reader doesn't already have.
- **Lower-level comments add precision** (units, boundary conditions, null meaning, invariants); **higher-level comments add intuition** (what a block accomplishes and why). Most useful comments are at a *different level of detail* than the code.
- **Interface comments** describe the abstraction (what a caller needs: behavior, args, returns, side effects, exceptions) — kept separate from implementation comments.
- **Implementation comments** explain *what and why*, not *how* (the code shows how).
- Document **cross-module design decisions** in a central, discoverable place.
- Establish **conventions** (e.g. every method has an interface comment) so comments are consistent.

## Choosing names (Ch. 14)

Names are a form of abstraction and a frequent source of bugs. A good name **creates an image** in the reader's mind and is **precise** (says exactly what the variable is, not vaguely). Use names **consistently** (the same concept → the same word). Avoid vague/generic names (`data`, `tmp`, `count`) where a precise one fits. If you struggle to name something precisely, the underlying design may be muddled. (Notes a differing view — the Go style guide favors very short names in small scopes; reconcile by scope.)

## Write the comments first (Ch. 15)

Treat comments as a **design tool**, written **before** the code:
- Write the **interface comment** for a class/method before implementing it — if it's hard to write simply, the design is too complex; redesign now (comments as an early complexity detector).
- **Delayed comments are bad comments** — written after the fact they're rushed, incomplete, and skip the rationale you've already forgotten.
- Early comments make design issues visible early and are "fun" because they're part of thinking, not a chore; the cost is small and front-loaded.

## Modifying existing code (Ch. 16)

- **Stay strategic** — every change is a chance to improve the design (the Boy Scout instinct); don't just bolt on the smallest tactical patch that compounds complexity.
- **Maintain comments:** keep them **near the code** (not far away, where they rot), in the **code, not the commit log** (commits are hard to find later), avoid duplication (one authoritative place), and **review the diff** to catch comments you forgot to update. Higher-level comments survive change better than detailed ones.

## Consistency (Ch. 17)

Consistency lowers cognitive load and reduces unknown-unknowns: similar things done similarly let readers reuse understanding. Apply to names, coding style, interfaces, design patterns, invariants. **Ensure it** with documented conventions, automated enforcement (linters/formatters), and "when in Rome" (follow existing conventions, don't fight them). **Don't take it too far** — don't preserve a bad convention forever, but changing one requires changing *all* instances.

## Code should be obvious (Ch. 18)

Obscurity is half of complexity; obvious code can be read quickly with correct assumptions and little mental effort. **Make code more obvious:** good names, consistency, sensible whitespace, and **comments** for what can't be made obvious in code. **Things that obscure:** event-driven control flow, generic containers (`Pair`/tuples that hide meaning), inconsistency, code whose type/behavior differs from its declaration, and missing the information a reader needs. The test of obviousness is someone *else* reading it without difficulty.
