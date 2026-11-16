#!/usr/bin/env python3
"""Tests that the contracts stay internally consistent and documented.

The point of contracts.py is that one definition drives both the checker and
the page the model reads. These tests are what stop that from quietly becoming
two definitions.

Run: python3 tests/application-review/test_contracts.py
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "application-review"
sys.path.insert(0, str(SCRIPTS))

import contracts  # noqa: E402
import gen_contracts_doc  # noqa: E402


class DocIsInSync(unittest.TestCase):
    def test_the_reference_matches_the_module(self):
        path = gen_contracts_doc.DOC_PATH
        self.assertTrue(
            path.exists(),
            f"{path} is missing. Run: python3 scripts/application-review/gen_contracts_doc.py --write",
        )
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            gen_contracts_doc.generate(),
            "contracts.md is out of date. Run: "
            "python3 scripts/application-review/gen_contracts_doc.py --write",
        )

    def test_the_doc_mentions_every_contract_file(self):
        text = gen_contracts_doc.generate()
        for name in contracts.STEP_ORDER:
            with self.subTest(contract=name):
                self.assertIn(contracts.CONTRACTS[name]["file"], text)

    def test_the_doc_mentions_every_enum_value(self):
        # A closed vocabulary the model is never shown is a trap.
        text = gen_contracts_doc.generate()
        for group in (
            contracts.REQUIREMENT_TYPES, contracts.STRENGTHS, contracts.MODEL_STATUSES,
            contracts.RECOMMENDATION_KINDS, contracts.PARSE_HEALTH,
            contracts.KNOCKOUT_EXPOSURE, contracts.AI_TIERS, contracts.LANGUAGES,
            contracts.RANK_SIGNAL_CODES, contracts.FLAG_CODES, contracts.REFUSAL_CODES,
            list(contracts.PARSE_SIGNALS),
        ):
            for value in group:
                with self.subTest(value=value):
                    self.assertIn(f"`{value}`", text)


class Structure(unittest.TestCase):
    def test_every_contract_has_the_metadata_the_doc_needs(self):
        for name, contract in contracts.CONTRACTS.items():
            with self.subTest(contract=name):
                for key in ("file", "step", "written_by", "purpose", "root"):
                    self.assertIn(key, contract)

    def test_step_order_covers_every_contract(self):
        self.assertEqual(sorted(contracts.STEP_ORDER), sorted(contracts.CONTRACTS))

    def test_ambiguous_is_edge_only(self):
        # The one status the model must not write. If this ever lands in
        # MODEL_STATUSES, the quote edge stops being able to tell a confirmed
        # match from an unconfirmed one.
        self.assertNotIn("ambiguous", contracts.MODEL_STATUSES)
        self.assertIn("ambiguous", contracts.POST_EDGE_STATUSES)

    def test_every_knockout_type_is_a_requirement_type(self):
        for t in contracts.KNOCKOUT_TYPES:
            with self.subTest(type=t):
                self.assertIn(t, contracts.REQUIREMENT_TYPES)

    def test_every_signal_severity_is_legal(self):
        for code, (severity, detail) in contracts.PARSE_SIGNALS.items():
            with self.subTest(code=code):
                self.assertIn(severity, contracts.SIGNAL_SEVERITIES)
                self.assertTrue(detail.endswith("."), f"{code}: detail should be a sentence")

    def test_no_contract_has_a_score_field(self):
        # Design D1: there is no number. A field named like one would invite a
        # renderer or a model to produce it.
        def walk(spec, path=""):
            for name, child in (spec.get("fields") or {}).items():
                full = f"{path}.{name}"
                for banned in ("score", "percent", "rating", "fit"):
                    self.assertNotIn(banned, name.lower(), f"{full} looks like a score")
                walk(child, full)
                if child.get("items"):
                    walk(child["items"], full + "[]")

        for name, contract in contracts.CONTRACTS.items():
            with self.subTest(contract=name):
                walk(contract["root"], name)


class ValidatorEdgeCases(unittest.TestCase):
    def test_an_unknown_contract_raises(self):
        with self.assertRaises(KeyError):
            contracts.validate("nope", {})

    def test_a_non_object_root_is_reported(self):
        self.assertTrue(contracts.validate("requirements", []))
        self.assertTrue(contracts.validate("requirements", "text"))

    def test_a_boolean_is_not_an_integer(self):
        spec = {"type": "integer", "required": True}
        problems = []
        contracts._check(True, spec, "x", problems)
        self.assertTrue(problems)

    def test_free_form_objects_accept_anything(self):
        spec = {"type": "object", "free_form": True, "required": True}
        problems = []
        contracts._check({"whatever": [1, 2]}, spec, "x", problems)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
