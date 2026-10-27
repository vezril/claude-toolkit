#!/usr/bin/env python3
"""Tests for the router: where an item is, and what runs next.

Run: python3 tests/delivery-flow/test_flow_status.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
FLOW = SCRIPTS / "flow-status.py"

TRIAGE = {"item": "DEM-12", "type": "feature", "path": "standard", "domains": ["backend"],
          "summary": "s", "rationale": "r", "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False}


class Repo:
    def __init__(self, vault=False, item="DEM-12"):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: local-markdown\nforge:\n  kind: github-pr\n"
            + ("vault:\n  binding: olympus\n" if vault else "vault:\n  binding: null\n"))
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def artifact(self, name, doc=None):
        (self.item_dir / name).write_text(json.dumps(doc or {"item": self.item}, indent=2))

    def edge(self, artifact, exit_code=0, summary="ok", step=None):
        rec = {"ts": "2026-10-21T00:00:00+00:00", "item": self.item, "step": step,
               "artifact": artifact, "hook": "check-edge",
               "edge": {"name": "schema", "exit": exit_code, "summary": summary}}
        with (self.item_dir / "trace.jsonl").open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def challenge(self, verdict, target="breakdown.json", findings=(), artifact="challenge-breakdown.json"):
        self.artifact(artifact, {
            "item": self.item, "target": target, "verdict": verdict,
            "attacks": [{"attack": f"a{i}", "method": "checked it against the item", "result":
                         "landed" if verdict != "SURVIVED" and i == 0 else "failed"} for i in range(3)],
            "findings": [{"finding": f, "evidence": "quoted from the artifact"} for f in findings],
        })

    def verdict_record(self, verdict, target="breakdown.json", step="challenge-breakdown"):
        """A challenge run as the trace records it, which is how refutations are counted."""
        rec = {"ts": "2026-10-21T00:00:00+00:00", "item": self.item, "step": step,
               "artifact": "challenge-breakdown.json", "target": target, "verdict": verdict}
        with (self.item_dir / "trace.jsonl").open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def through_breakdown(self):
        """Every artifact up to and including breakdown.json, each with a passing edge."""
        for a in ("item.json", "triage.json"):
            self.artifact(a, TRIAGE if a == "triage.json" else None)
            self.edge(a)
        self.artifact("breakdown.json")
        self.edge("breakdown.json", step="breakdown")
        return self

    def punch_out(self, n=1, text="scope is unclear"):
        p = self.item_dir / f"punch-out-{n}.md"
        p.write_text(f"# Punch-out {n}\n\n{text}\n")
        return p

    def decide(self, n=1, choice="proceed", sha=None):
        import hashlib
        p = self.item_dir / f"punch-out-{n}.md"
        d = self.item_dir / "decisions"
        d.mkdir(exist_ok=True)
        (d / f"punch-out-{n}.json").write_text(json.dumps({
            "id": f"punch-out-{n}", "item": self.item, "trigger": "scope",
            "artifact": p.name, "sha256": sha or hashlib.sha256(p.read_bytes()).hexdigest(),
            "choice": choice, "note": "", "decider": "calvin", "ts": "2026-10-21T00:00:00+00:00",
            "signature": "(test)"}))

    def status(self):
        r = subprocess.run([sys.executable, str(FLOW), self.item, "--json", "--repo", str(self.dir)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)


class TestRouting(unittest.TestCase):
    def test_empty_item_starts_at_intake(self):
        self.assertEqual(Repo().status()["next_step"], "intake")

    def test_after_item_comes_triage(self):
        r = Repo(); r.artifact("item.json"); r.edge("item.json")
        self.assertEqual(r.status()["next_step"], "triage")

    def test_vault_step_skipped_without_a_binding(self):
        r = Repo(vault=False)
        r.artifact("item.json"); r.artifact("triage.json", TRIAGE)
        st = r.status()
        self.assertEqual(st["next_step"], "breakdown")
        self.assertTrue(next(x for x in st["table"] if x["step"] == "project-memory")["skipped"])

    def test_vault_step_runs_when_bound(self):
        r = Repo(vault=True)
        r.artifact("item.json"); r.artifact("triage.json", TRIAGE)
        self.assertEqual(r.status()["next_step"], "project-memory")

    def test_quick_path_skips_the_breakdown(self):
        r = Repo()
        r.artifact("item.json")
        r.artifact("triage.json", dict(TRIAGE, type="bug", path="quick"))
        st = r.status()
        self.assertEqual(st["next_step"], "solutioning")
        for step in ("breakdown", "challenge-breakdown"):
            self.assertTrue(next(x for x in st["table"] if x["step"] == step)["skipped"])


class TestBlocking(unittest.TestCase):
    def test_failed_edge_reruns_the_producing_step(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json")
        r.artifact("triage.json", TRIAGE); r.edge("triage.json", 1, "domains not in the vocabulary: security")
        st = r.status()
        self.assertEqual(st["next_step"], "triage")
        self.assertIn("failed its edge", st["blocked"])
        self.assertIn("security", st["blocked"])

    def test_rerun_limit_becomes_a_punch_out(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json")
        r.artifact("triage.json", TRIAGE)
        for _ in range(3):
            r.edge("triage.json", 1, "schema violation")
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("rerun limit", st["blocked"])

    def test_latest_edge_wins(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json", 1, "bad"); r.edge("item.json", 0, "ok")
        self.assertEqual(r.status()["next_step"], "triage")

    def test_open_punch_out_blocks_everything(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json")
        r.punch_out(1)
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("undecided", st["blocked"])

    def test_proceed_decision_releases_the_flow(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json")
        r.punch_out(1); r.decide(1, "proceed")
        self.assertEqual(r.status()["next_step"], "triage")

    def test_stop_decision_keeps_the_flow_stopped(self):
        r = Repo()
        r.artifact("item.json"); r.punch_out(1); r.decide(1, "stop")
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("decided: stop", st["blocked"])

    def test_editing_a_punch_out_after_deciding_reopens_it(self):
        r = Repo()
        r.artifact("item.json"); p = r.punch_out(1); r.decide(1, "proceed")
        p.write_text("# Punch-out 1\n\nactually something else\n")
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("stale", st["blocked"])


class TestChallengeVerdicts(unittest.TestCase):
    """The verdict routes mechanically. The reviewer is a node; these rules are the code."""

    def test_survived_proceeds(self):
        r = Repo().through_breakdown()
        r.challenge("SURVIVED"); r.edge("challenge-breakdown.json", step="challenge-breakdown")
        st = r.status()
        self.assertEqual(st["next_step"], "solutioning")
        self.assertIsNone(st["blocked"])

    def test_weakened_proceeds_and_carries_its_findings_forward(self):
        r = Repo().through_breakdown()
        r.challenge("WEAKENED", findings=["S2's criteria do not test the toggle it promises"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        st = r.status()
        self.assertEqual(st["next_step"], "solutioning")
        self.assertIsNone(st["blocked"])
        self.assertEqual(st["carry_forward"], ["S2's criteria do not test the toggle it promises"])

    def test_refuted_reruns_the_producing_step(self):
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["the zero-quantity deliverable is in no story"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        st = r.status()
        self.assertEqual(st["next_step"], "breakdown")
        self.assertIn("REFUTED", st["blocked"])
        self.assertIn("zero-quantity", st["blocked"])
        self.assertFalse(st["complete"])

    def test_refuted_does_not_carry_findings_forward(self):
        """A refuted artifact is redone, so its findings are a rerun instruction, not a
        constraint handed to the step after it."""
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["the plan contradicts the item"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        self.assertEqual(r.status()["carry_forward"], [])

    def test_refuted_twice_is_a_punch_out_not_a_third_attempt(self):
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["still missing the zero-quantity work"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        r.verdict_record("REFUTED"); r.verdict_record("REFUTED")
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("REFUTED 2 times", st["blocked"])
        self.assertIn("punch-out", st["blocked"])

    def test_one_refutation_in_the_trace_still_reruns(self):
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["a deliverable is missing"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        r.verdict_record("REFUTED")
        self.assertEqual(r.status()["next_step"], "breakdown")

    def test_a_challenge_of_an_older_breakdown_is_stale(self):
        """The rerun a refutation asks for must not be the thing that keeps the flow blocked:
        once the breakdown is written again, the verdict on disk is about a version that is
        gone, so the challenge reruns rather than the step it already refuted."""
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["a deliverable is missing"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        r.artifact("breakdown.json", {"item": r.item, "v": 2})
        r.edge("breakdown.json", step="breakdown")
        st = r.status()
        self.assertEqual(st["next_step"], "challenge-breakdown")
        self.assertIn("written again", st["blocked"])

    def test_a_survived_verdict_on_an_older_breakdown_is_also_stale(self):
        r = Repo().through_breakdown()
        r.challenge("SURVIVED")
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        r.artifact("breakdown.json", {"item": r.item, "v": 2})
        r.edge("breakdown.json", step="breakdown")
        self.assertEqual(r.status()["next_step"], "challenge-breakdown")

    def test_a_verdict_with_no_trace_at_all_is_taken_as_current(self):
        r = Repo()
        for a in ("item.json", "triage.json"):
            r.artifact(a, TRIAGE if a == "triage.json" else None)
        r.artifact("breakdown.json")
        r.challenge("REFUTED", findings=["a deliverable is missing"])
        self.assertEqual(r.status()["next_step"], "breakdown")

    def test_an_unreadable_challenge_blocks_rather_than_being_ignored(self):
        r = Repo().through_breakdown()
        (r.item_dir / "challenge-breakdown.json").write_text("{not json")
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("cannot be read", st["blocked"])

    def test_an_open_punch_out_outranks_a_refuted_verdict(self):
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["a deliverable is missing"])
        r.edge("challenge-breakdown.json", step="challenge-breakdown")
        r.punch_out(1)
        st = r.status()
        self.assertIsNone(st["next_step"])
        self.assertIn("punch-out-1", st["blocked"])

    def test_a_failed_edge_outranks_a_refuted_verdict(self):
        r = Repo().through_breakdown()
        r.challenge("REFUTED", findings=["a deliverable is missing"])
        r.edge("challenge-breakdown.json", 1, "sentinel count mismatch", step="challenge-breakdown")
        st = r.status()
        self.assertEqual(st["next_step"], "challenge-breakdown")
        self.assertIn("failed its edge", st["blocked"])

    def test_the_quick_path_has_no_verdict_to_route(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json")
        r.artifact("triage.json", dict(TRIAGE, type="bug", path="quick")); r.edge("triage.json")
        st = r.status()
        self.assertEqual(st["next_step"], "solutioning")
        self.assertEqual(st["challenges"], [])


class TestCompletion(unittest.TestCase):
    def test_every_artifact_present_is_complete(self):
        r = Repo()
        import importlib.util
        spec = importlib.util.spec_from_file_location("flow_status", FLOW)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for artifact, _, _, optional_when in mod.STEPS:
            if optional_when == "vault":
                continue
            r.artifact(artifact) if artifact.endswith(".json") else (r.item_dir / artifact).write_text("# prose\n")
            r.edge(artifact)
        st = r.status()
        self.assertTrue(st["complete"])
        self.assertIsNone(st["next_step"])


class TestGuards(unittest.TestCase):
    def test_not_a_delivery_repo(self):
        d = Path(tempfile.mkdtemp()); (d / ".git").mkdir()
        r = subprocess.run([sys.executable, str(FLOW), "DEM-12", "--repo", str(d)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("not a delivery-flow repo", r.stderr)

    def test_torn_trace_line_does_not_crash(self):
        r = Repo()
        r.artifact("item.json"); r.edge("item.json")
        with (r.item_dir / "trace.jsonl").open("a") as f:
            f.write('{"half written\n')
        self.assertEqual(r.status()["next_step"], "triage")


if __name__ == "__main__":
    unittest.main(verbosity=2)
