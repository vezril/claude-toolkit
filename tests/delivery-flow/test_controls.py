"""The controls harness, enforced rather than reported.

`tests/delivery-flow/controls/run-controls.py` drives the three new controls through the
scripts that run them in production and writes a report. This file is what makes the report's
claims fail a build when they stop being true — the same reason
`tests/workflow/test_readiness_delegation.py` exists alongside its harness.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tests" / "delivery-flow" / "controls" / "run-controls.py"
REPORT = ROOT / "tests" / "delivery-flow" / "controls" / "controls-report.results.json"


def _load():
    spec = importlib.util.spec_from_file_location("run_controls", HARNESS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTheHarnessCannotGoVacuous(unittest.TestCase):
    def setUp(self):
        self.h = _load()

    def test_it_probes_both_polarities(self):
        """A control only ever seen firing proves nothing about when it should stay quiet,
        and the reverse. Both sets must be non-empty."""
        names = {p[0] for p in self.h.PROBES}
        self.assertTrue(self.h.FIRES & names, "no fires-probe is registered")
        self.assertTrue(self.h.QUIET & names, "no quiet-probe is registered")

    def test_every_probe_is_classified(self):
        """An unclassified probe is invisible to the inconclusive check."""
        for name, _fn, _expect in self.h.PROBES:
            with self.subTest(probe=name):
                self.assertIn(name, self.h.FIRES | self.h.QUIET)

    def test_each_control_has_both_a_fires_and_a_quiet_probe(self):
        """Per control, not just overall — the gap that would hide a half-tested one."""
        for control, fires, quiet in (
            ("diff size", "size-ceiling-fires", "size-within-ceiling-quiet"),
            ("test scope", "scope-rejects-uncovered-p0", "scope-accepts-right-scope"),
            ("review verdict", "weakened-review-blocks", "weakened-breakdown-advances"),
            ("review schema", "review-schema-rejects-malformed", "review-schema-accepts-valid"),
        ):
            with self.subTest(control=control):
                names = {p[0] for p in self.h.PROBES}
                self.assertIn(fires, names)
                self.assertIn(quiet, names)


class TestTheCommittedReport(unittest.TestCase):
    def test_it_exists_and_covers_every_probe(self):
        """Adding a probe without regenerating the evidence fails here: the report is group
        5's artifact, and one describing a smaller suite than runs is not evidence of it."""
        self.assertTrue(REPORT.exists(), f"no committed report at {REPORT}")
        data = json.loads(REPORT.read_text())
        recorded = {p["probe"] for p in data["probes"]}
        self.assertEqual(recorded, {p[0] for p in _load().PROBES},
                         "re-run tests/delivery-flow/controls/run-controls.py")

    def test_the_committed_run_was_conclusive_and_green(self):
        data = json.loads(REPORT.read_text())
        self.assertEqual("", data.get("inconclusive", ""))
        for p in data["probes"]:
            with self.subTest(probe=p["probe"]):
                self.assertTrue(p["ok"], f"{p['probe']} recorded as unexpected")


class TestTheDeclarationsTheProbesRestOn(unittest.TestCase):
    """If these drift, the probes keep passing while measuring something else."""

    def setUp(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
        self.D = _mod("g5_descriptor", ROOT / "scripts" / "workflow" / "descriptor.py")
        self.V = _mod("g5_verdict", ROOT / "scripts" / "workflow" / "verdict.py")
        self.desc = self.D.load(ROOT / "skills" / "delivery-flow" / "workflow.yaml")

    def test_review_is_declared_require_addressed_and_the_chain_is_not(self):
        self.assertEqual("require-addressed", self.V.weakened_policy(self.desc, "review"))
        self.assertEqual("advance", self.V.weakened_policy(self.desc, "challenge-breakdown"))

    def test_the_verify_edge_check_is_declared_and_present(self):
        checks = self.desc.get("edge_checks") or {}
        self.assertIn("verify.json", checks)
        self.assertTrue((ROOT / checks["verify.json"]).exists())

    def test_review_is_routed_in_the_full_profile(self):
        steps = [r[1] for r in self.D.step_table(self.desc)]
        self.assertIn("review", steps)
        self.assertLess(steps.index("review"), steps.index("pr-description"),
                        "review must come before the PR description")


def _mod(name, path):
    import sys
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


if __name__ == "__main__":
    unittest.main()
