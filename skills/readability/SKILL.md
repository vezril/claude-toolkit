---
name: readability
description: Analyze text readability with Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog, and SMOG — computed by a bundled Python script for accuracy, then interpreted with audience fit and concrete revision suggestions. Use when checking whether prose matches its intended audience.
user-invocable: true
argument-hint: "[text to analyze]"
---

# Analyze Readability

Compute readability metrics with the bundled script, then interpret them.

## Input

Text comes from $ARGUMENTS. If none is provided, ask for it.

## Step 1: Compute (don't estimate)

Never hand-count syllables or eyeball the formulas — run the script:

```bash
python3 <skill-dir>/scripts/readability.py <<'EOF'
[the text]
EOF
```

It returns JSON with the four scores plus supporting stats. If Python is unavailable, fall back to careful manual computation and say the numbers are approximate.

## Step 2: Interpret

| Flesch Reading Ease | Grade level | Audience |
|---------------------|-------------|----------|
| 90-100 | 5th | Very easy — general public, any context |
| 80-89 | 6th | Easy — consumer content |
| 70-79 | 7th | Fairly easy — most web writing should land here |
| 60-69 | 8-9th | Standard — newspapers, business email |
| 50-59 | 10-12th | Fairly difficult — trade publications |
| 30-49 | College | Difficult — academic, technical docs |
| 0-29 | Graduate | Very difficult — dense academic prose |

Cross-check the four scores: when they disagree sharply, say why (Fog and SMOG punish polysyllables; Flesch-Kincaid punishes long sentences).

## Output Format

```
## Readability Analysis

### Scores
| Metric | Score | Meaning |
|--------|-------|---------|
| Flesch Reading Ease | X | [band] |
| Flesch-Kincaid Grade | X | [grade] |
| Gunning Fog | X | [years of education] |
| SMOG | X | [grade] |

### Statistics
- Words: X · Sentences: X · Avg sentence: X words
- Complex words (3+ syllables): X (Y%)

### Audience Fit
[Who reads this comfortably — and whether that matches the text's apparent purpose]

### Top 3 Fixes
1. [Quote a specific long sentence and show a shorter split]
2. [Name specific complex words and give plain swaps]
3. [One structural suggestion]
```

## Interpretation Rules

- Judge against the text's **purpose**: grade 14 is fine for a systems-design doc, a problem for a landing page.
- Suggestions must quote the actual text — no generic "shorten your sentences" advice.
- Note the script's own caveats (heuristic syllables; SMOG needs 30+ sentences) when relevant.
