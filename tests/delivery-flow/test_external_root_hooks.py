#!/usr/bin/env python3
"""The hooks under a configured `artifacts.root` outside the repo.

Every other fixture in this suite uses the default in-repo `delivery/`, which is why the
`artifacts.root` branch shipped broken: `check-edge` globbed the configured root correctly and
then parsed the result without it, so every artifact under an external root returned
`(None, None)` and was skipped. Edges silently stopped running. `enforce-punch-outs` went inert
for a related reason — it gated on the payload containing the string `delivery/`, which never
appears once the root moves.

The paths here contain a space on purpose. The real root is `~/Amazon RAG/Atlas/RAG/_runs`, and
a quoting bug would be invisible against a tmpdir with no spaces in it.

Run: python3 tests/delivery-flow/test_external_root_hooks.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
EDGE = ROOT / "hooks" / "check-edge.py"
ENFORCE = ROOT / "hooks" / "enforce-punch-outs.py"
sys.path.insert(0, str(SCRIPTS))

TRIAGE = {"item": "AN-1", "type": "feature", "path": "standard", "domains": ["backend"],
          "summary": "s", "rationale": "r", "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False}


def breakdown(stories=2):
    return {"item": "AN-1", "epics": [{"id": "E1", "title": "T", "stories": [
        {"id": f"S{i}", "statement": f"story {i}", "domains": ["backend"],
         "acceptance_criteria": [{"id": f"AC{i}", "given": "g", "when": "w", "then": "t"}]}
        for i in range(1, stories + 1)]}]}


class ExternalRoot:
    """A delivery repo whose artifacts live outside it, in a path containing a space."""

    def __init__(self):
        base = Path(tempfile.mkdtemp())
        self.runs = base / "Amazon RAG" / "Atlas" / "RAG" / "_runs"
        self.runs.mkdir(parents=True)
        self.repo = base / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        (self.repo / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\nprofile: full\n"
            f"artifacts:\n  root: {self.runs}\n  commit: false\n"
            "decisions:\n  allowed_signers: /nonexistent/allowed_signers\n")
        self.item = "AN-1"
        self.item_dir = self.runs / self.item
        self.item_dir.mkdir()

    def write(self, name, doc):
        (self.item_dir / name).write_text(json.dumps(doc, indent=2))

    def sentinel(self, name, step, counts=None):
        argv = [sys.executable, str(SCRIPTS / "write-sentinel.py"),
                str(self.item_dir / name), "--step", step]
        for key, value in (counts or {}).items():
            argv += ["--count", f"{key}={value}"]
        return subprocess.run(argv, capture_output=True, text=True)

    def edge(self, name, tool="Write"):
        payload = {"hook_event_name": "PostToolUse", "tool_name": tool,
                   "cwd": str(self.repo),
                   "tool_input": {"file_path": str(self.item_dir / name)} if tool == "Write"
                   else {"command": f'cat x > "{self.item_dir / name}"'}}
        return subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def enforce(self, tool, tool_input):
        payload = {"hook_event_name": "PreToolUse", "tool_name": tool,
                   "cwd": str(self.repo), "tool_input": tool_input}
        return subprocess.run([sys.executable, str(ENFORCE)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def trace(self):
        path = self.item_dir / "trace.jsonl"
        if not path.exists():
            return []
        return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

    def open_punch_out(self):
        (self.item_dir / "punch-out-1.md").write_text("# Punch-out 1: architecture\n\nbody\n")
        (self.item_dir / ".current-step").write_text(
            json.dumps({"step": "breakdown", "item": self.item}))


class TestEdgeUnderExternalRoot(unittest.TestCase):
    def test_a_good_artifact_is_checked_and_traced(self):
        """The defect: the glob found it, the parse threw it away, nothing was recorded."""
        r = ExternalRoot()
        r.write("breakdown.json", breakdown())
        self.assertEqual(r.sentinel("breakdown.json", "breakdown").returncode, 0)
        out = r.edge("breakdown.json")
        self.assertEqual(out.returncode, 0, out.stderr)
        records = [x for x in r.trace() if x.get("artifact") == "breakdown.json"]
        self.assertTrue(records, "the edge produced no trace record under an external root")
        self.assertEqual(records[-1]["edge"]["exit"], 0)

    def test_a_bad_artifact_is_rejected(self):
        r = ExternalRoot()
        r.write("triage.json", {**TRIAGE, "type": "enhancement", "handoff": "yes"})
        r.sentinel("triage.json", "triage")
        out = r.edge("triage.json")
        self.assertEqual(out.returncode, 2, "a schema violation must still block")
        self.assertIn("enhancement", out.stderr)

    def test_a_sentinel_count_lie_is_caught(self):
        r = ExternalRoot()
        r.write("breakdown.json", breakdown(stories=2))
        r.sentinel("breakdown.json", "breakdown", counts={"stories": 99})
        out = r.edge("breakdown.json")
        self.assertEqual(out.returncode, 2)
        self.assertIn("99", out.stderr)

    def test_content_detection_catches_a_write_the_command_text_hides(self):
        """The handoff asked for this to be confirmed, not assumed.

        A Bash redirect through a shell variable under an external root leaves no
        `delivery/`-shaped fragment in the command, so only content comparison can find it.
        """
        r = ExternalRoot()
        r.write("breakdown.json", breakdown())
        r.sentinel("breakdown.json", "breakdown", counts={"stories": 99})
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(r.repo),
                   "tool_input": {"command": f'R="{r.item_dir}"; cat x > "$R/breakdown.json"'}}
        out = subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 2, f"content detection missed it: {out.stderr}")
        self.assertIn("99", out.stderr)

    def test_a_space_in_the_root_does_not_break_it(self):
        r = ExternalRoot()
        self.assertIn(" ", str(r.runs))
        r.write("breakdown.json", breakdown())
        r.sentinel("breakdown.json", "breakdown")
        self.assertEqual(r.edge("breakdown.json").returncode, 0)
        self.assertTrue(r.trace())

    def test_it_stays_inert_in_a_repo_with_no_config(self):
        plain = Path(tempfile.mkdtemp())
        (plain / ".git").mkdir()
        (plain / "delivery" / "AN-1").mkdir(parents=True)
        (plain / "delivery" / "AN-1" / "notes.txt").write_text("scratch")
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": str(plain),
                   "tool_input": {"file_path": str(plain / "delivery" / "AN-1" / "notes.txt")}}
        out = subprocess.run([sys.executable, str(EDGE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)


class TestEnforceUnderExternalRoot(unittest.TestCase):
    def test_a_decision_write_is_denied(self):
        """The hook that matters most: nobody but a human writes a decision."""
        r = ExternalRoot()
        r.open_punch_out()
        out = r.enforce("Write", {"file_path": str(r.item_dir / "decisions" / "punch-out-1.json"),
                                  "content": '{"choice":"proceed"}'})
        self.assertIn("deny", out.stdout.lower() + out.stderr.lower(),
                      f"a decision write was permitted under an external root: {out.stdout}")

    def test_invoking_decide_py_is_denied(self):
        r = ExternalRoot()
        r.open_punch_out()
        out = r.enforce("Bash", {"command": f"python3 {SCRIPTS}/decide.py AN-1 punch-out-1 "
                                            "--choose proceed"})
        self.assertIn("deny", out.stdout.lower() + out.stderr.lower())

    def test_a_merge_is_denied(self):
        r = ExternalRoot()
        r.open_punch_out()
        out = r.enforce("Bash", {"command": "gh pr merge 12 --squash"})
        self.assertIn("deny", out.stdout.lower() + out.stderr.lower())

    def test_it_stays_inert_outside_a_delivery_repo(self):
        plain = Path(tempfile.mkdtemp())
        (plain / ".git").mkdir()
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": str(plain),
                   "tool_input": {"command": "gh pr merge 12 --squash"}}
        out = subprocess.run([sys.executable, str(ENFORCE)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertNotIn("deny", out.stdout.lower(),
                         "the hook must be inert where no delivery-flow config exists")


if __name__ == "__main__":
    unittest.main(verbosity=2)
