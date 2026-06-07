---
name: html-css
description: Semantic HTML5 and modern CSS — structuring and styling web pages — distilled from *HTML5 in Action*, *HTML & CSS QuickStart Guide*, *CSS3 Foundations*, the CSS Fonts/Text specs, and the responsive-design books (*Responsive Web Design with HTML5 & CSS3*, *Beginning Responsive Web Design*). Covers semantic HTML5 (document structure, sectioning elements, forms & input types, media, accessibility/ARIA), the CSS model (selectors & specificity, the cascade & inheritance, the box model, units rem/em/%/vw, custom properties), modern layout (Flexbox and Grid — the right tool for each), responsive design (mobile-first, media queries, fluid type/images, container queries), typography (web fonts, @font-face, the CSS Fonts/Text properties), transitions/animations/transforms, and accessibility & performance basics. Use when writing or reviewing HTML/CSS, structuring a page semantically, building responsive layouts with Flexbox/Grid, debugging the cascade/specificity/box-model, styling typography, or improving accessibility. The presentation layer beneath react, vue, and nextjs; pairs with ux-design and javascript.
---

# HTML & CSS

The web's **structure and presentation** layer — semantic **HTML5** + modern **CSS** — from *HTML5 in Action*, *HTML & CSS QuickStart*, *CSS3 Foundations*, the CSS Fonts/Text specs, and the responsive-design books. Even when you build with [[react]]/[[vue]], you're producing HTML and styling it with CSS — get the fundamentals right and frameworks become easy.

Cross-links: [[javascript]] (scripts the DOM this defines), [[react]] / [[vue]] / [[nextjs]] (render this), [[ux-design]] (the design principles behind the markup), [[secure-coding]] (escaping, CSP).

## Semantic HTML5

Write markup that describes **meaning**, not appearance:
- **Document structure:** `<!DOCTYPE html>`, `<html lang>`, `<head>` (meta charset, viewport, title), `<body>`. The viewport meta tag is mandatory for responsive: `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- **Sectioning/semantic elements:** `<header>`, `<nav>`, `<main>` (one per page), `<article>`, `<section>`, `<aside>`, `<footer>`, `<figure>/<figcaption>` — over `<div>` soup. Headings `<h1>…<h6>` form the outline (don't skip levels).
- **Forms:** `<form>`, `<label>` (always associate with inputs), HTML5 input types (`email`, `number`, `date`, `range`, `tel`, `url`, `search`, `color`), `required`/`pattern`/`min`/`max` validation, `<fieldset>/<legend>`, `<select>`, `<textarea>`, `<button type>`.
- **Media:** `<img>` (always `alt`), `<picture>`/`srcset` for responsive images, `<video>`/`<audio>`, `<canvas>`/`<svg>`.
- **Accessibility:** semantic elements give you a11y for free; add **ARIA** only when semantics don't suffice (`role`, `aria-label`, `aria-*`); keyboard navigability; sufficient contrast. ([[ux-design]] for the principles.)

## The CSS model

- **Selectors & specificity:** type/class/id/attribute/pseudo-class(`:hover`,`:focus`,`:nth-child`)/pseudo-element(`::before`). **Specificity** = (ids, classes, types); more specific wins; `!important` overrides (avoid it). Keep specificity low and flat — prefer classes.
- **The cascade & inheritance:** the value applied is decided by origin, specificity, and source order; some properties (color, font) **inherit**, most don't. Understanding cascade + specificity is what makes CSS predictable.
- **The box model:** content → padding → border → margin. **Always set `box-sizing: border-box`** (width includes padding+border — far saner). Margin collapsing between block elements is a classic gotcha.
- **Units:** `rem` (root-relative — use for type/spacing, respects user font size), `em` (relative to element), `%`, `vw`/`vh`, `fr` (grid), `ch`. Prefer relative units for responsive/accessible sizing over `px`.
- **Custom properties (CSS variables):** `--brand: #06c; color: var(--brand);` — themeable, cascade-aware, runtime-changeable (theming, dark mode).

## Modern layout — Flexbox & Grid (the core skill)

Two complementary systems; pick by the job:
- **Flexbox** — **one-dimensional** (a row *or* a column): nav bars, toolbars, distributing items along an axis, centering. `display:flex`, `justify-content` (main axis), `align-items` (cross axis), `gap`, `flex: 1`, `flex-wrap`.
- **Grid** — **two-dimensional** (rows *and* columns): page layouts, card grids, anything with both axes. `display:grid`, `grid-template-columns: repeat(auto-fit, minmax(200px,1fr))`, `gap`, named areas (`grid-template-areas`), `fr` units.
- Rule of thumb: **Grid for the overall layout, Flexbox for components within it.** Both replace the old float/positioning hacks. `position` (relative/absolute/sticky/fixed) for overlays/sticky headers; floats are legacy.

