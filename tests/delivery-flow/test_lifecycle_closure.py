#!/usr/bin/env python3
"""Tests for OpenSpec lifecycle closure: tick what shipped, never archive.

Run: python3 tests/delivery-flow/test_lifecycle_closure.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
CLOSE = SCRIPTS / "close-openspec-change.py"
FLOW = SCRIPTS / "flow-status.py"

CHANGE_ID = "add-bounded-backoff"
TASKS_MD = ("## 1. Work\n\n"
            "- [ ] T1 Add the backoff schedule\n"
            "- [ ] T2 Emit a retry metric\n"
            "- [ ] T3 Document the policy\n")


class Repo:
    def __init__(self, item="LCY-1", tasks_md=TASKS_MD, implementation=None):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\n  external: true\nprofile: full\nvault:\n  binding: null\n")
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)
        self.change_dir = self.dir / "openspec" / "changes" / CHANGE_ID
        self.change_dir.mkdir(parents=True)
        self.tasks_md = self.change_dir / "tasks.md"
        self.tasks_md.write_text(tasks_md)

        (self.item_dir / "proposal.json").write_text(json.dumps({
            "item": item, "change_id": CHANGE_ID,
            "change_path": f"openspec/changes/{CHANGE_ID}",
            "specs_touched": ["x"],
            "tasks": [{"id": f"T{i}", "description": "d", "files": ["src/a.scala"]}
                      for i in (1, 2, 3)],
            "dependencies_added": [], "scope": False, "architecture": False, "breaking": False,
        }, indent=2))
        if implementation is not None:
            (self.item_dir / "implementation.json").write_text(json.dumps(implementation))

    def close(self, *args):
        return subprocess.run([sys.executable, str(CLOSE), self.item, "--repo", str(self.dir),
                               *args], capture_output=True, text=True)

    def status(self):
        return subprocess.run([sys.executable, str(FLOW), self.item, "--repo", str(self.dir)],
                              capture_output=True, text=True)


class TestTicking(unittest.TestCase):
    def test_shipped_tasks_are_ticked(self):
        r = Repo(implementation={"tasks_done": ["T1", "T2"]})
        out = r.close()
        self.assertEqual(out.returncode, 0, out.stderr)
        text = r.tasks_md.read_text()
        self.assertIn("- [x] T1", text)
        self.assertIn("- [x] T2", text)
        self.assertIn("- [ ] T3", text)

    def test_an_unclaimed_task_stays_open_and_is_reported(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        out = r.close()
        self.assertIn("T2", out.stdout)
        self.assertIn("T3", out.stdout)
        self.assertIn("left open", out.stdout)
        self.assertIn("- [ ] T3", r.tasks_md.read_text())

    def test_an_unknown_task_id_exits_nonzero(self):
        r = Repo(implementation={"tasks_done": ["T1", "T99"]})
        out = r.close()
        self.assertEqual(out.returncode, 1)
        self.assertIn("T99", out.stderr)
        self.assertIn("- [ ] T1", r.tasks_md.read_text())  # nothing written

    def test_the_task_text_survives_ticking(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        r.close()
        self.assertIn("- [x] T1 Add the backoff schedule", r.tasks_md.read_text())

    def test_the_structured_tasks_form_is_also_accepted(self):
        r = Repo(implementation={"tasks": [{"id": "T1", "status": "done"},
                                           {"id": "T2", "status": "in-progress"}]})
        r.close()
        text = r.tasks_md.read_text()
        self.assertIn("- [x] T1", text)
        self.assertIn("- [ ] T2", text)

    def test_dry_run_writes_nothing(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        before = r.tasks_md.read_text()
        out = r.close("--dry-run", "--json")
        self.assertEqual(out.returncode, 0)
        self.assertEqual(r.tasks_md.read_text(), before)
        self.assertEqual(json.loads(out.stdout)["ticked"], ["T1"])

    def test_reticking_is_idempotent(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        r.close()
        first = r.tasks_md.read_text()
        out = r.close()
        self.assertEqual(r.tasks_md.read_text(), first)
        self.assertIn("nothing new", out.stdout)


class TestArchiveIsHuman(unittest.TestCase):
    def test_the_script_never_archives(self):
        r = Repo(implementation={"tasks_done": ["T1", "T2", "T3"]})
        out = r.close()
        self.assertTrue(r.change_dir.is_dir())
        self.assertFalse((r.dir / "openspec" / "specs").exists())
        self.assertIn(f"openspec archive {CHANGE_ID}", out.stdout)

    def test_the_json_output_says_it_did_not_archive(self):
        r = Repo(implementation={"tasks_done": ["T1", "T2", "T3"]})
        payload = json.loads(r.close("--json").stdout)
        self.assertFalse(payload["archived"])
        self.assertEqual(payload["outstanding"], 0)
        self.assertEqual(payload["archive_command"], f"openspec archive {CHANGE_ID}")

    def test_an_incomplete_change_is_not_offered_for_archive(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        out = r.close()
        self.assertIn("not ready to archive", out.stdout)
        self.assertNotIn(f"    openspec archive", out.stdout)


class TestGuards(unittest.TestCase):
    def test_no_implementation_artifact_is_a_usage_error(self):
        r = Repo()
        out = r.close()
        self.assertEqual(out.returncode, 2)
        self.assertIn("implementation.json", out.stderr)

    def test_a_missing_tasks_md_is_a_usage_error(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        r.tasks_md.unlink()
        out = r.close()
        self.assertEqual(out.returncode, 2)
        self.assertIn("tasks.md", out.stderr)


class TestStatusSurfacesOutstandingWork(unittest.TestCase):
    def test_outstanding_tasks_are_reported(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        r.close()
        out = r.status()
        self.assertIn(CHANGE_ID, out.stdout)
        self.assertIn("2 task(s) still unticked", out.stdout)

    def test_a_fully_ticked_change_names_the_archive_command(self):
        r = Repo(implementation={"tasks_done": ["T1", "T2", "T3"]})
        r.close()
        out = r.status()
        self.assertIn("every task ticked", out.stdout)
        self.assertIn(f"openspec archive {CHANGE_ID}", out.stdout)

    def test_an_unreadable_tasks_md_is_reported_not_ignored(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        r.tasks_md.unlink()
        out = r.status()
        self.assertIn("cannot be read", out.stdout)

    def test_no_proposal_means_no_change_line(self):
        r = Repo(implementation={"tasks_done": ["T1"]})
        (r.item_dir / "proposal.json").unlink()
        out = r.status()
        self.assertNotIn(CHANGE_ID, out.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
