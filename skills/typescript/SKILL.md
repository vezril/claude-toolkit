---
name: typescript
description: TypeScript — JavaScript with a static type system — distilled from Vanderkam's *Effective TypeScript* and the official TS docs (5.x). Covers the type system (primitives, arrays/tuples, objects, union & intersection, literal types, any/unknown/never/void), structural ("duck") typing, type aliases vs interfaces, generics & constraints, narrowing/type guards/discriminated unions/exhaustiveness, utility types (Partial/Pick/Omit/Record/ReturnType/…), functions typing, modules & declaration files (.d.ts, @types/DefinitelyTyped), and project config (`strict` + the strictNullChecks family, key tsconfig options), plus the *Effective TypeScript* practices (prefer types that model the domain, make illegal states unrepresentable, prefer unknown to any, use the compiler to find errors). Use when writing or reviewing TypeScript, designing types/interfaces/generics, narrowing unions, configuring tsconfig, typing a JS library, or deciding any-vs-unknown. Builds on javascript; the type layer for react, vue, nodejs, and nextjs; carries a Scala/FP comparison lens.
---

# TypeScript

**JavaScript with syntax for types** — a static type-checker that compiles to plain JS — from **Dan Vanderkam's *Effective TypeScript*** and the official docs (TS 5.x). It catches a whole class of [[javascript]] bugs at compile time and makes large codebases tractable. *"Your existing working JavaScript code is also TypeScript code."*

Cross-links: [[javascript]] (the language underneath — types erase at runtime), [[react]] / [[vue]] / [[nodejs]] / [[nextjs]] (where you use it), [[functional-programming]] / [[scala]] (the comparison lens — TS has real ADTs via unions), [[clean-code]] (types as documentation).

## Core idea: types over JavaScript, erased at runtime

TS adds a **static type layer**; the compiler checks it, then **erases** all types to emit JS. Types describe "the shapes and behaviors of values when the program runs" — they don't exist at runtime (no type-based dispatch; use `typeof`/`instanceof`/tagged unions for that). Annotations and `as`/`!` have **zero runtime effect**.

## The type system

