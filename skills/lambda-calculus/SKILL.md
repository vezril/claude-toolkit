---
name: lambda-calculus
description: The λ-calculus — Alonzo Church's formalism for computation and the theoretical foundation of functional programming, distilled from Greg Michaelson's *An Introduction to Functional Programming Through Lambda Calculus*. Covers pure λ-calculus syntax (variables, abstraction λx.body, application), free vs bound variables and α-conversion / name-capture avoidance, β-reduction (substitution) and η-reduction, redexes and normal form, evaluation orders (normal order / lazy vs applicative order / eager) and the Church–Rosser theorems, currying and partial application, and how to *build* a programming language from this basis: Church encodings of pairs, booleans and conditionals, Church numerals and arithmetic (successor/predecessor/add/mult), recursion via the Y / fixed-point combinator (since λ has no names), an introduction to types (simply-typed λ-calculus), and encodings of lists and strings. Use whenever reasoning about λ-calculus, reduction/normal forms/evaluation order, currying, combinators (S, K, I, Y), Church encodings, the theory beneath functional languages, why recursion needs a fixed-point combinator, or the lazy-vs-eager distinction. Complements functional-programming and scala; pairs with information-theory.
---

# Lambda Calculus

The **λ-calculus** is Alonzo Church's tiny, complete model of computation: everything is a *function*, built from three syntactic forms, reduced by one rule. It is Turing-complete, evaluation-order-independent in its results, and the theoretical bedrock under every functional language. Distilled from Greg Michaelson's *An Introduction to Functional Programming Through Lambda Calculus*, whose method is to start from pure λ-calculus and *add layers* (booleans, numbers, recursion, types, lists) until you have a real functional notation.

Cross-links: [[functional-programming]] (this is the "why" beneath purity, currying, and referential transparency), [[scala]] (where the encodings become real ADTs and `=>` functions), [[information-theory]] (computation as a formal system).

## Syntax: the whole language in three forms

A λ-expression is one of:

- **Variable** — `x`, `y`, `f` … a name.
- **Abstraction** — `λx.E` ("lambda x dot E"): an anonymous function of parameter `x` with body `E`. (Often written `\x.E` or `fun x -> E`.)
- **Application** — `(E1 E2)`: apply function `E1` to argument `E2`.

That's it. Conventions: application is **left-associative** (`f a b` = `((f a) b)`); the body of a λ **extends as far right as possible** (`λx.x y` = `λx.(x y)`, not `(λx.x) y`). Every function takes **exactly one argument** — multi-argument functions are *curried* (below).

## Free and bound variables, α-conversion

In `λx.E`, the `x` is **bound** within `E`; a variable not bound by any enclosing λ is **free**. `λx.x y` binds `x` but `y` is free.

- **α-conversion** (renaming): a bound variable can be renamed consistently without changing meaning — `λx.x` ≡ `λz.z`. Bound names are arbitrary.
- This matters because of **name capture**: when substituting, a free variable in the argument must not accidentally fall under a λ that binds the same name. β-reduction must α-rename to avoid it. This is exactly the hygiene problem real languages handle with lexical scoping.

## β-reduction: the one computation rule

**β-reduction** applies a function by **substitution**: `(λx.E) A → E[x := A]` — replace every *free* occurrence of `x` in `E` with `A` (α-renaming as needed to avoid capture).

- A **redex** ("reducible expression") is any `(λx.E) A`. Reducing redexes is the entire mechanics of computation.
- A term with no redexes is in **normal form** — fully evaluated. Some terms have none (e.g. the looping `(λx.x x)(λx.x x)`, which β-reduces to itself forever).
- **η-reduction** (eta): `λx.(f x) → f` when `x` is not free in `f` — a function that just forwards its argument *is* that function (extensionality). The dual, η-expansion, goes the other way.

## Evaluation order & Church–Rosser

When a term has several redexes, which do you reduce first?

- **Normal order** — reduce the **leftmost-outermost** redex first (the argument is substituted *unreduced*). This is **call-by-name / lazy**-ish: it does the function first and only evaluates arguments as needed.
- **Applicative order** — reduce the **leftmost-innermost** redex first (evaluate arguments *before* substituting). This is **call-by-value / eager**, what most languages do.

The **Church–Rosser theorems** are the payoff:
1. **Confluence (CR-I)**: if a term can be reduced (by any order) to two different terms, both can be further reduced to a common term. ⇒ **normal form is unique** if it exists — the result doesn't depend on the order.
2. **CR-II / standardization**: if a normal form exists, **normal-order reduction will find it**. Applicative order may loop forever on a term that normal order would terminate (it can evaluate an argument that the function would have discarded). So normal order is "more terminating," eager is usually more efficient.

This independence-of-result is *why* functional code is safe to reason about and to evaluate lazily.

## Currying

Every function is unary, so a "two-argument" function is a function returning a function: `λx.λy.E`, applied as `((f a) b)`. **Partial application** (`f a`) yields a specialized one-argument function. Currying is not an add-on — it's the only way λ-calculus has multiple arguments, and it's where [[functional-programming]]'s currying/partial-application come from.

