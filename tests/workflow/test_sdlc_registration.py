#!/usr/bin/env python3
"""The SDLC pipeline registered as segments (tasks 4.1-4.4).

This is the second workflow, and the point of the substrate. The strongest evidence that
sections 1-2 did their job is not in this file: it is that all 532 tests in
`tests/delivery-flow` passed unaltered the first time a second descriptor existed. These tests
pin the declaration itself.

What matters most here is **4.3: declaring the pipeline must not make it runnable.** Every
node is `certified: false`, and `check-certification.py` blocks delegation to an uncertified
step. A registry that declared six segments and let an orchestrator drive them would be worse
than no registry — it would read as evidence of a pipeline that has none.

Run: python3 tests/workflow/test_sdlc_registration.py
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
import common  # noqa: E402
import descriptor as D  # noqa: E402

SDLC = ROOT / "skills" / "sdlc-orchestration" / "workflow.yaml"
REGISTRY = ROOT / "skills" / "sdlc-orchestration" / "steps.yaml"
PROFILES = ROOT / "templates" / "sdlc" / "profiles.yaml"

EXPECTED_SEGMENTS = ["analysis", "planning", "solutioning", "readiness",
                     "implementation", "verification"]


def certification():
    spec = importlib.util.spec_from_file_location(
        "check_certification", ROOT / "scripts" / "delivery-flow" / "check-certification.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTheDescriptorParsesWithTheSharedParser(unittest.TestCase):
    """4.2. If this needed a parser change, the generalisation was not real.

    The substrate would have been shaped around delivery-flow and the second workflow would
    have been the thing that revealed it — which is exactly what a second workflow is for.
    """

    def setUp(self):
        self.doc = D.load(SDLC)

    def test_it_loads_at_all(self):
        self.assertEqual(self.doc["workflow"], "sdlc")

    def test_its_pointers_exist(self):
        for key in ("schemas", "registry", "profiles"):
            self.assertTrue((ROOT / self.doc[key]).exists(),
                            f"{key} points at {self.doc[key]}, which is absent")

    def test_the_six_segments_are_declared_in_order(self):
        self.assertEqual([s["step"] for s in self.doc["steps"]], EXPECTED_SEGMENTS)

    def test_every_segment_is_a_segment(self):
        for s in self.doc["steps"]:
            self.assertEqual(s["kind"], "segment", s["step"])

    def test_every_segment_names_its_nodes_and_terminus(self):
        for s in self.doc["steps"]:
            with self.subTest(segment=s["step"]):
                self.assertTrue(s.get("nodes"), "no nodes")
                self.assertTrue(s.get("terminus"), "no terminus")
                self.assertEqual(s["terminus"], s["nodes"][-1],
                                 "the terminus must be the last node (design D1)")

    def test_every_segment_declares_its_handoff(self):
        for s in self.doc["steps"]:
            self.assertIn(s.get("handoff"), ("data", "prose"), s["step"])

    def test_the_handoff_artifact_has_a_schema_where_it_is_data(self):
        """D1: an intra-pipeline hand-off is schema-backed, or a human reads it.

        A `data` hand-off with no schema is a join nothing checks — the inert-edge shape. This
        is allowed to fail while the pipeline is being built, so it reports which segments are
        not yet checkable rather than only that some are not.
        """
        schemas = common.load_schemas()
        unchecked = [s["step"] for s in self.doc["steps"]
                     if s.get("handoff") == "data"
                     and common.schema_for(s["artifact"], schemas) is None]
        self.assertEqual(
            unchecked, ["analysis", "planning", "solutioning", "implementation"],
            "the set of segments whose hand-off has no schema has changed; "
            "readiness and verification are the two that do")


class TestTheRegistry(unittest.TestCase):
    """4.1. Every node the segments name must exist in the registry, and vice versa."""

    def setUp(self):
        self.doc = D.load(SDLC)
        self.registry = certification().parse_registry(REGISTRY.read_text())
        self.steps = {s["step"]: s for s in self.registry.get("steps", [])}

    def test_every_node_named_by_a_segment_is_in_the_registry(self):
        for seg in self.doc["steps"]:
            for node in seg["nodes"]:
                with self.subTest(segment=seg["step"], node=node):
                    self.assertIn(node, self.steps)

    def test_no_registry_step_is_orphaned(self):
        claimed = {n for seg in self.doc["steps"] for n in seg["nodes"]}
        self.assertEqual(set(self.steps) - claimed, set(),
                         "a registry step belongs to no segment")

    def test_every_step_names_the_segment_it_belongs_to(self):
        by_segment = {seg["step"]: seg["nodes"] for seg in self.doc["steps"]}
        for name, step in self.steps.items():
            with self.subTest(step=name):
                self.assertIn(name, by_segment.get(step["segment"], []),
                              f"{name} says segment={step['segment']} which does not claim it")

    def test_every_prompt_path_exists(self):
        """A registry naming a prompt that is not on disk certifies nothing."""
        for name, step in self.steps.items():
            with self.subTest(step=name):
                self.assertTrue((ROOT / step["prompt"]).is_file(), step["prompt"])

    def test_every_agent_exists(self):
        for name, step in self.steps.items():
            with self.subTest(step=name):
                self.assertTrue((ROOT / "agents" / f"{step['agent']}.md").is_file(),
                                step["agent"])


class TestNothingIsCertified(unittest.TestCase):
    """4.3. Declaring the pipeline must not make it runnable."""

    def setUp(self):
        self.registry = certification().parse_registry(REGISTRY.read_text())
        self.steps = {s["step"]: s for s in self.registry.get("steps", [])}

    def test_every_step_is_marked_uncertified(self):
        for name, step in self.steps.items():
            with self.subTest(step=name):
                self.assertIs(step.get("certified"), False)

    def test_no_step_claims_evidence_it_does_not_have(self):
        """The fields that would make a step look certified must be absent.

        A `prompt_sha256` with no `results` behind it is the shape of a step that looks
        examined and is not.
        """
        for name, step in self.steps.items():
            with self.subTest(step=name):
                for field in ("prompt_sha256", "results", "consecutive_runs",
                              "certified_version"):
                    self.assertNotIn(field, step, f"{name} claims {field}")

    def test_every_step_states_its_residual(self):
        for name, step in self.steps.items():
            self.assertTrue(step.get("known_residual"), name)


class TestProfiles(unittest.TestCase):
    """4.4. A run can be scoped to readiness alone and stop at its terminus."""

    def setUp(self):
        self.doc = D.load(SDLC)
        self.profiles = common.load_profiles(PROFILES)
        self.by_name = {p["profile"]: p for p in self.profiles}
        self.table = [s["step"] for s in self.doc["steps"]]

    def test_readiness_can_be_run_alone(self):
        p = self.by_name["readiness"]
        self.assertEqual(p["steps"], ["readiness"])
        self.assertEqual(p["terminus"], "readiness")

    def test_every_profile_step_is_in_the_routing_table(self):
        for name, p in self.by_name.items():
            for step in p["steps"]:
                with self.subTest(profile=name, step=step):
                    self.assertIn(step, self.table)

    def test_no_segment_is_orphaned(self):
        covered = {s for p in self.profiles for s in p["steps"]}
        self.assertEqual(set(self.table) - covered, set())

    def test_the_terminus_is_the_last_step(self):
        for name, p in self.by_name.items():
            with self.subTest(profile=name):
                self.assertEqual(p["terminus"], p["steps"][-1])

    def test_next_names_a_profile_or_nothing(self):
        for name, p in self.by_name.items():
            with self.subTest(profile=name):
                nxt = p.get("next")
                if nxt is not None:
                    self.assertIn(nxt, self.by_name)

    def test_full_is_the_whole_table(self):
        self.assertEqual(self.by_name["full"]["steps"], self.table)


class TestTheReadinessVerdictSchema(unittest.TestCase):
    """4.6, and the design error it nearly shipped with."""

    def setUp(self):
        self.schema = common.schema_for("readiness-verdict.json", common.load_schemas())

    def test_it_resolves(self):
        self.assertIsNotNone(self.schema)

    def test_the_three_verdicts_are_the_fixed_set(self):
        self.assertEqual(self.schema["properties"]["verdict"]["enum"],
                         ["REFUTED", "WEAKENED", "SURVIVED"])

    def test_it_does_not_let_the_node_report_the_deterministic_gates(self):
        """The first draft had a `gates` field recording lint-story and openspec results.

        That is a node self-reporting that a deterministic check passed, which designs D4 and
        D5 put on the *edge*. The reviewer's artifact carries its judgement; whether the gates
        ran is the trace's business, and a node cannot be the witness for its own guardrail.
        """
        self.assertNotIn("gates", self.schema["properties"])

    def test_attacks_have_a_floor(self):
        """A verdict reached without attacking anything is not a review."""
        self.assertGreaterEqual(self.schema["properties"]["attacks"]["minItems"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
