#!/usr/bin/env python3
"""Tests for the edge machinery: schema validation, sentinels, and the PostToolUse hook.

Run: python3 tests/delivery-flow/test_edges.py
Standard library only, like the code under test.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
HOOK = ROOT / "hooks" / "check-edge.py"
sys.path.insert(0, str(SCRIPTS))
from common import count_expr  # noqa: E402


def breakdown(stories_per_epic=(2,), acs=2):
    epics = []
    for e, n in enumerate(stories_per_epic, start=1):
        stories = []
        for s in range(1, n + 1):
            stories.append({
                "id": f"S{e}{s}",
                "statement": f"As a user, I want thing {e}.{s}, so that it works",
                "domains": ["backend"],
                "acceptance_criteria": [
                    {"id": f"AC{i}", "given": "a repo", "when": "the step runs", "then": "it passes"}
                    for i in range(1, acs + 1)
                ],
            })
        epics.append({"id": f"E{e}", "title": f"Epic {e}", "stories": stories})
    return {"item": "DEM-12", "epics": epics}


TRIAGE = {
    "item": "DEM-12", "type": "feature", "path": "standard", "domains": ["backend"],
    "summary": "Add a range endpoint", "rationale": "The item describes a new API surface",
    "handoff": False, "handoff_reason": None,
    "architecture_change": False, "breaking_change": False,
}


class Fixture:
    """A throwaway delivery-flow repo with one item."""

    def __init__(self, delivery_repo=True, item="DEM-12"):
        self.dir = Path(tempfile.mkdtemp())
        self.item = item
        (self.dir / ".git").mkdir()
        if delivery_repo:
            (self.dir / ".delivery-flow.yaml").write_text("binding: test\n")
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def write(self, name, doc):
        p = self.item_dir / name
        p.write_text(json.dumps(doc, indent=2) + "\n")
        return p

    def sentinel(self, name, step="breakdown", counts=None, status="complete"):
        args = [sys.executable, str(SCRIPTS / "write-sentinel.py"), str(self.item_dir / name), "--step", step,
                "--status", status]
        for k, v in (counts or {}).items():
            args += ["--count", f"{k}={v}"]
        return subprocess.run(args, capture_output=True, text=True)

    def hook(self, name, tool="Write"):
        payload = {"hook_event_name": "PostToolUse", "tool_name": tool, "cwd": str(self.dir),
                   "session_id": "s1", "tool_input": {"file_path": str(self.item_dir / name)}}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def trace(self):
        p = self.item_dir / "trace.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


class TestCountExpressions(unittest.TestCase):
    def test_nested_counts(self):
        doc = breakdown(stories_per_epic=(2, 3), acs=2)
        self.assertEqual(count_expr(doc, "epics[]"), 2)
        self.assertEqual(count_expr(doc, "epics[].stories[]"), 5)
        self.assertEqual(count_expr(doc, "epics[].stories[].acceptance_criteria[]"), 10)


class TestValidator(unittest.TestCase):
    def validate(self, path, *extra):
        return subprocess.run([sys.executable, str(SCRIPTS / "validate-artifact.py"), str(path), *extra],
                              capture_output=True, text=True)

    def test_valid_artifact_passes(self):
        f = Fixture()
        r = self.validate(f.write("breakdown.json", breakdown()))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_schema_violation_fails(self):
        f = Fixture()
        doc = breakdown()
        doc["epics"][0]["stories"][0]["acceptance_criteria"] = []  # minItems 1
        r = self.validate(f.write("breakdown.json", doc))
        self.assertEqual(r.returncode, 1)
        self.assertIn("needs at least 1", r.stdout)

    def test_bad_enum_fails(self):
        f = Fixture()
        doc = dict(TRIAGE, type="epic")
        r = self.validate(f.write("triage.json", doc))
        self.assertEqual(r.returncode, 1)
        self.assertIn("not one of", r.stdout)

    def test_unexpected_field_fails(self):
        f = Fixture()
        r = self.validate(f.write("triage.json", dict(TRIAGE, severity="high")))
        self.assertEqual(r.returncode, 1)
        self.assertIn("unexpected field", r.stdout)

    def test_consumer_contract(self):
        f = Fixture()
        doc = dict(TRIAGE)
        doc["summary"] = ""
        r = self.validate(f.write("triage.json", doc), "--consumer", "breakdown")
        self.assertEqual(r.returncode, 1)
        self.assertIn("breakdown requires field 'summary'", r.stdout)


class TestSentinelAndHook(unittest.TestCase):
    def test_honest_run_passes_and_is_traced(self):
        f = Fixture()
        f.write("breakdown.json", breakdown(stories_per_epic=(2, 3)))
        self.assertEqual(f.sentinel("breakdown.json").returncode, 0)
        r = f.hook("breakdown.json")
        self.assertEqual(r.returncode, 0, r.stderr)
        trace = f.trace()
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0]["edge"]["exit"], 0)
        self.assertEqual(trace[0]["artifact"], "breakdown.json")

    def test_sentinel_count_mismatch_fails_while_schema_passes(self):
        f = Fixture()
        f.write("breakdown.json", breakdown(stories_per_epic=(2, 3)))  # 5 stories
        f.sentinel("breakdown.json", counts={"stories": 8})            # claims 8
        r = f.hook("breakdown.json")
        self.assertEqual(r.returncode, 2)
        self.assertIn("claims stories=8", r.stderr)
        self.assertIn("holds 5", r.stderr)
        self.assertEqual(f.trace()[0]["edge"]["exit"], 1)

    def test_missing_sentinel_fails(self):
        f = Fixture()
        f.write("breakdown.json", breakdown())
        r = f.hook("breakdown.json")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no readable sentinel", r.stderr)

    def test_artifact_edited_after_sentinel_fails(self):
        f = Fixture()
        f.write("breakdown.json", breakdown())
        f.sentinel("breakdown.json")
        f.write("breakdown.json", breakdown(stories_per_epic=(3,)))  # changed after the claim
        r = f.hook("breakdown.json")
        self.assertEqual(r.returncode, 2)
        self.assertIn("does not match the file", r.stderr)

    def test_downstream_input_contract_fails_at_the_producing_handoff(self):
        f = Fixture()
        doc = dict(TRIAGE)
        del doc["summary"]  # breakdown requires it
        f.write("triage.json", doc)
        f.sentinel("triage.json", step="triage")
        r = f.hook("triage.json")
        self.assertEqual(r.returncode, 2)
        self.assertIn("breakdown requires field 'summary'", r.stderr)

    def test_schema_failure_reported_by_hook(self):
        f = Fixture()
        f.write("triage.json", dict(TRIAGE, path="express"))
        f.sentinel("triage.json", step="triage")
        r = f.hook("triage.json")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not one of", r.stderr)

    def test_non_delivery_repo_untouched(self):
        f = Fixture(delivery_repo=False)
        f.write("breakdown.json", breakdown())
        r = f.hook("breakdown.json")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(f.trace(), [])

    def test_unknown_file_ignored(self):
        f = Fixture()
        (f.item_dir / "notes.txt").write_text("scratch")
        r = f.hook("notes.txt")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(f.trace(), [])

    def test_bash_write_is_checked(self):
        f = Fixture()
        f.write("breakdown.json", breakdown())
        f.sentinel("breakdown.json", counts={"epics": 99})
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "cwd": str(f.dir),
                   "tool_input": {"command": f"cat x > delivery/{f.item}/breakdown.json"}}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("claims epics=99", r.stderr)

    def test_sentinel_itself_is_validated(self):
        f = Fixture()
        f.write("breakdown.json", breakdown())
        f.sentinel("breakdown.json")
        p = f.item_dir / "breakdown.json.sentinel.json"
        bad = json.loads(p.read_text())
        bad["status"] = "mostly"
        p.write_text(json.dumps(bad))
        r = f.hook("breakdown.json.sentinel.json")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not one of", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
