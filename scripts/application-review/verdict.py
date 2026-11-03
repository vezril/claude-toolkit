#!/usr/bin/env python3
"""S3: compose the four-part verdict in code, from the model's evidence.

Design D1 is the whole argument for this file. The overlap-percentage tools
publish no basis for their thresholds, different tools score the same CV
differently, and the LLM screeners they are imitating are themselves noisy and
biased. A precise number would claim an accuracy nobody has. So the output is
four categorical judgements, each one traceable to a requirement id:

  knockout exposure   clear / at_risk / unknown_ask
  likely AI tier      all_required_evidenced / some_gaps / major_gaps
  parse health        clean / structural_risk / unreadable
  rank signals        an advisory list

And the arithmetic is done here, not by the model. S2 decides *which* positions
evidence a skill; this file sums their dates (D5) and compares the total with
the posting's threshold. When the model's status and the arithmetic disagree,
the arithmetic wins and the disagreement is recorded as a downgrade, because a
reader deserves to see where the agent stopped believing itself.

    verdict.py --requirements r.json --evidence e.json --parse p.json --out v.json

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

import contracts
from years import Range, meets_threshold, merge_ranges, months_to_years, position_range

__all__ = ["compute", "seniority"]

#: Statuses that mean "the CV shows this". Everything else is a gap of some
#: kind, including `ambiguous`, which means we could not confirm the quote.
_EVIDENCED = {"met"}

#: Strengths that can put a run at risk of a hard filter. `preferred` cannot:
#: a preferred certification is a ranking matter. `unspecified` can, because
#: postings routinely state work authorization with no Required heading at all,
#: and treating that as optional would miss the commonest filter there is.
_KNOCKOUT_STRENGTHS = {"required", "unspecified"}

#: How each non-met status reads in a sentence. Spelling the enum into prose
#: here keeps the raw vocabulary out of the report, which otherwise ends up
#: telling the user their CV shows something as "unknown_ask".
_GAP_PHRASE = {
    "partial": "the CV only partly evidences it",
    "unmet": "the CV gives no evidence for it",
    "ambiguous": "the quoted evidence could not be confirmed in the CV text",
    "unknown_ask": "the CV is silent on it",
    None: "there is no finding for it",
}

#: A rough seniority ladder for comparing the posting's title with the
#: candidate's most recent one. Deliberately coarse: it drives an advisory
#: signal, never a verdict component.
_SENIORITY = [
    (1, ("intern", "internship", "stagiaire", "student", "etudiant", "trainee",
         "junior", "jr", "entry level", "debutant", "associate", "assistant",
         "apprentice", "graduate")),
    (2, ("engineer", "developer", "developpeur", "developpeuse", "analyst",
         "analyste", "programmer", "programmeur", "specialist", "consultant",
         "administrator", "technician", "ingenieur", "ingenieure")),
    (3, ("senior", "sr", "senior level", "principal engineer ii", "intermediate",
         "intermediaire", "confirme", "experienced", "ii", "iii")),
    (4, ("staff", "principal", "architect", "architecte", "expert", "lead",
         "tech lead", "chef d equipe", "manager", "gestionnaire", "head",
         "director", "directeur", "directrice", "vp", "chief")),
]


def _id_key(rid: str) -> tuple[str, int]:
    """Sort R2 before R10, which a plain string sort gets backwards."""
    head = "".join(c for c in str(rid) if c.isalpha())
    tail = "".join(c for c in str(rid) if c.isdigit())
    return (head, int(tail) if tail else 0)


def _fold(text: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", str(text))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def seniority(title: str) -> int | None:
    """Coarse rank for a job title, or None when nothing in it is a rank word."""
    words = set(_fold(title).split())
    best: int | None = None
    for rank, markers in _SENIORITY:
        for marker in markers:
            parts = marker.split()
            if (len(parts) == 1 and parts[0] in words) or (len(parts) > 1 and marker in _fold(title)):
                best = rank if best is None else max(best, rank)
                break
    return best


def _ranges_for(position_ids: list[str], positions: dict[str, dict], run_date: str) -> tuple[list[Range], bool]:
    """Date ranges for the named positions. The bool says whether any failed to parse."""
    ranges: list[Range] = []
    unreadable = False
    for pid in position_ids:
        pos = positions.get(pid)
        if not pos:
            unreadable = True
            continue
        try:
            ranges.append(position_range(pos["start"], pos["end"], run_date=run_date))
        except (ValueError, KeyError):
            unreadable = True
    return ranges, unreadable


def compute(
    requirements: dict,
    evidence: dict,
    parse: dict,
    *,
    downgrades: list[dict] | None = None,
    run_date: str | None = None,
) -> dict:
    """Roll the model's findings plus the parse signals into a verdict."""
    run_date = run_date or date.today().isoformat()
    reqs = {r["id"]: r for r in requirements.get("requirements", [])}
    findings = {f["requirement_id"]: dict(f) for f in evidence.get("findings", [])}
    positions = {p["id"]: p for p in evidence.get("positions", [])}

    all_downgrades: list[dict] = [dict(d) for d in (downgrades or [])]
    reasons: list[dict] = []
    rank_signals: list[dict] = []
    per_requirement: dict[str, dict] = {}

    def signal(code: str, detail: str, requirement_id: str | None = None) -> None:
        entry = {"code": code, "requirement_id": requirement_id, "detail": detail}
        if entry not in rank_signals:
            rank_signals.append(entry)

    # ---- the years override (D5) -----------------------------------------
    for rid, req in reqs.items():
        finding = findings.get(rid)
        if not finding:
            continue
        threshold = (req.get("threshold") or {}).get("years")
        if req.get("type") != "years" or threshold is None:
            continue

        cited = finding.get("position_ids") or []
        if not cited and finding["status"] not in ("met", "partial"):
            # No dates to do arithmetic on, and no claim to check. Computing
            # zero months here would turn "the CV is unreadable" or "the CV
            # does not say" into "this candidate has no experience", which is
            # a different and much worse statement. A met or partial with no
            # cited position is another matter: that claim has nothing holding
            # it up, so it still goes through the arithmetic below.
            continue

        ranges, unreadable = _ranges_for(cited, positions, run_date)
        merged = merge_ranges(ranges)
        months = sum(r.months for r in merged) if ranges else 0
        approximate = any(r.approximate for r in merged)

        if unreadable and not ranges:
            per_requirement[rid] = {"months": None, "years": None, "approximate": True,
                                    "ranges": [], "threshold_years": threshold}
            if finding["status"] != "unknown_ask":
                all_downgrades.append({
                    "requirement_id": rid, "from": finding["status"], "to": "ambiguous",
                    "why": "the position dates could not be read, so the years could not be computed",
                })
                finding["status"] = "ambiguous"
            reasons.append({
                "component": "likely_ai_tier", "code": "years_unreadable",
                "requirement_id": rid,
                "why": "the position dates could not be read, so the years could not be computed",
            })
            continue

        computed = meets_threshold(months, threshold, approximate=approximate)
        per_requirement[rid] = {
            "months": months, "years": months_to_years(months), "approximate": approximate,
            "ranges": [list(r.iso()) for r in merged], "threshold_years": threshold,
        }
        if computed != finding["status"]:
            all_downgrades.append({
                "requirement_id": rid, "from": finding["status"], "to": computed,
                "why": (
                    f"the dates give {months_to_years(months)} years against a "
                    f"{threshold}-year requirement"
                ),
            })
            finding["status"] = computed
        if computed == "partial":
            signal("years_near_miss",
                   f"the dates give {months_to_years(months)} years against a "
                   f"{threshold}-year requirement, which is close enough that a "
                   f"different rounding could go either way",
                   rid)

    # ---- knockout exposure (D1, D6) --------------------------------------
    exposure = "clear"
    for rid, req in sorted(reqs.items()):
        if not req.get("knockout_likely") or req.get("strength") not in _KNOCKOUT_STRENGTHS:
            continue
        status = findings.get(rid, {}).get("status")
        if status in ("unmet", "partial"):
            exposure = "at_risk"
            reasons.append({
                "component": "knockout_exposure", "code": "knockout_at_risk",
                "requirement_id": rid,
                "why": f"{req['text']!r} is a likely screening question and the CV does not meet it",
            })
        elif status in ("unknown_ask", "ambiguous") and exposure != "at_risk":
            exposure = "unknown_ask"
            reasons.append({
                "component": "knockout_exposure", "code": "knockout_unknown",
                "requirement_id": rid,
                "why": (
                    f"{req['text']!r} is a likely screening question and the CV is silent on it, "
                    "so it has to be asked rather than inferred"
                ),
            })
        if req.get("equivalents_allowed") and status in ("unmet", "partial", "ambiguous"):
            signal("equivalents_allowed",
                   f"the posting allows an equivalent for {req['text']!r}", rid)

    # A later at_risk must win over an earlier unknown_ask, so the reasons are
    # pruned to the component that actually carries.
    if exposure == "at_risk":
        reasons = [r for r in reasons if r.get("code") != "knockout_unknown"]

    # ---- likely AI tier --------------------------------------------------
    # "Evidenced" means met. A `partial`, an `unmet` and an `ambiguous` are all
    # gaps in the CV's evidence and count toward major_gaps. An `unknown_ask`
    # is not: it is a question for the candidate, it is already reported under
    # knockout exposure, and counting it twice would make a silent line on the
    # CV look like a missing qualification.
    required_ids = [rid for rid, r in reqs.items() if r.get("strength") == "required"]
    statuses = {rid: findings.get(rid, {}).get("status") for rid in reqs}
    missing = [rid for rid in required_ids if statuses.get(rid) not in _EVIDENCED]
    hard = [rid for rid in missing if statuses.get(rid) in ("unmet", "partial", "ambiguous")]

    if not required_ids or not missing:
        tier = "all_required_evidenced"
    else:
        allowance = max(1, math.ceil(0.25 * len(required_ids)))
        # The allowance has a floor of one, which on a one-requirement posting
        # would call "nothing met" a mere some_gaps. So a CV that evidences
        # none of the required items and plainly fails at least one is
        # major_gaps regardless of how short the posting is. An `unknown_ask`
        # or `ambiguous` does not trigger that: those are things we could not
        # determine, not things the CV lacks.
        nothing_met = not any(statuses.get(rid) in _EVIDENCED for rid in required_ids)
        flatly_unmet = any(statuses.get(rid) == "unmet" for rid in required_ids)
        if len(hard) > allowance or (nothing_met and flatly_unmet):
            tier = "major_gaps"
        else:
            tier = "some_gaps"
        knocked = {r["requirement_id"] for r in reasons if r["component"] == "knockout_exposure"}
        for rid in sorted(missing, key=_id_key):
            # Said once. If the requirement already appears under knockout
            # exposure, repeating it here just makes the Why list longer.
            if rid in knocked:
                continue
            reasons.append({
                "component": "likely_ai_tier", "code": "tier_gap", "requirement_id": rid,
                "why": f"{reqs[rid]['text']!r} is required and {_GAP_PHRASE[statuses.get(rid)]}",
            })

    # ---- parse health ----------------------------------------------------
    parse_health = parse.get("parse_health", "clean")
    for sig in parse.get("signals", []):
        if sig.get("severity") in ("risk", "fatal"):
            reasons.append({
                "component": "parse_health", "code": "parse_signal",
                "requirement_id": None, "signal": sig["code"],
                "why": f"{sig['code']}: {sig['detail']}",
            })

    # ---- rank signals ----------------------------------------------------
    for rid, req in sorted(reqs.items()):
        status = findings.get(rid, {}).get("status")
        if req.get("strength") == "preferred":
            if status in _EVIDENCED:
                signal("preferred_met", f"the CV evidences the preferred {req['text']!r}", rid)
            else:
                signal("preferred_unmet", f"the preferred {req['text']!r} is not evidenced", rid)

    posting_language = requirements.get("posting_language", "unknown")
    cv_language = evidence.get("cv_language", "unknown")
    if (
        posting_language in ("en", "fr") and cv_language in ("en", "fr")
        and posting_language != cv_language
    ):
        signal("language_mismatch",
               f"the posting is in {posting_language} and the CV is in {cv_language}")

    title_reqs = [r for r in reqs.values() if r.get("type") == "title"]
    newest = _most_recent_position(positions, run_date)
    if title_reqs and newest:
        wanted = max((seniority(r["text"]) or 0) for r in title_reqs)
        held = seniority(newest.get("title", "")) or 0
        if wanted and held:
            if held < wanted:
                signal("title_below_posting",
                       f"the posting asks for {title_reqs[0]['text']!r} and the most recent "
                       f"title on the CV is {newest['title']!r}")
            elif held > wanted:
                signal("title_above_posting",
                       f"the most recent title on the CV, {newest['title']!r}, is more senior "
                       f"than the posting's {title_reqs[0]['text']!r}")

    # ---- career total ----------------------------------------------------
    all_ranges, _ = _ranges_for(list(positions), positions, run_date)
    merged_all = merge_ranges(all_ranges)

    return {
        "knockout_exposure": exposure,
        "likely_ai_tier": tier,
        "parse_health": parse_health,
        "statuses": {rid: statuses.get(rid) for rid in sorted(reqs, key=_id_key)},
        "rank_signals": rank_signals,
        "reasons": reasons,
        "years": {
            "run_date": run_date,
            "total_months": sum(r.months for r in merged_all),
            "total_years": months_to_years(sum(r.months for r in merged_all)),
            "approximate": any(r.approximate for r in merged_all),
            "merged_ranges": [list(r.iso()) for r in merged_all],
            "per_requirement": per_requirement,
        },
        "downgrades": all_downgrades,
    }


