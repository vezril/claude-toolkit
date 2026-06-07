# Layout, responsive & typography recipes

Working CSS reference (CSS3 Foundations; responsive-design books; CSS Fonts/Text).

## Specificity & cascade (decide which rule wins)
Specificity tuple **(ids, classes/attrs/pseudo-classes, types/pseudo-elements)** — compare left to right; higher wins; ties → later source order. Inline style beats selectors; `!important` beats all (avoid). Keep it flat: prefer a single class; avoid `#id` and descendant chains. Inherited properties (color, font-*, line-height, visibility) flow to children; set them high.

## Box model
`box-sizing: border-box` (set globally: `*{box-sizing:border-box}`) so `width` includes padding+border. Layers: content → padding → border → margin. Vertical margins between blocks **collapse** (the larger wins) — a frequent surprise; fl/grid `gap` avoids it.

## Flexbox (1D) recipe
```css
.toolbar { display:flex; align-items:center; justify-content:space-between; gap:1rem; }
.toolbar .spacer { flex:1; }            /* push items apart */
.center { display:flex; justify-content:center; align-items:center; } /* perfect centering */
.cards { display:flex; flex-wrap:wrap; gap:1rem; }
.card { flex: 1 1 200px; }              /* grow, shrink, basis */
```
`flex-direction: row|column`; `justify-content` = main axis, `align-items` = cross axis.

## Grid (2D) recipe
```css
.page { display:grid; grid-template-columns: 240px 1fr; gap:1rem; }     /* sidebar + content */
.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1rem; } /* responsive cards, no media query */
.layout {
  display:grid;
  grid-template-areas: "header header" "nav main" "footer footer";
  grid-template-columns: 200px 1fr;
}
.header{grid-area:header} .nav{grid-area:nav} .main{grid-area:main} .footer{grid-area:footer}
```
Use `fr` for flexible tracks, `minmax()` + `auto-fit/auto-fill` for responsive grids without breakpoints, named areas for readable layouts. **Grid for the page, Flexbox inside components.**

## Responsive (mobile-first)
```css
/* base = mobile */
.container { padding: 1rem; }
/* enhance upward */
@media (min-width: 48rem)  { .container { padding: 2rem; } }   /* tablet  */
@media (min-width: 64rem)  { .grid { grid-template-columns: repeat(3,1fr); } } /* desktop */
```
- Fluid type: `font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem);`
- Fluid images: `img{max-width:100%;height:auto}`; responsive sources via `srcset`/`<picture>`.
- **Container queries** (component-level): `.card{container-type:inline-size}` then `@container (min-width:30rem){ .card{...} }` — style by the *container*, perfect for reusable components.
- Honor: `@media (prefers-color-scheme: dark)`, `@media (prefers-reduced-motion: reduce)`.

## Custom properties (theming/dark mode)
```css
:root { --bg:#fff; --fg:#111; --brand:#06c; --space:1rem; }
@media (prefers-color-scheme: dark){ :root{ --bg:#111; --fg:#eee; } }
body{ background:var(--bg); color:var(--fg); }
```
Variables cascade and can be overridden per-scope; great for themes, spacing scales, and runtime changes via JS.

## Typography & web fonts
```css
@font-face {
  font-family:"Inter"; src:url("/fonts/inter.woff2") format("woff2");
  font-weight:100 900; font-display:swap;     /* variable font, no FOIT */
}
body { font-family:"Inter", system-ui, sans-serif; line-height:1.6; }
.prose { max-width:70ch; }                      /* readable measure 45–75ch */
.title { font-size:clamp(1.5rem,4vw,2.5rem); letter-spacing:-0.01em; }
.truncate { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
```
`line-height` unitless; fallback stacks; self-host woff2 for privacy/perf; variable fonts for many weights in one file.

## Motion (cheap, smooth)
```css
.btn { transition: transform .15s ease, background-color .15s ease; }
.btn:hover { transform: translateY(-1px); }
@keyframes fade { from{opacity:0} to{opacity:1} }
.modal { animation: fade .2s ease both; }
@media (prefers-reduced-motion: reduce){ *{animation:none!important;transition:none!important} }
```
Animate **`transform`/`opacity`** (GPU-composited, no reflow); avoid animating width/height/top/left (jank).

## Quick a11y checklist
Semantic elements · one `<h1>`, no skipped levels · `<label>` for every input · `alt` on images · visible `:focus` styles · keyboard operable · WCAG contrast (4.5:1 text) · `aria-*` only where semantics fall short · don't convey info by color alone.
