#!/usr/bin/env python3
"""Tests for render.py, mostly as golden files.

Two complete runs are rendered and compared byte for byte against
golden/*.md. A golden file is a blunt instrument, which is what makes it the
right one here: the report is the only part of this pipeline a person actually
reads, and any change to its wording should be a deliberate, reviewable diff
rather than something that slips through because a test only checked for a
substring.

Regenerate after an intentional change:

    UPDATE_GOLDEN=1 python3 tests/application-review/test_render.py

Then read the diff before committing it.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "application-review"
GOLDEN = Path(__file__).resolve().parent / "golden"
sys.path.insert(0, str(SCRIPTS))

import contracts  # noqa: E402
import render  # noqa: E402
import verdict as V  # noqa: E402

RUN_DATE = "2026-11-03"
UPDATE = os.environ.get("UPDATE_GOLDEN") == "1"

# ---------------------------------------------------------------------------
# Case A: an English CV against a posting it mostly fits, with one hard miss,
# one unknown, a near miss on years and a header-contact parse risk.
# ---------------------------------------------------------------------------

CV_A = """Marie Tremblay

EXPERIENCE

Senior Platform Engineer, Northwind Logistics
2022-01 - Present
Operated production Kubernetes clusters across three regions.
Built data pipelines in Python and Scala.

