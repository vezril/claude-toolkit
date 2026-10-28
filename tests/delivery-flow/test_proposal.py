#!/usr/bin/env python3
"""Tests for the proposal edge: does proposal.json describe the change directory that exists?

Run: python3 tests/delivery-flow/test_proposal.py
"""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
EDGE = ROOT / "hooks" / "check-edge.py"
SENTINEL = SCRIPTS / "write-sentinel.py"

sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("validate_proposal", SCRIPTS / "validate-proposal.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)

CHANGE_ID = "add-bounded-backoff"


def proposal_doc(**over):
    doc = {
        "item": "PRP-1",
        "change_id": CHANGE_ID,
        "change_path": f"openspec/changes/{CHANGE_ID}",
        "specs_touched": [f"openspec/changes/{CHANGE_ID}/specs/retry-policy/spec.md"],
        "tasks": [
            {"id": "T1", "description": "Add the backoff schedule", "files": ["src/Consumer.scala"]},
            {"id": "T2", "description": "Emit a retry metric", "files": ["src/Metrics.scala"]},
        ],
        "dependencies_added": [],
        "scope": False, "architecture": False, "breaking": False,
    }
    doc.update(over)
    return doc


class Repo:
    def __init__(self, item="PRP-1", tasks_md=None, with_change=True, with_spec=True,
                 artifacts=("proposal.md", "design.md", "tasks.md")):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\n  external: true\nprofile: full\nvault:\n  binding: null\n"
            "punch_out:\n  contract_paths: [the-lexicon]\n  protected_paths: [.github]\n")
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

        if with_change:
            cd = self.dir / "openspec" / "changes" / CHANGE_ID
            cd.mkdir(parents=True)
            for name in artifacts:
                if name == "tasks.md":
                    (cd / name).write_text(
                        tasks_md if tasks_md is not None
                        else "## 1. Work\n\n- [ ] T1 Add the backoff schedule\n- [ ] T2 Emit a retry metric\n")
                else:
                    (cd / name).write_text(f"# {name}\n")
            if with_spec:
                (cd / "specs" / "retry-policy").mkdir(parents=True)
                # A real delta: `openspec validate --strict` requires at least one scenario per
                # requirement, and the fixture has to satisfy the same validator production
                # does — otherwise the happy-path test only passes on machines without the CLI.
                (cd / "specs" / "retry-policy" / "spec.md").write_text(
                    "## ADDED Requirements\n\n"
                    "### Requirement: Retries use bounded exponential backoff\n"
                    "The consumer SHALL retry with exponential backoff capped at 30 seconds.\n\n"
                    "#### Scenario: A downstream timeout backs off\n\n"
                    "- **WHEN** the downstream times out\n"
                    "- **THEN** the delay grows 1s, 2s, 4s up to a 30s cap\n")
            (cd / ".openspec.yaml").write_text("schema: spec-driven\ncreated: 2026-10-27\n")
        self.change_dir = self.dir / "openspec" / "changes" / CHANGE_ID

    def write(self, doc):
        (self.item_dir / "proposal.json").write_text(json.dumps(doc, indent=2))
        return self.item_dir / "proposal.json"

    def problems(self, doc=None):
        path = self.write(doc if doc is not None else proposal_doc())
        found, info = vp.problems(path, self.dir)
        return found, info

    def hook(self, doc=None):
        path = self.write(doc if doc is not None else proposal_doc())
        subprocess.run([sys.executable, str(SENTINEL), str(path), "--step", "propose"],
                       capture_output=True, check=True)
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(path)},
                              "cwd": str(self.dir)})
        return subprocess.run([sys.executable, str(EDGE)], input=payload,
                              capture_output=True, text=True)

    def trace(self):
        p = self.item_dir / "trace.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


class TestHappyPath(unittest.TestCase):
    def test_a_consistent_proposal_passes(self):
        found, info = Repo().problems()
        self.assertEqual(found, [])
        self.assertEqual(info["tasks"], 2)
        self.assertEqual(info["files"], 2)

    def test_the_edge_passes_through_the_hook(self):
        r = Repo()
        out = r.hook()
        self.assertEqual(out.returncode, 0, out.stderr)
        rec = [t for t in r.trace() if t.get("artifact") == "proposal.json"][-1]
        self.assertIn("change-dir", rec["edge"]["name"])
        self.assertIn("schema", rec["edge"]["name"])


class TestTaskIdClosure(unittest.TestCase):
    def test_a_task_in_the_json_but_not_the_markdown_fails(self):
        r = Repo(tasks_md="- [ ] T1 Add the backoff schedule\n")
        found, _ = r.problems()
        self.assertTrue(any("T2" in p and "tasks.md does not" in p for p in found), found)

    def test_a_task_in_the_markdown_but_not_the_json_fails(self):
        r = Repo(tasks_md="- [ ] T1 a\n- [ ] T2 b\n- [ ] T3 an extra task\n")
        found, _ = r.problems()
        self.assertTrue(any("T3" in p and "proposal.json does not" in p for p in found), found)

    def test_a_tasks_md_with_no_checklist_ids_fails(self):
        r = Repo(tasks_md="## Work\n\nDo the thing.\n")
        found, _ = r.problems()
        self.assertTrue(any("no `- [ ] T<n>` checklist items" in p for p in found), found)

    def test_already_ticked_tasks_still_count_as_present(self):
        """Closure runs after implementation, so a ticked task must not read as missing."""
        r = Repo(tasks_md="- [x] T1 a\n- [X] T2 b\n")
        found, _ = r.problems()
        self.assertEqual(found, [])


