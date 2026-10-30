#!/usr/bin/env python3
"""An artifact nothing checked must say so, rather than leaving a silence.

Eight artifacts in the routing table have no schema: implementation.json, verify.json,
challenge-implementation.json, pr-opened.json, posted.json, vault-updated.json, and the
`pr.md` / `post.md` prose. Every one sits in the `full` profile past `propose`, so the gap is
plausibly a profile whose edges were never built — but nothing in the pipeline could say that,
because `changed_artifacts` skipped a missing schema with a bare `continue`. No check ran, no
record said none had, `flow-status.py` printed "no edge recorded" beside a **✓**, and the trace
that criterion 4 is computed from held nothing at all.

This is the fourth instance of one class found in two days, and the other three were the same
shape: defect 12 handed the wrong diff to a correct matcher, the story schema handed nothing to
a correct validator, and the architecture derivation handed the guarded node's own reasoning to
a correct trigger. In each the checker was right and tested, and the dispatch to it was wrong
and untested. So these tests sit at the dispatch boundary on purpose: they assert a record
*exists*, not that a check passed.

Recording the gap does not close it. These artifacts are still unchecked; what changes is that
the absence is countable, the way an uncertified step is countable because it records
`certified: false` instead of quietly not being certified.

Run: python3 tests/delivery-flow/test_unchecked_edges.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "check-edge.py"
SCRIPTS = ROOT / "scripts" / "delivery-flow"
FLOW = SCRIPTS / "flow-status.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(SCRIPTS))
import common  # noqa: E402

flow_status = _load("flow_status", FLOW)
check_edge = _load("check_edge", HOOK)


class Repo:
    def __init__(self, item="DEM-12"):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: local-markdown\n  external: false\n")
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def write(self, name, doc):
        p = self.item_dir / name
        p.write_text(json.dumps(doc, indent=2) if isinstance(doc, (dict, list)) else str(doc))
        return p

    def hook(self, name):
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                   "cwd": str(self.dir), "session_id": "s1",
                   "tool_input": {"file_path": str(self.item_dir / name)}}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def bash(self, command):
        payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                   "cwd": str(self.dir), "session_id": "s1",
                   "tool_input": {"command": command}}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def trace(self):
        p = self.item_dir / "trace.jsonl"
        if not p.exists():
            return []
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

    def records_for(self, artifact):
        return [r for r in self.trace() if r.get("artifact") == artifact]


class TestTheGapIsIdentified(unittest.TestCase):

    def setUp(self):
        self.schemas = common.load_schemas()
        self.governed = check_edge.unschemad(flow_status, common, self.schemas)

    def test_the_eight_unschemad_routing_table_artifacts(self):
        """Pinned. If this set changes, a schema was added or an artifact was renamed, and
        either way the report's unchecked count means something different."""
        self.assertEqual(
            {"implementation.json", "verify.json", "challenge-implementation.json",
             "pr.md", "pr-opened.json", "post.md", "posted.json", "vault-updated.json"},
            self.governed)

    def test_the_certified_chains_artifacts_are_all_governed(self):
        """The triage profile is the Stage 4 chain; none of its artifacts may be unchecked."""
        for artifact in ("item.json", "triage.json", "project-context.json",
                         "breakdown.json", "challenge-breakdown.json", "outcome.json"):
            with self.subTest(artifact=artifact):
                self.assertNotIn(artifact, self.governed)
                self.assertIsNotNone(common.schema_for(artifact, self.schemas))

    def test_summary_md_is_not_counted_unchecked(self):
        """It has no schema but it does have a checker, so it is governed, not unchecked."""
        self.assertNotIn("summary.md", self.governed)
        self.assertIn("summary.md", check_edge.TERMINAL_PROSE)


