#!/usr/bin/env python3
"""Tests for `templates/delivery-flow/roster.yaml`: every name in it must resolve.

The roster is a dispatch table, so a name that does not exist is not a typo — it is a story
that silently gets no architect or no reviewer. Nothing at runtime would notice: the resolve
would hand the orchestrator a name, and the orchestrator would try to spawn an agent that is
not there. So the test is the check.

Run: python3 tests/delivery-flow/test_roster.py
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))

from common import load_roster  # noqa: E402

ROSTER_PATH = ROOT / "templates" / "delivery-flow" / "roster.yaml"
ROSTER_DOC = ROOT / "skills" / "delivery-flow" / "references" / "roster.md"

# The closed vocabulary. Paired with `roster.md` and, once it exists, `resolve-roster.py`.
KINDS = ["ux", "frontend", "backend", "contracts", "infra", "data", "mobile", "docs"]
AGENT_KEYS = ["architect", "deploy"]


def agents() -> set:
    return {p.stem for p in (ROOT / "agents").glob("*.md") if p.stem != "README"}


def skills() -> set:
    return {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()}


class TestRoster(unittest.TestCase):
    def setUp(self):
        self.roster = load_roster(ROSTER_PATH)

    def test_the_vocabulary_is_exactly_the_documented_one(self):
        self.assertEqual(sorted(self.roster), sorted(KINDS))

    def test_every_kind_names_its_reviewers(self):
        """A kind of work with no reviewer is a kind of work nobody checks."""
        for kind, entry in self.roster.items():
            with self.subTest(kind=kind):
                self.assertTrue(entry.get("reviewers"), f"{kind} has no reviewers")

    def test_every_kind_names_its_skills(self):
        for kind, entry in self.roster.items():
            with self.subTest(kind=kind):
                self.assertTrue(entry.get("skills"), f"{kind} has no skills")

    def test_every_agent_named_exists(self):
        have = agents()
        for kind, entry in self.roster.items():
            named = [entry.get(k) for k in AGENT_KEYS if entry.get(k)]
            named += list(entry.get("reviewers") or [])
            for name in named:
                with self.subTest(kind=kind, agent=name):
                    self.assertIn(name, have, f"{kind} names agent {name!r}, which does not exist")

    def test_every_skill_named_exists(self):
        have = skills()
        for kind, entry in self.roster.items():
            for name in entry.get("skills") or []:
                with self.subTest(kind=kind, skill=name):
                    self.assertIn(name, have, f"{kind} names skill {name!r}, which does not exist")

    def test_an_absent_architect_is_null_not_a_missing_key(self):
        """`docs` has no architect. Saying so explicitly is the difference between a decision
        and an omission — and the resolve reads a missing key as a mistake."""
        for kind, entry in self.roster.items():
            with self.subTest(kind=kind):
                self.assertIn("architect", entry, f"{kind} does not say who its architect is")

    def test_the_dev_pair_is_not_in_the_roster(self):
        """One test-writer and one implementer build every story. A roster entry naming a
        variant would need the boundary hook duplicated for it."""
        names = set()
        for entry in self.roster.values():
            names |= {entry.get(k) for k in AGENT_KEYS if entry.get(k)}
            names |= set(entry.get("reviewers") or [])
        self.assertNotIn("test-writer", names)
        self.assertNotIn("implementer", names)

    def test_the_reference_documents_the_same_vocabulary(self):
        text = ROSTER_DOC.read_text()
        for kind in KINDS:
            with self.subTest(kind=kind):
                self.assertIn(f"`{kind}`", text, f"roster.md does not mention {kind}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
