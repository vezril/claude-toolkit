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
        self.assertEqual("red", doc["suite"]["status"])
        self.assertTrue((item / "verify.json").exists())

    def test_it_records_the_command_it_ran(self):
        """So a reviewer can re-run it rather than take the result on trust."""
        repo, _ = _repo(test_command='"true"')
        doc, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        self.assertEqual("true", doc["command"])


class TestTheDistinctionsThatWouldFlatter(unittest.TestCase):
    def test_no_test_command_is_not_run_not_red(self):
        """A suite that never started says nothing about the code; a red one says plenty.
        Collapsing them would let a missing test_command read as a failing build."""
        repo, _ = _repo(test_command='""')
        doc, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        self.assertEqual("not-run", doc["suite"]["status"])
        self.assertIn("not a statement that the tests pass", doc["suite"]["summary"])

    def test_not_run_is_distinguishable_from_green(self):
        repo, _ = _repo(test_command='""')
        absent, _ = _run(repo, "--test", "t1:AC-1", dry=True)
        repo2, _ = _repo(test_command='"true"')
        green, _ = _run(repo2, "--test", "t1:AC-1", dry=True)
        self.assertNotEqual(absent["suite"]["status"], green["suite"]["status"])

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
