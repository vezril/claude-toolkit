"""The sdlc implementation (test-writer) eval suite, enforced before any model run.

Its output is test source code, so the only honest grading is execution: run what the agent
wrote, then run it again with a reference implementation applied. `grade.py` does both.

The tests here run the grader's own calibration in CI. A grader that drifts from its
calibration scores a prompt it is not measuring, and the criterion most at risk is `green` —
it only means anything if a test that guards nothing actually loses the point.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "evals" / "sdlc-implementation"


class TestTheGraderIsCalibrated(unittest.TestCase):
    def test_calibration_passes(self):
        """4 correct answers score 4/4; 9 defects each lose exactly their criteria."""
        out = subprocess.run([sys.executable, "-I", str(SUITE / "calibrate.py")],
                             cwd=str(SUITE), capture_output=True, text=True, timeout=900)
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("ALL AS EXPECTED", out.stdout)

    def test_every_fixture_starts_from_a_clean_baseline(self):
        """If a fixture already fails, `red` passes trivially and measures nothing."""
        for case in sorted(p for p in (SUITE / "fixture").iterdir() if p.is_dir()):
            with self.subTest(case=case.name):
                out = subprocess.run(
                    "python3 -m unittest discover -s tests -t . -q",
                    shell=True, cwd=str(case), capture_output=True, text=True, timeout=120)
                self.assertEqual(0, out.returncode,
                                 f"{case.name} does not start green:\n{out.stdout}{out.stderr}")

    def test_every_case_has_ground_truth(self):
        for case in sorted(p for p in (SUITE / "fixture").iterdir() if p.is_dir()):
            with self.subTest(case=case.name):
                self.assertTrue((SUITE / "expected" / f"{case.name}.json").exists())

    def test_cases_needing_green_have_a_hidden_reference(self):
        """`green` cannot be scored without one, and must not silently pass instead."""
        for exp in sorted((SUITE / "expected").glob("*.json")):
            doc = json.loads(exp.read_text())
            if doc.get("expect_handback"):
                continue
            with self.subTest(case=exp.stem):
                self.assertIn("reference_target", doc)
                self.assertTrue((SUITE / "hidden" / f"{exp.stem}.py").exists())

    def test_the_reference_is_not_readable_from_the_fixture(self):
        """`hidden/` sits outside every working_dir, so the agent cannot read the answer."""
        for case in sorted(p for p in (SUITE / "fixture").iterdir() if p.is_dir()):
            with self.subTest(case=case.name):
                self.assertEqual([], list(case.rglob("*.patch")))
                self.assertFalse((case / "hidden").exists())


class TestTheRunnerCannotDestroyTheFixtures(unittest.TestCase):
    """It did once: `git clean -fdq fixture/` on an untracked tree deleted three of them."""

    def test_the_fixtures_are_tracked(self):
        out = subprocess.run(["git", "ls-files", "--error-unmatch",
                              "evals/sdlc-implementation/fixture"],
                             cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(0, out.returncode,
                         "fixture/ is untracked, so run.sh's restore would delete it")

    def test_the_runner_refuses_an_untracked_fixture_tree(self):
        self.assertIn("is not tracked by git", (SUITE / "run.sh").read_text())

    def test_it_restores_before_calibrating(self):
        """Calibrating first meant a tree left dirty aborted the run before the restore
        could clean it — a correct refusal in an order that could not recover."""
        text = (SUITE / "run.sh").read_text()
        self.assertLess(text.index("restore_fixtures"), text.index("calibrate.py"))

    def test_it_refuses_repeat_above_one(self):
        """--repeat reuses the working dir, and this agent writes into it."""
        out = subprocess.run(["bash", str(SUITE / "run.sh"), "v1", "haiku"],
                             cwd=str(SUITE), capture_output=True, text=True,
                             env={**__import__("os").environ, "REPEAT": "3"}, timeout=120)
        self.assertEqual(2, out.returncode)
        self.assertIn("REPEAT must be 1", out.stdout + out.stderr)


class TestTheSuiteMeasuresWhatItClaims(unittest.TestCase):
    """Three runs were discarded to harness bugs, and each produced plausible numbers.

    Both of these were invisible from the results file: a run over three of five cases and a
    run where both providers were the same model both reported a full table of scores.
    """

    def test_every_fixture_case_is_wired_into_the_config(self):
        """Cases 04 and 05 had fixtures and ground truth but no `tests:` entry, so the suite
        looked complete and silently measured three of five."""
        config = (SUITE / "promptfooconfig.yaml").read_text()
        # The `vars:` form only, so a case named in a comment cannot stand in for a test.
        wired = set(re.findall(r"vars:\s*\{\s*case:\s*(case-\d+)\s*\}", config))
        on_disk = {p.name for p in (SUITE / "fixture").iterdir() if p.is_dir()}
        self.assertEqual(on_disk, wired)

    def test_the_provider_has_no_model_default(self):
        """`${CLI_MODEL:-sonnet}` ran both providers as sonnet and reported it as a
        two-model comparison. A missing model must fail, not fall back."""
        cli = (SUITE / "provider" / "claude-cli.sh").read_text()
        self.assertIn("MODEL_OVERRIDE:?", cli)
        self.assertNotRegex(cli, r"MODEL_OVERRIDE:-|CLI_MODEL:-")

    def test_each_wrapper_sets_its_own_model(self):
        for model in ("haiku", "sonnet"):
            with self.subTest(model=model):
                text = (SUITE / "provider" / f"claude-{model}.sh").read_text()
                self.assertRegex(text, rf"MODEL_OVERRIDE=[\"']?{model}")

    def test_the_provider_reads_only_the_prompt_argument(self):
        """promptfoo's third argument is a context JSON holding the test's ground truth."""
        cli = (SUITE / "provider" / "claude-cli.sh").read_text()
        self.assertNotRegex(cli, r'\$\{?[23]\}?|\$\{?@\}?|\$\*')

    def test_the_provider_keeps_its_stderr(self):
        """Sending it to /dev/null turned a missing model into a bare 'Command failed'."""
        cli = (SUITE / "provider" / "claude-cli.sh").read_text()
        self.assertNotIn("2>/dev/null", cli)

    def test_the_work_tree_is_keyed_by_case_and_model(self):
        """Keyed by case alone, parallel providers copied into each other's trees."""
        cli = (SUITE / "provider" / "claude-cli.sh").read_text()
        self.assertIn('.work/$CASE-$MODEL', cli)


class TestTheRegistryClaimsOnlyWhatExists(unittest.TestCase):
    def setUp(self):
        import importlib.util
        gate = ROOT / "scripts" / "delivery-flow" / "check-certification.py"
        spec = importlib.util.spec_from_file_location("check_certification", gate)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        reg = ROOT / "skills" / "sdlc-orchestration" / "steps.yaml"
        self.entry = {e["step"]: e for e in
                      self.m.parse_registry(reg.read_text())["steps"]}["implementation"]

    def test_the_load_bearing_map_clears_the_bar(self):
        got, total = self.m.load_bearing_ratio(ROOT / self.entry["load_bearing"])
        self.assertGreaterEqual(got / total, self.m.LOAD_BEARING_BAR, f"{got}/{total}")

    def test_it_declares_four_criteria(self):
        self.assertEqual({"territory", "red", "green", "scope"}, set(self.entry["criteria"]))

    def test_it_claims_no_results_it_does_not_have(self):
        for field in ("results", "prompt_sha256", "certified_version", "iteration_log"):
            with self.subTest(field=field):
                self.assertNotIn(field, self.entry)

    def test_the_step_is_still_uncertified(self):
        self.assertIs(False, self.entry["certified"])


if __name__ == "__main__":
    unittest.main()
