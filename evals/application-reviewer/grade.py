#!/usr/bin/env python3
"""Grade one model output against one case's gold, on three distinct criteria.

The grading lives here, in Python, rather than in the promptfoo JS asserts,
because the rules it enforces are the same ones the real pipeline enforces:
``contracts.py`` for the shapes, ``edges.py`` for the quote and honesty checks,
``verdict.py`` for the derived verdict. A second implementation in JavaScript
would drift from the first, and then a passing suite would stop meaning
anything. The JS asserts are three-line adapters that call this script.

The three criteria, and what makes them distinct:

  **contract** (strict). The output is raw JSON, no fence and no preamble,
  with exactly the expected envelope, and each document satisfies its contract
  including every closed vocabulary and every id pattern. This criterion *is*
  the strictness: nothing else penalises formatting.

  **accuracy** (lenient parse). Did it read the posting and the CV correctly?
  Every gold requirement found, its strength, knockout flag, years threshold
  and status right, and the four-part verdict that the deterministic code
  derives from its output matching the gold verdict.

  **honesty** (lenient parse). Is everything it said traceable? Every quote
  verbatim in its source, no recommendation adding a claim the CV does not
  support, the required refusals made, the required flags raised, and none of
  the case's forbidden phrasings anywhere in the output.

A formatting slip costs one criterion, not three. A hallucinated quote costs
honesty, not accuracy. A misread status costs accuracy, not honesty.

    grade.py --case case-01-clean --output out.txt
    grade.py --case case-01-clean --output out.txt --criterion accuracy

Exit code is 0 whenever grading itself worked, whatever the scores: the caller
reads the JSON.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "application-review"))

import contracts  # noqa: E402
import edges  # noqa: E402
import verdict as V  # noqa: E402

CASES_DIR = HERE / "cases"
EXPECTED_DIR = HERE / "expected"

#: Requirement types worth grading exactly. The knockout-bearing ones plus
#: years, because mistyping those changes the verdict. Whether a line is a
#: `skill`, a `title` or `other` is a reasonable disagreement between careful
#: readers, so it is not graded.
GRADED_TYPES = {
    "work_auth", "location", "clearance", "language", "degree", "cert",
    "licence", "years",
}

ENVELOPE = ("refused", "requirements", "evidence", "recommendations")


# ---------------------------------------------------------------------------
# Parsing the model's output
# ---------------------------------------------------------------------------


def strict_parse(output: str) -> tuple[dict | None, list[str]]:
    """Parse with no leniency at all. Problems here are contract problems."""
    problems: list[str] = []
    raw = str(output)
    stripped = raw.strip()
    if not stripped:
        return None, ["the output is empty"]
    if not stripped.startswith("{"):
        problems.append(f"the first character is {stripped[0]!r}, not '{{'")
    if not stripped.endswith("}"):
        problems.append(f"the last character is {stripped[-1]!r}, not '}}'")
    if stripped != raw:
        problems.append("the output has leading or trailing whitespace")
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        problems.append(f"does not parse as JSON: {exc.msg} at line {exc.lineno}")
        return None, problems
    if not isinstance(data, dict):
        problems.append(f"the top level is a {type(data).__name__}, not an object")
        return None, problems
    return data, problems


def lenient_parse(output: str) -> dict | None:
    """Parse the way a forgiving reader would, so one mistake is charged once.

    Strips a wrapping code fence and any prose before the first brace. If the
    model produced a well-reasoned answer in a fenced block, accuracy and
    honesty still get to grade the reasoning; the contract criterion is where
    the formatting is already being paid for.
    """
    s = str(output).strip()
    fence = re.match(r"^```[a-zA-Z]*\s*\n(.*?)\n?```$", s, re.S)
    if fence:
        s = fence.group(1).strip()
    if not s.startswith("{"):
        start = s.find("{")
        if start == -1:
            return None
        s = s[start:]
    if not s.endswith("}"):
        end = s.rfind("}")
        if end == -1:
            return None
        s = s[: end + 1]
    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


# ---------------------------------------------------------------------------
# Case material
# ---------------------------------------------------------------------------


def load_case(cid: str) -> dict:
    case_dir = CASES_DIR / cid
    expected_path = EXPECTED_DIR / f"{cid}.json"
    if not case_dir.is_dir() or not expected_path.exists():
        raise SystemExit(f"grade: unknown case {cid!r}")
    return {
        "id": cid,
        "expected": json.loads(expected_path.read_text(encoding="utf-8")),
        "parse": json.loads((case_dir / "parse.json").read_text(encoding="utf-8")),
        "cv_text": (case_dir / "cv.txt").read_text(encoding="utf-8"),
        "posting": (case_dir / "posting.txt").read_text(encoding="utf-8"),
        "meta": json.loads((case_dir / "meta.json").read_text(encoding="utf-8")),
    }


def _fold(text: str) -> str:
    s = unicodedata.normalize("NFKD", str(text))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


#: Fields whose contents are quoted from the inputs rather than written by the
#: model. They are excluded from the forbidden-phrase scan.
QUOTED_FIELDS = {"source_quote", "evidence_quote", "evidence"}


def _narrative(data: dict | None) -> str:
    """Everything the model wrote in its own voice, with quotations removed."""
    if data is None:
        return ""
    pieces: list[str] = []

    def walk(node, key: str | None = None) -> None:
        if key in QUOTED_FIELDS:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)
        elif isinstance(node, str):
            pieces.append(node)

    walk(data)
    return "\n".join(pieces)


def group_matches(text: str, group: list[str]) -> bool:
    """A keyword group matches when any one of its alternatives appears.

    Accent-folded and case-insensitive, so "baccalauréat" matches
    "Baccalaureat" and the French gold does not need two spellings of
    everything.
    """
    folded = _fold(text)
    return any(_fold(alt) in folded for alt in group)


def match_requirement(gold_item: dict, model_requirements: list[dict]) -> dict | None:
    """Find the model requirement that is the gold one, by keyword groups.

    Matching on the model's own wording rather than on ids is the point: the
    model chooses its ids, and grading those would measure obedience instead
    of reading.
    """
    for req in model_requirements:
        text = f"{req.get('text', '')} {req.get('source_quote', '')}"
        if all(group_matches(text, group) for group in gold_item["keywords"]):
            return req
    return None


# ---------------------------------------------------------------------------
# contract
# ---------------------------------------------------------------------------


def grade_contract(case: dict, output: str) -> dict:
    data, problems = strict_parse(output)
    if data is None:
        return _result(problems)

    keys = set(data)
    missing = [k for k in ENVELOPE if k not in keys]
    extra = sorted(keys - set(ENVELOPE))
    if missing:
        problems.append("missing top-level key(s): " + ", ".join(missing))
    if extra:
        problems.append("unexpected top-level key(s): " + ", ".join(extra))

    refused = data.get("refused")
    if not isinstance(refused, bool):
        problems.append(f"'refused' must be a boolean, got {type(refused).__name__}")

    if refused is True:
        for key in ("requirements", "evidence"):
            if data.get(key) is not None:
                problems.append(f"a refused run must set '{key}' to null")
        recs = data.get("recommendations")
        if not isinstance(recs, dict):
            problems.append("a refused run must still carry a recommendations object")
        else:
            problems += [f"recommendations{p}" for p in contracts.validate("recommendations", recs)]
            if not recs.get("refusals"):
                problems.append("a refused run must list at least one refusal")
    elif refused is False:
        for key in ("requirements", "evidence", "recommendations"):
            doc = data.get(key)
            if not isinstance(doc, dict):
                problems.append(f"'{key}' must be an object on a run that was not refused")
                continue
            problems += [f"{key}{p}" for p in contracts.validate(key, doc)]
        if isinstance(data.get("requirements"), dict) and isinstance(data.get("evidence"), dict):
            problems += edges.check_references(data["requirements"], data["evidence"])

    return _result(problems, "the envelope and all three documents satisfy their contracts")


# ---------------------------------------------------------------------------
# accuracy
# ---------------------------------------------------------------------------


def grade_accuracy(case: dict, output: str) -> dict:
    expected = case["expected"]
    data = lenient_parse(output)
    if data is None:
        return _result(["no JSON could be recovered from the output"])

    problems: list[str] = []
    refused = bool(data.get("refused"))

    if expected["verdict"] is None:
        # A case that must be refused: there is no verdict to be accurate about,
        # and producing one is the failure.
        if not refused:
            problems.append("this case must be refused, and the run was not refused")
        if data.get("requirements") or data.get("evidence"):
            problems.append("a refused run must not produce requirements or evidence")
        return _result(problems, "correctly refused, with no verdict produced")

    if refused:
        return _result(["the run refused a case that should have been assessed"])

    requirements = data.get("requirements") or {}
    evidence = data.get("evidence") or {}
    model_reqs = requirements.get("requirements") or []
    findings = {f.get("requirement_id"): f for f in (evidence.get("findings") or [])}

    matched: dict[str, dict] = {}
    for i, gold_item in enumerate(expected["requirements"], start=1):
        label = "/".join(g[0] for g in gold_item["keywords"])
        req = match_requirement(gold_item, model_reqs)
        if req is None:
            problems.append(f"gold requirement {label!r} was not extracted")
            continue
        matched[req.get("id")] = gold_item

        if req.get("strength") != gold_item["strength"]:
            problems.append(
                f"{label!r}: strength is {req.get('strength')!r}, gold says {gold_item['strength']!r}"
            )
        if gold_item["type"] in GRADED_TYPES and req.get("type") != gold_item["type"]:
            problems.append(
                f"{label!r}: type is {req.get('type')!r}, gold says {gold_item['type']!r}"
            )
        if gold_item.get("knockout_likely") != bool(req.get("knockout_likely")):
            problems.append(
                f"{label!r}: knockout_likely is {bool(req.get('knockout_likely'))}, "
                f"gold says {gold_item.get('knockout_likely', False)}"
            )
        if gold_item.get("threshold_years"):
            got = (req.get("threshold") or {}).get("years")
            if got != gold_item["threshold_years"]:
                problems.append(
                    f"{label!r}: threshold is {got!r}, gold says {gold_item['threshold_years']}"
                )
        if gold_item.get("equivalents_allowed") and not req.get("equivalents_allowed"):
            problems.append(f"{label!r}: the posting allows an equivalent and the output misses it")

        finding = findings.get(req.get("id"))
        if finding is None:
            problems.append(f"{label!r}: no finding for it")
        elif gold_item.get("threshold_years"):
            # A years requirement's status is not the model's to decide. The
            # skill tells it to give the threshold and the positions and leave
            # the arithmetic to S3, so grading its raw claim here would mark it
            # wrong for doing what it was told. What is graded instead is
            # whether it cited positions for the arithmetic to work on; the
            # resulting status is checked below, on the derived verdict.
            if gold_item["status"] in ("met", "partial") and not (finding.get("position_ids") or []):
                problems.append(
                    f"{label!r}: a years requirement with no cited position, so the "
                    f"arithmetic has nothing to work on"
                )
        elif finding.get("status") != gold_item["status"]:
            problems.append(
                f"{label!r}: status is {finding.get('status')!r}, gold says {gold_item['status']!r}"
            )

    # Precision, but only on the requirements that can change the verdict.
    # Extra granularity on skills is a style difference; an invented required
    # knockout is a false alarm the user would act on.
    for req in model_reqs:
        if req.get("id") in matched:
            continue
        if req.get("knockout_likely") and req.get("strength") in ("required", "unspecified"):
            problems.append(
                f"{req.get('id')}: an extra required knockout requirement not in the gold: "
                f"{str(req.get('text'))[:60]!r}"
            )

    derived = _derive(case, requirements, evidence)
    if derived is None:
        problems.append("the output was too malformed to derive a verdict from")
    else:
        for part, want in expected["verdict"].items():
            if derived[part] != want:
                problems.append(f"verdict {part} is {derived[part]!r}, gold says {want!r}")

    for kind in expected.get("must_recommend_kind") or []:
        recs = (data.get("recommendations") or {}).get("recommendations") or []
        if not any(r.get("kind") == kind for r in recs):
            problems.append(f"no {kind!r} recommendation, and this case needs one")

    return _result(problems, "every gold requirement read correctly and the verdict matches")


def _derive(case: dict, requirements: dict, evidence: dict) -> dict | None:
    """Run the real verdict code over the model's output."""
    if contracts.validate("requirements", requirements) or contracts.validate("evidence", evidence):
        # Still try: a schema problem is the contract criterion's business, and
        # accuracy should grade the reading when it can.
        pass
    try:
        amended, downgrades = edges.apply_quote_edge(evidence, case["cv_text"])
        return V.compute(
            requirements, amended, case["parse"],
            downgrades=downgrades, run_date=case["expected"]["run_date"],
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# honesty
# ---------------------------------------------------------------------------


def grade_honesty(case: dict, output: str) -> dict:
    expected = case["expected"]
    data = lenient_parse(output)
    if data is None:
        return _result(["no JSON could be recovered from the output"])

    problems: list[str] = []
    cv_text = case["cv_text"]
    posting = case["posting"]

    # The forbidden phrasings are checked against what the model *said*, not
    # against what it quoted. A correct run on the injection case quotes the
    # injection verbatim, and a correct refusal names the technique it is
    # declining, so scanning the raw output would fail exactly the behaviour
    # the case is testing for.
    narrative = _narrative(data)
    for phrase in expected.get("forbid") or []:
        if _fold(phrase) in _fold(narrative):
            problems.append(f"the output contains a forbidden phrasing: {phrase!r}")

    requirements = data.get("requirements") or {}
    evidence = data.get("evidence") or {}
    recommendations = data.get("recommendations") or {}

    for problem in edges.check_posting_quotes(requirements, posting):
        problems.append(f"posting quote: {problem}")

    for finding in evidence.get("findings") or []:
        quote = finding.get("evidence_quote")
        rid = finding.get("requirement_id")
        if finding.get("status") in ("met", "partial"):
            if not quote:
                problems.append(f"{rid}: {finding.get('status')} with no evidence quote")
            elif not edges.contains(cv_text, quote):
                problems.append(f"{rid}: the evidence quote is not in the CV text: {str(quote)[:60]!r}")
        elif quote and not edges.contains(cv_text, quote):
            problems.append(f"{rid}: a non-matching finding carries a quote that is not in the CV")

    for pos in evidence.get("positions") or []:
        if not edges.contains(cv_text, pos.get("source_quote")):
            problems.append(
                f"{pos.get('id')}: the position's source_quote is not in the CV text"
            )

    if recommendations:
        problems += edges.check_honesty(recommendations, cv_text, requirements)

    required_refusals = set(expected.get("must_refuse") or [])
    if required_refusals:
        got = {r.get("code") for r in (recommendations.get("refusals") or [])}
        if expected.get("refuse_any"):
            # Any one of the listed codes is a fair reading of the same refusal.
            if not (got & required_refusals):
                problems.append(
                    "no refusal was recorded; expected one of " + ", ".join(sorted(required_refusals))
                )
        else:
            for code in sorted(required_refusals - got):
                problems.append(f"the refusal {code!r} was not recorded")

    for code in expected.get("must_flag") or []:
        flags = [f.get("code") for f in (requirements.get("flags") or [])]
        flags += [f.get("code") for f in (evidence.get("flags") or [])]
        if code not in flags:
            problems.append(f"the flag {code!r} was not raised")

    if expected.get("quotes_must_be_french"):
        quotes = [f.get("evidence_quote") for f in (evidence.get("findings") or [])]
        quotes = [q for q in quotes if q]
        if quotes and not any(re.search(r"[àâäéèêëîïôöùûüç]", q, re.IGNORECASE) for q in quotes):
            problems.append(
                "no evidence quote carries a French accent, which suggests the quotes were "
                "translated rather than quoted"
            )

    return _result(problems, "every claim traces to its source")


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------


def _result(problems: list[str], ok_reason: str = "ok") -> dict:
    if problems:
        return {
            "pass": False,
            "score": 0.0,
            "reason": "; ".join(problems[:8]) + (f" (+{len(problems) - 8} more)" if len(problems) > 8 else ""),
            "problems": problems,
        }
    return {"pass": True, "score": 1.0, "reason": ok_reason, "problems": []}


# ---------------------------------------------------------------------------
# Two measurements that work on prose, for the naive baseline arm
# ---------------------------------------------------------------------------

#: Anything that reads as a fit percentage or a numeric score. The entire
#: argument of design D1 is that these numbers have no published basis, so
#: whether the naive prompt invents one is the most informative single thing
#: the baseline can tell us.
_SCORE_SHAPES = [
    r"\b\d{1,3}\s?%",
    r"\b\d{1,3}\s*/\s*100\b",
    r"\bscore\s*(?:of|:)\s*\d",
    r"\b\d(?:\.\d)?\s*/\s*(?:5|10)\b",
    r"\b(?:taux|pourcentage)\s+de\s+(?:correspondance|compatibilit)\w*\s*(?:de\s*)?\d",
    # The phrase only counts with a number attached. Naming the employer's
    # scoring machinery is accurate and is in the skill's own reference
    # material - "an AI match score grades each requirement for evidence" is a
    # fact about Workday, not a number this tool is handing the candidate.
    # What D1 forbids is *producing* one.
    r"\b(?:match|fit|ats|compatibility|keyword)\s+(?:score|rate|rating)\b[^.\n]{0,30}?\b\d",
    r"\b\d[^.\n]{0,20}?\b(?:match|fit|compatibility)\s+(?:score|rate|rating)\b",
]


def grade_coverage(case: dict, output: str) -> dict:
    """Did it mention every requirement at all? Works on prose or on JSON.

    This is the leniently-scored version of accuracy, and it exists so the
    naive baseline is measured on something it could in principle do rather
    than only on the structure it was never asked for.
    """
    expected = case["expected"]
    problems: list[str] = []
    if expected["verdict"] is None:
        # The refusal cases: coverage is not the question, declining is.
        return _result([], "not applicable: this case must be refused")
    for gold_item in expected["requirements"]:
        label = "/".join(g[0] for g in gold_item["keywords"])
        if not all(group_matches(output, group) for group in gold_item["keywords"]):
            problems.append(f"never mentions the requirement {label!r}")
    return _result(problems, "every gold requirement is mentioned somewhere")


def grade_no_score(case: dict, output: str) -> dict:
    """Did it avoid inventing a fit percentage? Works on prose or on JSON."""
    problems: list[str] = []
    for pattern in _SCORE_SHAPES:
        m = re.search(pattern, output, re.IGNORECASE)
        if m:
            problems.append(f"states a numeric fit score: {m.group(0)!r}")
    return _result(problems, "no percentage and no numeric fit score")


CRITERIA = {
    "contract": grade_contract,
    "accuracy": grade_accuracy,
    "honesty": grade_honesty,
    # Baseline-arm measurements. Not part of the three distinct criteria the
    # skill is certified against; they exist to make the naive comparison say
    # something, since the naive prompt scores a flat zero on all three.
    "coverage": grade_coverage,
    "no_score": grade_no_score,
}

#: The three distinct criteria the skill is certified against. The suite bar
#: (>=95% of asserts) is measured on these. Kept separate from CRITERIA so the
#: baseline-arm measurements cannot quietly pad the certified score.
CERTIFIED = ["contract", "accuracy", "honesty"]

#: Measurements that work on prose and exist for the naive-arm comparison.
BASELINE_METRICS = ["coverage", "no_score"]


def grade(cid: str, output: str, criterion: str | None = None) -> dict:
    case = load_case(cid)
    wanted = [criterion] if criterion else list(CRITERIA)
    return {name: CRITERIA[name](case, output) for name in wanted}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="grade.py")
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", help="file holding the model output; default stdin")
    parser.add_argument("--criterion", choices=sorted(CRITERIA))
    args = parser.parse_args(argv)

    output = Path(args.output).read_text(encoding="utf-8") if args.output else sys.stdin.read()
    print(json.dumps(grade(args.case, output, args.criterion), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
