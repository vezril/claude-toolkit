---
name: markdown
description: "Writing Markdown, focused on Obsidian (the primary environment) with portable base Markdown as the foundation. Covers CommonMark/GFM basics (headings, emphasis, lists, links, images, code, tables, task lists, footnotes) with the whitespace gotchas that actually bite, and Obsidian Flavored Markdown in depth: internal wikilinks with heading/block links and display text, embeds with image sizing, block identifiers (^id), callouts (the full type list + foldable/nested variants), YAML properties/frontmatter (types, tags/aliases/cssclasses), tags (inline vs frontmatter, nested), attachments, math ($/$$), mermaid, comments (%%), plus folding and multiple cursors. Use when writing or editing Markdown notes — especially Obsidian vault notes — building callouts, frontmatter, wikilinks/embeds, tables, or when unsure what syntax Obsidian supports vs generic Markdown. Distilled from markdownguide.org and the Obsidian help docs."
argument-hint: "[what you're writing, or a syntax question]"
license: MIT
---

# Markdown (Obsidian-focused)

Writing Markdown well, primarily for **Obsidian** vaults. Obsidian stores everything as plaintext `.md` files and builds on **CommonMark + GitHub Flavored Markdown**, adding its own extensions (Obsidian Flavored Markdown — OFM) on top. So the mental model is two layers: **portable base Markdown** that works anywhere, and **Obsidian-only syntax** (`[[wikilinks]]`, `![[embeds]]`, callouts, `%%comments%%`) that won't render outside Obsidian. Know which layer you're using and why.

## Base Markdown (portable foundation)