## Building a language: Church encodings

Pure λ has *only* functions — no booleans, numbers, or data. Michaelson's central move is to **encode** all of these as functions. See `references/church-encodings-and-recursion.md` for the full derivations; the headlines:

- **Pairs / tuples**: `pair = λx.λy.λf.f x y`; selectors `fst = λp.p (λx.λy.x)`, `snd = λp.p (λx.λy.y)`. A pair is a function that, given a selector, hands it both components.
- **Booleans & conditionals**: `true = λx.λy.x`, `false = λx.λy.y` (a boolean *is* a chooser); `if = λc.λt.λe.c t e` reduces to the taken branch. `and`, `or`, `not` follow.
- **Church numerals**: `n` = "apply `f` to `x`, `n` times": `0 = λf.λx.x`, `1 = λf.λx.f x`, `2 = λf.λx.f (f x)`, …. `succ`, `add`, `mult` (and the famously tricky `pred`) are all plain λ-terms.
- **Lists & strings**: built from pairs (or as right-folds), enabling the linear and nested list processing the book develops.

The lesson: data structures and control flow are *derivable*, not primitive. Real functional languages add them as syntax/types for ergonomics and efficiency, but the semantics bottom out here.

## Recursion needs a fixed-point combinator

λ-abstractions are **anonymous** — a function can't refer to itself by name, so naive recursion is impossible. The fix is a **fixed-point combinator**, classically **Y**:

```
Y = λf.(λx.f (x x)) (λx.f (x x))
```

`Y F` β-reduces to `F (Y F)`, i.e. `Y F` is a fixed point of `F`. You write the recursive body as a function of "itself" (`F = λself.λn. … self …`) and `Y F` ties the knot, unfolding one recursive call each time it's needed. (Under applicative order the looping variant **Z** is used to avoid eager non-termination.) This is the formal origin of `letrec`/named recursion and of why total/structural recursion matters.

## Types

Pure (untyped) λ-calculus lets you write self-application like `(x x)` and the non-terminating Ω — powerful but allows nonsense. **Typing** (the **simply-typed λ-calculus**) assigns each term a type (`α → β` for functions), ruling out ill-formed applications; well-typed terms in the simply-typed calculus are *strongly normalizing* (always terminate) — at the cost of no longer being Turing-complete without a recursion primitive. Michaelson introduces typed representations of booleans, numbers, and characters; this is the seed of the Hindley–Milner type systems in ML/Scala/Haskell ([[scala]]).

## Combinators (point-free building blocks)

Closed λ-terms with no free variables. The classics: **I** = `λx.x` (identity), **K** = `λx.λy.x` (const), **S** = `λf.λg.λx.f x (g x)` (apply-and-distribute). **{S, K}** alone is Turing-complete (SKI calculus) — even variables can be eliminated. Combinators underlie point-free style and combinator-based compilation.

## Relation to functional programming (the book's arc)

λ-calculus → add named definitions, booleans, numerals, conditionals → add recursion (Y) → add types → add lists/strings → you have a high-level functional language; Michaelson closes by mapping it onto LISP. So when you write Scala/Haskell, you're using sugar over exactly these constructs: a lambda is an abstraction, a call is application, evaluation is reduction (β), `val`/`def` are names over closed terms, ADTs are typed encodings, and laziness vs strictness is normal vs applicative order.

## How to use this skill

- **`references/reduction-and-evaluation.md`** — substitution and capture-avoidance in detail, α/β/η rules, redexes and normal forms, normal vs applicative order with worked reductions, the Church–Rosser theorems, and termination.
- **`references/church-encodings-and-recursion.md`** — full derivations of pairs, booleans/conditionals, Church numerals and arithmetic (incl. predecessor), the Y/Z combinator and recursive functions, and list/string encodings.

## Always-apply (when reasoning in λ-calculus)

1. Respect the conventions: application left-associates, λ-body extends maximally, all functions are unary (curry).
2. β-reduce by **capture-avoiding** substitution; α-rename when a bound name would capture a free one.
3. Distinguish **normal order** (lazy, finds the normal form if one exists) from **applicative order** (eager, may diverge where normal order wouldn't); results agree when both terminate (Church–Rosser).
4. Treat data/control as **encodings** (booleans, numerals, pairs, lists are functions); recursion is a **fixed point** (Y), not a name.
5. Typing buys termination/safety but costs raw expressiveness — know the trade.

## Related

- [[functional-programming]] — the discipline this theory underlies: currying, purity = referential transparency = confluent reduction, recursion, laziness.
- [[scala]] — where abstractions become `=>` functions, encodings become ADTs, and types become Hindley–Milner inference.
- [[information-theory]] — computation as a formal symbolic system.
- Source: *An Introduction to Functional Programming Through Lambda Calculus* (Greg Michaelson, Heriot-Watt).
