"""The verify step's producer.

`verify` was `kind: build` in the routing table with nothing behind it. Four things read
`verify.json` — `decide.py`, the `review` and `post-summary` prompts, `vault-update` — and
nothing wrote it, so the test-scope edge could never fire and a `full` run could not get past
this step.

The distinctions worth testing are the ones that would flatter a bad run if collapsed:
`not-run` vs `red`, and `protected_paths_checked: false` vs an empty violations list.
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
VERIFY = SCRIPTS / "run-verify.py"

STORY = ("## Acceptance Criteria\n"
         "- AC-1 (P0): Given a, when b, then c.\n"
         "- AC-2 (P1): Given d, when e, then f.\n"
         "- AC-3 (P3): Given g, when h, then i.\n")


def _repo(test_command='"true"'):
    d = Path(tempfile.mkdtemp())
    (d / ".git").mkdir()
    runs = d / "runs"
    (runs / "V-1").mkdir(parents=True)
    (d / ".delivery-flow.yaml").write_text(
        f"profile: full\ntest_command: {test_command}\n"
        f"artifacts:\n  root: {runs}\n  commit: false\n")
    (d / "story.md").write_text(STORY)
    return d, runs / "V-1"


def _run(repo, *extra, dry=False):
    args = [sys.executable, str(VERIFY), "V-1", "--story", "story.md",
            "--repo", str(repo), "--json", *extra]
    if dry:
        args.append("--dry-run")
    out = subprocess.run(args, capture_output=True, text=True)
    # `--json` prints the document and then a status line, so decode the leading object
    # rather than assuming stdout is only JSON.
    text = out.stdout.lstrip()
    if not text.startswith("{"):
        return {}, out.returncode
    try:
        doc, _end = json.JSONDecoder().raw_decode(text)
        return doc, out.returncode
    except json.JSONDecodeError:
        return {}, out.returncode


class TestItProducesTheArtifact(unittest.TestCase):
    def test_a_green_suite_writes_verify_json(self):
        repo, item = _repo()
        _, code = _run(repo, "--test", "t1:AC-1,AC-2")
        self.assertEqual(0, code)
        self.assertTrue((item / "verify.json").exists())

    def test_the_artifact_validates_against_its_schema(self):
        """It had no schema at all before this; `additionalProperties` is false."""
        repo, item = _repo()
        _run(repo, "--test", "t1:AC-1,AC-2")
        out = subprocess.run([sys.executable, str(SCRIPTS / "validate-artifact.py"),
                              str(item / "verify.json")], capture_output=True, text=True)
        self.assertEqual(0, out.returncode, out.stdout + out.stderr)

    def test_a_red_suite_still_writes_and_exits_zero(self):
        """The step's job is to report what happened. Failing here would make a red suite
        indistinguishable from a broken verify step."""
        repo, item = _repo(test_command='"false"')
        doc, code = _run(repo, "--test", "t1:AC-1")
        self.assertEqual(0, code)
        self.assertEqual("red", doc["status"])
        self.assertTrue((item / "verify.json").exists())

    def test_it_records_the_command_it_ran(self):
        """So a reviewer can re-run it rather than take the result on trust."""
        repo, _ = _repo(test_command='"true"')
        doc, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        self.assertEqual("true", doc["test_command"]["command"])


class TestTheDistinctionsThatWouldFlatter(unittest.TestCase):
    def test_no_test_command_is_not_run_not_red(self):
        """A suite that never started says nothing about the code; a red one says plenty.
        Collapsing them would let a missing test_command read as a failing build."""
        repo, _ = _repo(test_command='""')
        doc, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        self.assertEqual("not-run", doc["status"])
        self.assertIn("not a statement that the tests pass", doc["test_command"]["summary"])

    def test_not_run_is_distinguishable_from_green(self):
        repo, _ = _repo(test_command='""')
        absent, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        repo2, _ = _repo(test_command='"true"')
        green, _ = _run(repo2, "--test", "t1:AC-1", dry=True)
        self.assertNotEqual(absent["status"], green["status"])
        self.assertFalse(absent["passed"])

    def test_an_unrunnable_protected_check_is_not_recorded_as_clean(self):
        """`protected_paths_checked: false` with no violations must not read as
        "nothing was touched" — the empty-policy case the checker itself refuses."""
        repo, _ = _repo()
        doc, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        self.assertFalse(doc["protected_paths_checked"])
        self.assertEqual([], doc["protected_violations"])


class TestItRefusesBadInput(unittest.TestCase):
    def test_a_missing_story_is_a_usage_error(self):
        """The scope edge resolves priorities from the story; without it the check silently
        degrades to a no-op, so the producer refuses rather than emitting an unusable artifact."""
        repo, _ = _repo()
        out = subprocess.run([sys.executable, str(VERIFY), "V-1", "--story", "gone.md",
                              "--repo", str(repo)], capture_output=True, text=True)
        self.assertEqual(2, out.returncode)
        self.assertIn("does not exist", out.stdout + out.stderr)

    def test_a_malformed_test_mapping_is_refused(self):
        repo, _ = _repo()
        for bad in ("noseparator", "name:", ":AC-1"):
            with self.subTest(arg=bad):
                out = subprocess.run([sys.executable, str(VERIFY), "V-1", "--story", "story.md",
                                      "--repo", str(repo), "--test", bad],
                                     capture_output=True, text=True)
                self.assertEqual(2, out.returncode)

    def test_a_non_delivery_repo_is_a_usage_error(self):
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        out = subprocess.run([sys.executable, str(VERIFY), "V-1", "--story", "x.md",
                              "--repo", str(d)], capture_output=True, text=True)
        self.assertEqual(2, out.returncode)


class TestTheEdgeCanNowFire(unittest.TestCase):
    """The point of the whole change: the scope check had no input before this."""

    def _scope(self, repo, item):
        spec = importlib.util.spec_from_file_location(
            "check_test_scope", SCRIPTS / "check-test-scope.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.problems(item / "verify.json", repo)

    def test_a_correct_scope_passes_through_a_real_artifact(self):
        repo, item = _repo()
        _run(repo, "--test", "t1:AC-1,AC-2")
        found, _ = self._scope(repo, item)
        self.assertEqual([], found)

    def test_an_out_of_scope_test_is_caught_through_a_real_artifact(self):
        repo, item = _repo()
        _run(repo, "--test", "t1:AC-1,AC-2", "--test", "extra:AC-3")
        found, _ = self._scope(repo, item)
        self.assertTrue(any("AC-3 is P3" in f for f in found), found)

    def test_an_uncovered_p0_is_caught_through_a_real_artifact(self):
        repo, item = _repo()
        _run(repo, "--test", "t1:AC-2")
        found, _ = self._scope(repo, item)
        self.assertTrue(any("AC-1 is P0" in f for f in found), found)


if __name__ == "__main__":
    unittest.main()


class TestTheSchemaAcceptsWhatTheStepActuallyWrites(unittest.TestCase):
    """The regression that blocked eight live runs.

    The first version of this schema was designed from the prompt descriptions rather than from
    the artifacts on disk. It was closed (`additionalProperties: false`) and required invented
    field names, so it rejected every `verify.json` ever written — 33 mismatches on AN-3668 —
    and the edge then blocked those items.

    Across the eight real artifacts only `item` appears in all of them, and `test_command`
    appears as both a string and an object. This artifact is a free-form evidence document the
    orchestrator shapes per run, which is why it had no schema for so long.
    """

    SCHEMA = ROOT / "schemas" / "verify.schema.json"

    def setUp(self):
        self.schema = json.loads(self.SCHEMA.read_text())

    def test_it_requires_only_the_one_stable_field(self):
        self.assertEqual(["item"], self.schema["required"])

    def test_it_is_open_to_extra_fields(self):
        """`gates`, `discrepancies`, `planned_vs_realized` and ~80 others vary by run. A
        closed schema here is not strictness, it is a rejection of the real artifact."""
        self.assertIs(True, self.schema["additionalProperties"])

    def test_test_command_accepts_both_shapes_seen_in_the_wild(self):
        types = {b["type"] for b in self.schema["properties"]["test_command"]["oneOf"]}
        self.assertEqual({"string", "object"}, types)

    def test_tests_and_story_are_optional(self):
        """The scope edge reports an honest no-op without them; requiring them would
        invalidate every artifact written before they existed."""
        for field in ("tests", "story"):
            with self.subTest(field=field):
                self.assertIn(field, self.schema["properties"])
                self.assertNotIn(field, self.schema["required"])

    def test_the_shape_note_records_why_it_is_open(self):
        """So nobody tightens it back without meeting the eight artifacts first."""
        self.assertIn("_shape_note", self.schema)
        self.assertIn("only `item` appears in every one", self.schema["_shape_note"])


class TestTheRealArtifactsValidate(unittest.TestCase):
    """Against fixtures copied from the live runs this schema broke.

    A schema test written only against artifacts this script produces would have passed the
    broken version too — the script and the schema agreed with each other and with nothing
    else. These are the shapes the orchestrator actually wrote.
    """

    # Minimal excerpts of the two real shapes, kept here so the test does not depend on a
    # vault being mounted. Both were rejected by the first schema.
    SHAPES = {
        "test_command as an object, with gates and discrepancies": {
            "item": "AN-3668", "branch": "delivery/AN-3668", "revision": 3,
            "status": "passed_with_discrepancy", "passed": True,
            "test_command": {"command": "make test", "exit_code": 2,
                             "source": ".delivery-flow.yaml test_command"},
            "gates": {"tests": "722 passed", "coverage": "90.1%"},
            "discrepancies": ["lint failed, not the suite"],
            "planned_vs_realized": {"planned": 4, "realized": 4},
        },
        "test_command as a bare string": {
            "item": "AN-3667", "branch": "delivery/AN-3667",
            "test_command": "make test", "passed": True,
            "protected_paths": [], "contract_paths": [],
        },
    }

    def test_both_real_shapes_validate(self):
        import tempfile as tf
        spec = importlib.util.spec_from_file_location(
            "validate_artifact", SCRIPTS / "validate-artifact.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for label, doc in self.SHAPES.items():
            with self.subTest(shape=label):
                d = Path(tf.mkdtemp())
                p = d / "verify.json"
                p.write_text(json.dumps(doc))
                out = subprocess.run(
                    [sys.executable, str(SCRIPTS / "validate-artifact.py"), str(p)],
                    capture_output=True, text=True)
                self.assertEqual(0, out.returncode, out.stdout + out.stderr)
