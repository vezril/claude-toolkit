---
name: constellation-logo-key
description: Key raw logo art (a checkerboard- or solid-background JPEG/PNG from an image model) into a transparent PNG brand mark — difference-matte the background out, preserve the neon glow as a semi-transparent halo, crop and pad to a centered 1024×1024 with a straight alpha channel. Use after generating mark art (e.g. from constellation-logo-prompt) and before dropping the mark into a project. Bundles the keyer script; needs Pillow + numpy.
user-invocable: true
argument-hint: "<source-image...> [--out mark.png | --outdir DIR]"
license: MIT
---

# Constellation Logo Key (art → transparent mark)

Turn raw generated logo art into a finished brand mark on a **transparent** background. Image
models emit art on a backdrop — usually a two-tone **checkerboard** (a keying aid) or a **flat**
color. This mattes that background out and keeps a straight alpha channel, so the neon mark drops
onto any surface (dark theme, docs, light, print).

Step 2 of the brand pipeline: `constellation-logo-prompt` (prompt) → generate in the image model
→ **this skill** (key to transparent) → drop the mark at `<project>/docs/brand/<name>.png`.

## Input

Parse `$ARGUMENTS` for:
- **Source image(s)** — the raw art file(s) (`.jpeg`/`.png`). One or many.
- **Output** — `--out mark.png` for a single source, or `--outdir DIR` (each `src` → `<stem>.png`).
  Default when neither is given: write `<stem>.png` next to each source.

If the destination is a project's brand folder, put the final file at `docs/brand/<name>.png`
(the mark name = the divinity/service, lowercase).

## The bundled keyer

`key_transparent.py` sits in this skill's folder. Run it with Pillow + numpy present — zero-install
via uv:

```
uv run --with pillow --with numpy python3 <skill-dir>/key_transparent.py \
    SRC.jpeg --out docs/brand/NAME.png
```

Or, if Pillow/numpy are already installed, `python3 <skill-dir>/key_transparent.py ...`.

How it works (so you can reason about failures): estimate the background gray(s) from the four
corners → difference-matte every pixel against the nearer gray → steep alpha ramp (real neon
saturates to full opacity fast; checker/JPEG ghosts fall below threshold) → recover the foreground
color, flattening the checker's light/dark alternation inside partial-alpha glow → synthesize the
bloom as a **semi-transparent colored halo** (blurred premultiplied art over blurred alpha) →
crop to content + 6% margin, pad square, resize 1024². It degenerates gracefully on a **solid**
background (the two grays collapse to one; the matte still separates art from ground).

Flags: `--size` (default 1024), `--margin` (0.06), `--bloom` halo strength (0.55), `--preview`
(also emit a dark-bg contact sheet — see below), and `--flat #RRGGBB` for the **legacy** opaque
composite onto a color instead of alpha (only if a project still wants baked marks).

## Preview before committing (transparent marks are hard to eyeball)

A transparent PNG looks like nothing on a transparent viewer. Always generate a **preview on the
dark theme background** so the human can judge the glow/edges, and show it to them:

```
uv run --with pillow --with numpy python3 <skill-dir>/key_transparent.py \
    docs/brand/*.jpeg --outdir docs/brand --preview --preview-out /tmp/_preview_marks.png
```

Surface `/tmp/_preview_marks.png` to the user. Brand quality is **their** call — do not treat the
mark as final until they approve it. Delete the scratch preview afterward.

## Verify each output

After keying, confirm: mode `RGBA`, size `1024×1024`, alpha `min 0 / max 255` (real transparency,
not a fully-opaque frame), and a sane crop (the printed `crop WxH` should match the art's aspect —
a tall emblem like a staff *should* be narrow). If the matte comes back **empty** or full-frame,
the corners weren't background (art bled into them, or an unusual backdrop) — re-generate the art
with clean corners, or hand-crop before keying.

## Notes

- **Convention:** transparent supersedes the older `#06060F`-baked marks. Prefer transparent for
  new and regenerated marks; only use `--flat` if a specific project still requires opaque.
- **Text-free, single-accent, facing right** are set at *generation* time (the prompt skill), not
  here — this skill only removes the background and preserves what's there.
- Self-contained: the keyer is bundled, so this works in any repo without the source project.