def _most_recent_position(positions: dict[str, dict], run_date: str) -> dict | None:
    best: tuple[tuple[int, int], dict] | None = None
    for pos in positions.values():
        try:
            rng = position_range(pos["start"], pos["end"], run_date=run_date)
        except (ValueError, KeyError):
            continue
        if best is None or rng.end > best[0]:
            best = (rng.end, pos)
    return best[1] if best else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verdict.py",
        description="Compose the four-part verdict from the pipeline's JSON.",
    )
    parser.add_argument("--requirements", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--parse", required=True)
    parser.add_argument("--downgrades", help="the quote edge's downgrade list, if it wrote one")
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--run-date",
        help="ISO date used to resolve Present. Defaults to today; set it to make a run reproducible.",
    )
    args = parser.parse_args(argv)

    def load(path: str):
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"verdict failed: {path}: no such file", file=sys.stderr)
            raise SystemExit(2)
        except json.JSONDecodeError as exc:
            print(f"verdict failed: {path}: invalid JSON: {exc.msg}", file=sys.stderr)
            raise SystemExit(2)

    downgrades = load(args.downgrades) if args.downgrades else []
    result = compute(
        load(args.requirements), load(args.evidence), load(args.parse),
        downgrades=downgrades, run_date=args.run_date,
    )

    problems = contracts.validate("verdict", result)
    if problems:  # pragma: no cover - a bug here, not in the input
        print("verdict produced invalid JSON: " + "; ".join(problems), file=sys.stderr)
        return 3

    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "verdict: knockout={knockout_exposure} tier={likely_ai_tier} parse={parse_health} "
        "rank_signals={n}".format(n=len(result["rank_signals"]), **result)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