- **Primitives:** `string`, `number` (one numeric type), `boolean`, `bigint`, `symbol`, `null`, `undefined`. (Lowercase; avoid `String`/`Number`.)
- **Arrays/tuples:** `number[]` / `Array<number>`; tuples `[string, number]`.
- **Objects:** structural shapes; optional props `name?: string`; `readonly`.
- **Union** `A | B` (one of) — operations must be valid for *every* member → you **narrow**. **Intersection** `A & B` (all of).
- **Literal types** `"left" | "right"`, `as const` for literal inference; `boolean` = `true | false`.
- **The special four:**
  - **`any`** — opt out of checking (avoid; it's contagious).
  - **`unknown`** — the safe `any`: you must narrow before use. *Prefer `unknown` to `any`.*
  - **`never`** — the empty type; assignable to everything, nothing assignable to it; used for exhaustiveness.
  - **`void`** — returns nothing meaningful.

## Structural ("duck") typing — the key mental shift

TS is **structurally typed**: a value is assignable if it has the required shape, regardless of declared class/name. *"If two objects have the same shape, they're the same type."* This differs from Scala/Java nominal typing — an object literal with the right fields satisfies an interface without `implements`. Excess-property checks apply only to fresh object literals.

## Type aliases vs interfaces

- `type X = …` names **any** type (object, union, primitive, tuple, mapped, conditional). `interface X {…}` names an object/class shape.
- **Interfaces** can be **re-opened** (declaration merging) and `extends`; **type aliases** can't merge but can express unions/intersections/mapped/conditional types. Docs heuristic: *"use `interface` until you need features of `type`."* For union ADTs and computed types, you need `type`.
- **Type assertions** `x as T` (or `<T>x`, not in `.tsx`) override the checker — use sparingly; double `as unknown as T` to force.

## Generics & constraints

Write code over many types: `function first<T>(a: T[]): T`. **Constraints** `<T extends {length: number}>`; defaults `<T = string>`; `keyof`/indexed access (`T[K]`) for key-safe generic code; `const` type params (`<const T>`) for literal inference. Don't over-genericize — add a type parameter only when it relates inputs to outputs.

## Narrowing, type guards, discriminated unions

- **Narrowing** = refining a union to a specific member. Guards: `typeof`, truthiness, `===`/`switch`, `in`, `instanceof`.
- **User-defined type guards:** `function isFish(x): x is Fish`. **Assertion functions:** `function assert(x): asserts x is T`.
- **Discriminated unions** — a shared literal **tag** (`kind: "circle" | "square"`) lets TS narrow each case; the idiomatic way to model variants (this is TS's **ADT** — like a Scala `sealed trait`). 
- **Exhaustiveness:** in the `default`/else, assign to `const _: never = x` — compiles only if every case is handled (the compiler tells you when you add a case). Pairs with [[functional-programming]] "make illegal states unrepresentable."

## Utility types

Built-in type transforms: `Partial<T>`, `Required<T>`, `Readonly<T>`, `Pick<T,K>`, `Omit<T,K>`, `Record<K,T>`, `Exclude<U,M>`, `Extract<T,U>`, `NonNullable<T>`, `ReturnType<T>`, `Parameters<T>`, `InstanceType<T>`, `Awaited<T>`, and string intrinsics `Uppercase`/`Lowercase`/`Capitalize`. Plus your own via **mapped** + **conditional** + **template-literal** types. Derive types from a single source of truth rather than duplicating.

## Functions, modules & declaration files

- Param/return annotations, optional/default/rest params, overloads, contextual typing of callbacks, `(a: string) => void` function types.
- **ES modules** with `import type`/`export type` (type-only); module augmentation; ambient `declare`.
- **Declaration files** (`.d.ts`) describe the types of JS with no implementation; ship them for libraries. **`@types/*`** (DefinitelyTyped) provide types for untyped packages, resolved from `node_modules/@types`.

## tsconfig & strictness

- **`strict: true`** — turn it on. It enables the family: **`strictNullChecks`** (the most valuable — null/undefined must be handled), `noImplicitAny`, `strictFunctionTypes`, `strictPropertyInitialization`, etc.
- Other common options: `target`, `module`, `moduleResolution: "bundler"` (or `node16`), `lib`, `jsx`, `esModuleInterop`, `skipLibCheck`, **`noUncheckedIndexedAccess`** (array access yields `T | undefined`), `declaration`.

## Effective TypeScript practices (Vanderkam)

- **Use the type system to model the domain** — make the types mirror reality so illegal states won't typecheck.
- **Prefer `unknown` to `any`**; confine any necessary `any` to the smallest scope.
- **Let inference do the work** — annotate function signatures and boundaries, not every local.
- **Prefer types that make illegal states unrepresentable** (discriminated unions over loose flags).
- **Use `interface`/`type` to name domain concepts**; derive types from values (`typeof`) and from a single source of truth.
- **Push types to the boundary** — validate untrusted input once (e.g. zod) into a well-typed core (mirrors [[functional-programming]] smart constructors).
- **Treat type errors as real errors**; keep `strict` on; minimize `as`/`!`.

## Scala / FP comparison lens

- **Discriminated unions ≈ Scala sealed-trait ADTs**; exhaustiveness checking ≈ exhaustive `match`. TS *does* let you "make illegal states unrepresentable."
- **Structural** (TS) vs **nominal** (Scala) typing; TS types are **erased** (no runtime reflection) and **unsound** in places (it trades soundness for JS-pragmatism — e.g. `any`, bivariant cases).
- No built-in `Option`/`Either` — model with `T | undefined`, discriminated unions, or a library; narrowing replaces pattern matching.

## Anti-patterns

- `any` everywhere (defeats the point — it spreads); `as`/`!` to silence the checker instead of narrowing/modeling.
- `strict` / `strictNullChecks` off; ignoring `noUncheckedIndexedAccess`.
- Loose flag combinations where a **discriminated union** would make illegal states impossible; no exhaustiveness check.
- Duplicating types instead of deriving (`Pick`/`Omit`/`ReturnType`/`typeof`); over-generic code.
- Treating TS as runtime validation — types are erased; validate untrusted input at the boundary.
- Fighting **structural** typing by expecting nominal behavior.

## Always-apply

1. **`strict: true`** (esp. `strictNullChecks`); minimize `any`/`as`/`!`; prefer **`unknown`** at boundaries.
2. Model the domain with types; **discriminated unions + exhaustiveness** to make illegal states unrepresentable.
3. Let **inference** work; annotate **boundaries/signatures**; derive types from one source (`Pick`/`Omit`/`typeof`).
4. **Narrow** with type guards; remember types are **structural** and **erased** at runtime.
5. Validate untrusted input once into a typed core; ship/consume `.d.ts`/`@types`.

## How to use the reference

- **`references/types-and-config.md`** — narrowing/guards/discriminated-union patterns, generics & mapped/conditional types, the utility-type catalog, and an annotated strict `tsconfig`.

## Related

- [[javascript]] — the runtime language TS compiles to.
- [[react]] / [[vue]] / [[nextjs]] / [[nodejs]] — where TS is used (all TS-first today).
- [[functional-programming]] / [[scala]] — ADTs, illegal-states-unrepresentable, the comparison lens.
- [[clean-code]] — types as documentation; [[secure-coding]] — validating untrusted input at the typed boundary.
- Sources: *Effective TypeScript* (Dan Vanderkam); the official TypeScript docs/handbook (typescriptlang.org, 5.x).
