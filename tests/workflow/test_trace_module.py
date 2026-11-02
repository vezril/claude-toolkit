#!/usr/bin/env python3
"""The trace's damage policy, which three readers used to decide differently.

Before the extraction, `common.append_trace` wrote the lines and two readers parsed them:
`check-punch-out.read_trace` and `check-edge.last_traced_sha`. They disagreed about a missing
file, a blank line and a malformed line — in a system where the trace is one of the five
things the Stage 4 certification examines. A record dropped by one reader and kept by another
is an audit trail that answers differently depending on who asks.

These tests pin the single policy: **unreadable is empty, unparseable is skipped, never
fatal.** A hook must not crash because an earlier write was interrupted; losing one record is
recoverable, taking down every subsequent edge check is not.

Run: python3 tests/workflow/test_trace_module.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
import common  # noqa: E402
import trace as trace_mod  # noqa: E402


class TestRoundTrip(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "nested" / "trace.jsonl"

    def test_append_creates_the_directory(self):
        """A new item has no directory yet; the first write must not need one."""
        trace_mod.append(self.path, {"step": "triage"})
        self.assertTrue(self.path.is_file())

    def test_records_come_back_oldest_first(self):
        for i in range(3):
            trace_mod.append(self.path, {"n": i})
        self.assertEqual([r["n"] for r in trace_mod.read(self.path)], [0, 1, 2])

    def test_one_record_per_line(self):
        trace_mod.append(self.path, {"a": 1})
        trace_mod.append(self.path, {"b": 2})
        self.assertEqual(len(self.path.read_text().strip().splitlines()), 2)

    def test_keys_are_sorted_so_records_are_diffable(self):
        trace_mod.append(self.path, {"z": 1, "a": 2})
        self.assertTrue(self.path.read_text().startswith('{"a"'))


class TestTheDamagePolicy(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "trace.jsonl"

    def test_a_missing_file_reads_as_empty(self):
        self.assertEqual(trace_mod.read(self.dir / "nope.jsonl"), [])

    def test_a_directory_in_place_of_the_file_reads_as_empty(self):
        """OSError, not just FileNotFoundError — the old readers differed here."""
        (self.dir / "adir.jsonl").mkdir()
        self.assertEqual(trace_mod.read(self.dir / "adir.jsonl"), [])

    def test_blank_lines_are_skipped(self):
        self.path.write_text('{"a": 1}\n\n   \n{"b": 2}\n')
        self.assertEqual(len(trace_mod.read(self.path)), 2)

    def test_a_malformed_line_is_skipped_not_fatal(self):
        self.path.write_text('{"a": 1}\nnot json at all\n{"b": 2}\n')
        self.assertEqual([list(r)[0] for r in trace_mod.read(self.path)], ["a", "b"])

    def test_a_truncated_final_line_does_not_lose_the_rest(self):
        """The realistic damage: a write interrupted mid-line."""
        self.path.write_text('{"a": 1}\n{"b": 2}\n{"c": ')
        self.assertEqual(len(trace_mod.read(self.path)), 2)

    def test_a_json_scalar_line_is_kept(self):
        """`json.loads("3")` succeeds. Documenting it rather than pretending otherwise."""
        self.path.write_text("3\n")
        self.assertEqual(trace_mod.read(self.path), [3])


class TestTheDeliveryFlowShims(unittest.TestCase):
    """`common.append_trace` / `read_trace` must route through this module."""

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        (self.repo / ".git").mkdir()
        (self.repo / ".delivery-flow.yaml").write_text("profile: full\n")

    def test_append_then_read_through_common(self):
        common.append_trace(self.repo, "AN-1", {"step": "triage", "artifact": "triage.json"})
        records = common.read_trace(self.repo, "AN-1")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["step"], "triage")

    def test_common_writes_where_trace_path_says(self):
        common.append_trace(self.repo, "AN-1", {"step": "triage"})
        self.assertTrue(common.trace_path(self.repo, "AN-1").is_file())

    def test_read_trace_on_an_item_that_never_ran_is_empty(self):
        self.assertEqual(common.read_trace(self.repo, "AN-NOPE"), [])

    def test_the_two_readers_now_agree_on_a_damaged_trace(self):
        """The regression this slice exists to prevent.

        `check-punch-out.read_trace` and the substrate's `read` must return the same records
        for the same damaged file. They were separate implementations and differed.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cpo", ROOT / "scripts" / "delivery-flow" / "check-punch-out.py")
        cpo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cpo)

        item_dir = common.item_dir(self.repo, "AN-1")
        item_dir.mkdir(parents=True, exist_ok=True)
        (item_dir / "trace.jsonl").write_text('{"a": 1}\n\nbroken\n{"b": 2}\n{"c": ')

        self.assertEqual(cpo.read_trace(item_dir),
                         trace_mod.read(item_dir / "trace.jsonl"))
        self.assertEqual(len(cpo.read_trace(item_dir)), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
