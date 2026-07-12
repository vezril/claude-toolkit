---
name: word-stats
description: Get exact word count, character count, sentence/paragraph counts, reading and speaking time, and vocabulary stats — computed by a bundled Python script, presented as tables with zero prose. Use for quick text statistics with no questions asked.
user-invocable: true
argument-hint: "[text to analyze]"
---

# Word Statistics

Exact text statistics, fast. No clarifying questions, no commentary — just the numbers.

## Input

Text comes from $ARGUMENTS. If text is present, output stats immediately.

## Step 1: Compute (don't count by eye)

Run the bundled script — never count words or characters yourself:

```bash
python3 <skill-dir>/scripts/word_stats.py <<'EOF'
[the text]
EOF
```

If Python is unavailable, use `wc` for words/characters and note that the derived stats are approximate.

## Step 2: Present

```
## Word Statistics

| Metric | Value |
|--------|-------|
| Words | X |
| Characters (with spaces) | X |
| Characters (no spaces) | X |
| Sentences | X |
| Paragraphs | X |
| Reading time | X min (238 wpm) |
| Speaking time | X min (150 wpm) |
| Unique words | X (Y%) |
| Avg word length | X chars |
| Longest word | word (X chars) |
| Avg sentence | X words |
| Longest / shortest sentence | X / X words |
```

## Rules

- One table, no headers-per-section unless the user asks for detail.
- No recommendations, no interpretation, no prose — unless explicitly asked.
- Round times to one decimal; under 0.5 min, show seconds instead.