class TestTheGapIsRecorded(unittest.TestCase):

    def test_an_unschemad_artifact_gets_a_trace_record(self):
        r = Repo()
        out = r.hook("verify.json") if r.write("verify.json", {"tests": "green"}) else None
        self.assertEqual(0, out.returncode, out.stderr)
        records = r.records_for("verify.json")
        self.assertEqual(1, len(records), f"expected one record, got {r.trace()}")
        self.assertEqual("no-schema", records[0]["edge"]["name"])
        self.assertEqual(0, records[0]["edge"]["exit"])

    def test_the_record_does_not_say_ok(self):
        """"ok" against an unchecked artifact is the false-success this exists to remove."""
        r = Repo()
        r.write("implementation.json", {"done": True})
        r.hook("implementation.json")
        summary = r.records_for("implementation.json")[0]["edge"]["summary"]
        self.assertNotEqual("ok", summary)
        self.assertIn("no schema", summary)

    def test_the_record_carries_the_sha_of_the_bytes_nothing_checked(self):
        r = Repo()
        p = r.write("posted.json", {"posted": True})
        r.hook("posted.json")
        self.assertEqual(common.sha256(p), r.records_for("posted.json")[0]["sha256"])

    def test_an_unrelated_command_does_not_append_another_record(self):
        """What the sha is for. `changed_artifacts` rescans the whole artifact root on every
        command, so without a recorded sha to compare against, an unchecked artifact would
        collect a fresh record for the rest of the run."""
        r = Repo()
        r.write("posted.json", {"posted": True})
        r.hook("posted.json")
        before = len(r.records_for("posted.json"))
        self.assertEqual(1, before)
        r.bash("ls delivery/")
        r.bash("echo unrelated")
        self.assertEqual(before, len(r.records_for("posted.json")), "the record re-fired")

    def test_a_rewrite_records_again_as_a_schemad_artifact_would(self):
        """A write is an event, and the trace is append-only. Verified against a schema'd
        artifact too: rewriting `triage.json` also appends a second record, so unchecked
        artifacts are not behaving specially here."""
        r = Repo()
        r.write("posted.json", {"posted": True})
        r.hook("posted.json")
        r.write("posted.json", {"posted": False})
        r.hook("posted.json")
        self.assertEqual(2, len(r.records_for("posted.json")))

    def test_an_unchecked_artifact_does_not_block_the_flow(self):
        """Nothing checked it, so there is nothing for it to have failed. Exiting 2 here would
        halt the whole full profile on an absence rather than on a defect."""
        r = Repo()
        r.write("vault-updated.json", {"committed": True})
        self.assertEqual(0, r.hook("vault-updated.json").returncode)

    def test_malformed_json_in_an_unchecked_artifact_still_does_not_block(self):
        """It is unchecked: not even parsed. Recording must not smuggle in a parse gate."""
        r = Repo()
        (r.item_dir / "verify.json").write_text("{not json")
        out = r.hook("verify.json")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual("no-schema", r.records_for("verify.json")[0]["edge"]["name"])

    def test_prose_artifacts_are_recorded_too(self):
        r = Repo()
        (r.item_dir / "pr.md").write_text("# A pull request\n")
        r.hook("pr.md")
        self.assertEqual("no-schema", r.records_for("pr.md")[0]["edge"]["name"])


class TestNonArtifactsStayOut(unittest.TestCase):
    """The trail must not fill with records of the hook's own leavings."""

    def test_a_punch_out_file_is_not_recorded(self):
        r = Repo()
        (r.item_dir / "punch-out-1.md").write_text("# Punch-out 1: scope\n")
        r.hook("punch-out-1.md")
        self.assertEqual([], r.records_for("punch-out-1.md"))

    def test_the_trace_itself_is_not_recorded(self):
        """A record of writing the trace would be appended to the trace, forever."""
        r = Repo()
        r.write("verify.json", {"tests": "green"})
        r.hook("verify.json")
        before = len(r.trace())
        r.hook("trace.jsonl")
        self.assertEqual([], r.records_for("trace.jsonl"))
        self.assertEqual(before, len(r.trace()))

    def test_the_current_step_marker_is_not_recorded(self):
        r = Repo()
        (r.item_dir / ".current-step").write_text(json.dumps({"step": "verify"}))
        r.hook(".current-step")
        self.assertEqual([], r.records_for(".current-step"))

    def test_a_decision_file_is_not_recorded(self):
        r = Repo()
        (r.item_dir / "decisions").mkdir()
        (r.item_dir / "decisions" / "punch-out-1.json").write_text('{"choice":"proceed"}')
        r.hook("decisions/punch-out-1.json")
        self.assertEqual([], r.records_for("punch-out-1.json"))


class TestItReadsAsUnchecked(unittest.TestCase):
    """A ✓ beside an unchecked artifact is the bug, so the display is part of the fix."""

    def test_flow_status_does_not_tick_an_unchecked_artifact(self):
        r = Repo()
        r.write("item.json", {"key": r.item, "title": "t", "body": "b", "status": "Open",
                              "url": "https://example.invalid/1", "source": "local-markdown",
                              "labels": [], "links": []})
        r.write("verify.json", {"tests": "green"})
        r.hook("verify.json")
        out = subprocess.run([sys.executable, str(FLOW), r.item, "--repo", str(r.dir)],
                             capture_output=True, text=True)
        line = next((l for l in out.stdout.splitlines() if "verify.json" in l), "")
        self.assertIn("unchecked", line, out.stdout)
        self.assertNotIn("✓", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
