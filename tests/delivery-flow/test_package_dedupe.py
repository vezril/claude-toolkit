"""The evidence package: one entry per artifact root, and every entry findable.

Both defects here were in the one claim the package makes — *every file is listed with its
sha, go and diff it* — and both made that claim false while the package looked immaculate.

Every ticket worktree carries a copy of `.delivery-flow.yaml` on purpose, so every worktree
registers itself as a delivery repo and they all resolve to one artifact root. The packager
walked all of them, and the result was a package claiming **220 completed runs instead of 10**
and a MANIFEST.txt of 10,244 lines for 499 distinct files.

The package's entire argument is "here is every file with its sha, go and diff it". These
tests exist because that argument was false in the most checkable way possible.
"""

import importlib.util
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "delivery-flow" / "package-evidence.py"

spec = importlib.util.spec_from_file_location("package_evidence", SCRIPT)
pe = importlib.util.module_from_spec(spec)
sys.modules["package_evidence"] = pe
spec.loader.exec_module(pe)


def make_repo(path: Path, artifacts: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".delivery-flow.yaml").write_text(textwrap.dedent(f"""\
        tracker:
          kind: local-markdown
        forge:
          kind: github-pr
          base: main
        artifacts:
          root: {artifacts}
        """))
    return path


class TestOneArtifactRootCountsOnce(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.artifacts = t / "runs"
        (self.artifacts / "AN-1").mkdir(parents=True)
        (self.artifacts / "AN-1" / "outcome.json").write_text(
            json.dumps({"item": "AN-1", "status": "completed", "profile": "triage"}))
        self.primary = make_repo(t / "repo", self.artifacts)
        self.worktrees = [make_repo(t / "repo" / ".worktrees" / f"AN-{i}", self.artifacts)
                          for i in (1, 2, 3)]

    def tearDown(self):
        self.tmp.cleanup()

    def test_worktrees_collapse_into_the_primary(self):
        kept, collapsed = pe.dedupe_by_artifact_root([self.primary, *self.worktrees])
        self.assertEqual([self.primary], kept)
        self.assertEqual(3, len(collapsed))

    def test_the_first_path_given_is_the_one_kept(self):
        """Order matters: the caller's first path is the one named in the output."""
        kept, _ = pe.dedupe_by_artifact_root([self.worktrees[0], self.primary])
        self.assertEqual([self.worktrees[0]], kept)

    def test_distinct_roots_are_both_kept(self):
        t = Path(self.tmp.name)
        other = make_repo(t / "other", t / "other-runs")
        kept, collapsed = pe.dedupe_by_artifact_root([self.primary, other])
        self.assertEqual([self.primary, other], kept)
        self.assertEqual([], collapsed)

    def test_the_run_census_is_not_multiplied(self):
        """The defect in its original form: the same run counted once per registered path."""
        with tempfile.TemporaryDirectory() as out:
            dest = Path(out) / "pkg"
            many = [self.primary, *self.worktrees]
            kept, _ = pe.dedupe_by_artifact_root(many)
            manifest = []
            census = pe.collect_runs(kept, dest, manifest, dry=True)
            self.assertEqual(1, census["completed"])
            self.assertEqual(1, len(census["items"]))

    def test_without_the_dedupe_the_census_would_multiply(self):
        """Proves the test above is measuring the dedupe and not something incidental."""
        with tempfile.TemporaryDirectory() as out:
            dest = Path(out) / "pkg"
            many = [self.primary, *self.worktrees]
            census = pe.collect_runs(many, dest, [], dry=True)
            self.assertEqual(4, census["completed"],
                             "four paths, one root: this is the bug the dedupe removes")

    def test_the_script_itself_dedupes_the_paths_it_is_given(self):
        """The unit tests above call the two functions directly, so on their own they would
        still pass if `main` never wired the dedupe in. This runs the script."""
        import subprocess
        with tempfile.TemporaryDirectory() as out:
            dest = Path(out) / "pkg"
            res = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), "--out", str(dest), "--dry-run",
                 "--allow-uncertified",
                 "--repo", str(self.primary), *sum((["--repo", str(w)]
                                                    for w in self.worktrees), [])],
                capture_output=True, text=True)
            said = res.stdout + res.stderr
            self.assertIn("collapsed to one artifact root", said, said)
            self.assertIn("runs collected                 1", said, said)

    def test_a_repo_with_no_resolvable_root_is_still_passed_through(self):
        """Dropping a path the caller asked about would hide a misconfiguration."""
        missing = Path(self.tmp.name) / "not-a-repo"
        missing.mkdir()
        kept, _ = pe.dedupe_by_artifact_root([missing])
        self.assertEqual([missing], kept)