- **Headings** `# H1` … `###### H6` — space after `#` required; blank line before and after.
- **Emphasis** `*italic*` / `_italic_`, `**bold**` / `__bold__`, `***bold italic***`. Use asterisks for mid-word emphasis (underscores don't work mid-word). `~~strikethrough~~` (GFM).
- **Lists.** Unordered `-`/`*`/`+` (don't mix delimiters in one list); ordered `1.` `2.` `3.` (periods; start number honored). Nest by indenting under the parent's content (4 spaces / 1 tab is the safe rule). Child paragraphs/blocks under a list item indent 4 spaces, separated by a blank line.
- **Task lists** (GFM) `- [ ]` / `- [x]`.
- **Blockquotes** `> quote`; nest with `>>`; keep a bare `>` on blank lines between quoted paragraphs.
- **Code.** Inline `` `code` `` (wrap in `` `` `` if it contains a backtick). Fenced blocks with a language for highlighting:
  ````
  ```python
  print("hi")
  ```
  ````
- **Links.** Inline `[text](https://url "optional title")`; reference-style `[text][ref]` + `[ref]: https://url`; autolink `<https://url>`. Encode spaces in URLs as `%20`.
- **Images** `![alt](path "title")`; clickable image `[![alt](img)](url)`.
- **Horizontal rule** `---` / `***` / `___` on its own line (blank lines around it — `---` directly under text becomes a Setext H2 instead).
- **Tables** (GFM):
  ```
  | Col | Col |
  | :-- | --: |
  | a   | b   |
  ```
  Colons in the delimiter row set alignment (`:--` left, `:--:` center, `--:` right). Inline formatting/links work in cells; escape a literal pipe as `\|`.
- **Footnotes** `text[^1]` … `[^1]: definition` (also named `[^note]` and inline `^[inline note]`).
- **Escaping** — backslash before a literal: `` \ ` * _ { } [ ] ( ) # + - . ! | ^ > ``.
- **HTML** is allowed as a fallback for things Markdown lacks (`<ins>underline</ins>`, `<img width=200>`, `<center>`, colored `<font>`, `&copy;`/`&#960;` entities) — but **Markdown is not parsed inside HTML block elements**, in Obsidian especially.

### The whitespace gotchas that actually bite

- **Blank lines around every block** (headings, lists, blockquotes, fenced code, tables, rules). Most "why won't this render" bugs are a missing blank line.
- **Hard line break** = two trailing spaces, or `<br>` (preferred — invisible spaces are a trap). In Obsidian, `Shift+Enter` inserts the line break for you.
- **Don't mix tabs and spaces** for indentation — pick one.

## Obsidian Flavored Markdown (the focus)

Obsidian-only. These are the payload of a vault.

- **Internal links (wikilinks).** `[[Note name]]`; to a heading `[[Note#Heading]]`; heading chain `[[Note#Heading#Subheading]]`; same-note heading `[[#Heading]]`; to a block `[[Note#^block-id]]`; **custom display text** `[[Note|shown text]]` (and `[[Note#Heading|shown text]]`). Markdown-link equivalent: `[shown text](Note%20name.md)` (spaces → `%20`). Obsidian emits wikilinks by default; the *Settings → Files and links → "Use `[[Wikilinks]]`"* toggle switches to Markdown links.
- **Embeds** = a link with `!` in front. `![[Note]]` (whole note), `![[Note#Heading]]` (section), `![[Note#^block-id]]` (block). Images: `![[image.png]]`, sized `![[image.png|100]]` (width) or `![[image.png|100x145]]` (w×h). Also `![[audio.mp3]]`, `![[Doc.pdf#page=3]]`, `![[My canvas.canvas]]`. (Link = reference; embed = inline the content.)
- **Block identifiers** make any block linkable/embeddable. Simple paragraph: append ` ^block-id` at the end of the line. Structured block (list/table/quote/callout): put `^block-id` on its **own line with a blank line before it**. Human-readable IDs use Latin letters/numbers/dashes only (`^quote-of-the-day`); otherwise Obsidian auto-generates one like `^37066d`.
- **Highlight** `==text==` (OFM). **Comments** `%%hidden%%` — inline or block (`%% … %%` across lines); never rendered, stays in the file.
- **Math** (LaTeX/MathJax): inline `$e^{i\pi}=-1$`, display `$$ … $$` on its own lines.
- **Diagrams**: a ` ```mermaid ` fenced block. Wikilinks inside a diagram need the `internal-link` class; quote node names with special characters.
- **Tables with links**: escape the pipe inside a cell — `[[Note\|alias]]`, `![[image.png\|200]]`.

## Callouts

Blockquote + a `[!type]` token. The signature Obsidian feature.

```
> [!tip] Optional custom title
> Body — supports **markdown**, `[[wikilinks]]`, and `![[embeds]]`.
```

- **Foldable:** `> [!type]+` (expanded by default) or `> [!type]-` (collapsed). Title-only: `> [!note] Just a title` (no body).
- **Nesting:** add a `>` per level (`> > [!todo]`).
- **Built-in types** (identifiers case-insensitive; unknown type falls back to `note`):
  `note` · `abstract` (aliases `summary`, `tldr`) · `info` · `todo` · `tip` (`hint`, `important`) · `success` (`check`, `done`) · `question` (`help`, `faq`) · `warning` (`caution`, `attention`) · `failure` (`fail`, `missing`) · `danger` (`error`) · `bug` · `example` · `quote` (`cite`).
- **Custom types** via a CSS snippet: `.callout[data-callout="my-type"] { --callout-color: 0,0,0; --callout-icon: lucide-flame; }`.

## Properties (YAML frontmatter)

A `---` fenced block at the very top of the file. Name, colon, **space**, value; each name unique.

```yaml
---
title: My note
year: 1977            # number
date: 2020-08-21      # date (ISO 8601); datetime adds T10:30:00
favorite: true        # checkbox (boolean)
tags:                 # list
  - project
  - reference
aliases:
  - Alt name
cssclasses:
  - wide-note
link: "[[Other note]]"  # internal links in properties MUST be quoted
---
```

Types: text (markdown not rendered), list, number, checkbox, date, date-&-time. The three **special properties**: `tags`, `aliases` (both YAML lists), and `cssclasses` (apply CSS). Templating plugins writing raw YAML must add the quotes around `[[wikilinks]]` themselves.

## Tags, attachments, and editor niceties

- **Tags.** Inline in the body with `#`: `#meeting`, nested `#inbox/to-read` (searching the parent matches children). In frontmatter under `tags:` they're written **without** the `#`. Rules: no spaces (`#camelCase`/`#kebab-case`), can't be purely numeric (`#1984` invalid, `#y1984` fine); letters/numbers/`_`/`-`/`/` (+ many Unicode/emoji). Case-insensitive. **Tags label many notes by topic/status; links connect two specific notes** — reach for links when you want the graph/backlinks, tags for categorization.
- **Attachments.** Regular files in the vault; *Settings → Files & Links → Default location for new attachments* controls where pasted/dragged files land (vault root, a set folder, same folder as note, or a subfolder). Paste or drag auto-embeds with `![[…]]`. Accepted: `.md`; images `.avif .bmp .gif .jpeg .jpg .png .svg .webp`; audio `.flac .m4a .mp3 .ogg .wav .webm .3gp`; video `.mkv .mov .mp4 .ogv .webm`; `.pdf` (a/v depends on device codecs).
- **Folding** is a *display* feature (headings and indented lists fold; nothing changes in the file). **Multiple cursors:** `Alt`/`Option`-click to add cursors; `Shift+Alt`/`Shift+Option`-drag for column selection; `Escape` clears extras.

## Portability — what breaks outside Obsidian

Base Markdown (everything in the first section) travels. **These do not render outside Obsidian:** `[[wikilinks]]`, `![[embeds]]`, block IDs `^id`, `%%comments%%`, callouts, `==highlight==` (patchy elsewhere), and `$$`math/`mermaid` (renderer-dependent). And Obsidian itself does **not** support some extended Markdown — heading IDs (`{#id}`), definition lists, emoji shortcodes (`:joy:` — paste the literal emoji instead), and subscript/superscript (use `<sub>`/`<sup>`). If a note must publish to plain Markdown, stay in the base layer or plan the conversion.

## Related

- [[calvin-voice]] — the prose *voice* for vault notes; this skill is the *syntax* they're written in.
- [[morning]] — the ADHD morning-kickoff routine that lives in the vault.
- [[requirements-engineering]] · [[spec-driven-development]] — docs authored in Markdown.

Sources: markdownguide.org (basic-syntax, extended-syntax, cheat-sheet, hacks, tools/obsidian); the Obsidian help docs (syntax, advanced-syntax, obsidian-flavored-markdown, callouts, properties, folding, multiple-cursors, links, aliases, embeds, tags, attachments) — fetched 2026-07.
