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


if __name__ == "__main__":
    unittest.main(verbosity=2)
