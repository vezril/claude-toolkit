---
name: cooklang
description: "Writing Cooklang — the plain-text markup for recipes (.cook files). Covers the full syntax: ingredients (@), cookware (#), timers (~), quantities and units ({qty%unit}), preparations, one-word vs {} multi-word tokens, steps as blank-line-separated paragraphs, sections (= ... =), notes (>), block/inline comments ([- -] and --), YAML frontmatter metadata (servings/source/time/tags/etc.), fractions and scaling, and recipe references (@./path{}). Plus the CookCLI toolchain: recipe/shopping-list/server/seed/import/doctor/pantry subcommands, aisle.conf shopping categories, and pantry.conf. Use when authoring or editing .cook recipe files, building a Cooklang recipe collection, generating shopping lists, or answering what Cooklang syntax is valid. Builds on the base-Markdown foundation (see the markdown skill) since .cook files are Markdown-adjacent plaintext with YAML frontmatter."
argument-hint: "[the recipe you're writing, or a Cooklang syntax question]"
license: MIT
---

# Cooklang

Cooklang is a **markup language for recipes** — plain text you write in a `.cook` file that a parser turns into structured ingredient lists, cookware, timers, and steps. The design goal: a recipe reads naturally as prose to a human, but the `@`/`#`/`~` markers let a machine extract a shopping list, scale servings, or render a clean recipe card. Think Markdown, but for cooking.

The mental model is two layers, exactly like [[markdown]]: **the prose** — ordinary sentences describing what to do — and **the markup tokens** embedded in that prose (`@ingredient`, `#cookware`, `~timer`) that carry the structured data. Everything not marked up is just step text. `.cook` files also use **YAML frontmatter** for metadata, so the base-Markdown frontmatter rules from the markdown skill carry straight over.

## The five tokens

| Token | Marks | Single word | Multi-word / with amount |
|:--|:--|:--|:--|
| `@` | ingredient | `@salt` | `@olive oil{}` · `@flour{200%g}` |
| `#` | cookware | `#pot` | `#frying pan{}` · `#bowl{2}` |
| `~` | timer | — | `~{25%minutes}` · `~eggs{3%min}` |
| `>` | note (line prefix) | `> Best made a day ahead.` | |
| `--` / `[- -]` | comment | `-- inline to EOL` | `[- block comment -]` |

**The `{}` rule is the thing to get right.** A bare `@word` / `#word` captures exactly **one word** (up to the next space or punctuation). The moment the name is **multiple words**, or you want to attach a **quantity**, you must close it with braces:

```cook
@salt                    -- one word, no braces needed
@ground black pepper{}   -- multi-word: {} marks where the name ends
@potato{2}               -- quantity, no unit
@bacon{1%kg}             -- quantity + unit (% separates them)
@milk{1/2%cup}           -- fractions are fine
```

Without the braces, `@ground black pepper` parses as the ingredient "ground" followed by the plain words "black pepper".

## Ingredients (`@`)

```cook
Crack @eggs{3} into a #bowl{} and whisk with @whole milk{200%ml}.
Season with @salt and @black pepper{}.
```

- **Quantity** goes in braces: `@sugar{100%g}`. **Unit** follows a `%`. No unit? Just the number: `@egg{2}`.
- **Preparation** in parentheses right after the token: `@onion{1}(finely chopped)`, `@garlic{2%cloves}(minced)`. The prep note is metadata attached to the ingredient, kept out of the name.
- **Text / "to taste" amounts** work: `@salt{a pinch}`, `@oil{some}` — the quantity slot holds free text when there's no number.
- **Mention each ingredient once.** Tag it with `@` on first appearance so it lands in the shopping list exactly once. Later references are plain prose: *"add the remaining onion"*, *"half the reserved stock"* — no `@`, or you'll double-count.
- **Scaling:** because quantities are structured, `@flour{200%g}` scales automatically when the recipe is cooked at a different serving count. Write amounts as real numbers/fractions so scaling works; keep "a pinch" for things that genuinely don't scale.

## Cookware (`#`)

Same shape as ingredients, minus units. `#pot`, `#large saucepan{}`, `#ramekins{4}`. The count in braces is a quantity (`{2}` = two of them), and cookware also accepts a parenthetical note: `#skillet{}(cast iron)`.

## Timers (`~`)

```cook
Simmer for ~{25%minutes}, then rest ~eggs{3%min} off the heat.
```

Always braced with a `quantity%unit`. **Optionally named** — the word between `~` and `{` (`~eggs`) labels the timer so a renderer/app can show "eggs — 3 min". Fractions allowed: `~{1/2%hour}`.

## Steps, sections, and notes

- **Steps** are paragraphs separated by **a blank line**. One paragraph = one step. (Same blank-line-is-load-bearing discipline as Markdown blocks — see [[markdown]].) A single step can span multiple typed lines; they join into one step unless separated by a blank line. Force a hard line break inside a step with a trailing backslash `\`.
- **Sections** group steps within a recipe (e.g. "Dough" vs "Filling"): a line of `= Section name =` (one or more `=` on each side; `= Dough` also works). Bare `==` with no text is a divider.
- **Notes** are non-step background — tips, make-ahead advice. Prefix the line with `>` (mirrors a Markdown blockquote): `> Rest the dough overnight for better flavour.`

## Comments

- **Inline**, to end of line: `-- this is ignored by the parser`
- **Block**, inline or spanning: `[- ignored -]`

Comments never appear in rendered output or shopping lists — use them for authoring notes, alternatives, or TODOs.

## Metadata (YAML frontmatter)

A `---`-fenced YAML block at the **very top** of the file, following the same rules as frontmatter in the [[markdown]] skill (name, colon, **space**, value; lists as YAML sequences). Older Cooklang used `>> key: value` lines; **prefer YAML frontmatter** — it's the current convention.

```cook
---
title: Root Vegetable Soup
servings: 4
source: https://example.com/soup
author: A. Cook
course: dinner
prep time: 15 min
cook time: 40 min
cuisine: British
diet: vegetarian
tags: [soup, winter, batch-cook]
---

