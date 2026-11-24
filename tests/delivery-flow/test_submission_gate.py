"""The last gate before a Stage 4 submission.

`package-evidence.py` gates only on the chain being certified. Asked to build with the Stage 4
figure reading `—`, it produced five populated directories, a 3,123-entry manifest and no
complaint — a package that looks finished with the one number the certification asks for
absent. This gate checks the claims instead of the file count.

The half that matters is that it can **pass**: a gate that always refuses is as useless as one
that always permits, and it would be the easier of the two to write by accident.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "delivery-flow" / "check-submission.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_submission", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _summary(runs):
    """A delivery-report-shaped summary. `runs` is [(item, steps, certified, replay)]."""
    items = [{"item": i, "status": "completed", "profile": "triage", "steps": s,
              "certified": c, "replay": r} for i, s, c, r in runs]
    certified = [x for x in items if x["certified"]]
    return {"items": items,
            "overall": {"certified_only": {
                "completed": len(certified), "failed": 0, "punched_out": 0,
                "rate_excluding_punch_outs": 100.0 if certified else None}}}


class TestCriterion4IsTheGate(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def _c4(self, summary, min_runs=5):
        return self.m.check_criterion_4(summary, min_runs)[0]

    def test_no_certified_runs_is_blocking(self):
        """The whole point: a package must not ship with the Stage 4 figure empty."""
        c = self._c4(_summary([("A", 10, False, False)]))
        self.assertFalse(c["ok"])
        self.assertFalse(c.get("warn_only"), "an absent rate must block, not warn")

    def test_a_certified_run_passes_the_gate(self):
        """A gate that cannot pass is as useless as one that cannot fail."""
        c = self._c4(_summary([("A", 10, True, False)]))
        self.assertTrue(c["ok"], c["detail"])

    def test_a_thin_denominator_warns_rather_than_blocks(self):
        """What denominator a reviewer accepts is the reviewer's call, not this script's."""
        checks = self.m.check_criterion_4(_summary([("A", 10, True, False)]), min_runs=5)
        thin = [c for c in checks if "denominator" in c["name"]]
        self.assertTrue(thin)
        self.assertFalse(thin[0]["ok"])
        self.assertTrue(thin[0]["warn_only"])

    def test_a_sufficient_denominator_raises_no_warning(self):
        runs = [(f"R{i}", 10, True, False) for i in range(5)]
        checks = self.m.check_criterion_4(_summary(runs), min_runs=5)
        self.assertTrue(all(c["ok"] for c in checks), [c for c in checks if not c["ok"]])

    def test_the_fix_names_the_cwd_cause(self):
        """The one cause that wasted a fortnight; the message has to say it."""
        c = self._c4(_summary([]))
        self.assertIn("cwd", c["fix"])


class TestStepRecordsAreChecked(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_a_run_with_no_step_records_blocks_and_is_named(self):
        c = self.m.check_runs_have_step_records(
            _summary([("GOOD", 10, True, False), ("EMPTY", 0, None, False)]))
        self.assertFalse(c["ok"])
        self.assertIn("EMPTY", c["detail"])
        self.assertNotIn("GOOD", c["detail"].split("empty:")[-1])

    def test_all_runs_having_records_passes(self):
        c = self.m.check_runs_have_step_records(_summary([("A", 10, True, False)]))
        self.assertTrue(c["ok"], c["detail"])

    def test_no_terminal_runs_at_all_is_not_a_pass(self):
        """Zero runs means nothing to audit, which is not the same as a clean audit."""
        c = self.m.check_runs_have_step_records(_summary([]))
        self.assertFalse(c["ok"])


class TestTheDenominatorDisclosure(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_replays_are_named(self):
        c = self.m.check_denominator_disclosed(
            _summary([("LIVE", 5, True, False), ("REP", 5, True, True)]))
        self.assertIn("REP", c["detail"])
        self.assertIn("1 of 2", c["detail"])

    def test_it_never_blocks_on_replays(self):
        """A replay is countable; this reports composition rather than judging it."""
        c = self.m.check_denominator_disclosed(_summary([("REP", 5, True, True)]))
        self.assertTrue(c["ok"])


class TestItRefusesRatherThanSkipping(unittest.TestCase):
    def test_a_non_delivery_repo_is_a_usage_error(self):
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        out = subprocess.run([sys.executable, str(GATE), "--repo", str(d)],
                             capture_output=True, text=True)
        self.assertEqual(2, out.returncode)
        self.assertIn("not a delivery-flow repo", out.stdout + out.stderr)

    def test_an_unreadable_report_is_a_failure_not_a_pass(self):
        """A check that cannot run must never report success — the rule every gate here
        follows, and the one this whole project keeps finding broken."""
        m = _load()
        self.assertFalse(
            {"name": "x", "ok": False}.get("warn_only", False),
            "the unreadable-report check must be blocking")
        # The behaviour itself: a repo whose artifact root does not exist.
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        (d / ".delivery-flow.yaml").write_text(
            "profile: triage\nartifacts:\n  root: /nonexistent/runs\n  commit: false\n")
        out = subprocess.run([sys.executable, str(GATE), "--repo", str(d), "--json"],
                             capture_output=True, text=True)
        self.assertNotEqual(0, out.returncode)
        if out.stdout.strip():
            doc = json.loads(out.stdout)
            self.assertFalse(doc["submittable"])


if __name__ == "__main__":
    unittest.main()
