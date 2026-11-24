"""Replayed runs are counted and disclosed.

Re-running the flow over an already-closed ticket gathers volume for criterion 4. It is a real
run — real nodes, real edges, real artifacts — and for the analysis-only `triage` profile it
exercises exactly what the end-to-end rate measures, so it is not excluded.

It is also **not a delivery**, and a reviewer reading "100% over n=20" will assume live work.
The flag exists so that disclosure is a field in the evidence rather than something a human has
to remember to say at submission time.

The flag is set by the caller, because nothing on disk distinguishes a replay from a first run:
the artifacts are identical. That makes it the one claim in `outcome.json` taken on trust,
which is why it is recorded rather than inferred.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"

TRIAGE = {"item": "X-1", "type": "bug", "path": "quick", "domains": ["docs"],
          "summary": "s", "rationale": "r", "handoff": False,
          "architecture_change": False, "breaking_change": False}


def _repo():
    d = Path(tempfile.mkdtemp())
    (d / ".git").mkdir()
    runs = d / "runs"
    (runs / "X-1").mkdir(parents=True)
    (d / ".delivery-flow.yaml").write_text(
        f"profile: triage\nartifacts:\n  root: {runs}\n  commit: false\n")
    item = runs / "X-1"
    (item / "item.json").write_text(json.dumps({"item": "X-1"}))
    (item / "triage.json").write_text(json.dumps(TRIAGE))
    (item / "project-context.json").write_text(json.dumps({"item": "X-1"}))
    (item / "summary.md").write_text("# brief\n")
    return d, item


def _outcome(repo, *flags):
    out = subprocess.run([sys.executable, str(SCRIPTS / "write-outcome.py"), "X-1",
                          "--repo", str(repo), "--json", "--dry-run", *flags],
                         capture_output=True, text=True)
    try:
        return json.loads(out.stdout), out.returncode
    except json.JSONDecodeError:
        return {}, out.returncode


class TestTheFlagIsRecorded(unittest.TestCase):
    def test_replay_sets_the_field(self):
        repo, _ = _repo()
        doc, code = _outcome(repo, "--replay")
        self.assertEqual(0, code)
        self.assertIs(True, doc.get("replay"))

    def test_the_field_is_absent_without_the_flag(self):
        """Absent rather than `false`: an outcome written before this field existed must not
        read as an asserted first run."""
        repo, _ = _repo()
        doc, _ = _outcome(repo)
        self.assertNotIn("replay", doc)

    def test_the_flag_does_not_change_the_status(self):
        """A replay that completes is `completed`. The flag discloses what the run was, it
        does not grade it."""
        repo, _ = _repo()
        plain, _ = _outcome(repo)
        replay, _ = _outcome(repo, "--replay")
        self.assertEqual(plain["status"], replay["status"])

    def test_the_schema_accepts_it(self):
        """`additionalProperties: false`, so an undeclared field would fail the edge."""
        repo, item = _repo()
        subprocess.run([sys.executable, str(SCRIPTS / "write-outcome.py"), "X-1",
                        "--repo", str(repo), "--replay"], capture_output=True)
        out = subprocess.run([sys.executable, str(SCRIPTS / "validate-artifact.py"),
                              str(item / "outcome.json")], capture_output=True, text=True)
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)


class TestTheReportDisclosesTheSplit(unittest.TestCase):
    def _report(self, replays, live):
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        runs = d / "runs"
        runs.mkdir()
        (d / ".delivery-flow.yaml").write_text(
            f"profile: triage\nartifacts:\n  root: {runs}\n  commit: false\n")
        for name, is_replay in [(f"R-{i}", True) for i in range(replays)] + \
                               [(f"L-{i}", False) for i in range(live)]:
            item = runs / name
            item.mkdir()
            doc = {"item": name, "profile": "triage", "status": "completed", "step": "report",
                   "ts": "2026-11-24T00:00:00+00:00", "manual_corrections": []}
            if is_replay:
                doc["replay"] = True
            (item / "outcome.json").write_text(json.dumps(doc))
            (item / "trace.jsonl").write_text(json.dumps({
                "ts": "2026-11-24T00:00:00+00:00", "item": name, "step": "triage",
                "hook": "trace-step", "model": "claude-sonnet-5-5", "certified": True,
                "input_tokens": 1, "output_tokens": 1, "api_equivalent_cost_usd": 0.01}) + "\n")
        spec = importlib.util.spec_from_file_location(
            "delivery_report", SCRIPTS / "delivery-report.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        s = mod.summarize(mod.collect([d]))
        return mod.markdown(s, "2026-09-15"), s

    def test_it_states_the_count_when_there_are_replays(self):
        md, _ = self._report(replays=2, live=1)
        self.assertIn("**2 of 3** terminal runs were **replays**", md)

    def test_it_names_each_replayed_item(self):
        """A count without the items cannot be audited against the run directories."""
        md, _ = self._report(replays=2, live=1)
        self.assertIn("`R-0`", md)
        self.assertIn("`R-1`", md)

    def test_it_says_so_explicitly_when_there_are_none(self):
        """Silence would read the same as "nobody checked"."""
        md, _ = self._report(replays=0, live=2)
        self.assertIn("were first runs on live tickets", md)
        self.assertIn("No replays", md)

    def test_replays_are_counted_in_the_rate_not_excluded(self):
        """The deliberate choice: a replay exercises what the rate measures."""
        _, s = self._report(replays=2, live=1)
        self.assertEqual(3, s["overall"]["all"]["completed"])

    def test_the_section_precedes_any_rate_computed_over_it(self):
        """A reader must meet the denominator's composition before its rates."""
        md, _ = self._report(replays=1, live=1)
        self.assertLess(md.index("## What the runs were"), md.index("## End-to-end rate"))


if __name__ == "__main__":
    unittest.main()
