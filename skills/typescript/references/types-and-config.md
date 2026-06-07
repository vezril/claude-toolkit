# TypeScript — patterns, generics & config

Working detail (Effective TypeScript; TS handbook 5.x).

## Discriminated unions (TS's ADTs)
```ts
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "square": return s.side ** 2;
    default: { const _exhaustive: never = s; return _exhaustive; } // add a case -> compile error
  }
}
```
The shared literal `kind` is the discriminant; the `never` default gives exhaustiveness (the compiler flags any unhandled case). This is "make illegal states unrepresentable" — there's no `Shape` with both `radius` and `side`.

## Narrowing & guards
- `typeof x === "string"`, truthiness (`if (x)`), `===`/`switch`, `"prop" in x`, `x instanceof C`.
- **Type predicate:** `function isString(x: unknown): x is string { return typeof x === "string"; }`
- **Assertion fn:** `function assertDefined<T>(x: T): asserts x is NonNullable<T> { if (x == null) throw new Error(); }`
- Prefer narrowing over `as`. Validate `unknown` from JSON/APIs with guards (or zod) into typed values.

## Generics, mapped & conditional types
```ts
function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map(i => i[key]);
}
type Nullable<T> = { [K in keyof T]: T[K] | null };       // mapped
type Unwrap<T> = T extends Promise<infer U> ? U : T;       // conditional + infer
type Getters<T> = { [K in keyof T & string as `get${Capitalize<K>}`]: () => T[K] }; // key remap + template literal
```
- Constrain (`K extends keyof T`), default (`<T = string>`), `const` params for literal inference.
- Don't add a type parameter unless it links inputs to outputs.

## Utility-type catalog
| Type | Does |
|------|------|
| `Partial<T>` / `Required<T>` | all props optional / required |
| `Readonly<T>` | all props readonly |
| `Pick<T,K>` / `Omit<T,K>` | keep / drop keys |
| `Record<K,T>` | object type with keys K of value T |
| `Exclude<U,M>` / `Extract<T,U>` | remove / keep union members |
| `NonNullable<T>` | drop null/undefined |
| `ReturnType<F>` / `Parameters<F>` | a function's return / params |
| `InstanceType<C>` / `ConstructorParameters<C>` | class instance / ctor params |
| `Awaited<T>` | unwrap nested Promises |
| `Uppercase/Lowercase/Capitalize/Uncapitalize` | string literal transforms |
Derive from one source: `type User = {...}; type UserUpdate = Partial<Omit<User,"id">>;` and `type X = ReturnType<typeof makeX>`.

## Type vs interface — quick call
- Object shape that others might extend / a public API surface → **interface** (extensible, merges, good errors).
- Union, tuple, mapped, conditional, or "name this exact type" → **type**.
- Both are structural; pick by feature need, stay consistent.

## Annotated strict tsconfig
```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",   // or "node16"
    "lib": ["ES2022", "DOM"],
    "jsx": "react-jsx",               // for React
    "strict": true,                   // ON — enables the whole family
    "noUncheckedIndexedAccess": true, // arr[i] is T | undefined
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "skipLibCheck": true,             // faster builds; trust lib .d.ts
    "declaration": true,              // emit .d.ts if publishing a lib
    "outDir": "dist", "rootDir": "src",
    "verbatimModuleSyntax": true      // explicit import type
  }
}
```
`strict` is the single most important line; `strictNullChecks` (inside it) catches the most bugs. Add `noUncheckedIndexedAccess` for array/record safety.

## Boundary validation (Effective TS)
Types are erased — they don't validate runtime data. Parse untrusted input (HTTP/JSON/forms) once at the edge (e.g. **zod**: `const User = z.object({...}); type User = z.infer<typeof User>;`) into a fully-typed core. Mirrors [[functional-programming]] smart constructors / [[requirements-engineering]] "validate at the boundary."
