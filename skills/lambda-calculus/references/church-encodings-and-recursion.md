# Church encodings & recursion (Michaelson)

How Michaelson builds a real functional notation out of nothing but functions. Each "data type" and "control structure" is a λ-term. (Notation: `λx.E`; application left-associative.)

## Pairs and tuples

A pair holds two values and hands them to any selector you give it:

```
pair = λx.λy.λf.f x y      -- build: (pair a b) waits for a selector
fst  = λp.p (λx.λy.x)      -- give it a selector that keeps the first
snd  = λp.p (λx.λy.y)      -- ... or the second
```

`fst (pair a b) = (pair a b)(λx.λy.x) = (λx.λy.x) a b = a`. Tuples and records are nested pairs; this is also the workhorse for building lists and for the tricky predecessor.

## Booleans and conditionals

A boolean *is* a two-way chooser (note: `true`/`fst`-selector are the same shape):

```
true  = λx.λy.x
false = λx.λy.y
if    = λc.λt.λe.c t e      -- c picks t or e
not   = λb.b false true
and   = λa.λb.a b false     -- a ? b : false
or    = λa.λb.a true b      -- a ? true : b
```

`if true t e ↠ t`, `if false t e ↠ e`. Because the chooser selects *before* its branches are forced, conditionals work cleanly under normal order.

## Church numerals

A numeral `n` encodes "do something `n` times" — apply `f` to `x`, `n` times:

```
0 = λf.λx.x
1 = λf.λx.f x
2 = λf.λx.f (f x)
3 = λf.λx.f (f (f x))
```

Arithmetic:

```
succ = λn.λf.λx.f (n f x)          -- one more application
add  = λm.λn.λf.λx.m f (n f x)     -- compose m and n applications
mult = λm.λn.λf.m (n f)            -- n-fold, m times
exp  = λm.λn.n m                   -- (with suitable arg order)
isZero = λn.n (λx.false) true      -- "any application of false" else true
```

**Predecessor** is famously hard (you can't "un-apply"): the standard trick walks a pair `(n, n+1)`-style with `succ`, returning the lagging component — Michaelson derives it via pairs. From `pred` you get subtraction, comparisons, etc.

## Recursion via the fixed-point (Y) combinator

λ-abstractions are anonymous, so a function can't name itself. Express the recursive function as a transformation `F` that receives "itself" as a parameter, then take its **fixed point**:

```
Y = λf.(λx.f (x x)) (λx.f (x x))
Y F ↠ F (Y F)        -- defining property: Y F is a fixed point of F
```

Example — factorial:

```
F = λself.λn. if (isZero n) 1 (mult n (self (pred n)))
fact = Y F
fact 3 ↠ F fact 3 ↠ if (isZero 3) 1 (mult 3 (fact (pred 3))) ↠ ... ↠ 6
```

Each unfolding of `Y F` exposes one more `F`, supplying the next recursive call exactly when the body needs it. Under **applicative order**, `Y` diverges (it tries to build the infinite unfolding eagerly), so the **strict fixed-point combinator Z** is used:

```
Z = λf.(λx.f (λv.x x v)) (λx.f (λv.x x v))
```

The extra `λv.` η-delays the self-application until an argument arrives. This is the formal seed of `letrec` and named recursion in real languages.

## Lists and strings

Two common encodings:

- **Pair-based (cons cells)**: a non-empty list is `pair head tail`; the empty list and an `isEmpty` test are encoded with booleans (e.g. tag each node, or use a dedicated `nil`). `head = fst`, `tail = snd`. Linear list processing (length, append, map, filter, fold) is then ordinary recursion via `Y`.
- **Right-fold (Church) encoding**: a list *is* its own fold — `cons = λh.λt.λc.λn.c h (t c n)`, `nil = λc.λn.n`. Applying the list to `c` (combine) and `n` (base) folds it.

Strings are lists of character codes (themselves numerals/typed characters). With lists in hand, Michaelson develops linear list processing (chapter 6) and nested/composite structures like trees (chapter 7) — the same recursion-over-encoded-data pattern throughout.

## The takeaway

Booleans, numbers, pairs, lists, conditionals, and recursion are **not primitives** — they're λ-terms. A functional language is layers of convenient syntax and types over exactly these encodings; reduction (β) is its evaluation, and the fixed-point combinator is the meaning of recursion. (Michaelson finishes by realizing the whole stack in LISP.)
