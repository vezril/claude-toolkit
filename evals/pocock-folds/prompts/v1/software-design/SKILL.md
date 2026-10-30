---
name: software-design
description: Module- and system-level software design, distilled from John Ousterhout's *A Philosophy of Software Design* — complexity is the enemy; fight it with deep modules (simple interfaces over powerful implementations), information hiding, pulling complexity downward, defining errors out of existence, strategic (not tactical) programming, designing it twice, and comments that capture what the code can't. Use whenever designing or reviewing the structure of a module/class/API/system, deciding how to split or combine components, reducing complexity/coupling/cognitive load, judging an abstraction or interface, choosing what to hide vs expose, or reasoning about whether a change makes the system simpler — i.e. design decisions above the line-by-line level. Sits at the design tier above the clean-code skill (which is line-level) and pairs with design-patterns and domain-driven-design. Language-agnostic with Scala/FP notes; flags where it diverges from Clean Code (comments, function size).
---

# Software Design (A Philosophy of Software Design)

Module- and system-level design, from John Ousterhout's *A Philosophy of Software Design* (APoSD). One thesis: **complexity is the enemy**, it accumulates incrementally, and the job of design is to keep it manageable so the system stays understandable as it grows. This is the **design tier above [[clean-code]]** (which is more line-level): APoSD is about interfaces, modules, abstractions, and how complexity flows through a system.

Language-agnostic principles with Scala/FP notes (the book's examples are Java/C++). Pairs with [[clean-code]], [[design-patterns]], [[domain-driven-design]], [[functional-programming]], [[tdd]]. Where it disagrees with Clean Code, this skill says so.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Otherwise this is a default design lens.

## Complexity is the enemy

**Complexity** = anything about the structure that makes a system hard to understand or modify. It shows up as three **symptoms**:
- **Change amplification** — a simple change requires edits in many places.
- **Cognitive load** — how much you must know to make a change.
- **Unknown unknowns** — it's not obvious *what* you must change or know (the worst, because you can't even see it).

Its two **causes** are **dependencies** (when code can't be understood/changed in isolation) and **obscurity** (when important information isn't obvious). Complexity is **incremental** — it accrues a little at a time, so the discipline is to resist each increment ("zero-tolerance"), not to wait for a big cleanup.

## Strategic, not tactical, programming

- **Tactical programming** optimizes for getting *this* feature working now; each shortcut adds a little complexity, and they compound into an unmaintainable mess.
- **Strategic programming** treats *working code as not enough* — the real goal is a clean design that stays easy to change. Invest a small, continuous amount (Ousterhout suggests ~10–20% of time) in design; it pays for itself quickly. The best designs come from many small investments, not heroics.

## Deep modules — the central idea

A **module** (class, file, service, subsystem) has an **interface** (what a caller must know) and an **implementation** (how it works). Think of each as providing **abstraction** — a simplified view that omits unimportant detail.

> **The best modules are *deep*: a simple interface over a powerful (large) implementation.** Depth = the ratio of functionality to interface complexity. A deep module hides a lot behind a little, so it removes more complexity than it adds.

- **Shallow modules** (lots of interface for little functionality) are a net loss — they add interface complexity without hiding much. **"Classitis"** — the belief that classes should be small, leading to many tiny shallow classes — *increases* system complexity (more interfaces, more boilerplate, more interconnections). (This is the book's sharpest disagreement with Clean Code's "small classes/functions" emphasis.)
- The best interface is **simpler than the implementation**; pass-through methods/variables that just forward are a red flag (a layer that adds interface but no abstraction).

## Always-apply design moves

1. **Make modules deep** — hide as much as possible behind a simple interface; the interface should describe *what*, not *how*.
2. **Information hiding** — each module encapsulates a design decision (a data structure, an algorithm) so it doesn't leak into its interface or other modules. Fight **information leakage** (the same knowledge appearing in multiple modules) and **temporal decomposition** (structuring code by execution order instead of by knowledge).
3. **Make classes somewhat general-purpose** — a slightly more general interface is usually simpler *and* deeper than a special-purpose one; design the API around what's fundamentally needed, not the first use case.
4. **Different layer → different abstraction.** Adjacent layers should offer different abstractions; if a method just forwards to another with the same signature (pass-through), or a variable is threaded through many layers unused (pass-through variable), collapse or redesign.
5. **Pull complexity downward** — it's better for the *module* to absorb complexity (e.g. sensible defaults, handling edge cases internally) than to push it up to many callers. A developer-author suffers complexity once so every caller is spared.
6. **Define errors out of existence** — the best exception handling is to design the API so the error *can't occur* (e.g. make an operation idempotent, or define semantics so the "error" is normal). Failing that, **mask** exceptions low down, **aggregate** handling, or even just crash for unrecoverable cases — anything to reduce the number of places that handle exceptions.
7. **Design it twice** — consider at least two genuinely different designs for any important interface/module before choosing; comparing alternatives produces far better results than taking the first idea.
8. **Better together or apart?** Bring pieces together if they share information, simplify the interface, or eliminate duplication; keep them apart to separate general-purpose from special-purpose code. Don't split methods just to make them short.