## Responsive design

Build for **mobile-first**, then enhance:
- **Fluid layouts** (%, fr, flex/grid) + **media queries** (`@media (min-width: 768px) {…}`) — start with the small-screen styles, add `min-width` breakpoints upward.
- **Responsive images:** `srcset`/`sizes`, `<picture>`, `max-width:100%`. **Fluid type:** `clamp(1rem, 2.5vw, 1.5rem)`.
- **Container queries** (`@container`) — style a component by *its container's* size, not the viewport (the modern upgrade over media queries for reusable components).
- Test across breakpoints; respect `prefers-reduced-motion` and `prefers-color-scheme`.

## Typography (CSS Fonts & Text)

- **Web fonts:** `@font-face` (self-host for privacy/perf) or a service; `font-display: swap` to avoid invisible text; variable fonts for many weights in one file.
- **Font properties:** `font-family` (with fallback stack), `font-size`, `font-weight`, `font-style`, `line-height` (unitless), `font-feature-settings`.
- **Text properties:** `text-align`, `letter-spacing`, `word-spacing`, `text-transform`, `text-decoration`, `white-space`, `overflow-wrap`/`hyphens`, `text-overflow: ellipsis`. Set a readable measure (~45–75ch line length) and rhythm.

## Transitions, animations, transforms

- **`transition`** for state changes (hover/focus) — cheap polish; animate `transform`/`opacity` (GPU-friendly), not layout properties (avoid jank).
- **`@keyframes` + `animation`** for multi-step motion; **`transform`** (translate/scale/rotate) for movement without reflow. Respect `prefers-reduced-motion`.

## Accessibility & performance basics

- A11y: semantic HTML first, labels, alt text, focus states, keyboard support, color contrast (WCAG), `aria-*` only as needed.
- Perf: minimize/critical CSS, avoid huge selectors, lazy-load images (`loading="lazy"`), `font-display: swap`, and let the framework ([[nextjs]] Image/Font) optimize.
- Methodologies for scaling CSS: utility-first (Tailwind), BEM naming, CSS Modules, or scoped styles ([[vue]] SFC `<style scoped>`); pick one and be consistent.

## Anti-patterns

- `<div>` soup instead of semantic elements; skipping heading levels; missing `alt`/`<label>`/viewport meta.
- Float/absolute-positioning hacks where **Flexbox/Grid** belong; not setting `box-sizing: border-box`.
- Specificity wars and `!important` everywhere; over-qualified selectors; inline styles for everything.
- `px` for type/spacing (ignores user prefs); desktop-first with `max-width` everywhere instead of mobile-first.
- Animating layout properties (jank) instead of `transform`/`opacity`; ignoring `prefers-reduced-motion`.
- Forgetting accessibility/contrast; building HTML by string concat from untrusted data (XSS — [[secure-coding]]).

## Always-apply

1. **Semantic HTML5 first** (a11y for free); `lang`, viewport meta, labels, `alt`.
2. **`box-sizing: border-box`**; keep specificity low (classes); use **custom properties** for theming.
3. **Grid for layout, Flexbox for components**; relative units (`rem`/`fr`/`clamp`).
4. **Mobile-first** responsive (min-width queries, fluid type/images, container queries for components).
5. Animate `transform`/`opacity`; mind **accessibility, contrast, and `prefers-*`**.

## How to use the reference

- **`references/layout-and-responsive.md`** — Flexbox & Grid recipes, the specificity/cascade rules, responsive patterns (breakpoints, fluid type, container queries), and a typography/web-font setup.

## Related

- [[javascript]] — scripts the DOM; [[react]] / [[vue]] / [[nextjs]] — generate this markup/CSS.
- [[ux-design]] — the design heuristics (Gestalt, Fitts, hierarchy) the markup serves.
- [[secure-coding]] — output escaping, Content-Security-Policy.
- Sources: *HTML5 in Action*; *HTML & CSS QuickStart Guide*; *CSS3 Foundations*; CSS Fonts & CSS Text specs; *Responsive Web Design with HTML5 & CSS3* / *Beginning Responsive Web Design*.
