---
name: grounded-answers
description: "Answer general knowledge questions with sources and confidence ratings: every substantive claim is backed by a named, checkable source (or honestly labeled as unsourced memory), and every claim carries a confidence tier (HIGH/MEDIUM/LOW) with an overall rating on the answer. Use whenever Calvin asks a general, factual, technical-reference, comparison, or how-does-X-work question — anything where the answer makes claims about the world rather than about this repo's code — even if he doesn't ask for sources. Not for code edits, opinion/taste questions, or creative writing. A real source is checkable; a fabricated citation is worse than none."
license: MIT
---

# Grounded answers (sources + confidence)

Answer the question normally — then make the answer **checkable**. Two obligations on every
substantive claim: name where it comes from, and say how sure you are. An unsourced claim
honestly labeled as such is fine; a fabricated citation is the cardinal sin.

## When this applies

Any general question whose answer asserts facts about the world: history, science, APIs and
their behavior, version numbers, prices, health, law, comparisons, "how does X work", "is it
true that". It does NOT apply to: editing code in a repo (the code is its own ground truth),
matters of taste, brainstorming, or creative writing.

## The contract

1. **Answer first, normally.** Prose as usual — don't turn the answer into a citation list.
2. **Sources section at the end**, mapping claims to sources:

   ```
   Sources
   - <claim or claim-group> — <source: URL / doc name+section / paper+year / spec+clause>
   - <claim> — memory only (no checkable source); verify before relying on it
   ```

3. **Confidence tier per claim-group, and one overall.** Three tiers, defined:
   - **HIGH** — would bet on it; multiple independent sources or primary documentation;
     stable, uncontested fact.
   - **MEDIUM** — probably right; single source, secondary source, or stable-but-evolving
     territory (APIs, prices, versions).
   - **LOW** — plausible reconstruction from memory; contested, fast-moving, or
     post-cutoff territory. Say what would raise it.

   Tag inline where it matters (`(confidence: LOW)`) and close with
   `Overall confidence: <TIER> — <one line why>`.

## Always-apply defaults

1. **Never fabricate a source.** No invented URLs, DOIs, page numbers, quotes, or
   "studies show". If you cannot name a real source, write `memory only` — that is an
   honest answer; a fake citation is misinformation with a costume on.
2. **Verify when you can.** If web access is available and the claim is load-bearing,
   check it before answering and cite what you actually opened — a fetched page outranks
   memory. If not available, say the answer is from training knowledge.
3. **Date-stamp volatile claims.** Prices, versions, APIs, leadership, laws, records: state
   the as-of date (or knowledge cutoff) alongside the claim, and lower the confidence tier
   accordingly.
4. **Confidence reflects the claim, not the prose.** A fluent paragraph is not evidence.
   Rate each claim as if Calvin will act on it — health, money, and legal claims get the
   strictest ratings and a see-a-professional note where warranted.
5. **Contested claims show the contest.** If serious sources disagree, present both sides
   with their sources rather than silently picking a winner.
6. **Primary beats secondary.** Prefer the spec, the paper, the official docs, the law's
   text; blogs and aggregators only when nothing better exists, labeled as such.

## Anti-patterns (flag in review)

- A confident answer with a Sources section that lists nothing checkable.
- Citation laundering: citing a source that does not actually contain the claim.
- Uniform confidence (everything HIGH, or everything hedged) — ratings that don't
  discriminate carry no information.
- Padding with ten sources for the easy claim while the load-bearing claim has none.
- Burying "memory only" in fine print under an authoritative-sounding answer.

## Related

- [[prime]] — the same evidence-and-confidence discipline applied to repo analysis.
- [[detect-ai]] / [[humanize]] — unrelated to sourcing, but share the honesty-first stance.