Chop @carrots{3}(diced) and @onion{1}...
```

**Canonical keys** the ecosystem recognizes (many have synonyms — pick one and be consistent):

| Purpose | Keys |
|:--|:--|
| Name | `title` |
| Servings (drives scaling) | `servings` · `serves` · `yield` |
| Origin | `source` · `source.name` · `source.url` · `author` · `source.author` |
| Timing | `time required` / `time` / `duration` · `prep time` / `time.prep` · `cook time` / `time.cook` |
| Classification | `course` / `category` · `cuisine` · `difficulty` · `diet` · `tags` |
| Media / prose | `image(s)` / `picture(s)` · `introduction` / `description` |
| Locale | `locale` (ISO 639 lang, optional `_` + ISO 3166 country, e.g. `en_GB`) |

## Recipe references

Compose recipes: reference another `.cook` file as if it were an ingredient, with a relative path and optional amount.

```cook
Serve the curry over @./Basics/Rice.cook{2%servings}.
```

The referenced recipe's ingredients can be pulled into a combined shopping list. Paths are relative to the current file.

## A complete example

```cook
---
title: Garlic Butter Pasta
servings: 2
prep time: 5 min
cook time: 15 min
tags: [pasta, quick, vegetarian]
---

Bring a #large pot{} of salted water to a boil and cook
@spaghetti{200%g} for ~{9%minutes} until al dente.

= Sauce =

Melt @butter{3%tbsp} in a #frying pan{} over medium heat.
Add @garlic{4%cloves}(thinly sliced) and cook ~garlic{2%min}
until golden -- don't let it brown or it turns bitter.

Toss the drained pasta with the garlic butter, @parmesan{30%g}(grated),
and a handful of @parsley{}(chopped). Season with @salt and @black pepper{}.

> Reserve a splash of pasta water before draining to loosen the sauce.
```

## CookCLI — the toolchain

`cook` is the reference CLI for `.cook` files (install per <https://cooklang.org/cli/download/>). Core subcommands:

| Command | Alias | Does |
|:--|:--|:--|
| `cook recipe read <file.cook>` | `r` | Parse, validate, and print a recipe (human-readable, or `--output-format json`/`yaml` for structured data) |
| `cook shopping-list <files...>` | `sl` | Combine recipes into one aggregated shopping list, grouped by aisle |
| `cook server` | `s` | Start a local web UI to browse the recipe collection |
| `cook seed` | | Drop example recipes into the current dir to start a collection |
| `cook search <query>` | | Search recipes in the collection |
| `cook import <url>` | | Import a recipe from a website into `.cook` form |
| `cook doctor` | | Validate a collection — report broken references, warnings |
| `cook pantry` | | Work with pantry stock (subtract what you have from shopping lists) |
| `cook report` | | Render recipes through a custom template |

```bash
cook recipe read "Garlic Butter Pasta.cook"            # pretty-print
cook recipe read pasta.cook --output-format json       # structured output
cook shopping-list Monday.cook Tuesday.cook            # combined list
cook server                                            # browse at localhost
```

### `aisle.conf` — shopping-list categories

Groups ingredients under supermarket aisles so `shopping-list` output is sorted by section. Plain-text file of `[category]` headers followed by one ingredient per line; use `|` for aliases/synonyms so different spellings collapse to one entry.

```conf
[produce]
carrots
onion|onions|brown onion
garlic

[dairy]
butter
milk|whole milk
parmesan|parmigiano

[pantry]
spaghetti|pasta
olive oil
salt
```

Lives in the collection's config directory (a `config/` or `.cooklang/` folder alongside the recipes, or the platform config dir). A companion **`pantry.conf`** lists what you already have on hand so `cook pantry`/`shopping-list` can subtract it.

## Gotchas

- **Forgetting `{}` on a multi-word or amount-bearing token** is the #1 mistake — `@olive oil` ≠ `@olive oil{}`. The former is the ingredient "olive" plus the word "oil".
- **Blank line = new step.** A stray blank line splits one step into two; a missing one merges two steps. (Same block-separation discipline as [[markdown]].)
- **`%` only inside braces** separates quantity from unit. Outside braces it's a literal percent character.
- **Double-tagging an ingredient** duplicates it in the shopping list — tag once, refer to it by plain name afterward.
- **YAML frontmatter must be the first thing in the file** (before any step text) and validly indented, or the whole block is treated as a step.
- **File extension is `.cook`** — the CLI and apps discover recipes by extension.

## Related

- [[markdown]] — the base-plaintext foundation this builds on: `.cook` files are Markdown-adjacent, and the **YAML frontmatter** rules (name/colon/space, lists, quoting) are identical. Read that skill for the frontmatter and blank-line-block mechanics; read this one for the recipe tokens layered on top.

Sources: cooklang.org/docs (spec, best-practices, conventions) and cooklang.org/cli — fetched 2026-07.
