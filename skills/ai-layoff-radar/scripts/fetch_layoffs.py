#!/usr/bin/env python3
"""Fetch candidate layoff articles from Google News RSS. Stdlib only — no API key, no cost.

This is the deterministic HALF of the ai-layoff-radar skill: it pulls and lightly
structures headlines. It does NOT decide whether a layoff is AI-caused — that judgment
is left to the model reading this script's output (see SKILL.md), which is both free and
better than a keyword match. The script never claims causality; it extracts what the
headline/snippet literally says and flags AI mentions for the model to weigh.

Google News RSS is public and keyless. The only network calls are to
`news.google.com/rss/search` — nothing else, no third-party billing, no telemetry.

Usage:
    python3 fetch_layoffs.py                       # default keywords, last 14 days, JSON to stdout
    python3 fetch_layoffs.py --days 7 --max 8      # tighter window, fewer per feed
    python3 fetch_layoffs.py --query "AI layoffs" --query "automation job cuts"
    python3 fetch_layoffs.py --region GB           # gl/ceid region hint (default US)

Output: JSON {"generated_at","window_days","queries","count","candidates":[...]}
Each candidate: title, snippet, source, url, published, published_iso,
                company_guess, layoff_count, country_guess, mentions_ai (bool),
                ai_terms (list). Deduplicated by normalized title.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional

DEFAULT_QUERIES = [
    "AI layoffs",
    "AI job cuts",
    "automation layoffs",
    "artificial intelligence layoffs",
    "AI replacing workers",
    "AI efficiency job cuts",
]

# AI terms are surfaced for the MODEL to weigh — presence is a signal, not a verdict.
AI_TERMS = [
    "ai", "a.i.", "artificial intelligence", "automation", "automate", "automated",
    "machine learning", "generative ai", "genai", "chatbot", "ai agent", "ai agents",
    "llm", "algorithm", "robot", "efficiency",
]
LAYOFF_TERMS = [
    "layoff", "lay off", "lays off", "laid off", "job cut", "jobs cut", "cut jobs",
    "cutting jobs", "redundanc", "workforce reduction", "reduce headcount",
    "headcount reduction", "slash jobs", "downsiz", "let go", "restructur",
]
COUNTRY_MAP = {
    "united states": "USA", " u.s.": "USA", " us ": "USA", "america": "USA",
    "united kingdom": "UK", " u.k.": "UK", "britain": "UK", "england": "UK",
    "canada": "Canada", "india": "India", "china": "China", "germany": "Germany",
    "france": "France", "japan": "Japan", "australia": "Australia", "ireland": "Ireland",
}
# Headline tokens that terminate a leading company name ("Google cuts 200 jobs" -> "Google").
_STOP_TOKENS = {
    "cuts", "cut", "lays", "lay", "laying", "slashes", "slash", "to", "will", "plans",
    "announces", "confirms", "after", "amid", "as", "is", "are", "reportedly", "said",
    "sheds", "shed", "trims", "trim", "axes", "axe", "fires", "reduces",
}
UA = "Mozilla/5.0 (compatible; ai-layoff-radar/1.0; +https://news.google.com/rss)"


def _rss_url(query: str, region: str) -> str:
    region = (region or "US").upper()
    hl = {"US": "en-US", "GB": "en-GB", "CA": "en-CA", "AU": "en-AU", "IN": "en-IN"}.get(region, "en-US")
    q = urllib.parse.quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={region}&ceid={region}:{hl.split('-')[0]}"


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
           .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", s).strip()


# Leading words that mean the headline doesn't start with a company name.
_NON_COMPANY_LEAD = {
    "the", "a", "an", "how", "why", "what", "when", "thousands", "hundreds",
    "dozens", "millions", "more", "over", "amid", "as", "after", "these", "this",
    "report", "opinion", "exclusive", "breaking", "tech", "ai", "another", "inside",
}


def _company_guess(title: str) -> str:
    head = re.split(r"[:\-–—|]", title, 1)[0].strip()
    tokens = head.split()
    if not tokens:
        return ""
    first = tokens[0].lower().strip(",.")
    # Reject headlines that don't open with a proper-noun-looking company token.
    if first in _NON_COMPANY_LEAD or tokens[0][:1].isdigit() or not tokens[0][:1].isupper():
        return ""
    company = []
    for tok in tokens:
        if tok.lower().strip(",.") in _STOP_TOKENS:
            break
        company.append(tok)
        if len(company) >= 4:
            break
    guess = " ".join(company).strip(" ,.")
    return guess if 1 < len(guess) < 50 else ""


def _layoff_count(text: str) -> Optional[int]:
    patterns = [
        r"(\d{1,3}(?:,\d{3})+|\d{2,6})\s+(?:employees|workers|staff|jobs|roles|people|positions)",
        r"(?:cut|cuts|lay(?:ing)? off|lays off|laid off|slash(?:ing)?|shed(?:ding)?|axe[sd]?)\s+(?:about |around |up to |nearly )?(\d{1,3}(?:,\d{3})+|\d{2,6})",
        r"(\d{1,2}(?:\.\d+)?)\s*%\s+of\s+(?:its |the )?(?:workforce|staff|employees)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m and "%" not in m.group(0):
            try:
                return int(m.group(1).replace(",", ""))
            except ValueError:
                continue
    return None


def _country_guess(text: str) -> str:
    low = f" {text.lower()} "
    for needle, name in COUNTRY_MAP.items():
        if needle in low:
            return name
    return ""


def _ai_terms_in(text: str) -> List[str]:
    low = f" {text.lower()} "
    return sorted({t.strip() for t in AI_TERMS if f" {t} " in low or t in low})


def _looks_like_layoff(text: str) -> bool:
    low = text.lower()
    return any(t in low for t in LAYOFF_TERMS)


def _fetch(url: str, timeout: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - fixed news.google.com host
        return resp.read().decode("utf-8", errors="replace")


def _process_feed(xml_text, cutoff, max_per_feed, seen, candidates):
    """Parse one RSS document and append qualifying, deduped, in-window items."""
    root = ET.fromstring(xml_text)
    for item in list(root.iter("item"))[:max_per_feed]:
        title = _strip_html(item.findtext("title") or "")
        if not title:
            continue
        key = re.sub(r"[^a-z0-9]+", "", title.lower())[:80]
        if key in seen:
            continue
        snippet = _strip_html(item.findtext("description") or "")
        blob = f"{title} {snippet}"
        if not _looks_like_layoff(blob):
            continue
        pub_raw = item.findtext("pubDate") or ""
        pub_iso, pub_dt = "", None
        try:
            pub_dt = parsedate_to_datetime(pub_raw)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            pub_iso = pub_dt.astimezone(timezone.utc).isoformat()
        except Exception:
            pass
        if pub_dt is not None and pub_dt < cutoff:
            continue
        seen.add(key)
        source = ""
        src_el = item.find("source")
        if src_el is not None and src_el.text:
            source = src_el.text.strip()
        terms = _ai_terms_in(blob)
        candidates.append({
            "title": title,
            "snippet": snippet,
            "source": source,
            "url": (item.findtext("link") or "").strip(),
            "published": pub_raw,
            "published_iso": pub_iso,
            "company_guess": _company_guess(title),
            "layoff_count": _layoff_count(blob),
            "country_guess": _country_guess(blob),
            "mentions_ai": bool(terms),
            "ai_terms": terms,
        })


def fetch(queries, days, max_per_feed, region, timeout, stdin_xml=None):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    seen, candidates, errors = set(), [], []
    if stdin_xml is not None:
        # Offline / SSL-workaround path: one pre-fetched RSS document on stdin.
        queries = ["<stdin>"]
        try:
            _process_feed(stdin_xml, cutoff, max_per_feed, seen, candidates)
        except Exception as exc:
            errors.append({"query": "<stdin>", "error": str(exc)})
    else:
        for query in queries:
            try:
                xml = _fetch(_rss_url(query, region), timeout)
                _process_feed(xml, cutoff, max_per_feed, seen, candidates)
            except Exception as exc:  # network/parse errors are non-fatal per query
                msg = str(exc)
                if "CERTIFICATE_VERIFY_FAILED" in msg:
                    msg += (" — your Python has no CA bundle. Fix its certificates, or pipe a "
                            "feed in instead: curl -s '<rss-url>' | python3 fetch_layoffs.py --stdin")
                errors.append({"query": query, "error": msg})
                continue
    candidates.sort(key=lambda c: (c["published_iso"] or ""), reverse=True)
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": days,
        "region": (region or "US").upper(),
        "queries": queries,
        "count": len(candidates),
        "candidates": candidates,
    }
    if errors:
        out["fetch_errors"] = errors
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch candidate layoff articles (Google News RSS, keyless).")
    p.add_argument("--query", action="append", dest="queries", help="Search query (repeatable). Default: a built-in AI-layoff set.")
    p.add_argument("--days", type=int, default=14, help="Recency window in days (default 14).")
    p.add_argument("--max", type=int, default=10, dest="max_per_feed", help="Max items per query feed (default 10).")
    p.add_argument("--region", default="US", help="Region hint: US, GB, CA, AU, IN (default US).")
    p.add_argument("--timeout", type=int, default=20, help="Per-request timeout seconds (default 20).")
    p.add_argument("--stdin", action="store_true",
                   help="Parse one RSS document from stdin instead of fetching (offline / SSL workaround: "
                        "curl -s '<rss-url>' | python3 fetch_layoffs.py --stdin).")
    args = p.parse_args()
    queries = args.queries or DEFAULT_QUERIES
    stdin_xml = sys.stdin.read() if args.stdin else None
    try:
        result = fetch(queries, args.days, args.max_per_feed, args.region, args.timeout, stdin_xml=stdin_xml)
    except Exception as exc:  # only truly unexpected errors reach here
        print(json.dumps({"error": "unexpected", "detail": str(exc)}))
        sys.exit(1)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
