#!/usr/bin/env python3
"""Tests for the brief: the chain's terminal prose, and what its edge holds it to.

Run: python3 tests/delivery-flow/test_render_brief.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
RENDER = SCRIPTS / "render-brief.py"
EDGE = ROOT / "hooks" / "check-edge.py"

sys.path.insert(0, str(SCRIPTS))
import brief  # noqa: E402

ITEM = {"key": "BRF-1", "title": "Retries hammer the consumer", "body": "No backoff anywhere.",
        "status": "Open", "url": "https://example.invalid/BRF-1", "source": "jira",
        "labels": ["dlq"], "links": []}
TRIAGE = {"item": "BRF-1", "type": "feature", "path": "standard", "domains": ["backend", "infra"],
          "summary": "Add bounded backoff to the consumer.", "rationale": "Retries amplify load.",
          "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False}
BREAKDOWN = {"item": "BRF-1", "epics": [{"id": "E1", "title": "Backoff", "stories": [
    {"id": "S1", "statement": "Retry with capped exponential backoff", "domains": ["backend"],
     "acceptance_criteria": [{"id": "AC1", "given": "a timeout", "when": "it retries",
                              "then": "delays grow to a 30s cap"}]},
    {"id": "S2", "statement": "Emit a metric per attempt", "domains": ["infra"],
     "acceptance_criteria": [{"id": "AC2", "given": "a retry", "when": "scheduled",
                              "then": "a counter increments"}]}]}]}
WEAKENED = {"item": "BRF-1", "target": "breakdown.json", "verdict": "WEAKENED",
            "attacks": [{"attack": "a", "method": "m", "result": "landed"},
                        {"attack": "b", "method": "m", "result": "failed"},
                        {"attack": "c", "method": "m", "result": "failed"}],
            "findings": [{"finding": "No story covers idempotent redelivery.",
                          "evidence": "AC1 describes timing only."}]}
SURVIVED = {**WEAKENED, "verdict": "SURVIVED", "findings": []}
PROPOSAL = {"item": "BRF-1", "change_id": "add-bounded-backoff",
            "change_path": "openspec/changes/add-bounded-backoff",
            "specs_touched": ["openspec/changes/add-bounded-backoff/specs/retry/spec.md"],
            "tasks": [{"id": "T1", "description": "Add the backoff schedule",
                       "files": ["src/Consumer.scala"]},
                      {"id": "T2", "description": "Emit a retry metric",
                       "files": ["src/Metrics.scala"]}],
            "dependencies_added": ["cats-retry"],
            "scope": False, "architecture": False, "breaking": False}


SENTINEL = SCRIPTS / "write-sentinel.py"
# Keyed on each schema's own `artifact` field, not on its filename: challenge.schema.json
# describes challenge-breakdown.json, so deriving the name from the file misses it.
PRODUCED_BY = {}
for _p in sorted((ROOT / "schemas").glob("*.schema.json")):
    _s = json.loads(_p.read_text())
    if _s.get("artifact") and _s.get("produced_by"):
        PRODUCED_BY[_s["artifact"]] = _s["produced_by"]


class Repo:
    def __init__(self, item="BRF-1"):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\n  external: true\nprofile: triage\nvault:\n  binding: null\n")
        self.item = item
        self.item_dir = self.dir / "delivery" / item
        self.item_dir.mkdir(parents=True)

    def write(self, name, doc):
        """Write an upstream artifact *and its sentinel*.

        A real pipeline never leaves an artifact without one — the node writes the sentinel as
        its last action — so a fixture that omitted them was modelling an impossible state.
        It only surfaced once the edge hook started detecting writes by content rather than by
        parsing the command line, at which point these upstream files became visible to it.
        """
        (self.item_dir / name).write_text(json.dumps(doc, indent=2))
        step = PRODUCED_BY.get(name)
        if step:
            subprocess.run([sys.executable, str(SENTINEL), str(self.item_dir / name),
                            "--step", step], capture_output=True, text=True, check=False)
        if name == "proposal.json":
            self.scaffold_change(doc)

    def scaffold_change(self, proposal):
        """Create the OpenSpec change directory the proposal declares.

        `propose` always writes both — the directory for humans, the JSON as the edge — so a
        proposal.json without its change directory is another state the pipeline cannot
        produce. The proposal edge checks the two agree, and now that the hook finds artifacts
        by content it checks this one too.
        """
        change = self.dir / proposal["change_path"]
        (change / "specs").mkdir(parents=True, exist_ok=True)
        (change / "proposal.md").write_text("## Why\n\nFixture.\n")
        (change / "design.md").write_text("## Decisions\n\nFixture.\n")
        for spec in proposal.get("specs_touched", []):
            path = self.dir / spec
            path.parent.mkdir(parents=True, exist_ok=True)
            # Shaped to pass `openspec validate --strict`, which the proposal edge runs:
            # SHALL wording plus at least one scenario per requirement.
            path.write_text(
                "## ADDED Requirements\n\n"
                "### Requirement: Bounded backoff\n"
                "The consumer SHALL cap its retry delay.\n\n"
                "#### Scenario: The delay stops growing\n\n"
                "- **WHEN** retries exceed the cap\n"
                "- **THEN** the delay stays at the cap\n")
        tasks = "\n".join(f"- [ ] {task['id']} {task['description']}"
                           for task in proposal.get("tasks", []))
        (change / "tasks.md").write_text(f"## 1. Work\n\n{tasks}\n")

    def render(self, *args):
        return subprocess.run([sys.executable, str(RENDER), self.item, "--repo", str(self.dir),
                               *args], capture_output=True, text=True)

    def edge(self):
        payload = json.dumps({"tool_name": "Write",
                              "tool_input": {"file_path": str(self.item_dir / "summary.md")},
                              "cwd": str(self.dir)})
        return subprocess.run([sys.executable, str(EDGE)], input=payload,
                              capture_output=True, text=True)

    def trace(self):
        path = self.item_dir / "trace.jsonl"
        return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def standard(r):
    r.write("item.json", ITEM)
    r.write("triage.json", TRIAGE)
    r.write("breakdown.json", BREAKDOWN)
    r.write("challenge-breakdown.json", WEAKENED)
    return r


class TestRendering(unittest.TestCase):
    def test_the_brief_is_reproducible(self):
        r = standard(Repo())
        first = r.render("--stdout").stdout
        second = r.render("--stdout").stdout
        self.assertEqual(first, second)
        self.assertNotIn("202", first.split("\n")[0])  # no timestamp anywhere in the title

    def test_every_section_is_present_in_order(self):
        r = standard(Repo())
        text = r.render("--stdout").stdout
        positions = [text.index(f"## {s}") for s in brief.SECTIONS]
        self.assertEqual(positions, sorted(positions))

    def test_an_empty_section_says_so_rather_than_vanishing(self):
        r = standard(Repo())
        r.write("challenge-breakdown.json", SURVIVED)
        text = r.render("--stdout").stdout
        self.assertIn(f"## {brief.SECTIONS[4]}", text)
        self.assertIn("no findings require an answer", text)

    def test_the_quick_path_keeps_the_same_shape(self):
        r = Repo()
        r.write("item.json", ITEM)
        r.write("triage.json", {**TRIAGE, "type": "bug", "path": "quick"})
        text = r.render("--stdout").stdout
        for s in brief.SECTIONS:
            self.assertIn(f"## {s}", text)
        self.assertIn("quick path, which writes no breakdown", text)
        self.assertIn("quick path does not challenge", text)

    def test_counts_and_ids_are_carried(self):
        text = standard(Repo()).render("--stdout").stdout
        self.assertIn("1 epic, 2 stories, 2 acceptance criteria", text)
        for ident in ("E1", "S1", "S2"):
            self.assertIn(ident, text)

    def test_flags_are_named_when_raised(self):
        r = standard(Repo())
        r.write("triage.json", {**TRIAGE, "breaking_change": True, "handoff": True})
        text = r.render("--stdout").stdout
        self.assertIn("scope handoff", text)
        self.assertIn("breaking change", text)

    def test_an_open_punch_out_is_surfaced_as_the_decision(self):
        r = standard(Repo())
        (r.item_dir / "punch-out-1.md").write_text("# Punch-out 1: architecture\n\nbody\n")
        text = r.render("--stdout").stdout
        self.assertIn("architecture", text)
        self.assertIn("punch-out-1.md", text)

    def test_a_missing_required_input_is_an_error_not_an_empty_brief(self):
        r = Repo()
        r.write("item.json", ITEM)
        out = r.render()
        self.assertEqual(out.returncode, 2)
        self.assertIn("triage.json is required", out.stderr)
        self.assertFalse((r.item_dir / "summary.md").exists())

    def test_no_sentinel_is_written(self):
        """The producer is a script: there is no claim to test, so there is no sentinel."""
        r = standard(Repo())
        r.render()
        self.assertFalse((r.item_dir / "summary.md.sentinel.json").exists())


class TestProposalSection(unittest.TestCase):
    def test_the_section_is_present_and_explicit_without_a_proposal(self):
        text = standard(Repo()).render("--stdout").stdout
        self.assertIn(f"## {brief.SECTIONS[4]}", text)
        self.assertIn("no change has been proposed", text)

    def test_the_proposal_is_summarised(self):
        r = standard(Repo())
        r.write("proposal.json", PROPOSAL)
        text = r.render("--stdout").stdout
        self.assertIn("add-bounded-backoff", text)
        self.assertIn("2 tasks, 2 files", text)
        self.assertIn("T1: Add the backoff schedule", text)
        self.assertIn("T2: Emit a retry metric", text)
        self.assertIn("src/Consumer.scala", text)
        self.assertIn("New dependencies: cats-retry", text)

    def test_proposal_flags_are_named(self):
        r = standard(Repo())
        r.write("proposal.json", {**PROPOSAL, "breaking": True, "scope": True})
        text = r.render("--stdout").stdout
        self.assertIn("Flags on the proposal: scope, breaking", text)

    def test_section_order_holds_with_a_proposal(self):
        r = standard(Repo())
        r.write("proposal.json", PROPOSAL)
        text = r.render("--stdout").stdout
        positions = [text.index(f"## {s}") for s in brief.SECTIONS]
        self.assertEqual(positions, sorted(positions))

    def test_every_proposal_task_must_reach_the_page(self):
        r = standard(Repo())
        r.write("proposal.json", PROPOSAL)
        r.render()
        self.assertEqual(r.edge().returncode, 0)
        p = r.item_dir / "summary.md"
        p.write_text("\n".join(l for l in p.read_text().split("\n")
                               if not l.startswith("- T2:")))
        out = r.edge()
        self.assertEqual(out.returncode, 2)
        self.assertIn("T2 is in proposal.json but not in the brief", out.stderr)

    def test_proposal_file_paths_are_not_flagged_as_invented(self):
        """The files the proposal names are in its inputs, so naming them is not an invention."""
        r = standard(Repo())
        r.write("proposal.json", PROPOSAL)
        r.render()
        self.assertEqual(r.edge().returncode, 0)


class TestCoverageEdge(unittest.TestCase):
    def test_a_faithful_brief_passes(self):
        r = standard(Repo())
        r.render()
        self.assertEqual(r.edge().returncode, 0)

    def test_a_dropped_story_fails_the_edge(self):
        r = standard(Repo())
        r.render()
        p = r.item_dir / "summary.md"
        p.write_text("\n".join(l for l in p.read_text().split("\n") if not l.startswith("- S2:")))
        out = r.edge()
        self.assertEqual(out.returncode, 2)
        self.assertIn("S2 is in breakdown.json but not in the brief", out.stderr)

    def test_an_invented_identifier_fails_the_edge(self):
        r = standard(Repo())
        r.render()
        p = r.item_dir / "summary.md"
        p.write_text(p.read_text() + "\nAlso touches RetryPolicy.scala.\n")
        out = r.edge()
        self.assertEqual(out.returncode, 2)
        self.assertIn("RetryPolicy.scala", out.stderr)

    def test_an_omitted_finding_fails_the_edge(self):
        r = standard(Repo())
        r.render()
        p = r.item_dir / "summary.md"
        p.write_text(p.read_text().replace("No story covers idempotent redelivery.", "All good."))
        out = r.edge()
        self.assertEqual(out.returncode, 2)
        self.assertIn("a finding the verdict requires is not carried", out.stderr)

    def test_a_missing_verdict_fails_the_edge(self):
        r = standard(Repo())
        r.render()
        p = r.item_dir / "summary.md"
        p.write_text(p.read_text().replace("WEAKENED", "fine"))
        out = r.edge()
        self.assertEqual(out.returncode, 2)
        self.assertIn("verdict WEAKENED is not stated", out.stderr)

    def test_a_missing_section_fails_the_edge(self):
        r = standard(Repo())
        r.render()
        p = r.item_dir / "summary.md"
        p.write_text(p.read_text().replace(f"## {brief.SECTIONS[5]}", "## Something else"))
        out = r.edge()
        self.assertEqual(out.returncode, 2)
        self.assertIn("is missing", out.stderr)

    def test_a_survived_verdicts_findings_are_not_required(self):
        r = standard(Repo())
        r.write("challenge-breakdown.json", {**WEAKENED, "verdict": "SURVIVED"})
        r.render()
        self.assertEqual(r.edge().returncode, 0)


class TestReadabilityIsMeasuredNotGated(unittest.TestCase):
    def test_the_metrics_reach_the_trace(self):
        r = standard(Repo())
        r.render()
        r.edge()
        rec = [t for t in r.trace() if t.get("artifact") == "summary.md"][-1]
        self.assertIn("flesch_kincaid_grade", rec["metrics"])
        self.assertIn("gunning_fog", rec["metrics"])
        self.assertIn("readability", rec["edge"]["name"])

    def test_inherited_prose_above_the_target_grade_still_passes(self):
        """The renderer cannot rewrite what the breakdown node wrote, so it is not failed for it."""
        dense = {"item": "BRF-1", "epics": [{"id": "E1", "title": "Backoff", "stories": [
            {"id": "S1", "domains": ["backend"],
             "statement": ("Implement a configurable, instrumentation-compatible exponential "
                           "backoff coordination subsystem whose retry-scheduling "
                           "characteristics accommodate heterogeneous downstream "
                           "availability expectations notwithstanding intermittent "
                           "infrastructure degradation"),
             "acceptance_criteria": [{"id": "AC1", "given": "a timeout", "when": "it retries",
                                      "then": "delays grow to a cap"}]}]}]}
        r = standard(Repo())
        r.write("breakdown.json", dense)
        r.render()
        self.assertEqual(r.edge().returncode, 0)
        rec = [t for t in r.trace() if t.get("artifact") == "summary.md"][-1]
        self.assertGreater(rec["metrics"]["flesch_kincaid_grade"], 12)


class TestIdentifierRule(unittest.TestCase):
    """The no-invention check has to be narrow enough not to flag ordinary prose."""

    def test_ordinary_words_are_not_identifiers(self):
        self.assertEqual(brief.identifiers("The consumer retries. It is fine, e.g. mostly."), set())

    def test_files_and_ids_are_identifiers(self):
        found = brief.identifiers("See RetryPolicy.scala for S1 and AC2 and E1.")
        self.assertEqual(found, {"RetryPolicy.scala", "S1", "AC2", "E1"})

    def test_a_sentence_ending_before_a_known_suffix_is_not_a_file(self):
        self.assertEqual(brief.identifiers("Retries are capped.Then it stops."), set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
