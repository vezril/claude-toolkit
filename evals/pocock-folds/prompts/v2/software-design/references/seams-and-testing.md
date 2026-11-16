# Seams, dependencies and testing a deep module

How to deepen a cluster of shallow modules safely, and how to explore its interface. The design tier
above this is the main skill (deep modules, information hiding); this file is the working procedure
for one deepening. Adapted from Matt Pocock's `codebase-design` skill (mattpocock/skills, MIT; see
`THIRD_PARTY_NOTICES.md` at the repo root).

A **seam** (Michael Feathers) is a place where behaviour can be altered without editing in that
place: the location where a module's interface lives. An **adapter** is a concrete thing that
satisfies the interface at a seam (a role, not a size: a Postgres repository is a small adapter with
a large implementation; an in-memory fake is the reverse).

## Classify the dependencies first

The category of each dependency decides how the deepened module is tested across its seam.

1. **In-process**: pure computation, in-memory state, no I/O. Always deepenable: merge the modules and
   test through the new interface directly. No adapter, no port.
2. **Local-substitutable**: dependencies with a local stand-in (an embedded or containerised
   Postgres, an in-memory file system). Deepenable if the stand-in exists; the tests run against the
   stand-in. The seam is internal: no port in the module's external interface.
3. **Remote but owned** (ports & adapters): your own services across a network boundary. Define a
   **port** at the seam; the deep module owns the logic and the transport is injected as an adapter.
   Production gets the HTTP/gRPC/queue adapter, tests an in-memory adapter.
4. **True external**: third-party services you don't control (payments, email, SMS). The module takes
   the dependency as an injected port; tests supply a fake or mock adapter.

## Seam discipline

- **One adapter means a hypothetical seam; two adapters mean a real one.** Don't introduce a port
  unless at least two adapters are justified (typically production and test). A port with a single
  adapter is indirection, a shallow module of its own.
- **Internal seams stay internal.** A deep module may have private seams its own tests use; don't
  widen the interface to expose them.

## Testing: replace, don't layer

- Once tests exist at the deepened module's interface, the old unit tests on the shallow modules it
  swallowed are waste: delete them.
- The **interface is the test surface**: assert observable outcomes through it, never internal state.
- A test that has to change when the implementation changes (with no behaviour change) is testing
  past the interface.
- **The deletion test**: imagine deleting a module. If its complexity vanishes, it was a
  pass-through; if the complexity reappears across its callers, it was earning its keep.

## Design it twice, in parallel

The main skill says to consider at least two genuinely different designs. For an interface that
matters, do it with subagents so the alternatives don't anchor on each other:

1. **Frame the problem** for the user: the constraints any interface must satisfy, the dependencies
   and their categories (above), and a rough code sketch that makes the constraints concrete (not a
   proposal). Show it, then go straight to step 2 while the user reads.
2. **Spawn 3 or more subagents in parallel**, each with the same technical brief (file paths,
   coupling, dependency categories, what sits behind the seam) and a different constraint:
   - minimise the interface: 1–3 entry points, maximum leverage each;
   - maximise flexibility: many use cases and extension points;
   - optimise for the most common caller: make the default case trivial;
   - (when it applies) design around ports & adapters for the cross-seam dependencies.
   Each returns: the interface (types, operations, invariants, ordering, error modes), a usage
   example, what the implementation hides, the dependency strategy and adapters, and its trade-offs.
3. **Present and compare**: show the designs one after another, then compare them on **depth**
   (leverage at the interface), **locality** (where change concentrates) and **seam placement**.
   End with your own recommendation, and a hybrid if parts of two combine well. Be opinionated: the
   user wants a strong read, not a menu.
