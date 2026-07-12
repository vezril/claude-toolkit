---
name: humanize
description: Edit stilted, AI-drafted, or over-formal text so it reads like natural human prose — vary sentence rhythm, cut clichés and hedging, add concrete detail, restore a real voice. For improving writing you're entitled to present as yours. NOT for evading AI detectors or misrepresenting authorship in academic or disclosure-required contexts.
user-invocable: true
argument-hint: "[text to edit] [--touch light|standard|deep]"
---

# Humanize: Natural-Prose Editing

Rewrite text that reads as machine-drafted or over-polished so it sounds like a person wrote it. This is an **editing skill**, done locally by you — no external service, no credits, no API.

## Scope Boundary (read first)

This skill improves prose quality. It is **not** a detector-evasion tool:

- If the user's stated goal is to beat an AI detector (GPTZero, Turnitin, Originality.ai, etc.), to pass off AI work as their own in an academic submission, or to defeat an authorship check — decline that framing. Offer instead to help them improve the writing openly, or to disclose AI assistance where required.
- Editing your own drafts, marketing copy, emails, docs, or blog posts to sound natural is squarely in scope.

## Input

Parse $ARGUMENTS for the text and an optional `--touch` flag:

| Touch | Behavior |
|-------|----------|
| `light` | Fix only the worst offenders: clichés, hedging, dead openers. Preserve structure and voice. |
| `standard` (default) | Full pass: rhythm, word choice, structure, voice. Meaning preserved exactly. |
| `deep` | Restructure freely — reorder points, merge/split paragraphs, rewrite in a genuinely conversational register. Confirm key facts survived. |

## Editing Moves

1. **Break the rhythm.** Vary sentence length hard. Follow a long sentence with a three-word one. Like this.
2. **Kill stock phrases.** "Delve", "tapestry", "in today's fast-paced world", "it's important to note", "moreover", "in conclusion" — delete or replace with plain words.
3. **Cut hedging and throat-clearing.** Take a stance. "It could be argued that X is beneficial" → "X works."
4. **Concretize.** Replace generic claims with specifics the text already implies; where specifics are missing, insert a bracketed prompt like `[add: actual number]` rather than inventing facts.
5. **Un-symmetrize structure.** Not every paragraph needs three sentences. Not every list needs three items. Drop the summary paragraph that restates everything.
6. **Restore voice.** Contractions, occasional sentence fragments, direct address where the register allows. Match the user's own voice if earlier writing samples are available in context.
7. **Never fabricate.** No invented anecdotes, credentials, or data to make text seem more "human". Naturalness comes from rhythm and word choice, not fake lived experience.

## Output Format

```
## Edited Text

[the rewritten text]

---
**Touch:** [light/standard/deep]
**Key changes:** [3-5 bullets: what was changed and why]
**Flags:** [any [add: ...] placeholders needing real facts, or "none"]
```

Keep the before/after honest: if the original was already natural, say so and make minimal changes rather than churning it.
