"""The roster resolve, and the review step's routing through it.

`skills/delivery-flow/references/roster.md` has documented `resolve-roster.py` since the
roster was written and the script did not exist, so the roster's `reviewers:` field was
declared, documented, and dispatched by nothing. The `review` step is its first consumer.

The cases that matter here are the refusals. A resolve that silently returns no reviewer is
exactly how the review step becomes decorative: the run looks reviewed, and nobody read the
diff.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOLVE = ROOT / "scripts" / "delivery-flow" / "resolve-roster.py"


def _load():
    spec = importlib.util.spec_from_file_location("resolve_roster", RESOLVE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cli(*args):
    out = subprocess.run([sys.executable, str(RESOLVE), *args], capture_output=True, text=True)
    return out.returncode, (out.stdout or "") + (out.stderr or "")


class TestTheResolve(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_every_kind_in_the_vocabulary_resolves_to_a_reviewer(self):
        """The guarantee the review step depends on: no kind dispatches to nobody."""
        for kind in self.m.KINDS:
            with self.subTest(kind=kind):
                out = self.m.resolve([kind])
                self.assertTrue(out["reviewers"], f"{kind} resolves to no reviewer")

    def test_reviewers_are_de_duplicated_across_kinds(self):
        out = self.m.resolve(["frontend", "ux"])
        self.assertEqual(len(out["reviewers"]), len(set(out["reviewers"])))
        self.assertIn("frontend-reviewer", out["reviewers"])

    def test_skills_are_unioned_in_declared_order(self):
        out = self.m.resolve(["backend", "docs"])
        self.assertEqual(len(out["skills"]), len(set(out["skills"])))
        self.assertIn("scala", out["skills"])

    def test_a_kind_with_no_architect_is_not_an_error(self):
        """`docs` declares `architect: null` deliberately — no architecture step for it."""
        out = self.m.resolve(["docs"])
        self.assertIsNone(out["architects"]["docs"])
        self.assertTrue(out["reviewers"])


class TestItRefuses(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_a_kind_outside_the_vocabulary_is_refused(self):
        with self.assertRaises(ValueError) as cm:
            self.m.resolve(["poster"])
        self.assertIn("outside the vocabulary", str(cm.exception))

    def test_an_entry_with_no_reviewer_is_an_error_not_a_skip(self):
        """The failure this script exists to prevent. An override that drops every reviewer
        must stop the resolve, not quietly produce a run with no review."""
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        (d / ".delivery-flow.yaml").write_text(
            "roster_overrides:\n"
            "  backend:\n"
            "    architect: solution-architect\n"
            "    skills: [scala]\n"
            "    reviewers: []\n")
        with self.assertRaises(ValueError) as cm:
            self.m.resolve(["backend"], repo=d)
        self.assertIn("names no reviewer", str(cm.exception))

    def test_an_override_replaces_rather_than_merges(self):
        """roster.md promises replacement. A merge would let a plugin reviewer survive a
        repo's decision to drop it, which is the opposite of an override."""
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        (d / ".delivery-flow.yaml").write_text(
            "roster_overrides:\n"
            "  backend:\n"
            "    architect: solution-architect\n"
            "    skills: [scala]\n"
            "    reviewers: [clean-code-reviewer]\n")
        out = self.m.resolve(["backend"], repo=d)
        self.assertEqual(["clean-code-reviewer"], out["reviewers"],
                         "scala-fp-reviewer survived an override that dropped it")

    def test_the_cli_exits_nonzero_on_a_bad_kind(self):
        code, out = _cli("poster")
        self.assertEqual(code, 1, out)

    def test_the_cli_refuses_both_or_neither_input(self):
        self.assertEqual(_cli()[0], 2)
        self.assertEqual(_cli("backend", "--from-proposal", "x.json")[0], 2)

    def test_a_missing_repo_config_means_no_overrides_not_a_crash(self):
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        out = self.m.resolve(["backend"], repo=d)
        self.assertIn("scala-fp-reviewer", out["reviewers"])


class TestTheReviewVerdictRoutes(unittest.TestCase):
    """1.8 — review.json travels the same route as the other challenge artifacts."""

    def test_review_is_registered_as_a_routed_verdict(self):
        spec = importlib.util.spec_from_file_location(
            "flow_status", ROOT / "scripts" / "delivery-flow" / "flow-status.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertIn("review.json", mod.CHALLENGES)
        target, step = mod.CHALLENGES["review.json"]
        self.assertEqual(("implementation.json", "implementation"), (target, step),
                         "the diff is not traced, so implementation.json is the stand-in")


if __name__ == "__main__":
    unittest.main()
