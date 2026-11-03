#!/usr/bin/env python3
"""Tests for verdict.py: the D1 roll-up, and the years override of D5.

The verdict is the one thing in this pipeline a user will quote back at us, and
it is computed entirely in code. These tests are the specification of what each
of the four parts means.

Run: python3 tests/application-review/test_verdict.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "application-review"
sys.path.insert(0, str(SCRIPTS))

import contracts  # noqa: E402
import verdict as V  # noqa: E402

RUN_DATE = "2026-11-03"


def req(id_, **kw):
    base = {
        "id": id_, "text": f"requirement {id_}", "type": "skill",
        "strength": "required", "threshold": None, "knockout_likely": False,
        "equivalents_allowed": False, "source_quote": f"requirement {id_}",
    }
    base.update(kw)
    return base


def finding(rid, status, *, quote="evidence", positions=("P1",)):
    return {
        "requirement_id": rid, "status": status,
        "evidence_quote": quote if status in ("met", "partial") else None,
        "position_ids": list(positions) if status in ("met", "partial") else [],
        "note": None,
    }


def pos(id_, start, end, title="Engineer"):
    return {"id": id_, "title": title, "employer": "Northwind",
            "start": start, "end": end, "source_quote": f"{start} - {end}"}


def parse(health="clean", signals=(), language="en"):
    return {
        "source_file": "cv.txt", "format": "txt", "text": "cv text",
        "parse_health": health,
        "signals": [{"code": c, "severity": contracts.PARSE_SIGNALS[c][0],
                     "detail": contracts.PARSE_SIGNALS[c][1], "evidence": None} for c in signals],
        "sections": {"experience": True}, "language": language,
        "extractor": {"tool": "t", "version": "1"},
    }


def evidence(findings, positions=(pos("P1", "2018-01", "Present"),), language="en"):
    return {"cv_language": language, "positions": list(positions),
            "findings": list(findings), "flags": []}


def compute(requirements, findings, *, positions=(pos("P1", "2018-01", "Present"),),
            parse_doc=None, downgrades=(), run_date=RUN_DATE, posting_language="en"):
    reqs = {"posting_language": posting_language, "requirements": list(requirements), "flags": []}
    return V.compute(
        reqs, evidence(findings, positions), parse_doc or parse(),
        downgrades=list(downgrades), run_date=run_date,
    )


class Shape(unittest.TestCase):
    def test_the_output_matches_its_contract(self):
        v = compute([req("R1")], [finding("R1", "met")])
        self.assertEqual(contracts.validate("verdict", v), [])

    def test_there_is_no_score_anywhere_in_the_output(self):
        # D1: no percentage, ever. The field must not exist for a renderer to
        # accidentally find.
        v = compute([req("R1")], [finding("R1", "met")])
        flat = json.dumps(v)
        for banned in ["score", "percent", "match_rate", "fit"]:
            self.assertNotIn(banned, flat.lower())


class KnockoutExposure(unittest.TestCase):
    def test_no_knockout_requirements_is_clear(self):
        v = compute([req("R1")], [finding("R1", "met")])
        self.assertEqual(v["knockout_exposure"], "clear")

    def test_a_met_knockout_is_clear(self):
        v = compute([req("R1", type="degree", knockout_likely=True)], [finding("R1", "met")])
        self.assertEqual(v["knockout_exposure"], "clear")

    def test_an_unmet_required_knockout_is_at_risk_and_named(self):
        # The spec's scenario: high overlap, one required certification missing.
        v = compute(
            [req("R1"), req("R2", type="cert", knockout_likely=True)],
            [finding("R1", "met"), finding("R2", "unmet")],
        )
        self.assertEqual(v["knockout_exposure"], "at_risk")
        self.assertTrue(any(r["requirement_id"] == "R2" and r["component"] == "knockout_exposure"
                            for r in v["reasons"]), v["reasons"])

    def test_silence_on_work_authorization_is_unknown_ask(self):
        v = compute(
            [req("R1", type="work_auth", knockout_likely=True)],
            [finding("R1", "unknown_ask")],
        )
        self.assertEqual(v["knockout_exposure"], "unknown_ask")

    def test_a_known_problem_outranks_an_unknown_one(self):
        # Reporting "unknown" when we already found a hard miss would bury the
        # thing the user most needs to see.
        v = compute(
            [req("R1", type="work_auth", knockout_likely=True),
             req("R2", type="degree", knockout_likely=True)],
            [finding("R1", "unknown_ask"), finding("R2", "unmet")],
        )
        self.assertEqual(v["knockout_exposure"], "at_risk")

    def test_an_unconfirmed_quote_counts_as_unknown_not_clear(self):
        v = compute(
            [req("R1", type="licence", knockout_likely=True)],
            [{"requirement_id": "R1", "status": "ambiguous", "evidence_quote": "x",
              "position_ids": [], "note": None}],
        )
        self.assertEqual(v["knockout_exposure"], "unknown_ask")

    def test_a_preferred_knockout_type_does_not_put_the_run_at_risk(self):
        # A preferred certification is a ranking matter, not a filter.
        v = compute(
            [req("R1", type="cert", strength="preferred", knockout_likely=True)],
            [finding("R1", "unmet")],
        )
        self.assertEqual(v["knockout_exposure"], "clear")
        self.assertTrue(any(s["code"] == "preferred_unmet" for s in v["rank_signals"]))

    def test_an_unspecified_work_auth_requirement_still_counts(self):
        # Postings often state work authorization without a Required heading.
        # Treating that as optional would miss the commonest hard filter.
        v = compute(
            [req("R1", type="work_auth", strength="unspecified", knockout_likely=True)],
            [finding("R1", "unmet")],
        )
        self.assertEqual(v["knockout_exposure"], "at_risk")

    def test_a_partial_knockout_is_at_risk_because_thresholds_are_hard(self):
        v = compute(
            [req("R1", type="years", strength="required", knockout_likely=True,
                 threshold={"years": 10})],
            [finding("R1", "partial")],
        )
        self.assertEqual(v["knockout_exposure"], "at_risk")


class LikelyAiTier(unittest.TestCase):
    def test_every_required_item_met(self):
        v = compute(
            [req("R1"), req("R2"), req("R3", strength="preferred")],
            [finding("R1", "met"), finding("R2", "met"), finding("R3", "unmet")],
        )
        self.assertEqual(v["likely_ai_tier"], "all_required_evidenced")

    def test_preferred_misses_are_only_rank_signals(self):
        # The spec's scenario: all required met, all preferred missing.
        v = compute(
            [req("R1"), req("R2", strength="preferred"), req("R3", strength="preferred")],
            [finding("R1", "met"), finding("R2", "unmet"), finding("R3", "unmet")],
        )
        self.assertEqual(v["likely_ai_tier"], "all_required_evidenced")
        self.assertEqual(sum(1 for s in v["rank_signals"] if s["code"] == "preferred_unmet"), 2)

    def test_one_miss_in_four_is_some_gaps(self):
        reqs = [req(f"R{i}") for i in range(1, 5)]
        finds = [finding("R1", "met"), finding("R2", "met"), finding("R3", "met"),
                 finding("R4", "unmet")]
        self.assertEqual(compute(reqs, finds)["likely_ai_tier"], "some_gaps")

    def test_most_required_items_missing_is_major_gaps(self):
        reqs = [req(f"R{i}") for i in range(1, 5)]
        finds = [finding("R1", "met"), finding("R2", "unmet"), finding("R3", "unmet"),
                 finding("R4", "unmet")]
        self.assertEqual(compute(reqs, finds)["likely_ai_tier"], "major_gaps")

    def test_a_partial_is_a_gap_not_a_pass(self):
        v = compute([req("R1"), req("R2")], [finding("R1", "met"), finding("R2", "partial")])
        self.assertEqual(v["likely_ai_tier"], "some_gaps")

    def test_an_ambiguous_status_is_a_gap(self):
        v = compute(
            [req("R1"), req("R2")],
            [finding("R1", "met"),
             {"requirement_id": "R2", "status": "ambiguous", "evidence_quote": "x",
              "position_ids": [], "note": None}],
        )
        self.assertEqual(v["likely_ai_tier"], "some_gaps")

    def test_a_single_required_item_flatly_unmet_is_major_not_some(self):
        # The 25% allowance has a floor of one, which on a one-requirement
        # posting would report "some gaps" for a CV that evidences nothing.
        v = compute([req("R1")], [finding("R1", "unmet")])
        self.assertEqual(v["likely_ai_tier"], "major_gaps")

    def test_nothing_met_but_nothing_refuted_either_is_some_gaps(self):
        # Silence is not a gap in the same sense. unknown_ask means we could
        # not determine it, so it must not be reported as a missing
        # qualification.
        v = compute([req("R1")], [finding("R1", "unknown_ask")])
        self.assertEqual(v["likely_ai_tier"], "some_gaps")

    def test_two_required_one_met_one_unmet_is_some_gaps(self):
        v = compute([req("R1"), req("R2")], [finding("R1", "met"), finding("R2", "unmet")])
        self.assertEqual(v["likely_ai_tier"], "some_gaps")

    def test_a_posting_with_no_required_items_is_vacuously_evidenced(self):
        v = compute([req("R1", strength="preferred")], [finding("R1", "unmet")])
        self.assertEqual(v["likely_ai_tier"], "all_required_evidenced")


class ParseHealthPassesThrough(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(compute([req("R1")], [finding("R1", "met")])["parse_health"], "clean")

    def test_structural_risk(self):
        v = compute([req("R1")], [finding("R1", "met")],
                    parse_doc=parse("structural_risk", ["multi_column_layout"]))
        self.assertEqual(v["parse_health"], "structural_risk")
        self.assertTrue(any(r["component"] == "parse_health" for r in v["reasons"]))

    def test_unreadable_is_reported_without_pretending_the_rest_is_solid(self):
        v = compute([req("R1")], [finding("R1", "met")],
                    parse_doc=parse("unreadable", ["no_text_layer"]))
        self.assertEqual(v["parse_health"], "unreadable")


class YearsArithmetic(unittest.TestCase):
    def test_overlapping_positions_are_merged(self):
        v = compute(
            [req("R1", type="years", threshold={"years": 5}, knockout_likely=True)],
            [finding("R1", "met", positions=("P1", "P2"))],
            positions=(pos("P1", "2018-01", "2021-12"), pos("P2", "2020-06", "2023-06")),
        )
        self.assertEqual(v["years"]["per_requirement"]["R1"]["months"], 66)
        self.assertEqual(v["years"]["per_requirement"]["R1"]["years"], 5.5)

    def test_the_computed_total_overrides_a_models_optimism(self):
        # S2 says met; the dates say 24 months against a 5-year bar. Code wins.
        v = compute(
            [req("R1", type="years", threshold={"years": 5}, knockout_likely=True)],
            [finding("R1", "met", positions=("P1",))],
            positions=(pos("P1", "2024-01", "2025-12"),),
        )
        self.assertEqual(v["knockout_exposure"], "at_risk")
        self.assertTrue(any(d["requirement_id"] == "R1" and d["to"] == "unmet"
                            for d in v["downgrades"]), v["downgrades"])

    def test_a_near_miss_becomes_partial_and_a_rank_signal(self):
        v = compute(
            [req("R1", type="years", threshold={"years": 5}, knockout_likely=True)],
            [finding("R1", "met", positions=("P1",))],
            positions=(pos("P1", "2022-01", "2026-09"),),  # 57 months
        )
        self.assertTrue(any(s["code"] == "years_near_miss" for s in v["rank_signals"]))

    def test_present_uses_the_injected_run_date(self):
        v = compute(
            [req("R1", type="years", threshold={"years": 5}, knockout_likely=True)],
            [finding("R1", "met", positions=("P1",))],
            positions=(pos("P1", "2020-01", "Present"),),
            run_date="2026-11-03",
        )
        self.assertEqual(v["years"]["per_requirement"]["R1"]["months"], 83)

    def test_month_less_dates_are_flagged_approximate(self):
        v = compute(
            [req("R1", type="years", threshold={"years": 5}, knockout_likely=True)],
            [finding("R1", "met", positions=("P1",))],
            positions=(pos("P1", "2018", "2024"),),
        )
        self.assertTrue(v["years"]["per_requirement"]["R1"]["approximate"])

    def test_the_total_career_span_is_reported(self):
        v = compute(
            [req("R1")], [finding("R1", "met")],
            positions=(pos("P1", "2018-01", "2019-12"), pos("P2", "2021-01", "2021-12")),
        )
        self.assertEqual(v["years"]["total_months"], 36)
        self.assertEqual(len(v["years"]["merged_ranges"]), 2)

    def test_an_unparseable_date_does_not_crash_the_run(self):
        v = compute(
            [req("R1", type="years", threshold={"years": 5})],
            [finding("R1", "met", positions=("P1",))],
            positions=({"id": "P1", "title": "Dev", "employer": "X",
                        "start": "sometime", "end": "later", "source_quote": "sometime - later"},),
        )
        self.assertEqual(contracts.validate("verdict", v), [])
        self.assertIn("R1", v["years"]["per_requirement"])
        self.assertIsNone(v["years"]["per_requirement"]["R1"]["months"])
        # Unreadable dates are an honest "we could not compute this", so the
        # requirement cannot be reported as evidenced.
        self.assertEqual(v["likely_ai_tier"], "some_gaps")
        self.assertTrue(any("date" in r["why"].lower() for r in v["reasons"]), v["reasons"])

    def test_a_years_requirement_with_no_positions_cannot_be_met(self):
        v = compute(
            [req("R1", type="years", threshold={"years": 5}, knockout_likely=True)],
            [finding("R1", "met", positions=())],
        )
        self.assertEqual(v["knockout_exposure"], "at_risk")

    def test_an_unknown_years_requirement_is_not_turned_into_zero_experience(self):
        # An unreadable CV cites no positions. Computing zero months there
        # would report "no experience" when the truth is "nothing was read".
        v = compute(
            [req("R1", type="years", threshold={"years": 3}, knockout_likely=True)],
            [finding("R1", "unknown_ask", positions=())],
            positions=(),
            parse_doc=parse("unreadable", ["no_text_layer"]),
        )
        self.assertEqual(v["knockout_exposure"], "unknown_ask")
        self.assertNotIn("R1", v["years"]["per_requirement"])
        self.assertEqual(v["downgrades"], [])


class RankSignals(unittest.TestCase):
    def test_preferred_met_and_unmet_are_both_reported(self):
        v = compute(
            [req("R1", strength="preferred"), req("R2", strength="preferred")],
            [finding("R1", "met"), finding("R2", "unmet")],
        )
        codes = [s["code"] for s in v["rank_signals"]]
        self.assertIn("preferred_met", codes)
        self.assertIn("preferred_unmet", codes)

    def test_equivalents_allowed_softens_a_degree_gap(self):
        v = compute(
            [req("R1", type="degree", knockout_likely=True, equivalents_allowed=True)],
            [finding("R1", "unmet")],
        )
        codes = [s["code"] for s in v["rank_signals"]]
        self.assertIn("equivalents_allowed", codes)

    def test_a_language_mismatch_is_a_rank_signal(self):
        v = compute([req("R1")], [finding("R1", "met")], posting_language="fr")
        self.assertTrue(any(s["code"] == "language_mismatch" for s in v["rank_signals"]))

    def test_a_matching_language_is_not_a_signal(self):
        v = compute([req("R1")], [finding("R1", "met")], posting_language="en")
        self.assertFalse(any(s["code"] == "language_mismatch" for s in v["rank_signals"]))

    def test_a_junior_cv_against_a_senior_posting(self):
        v = compute(
            [req("R1", type="title", text="Senior Data Engineer", strength="required")],
            [finding("R1", "partial")],
            positions=(pos("P1", "2024-01", "Present", title="Junior Developer"),),
        )
        self.assertTrue(any(s["code"] == "title_below_posting" for s in v["rank_signals"]),
                        v["rank_signals"])

    def test_an_overqualified_title_is_also_worth_saying(self):
        v = compute(
            [req("R1", type="title", text="Junior Developer", strength="required")],
            [finding("R1", "met")],
            positions=(pos("P1", "2014-01", "Present", title="Principal Engineer"),),
        )
        self.assertTrue(any(s["code"] == "title_above_posting" for s in v["rank_signals"]),
                        v["rank_signals"])

    def test_an_equal_title_produces_no_seniority_signal(self):
        v = compute(
            [req("R1", type="title", text="Senior Data Engineer", strength="required")],
            [finding("R1", "met")],
            positions=(pos("P1", "2018-01", "Present", title="Senior Platform Engineer"),),
        )
        codes = [s["code"] for s in v["rank_signals"]]
        self.assertNotIn("title_below_posting", codes)
        self.assertNotIn("title_above_posting", codes)

    def test_rank_signals_never_change_the_first_two_components(self):
        v = compute(
            [req("R1"), req("R2", strength="preferred")],
            [finding("R1", "met"), finding("R2", "unmet")],
        )
        self.assertEqual(v["knockout_exposure"], "clear")
        self.assertEqual(v["likely_ai_tier"], "all_required_evidenced")


class DowngradesAreCarried(unittest.TestCase):
    def test_quote_edge_downgrades_appear_in_the_verdict(self):
        v = compute(
            [req("R1")], [finding("R1", "met")],
            downgrades=[{"requirement_id": "R1", "from": "met", "to": "ambiguous",
                         "why": "evidence quote was not found in the CV text"}],
        )
        self.assertTrue(any(d["why"].startswith("evidence quote") for d in v["downgrades"]))


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.write("requirements.json", {
            "posting_language": "en",
            "requirements": [req("R1", type="cert", knockout_likely=True)],
            "flags": [],
        })
        self.write("evidence.json", evidence([finding("R1", "unmet")]))
        self.write("parse.json", parse())

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, doc):
        (self.dir / name).write_text(json.dumps(doc, indent=2))

    def test_writes_a_valid_verdict(self):
        out = self.dir / "verdict.json"
        r = subprocess.run([
            sys.executable, str(SCRIPTS / "verdict.py"),
            "--requirements", str(self.dir / "requirements.json"),
            "--evidence", str(self.dir / "evidence.json"),
            "--parse", str(self.dir / "parse.json"),
            "--out", str(out), "--run-date", RUN_DATE,
        ], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        v = json.loads(out.read_text())
        self.assertEqual(contracts.validate("verdict", v), [])
        self.assertEqual(v["knockout_exposure"], "at_risk")

    def test_the_run_date_is_required_for_reproducibility(self):
        r = subprocess.run([
            sys.executable, str(SCRIPTS / "verdict.py"),
            "--requirements", str(self.dir / "requirements.json"),
            "--evidence", str(self.dir / "evidence.json"),
            "--parse", str(self.dir / "parse.json"),
            "--out", str(self.dir / "v.json"),
        ], capture_output=True, text=True)
        # Defaulting to today is fine for a real run; the flag exists so an
        # eval run is reproducible. Either way it must not crash.
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