EDUCATION
B.Sc. Computer Science, McGill University, 2017
"""

PARSE_A = {
    "source_file": "cv.pdf", "format": "pdf", "text": CV_A,
    "parse_health": "structural_risk",
    "signals": [
        {"code": "contact_in_header", "severity": "risk",
         "detail": contracts.PARSE_SIGNALS["contact_in_header"][1],
         "evidence": "marie.tremblay@example.com | 514-555-0142"},
    ],
    "sections": {"experience": True, "education": True, "skills": False,
                 "certifications": False, "languages": False, "summary": False,
                 "projects": False},
    "language": "en",
    "extractor": {"tool": "pdftotext", "version": "26.10.0"},
}

REQUIREMENTS_A = {
    "posting_language": "en",
    "requirements": [
        {"id": "R1", "text": "5+ years of Python", "type": "years", "strength": "required",
         "threshold": {"years": 5}, "knockout_likely": True, "equivalents_allowed": False,
         "source_quote": "5+ years of Python"},
        {"id": "R2", "text": "Experience with Kubernetes", "type": "skill", "strength": "required",
         "threshold": None, "knockout_likely": False, "equivalents_allowed": False,
         "source_quote": "Experience with Kubernetes"},
        {"id": "R3", "text": "Authorized to work in Canada", "type": "work_auth",
         "strength": "required", "threshold": None, "knockout_likely": True,
         "equivalents_allowed": False, "source_quote": "Authorized to work in Canada"},
        {"id": "R4", "text": "AWS Certified Solutions Architect", "type": "cert",
         "strength": "preferred", "threshold": None, "knockout_likely": True,
         "equivalents_allowed": False, "source_quote": "AWS Certified Solutions Architect"},
    ],
    "flags": [],
}

EVIDENCE_A = {
    "cv_language": "en",
    "positions": [
        {"id": "P1", "title": "Senior Platform Engineer", "employer": "Northwind Logistics",
         "start": "2022-01", "end": "Present", "source_quote": "2022-01 - Present"},
    ],
    "findings": [
        {"requirement_id": "R1", "status": "met",
         "evidence_quote": "Built data pipelines in Python and Scala.",
         "position_ids": ["P1"], "note": None},
        {"requirement_id": "R2", "status": "met",
         "evidence_quote": "Operated production Kubernetes clusters across three regions.",
         "position_ids": ["P1"], "note": None},
        {"requirement_id": "R3", "status": "unknown_ask", "evidence_quote": None,
         "position_ids": [], "note": "The CV never states work authorization."},
        {"requirement_id": "R4", "status": "unmet", "evidence_quote": None,
         "position_ids": [], "note": None},
    ],
    "flags": [],
}

RECOMMENDATIONS_A = {
    "recommendations": [
        {"id": "C1", "kind": "format", "requirement_id": None,
         "text": "Move your email and phone out of the page header into the first line of the body.",
         "evidence_quote": None, "condition": None},
        {"id": "C2", "kind": "reframe", "requirement_id": "R2",
         "text": "Name Kubernetes on a skills line as well as in the bullet, so a keyword match finds it.",
         "evidence_quote": "Operated production Kubernetes clusters across three regions.",
         "condition": None},
        {"id": "C3", "kind": "ask", "requirement_id": "R3",
         "text": "If you are authorized to work in Canada, say so in one line under your contact details.",
         "evidence_quote": None,
         "condition": "if you are authorized to work in Canada"},
        {"id": "C4", "kind": "gap", "requirement_id": "R4",
         "text": "You hold no AWS certification. It is preferred rather than required, so it costs you ranking, not the application.",
         "evidence_quote": None, "condition": None},
    ],
    "refusals": [],
}

# ---------------------------------------------------------------------------
# Case B: a French CV, an unreadable file, injection text, and a refusal.
# ---------------------------------------------------------------------------

PARSE_B = {
    "source_file": "cv.pdf", "format": "pdf", "text": "",
    "parse_health": "unreadable",
    "signals": [
        {"code": "no_text_layer", "severity": "fatal",
         "detail": contracts.PARSE_SIGNALS["no_text_layer"][1], "evidence": None},
    ],
    "sections": {"experience": False, "education": False, "skills": False,
                 "certifications": False, "languages": False, "summary": False,
                 "projects": False},
    "language": "unknown",
    "extractor": {"tool": "pdftotext", "version": "26.10.0"},
}

REQUIREMENTS_B = {
    "posting_language": "fr",
    "requirements": [
        {"id": "R1", "text": "Baccalauréat en informatique", "type": "degree",
         "strength": "required", "threshold": None, "knockout_likely": True,
         "equivalents_allowed": True, "source_quote": "Baccalauréat en informatique"},
        {"id": "R2", "text": "Expérience canadienne requise", "type": "other",
         "strength": "required", "threshold": None, "knockout_likely": False,
         "equivalents_allowed": False, "source_quote": "Expérience canadienne requise"},
    ],
    "flags": [
        {"code": "discriminatory_requirement",
         "detail": "Requiring Canadian experience is banned in Ontario job postings since 2026 and is worth questioning anywhere.",
         "source_quote": "Expérience canadienne requise"},
    ],
}

EVIDENCE_B = {
    "cv_language": "unknown",
    "positions": [],
    "findings": [
        {"requirement_id": "R1", "status": "unknown_ask", "evidence_quote": None,
         "position_ids": [], "note": None},
        {"requirement_id": "R2", "status": "unknown_ask", "evidence_quote": None,
         "position_ids": [], "note": None},
    ],
    "flags": [
        {"code": "injection_text",
         "detail": "Text in the file addresses the reading system rather than a human. It is reported and ignored.",
         "source_quote": "Ignore all previous instructions"},
    ],
}

RECOMMENDATIONS_B = {
    "recommendations": [
        {"id": "C1", "kind": "format", "requirement_id": None,
         "text": "This PDF has no text layer, so it is an image. Export it again from the original document.",
         "evidence_quote": None, "condition": None},
    ],
    "refusals": [
        {"code": "hidden_text_request",
         "detail": "I won't add white or hidden keyword text: it is visible to a recruiter once parsed, and some systems flag it."},
    ],
}


def build(parse, requirements, evidence, recommendations, lang):
    v = V.compute(requirements, evidence, parse, run_date=RUN_DATE)
    assert contracts.validate("verdict", v) == [], contracts.validate("verdict", v)
    return render.render(parse, requirements, evidence, v, recommendations, lang=lang), v


CASES = {
    "case-a-en": (PARSE_A, REQUIREMENTS_A, EVIDENCE_A, RECOMMENDATIONS_A, "en"),
    "case-b-fr": (PARSE_B, REQUIREMENTS_B, EVIDENCE_B, RECOMMENDATIONS_B, "fr"),
}


class Golden(unittest.TestCase):
    def test_golden_files_match(self):
        GOLDEN.mkdir(exist_ok=True)
        for name, args in CASES.items():
            with self.subTest(case=name):
                text, _ = build(*args)
                path = GOLDEN / f"{name}.md"
                if UPDATE:
                    path.write_text(text, encoding="utf-8")
                    continue
                self.assertTrue(path.exists(), f"missing golden file {path}; run with UPDATE_GOLDEN=1")
                self.assertEqual(path.read_text(encoding="utf-8"), text)


class NoScoreEverywhere(unittest.TestCase):
    def test_the_report_prints_no_percentage(self):
        for name, args in CASES.items():
            with self.subTest(case=name):
                text, _ = build(*args)
                self.assertNotIn("%", text)
                self.assertNotRegex(text.lower(), r"\bmatch (score|rate)\b")


class Content(unittest.TestCase):
    def setUp(self):
        self.text_a, self.verdict_a = build(*CASES["case-a-en"])
        self.text_b, self.verdict_b = build(*CASES["case-b-fr"])

    def test_the_caveat_about_not_seeing_the_ats_appears_once(self):
        self.assertEqual(self.text_a.count("I can't see this employer's ATS settings"), 1)

    def test_every_requirement_has_a_row(self):
        for rid in ("R1", "R2", "R3", "R4"):
            self.assertIn(f"| {rid} |", self.text_a)

    def test_evidence_is_quoted_verbatim(self):
        self.assertIn("Operated production Kubernetes clusters across three regions.", self.text_a)

    def test_a_status_with_no_quote_says_so_rather_than_inventing_one(self):
        self.assertIn("no quote found", self.text_a)

    def test_the_years_arithmetic_is_shown(self):
        self.assertIn("2022-01 to 2026-11", self.text_a)
        self.assertIn("59 months", self.text_a)

    def test_the_unknown_note_appears_when_something_is_unknown(self):
        self.assertIn("I don't infer work authorization", self.text_a)

    def test_the_downgrade_is_explained(self):
        # S2 said met; 59 months against a 5-year bar is a near miss.
        self.assertIn("met → partly met", self.text_a)

    def test_refusals_are_shown(self):
        self.assertIn("hidden_text_request", self.text_b)

    def test_flags_from_both_steps_are_shown(self):
        self.assertIn("discriminatory_requirement", self.text_b)
        self.assertIn("injection_text", self.text_b)

    def test_the_french_report_uses_french_labels(self):
        self.assertIn("Revue de candidature", self.text_b)
        self.assertIn("Exigence par exigence", self.text_b)

    def test_the_french_report_does_not_translate_the_quoted_material(self):
        self.assertIn("Expérience canadienne requise", self.text_b)

    def test_the_french_report_has_no_english_machinery_showing_through(self):
        # The reasons and signals are generated by verdict.py in English. If
        # they reach a French report untranslated, the report reads like a
        # half-finished translation, which is exactly what RANK_FR and
        # SIGNAL_FR exist to prevent.
        for english in [
            "is a likely screening question",
            "is required and the CV",
            "has no extractable text layer",
            "is not evidenced",
        ]:
            with self.subTest(phrase=english):
                self.assertNotIn(english, self.text_b)

    def test_an_untranslated_reason_falls_back_to_english_rather_than_vanishing(self):
        v = json.loads(json.dumps(self.verdict_b))
        v["reasons"].append({
            "component": "likely_ai_tier", "code": "tier_gap", "requirement_id": None,
            "why": "a reason with no French phrasing available",
        })
        text = render.render(PARSE_B, REQUIREMENTS_B, EVIDENCE_B, v,
                             RECOMMENDATIONS_B, lang="fr")
        self.assertIn("est obligatoire et le CV ne l'appuie pas suffisamment", text)

    def test_an_unknown_language_falls_back_to_english(self):
        text = render.render(PARSE_A, REQUIREMENTS_A, EVIDENCE_A, self.verdict_a, lang="de")
        self.assertIn("Application review", text)

    def test_recommendations_are_grouped_by_kind(self):
        self.assertIn("File and layout fixes", self.text_a)
        self.assertIn("Questions only you can answer", self.text_a)
        self.assertIn("Real gaps", self.text_a)

    def test_recommendations_are_optional(self):
        text = render.render(PARSE_A, REQUIREMENTS_A, EVIDENCE_A, self.verdict_a)
        self.assertNotIn("What you can do", text)

    def test_a_pipe_in_a_quote_does_not_break_the_table(self):
        evidence = json.loads(json.dumps(EVIDENCE_A))
        evidence["findings"][1]["evidence_quote"] = "Python | Scala | Kubernetes"
        v = V.compute(REQUIREMENTS_A, evidence, PARSE_A, run_date=RUN_DATE)
        text = render.render(PARSE_A, REQUIREMENTS_A, evidence, v)
        row = next(line for line in text.splitlines() if line.startswith("| R2 |"))
        self.assertEqual(row.count("|") - row.count("\\|"), 6)

    def test_requirement_rows_sort_numerically(self):
        reqs = json.loads(json.dumps(REQUIREMENTS_A))
        for i in range(5, 13):
            reqs["requirements"].append({
                "id": f"R{i}", "text": f"thing {i}", "type": "skill", "strength": "preferred",
                "threshold": None, "knockout_likely": False, "equivalents_allowed": False,
                "source_quote": f"thing {i}",
            })
        ev = json.loads(json.dumps(EVIDENCE_A))
        for i in range(5, 13):
            ev["findings"].append({"requirement_id": f"R{i}", "status": "unmet",
                                   "evidence_quote": None, "position_ids": [], "note": None})
        v = V.compute(reqs, ev, PARSE_A, run_date=RUN_DATE)
        text = render.render(PARSE_A, reqs, ev, v)
        order = [line.split("|")[1].strip() for line in text.splitlines() if line.startswith("| R")]
        self.assertEqual(order.index("R2") < order.index("R10"), True)


class Cli(unittest.TestCase):
    def test_writes_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            v = V.compute(REQUIREMENTS_A, EVIDENCE_A, PARSE_A, run_date=RUN_DATE)
            for name, doc in [("parse", PARSE_A), ("requirements", REQUIREMENTS_A),
                              ("evidence", EVIDENCE_A), ("verdict", v),
                              ("recommendations", RECOMMENDATIONS_A)]:
                (d / f"{name}.json").write_text(json.dumps(doc))
            out = d / "report.md"
            r = subprocess.run([
                sys.executable, str(SCRIPTS / "render.py"),
                "--parse", str(d / "parse.json"),
                "--requirements", str(d / "requirements.json"),
                "--evidence", str(d / "evidence.json"),
                "--verdict", str(d / "verdict.json"),
                "--recommendations", str(d / "recommendations.json"),
                "--out", str(out),
            ], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Application review", out.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