class TestStructure(unittest.TestCase):
    def test_a_missing_change_directory_fails(self):
        r = Repo(with_change=False)
        found, _ = r.problems()
        self.assertTrue(any("no change directory" in p for p in found), found)

    def test_a_missing_required_artifact_fails(self):
        r = Repo(artifacts=("proposal.md", "tasks.md"))
        found, _ = r.problems()
        self.assertTrue(any("no design.md" in p for p in found), found)

    def test_no_delta_spec_fails(self):
        r = Repo(with_spec=False)
        found, _ = r.problems()
        self.assertTrue(any("no delta spec" in p for p in found), found)

    def test_a_named_spec_that_does_not_exist_fails(self):
        found, _ = Repo().problems(proposal_doc(
            specs_touched=[f"openspec/changes/{CHANGE_ID}/specs/ghost/spec.md"]))
        self.assertTrue(any("ghost" in p and "does not exist" in p for p in found), found)


class TestPathSafety(unittest.TestCase):
    def test_an_absolute_path_outside_the_repo_fails(self):
        found, _ = Repo().problems(proposal_doc(tasks=[
            {"id": "T1", "description": "d", "files": ["/etc/passwd"]},
            {"id": "T2", "description": "d", "files": ["src/Metrics.scala"]}]))
        self.assertTrue(any("/etc/passwd" in p and "outside the repository" in p for p in found), found)

    def test_a_dotdot_escape_fails(self):
        found, _ = Repo().problems(proposal_doc(tasks=[
            {"id": "T1", "description": "d", "files": ["../../other/repo/x.scala"]},
            {"id": "T2", "description": "d", "files": ["src/Metrics.scala"]}]))
        self.assertTrue(any("outside the repository" in p for p in found), found)

    def test_a_change_path_outside_the_repo_fails(self):
        found, _ = Repo().problems(proposal_doc(change_path="../elsewhere"))
        self.assertTrue(any("change_path" in p and "outside" in p for p in found), found)

    def test_an_empty_description_fails(self):
        found, _ = Repo().problems(proposal_doc(tasks=[
            {"id": "T1", "description": "   ", "files": ["src/Consumer.scala"]},
            {"id": "T2", "description": "d", "files": ["src/Metrics.scala"]}]))
        self.assertTrue(any("T1" in p and "empty description" in p for p in found), found)


class TestOpenspecLayer(unittest.TestCase):
    def test_an_absent_cli_is_recorded_as_skipped_not_passed(self):
        if shutil.which("openspec"):
            self.skipTest("openspec is installed here; this asserts the absent-CLI path")
        found, info = Repo().problems()
        self.assertEqual(found, [])
        self.assertIn("skipped", info["openspec_validate"])
        self.assertIn("not installed", info["openspec_validate"])

    def test_a_failing_cli_fails_the_edge(self):
        """Stubbed, so the behaviour is asserted on this machine too."""
        r = Repo()
        real = vp.openspec_layer
        vp.openspec_layer = lambda repo, cid: {"ran": True, "ok": False, "detail": "spec X is malformed"}
        try:
            found, _ = r.problems()
        finally:
            vp.openspec_layer = real
        self.assertTrue(any("openspec validate --strict failed" in p for p in found), found)

    def test_a_passing_cli_adds_nothing(self):
        r = Repo()
        real = vp.openspec_layer
        vp.openspec_layer = lambda repo, cid: {"ran": True, "ok": True, "detail": "ok"}
        try:
            found, info = r.problems()
        finally:
            vp.openspec_layer = real
        self.assertEqual(found, [])
        self.assertEqual(info["openspec_validate"], "ok")


class TestCli(unittest.TestCase):
    def test_the_script_exits_1_on_problems(self):
        r = Repo(with_change=False)
        path = r.write(proposal_doc())
        out = subprocess.run([sys.executable, str(SCRIPTS / "validate-proposal.py"), str(path),
                              "--repo", str(r.dir)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("no change directory", out.stdout)

    def test_the_script_exits_0_when_valid(self):
        r = Repo()
        path = r.write(proposal_doc())
        out = subprocess.run([sys.executable, str(SCRIPTS / "validate-proposal.py"), str(path),
                              "--repo", str(r.dir), "--json"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertTrue(json.loads(out.stdout)["ok"])

    def test_a_missing_file_is_a_usage_error(self):
        out = subprocess.run([sys.executable, str(SCRIPTS / "validate-proposal.py"), "/nope.json"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
