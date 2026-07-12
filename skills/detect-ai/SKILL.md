---
name: detect-ai
description: Analyze text for signs of AI generation using local stylometric signals — burstiness, cliché density, hedging, structural uniformity. Returns a 0-100 likelihood estimate with a per-signal breakdown and honest confidence caveats. Runs entirely locally; no text is sent anywhere. Use when reviewing content before publishing, or when curious whether prose reads as AI-drafted.
user-invocable: true
argument-hint: "[text to analyze]"
---

# Detect AI-Style Writing

Estimate how strongly a piece of text exhibits the stylistic fingerprints of AI-generated prose. This is a **local, heuristic judgment** — no external API, no detector service, nothing leaves the machine.

## Input

Take the text from $ARGUMENTS. If none is provided, ask for it. If the text is under ~100 words, still analyze it but flag that short samples give low-confidence results.

## Signals to Evaluate

Score each signal 0-10 (10 = strongly AI-like), then weight as shown:

| Signal | Weight | What to look for |
|--------|--------|------------------|
| **Burstiness** | 25% | Human writing mixes long and short sentences. Compute rough sentence-length variance; low variance (all sentences 15-25 words) is AI-like. |
| **Cliché density** | 20% | Stock AI phrasing: "delve", "tapestry", "in today's fast-paced world", "it's important to note", "furthermore/moreover" chains, "not only X but also Y", excessive em-dashes, rule-of-three lists everywhere. |
| **Hedging & throat-clearing** | 15% | "It's worth mentioning", "generally speaking", balanced both-sides framing with no actual stance. |
| **Structural uniformity** | 15% | Every paragraph the same length, intro-body-conclusion symmetry, headers with parallel gerunds, summary paragraph restating everything. |
| **Specificity deficit** | 15% | Vague claims with no concrete numbers, names, dates, or first-hand detail; examples that could apply to anything. |
| **Surface perfection** | 10% | Zero typos, perfectly consistent punctuation and register, no colloquial slips — combined with the signals above (alone, this just means good editing). |

## Scoring

Weighted average × 10 → 0-100 scale:

- **0-20** — Reads as human-written
- **21-40** — Probably human; a few AI-like patterns
- **41-60** — Mixed signals; genuinely ambiguous
- **61-80** — Reads as AI-drafted, possibly human-edited
- **81-100** — Strongly AI-patterned throughout

## Output Format

```
## AI-Style Analysis

**Estimate:** [score]/100 — [band label]
**Sample size:** [word count] words ([confidence: low <150 / medium 150-400 / high >400])

### Signal Breakdown
| Signal | Score | Evidence |
|--------|-------|----------|
| Burstiness | X/10 | [quote or stat] |
| Cliché density | X/10 | [specific phrases found] |
| ... | | |

### Strongest Evidence
[2-3 quoted examples from the text]

### Caveats
[Standard caveats below, adapted to this sample]
```

## Mandatory Caveats

Always include, in your own words:

1. **No detector is reliable.** Stylometric analysis — this one and commercial tools alike — produces false positives and false negatives. Skilled human writers trigger it; edited AI text evades it.
2. **Never treat this as proof.** This estimate must not be used to accuse a specific person (student, employee, applicant) of using AI. Refuse to frame results as evidence of misconduct.
3. **Short texts are noise.** Under ~150 words, say the estimate is weak and lean toward "inconclusive".
