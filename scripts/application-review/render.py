#!/usr/bin/env python3
"""S5: render the report a person reads, from the JSON the pipeline produced.

Everything here is formatting. No judgement is made in this file, which is the
point: if the report says a requirement is unmet, that came from verdict.py,
and the text under it came from the model's quoted evidence. A renderer that
decided anything would be a second, undocumented verdict.

Three things it is careful about:

  * **It prints no score.** There is no number to print (design D1).
  * **It says once, plainly, what we cannot know**: the employer's actual ATS
    configuration. Every knockout is "likely".
  * **It shows the arithmetic** behind any years figure, because a total that
    disagrees with the candidate's own count needs to be checkable.

Labels come in English and French (D10); the quoted material is never
translated, since the quotes are verbatim by contract.

    render.py --parse p.json --requirements r.json --evidence e.json \
              --verdict v.json --recommendations c.json --out report.md

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

__all__ = ["render"]

L = {
    "en": {
        "title": "Application review",
        "caveat": (
            "I can't see this employer's ATS settings, so nothing below is a prediction "
            "of what their system is configured to do. It's what this posting suggests "
            "they would filter on, with the evidence I could find in your CV quoted "
            "underneath."
        ),
        "verdict": "Verdict",
        "part": "Part",
        "reading": "Reading",
        "knockout": "Knockout exposure",
        "tier": "Likely AI tier",
        "parse": "Parse health",
        "why": "Why",
        "requirements": "Requirement by requirement",
        "col_id": "Id",
        "col_req": "Requirement",
        "col_strength": "Strength",
        "col_status": "Status",
        "col_evidence": "Evidence from your CV",
        "rank": "Ranking signals",
        "years": "Years of experience, as a parser would count them",
        "years_note": (
            "Overlapping roles are counted once, \"Present\" is dated to {run_date}, "
            "and anything you state as a total is ignored."
        ),
        "total": "Total across all positions",
        "months": "months",
        "approx": "approximate, because some dates give only a year",
        "parse_h": "How your file reads to a parser",
        "no_signals": "Nothing in the file's structure looked risky.",
        "todo": "What you can do",
        "kinds": {
            "reframe": "Surface what's already there",
            "ask": "Questions only you can answer",
            "format": "File and layout fixes",
            "gap": "Real gaps",
        },
        "declined": "What I declined to do",
        "findings": "Other findings",
        "downgrades": "Where I stopped trusting my own reading",
        "no_quote": "no quote found",
        "unknown_note": (
            "I don't infer work authorization, location or clearance from an address, "
            "a name or a school. Where your CV is silent, the answer is a question for you."
        ),
    },
    "fr": {
        "title": "Revue de candidature",
        "caveat": (
            "Je ne vois pas la configuration du système de suivi des candidatures de cet "
            "employeur. Rien ici n'est une prédiction de ce que leur outil fera. C'est ce "
            "que l'offre laisse supposer, avec les preuves trouvées dans votre CV citées "
            "en dessous."
        ),
        "verdict": "Verdict",
        "part": "Volet",
        "reading": "Lecture",
        "knockout": "Exposition aux critères éliminatoires",
        "tier": "Niveau probable au tri automatisé",
        "parse": "Lisibilité du fichier",
        "why": "Pourquoi",
        "requirements": "Exigence par exigence",
        "col_id": "Id",
        "col_req": "Exigence",
        "col_strength": "Force",
        "col_status": "Statut",
        "col_evidence": "Preuve tirée de votre CV",
        "rank": "Signaux de classement",
        "years": "Années d'expérience, calculées comme le ferait un analyseur",
        "years_note": (
            "Les postes qui se chevauchent ne sont comptés qu'une fois, « à ce jour » est "
            "daté au {run_date}, et tout total que vous annoncez est ignoré."
        ),
        "total": "Total pour tous les postes",
        "months": "mois",
        "approx": "approximatif, car certaines dates ne donnent que l'année",
        "parse_h": "Ce qu'un analyseur lit dans votre fichier",
        "no_signals": "Rien dans la structure du fichier ne semblait risqué.",
        "todo": "Ce que vous pouvez faire",
        "kinds": {
            "reframe": "Mettre en valeur ce qui y est déjà",
            "ask": "Questions auxquelles vous seul pouvez répondre",
            "format": "Corrections de format et de mise en page",
            "gap": "Véritables écarts",
        },
        "declined": "Ce que j'ai refusé de faire",
        "findings": "Autres constats",
        "downgrades": "Là où j'ai cessé de me fier à ma propre lecture",
        "no_quote": "aucune citation trouvée",
        "unknown_note": (
            "Je ne déduis ni l'autorisation de travail, ni le lieu, ni l'habilitation à "
            "partir d'une adresse, d'un nom ou d'une école. Là où votre CV est muet, la "
            "réponse est une question pour vous."
        ),
    },
}

#: Human readings of the enum values. The enums stay machine-shaped in the JSON
#: and get spelled out exactly once, here.
WORDING = {
    "en": {
        "clear": "clear",
        "at_risk": "at risk",
        "unknown_ask": "unknown, needs your answer",
        "all_required_evidenced": "every required item is evidenced",
        "some_gaps": "some gaps",
        "major_gaps": "major gaps",
        "clean": "clean",
        "structural_risk": "structural risk",
        "unreadable": "unreadable",
        "met": "met",
        "partial": "partly met",
        "unmet": "not met",
        "ambiguous": "unconfirmed",
        "required": "required",
        "preferred": "preferred",
        "unspecified": "unspecified",
    },
    "fr": {
        "clear": "dégagé",
        "at_risk": "à risque",
        "unknown_ask": "inconnu, à confirmer par vous",
        "all_required_evidenced": "toutes les exigences obligatoires sont appuyées",
        "some_gaps": "quelques écarts",
        "major_gaps": "écarts importants",
        "clean": "propre",
        "structural_risk": "risque structurel",
        "unreadable": "illisible",
        "met": "satisfaite",
        "partial": "partiellement satisfaite",
        "unmet": "non satisfaite",
        "ambiguous": "non confirmée",
        "required": "obligatoire",
        "preferred": "souhaitée",
        "unspecified": "non précisée",
    },
}


#: French phrasings for the machine-generated reasons and signals. verdict.py
#: emits an English ``why`` plus a ``code``; when the report is in French the
#: code is looked up here instead, so a French-speaking user does not get a
#: French report with English machinery showing through it. ``{req}`` is the
#: requirement's own text, which is never translated: it is quoted from the
#: posting.
REASON_FR = {
    "knockout_at_risk": (
        "« {req} » est une question de présélection probable et le CV n'y répond pas"
    ),
    "knockout_unknown": (
        "« {req} » est une question de présélection probable et le CV est muet là-dessus; "
        "il faut donc vous le demander plutôt que de le déduire"
    ),
    "tier_gap": "« {req} » est obligatoire et le CV ne l'appuie pas suffisamment",
    "years_unreadable": (
        "les dates du poste n'ont pas pu être lues, donc les années n'ont pas pu être calculées"
    ),
}

SIGNAL_FR = {
    "multi_column_layout": (
        "L'ordre du flux de contenu et l'ordre visuel divergent, ce qui suggère des colonnes "
        "ou une barre latérale."
    ),
    "contact_in_header": "Un courriel ou un téléphone n'apparaît que dans l'en-tête de page.",
    "contact_in_footer": "Un courriel ou un téléphone n'apparaît que dans le pied de page.",
    "hidden_white_text": "Du texte est en blanc ou presque blanc sur fond blanc.",
    "hidden_tiny_text": "Du texte est rendu sous une taille lisible.",
    "text_box": "Du contenu se trouve dans une zone de texte, que bien des analyseurs ignorent.",
    "table_layout": "Du contenu se trouve dans un tableau, qui peut être lu dans un ordre inattendu.",
    "no_experience_heading": "Aucun titre d'expérience ou de parcours professionnel n'a été trouvé.",
    "no_text_layer": "Le fichier n'a aucune couche de texte: c'est une image.",
    "no_layout_tested": (
        "Une source en texte brut n'a pas de mise en page à tester, donc les risques de "
        "mise en page sont inconnus."
    ),
    "injection_text": (
        "Du texte du fichier s'adresse au système de lecture plutôt qu'à une personne. "
        "Il est signalé et ignoré."
    ),
    "encrypted": "Le fichier est chiffré et ne peut pas être lu.",
}

RANK_FR = {
    "preferred_met": "le CV appuie l'exigence souhaitée « {req} »",
    "preferred_unmet": "l'exigence souhaitée « {req} » n'est pas appuyée",
    "years_near_miss": (
        "les années calculées sont proches du seuil demandé; voir le calcul ci-dessous"
    ),
    "equivalents_allowed": "l'offre accepte un équivalent pour « {req} »",
    "language_mismatch": "l'offre et le CV ne sont pas dans la même langue",
    "title_below_posting": "le titre le plus récent du CV est moins élevé que celui de l'offre",
    "title_above_posting": "le titre le plus récent du CV est plus élevé que celui de l'offre",
    "acronym_only": "l'acronyme est présent mais pas la forme longue",
    "full_form_only": "la forme longue est présente mais pas l'acronyme",
    "skill_listed_not_evidenced": "la compétence est listée mais aucune expérience ne l'appuie",
}


def _phrase(table: dict, code: str | None, fallback: str, req_text: str | None) -> str:
    """A localised phrase for ``code``, falling back to the English prose.

    A missing translation gives the English sentence rather than a blank line:
    an untranslated reason is a wart, a dropped one is a lie.
    """
    template = table.get(code or "")
    if not template:
        return fallback
    return template.format(req=req_text or "")


def _cell(text: str | None, limit: int = 160) -> str:
    """One table cell: pipes escaped, newlines flattened, length capped."""
    if not text:
        return "—"
    s = " ".join(str(text).split())
    if len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return s.replace("|", "\\|")


def render(
    parse: dict,
    requirements: dict,
    evidence: dict,
    verdict: dict,
    recommendations: dict | None = None,
    *,
    lang: str = "en",
) -> str:
    lang = lang if lang in L else "en"
    t = L[lang]
    w = WORDING[lang]
    recommendations = recommendations or {"recommendations": [], "refusals": []}

    reqs = {r["id"]: r for r in requirements.get("requirements", [])}
    findings = {f["requirement_id"]: f for f in evidence.get("findings", [])}
    # The verdict holds the FINAL status: the quote edge and the years
    # arithmetic both move statuses after the model wrote evidence.json, and a
    # report that printed the model's original answer would contradict the
    # verdict table two sections above it.
    final = verdict.get("statuses") or {}
    out: list[str] = []

    out.append(f"# {t['title']}")
    out.append("")
    out.append(t["caveat"])
    out.append("")

    # ---- the verdict table ----
    out.append(f"## {t['verdict']}")
    out.append("")
    out.append(f"| {t['part']} | {t['reading']} |")
    out.append("|---|---|")
    out.append(f"| {t['knockout']} | **{w[verdict['knockout_exposure']]}** |")
    out.append(f"| {t['tier']} | **{w[verdict['likely_ai_tier']]}** |")
    out.append(f"| {t['parse']} | **{w[verdict['parse_health']]}** |")
    out.append("")

    reasons = verdict.get("reasons", [])
    if reasons:
        out.append(f"### {t['why']}")
        out.append("")
        for reason in reasons:
            rid = reason.get("requirement_id")
            prefix = f"**{rid}** — " if rid else ""
            if lang == "en":
                why = reason["why"]
            elif reason.get("code") == "parse_signal":
                signal_code = reason.get("signal") or ""
                why = f"{signal_code}: {SIGNAL_FR.get(signal_code, reason['why'])}"
            else:
                req_text = reqs.get(rid, {}).get("text")
                why = _phrase(REASON_FR, reason.get("code"), reason["why"], req_text)
            out.append(f"- {prefix}{why}")
        out.append("")

    if verdict["knockout_exposure"] == "unknown_ask" or any(
        f.get("status") == "unknown_ask" for f in findings.values()
    ):
        out.append(t["unknown_note"])
        out.append("")

    # ---- requirement table ----
    out.append(f"## {t['requirements']}")
    out.append("")
    out.append(
        f"| {t['col_id']} | {t['col_req']} | {t['col_strength']} | {t['col_status']} | {t['col_evidence']} |"
    )
    out.append("|---|---|---|---|---|")
    for rid in sorted(reqs, key=_id_key):
        req = reqs[rid]
        finding = findings.get(rid, {})
        status = final.get(rid) or finding.get("status", "unmet")
        quote = finding.get("evidence_quote")
        shown = f'"{_cell(quote)}"' if quote and status in ("met", "partial") else t["no_quote"]
        out.append(
            f"| {rid} | {_cell(req['text'])} | {w.get(req['strength'], req['strength'])} "
            f"| {w.get(status, status)} | {shown} |"
        )
    out.append("")

    # ---- downgrades ----
    downgrades = verdict.get("downgrades", [])
    if downgrades:
        out.append(f"### {t['downgrades']}")
        out.append("")
        for d in downgrades:
            out.append(
                f"- **{d['requirement_id']}**: {w.get(d['from'], d['from'])} → "
                f"{w.get(d['to'], d['to'])}, {d['why']}"
            )
        out.append("")

    # ---- rank signals ----
    signals = verdict.get("rank_signals", [])
    if signals:
        out.append(f"## {t['rank']}")
        out.append("")
        for s in signals:
            rid = s.get("requirement_id")
            prefix = f"**{rid}** — " if rid else ""
            detail = s["detail"] if lang == "en" else _phrase(
                RANK_FR, s.get("code"), s["detail"], reqs.get(rid, {}).get("text")
            )
            out.append(f"- {prefix}{detail}")
        out.append("")

    # ---- years ----
    years = verdict.get("years", {})
    if years.get("merged_ranges") or years.get("per_requirement"):
        out.append(f"## {t['years']}")
        out.append("")
        out.append(t["years_note"].format(run_date=years.get("run_date", "?")))
        out.append("")
        spans = ", ".join(f"{a} to {b}" for a, b in years.get("merged_ranges", []))
        if spans:
            note = f" ({t['approx']})" if years.get("approximate") else ""
            out.append(
                f"- {t['total']}: {spans} = {years.get('total_months')} {t['months']} "
                f"({years.get('total_years')}){note}"
            )
        for rid, detail in sorted(years.get("per_requirement", {}).items(), key=lambda kv: _id_key(kv[0])):
            if detail.get("months") is None:
                out.append(f"- **{rid}**: dates could not be read")
                continue
            spans = ", ".join(f"{a} to {b}" for a, b in detail.get("ranges", []))
            note = f" ({t['approx']})" if detail.get("approximate") else ""
            against = detail.get("threshold_years")
            out.append(
                f"- **{rid}**: {spans or '—'} = {detail['months']} {t['months']} "
                f"({detail['years']}) against a {against}-year requirement{note}"
            )
        out.append("")

    # ---- parse health ----
    out.append(f"## {t['parse_h']}")
    out.append("")
    signals = [s for s in parse.get("signals", []) if s["code"] != "no_layout_tested"]
    if not signals:
        out.append(t["no_signals"])
    for s in parse.get("signals", []):
        detail = s["detail"] if lang == "en" else SIGNAL_FR.get(s["code"], s["detail"])
        out.append(f"- [{s['severity']}] **{s['code']}** — {detail}")
        if s.get("evidence"):
            out.append(f"  - `{_cell(s['evidence'], 200)}`")
    out.append("")

    # ---- recommendations ----
    recs = recommendations.get("recommendations", [])
    if recs:
        out.append(f"## {t['todo']}")
        out.append("")
        for kind in ("format", "reframe", "ask", "gap"):
            group = [r for r in recs if r.get("kind") == kind]
            if not group:
                continue
            out.append(f"### {t['kinds'][kind]}")
            out.append("")
            for r in group:
                rid = r.get("requirement_id")
                prefix = f"**{rid}** — " if rid else ""
                out.append(f"- {prefix}{r['text']}")
                if r.get("evidence_quote"):
                    out.append(f'  - {t["col_evidence"]}: "{_cell(r["evidence_quote"])}"')
            out.append("")

    # ---- refusals and flags ----
    refusals = recommendations.get("refusals", [])
    if refusals:
        out.append(f"## {t['declined']}")
        out.append("")
        for r in refusals:
            out.append(f"- **{r['code']}** — {r['detail']}")
        out.append("")

    flags = list(requirements.get("flags", [])) + list(evidence.get("flags", []))
    if flags:
        out.append(f"## {t['findings']}")
        out.append("")
        for f in flags:
            out.append(f"- **{f['code']}** — {f['detail']}")
            if f.get("source_quote"):
                out.append(f'  - "{_cell(f["source_quote"])}"')
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def _id_key(rid: str) -> tuple[str, int]:
    """Sort R2 before R10, which a plain string sort gets backwards."""
    head = "".join(c for c in str(rid) if c.isalpha())
    tail = "".join(c for c in str(rid) if c.isdigit())
    return (head, int(tail) if tail else 0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="render.py", description="Render the Markdown report.")
    parser.add_argument("--parse", required=True)
    parser.add_argument("--requirements", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--verdict", required=True)
    parser.add_argument("--recommendations")
    parser.add_argument("--lang", default="en", choices=sorted(L))
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    def load(path: str | None):
        if not path:
            return None
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"render failed: {path}: no such file", file=sys.stderr)
            raise SystemExit(2)
        except json.JSONDecodeError as exc:
            print(f"render failed: {path}: invalid JSON: {exc.msg}", file=sys.stderr)
            raise SystemExit(2)

    text = render(
        load(args.parse), load(args.requirements), load(args.evidence),
        load(args.verdict), load(args.recommendations), lang=args.lang,
    )
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"report: {args.out} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
