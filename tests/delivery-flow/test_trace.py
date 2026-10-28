#!/usr/bin/env python3
"""Tests for the audit trail: the trace hook and the report.

Run: python3 tests/delivery-flow/test_trace.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
HOOK = ROOT / "hooks" / "trace-step.py"
REPORT = SCRIPTS / "delivery-report.py"


def transcript(path: Path, model="claude-sonnet-5", messages=1, repeats=1, out=100, inp=10, start=0):
    """A transcript where each API message is repeated `repeats` times, as Claude Code writes it."""
    lines = []
    for i in range(messages):
        rec = {"type": "assistant", "message": {
            "id": f"msg_{start + i}", "model": model,
            "usage": {"input_tokens": inp, "output_tokens": out,
                      "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 500,
                      "cache_creation": {"ephemeral_5m_input_tokens": 500, "ephemeral_1h_input_tokens": 0}}}}
        lines += [json.dumps(rec)] * repeats
    path.write_text("\n".join(lines) + "\n")
    return path


class Repo:
    def __init__(self, item="DEM-12"):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text("tracker:\n  kind: local-markdown\n")
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def current_step(self, step):
        (self.item_dir / ".current-step").write_text(json.dumps({"step": step, "item": self.item}))

    def subagent_stop(self, tpath, agent="general-purpose", agent_id="a1"):
        payload = {"hook_event_name": "SubagentStop", "cwd": str(self.dir), "session_id": "s1",
                   "agent_id": agent_id, "agent_type": agent,
                   "agent_transcript_path": str(tpath), "transcript_path": str(tpath)}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def stop(self, tpath):
        payload = {"hook_event_name": "Stop", "cwd": str(self.dir), "session_id": "s1",
                   "transcript_path": str(tpath)}
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True)

    def trace(self):
        p = self.item_dir / "trace.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []

    def outcome(self, status, reason="", step=""):
        (self.item_dir / "outcome.json").write_text(json.dumps(
            {"item": self.item, "status": status, "reason": reason, "step": step}))

    def report(self, *extra):
        r = subprocess.run([sys.executable, str(REPORT), str(self.dir), "--json", *extra],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)


class TestTraceHook(unittest.TestCase):
    def test_usage_counted_once_per_message(self):
        r = Repo(); r.current_step("breakdown")
        t = transcript(r.dir / "sub.jsonl", messages=1, repeats=6, out=3)
        self.assertEqual(r.subagent_stop(t).returncode, 0)
        rec = r.trace()[0]
        self.assertEqual(rec["output_tokens"], 3, "six repeated lines are one message")
        self.assertEqual(rec["messages"], 1)
        self.assertEqual(rec["step"], "breakdown")

    def test_cost_and_pricing_metadata(self):
        r = Repo(); r.current_step("triage")
        t = transcript(r.dir / "sub.jsonl", model="claude-sonnet-5", messages=2, out=1000, inp=1000)
        r.subagent_stop(t)
        rec = r.trace()[0]
        # Sonnet 5 list rates over 2 messages:
        #   2000 in @ $2/M = 0.0040, 2000 out @ $10/M = 0.0200,
        #   2000 cache read @ $0.20/M = 0.0004, 1000 5m cache write @ $2.50/M = 0.0025
        self.assertAlmostEqual(rec["api_equivalent_cost_usd"], 0.0269, places=4)
        self.assertTrue(rec["pricing_as_of"])

    def test_unknown_model_is_flagged_not_guessed(self):
        r = Repo(); r.current_step("triage")
        t = transcript(r.dir / "sub.jsonl", model="some-other-model")
        r.subagent_stop(t)
        rec = r.trace()[0]
        self.assertIsNone(rec["api_equivalent_cost_usd"])
        self.assertTrue(rec["pricing_missing"])

    def test_model_conformance_against_the_registry(self):
        r = Repo(); r.current_step("triage")  # registry declares sonnet
        r.subagent_stop(transcript(r.dir / "a.jsonl", model="claude-opus-5"), agent_id="a1")
        self.assertFalse(r.trace()[0]["model_conformant"])
        r.subagent_stop(transcript(r.dir / "b.jsonl", model="claude-sonnet-5", start=50), agent_id="a2")
        self.assertTrue(r.trace()[1]["model_conformant"])

    def test_multi_model_transcript_splits_records(self):
        r = Repo(); r.current_step("breakdown")
        p = r.dir / "sub.jsonl"
        p.write_text("\n".join([
            json.dumps({"message": {"id": "m1", "model": "claude-sonnet-5",
                                    "usage": {"input_tokens": 5, "output_tokens": 5}}}),
            json.dumps({"message": {"id": "m2", "model": "claude-haiku-4-5",
                                    "usage": {"input_tokens": 7, "output_tokens": 7}}})]))
        r.subagent_stop(p)
        self.assertEqual({rec["model"] for rec in r.trace()},
                         {"claude-sonnet-5", "claude-haiku-4-5"})

    def test_main_session_counted_once_across_steps(self):
        r = Repo(); r.current_step("triage")
        t = r.dir / "main.jsonl"
        transcript(t, messages=2)
        r.stop(t)
        first = [x for x in r.trace() if x["step"] == "orchestrator"]
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["messages"], 2)
        transcript(t, messages=3)  # the session continues; message ids 0..2
        r.stop(t)
        orchestrator = [x for x in r.trace() if x["step"] == "orchestrator"]
        self.assertEqual(len(orchestrator), 2)
        self.assertEqual(orchestrator[1]["messages"], 1, "only the new message is counted again")

    def test_missing_transcript_records_the_error_not_a_number(self):
        r = Repo(); r.current_step("triage")
        res = r.subagent_stop(r.dir / "nope.jsonl")
        self.assertEqual(res.returncode, 0)
        rec = r.trace()[0]
        self.assertIn("transcript not found", rec["trace_error"])
        self.assertNotIn("input_tokens", rec)

    def test_inert_without_a_current_step(self):
        r = Repo()
        r.subagent_stop(transcript(r.dir / "sub.jsonl"))
        self.assertEqual(r.trace(), [])

    def test_inert_outside_a_delivery_repo(self):
        d = Path(tempfile.mkdtemp()); (d / ".git").mkdir()
        payload = {"hook_event_name": "SubagentStop", "cwd": str(d), "session_id": "s",
                   "agent_transcript_path": str(transcript(d / "t.jsonl"))}
        res = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertFalse((d / "delivery").exists())


class TestReport(unittest.TestCase):
    def test_both_readings_of_the_rate(self):
        base = Path(tempfile.mkdtemp())
        (base / ".git").mkdir(); (base / ".delivery-flow.yaml").write_text("tracker:\n  kind: local-markdown\n")
        # a week with 4 completed, 1 failed, 2 punched out
        for i, status in enumerate(["completed"] * 4 + ["failed"] + ["punched-out"] * 2):
            d = base / "delivery" / f"I-{i}"
            d.mkdir(parents=True)
            (d / "trace.jsonl").write_text(json.dumps({
                "ts": "2026-10-20T10:00:00+00:00", "item": f"I-{i}", "step": "triage",
                "model": "claude-sonnet-5", "input_tokens": 10, "output_tokens": 10,
                "cache_creation_tokens": 0, "cache_read_tokens": 0,
                "api_equivalent_cost_usd": 0.0001, "certified": True}) + "\n")
            (d / "outcome.json").write_text(json.dumps({"item": f"I-{i}", "status": status}))
        r = subprocess.run([sys.executable, str(REPORT), str(base), "--json"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        week = list(json.loads(r.stdout)["weekly"].values())[0]["all"]
        self.assertAlmostEqual(week["rate_excluding_punch_outs"], 80.0)
        self.assertAlmostEqual(week["rate_counting_punch_outs"], 4 / 7 * 100, places=1)

    def test_uncertified_run_excluded_from_the_stage4_rate(self):
        r = Repo(); r.current_step("triage")
        (r.item_dir / "trace.jsonl").write_text(json.dumps({
            "ts": "2026-10-20T10:00:00+00:00", "item": r.item, "step": "triage",
            "model": "claude-sonnet-5", "input_tokens": 1, "output_tokens": 1,
            "api_equivalent_cost_usd": 0.0, "certified": False}) + "\n")
        r.outcome("completed")
        week = list(r.report()["weekly"].values())[0]
        self.assertEqual(week["all"]["completed"], 1)
        self.assertEqual(week["certified_only"]["completed"], 0)

    def test_markdown_labels_cost_as_api_equivalent(self):
        r = Repo(); r.current_step("triage")
        r.subagent_stop(transcript(r.dir / "sub.jsonl"))
        r.outcome("completed")
        out = subprocess.run([sys.executable, str(REPORT), str(r.dir)], capture_output=True, text=True)
        self.assertIn("API-equivalent", out.stdout)
        self.assertIn("not billed per token", out.stdout)


class TestUncertifiedStepsDoNotCount(unittest.TestCase):
    """An `allow_uncertified` step must record certified: False, not None.

    `delivery-report.py` tests `rec.get("certified") is False`, so None would let a run with an
    uncertified node in the chain into the certified-only Stage 4 rate — the one number that is
    meaningless if any node is uncertified.
    """

    def test_a_step_with_no_registry_entry_records_certified_false(self):
        r = Repo()
        r.current_step("propose")          # a real step, deliberately not in steps.yaml
        t = transcript(r.dir / "sub.jsonl", model="claude-sonnet-5", messages=1, out=10, inp=10)
        self.assertEqual(r.subagent_stop(t).returncode, 0)
        recs = [x for x in r.trace() if x.get("step") == "propose" and "certified" in x]
        self.assertTrue(recs, "no step record was written")
        for rec in recs:
            self.assertIs(rec["certified"], False)
            self.assertIsNot(rec["certified"], None)

    def test_the_report_excludes_it_from_the_certified_only_rate(self):
        r = Repo()
        r.current_step("propose")
        t = transcript(r.dir / "sub.jsonl", model="claude-sonnet-5", messages=1, out=10, inp=10)
        r.subagent_stop(t)
        r.outcome("completed")
        payload = r.report()
        row = payload["items"][0]
        self.assertFalse(row["certified"])
        week = list(payload["weekly"].values())[0]
        self.assertEqual(week["certified_only"]["completed"], 0)
        self.assertEqual(week["all"]["completed"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
