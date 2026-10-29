#!/usr/bin/env python3
"""Tests for the breakdown→story seam.

The renderer's whole value is that it adds nothing, so these assert exact equality rather than
a pass rate: every story, criterion and domain comes from the breakdown unchanged, and the two
directions of drift — an invented story and a dropped one — are both checked. The dropped
direction matters more: an invented story is visible, a dropped one is silence, and the
`breakdown` node's known residual is exactly a dropped requirement.

Run: python3 tests/delivery-flow/test_stories.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
RENDER = SCRIPTS / "render-stories.py"
sys.path.insert(0, str(SCRIPTS))

from common import load_schemas, schema_for  # noqa: E402
from stories import invented, missing_from, stories_from, story_filename  # noqa: E402

_spec = importlib.util.spec_from_file_location("validate_artifact", SCRIPTS / "validate-artifact.py")
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

BREAKDOWN = {
    "item": "AN-1",
    "epics": [
        {"id": "E1", "title": "Cleanup on exit", "stories": [
            {"id": "S1", "statement": "Context manager cleans up on normal exit",
             "domains": ["backend"], "acceptance_criteria": [
                 {"id": "AC1", "given": "a running graph", "when": "the block ends",
                  "then": "the graph is destroyed"},
                 {"id": "AC2", "given": "a session", "when": "the block is entered",
                  "then": "the session is yielded"}]},
            {"id": "S2", "statement": "Cleanup on an exception",
             "domains": ["backend"], "acceptance_criteria": [
                 {"id": "AC3", "given": "a running graph", "when": "an exception is raised",
                  "then": "the graph is destroyed before the exception leaves"}]}]},
        {"id": "E2", "title": "Idempotence", "stories": [
            {"id": "S3", "statement": "No double cleanup",
             "domains": ["backend", "infra"], "acceptance_criteria": [
                 {"id": "AC4", "given": "an already-cleaned session", "when": "it is collected",
                  "then": "no second request is issued"}]}]},
    ],
}

CHALLENGE = {"item": "AN-1", "target": "breakdown.json", "verdict": "SURVIVED",
             "attacks": [{"attack": "a", "method": "m", "result": "failed"},
                         {"attack": "b", "method": "m", "result": "failed"},
                         {"attack": "c", "method": "m", "result": "failed"}],
             "findings": []}


class Repo:
    def __init__(self, challenge=CHALLENGE, breakdown=BREAKDOWN):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / ".git").mkdir()
        (self.dir / ".delivery-flow.yaml").write_text("tracker:\n  kind: jira\nprofile: full\n")
        self.item = "AN-1"
        self.item_dir = self.dir / "delivery" / self.item
        self.item_dir.mkdir(parents=True)
        (self.item_dir / "item.json").write_text(json.dumps({"key": "AN-1"}))
        (self.item_dir / "breakdown.json").write_text(json.dumps(breakdown))
        if challenge is not None:
            (self.item_dir / "challenge-breakdown.json").write_text(json.dumps(challenge))

    def render(self, *args):
        return subprocess.run([sys.executable, str(RENDER), self.item, "--repo", str(self.dir),
                               *args], capture_output=True, text=True)

    def stories(self):
        return [json.loads(p.read_text()) for p in sorted(self.item_dir.glob("story-*.json"))]


class TestMapping(unittest.TestCase):
    def test_every_breakdown_story_becomes_exactly_one_story(self):
        r = Repo()
        self.assertEqual(r.render().returncode, 0)
        self.assertEqual(len(r.stories()), 3)

    def test_ids_and_criteria_are_carried_across_unchanged(self):
        r = Repo()
        r.render()
        by_id = {(s["epic"], s["story"]): s for s in r.stories()}
        self.assertEqual(sorted(by_id), [("E1", "S1"), ("E1", "S2"), ("E2", "S3")])
        s1 = by_id[("E1", "S1")]
        self.assertEqual([a["id"] for a in s1["acceptance_criteria"]], ["AC1", "AC2"])
        self.assertEqual(s1["acceptance_criteria"][0]["then"], "the graph is destroyed")
        self.assertEqual(s1["statement"], "Context manager cleans up on normal exit")
        self.assertEqual(by_id[("E2", "S3")]["domains"], ["backend", "infra"])

    def test_a_story_satisfies_the_implementers_contract(self):
        r = Repo()
        r.render()
        schemas = load_schemas()
        for story in r.stories():
            # Resolved from the real file name, not the schema key: a rendered story is
            # `story-E1-S1.json`, and an exact-name lookup used to return None for every one
            # of them — the schema existed and nothing could find it.
            name = story_filename(story["epic"], story["story"])
            schema = schema_for(name, schemas)
            self.assertIsNotNone(schema, f"no schema resolved for {name}")
            problems = []
            validator.validate(story, schema, "", problems)
            problems += validator.consumer_problems(story, schema, "implementer")
            self.assertEqual(problems, [], story.get("story"))

    def test_the_test_writers_contract_is_satisfied_too(self):
        """Both halves of the dev pair are declared consumers, so both are checked."""
        r = Repo()
        r.render()
        schemas = load_schemas()
        for story in r.stories():
            schema = schema_for(story_filename(story["epic"], story["story"]), schemas)
            self.assertEqual(validator.consumer_problems(story, schema, "test-writer"), [],
                             story.get("story"))

    def test_sources_point_at_the_artifacts_rather_than_summarising_them(self):
        r = Repo()
        r.render()
        for story in r.stories():
            self.assertIn("breakdown.json", story["sources"])
            self.assertIn("challenge-breakdown.json", story["sources"])
            self.assertIn("item.json", story["sources"])

    def test_a_change_directory_joins_the_sources_when_given(self):
        r = Repo()
        r.render("--change", "openspec/changes/add-thing")
        self.assertIn("openspec/changes/add-thing", r.stories()[0]["sources"])

    def test_ordering_is_recorded_as_undetermined(self):
        r = Repo()
        r.render()
        positions = sorted(s["ordering"]["position"] for s in r.stories())
        self.assertEqual(positions, [1, 2, 3])
        for story in r.stories():
            self.assertFalse(story["ordering"]["determined"])
            self.assertIn("undetermined", story["ordering"]["basis"])

    def test_reruns_are_byte_identical(self):
        r = Repo()
        first = r.render("--stdout").stdout
        second = r.render("--stdout").stdout
        self.assertEqual(first, second)


class TestItAddsNothing(unittest.TestCase):
    def test_an_invented_criterion_is_detected(self):
        stories = stories_from(BREAKDOWN, ["breakdown.json"])
        stories[0]["acceptance_criteria"].append(
            {"id": "AC9", "given": "g", "when": "w", "then": "an outcome nobody asked for"})
        self.assertTrue(any("AC9" in p for p in invented(stories[0], BREAKDOWN)))

    def test_an_invented_domain_is_detected(self):
        stories = stories_from(BREAKDOWN, ["breakdown.json"])
        stories[0]["domains"].append("ux")
        self.assertTrue(any("ux" in p for p in invented(stories[0], BREAKDOWN)))

    def test_a_rewritten_statement_is_detected(self):
        stories = stories_from(BREAKDOWN, ["breakdown.json"])
        stories[0]["statement"] = "something the breakdown never said"
        self.assertTrue(any("statement" in p for p in invented(stories[0], BREAKDOWN)))

    def test_a_faithful_story_invents_nothing(self):
        for story in stories_from(BREAKDOWN, ["breakdown.json"]):
            self.assertEqual(invented(story, BREAKDOWN), [], story["story"])

    def test_a_dropped_story_is_detected(self):
        """The direction that matters: an invented story is visible, a dropped one is silence."""
        stories = stories_from(BREAKDOWN, ["breakdown.json"])
        kept = [s for s in stories if s["story"] != "S3"]
        self.assertTrue(any("S3" in p for p in missing_from(kept, BREAKDOWN)))
        self.assertEqual(missing_from(stories, BREAKDOWN), [])


class TestRefusals(unittest.TestCase):
    def test_it_refuses_an_unchallenged_breakdown(self):
        r = Repo(challenge=None)
        out = r.render()
        self.assertEqual(out.returncode, 1)
        self.assertIn("not been challenged", out.stderr)
        self.assertEqual(r.stories(), [])

    def test_it_refuses_a_refuted_breakdown(self):
        r = Repo(challenge={**CHALLENGE, "verdict": "REFUTED",
                            "findings": [{"finding": "the idempotency clause reaches no story",
                                          "evidence": "absent from all criteria"}]})
        out = r.render()
        self.assertEqual(out.returncode, 1)
        self.assertIn("REFUTED", out.stderr)
        self.assertIn("idempotency", out.stderr)
        self.assertEqual(r.stories(), [])

    def test_it_renders_a_weakened_breakdown_and_says_so(self):
        """WEAKENED means the plan stands and its findings are fixed in place."""
        r = Repo(challenge={**CHALLENGE, "verdict": "WEAKENED",
                            "findings": [{"finding": "AC2 asserts little", "evidence": "e"}]})
        out = r.render()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(len(r.stories()), 3)
        self.assertIn("WEAKENED", out.stdout)

    def test_a_quick_path_item_has_nothing_to_render(self):
        r = Repo()
        (r.item_dir / "breakdown.json").unlink()
        out = r.render()
        self.assertEqual(out.returncode, 2)
        self.assertIn("quick-path", out.stderr)

    def test_an_empty_breakdown_is_a_usage_error_not_an_empty_story_set(self):
        r = Repo(breakdown={"item": "AN-1", "epics": []})
        out = r.render()
        self.assertEqual(out.returncode, 2)
        self.assertEqual(r.stories(), [])

    def test_dry_run_writes_nothing(self):
        r = Repo()
        out = r.render("--dry-run")
        self.assertEqual(out.returncode, 0)
        self.assertEqual(r.stories(), [])
        self.assertIn("would write", out.stdout)


class TestSchemaResolution(unittest.TestCase):
    """`schema_for` must resolve a *set* of artifacts, not just fixed file names.

    Lives here because rendered stories are why the glob fallback exists: they are named
    `story-<epic>-<story>.json`, one per breakdown story, so no exact key could ever match and
    every rendered story went unvalidated — by `validate-artifact.py` and by the edge hook,
    which skipped them before they reached its checker.
    """

    def setUp(self):
        self.schemas = load_schemas()

    def test_a_rendered_story_resolves_to_the_story_schema(self):
        for name in ("story-E1-S1.json", "story-E12-S345.json"):
            schema = schema_for(name, self.schemas)
            self.assertIsNotNone(schema, name)
            self.assertEqual(schema["artifact"], "story-*.json")

    def test_the_sentinel_glob_still_resolves(self):
        schema = schema_for("breakdown.json.sentinel.json", self.schemas)
        self.assertIsNotNone(schema)
        self.assertEqual(schema["artifact"], "*.sentinel.json")

    def test_an_exact_name_beats_a_glob(self):
        self.assertEqual(schema_for("breakdown.json", self.schemas)["artifact"], "breakdown.json")

    def test_an_ungoverned_name_resolves_to_nothing(self):
        """The hook relies on None to stay inert: a stray file must not be governed."""
        for name in ("notes.json", "story.json", "story-.json.bak", "summary.md"):
            self.assertIsNone(schema_for(name, self.schemas), name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
