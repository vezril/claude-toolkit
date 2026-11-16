#!/usr/bin/env python3
"""Tests for `artifacts.root`: where a run's artifacts live.

The default has to stay exactly where it was. Three hooks and a dozen scripts resolve artifact
paths, and those hooks are what the Stage 4 guardrail and audit-trail criteria rest on — so the
first test here is that a repo saying nothing behaves as it always did. The configurable root
is the feature; the unchanged default is the safety property.

Run: python3 tests/delivery-flow/test_artifact_root.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
sys.path.insert(0, str(SCRIPTS))

from common import artifact_root, item_dir, parse_artifact_path, trace_path  # noqa: E402

ITEM = {"key": "AN-9", "title": "t", "body": "b", "status": "s", "url": "u",
        "source": "jira", "labels": [], "links": []}


def repo_with(config: str) -> Path:
    d = Path(tempfile.mkdtemp())
    (d / ".git").mkdir()
    (d / ".delivery-flow.yaml").write_text(config)
    return d


class TestDefaultIsUnchanged(unittest.TestCase):
    """The submission under review must not move."""

    def test_a_repo_saying_nothing_uses_delivery_inside_itself(self):
        repo = repo_with("tracker:\n  kind: jira\n")
        self.assertEqual(artifact_root(repo), repo / "delivery")
        self.assertEqual(item_dir(repo, "AN-9"), repo / "delivery" / "AN-9")
        self.assertEqual(trace_path(repo, "AN-9"), repo / "delivery" / "AN-9" / "trace.jsonl")

    def test_an_empty_artifacts_block_still_defaults(self):
        repo = repo_with("tracker:\n  kind: jira\nartifacts:\n  commit: true\n")
        self.assertEqual(artifact_root(repo), repo / "delivery")

    def test_the_default_path_pattern_still_matches_anywhere(self):
        """The hooks relied on matching `delivery/<ITEM>/<file>` without knowing the repo."""
        self.assertEqual(parse_artifact_path("/anywhere/delivery/AN-1/triage.json"),
                         ("AN-1", "triage.json"))


class TestAbsoluteRoot(unittest.TestCase):
    def setUp(self):
        self.vault = Path(tempfile.mkdtemp()) / "Amazon RAG" / "Atlas" / "RAG" / "_runs"
        self.vault.mkdir(parents=True)
        self.repo = repo_with("tracker:\n  kind: jira\nprofile: triage\n"
                              f"artifacts:\n  root: {self.vault}\n  commit: false\n")

    def test_an_absolute_root_puts_artifacts_outside_the_repo(self):
        self.assertEqual(artifact_root(self.repo), self.vault)
        self.assertFalse(str(artifact_root(self.repo)).startswith(str(self.repo)))

    def test_the_router_reads_an_item_from_the_configured_root(self):
        (self.vault / "AN-9").mkdir()
        (self.vault / "AN-9" / "item.json").write_text(json.dumps(ITEM))
        out = subprocess.run([sys.executable, str(SCRIPTS / "flow-status.py"), "AN-9",
                              "--repo", str(self.repo)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("Next: triage", out.stdout)

    def test_a_rooted_parse_accepts_the_configured_root(self):
        path = self.vault / "AN-9" / "triage.json"
        self.assertEqual(parse_artifact_path(path, self.vault), ("AN-9", "triage.json"))

    def test_a_rooted_parse_rejects_a_lookalike_elsewhere(self):
        """A configured root means that directory, not any directory called `delivery`."""
        other = Path(tempfile.mkdtemp()) / "delivery" / "AN-9" / "triage.json"
        self.assertEqual(parse_artifact_path(other, self.vault), (None, None))

    def test_a_deeper_path_under_the_root_is_not_an_artifact(self):
        """`<root>/<item>/<file>` exactly — a decisions/ subdirectory is not an artifact."""
        deeper = self.vault / "AN-9" / "decisions" / "punch-out-1.json"
        self.assertEqual(parse_artifact_path(deeper, self.vault), (None, None))


class TestRelativeRoot(unittest.TestCase):
    def test_a_relative_root_stays_inside_the_repo(self):
        repo = repo_with("tracker:\n  kind: jira\nartifacts:\n  root: .runs\n")
        self.assertEqual(artifact_root(repo), repo / ".runs")

    def test_a_relative_root_is_not_treated_as_absolute(self):
        repo = repo_with("tracker:\n  kind: jira\nartifacts:\n  root: build/runs\n")
        self.assertTrue(str(artifact_root(repo)).startswith(str(repo)))


class TestUnreadableConfig(unittest.TestCase):
    def test_a_repo_with_no_config_still_resolves(self):
        """`artifact_root` is called from hooks, which must not raise on a half-set-up repo."""
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        self.assertEqual(artifact_root(d), d / "delivery")


class TestArtifactsBelongInTheVault(unittest.TestCase):
    """The rule, and the preflight that enforces it.

    A run's artifacts are the ticket body, the triage rationale, the breakdown and the brief —
    someone else's words, most of the time. Inside the code repo they are one `git add` from a
    branch and one push from being published, which on a public checkout with a client's Jira
    is a disclosure. So `flow-status.py` refuses to compute a position when they are in the
    repo without a recorded reason.

    These drive `flow-status.py` rather than only `artifact_root_problems`, because the gate is
    the refusal, not the predicate: a correct predicate nobody consults is this week's recurring
    defect, not a guardrail.
    """

    FLOW = SCRIPTS / "flow-status.py"

    def flow(self, repo: Path):
        return subprocess.run([sys.executable, str(self.FLOW), "AN-9", "--repo", str(repo)],
                              capture_output=True, text=True)

    def test_an_unexplained_in_repo_root_blocks_the_flow(self):
        d = repo_with("tracker:\n  kind: jira\n  external: true\n")
        out = self.flow(d)
        self.assertEqual(2, out.returncode, out.stdout)
        self.assertIn("BLOCKED", out.stderr)
        self.assertIn("inside the repository", out.stderr)

    def test_the_refusal_names_the_two_ways_out(self):
        d = repo_with("tracker:\n  kind: jira\n  external: true\n")
        err = self.flow(d).stderr
        self.assertIn("in_repo_ack", err)
        self.assertIn("vault", err)

    def test_a_recorded_reason_lets_it_run(self):
        d = repo_with("tracker:\n  kind: jira\n  external: true\n"
                      "artifacts:\n  in_repo_ack: our own tracker, private repo\n")
        self.assertEqual(0, self.flow(d).returncode, self.flow(d).stderr)

    def test_an_empty_reason_is_not_a_reason(self):
        d = repo_with("tracker:\n  kind: jira\n  external: true\n"
                      "artifacts:\n  in_repo_ack: \"  \"\n")
        self.assertEqual(2, self.flow(d).returncode)

    def test_a_vault_rooted_run_is_fine(self):
        vault = Path(tempfile.mkdtemp()) / "Vault With Spaces"
        runs = vault / "Atlas" / "RAG" / "_runs"
        runs.mkdir(parents=True)
        d = repo_with("tracker:\n  kind: jira\n  external: true\n"
                      f"vault:\n  path: {vault}\n  graph_root: Atlas/RAG\n"
                      f"artifacts:\n  root: {runs}\n")
        self.assertEqual(0, self.flow(d).returncode, self.flow(d).stderr)

    def test_a_bound_vault_with_the_root_elsewhere_is_refused(self):
        """The positive form of the rule: if there is a vault, that is where runs go."""
        vault = Path(tempfile.mkdtemp()) / "Vault"
        (vault / "Atlas" / "RAG" / "_runs").mkdir(parents=True)
        elsewhere = Path(tempfile.mkdtemp()) / "somewhere-else"
        elsewhere.mkdir()
        d = repo_with("tracker:\n  kind: jira\n  external: true\n"
                      f"vault:\n  path: {vault}\n  graph_root: Atlas/RAG\n"
                      f"artifacts:\n  root: {elsewhere}\n")
        out = self.flow(d)
        self.assertEqual(2, out.returncode)
        self.assertIn("outside it", out.stderr)

    def test_the_vault_being_a_git_repo_is_not_the_problem(self):
        """It is its own private repo, and that is what versions the trail."""
        vault = Path(tempfile.mkdtemp()) / "Vault"
        runs = vault / "_runs"
        runs.mkdir(parents=True)
        (vault / ".git").mkdir()
        d = repo_with("tracker:\n  kind: jira\n  external: true\n"
                      f"vault:\n  path: {vault}\n"
                      f"artifacts:\n  root: {runs}\n")
        self.assertEqual(0, self.flow(d).returncode, self.flow(d).stderr)

    def test_the_derived_vault_runs_directory(self):
        from common import vault_artifact_root
        self.assertEqual(
            Path("/v/Atlas/RAG/_runs"),
            vault_artifact_root({"vault": {"path": "/v", "graph_root": "Atlas/RAG"}}))
        self.assertEqual(Path("/v/_runs"), vault_artifact_root({"vault": {"path": "/v"}}))
        self.assertIsNone(vault_artifact_root({"vault": {"binding": "olympus"}}))
        self.assertIsNone(vault_artifact_root({}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
