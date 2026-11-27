"""The delivery-review eval suite, enforced before any model run.

`skills/prompt-edd` orders this deliberately: the suite is built first, and the asserts are
proven against hand-written reference answers before a single model call. An assert that
cannot fail scores a prompt without measuring it; an assert that rejects a correct answer makes
every later number unattributable.

So this runs the suite's own self-test in CI, and checks the shape the certification gate will
read. It does NOT check scores — there are none, because no run has happened.
"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "evals" / "delivery-review"


class TestTheAssertsAreProvenFirst(unittest.TestCase):
    def test_the_selftest_passes(self):
        """8 reference answers accepted, 18 mutants killed. The gate for everything else."""
        out = subprocess.run(["node", str(SUITE / "asserts" / "selftest.js")],
                             cwd=str(SUITE), capture_output=True, text=True, timeout=120)
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)
        self.assertIn("ALL AS EXPECTED", out.stdout)

    def test_it_covers_every_case_with_a_reference_answer(self):
        """A case with no reference answer is a case whose asserts were never proven on it."""
        cases = {p.stem for p in (SUITE / "inputs").glob("*.diff")}
        text = (SUITE / "asserts" / "selftest.js").read_text()
        for c in sorted(cases):
            with self.subTest(case=c):
                self.assertIn(f"'{c}'", text)

    def test_every_case_has_ground_truth(self):
        for p in sorted((SUITE / "inputs").glob("*.diff")):
            with self.subTest(case=p.stem):
                self.assertTrue((SUITE / "expected" / f"{p.stem}.json").exists())


class TestTheThreeCriteriaAreDistinct(unittest.TestCase):
    """If one root cause can flip all three, the iteration log becomes unreadable."""

    def test_there_are_three(self):
        cfg = (SUITE / "promptfooconfig.yaml").read_text()
        for metric in ("contract", "accuracy", "grounding"):
            with self.subTest(metric=metric):
                self.assertIn(f"metric: {metric}", cfg)

    def test_contract_parses_strictly_and_the_others_leniently(self):
        """A formatting slip must cost one mark, not three.

        Checked on the `require` destructuring, not on the word appearing anywhere: the first
        version of this test matched `contract.js`'s own comment explaining that the OTHER two
        parse leniently, so it failed on a file that was correct.
        """
        import re
        def imports_lenient(name):
            src = (SUITE / "asserts" / name).read_text()
            m = re.search(r"const\s*\{([^}]*)\}\s*=\s*require\('\./lib'\)", src)
            return bool(m) and "lenient" in [x.strip() for x in m.group(1).split(",")]

        self.assertFalse(imports_lenient("contract.js"),
                         "contract must not parse leniently — it IS the strictness")
        for name in ("accuracy.js", "grounding.js"):
            with self.subTest(assert_=name):
                self.assertTrue(imports_lenient(name))


class TestTheGateSeesWhatIsActuallyThere(unittest.TestCase):
    """The registry must claim the suite and nothing it has not measured."""

    def setUp(self):
        import importlib.util
        gate = ROOT / "scripts" / "delivery-flow" / "check-certification.py"
        spec = importlib.util.spec_from_file_location("check_certification", gate)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        reg = ROOT / "skills" / "delivery-flow" / "steps.yaml"
        self.entry = {e["step"]: e for e in
                      self.m.parse_registry(reg.read_text())["steps"]}["review"]

    def test_the_load_bearing_map_clears_the_bar(self):
        got, total = self.m.load_bearing_ratio(ROOT / self.entry["load_bearing"])
        self.assertGreaterEqual(got / total, self.m.LOAD_BEARING_BAR,
                                f"{got}/{total} is below the bar")

    def test_it_declares_at_least_three_criteria(self):
        self.assertGreaterEqual(len(set(self.entry["criteria"])), 3)

    def test_every_criterion_it_declares_has_an_assert(self):
        """A declared criterion with no file behind it is a claim about nothing."""
        for name in self.entry["criteria"]:
            with self.subTest(criterion=name):
                self.assertTrue((SUITE / "asserts" / f"{name}.js").exists())

    def test_it_claims_no_results_it_does_not_have(self):
        """The honest state. Declaring a results file or a frozen prompt before the bar is
        cleared is the fabricated-evidence failure the method refuses.

        `iteration_log` used to be on this list, because there were no runs at all. There are
        four now and the log records them, so the field is legitimate; the three that remain
        are the ones that assert a *passing* version exists."""
        for field in ("results", "prompt_sha256", "certified_version"):
            with self.subTest(field=field):
                self.assertNotIn(field, self.entry)

    def test_the_iteration_log_it_names_exists_and_cites_its_results(self):
        """A log is evidence only if the runs behind it are on disk to check."""
        log = ROOT / self.entry["iteration_log"]
        self.assertTrue(log.exists(), f"{log} is named by steps.yaml and missing")
        text = log.read_text()
        for version in ("v1", "v2", "v3", "v4"):
            with self.subTest(version=version):
                self.assertTrue((SUITE / "results" / f"run_{version}_all.json").exists(),
                                f"the log discusses {version} with no results file")
                self.assertIn(version, text)

    def test_the_step_is_still_uncertified(self):
        """Until the runs exist. A suite is not a certification."""
        self.assertIs(False, self.entry["certified"])


if __name__ == "__main__":
    unittest.main()
