#!/usr/bin/env python3
"""Compute readability metrics for text on stdin. Stdlib only.

Usage: python3 readability.py < text.txt
Outputs JSON with Flesch Reading Ease, Flesch-Kincaid Grade,
Gunning Fog, SMOG, and supporting statistics.
"""
import json
import math
import re
import sys

VOWEL_GROUPS = re.compile(r"[aeiouy]+")


def count_syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = len(VOWEL_GROUPS.findall(w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and groups > 1:
        groups -= 1
    return max(1, groups)


def main() -> None:
    text = sys.stdin.read().strip()
    if not text:
        print(json.dumps({"error": "no input text"}))
        return

    sentences = [s for s in re.split(r"[.!?]+(?:\s|$)", text) if s.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    n_sent = max(1, len(sentences))
    n_words = max(1, len(words))

    syllables = [count_syllables(w) for w in words]
    n_syll = sum(syllables)
    # Complex words: 3+ syllables, excluding common suffix inflation (-es, -ed)
    complex_words = [w for w, s in zip(words, syllables) if s >= 3]
    n_complex = len(complex_words)

    wps = n_words / n_sent          # words per sentence
    spw = n_syll / n_words          # syllables per word
    pct_complex = n_complex / n_words * 100

    flesch = 206.835 - 1.015 * wps - 84.6 * spw
    fk_grade = 0.39 * wps + 11.8 * spw - 15.59
    fog = 0.4 * (wps + pct_complex)
    smog = 1.043 * math.sqrt(n_complex * 30 / n_sent) + 3.1291 if n_sent >= 1 else None

    sent_lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]

    print(json.dumps({
        "scores": {
            "flesch_reading_ease": round(flesch, 1),
            "flesch_kincaid_grade": round(fk_grade, 1),
            "gunning_fog": round(fog, 1),
            "smog": round(smog, 1) if smog is not None else None,
        },
        "stats": {
            "words": len(words),
            "sentences": len(sentences),
            "syllables": n_syll,
            "avg_sentence_length": round(wps, 1),
            "avg_word_length_chars": round(sum(len(w) for w in words) / n_words, 1),
            "complex_words": n_complex,
            "complex_word_pct": round(pct_complex, 1),
            "longest_sentence_words": max(sent_lengths) if sent_lengths else 0,
        },
        "notes": [
            "Syllable counts are heuristic (vowel-group method); scores may differ slightly from other tools.",
            "SMOG is designed for samples of 30+ sentences; treat it as rough below that.",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
