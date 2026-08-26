---
name: constellation-logo-drop
description: Drop a finished transparent brand mark into a project's design system — verify it meets the house convention (square, RGBA, real transparency), place it at docs/brand/<name>.png, and for a committed service register its accent in docs/ux-standards.md. Final step of the brand pipeline, after constellation-logo-key. Bundles a verifier; needs Pillow + numpy.
user-invocable: true
argument-hint: "<mark.png> <name> [accent hex] [--project ROOT]"
license: MIT
---

# Constellation Logo Drop (install the mark)

Install a finished mark into a project's design system and register its identity. Step 3 (final)
of the brand pipeline: `constellation-logo-prompt` → generate → `constellation-logo-key` →
**this skill**.

## Input

Parse `$ARGUMENTS` for:
- **Mark file** — the keyed transparent PNG (from `constellation-logo-key`).
- **Name** — the divinity/service, lowercase (becomes `docs/brand/<name>.png`).
- **Accent** (optional) — the mark's accent as `#RRGGBB` and/or an `oklch(...)` value, for the
  design-system row.
- **`--project ROOT`** (optional) — project root; default the current repo. Brand dir =
  `<ROOT>/docs/brand`, design table = `<ROOT>/docs/ux-standards.md`.

## Step 1 — verify (gate)

Run the bundled verifier; **do not proceed if it fails.**

```
uv run --with pillow --with numpy python3 <skill-dir>/verify_mark.py <mark.png>
```

It asserts: square, 1024×1024, `RGBA` with **real** transparency (a keyed-out background, not an
opaque frame), and a sane fill fraction. A failure means the mark wasn't keyed (re-run
`constellation-logo-key`) or the matte lost/kept too much — fix upstream, don't drop a bad mark.

## Step 2 — place the mark

Copy the verified PNG to `<ROOT>/docs/brand/<name>.png`. Convention: the keyed **`<name>.png`** is
the mark used everywhere; the raw generated **`<name>.jpeg`** stays alongside as the source (keep
it if present). Overwriting an existing `<name>.png` is fine (a regenerated mark) — but if you're
replacing a mark that's already wired into a live console, say so, since it changes that app's
favicon/sidebar.

## Step 3 — register the accent (committed services only)

Only if this mark belongs to a **real, committed service** — check `docs/pantheon-roadmap.md`.
**Speculative / sketchpad marks do NOT go in the accent table** (that discipline keeps the design
system honest). For a committed service, add one row to the accent table in
`docs/ux-standards.md`, matching the existing format:

```
| <name> | <short descriptor> | oklch(<L> <C> <H>) | #RRGGBB | dark |
```

- Both `oklch(...)` and `#hex` are expected — **oklch is canonical** (the theme compiles it; the
  hex is an approximation for reference). If you were given only a hex, add the row with the hex
  and flag the `oklch` as needing a real value (a color tool / the UI session computes it) —
  **do not fabricate a precise oklch from a hex.**
- Pick `dark` vs `light` foreground per how the accent reads on `#06060F` (bright/pale accents →
  `light`; see the note in ux-standards about which accents take the light foreground).
- The mark's accent and the service's UI `--primary` must be the **same** value (the "echo").

## Step 4 — hand off

- The mark is now available; the **owning UI session** wires it as favicon + sidebar mark per
  `docs/ux-standards.md` §Logo (that's their job, not this skill's).
- If the project keeps a brand index or roadmap that lists marks (`docs/brand/README.md`,
  `docs/pantheon-roadmap.md`), update the relevant pointer/status in the same change.

## Notes

- Marks are **text-free, single-accent, facing right, transparent** — all ensured upstream (the
  prompt + key skills). This skill installs and registers; it does not alter the art.
- Self-contained: the verifier is bundled, so this works in any repo.
