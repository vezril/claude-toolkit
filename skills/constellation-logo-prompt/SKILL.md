---
name: constellation-logo-prompt
description: Generate a ready-to-paste image-model prompt (Gemini / Imagen / any text-to-image) for a brand mark in the constellation's neon-glow house style — a single luminous accent, a text-free emblem in profile facing right, a transparent background, and 4 sample variations. Use when creating a logo/mark for a new divinity or service, or any mark that must match the existing pantheon marks. First step of the brand pipeline (prompt → generate → key to transparent → drop the mark).
user-invocable: true
argument-hint: "<name/subject> [domain or meaning] [accent color]"
license: MIT
---

# Constellation Logo Prompt

Turn a name + what it *means* into a prompt an image model can run to produce a brand mark that
matches the house style. **Output is a prompt, not an image** — the user pastes it into Gemini
(or another text-to-image model) themselves.

## Input

Parse `$ARGUMENTS` for:
- **Name / subject** — the mark's name (a divinity, a service, a concept).
- **Domain / meaning** — what it *does* or *stands for*. This drives the symbol. If missing and
  the name is a known figure (a Greek god, say), infer the attribute; otherwise ask.
- **Accent color** (optional) — a hex or a described hue. If absent, propose one (see below).

Also accept an optional **design-context override**: a path to a brand doc, an existing mark
image to match, or a pasted style description. If given, it *supplements or overrides* the
baked-in house style below — always prefer the project's own current convention when present
(e.g. the constellation's `docs/brand/README.md` + `docs/ux-standards.md`).

## The house style (the design context — binding unless overridden)

Every mark in this system obeys these. Bake them into the prompt:

1. **Text-free.** No letters, no wordmark, ever. The symbol alone carries it.
2. **Single luminous accent**, glowing as if lit from within, with a soft outer **bloom**. Neon
   line-art on a dark aesthetic. The accent is the service's UI `--primary` — the "echo".
3. **Emblem in profile FACING RIGHT.** Any figure, creature, or directional subject looks toward
   the right edge. (Non-negotiable consistency rule.)
4. **Transparent background** (PNG alpha) — no backdrop, no scene, no frame. Not baked onto a
   color.
5. **Square 1024×1024**, centered, symmetric, icon-like, ~6% margin.
6. **4 sample variations** per generation, distinct takes on the same concept.

## Choosing the SUBJECT

Derive a **single symbolic emblem** from the meaning — concrete, iconic, text-free:
- **A divinity** → its mythological attribute (Asclepius → the serpent-and-staff rod; Iris → a
  winged figure with a rainbow arc; Charon → a hooded ferryman poling a skiff). Prefer the
  attribute/object over a generic robed figure when one exists.
- **A service/concept** → a clean functional metaphor (a scheduler → an hourglass or time-wheel;
  a message bus → a winged courier; a vault → a sealed sigil).
Keep it to ONE subject. If it's a figure or has a direction, it **faces right**.

## Choosing the ACCENT

- If the user gave one, use it (quote the hex in the prompt).
- Otherwise **propose** one that fits the meaning and is **distinct from the existing marks** —
  if a project accent table is available (constellation: `docs/ux-standards.md`), consult it to
  avoid collisions; otherwise pick a luminous hue and give an approximate hex. State clearly it's
  a **suggestion** the user can override.
- Rules: it must glow on near-black (`#06060F`); if it looks weak, raise lightness, not chroma;
  never a mid-grey. Iridescent/multi-hue is allowed only when the meaning demands it (a rainbow,
  a spectrum) — otherwise one accent.

## The prompt to emit

Fill `{SUBJECT}` and `{ACCENT}` and produce exactly this shape:

> Create **4 sample variations** of a single emblem logo in a consistent house style: a
> minimalist, mystical **neon-glow emblem** of {SUBJECT}, shown **in profile facing to the
> right**. Luminous **{ACCENT}** linework glowing as if lit from within, with a soft outer bloom,
> on a **fully transparent background** (PNG alpha — no backdrop, no scene, no frame). Centered,
> symmetric, icon-like, **no text or letters of any kind**. Square 1024×1024. Clean vector-like
> glowing strokes, dark-fantasy pantheon-insignia feel. Give me 4 distinct takes on the same
> concept.

## Output format

Reply with, in order:
1. A one-line note: the **subject** you chose and why, and the **accent** (with hex) — flagging
   the accent as a suggestion if you picked it.
2. The finished prompt, in a single fenced code block, ready to paste.
3. One line of **pro tip + caveat**:
   - *Style match:* attach an existing mark (e.g. `docs/brand/ares.png`) to the model as a
     style-reference image — surest way to match the house glow.
   - *Transparency:* if the model ignores alpha and returns a solid background, re-ask for a
     "flat pure-black `#06060F` background" and key it out downstream instead.

Keep everything else brief. If asked for several marks at once, emit one titled block per subject.

## Where this sits

Step 1 of the brand pipeline. Downstream (separate skills / a workflow): generate in the image
model → key the result to a **transparent** PNG (checkerboard/opaque art → alpha) → drop the mark
at `docs/brand/<name>.png`. This skill only produces the prompt; it does not generate or process
images.
