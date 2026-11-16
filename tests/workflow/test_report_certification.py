#!/usr/bin/env python3
"""The report's certification claim, on two workflows (task 7.4).

`delivery-report.py` produces the Stage 4 numbers. Two defects found by pointing it at an sdlc
repo, both the same class as the gates in sections 5 and 6 — present, successful, checking
nothing:

1. **It could not see an sdlc run at all.** `trace_files` gated on `is_delivery_repo` and
   globbed a hard-coded `delivery/`. That one is loud (`main` exits non-zero on no items rather
   than printing 0%), but "no runs exist" and "this report cannot see the runs that exist" are
   different facts.

2. **An unrecognised uncertified step was silently excluded from the certification claim.**
   `certifiable()` asked whether the step's kind was in `CERTIFIABLE_KINDS`; a step absent from
   the table answered `False`, identical to a deterministic producer, so it was set aside and
   the run still counted toward the certified-only rate. Invisible while delivery-flow was the
   only workflow. With two, every sdlc node was an unknown step — and worse, the sdlc routing
   table is keyed by *segment* while the trace records the *node*, so even reading both
   descriptors left all eleven node names unrecognised.

Defect 2 is the one that matters: it inflates the number in the direction of claiming a
certification nobody made.

Run: python3 tests/workflow/test_report_certification.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))

_spec = importlib.util.spec_from_file_location(
    "delivery_report", ROOT / "scripts" / "delivery-flow" / "delivery-report.py")
report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(report)


def step_record(step, certified, **extra):
    return {"ts": "2026-11-04T00:00:00+00:00", "item": "SDLC-9", "step": step,
            "hook": "trace-step", "model": "claude-haiku-5-5", "certified": certified,
            "input_tokens": 100, "output_tokens": 50, "api_equivalent_cost_usd": 0.001,
            **extra}


def sdlc_repo(records, status="completed", profile="readiness", artifacts_root=None):
    """An sdlc repo with one run. `artifacts_root` absolute puts the run outside the repo."""
    d = Path(tempfile.mkdtemp()).resolve()
    (d / ".git").mkdir()
    root = str(artifacts_root) if artifacts_root else "sdlc"
    (d / ".sdlc.yaml").write_text(
        f"profile: readiness\nartifacts:\n  root: {root}\n  commit: false\n")
    item = Path(root) if artifacts_root else d / "sdlc"
    item = item / "SDLC-9"
    item.mkdir(parents=True)
    (item / "trace.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in records))
    (item / "outcome.json").write_text(json.dumps(
        {"item": "SDLC-9", "status": status, "profile": profile,
         "ts": "2026-11-04T00:00:00+00:00"}))
    return d


def one_row(repo):
    items = report.collect([repo])
    s = report.summarize(items)
    assert len(s["items"]) == 1, f"expected one run, got {len(s['items'])}"
    return s["items"][0], s


class TestItCanSeeAnSdlcRun(unittest.TestCase):
    """Defect 1 — the numbers come from here, so invisibility is a wrong number."""

    def test_trace_files_finds_a_run_in_the_sdlc_artifact_root(self):
        repo = sdlc_repo([step_record("readiness-review", True)])
        self.assertEqual(1, len(report.trace_files(repo)))

    def test_it_finds_a_run_whose_artifacts_live_outside_the_repo(self):
        """The real configuration: `artifacts.root` is absolute, pointing at the vault.

        An in-repo fixture cannot show this working — a plain `<repo>/sdlc/*/trace.jsonl` glob
        finds those runs whether or not the config is ever read. Only an absolute root proves
        the report resolves `artifacts.root` instead of guessing the directory name.
        """
        vault = Path(tempfile.mkdtemp()).resolve() / "vault-runs"
        repo = sdlc_repo([step_record("readiness-review", True)], artifacts_root=vault)
        found = report.trace_files(repo)
        self.assertEqual([vault / "SDLC-9" / "trace.jsonl"], found)

    def test_a_run_outside_the_repo_reaches_the_numbers(self):
        """Discovery is not the point; the rate is."""
        vault = Path(tempfile.mkdtemp()).resolve() / "vault-runs"
        repo = sdlc_repo([step_record("readiness-review", True)], artifacts_root=vault)
        row, s = one_row(repo)
        self.assertEqual("SDLC-9", row["item"])
        self.assertEqual(1, s["per_profile"]["readiness"]["certified_only"]["completed"])

    def test_it_still_finds_a_delivery_flow_run(self):
        d = Path(tempfile.mkdtemp()).resolve()
        (d / ".git").mkdir()
        (d / ".delivery-flow.yaml").write_text("profile: triage\n")
        item = d / "delivery" / "PRO-1"
        item.mkdir(parents=True)
        (item / "trace.jsonl").write_text(json.dumps(step_record("triage", True)) + "\n")
        self.assertEqual(1, len(report.trace_files(d)))

    def test_the_cli_reports_rather_than_refusing(self):
        repo = sdlc_repo([step_record("readiness-review", True)])
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts/delivery-flow/delivery-report.py"),
             str(repo), "--json"], capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("SDLC-9", r.stdout)


class TestAnUnrecognisedStepRefusesTheClaim(unittest.TestCase):
    """Defect 2, the one that inflates the number."""

    def test_an_unknown_uncertified_step_disqualifies_the_run(self):
        repo = sdlc_repo([step_record("some-step-nobody-declared", False)])
        row, _ = one_row(repo)
        self.assertFalse(row["certified"],
                         "an uncertified step the report does not recognise was waved through")

    def test_it_is_named_as_unknown_not_as_deliberately_excluded(self):
        """Two different facts. One bucket is how the first version hid this."""
        repo = sdlc_repo([step_record("some-step-nobody-declared", False)])
        row, _ = one_row(repo)
        self.assertEqual(["some-step-nobody-declared"], row["unknown_steps"])
        self.assertEqual([], row["excluded_from_certification"])

    def test_an_unknown_run_is_outside_the_certified_only_rate(self):
        """The claim, not just the label: it must not reach the Stage 4 numerator."""
        repo = sdlc_repo([step_record("some-step-nobody-declared", False)])
        _, s = one_row(repo)
        certified = s["per_profile"]["readiness"]["certified_only"]
        self.assertEqual(0, certified["completed"])
        self.assertEqual(1, s["per_profile"]["readiness"]["all"]["completed"])


class TestTheSdlcNodeNamesAreRecognised(unittest.TestCase):
    """The trace records a node; the sdlc routing table is keyed by segment."""

    NODES = ("analysis", "planning", "planning-review", "solutioning", "solutioning-review",
             "readiness", "readiness-review", "implementation", "implementation-green",
             "verification", "verification-ci")

    def test_every_declared_sdlc_node_resolves_as_a_node(self):
        for node in self.NODES:
            with self.subTest(node=node):
                self.assertEqual("node", report.certification_role(node))

    def test_an_uncertified_sdlc_node_disqualifies_and_is_named_as_a_node(self):
        repo = sdlc_repo([step_record("readiness-review", False)])
        row, _ = one_row(repo)
        self.assertFalse(row["certified"])
        self.assertEqual(["readiness-review"], row["uncertified_nodes"])

    def test_a_certified_sdlc_run_counts_toward_the_certified_rate(self):
        """The other direction: the fix must not make every sdlc run uncertifiable."""
        repo = sdlc_repo([step_record("readiness", True),
                          step_record("readiness-review", True)])
        row, s = one_row(repo)
        self.assertTrue(row["certified"])
        self.assertEqual(1, s["per_profile"]["readiness"]["certified_only"]["completed"])


class TestTheDeliberateExclusionsSurvive(unittest.TestCase):
    """Regression guard: the documented orchestrator fix must not be undone by the above."""

    def test_the_orchestrator_is_still_excluded_by_name(self):
        repo = sdlc_repo([step_record("readiness-review", True),
                          step_record("orchestrator", False)])
        row, _ = one_row(repo)
        self.assertTrue(row["certified"],
                        "the orchestrator disqualified the run again — a rate of 0/0")
        self.assertEqual(["orchestrator"], row["excluded_from_certification"])

    def test_a_deterministic_producer_is_still_excluded(self):
        repo = sdlc_repo([step_record("report", False)])
        row, _ = one_row(repo)
        self.assertTrue(row["certified"])
        self.assertEqual(["report"], row["excluded_from_certification"])

    def test_exclusions_are_a_closed_named_set_not_a_fallback(self):
        """If this ever grows silently, an unknown step is being excluded again."""
        self.assertEqual({"orchestrator"}, report.NOT_CERTIFIABLE_BY_DESIGN)


class TestBothDenominatorReadings(unittest.TestCase):
    """Design D8 — a punch-out is emitted both inside and outside the denominator."""

    def test_a_punched_out_sdlc_run_appears_in_both_readings(self):
        repo = sdlc_repo([step_record("readiness-review", True)], status="punched-out")
        _, s = one_row(repo)
        r = s["per_profile"]["readiness"]["all"]
        self.assertEqual(1, r["punched_out"])
        self.assertIsNone(r["rate_excluding_punch_outs"],
                          "no completed and no failed runs is no rate, not 0%")
        self.assertEqual(0.0, r["rate_counting_punch_outs"])

    def test_the_two_readings_differ_when_a_punch_out_is_present(self):
        """The whole point of emitting both: they must not be the same number."""
        repo = sdlc_repo([step_record("readiness-review", True)], status="punched-out")
        items = report.collect([repo])
        extra = sdlc_repo([step_record("readiness-review", True)], status="completed")
        items.update({f"OTHER-{k}": v for k, v in report.collect([extra]).items()})
        r = report.summarize(items)["per_profile"]["readiness"]["all"]
        self.assertEqual(100.0, r["rate_excluding_punch_outs"])
        self.assertEqual(50.0, r["rate_counting_punch_outs"])


class TestItDoesNotPromiseAnEndToEndRate(unittest.TestCase):
    """The report states a rate per *certified* segment and refuses the pipeline claim.

    sdlc is six segments and eleven nodes; section 5 certified `readiness` and the other nine
    nodes are `certified: false` in the registry on purpose. An end-to-end rate over that would
    be a number about links nobody measured.
    """

    def setUp(self):
        self.segs = report.segment_certification()

    def test_the_sdlc_segments_are_reported(self):
        self.assertIn("sdlc", self.segs)
        self.assertEqual(
            {"analysis", "planning", "solutioning", "readiness", "implementation",
             "verification"},
            set(self.segs["sdlc"]))

    def test_readiness_is_certified_and_the_rest_are_not(self):
        sdlc = self.segs["sdlc"]
        self.assertTrue(sdlc["readiness"]["certified"],
                        "section 5 certified readiness; the report cannot see it")
        for seg in ("analysis", "planning", "solutioning", "implementation", "verification"):
            with self.subTest(segment=seg):
                self.assertFalse(sdlc[seg]["certified"])

    def test_a_segment_is_certified_only_when_every_node_is(self):
        """Half a segment is no claim. `readiness` has two nodes and both were certified."""
        self.assertEqual(["readiness", "readiness-review"],
                         self.segs["sdlc"]["readiness"]["nodes"])
        self.assertEqual([], self.segs["sdlc"]["readiness"]["uncertified"])

    def test_an_uncertified_segment_names_which_nodes_are_missing(self):
        """"Not certified" is not actionable; which node needs an eval suite is."""
        self.assertTrue(self.segs["sdlc"]["planning"]["uncertified"])

    def test_the_markdown_refuses_the_end_to_end_claim_in_words(self):
        repo = sdlc_repo([step_record("readiness-review", True)])
        out = Path(tempfile.mkdtemp()) / "report.md"
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts/delivery-flow/delivery-report.py"),
             str(repo), "--markdown", str(out)], capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stderr)
        text = out.read_text()
        self.assertIn("No end-to-end rate is asserted", text)
        self.assertIn("an end-to-end rate for sdlc is not", text)

    def test_the_markdown_names_the_certified_segment(self):
        repo = sdlc_repo([step_record("readiness-review", True)])
        out = Path(tempfile.mkdtemp()) / "report.md"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/delivery-flow/delivery-report.py"),
             str(repo), "--markdown", str(out)], capture_output=True, text=True, check=True)
        self.assertIn("Certified segments: `readiness`", out.read_text())

    def test_an_unreadable_registry_is_unknown_not_certified(self):
        """Defaulting to certified would manufacture the claim this whole section is about."""
        original = report.workflow_descriptor.PLUGIN_ROOT
        self.addCleanup(setattr, report.workflow_descriptor, "PLUGIN_ROOT", original)
        report.workflow_descriptor.PLUGIN_ROOT = Path(tempfile.mkdtemp())
        segs = report.segment_certification()
        for by_segment in segs.values():
            for name, v in by_segment.items():
                with self.subTest(segment=name):
                    self.assertIsNot(v["certified"], True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