class TestTheManifestCanActuallyBeChecked(unittest.TestCase):
    """Its first column said `AN-3641/item.json` for a file at
    `4-end-to-end-rate/runs/AN-3641/item.json`, and `SKILL.md` for one at
    `1-workflow-definition/SKILL.md`. Not one of 498 entries resolved from the package root,
    so a reviewer verifying a sha could not find a single file to verify."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.artifacts = t / "runs"
        (self.artifacts / "AN-1").mkdir(parents=True)
        (self.artifacts / "AN-1" / "item.json").write_text('{"item": "AN-1"}')
        (self.artifacts / "AN-1" / "outcome.json").write_text(
            json.dumps({"item": "AN-1", "status": "completed", "profile": "triage"}))
        self.repo = make_repo(t / "repo", self.artifacts)
        self.out = t / "pkg"

    def tearDown(self):
        self.tmp.cleanup()

    def _build(self):
        import subprocess
        res = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--out", str(self.out), "--force",
             "--allow-uncertified", "--repo", str(self.repo)],
            capture_output=True, text=True)
        self.assertEqual(0, res.returncode, res.stdout + res.stderr)
        return [l for l in (self.out / "MANIFEST.txt").read_text().splitlines()
                if l.strip() and not l.startswith("#")]

    def test_every_entry_resolves_from_the_package_root(self):
        rows = self._build()
        self.assertTrue(rows, "the manifest is empty")
        for row in rows:
            rel = row.split("|")[0].strip()
            with self.subTest(entry=rel):
                self.assertTrue((self.out / rel).is_file(),
                                f"{rel} is in the manifest and not at that path")

    def test_every_recorded_sha_matches_the_file_in_the_package(self):
        """A path that resolves is not enough; the digest has to be the digest."""
        import hashlib
        for row in self._build():
            rel, _src, sha = [c.strip() for c in row.split("|")]
            with self.subTest(entry=rel):
                got = hashlib.sha256((self.out / rel).read_bytes()).hexdigest()
                self.assertEqual(sha, got, f"{rel} does not match its recorded sha")

    def test_the_run_artifacts_are_under_the_criterion_that_cites_them(self):
        """The nesting is the point of the layout: one directory answers one question."""
        rows = [r.split("|")[0].strip() for r in self._build()]
        runs = [r for r in rows if "AN-1" in r]
        self.assertTrue(runs)
        for r in runs:
            self.assertTrue(r.startswith("4-end-to-end-rate/runs/"), r)


class TestThePackageCanBeVerifiedByItsReader(unittest.TestCase):
    """The reviewer is an agent, so the package ships the recomputation of its own claims.

    A verifier that cannot fail is worse than none: it converts "unchecked" into "checked and
    fine". So these tests tamper with a built package six ways and require a non-zero exit
    each time.
    """

    def setUp(self):
        import subprocess
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.artifacts = t / "runs"
        for item, status in (("AN-1", "completed"), ("AN-2", "completed")):
            d = self.artifacts / item
            d.mkdir(parents=True)
            (d / "item.json").write_text(json.dumps({"item": item}))
            (d / "trace.jsonl").write_text(json.dumps({"item": item, "step": "triage"}) + "\n")
            (d / "outcome.json").write_text(json.dumps(
                {"item": item, "status": status, "profile": "triage", "replay": True}))
        self.repo = make_repo(t / "repo", self.artifacts)
        self.out = t / "pkg"
        res = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--out", str(self.out), "--force",
             "--allow-uncertified", "--repo", str(self.repo)],
            capture_output=True, text=True)
        self.assertEqual(0, res.returncode, res.stdout + res.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def _verify(self):
        import subprocess
        return subprocess.run([sys.executable, str(self.out / "verify.py")],
                              cwd=str(self.out), capture_output=True, text=True)

    def test_a_clean_package_verifies(self):
        r = self._verify()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("VERIFIED", r.stdout)

    def test_the_index_states_the_untrusted_paths(self):
        """The run artifacts reproduce third-party prose verbatim. An agent reviewer reads it,
        so the package has to say it is data rather than direction."""
        idx = json.loads((self.out / "INDEX.json").read_text())
        self.assertIn("untrusted_content", idx)
        self.assertTrue(idx["untrusted_content"]["paths"])
        self.assertIn("DATA", idx["untrusted_content"]["why"])

    def test_the_index_states_its_known_limits(self):
        """Stated as data so they cannot be skimmed past."""
        idx = json.loads((self.out / "INDEX.json").read_text())
        self.assertGreaterEqual(len(idx["known_limits"]), 3)
        for lim in idx["known_limits"]:
            self.assertTrue(lim.get("limit") and lim.get("where"))

    def test_the_rate_in_the_index_is_falsifiable(self):
        """It divided the completed runs by themselves once, which is 100% for any input."""
        idx = json.loads((self.out / "INDEX.json").read_text())
        obs = idx["criterion_4"]["observed_terminal_rate"]
        self.assertEqual(obs["denominator"], 2)
        self.assertNotIn("denominator", idx["criterion_4"],
                         "the top-level circular denominator must be gone")

    def test_tampering_with_a_file_fails_verification(self):
        f = self.out / "1-workflow-definition" / "SKILL.md"
        f.write_bytes(f.read_bytes() + b"\n<!-- tampered -->\n")
        self.assertEqual(1, self._verify().returncode)

    def test_deleting_a_manifested_file_fails_verification(self):
        (self.out / "1-workflow-definition" / "steps.yaml").unlink()
        self.assertEqual(1, self._verify().returncode)

    def test_overstating_the_run_count_fails_verification(self):
        idx = self.out / "INDEX.json"
        d = json.loads(idx.read_text()); d["runs"]["completed"] = 99
        idx.write_text(json.dumps(d))
        self.assertEqual(1, self._verify().returncode)

    def test_inflating_the_denominator_fails_verification(self):
        idx = self.out / "INDEX.json"
        d = json.loads(idx.read_text())
        d["criterion_4"]["observed_terminal_rate"]["denominator"] = 50
        idx.write_text(json.dumps(d))
        self.assertEqual(1, self._verify().returncode)

    def test_hiding_the_replays_fails_verification(self):
        idx = self.out / "INDEX.json"
        d = json.loads(idx.read_text()); d["runs"]["replays"] = 0
        idx.write_text(json.dumps(d))
        self.assertEqual(1, self._verify().returncode)

    def test_a_counted_run_without_a_trace_fails_verification(self):
        (self.out / "4-end-to-end-rate" / "runs" / "AN-1" / "trace.jsonl").unlink()
        self.assertEqual(1, self._verify().returncode)


if __name__ == "__main__":
    unittest.main()
