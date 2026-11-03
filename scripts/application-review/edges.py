#!/usr/bin/env python3
"""The edges: deterministic checks that run between the model's steps.

The pipeline's whole design rests on one idea. The model is good at reading a
posting and finding the matching line in a CV; it is not the thing that should
decide the verdict, and it should not be trusted to tell us whether its own
quotes are real. So after every model step, a script checks the output and the
run stops if the check fails.

There are four of them:

  ``schema``       the output matches its contract in contracts.py
  ``references``   ids line up across requirements.json and evidence.json
  ``quotes``       every evidence quote is really in the CV; a ``met`` whose
                   quote is not found is downgraded to ``ambiguous``
  ``honesty``      no recommendation adds a claim the CV does not support

Run as a CLI by the agent:

    edges.py schema requirements out/requirements.json
    edges.py references --requirements out/requirements.json --evidence out/evidence.json
    edges.py quotes --evidence out/evidence.json --cv out/cv.txt --out out/evidence.checked.json
    edges.py honesty --recommendations out/recommendations.json --cv out/cv.txt \
                     --requirements out/requirements.json

Exit code 0 means the step may proceed. Anything else means it may not, and the
reason is printed with the id of the record that caused it.

Standard library only.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import contracts

__all__ = [
    "apply_quote_edge",
    "check_honesty",
    "check_posting_quotes",
    "check_references",
    "contains",
    "find_injection",
    "normalise",
]

# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

#: Characters a word processor or PDF generator substitutes for the plain
#: ASCII a model is likely to type back. Without this mapping, a quote that is
#: genuinely in the CV fails the verbatim check because of a smart apostrophe.
_PUNCT = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "―": "-", "−": "-",
    "…": "...", " ": " ", " ": " ", " ": " ",
    "​": "", "­": "",
}


def normalise(text: str) -> str:
    """Canonical form for substring comparison.

    Whitespace is collapsed, typographic punctuation is folded to ASCII, and a
    hyphen at a line break is removed along with the break, because PDF text
    extraction preserves the hyphen a layout engine inserted mid-word.

    Case is preserved on purpose. "Verbatim" is the promise the report makes
    about every quote it prints, and lowercasing would quietly weaken it.
    """
    s = unicodedata.normalize("NFKC", str(text))
    for bad, good in _PUNCT.items():
        s = s.replace(bad, good)
    # A hyphen followed by a line break is hyphenation, not a real hyphen.
    s = re.sub(r"-[ \t]*\r?\n[ \t]*", "", s)
    return re.sub(r"\s+", " ", s).strip()


def contains(haystack: str, needle: str | None) -> bool:
    """Is ``needle`` present in ``haystack``, verbatim after normalisation?

    A blank needle is never contained: an empty quote is not evidence.
    """
    if needle is None:
        return False
    n = normalise(needle)
    if not n:
        return False
    return n in normalise(haystack)


def _ci_contains(haystack: str, needle: str | None) -> bool:
    """Case-insensitive containment, for text the model wrote rather than quoted."""
    if not needle:
        return False
    return normalise(needle).lower() in normalise(haystack).lower()


# ---------------------------------------------------------------------------
# Injection detection
# ---------------------------------------------------------------------------

#: Text in a CV or posting that addresses the reading system instead of a
#: person. Finding it is an `info` flag and a line in the report; it never
#: changes a status. About 1% of real resumes carry something like this, and in
#: the user's own CV it is usually a template leftover.
_INJECTION = [
    r"\bignore\s+(all\s+)?(the\s+)?(previous|prior|preceding|above|earlier)\s+(instruction|prompt|direction|rule)s?\b",
    r"\bdisregard\s+(all\s+)?(the\s+)?(previous|prior|preceding|above|earlier)\s+(instruction|prompt|direction|rule)s?\b",
    r"\bforget\s+(all\s+)?(the\s+)?(previous|prior|above)\s+(instruction|prompt)s?\b",
    r"\bignorez\s+(toutes\s+)?(les\s+)?(instructions|consignes|directives)\b",
    r"\boubliez\s+(toutes\s+)?(les\s+)?(instructions|consignes)\b",
    r"\brate\s+this\s+(candidate|applicant|resume|cv)\b",
    r"\b(score|rank)\s+this\s+(candidate|applicant|resume|cv)\b",
    r"\bthis\s+candidate\s+is\s+(a\s+)?(perfect|ideal|the\s+best)\b",
    r"\byou\s+(are|must\s+act)\s+as\s+an?\s+(ai|assistant|language\s+model|recruiter|ats)\b",
    r"^\s*(system|assistant)\s*:\s*\S",
    r"\bnew\s+instructions?\s*:\s*\S",
]

_INJECTION_RE = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in _INJECTION]


def _fold_accents(text: str) -> str:
    s = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in s if not unicodedata.combining(c))


def find_injection(text: str) -> list[str]:
    """Return the matched injection snippets, empty when there are none."""
    folded = _fold_accents(normalise(text))
    hits: list[str] = []
    for rx in _INJECTION_RE:
        for m in rx.finditer(folded):
            snippet = m.group(0).strip()
            if snippet not in hits:
                hits.append(snippet)
    return hits


# ---------------------------------------------------------------------------
# The schema edge
# ---------------------------------------------------------------------------


def check_schema(contract: str, data: Any) -> list[str]:
    return contracts.validate(contract, data)


# ---------------------------------------------------------------------------
# The reference edge
# ---------------------------------------------------------------------------


def check_references(requirements: dict, evidence: dict) -> list[str]:
    """Every requirement has exactly one finding, and every id resolves.

    Without this, a requirement can quietly vanish between S1 and S2 and the
    verdict is computed over a smaller posting than the one the user pasted.
    """
    problems: list[str] = []

    req_ids: list[str] = [r["id"] for r in requirements.get("requirements", [])]
    for rid in sorted({i for i in req_ids if req_ids.count(i) > 1}):
        problems.append(f"requirements: duplicate requirement id {rid}")
    req_set = set(req_ids)

    pos_ids = [p["id"] for p in evidence.get("positions", [])]
    for pid in sorted({i for i in pos_ids if pos_ids.count(i) > 1}):
        problems.append(f"evidence: duplicate position id {pid}")
    pos_set = set(pos_ids)

    seen: dict[str, int] = {}
    for finding in evidence.get("findings", []):
        rid = finding.get("requirement_id")
        seen[rid] = seen.get(rid, 0) + 1
        if rid not in req_set:
            problems.append(f"evidence: finding refers to unknown requirement {rid}")
        for pid in finding.get("position_ids") or []:
            if pid not in pos_set:
                problems.append(f"evidence: finding {rid} refers to unknown position {pid}")

    for rid, n in sorted(seen.items(), key=lambda kv: str(kv[0])):
        if n > 1:
            problems.append(f"evidence: requirement {rid} has a finding more than once ({n})")
    for rid in req_ids:
        if rid not in seen:
            problems.append(f"evidence: requirement {rid} has no finding")

    return problems


# ---------------------------------------------------------------------------
# The quote edge
# ---------------------------------------------------------------------------


def check_posting_quotes(requirements: dict, posting_text: str) -> list[str]:
    """Every requirement's ``source_quote`` must really be in the posting.

    This is the check that catches a requirement the model inferred from the
    job title or from its own idea of the role rather than read off the page.
    """
    problems: list[str] = []
    for req in requirements.get("requirements", []):
        if not contains(posting_text, req.get("source_quote")):
            problems.append(
                f"{req.get('id')}: source_quote is not in the posting text "
                f"({(req.get('source_quote') or '')[:60]!r})"
            )
    return problems


_NEEDS_QUOTE = ("met", "partial")


def _add_flag(doc: dict, code: str, detail: str, source_quote: str | None) -> None:
    flag = {"code": code, "detail": detail, "source_quote": source_quote}
    flags = doc.setdefault("flags", [])
    if flag not in flags:
        flags.append(flag)


def apply_quote_edge(evidence: dict, cv_text: str) -> tuple[dict, list[dict]]:
    """Verify every quote against the CV and downgrade what cannot be found.

    Returns an amended copy of ``evidence`` and the list of downgrades, which
    the report prints so the user can see where the agent stopped trusting its
    own reading. The input is not mutated, and running the edge twice changes
    nothing the second time.
    """
    out = copy.deepcopy(evidence)
    downgrades: list[dict] = []

    for finding in out.get("findings", []):
        rid = finding.get("requirement_id")
        status = finding.get("status")
        quote = finding.get("evidence_quote")

        if status in _NEEDS_QUOTE:
            if quote is None or not normalise(str(quote)):
                finding["status"] = "ambiguous"
                downgrades.append({
                    "requirement_id": rid, "from": status, "to": "ambiguous",
                    "why": f"status was {status} with no evidence quote",
                })
            elif not contains(cv_text, quote):
                finding["status"] = "ambiguous"
                downgrades.append({
                    "requirement_id": rid, "from": status, "to": "ambiguous",
                    "why": "evidence quote was not found in the CV text",
                })
                _add_flag(out, "unverifiable_claim",
                          f"{rid}: the evidence quote is not in the CV text", str(quote))
        elif quote is not None and normalise(str(quote)) and not contains(cv_text, quote):
            # Nothing to downgrade, but a quote that is not in the CV is still
            # a fabricated quote, and the report should say so.
            _add_flag(out, "unverifiable_claim",
                      f"{rid}: a {status} finding carries a quote that is not in the CV text",
                      str(quote))

    for pos in out.get("positions", []):
        if not contains(cv_text, pos.get("source_quote")):
            _add_flag(out, "unverifiable_claim",
                      f"{pos.get('id')}: the position's source_quote is not in the CV text",
                      str(pos.get("source_quote")))

    return out, downgrades


# ---------------------------------------------------------------------------
# The honesty edge (design D7)
# ---------------------------------------------------------------------------

#: Advice that is deceptive however it is framed. These are refusals in the
#: skill; the edge is the backstop that catches them if the prose slips.
_DECEPTIVE = [
    (r"\bwhite\s+(text|font|lettering)\b", "advises white text"),
    (r"\bhidden\s+(text|keywords?)\b", "advises hidden text"),
    (r"\binvisible\s+(text|keywords?)\b", "advises invisible text"),
    (r"\bfont\s+colou?r\s+to\s+white\b", "advises white text"),
    (r"\b(tiny|1\s*pt|one\s*point)\s+(font|text)\b", "advises unreadably small text"),
    (r"\bkeyword\s+stuff", "advises keyword stuffing"),
    (r"\bsay\s+you\s+(have|hold|are|were)\b", "tells the candidate to say something unconditionally"),
    (r"\bclaim\s+(you|to\s+have)\b", "tells the candidate to claim something"),
]

_DECEPTIVE_RE = [(re.compile(p, re.IGNORECASE), why) for p, why in _DECEPTIVE]

#: Only legitimate inside a conditional ``ask``: a credential that does not
#: exist yet cannot be listed as in progress on the strength of our guess.
_CONDITIONAL_ONLY = [
    (r"\bin\s+progress\b", "describes a credential as in progress"),
    (r"\bexpected\s+(completion|20\d\d)\b", "gives an expected completion"),
    (r"\ben\s+cours\b", "describes a credential as in progress"),
]

_CONDITIONAL_ONLY_RE = [(re.compile(p, re.IGNORECASE), why) for p, why in _CONDITIONAL_ONLY]

#: Words that are capitalised for reasons other than being a proper noun, so
#: they are not evidence of an invented employer or product.
_CAP_STOP = {
    "I", "I'm", "I've", "A", "An", "The", "If", "Your", "You", "It", "This",
    "That", "These", "Those", "And", "But", "Or", "So", "For", "To", "In", "On",
    "At", "As", "Be", "By", "No", "Not", "Add", "Put", "Say", "Move", "Use",
    "Mention", "List", "Name", "Keep", "Make", "Ask", "Note", "Consider",
    "CV", "ATS", "Experience", "Education", "Skills", "Certifications",
    "Summary", "Profile", "Languages", "Present", "Current", "Required",
    "Preferred", "Section", "Header", "Footer", "Monday", "Tuesday",
    "Wednesday", "Thursday", "Friday", "January", "February", "March",
    "April", "May", "June", "July", "August", "September", "October",
    "November", "December",
}

#: Words that carry no claim, so they are dropped when a requirement's text is
#: reduced to the terms that would be a lie to borrow.
_TERM_STOP = {
    "a", "an", "and", "or", "the", "of", "in", "on", "at", "to", "with", "for",
    "years", "year", "yrs", "experience", "experienced", "strong", "proven",
    "solid", "deep", "hands", "hands-on", "working", "knowledge", "ability",
    "able", "must", "have", "has", "plus", "required", "preferred", "nice",
    "familiarity", "familiar", "understanding", "skills", "skill", "using",
    "use", "including", "such", "etc", "equivalent", "related", "field",
    "degree", "minimum", "least", "more", "demonstrated", "excellent", "good",
    "ans", "experiences", "connaissance", "maitrise", "des", "les", "une",
    "dans", "avec", "pour", "est", "sur", "par",
}


#: Spellings of the same thing. Pairing an acronym with its full form is the
#: one keyword change design D7 allows, because it adds no claim: if the CV
#: says "K8s", telling the candidate to also write "Kubernetes" is truthful.
#: Without this table the honesty edge rejects exactly the advice the design
#: says to give.
#:
#: The list is curated on purpose and stays short. A general initials rule
#: would quietly admit the false friends the eval set exists to catch, so
#: Java/JavaScript and MySQL/SQL Server are deliberately absent: those are
#: different products, not two spellings.
_EQUIVALENTS: list[set[str]] = [
    {"kubernetes", "k8s"},
    {"postgresql", "postgres", "psql"},
    {"javascript", "js", "ecmascript"},
    {"typescript", "ts"},
    {"aws", "amazon web services"},
    {"gcp", "google cloud platform", "google cloud"},
    {"azure", "microsoft azure"},
    {"ci", "continuous integration"},
    {"cd", "continuous delivery", "continuous deployment"},
    {"iac", "infrastructure as code"},
    {"ml", "machine learning"},
    {"nlp", "natural language processing"},
    {"node", "nodejs", "node.js"},
    {"golang", "go"},
    {"csharp", "c#", "c sharp"},
    {"sql", "structured query language"},
    {"gha", "github actions"},
    {"cka", "certified kubernetes administrator"},
    {"oiq", "ordre des ingenieurs du quebec", "ordre des ingénieurs du québec"},
    {"k8s cluster", "kubernetes cluster"},
]


def _equivalent_forms(term: str) -> set[str]:
    """Every spelling of ``term`` that means the same thing, including itself."""
    key = term.strip().lower()
    forms = {key}
    for group in _EQUIVALENTS:
        if key in group:
            forms |= group
    return forms


def _mentioned(text: str, term: str) -> bool:
    """Is ``term``, or any equivalent spelling of it, in ``text``?"""
    folded = _fold_accents(normalise(text)).lower()
    for form in _equivalent_forms(term):
        pattern = r"\b" + re.escape(_fold_accents(form).lower()) + r"\b"
        if re.search(pattern, folded):
            return True
    return False


def _claim_terms(requirements: dict) -> list[str]:
    """The distinctive terms a posting asks for, as lowercase tokens.

    Borrowing one of these into a reframe is exactly the failure mode D7 is
    written against: the posting says "AWS Certified", the CV says nothing, and
    a helpful-sounding reframe hands the candidate a sentence that is a lie.
    """
    terms: list[str] = []
    for req in requirements.get("requirements", []):
        for raw in re.findall(r"[A-Za-z][A-Za-z0-9+#.]*", str(req.get("text", ""))):
            t = raw.lower()
            if len(t) < 3 or t in _TERM_STOP or t.isdigit():
                continue
            if t not in terms:
                terms.append(t)
    return terms


def _sentence_initial_spans(text: str) -> list[int]:
    """Offsets where a sentence begins, so the capital there proves nothing."""
    starts = [0]
    for m in re.finditer(r"""[.!?]['")\]]*\s+""", text):
        starts.append(m.end())
    return starts


def _unsupported_claims(text: str, cv_text: str, terms: list[str]) -> list[str]:
    """Claim-bearing tokens in ``text`` that the CV does not support."""
    found: list[str] = []
    norm_cv = normalise(cv_text)
    lower_cv = norm_cv.lower()

    # Dates. A year the CV never mentions is an invented one.
    for m in re.finditer(r"\b((?:19|20)\d{2})(-\d{2})?\b", text):
        token = m.group(0)
        if token not in norm_cv and m.group(1) not in norm_cv and token not in found:
            found.append(token)

    # Terms the posting asks for but the CV never evidences. An equivalent
    # spelling counts: "Kubernetes" is supported by a CV that says "K8s".
    for term in terms:
        if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
            if not _mentioned(cv_text, term) and term not in found:
                found.append(term)

    # Proper nouns: an employer, product or school we were never told about.
    starts = set(_sentence_initial_spans(text))
    for m in re.finditer(r"\b[A-Z][A-Za-z0-9+#.&/-]{1,}\b", text):
        word = m.group(0)
        if m.start() in starts or word in _CAP_STOP:
            continue
        if word.lower() in found:
            continue
        if not _mentioned(cv_text, word) and word not in found:
            found.append(word)

    return found


def check_honesty(recommendations: dict, cv_text: str, requirements: dict) -> list[str]:
    """The deterministic form of "never advise adding what the CV cannot show".

    Per design D7 the claim check applies to ``reframe``, because that is the
    kind that puts words in the candidate's CV. A ``gap`` is allowed to name
    the thing that is missing, and an ``ask`` is allowed to name it inside a
    condition, as long as the condition is actually in the sentence the user
    reads.
    """
    problems: list[str] = []
    recs = recommendations.get("recommendations", [])
    req_ids = {r["id"] for r in requirements.get("requirements", [])}
    terms = _claim_terms(requirements)

    ids = [r.get("id") for r in recs]
    for dup in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        problems.append(f"{dup}: duplicate recommendation id")

    for rec in recs:
        cid = rec.get("id")
        kind = rec.get("kind")
        text = str(rec.get("text") or "")
        rid = rec.get("requirement_id")
        where = f"{cid} ({kind})"

        if kind != "format":
            if rid is None:
                problems.append(f"{where}: requirement_id is required for every kind except format")
            elif rid not in req_ids:
                problems.append(f"{where}: refers to unknown requirement {rid}")

        for rx, why in _DECEPTIVE_RE:
            if rx.search(text):
                problems.append(f"{where}: {why}")

        if kind != "ask":
            for rx, why in _CONDITIONAL_ONLY_RE:
                if rx.search(text):
                    problems.append(f"{where}: {why}, which only a conditional ask may do")

        if kind == "reframe":
            quote = rec.get("evidence_quote")
            if not quote:
                problems.append(f"{where}: a reframe must cite an evidence_quote")
            elif not contains(cv_text, quote):
                problems.append(f"{where}: evidence_quote is not in the CV text")
            for claim in _unsupported_claims(text, cv_text, terms):
                problems.append(f"{where}: mentions {claim!r}, which is not in the CV")

        if kind == "ask":
            condition = rec.get("condition")
            if not condition:
                problems.append(f"{where}: an ask must carry a condition")
            elif not _ci_contains(text, condition):
                problems.append(f"{where}: the condition is missing from the text the user reads")

    return problems


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        _die(f"{path}: no such file")
    except json.JSONDecodeError as exc:
        _die(f"{path}: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}")


def _load_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        _die(f"{path}: no such file")


def _die(message: str) -> None:
    print(f"edge failed: {message}", file=sys.stderr)
    raise SystemExit(2)


def _report(label: str, problems: list[str]) -> int:
    if not problems:
        print(f"{label}: ok")
        return 0
    print(f"{label}: {len(problems)} problem(s)")
    for p in problems:
        print(f"  - {p}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="edges.py",
        description="Deterministic checks between the pipeline's model steps.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_schema = sub.add_parser("schema", help="validate a step's JSON against its contract")
    p_schema.add_argument("contract", choices=contracts.STEP_ORDER)
    p_schema.add_argument("path")

    p_refs = sub.add_parser("references", help="check ids line up across the two model steps")
    p_refs.add_argument("--requirements", required=True)
    p_refs.add_argument("--evidence", required=True)

    p_quotes = sub.add_parser("quotes", help="verify evidence quotes and downgrade what is not found")
    p_quotes.add_argument("--evidence", required=True)
    p_quotes.add_argument("--cv", required=True)
    p_quotes.add_argument("--out", required=True)
    p_quotes.add_argument("--downgrades", help="optional path for the downgrade list")

    p_posting = sub.add_parser("posting-quotes", help="verify requirement source quotes against the posting")
    p_posting.add_argument("--requirements", required=True)
    p_posting.add_argument("--posting", required=True)

    p_honesty = sub.add_parser("honesty", help="check recommendations add no unevidenced claim")
    p_honesty.add_argument("--recommendations", required=True)
    p_honesty.add_argument("--cv", required=True)
    p_honesty.add_argument("--requirements", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "schema":
        return _report(f"schema/{args.contract}", check_schema(args.contract, _load_json(args.path)))

    if args.cmd == "references":
        return _report("references", check_references(_load_json(args.requirements), _load_json(args.evidence)))

    if args.cmd == "posting-quotes":
        return _report("posting-quotes", check_posting_quotes(_load_json(args.requirements), _load_text(args.posting)))

    if args.cmd == "quotes":
        amended, downgrades = apply_quote_edge(_load_json(args.evidence), _load_text(args.cv))
        Path(args.out).write_text(json.dumps(amended, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if args.downgrades:
            Path(args.downgrades).write_text(json.dumps(downgrades, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if downgrades:
            print(f"quotes: {len(downgrades)} downgrade(s)")
            for d in downgrades:
                print(f"  - {d['requirement_id']}: {d['from']} -> {d['to']} ({d['why']})")
        else:
            print("quotes: ok, every quote was found")
        # Downgrades are a finding, not a failure: the run continues with the
        # weaker status, which is the whole point of having the edge.
        return 0

    if args.cmd == "honesty":
        return _report("honesty", check_honesty(
            _load_json(args.recommendations), _load_text(args.cv), _load_json(args.requirements)
        ))

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
