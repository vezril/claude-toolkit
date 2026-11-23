"""The diff-size ceilings.

This is the only punch-out trigger with **no flag path**. `scope`, `architecture` and
`breaking` each fire on a node's claim *or* on a derivation, and record a disagreement where
the two differ. There is no artifact field claiming a diff's size, so rewording an artifact
cannot move this one — which makes it the strongest of the set and the simplest to test.

Three answers that must never collapse into two: over a ceiling, inside every ceiling, and
not determinable. An unmeasured diff reading the same as a small one is the failure mode.
"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = {"punch_out": {"max_diff_files": 25, "max_diff_lines": 800}}


def _triggers():
    spec = importlib.util.spec_from_file_location(
        "triggers", ROOT / "scripts" / "delivery-flow" / "triggers.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTheCeilings(unittest.TestCase):
    def setUp(self):
        self.t = _triggers()

    def _fired(self, stat, cfg=CFG):
        return self.t.derive_diff(stat, cfg)["diff-size"]

    def test_a_change_inside_both_ceilings_does_not_fire(self):
        v = self._fired({"files": 10, "lines": 200})
        self.assertIs(v["fired"], False)

    def test_too_many_files_fires(self):
        v = self._fired({"files": 30, "lines": 200})
        self.assertIs(v["fired"], True)
        self.assertIn("30 files", v["evidence"])

    def test_too_many_lines_fires(self):
        v = self._fired({"files": 5, "lines": 2000})
        self.assertIs(v["fired"], True)
        self.assertIn("2000 lines", v["evidence"])

    def test_either_ceiling_alone_is_enough(self):
        """Breaching one must fire even while the other is comfortably inside."""
        self.assertIs(self._fired({"files": 999, "lines": 1})["fired"], True)
        self.assertIs(self._fired({"files": 1, "lines": 99999})["fired"], True)

    def test_exactly_at_the_ceiling_does_not_fire(self):
        """A ceiling is a maximum, not a forbidden value — pinned so it cannot drift."""
        self.assertIs(self._fired({"files": 25, "lines": 800})["fired"], False)

    def test_the_measurement_is_recorded_either_way(self):
        """The punch-out has to carry its own evidence: a reader must not need to
        recompute the diff to see why it fired, or why it did not."""
        for stat in ({"files": 10, "lines": 200}, {"files": 30, "lines": 900}):
            with self.subTest(stat=stat):
                self.assertIn(str(stat["files"]), self._fired(stat)["evidence"])


class TestUndeterminedIsNotNo(unittest.TestCase):
    def setUp(self):
        self.t = _triggers()

    def test_no_configured_ceiling_is_undetermined(self):
        """An absent ceiling is reported, never read as permission for any size."""
        v = self.t.derive_diff({"files": 999, "lines": 99999}, {})["diff-size"]
        self.assertIsNone(v["fired"])
        self.assertIn("not a statement that it is small", v["evidence"])

    def test_an_unmeasurable_diff_is_undetermined(self):
        v = self.t.derive_diff({}, CFG)["diff-size"]
        self.assertIsNone(v["fired"])
        self.assertIn("not a small one", v["evidence"])

    def test_one_ceiling_configured_still_measures_that_one(self):
        v = self.t.derive_diff({"files": 30, "lines": 1},
                               {"punch_out": {"max_diff_files": 25}})["diff-size"]
        self.assertIs(v["fired"], True)

    def test_a_non_numeric_ceiling_is_undetermined_not_zero(self):
        """A ceiling of `"many"` read as 0 would fire on every change."""
        v = self.t.derive_diff({"files": 1, "lines": 1},
                               {"punch_out": {"max_diff_files": "many"}})["diff-size"]
        self.assertIsNone(v["fired"])


class TestTheMeasurement(unittest.TestCase):
    """`diff_stat` against a real git repo — the derivation above is pure, this is not."""

    def setUp(self):
        self.t = _triggers()
        self.d = Path(tempfile.mkdtemp())
        run = lambda *a: subprocess.run(a, cwd=self.d, capture_output=True)
        run("git", "init", "-q", "-b", "main")
        run("git", "config", "user.email", "t@t")
        run("git", "config", "user.name", "t")
        (self.d / "a.txt").write_text("one\ntwo\nthree\n")
        run("git", "add", "-A")
        run("git", "commit", "-qm", "base")
        run("git", "checkout", "-q", "-b", "work")

    def test_it_counts_changed_files_and_lines(self):
        (self.d / "a.txt").write_text("one\ntwo\nfour\n")
        (self.d / "b.txt").write_text("new\n")
        subprocess.run(["git", "add", "-A"], cwd=self.d, capture_output=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "work"], cwd=self.d, capture_output=True)
        stat = self.t.diff_stat(self.d, "main")
        self.assertEqual(2, stat["files"])
        self.assertGreater(stat["lines"], 0)

    def test_deletions_count_toward_the_line_total(self):
        """A change that deletes 900 lines is as much to review as one that adds them."""
        (self.d / "a.txt").write_text("")
        subprocess.run(["git", "add", "-A"], cwd=self.d, capture_output=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "delete"], cwd=self.d, capture_output=True)
        self.assertGreaterEqual(self.t.diff_stat(self.d, "main")["lines"], 3)

    def test_a_non_repo_measures_nothing_rather_than_raising(self):
        """Which the derivation then reports as undetermined, not as small."""
        self.assertEqual({}, self.t.diff_stat(Path(tempfile.mkdtemp()), "main"))


if __name__ == "__main__":
    unittest.main()