## The famous divergences from Clean Code (apply judgment)

[[clean-code]] (Martin) and APoSD (Ousterhout) agree on most goals but **clash on two points** — surface both when reviewing:
- **Comments.** APoSD is strongly **pro-comment**: comments capture design intent and information *not present in the code* (the *why*, cross-module decisions, interface contracts); "self-documenting code" is largely a myth for non-trivial design, and you should **write comments first** (Ch. 15) as a design tool. Clean Code treats most comments as a failure to express intent in code. Reconcile: don't comment *what the code already says*, but **do** comment what it can't — and don't treat comments as inherently bad.
- **Method/class size.** Clean Code pushes toward very small functions/classes; APoSD warns that over-decomposition (**classitis**, splitting that creates shallow modules and entanglement) *adds* complexity. Reconcile: extract to make a module **deeper** (hide complexity) or remove duplication — not to hit a line count.

APoSD is also mildly skeptical of some industry trends (Ch. 19): it values **information hiding over deep inheritance**, accepts unit testing but is **critical of strict TDD** (it can encourage tactical, design-last coding), and warns against **design-pattern overuse** and reflexive getters/setters. Treat these as "apply with judgment," cross-referencing [[tdd]] and [[design-patterns]].

## Scala / FP notes

Several APoSD principles are structural defaults in [[functional-programming]] / [[scala]]: **information hiding** ≈ encapsulation behind a small module/trait with a pure interface; **deep modules** ≈ a small total function/typeclass hiding a rich implementation; **define errors out of existence** ≈ make illegal states unrepresentable (smart constructors, ADTs) and use `Option`/`Either` so the error case is ordinary data, not an exception; **pull complexity downward** ≈ the pure-core/effectful-shell boundary absorbing messiness. "Different layer, different abstraction" maps onto ports & adapters.

## Anti-patterns / red flags (a selection; full list in `references/errors-trends-redflags.md`)

- **Shallow module** (interface complexity ≈ implementation) and **classitis** (many tiny classes).
- **Information leakage** / **temporal decomposition** (structure mirrors execution order, not knowledge).
- **Pass-through method / variable**; **overexposure** (callers must learn rarely-used features to use common ones).
- **Conjoined methods** (two pieces only understandable together, far apart); **repetition** (DRY violation).
- **Hard to describe** — if a comment/interface is hard to write simply, the underlying design is probably too complex.
- **Non-obvious code** — a reader can't quickly tell what it does or why.

## How to use this skill

- **`references/deep-modules.md`** — Ch. 4–9: deep vs shallow modules & classitis, information hiding & leakage, general-purpose modules, different-layer/different-abstraction (pass-through methods/variables, decorators), pull complexity downward, better-together-or-apart.
- **`references/comments-names-design.md`** — Ch. 11–18: design it twice, the comments chapters (the four excuses, describe what isn't obvious, write comments first), choosing names, modifying existing code, consistency, code should be obvious.
- **`references/errors-trends-redflags.md`** — Ch. 2 (complexity in depth), Ch. 10 (define errors out of existence), Ch. 19 (software trends & critiques), Ch. 20 (designing for performance), and the book's **Summary of Design Principles** and **Summary of Red Flags**.

## Related

- [[clean-code]] — the line-level companion; agrees on most goals, diverges on comments and method/class size (see above).
- [[design-patterns]] — patterns are tools for deepening modules; APoSD warns against applying them for their own sake.
- [[domain-driven-design]] — bounded contexts/aggregates are deep modules at the domain scale; information hiding ≈ a context boundary.
- [[functional-programming]], [[scala]] — purity, ADTs, and errors-as-values realize "define errors out of existence" and "pull complexity down."
- [[tdd]] — APoSD accepts unit tests but is critical of strict TDD; balance the two.
- Source: *A Philosophy of Software Design*, John Ousterhout (2nd ed.). Principles faithful; Scala/FP notes and the Clean Code reconciliation added for this repo.
