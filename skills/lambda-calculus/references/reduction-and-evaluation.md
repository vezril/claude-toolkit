# Reduction & evaluation (Michaelson)

The mechanics of computing in λ-calculus: substitution, the reduction rules, normal forms, and evaluation order.

## Variables: free and bound

In `λx.E`, occurrences of `x` in `E` are **bound** by this λ. An occurrence not captured by any enclosing λ is **free**.

- `λx.(x y)` — `x` bound, `y` free.
- `(λx.x)(λy.x y)` — in the right term, the second `x` is free (no λ binds it there).
- Formally: `free(x) = {x}`; `free(λx.E) = free(E) \ {x}`; `free(E1 E2) = free(E1) ∪ free(E2)`.

A term with no free variables is **closed** (a *combinator*).

## α-conversion (renaming)

Bound names are arbitrary: `λx.x ≡ λy.y`. You may consistently rename a bound variable to any name **not already free** in the body. Used to keep names distinct before substitution.

## Substitution and name capture

β-reduction relies on substitution `E[x := A]` — "replace free `x` in `E` with `A`":

- `x[x:=A] = A`; `y[x:=A] = y` (y≠x).
- `(E1 E2)[x:=A] = (E1[x:=A]) (E2[x:=A])`.
- `(λx.E)[x:=A] = λx.E` (the inner `x` shadows — stop).
- `(λy.E)[x:=A]` where y≠x: if `y` is **not free in `A`**, = `λy.(E[x:=A])`. If `y` **is** free in `A`, you must first **α-rename** `y` to a fresh `z` to avoid **capture**, then substitute.

Capture example: reducing `(λx.λy.x) y` naively would give `λy.y` (wrong — the argument `y` got captured by the inner binder). α-rename the binder first: `(λx.λw.x) y → λw.y`. Correct.

## β-reduction

The computation rule: `(λx.E) A →β E[x := A]`.

- A `(λx.E) A` is a **redex**. Reduce redexes repeatedly.
- Worked example: `(λx.λy.x) p q → (λy.p) q → p` (this is `K` / `true`, selecting the first arg).
- `(λf.λx.f (f x)) g → λx.g (g x)` (numeral 2 applied to `g`).

## η-reduction

`λx.(E x) →η E` when `x` is **not free in `E`**. Captures *extensionality*: a wrapper that does nothing but pass its argument to `E` is observationally `E`. η-expansion is the reverse (used e.g. to delay evaluation).

## Normal form

A term with **no redexes** is in **normal form** — computation is done.

- Not all terms have one. `Ω = (λx.x x)(λx.x x) →β (λx.x x)(λx.x x) →β …` loops forever.
- Some terms reach a normal form only under the right order (below).

## Evaluation order

When multiple redexes exist, the strategy is which redex to reduce next:

- **Normal order** — leftmost-**outermost** first: reduce the outer application before its argument; the (unreduced) argument is substituted in and only evaluated where the body actually uses it. Corresponds to **call-by-name / lazy** evaluation.
- **Applicative order** — leftmost-**innermost** first: fully reduce the argument before substituting. Corresponds to **call-by-value / eager** evaluation.

Contrast on `(λx.λy.y) Ω`:
- *Normal order*: reduce the outer redex first → `λy.y` (discards `Ω` unevaluated) → **terminates**.
- *Applicative order*: try to reduce the argument `Ω` first → loops forever — **diverges**, even though a normal form exists.

So normal order is strictly more likely to terminate; applicative order is usually cheaper (evaluates each argument once, not once per use) — the lazy-vs-eager trade real languages make.

## Church–Rosser theorems

1. **Confluence (diamond property)**: if `E ↠ M` and `E ↠ N` by any sequences of reductions, then there exists `P` with `M ↠ P` and `N ↠ P`. Consequence: **a term has at most one normal form** — order cannot change the answer, only whether/how fast you reach it.
2. **Standardization / normalization**: if a term *has* a normal form, **normal-order reduction is guaranteed to reach it**. (Applicative order is not.)

Together these justify treating a λ-term as denoting a single value (referential transparency) and validate lazy evaluation as a complete strategy.

## Termination & undecidability

There is no general procedure to decide whether an arbitrary λ-term has a normal form (the halting problem, equivalently for λ-calculus). Typing (see the SKILL's *Types* section) recovers guaranteed termination for the simply-typed fragment, at the cost of Turing-completeness.
