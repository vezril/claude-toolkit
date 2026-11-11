#!/usr/bin/env python3
"""Closing out an sdlc run, and catching a hand-edit (tasks 7.2, 7.3).

`write-outcome.py` already distinguished completed / punched-out / failed / abandoned and
already detected manual corrections — for delivery-flow. On an sdlc repo it gated on
`is_delivery_repo` and exited 2. That failed *honestly*, unlike the enforcement hook in task
6.3 which recognised the repo and then looked in the wrong directory — but it meant an sdlc run
could never be closed out, and a profile that cannot write a terminal artifact is
indistinguishable from one that stalled.

Task 7.3's verification is the important one here: **hand-edit an artifact to force a gate pass
and confirm the run is marked failed.** Stage 4 counts a quiet fix as a failed run, not a
repair — a pipeline whose number depends on hand-edits has no number.

Run: python3 tests/workflow/test_sdlc_outcome.py
"""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WRITE_OUTCOME = ROOT / "scripts" / "delivery-flow" / "write-outcome.py"

VERDICT = {
    "change": "add-2fa", "verdict": "SURVIVED",
    "attacks": [{"attack": f"a{i}", "method": "m", "result": "failed"} for i in range(3)],
    "findings": [],
}


class Run:
    """An sdlc repo whose readiness segment has produced its verdict."""

    def __init__(self, verdict=None):
        self.dir = Path(tempfile.mkdtemp()).resolve()
        (self.dir / ".git").mkdir()
        (self.dir / ".sdlc.yaml").write_text(
            "profile: readiness\nartifacts:\n  root: sdlc\n  commit: false\n")
        self.item = "SDLC-9"
        self.item_dir = self.dir / "sdlc" / self.item
        self.item_dir.mkdir(parents=True)
        self.verdict_path = self.item_dir / "readiness-verdict.json"
        self.verdict_path.write_text(json.dumps(verdict or VERDICT, indent=2))
        self._trace_edge("readiness-verdict.json", "readiness-review")

    def _trace_edge(self, artifact, step, exit_code=0):
        sha = hashlib.sha256((self.item_dir / artifact).read_bytes()).hexdigest()
        with (self.item_dir / "trace.jsonl").open("a") as f:
            f.write(json.dumps({
                "ts": "2026-11-04T00:00:00+00:00", "item": self.item, "step": step,
                "hook": "check-edge", "artifact": artifact, "sha256": sha,
                "edge": {"name": "schema", "exit": exit_code,
                         "summary": "ok" if exit_code == 0 else "failed"}}) + "\n")

    def punch_out(self):
        (self.item_dir / "punch-out-1.md").write_text(
            "# Punch-out 1: phase-gate\n\n- **Item:** SDLC-9\n\n## Evidence\n\n"
            "readiness is a human gate\n\n## Decision needed\n\nApprove?\n")

    def close(self, *extra):
        return subprocess.run(
            [sys.executable, str(WRITE_OUTCOME), self.item, "--repo", str(self.dir), *extra],
            capture_output=True, text=True)

    def outcome(self):
        p = self.item_dir / "outcome.json"
        return json.loads(p.read_text()) if p.exists() else None


class TestItRunsOnAnSdlcRepoAtAll(unittest.TestCase):
    """7.2 — the gate was `is_delivery_repo`, so this was exit 2 before."""

    def test_it_writes_an_outcome(self):
        r = Run()
        out = r.close()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIsNotNone(r.outcome(), "no outcome.json was written")

    def test_it_writes_into_the_sdlc_artifact_root_not_delivery(self):
        """The directory `artifacts.root` names, not delivery-flow's."""
        r = Run()
        r.close()
        self.assertTrue((r.item_dir / "outcome.json").is_file())
        self.assertFalse((r.dir / "delivery").exists(),
                         "it created delivery/, so it is still using the wrong layout")

    def test_a_repo_opting_into_nothing_is_refused(self):
        """Inertness, and the message must name what is actually missing."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".git").mkdir()
            out = subprocess.run(
                [sys.executable, str(WRITE_OUTCOME), "X-1", "--repo", d],
                capture_output=True, text=True)
            self.assertEqual(out.returncode, 2)
            self.assertIn("opts into no workflow", out.stderr)


class TestTheFourStatuses(unittest.TestCase):
    """7.2 — completed / punched-out / failed / abandoned, on an sdlc run."""

    def test_a_clean_run_completes(self):
        r = Run()
        r.close()
        self.assertEqual(r.outcome()["status"], "completed")

    def test_an_open_punch_out_is_punched_out_not_failed(self):
        """The system worked and the run stopped. Those are different outcomes.

        Counting a human decision as a failure would make every correctly-gated run look like
        a defect, which is the opposite of what the gate is for.
        """
        r = Run()
        r.punch_out()
        r.close()
        self.assertEqual(r.outcome()["status"], "punched-out")

    def test_a_failing_edge_is_failed(self):
        r = Run()
        r._trace_edge("readiness-verdict.json", "readiness-review", exit_code=1)
        r.close()
        self.assertEqual(r.outcome()["status"], "failed")

    def test_abandoned_is_the_only_status_taken_on_trust(self):
        r = Run()
        r.close("--status", "abandoned", "--reason", "deprioritised")
        out = r.outcome()
        self.assertEqual(out["status"], "abandoned")
        self.assertIn("deprioritised", json.dumps(out))


class TestManualCorrectionIsCaught(unittest.TestCase):
    """7.3 — hand-edit an artifact to force a gate pass; the run must be marked failed."""

    def test_editing_the_verdict_after_its_edge_fails_the_run(self):
        """The exact attack: a WEAKENED verdict blocks, so rewrite it to SURVIVED.

        The edge already ran and recorded the sha of what it saw. The artifact now looks
        perfect and the run is still failed, because the number has to count the edit.
        """
        weakened = dict(VERDICT, verdict="WEAKENED",
                        findings=[{"finding": "f", "evidence": "e"}])
        r = Run(verdict=weakened)
        # ... then a hand-edit that makes it pass, after the edge saw it.
        r.verdict_path.write_text(json.dumps(VERDICT, indent=2))
        r.close()
        out = r.outcome()
        self.assertEqual(out["status"], "failed")
        self.assertIn("manual-correction", json.dumps(out))

    def test_an_untouched_run_is_not_accused(self):
        """The detector must not fire on a clean run, or every outcome is failed."""
        r = Run()
        r.close()
        self.assertEqual(r.outcome()["status"], "completed")
        self.assertNotIn("manual-correction", json.dumps(r.outcome()))

    def test_the_corrected_artifact_is_named(self):
        """"Something was edited" is not actionable; which artifact is."""
        r = Run(verdict=dict(VERDICT, verdict="WEAKENED",
                             findings=[{"finding": "f", "evidence": "e"}]))
        r.verdict_path.write_text(json.dumps(VERDICT, indent=2))
        r.close()
        self.assertIn("readiness-verdict.json", json.dumps(r.outcome()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
