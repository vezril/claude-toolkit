#!/usr/bin/env python3
"""Compute word/character/sentence statistics for text on stdin. Stdlib only.

Usage: python3 word_stats.py < text.txt
"""
import json
import re
import sys


def main() -> None:
    text = sys.stdin.read()
    stripped = text.strip()
    if not stripped:
        print(json.dumps({"error": "no input text"}))
        return

    words = re.findall(r"[A-Za-z0-9']+", stripped)
    sentences = [s for s in re.split(r"[.!?]+(?:\s|$)", stripped) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", stripped) if p.strip()]
    lowered = [w.lower() for w in words]
    unique = set(lowered)
    n_words = max(1, len(words))

    sent_lengths = [len(re.findall(r"[A-Za-z0-9']+", s)) for s in sentences] or [0]
    longest_word = max(words, key=len) if words else ""

    print(json.dumps({
        "counts": {
            "words": len(words),
            "characters_with_spaces": len(stripped),
            "characters_no_spaces": len(re.sub(r"\s", "", stripped)),
            "sentences": len(sentences),
            "paragraphs": len(paragraphs),
        },
        "time": {
            "reading_minutes": round(len(words) / 238, 1),
            "speaking_minutes": round(len(words) / 150, 1),
        },
        "words": {
            "unique": len(unique),
            "unique_pct": round(len(unique) / n_words * 100, 1),
            "avg_length_chars": round(sum(len(w) for w in words) / n_words, 1),
            "longest": longest_word,
            "longest_length": len(longest_word),
        },
        "sentences": {
            "avg_length_words": round(sum(sent_lengths) / max(1, len(sent_lengths)), 1),
            "longest_words": max(sent_lengths),
            "shortest_words": min(sent_lengths),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
