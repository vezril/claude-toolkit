#!/usr/bin/env python3
"""The workflow docs track the descriptor, not a memory of it (section 8).

`CLAUDE.md` says a change to the workflow is incomplete until the docs change with it, and the
pipeline's own rule is "artifacts drive state" — which stale docs break. That rule was prose,
and prose is exactly what nobody re-reads. These tests read the descriptor and the registry and
require the docs to agree with them.

What is deliberately *not* tested: whether the prose is any good. These check the facts a reader
would act on — segment names, which segment is certified, that every referenced figure exists,
and that the model-policy correction actually landed everywhere it was wrong.

Run: python3 tests/workflow/test_documentation_mirrors.py
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
import descriptor as D  # noqa: E402

SDLC = ROOT / "skills" / "sdlc-orchestration" / "workflow.yaml"
PLAYBOOK = ROOT / "docs" / "using-the-sdlc-dev-team.md"
SKILL = ROOT / "skills" / "sdlc-orchestration" / "SKILL.md"
AGENTS_README = ROOT / "agents" / "README.md"
ORCHESTRATOR = ROOT / "agents" / "sdlc-orchestrator.md"
PRIME = ROOT / "skills" / "prime" / "SKILL.md"
CERTIFICATION = ROOT / "skills" / "workflow-certification" / "SKILL.md"
EVALS_README = ROOT / "evals" / "README.md"

MIRRORS = {
    "docs/using-the-sdlc-dev-team.md": PLAYBOOK,
    "skills/sdlc-orchestration/SKILL.md": SKILL,
    "agents/README.md": AGENTS_README,
    "agents/sdlc-orchestrator.md": ORCHESTRATOR,
    "skills/prime/SKILL.md": PRIME,
}


def _certified_steps() -> dict:
    """step -> certified flag, from the registry, via check-certification's own parser."""
    spec = importlib.util.spec_from_file_location(
        "check_certification_for_docs",
        ROOT / "scripts" / "delivery-flow" / "check-certification.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    registry = D.load(SDLC)["registry"]
    entries = mod.parse_registry((D.PLUGIN_ROOT / registry).read_text()).get("steps") or []
    return {e["step"]: bool(e.get("certified")) for e in entries}


class TestThePlaybookNamesTheRealSegments(unittest.TestCase):
    """8.1 — the segment table is the descriptor's, or a reader is working from fiction."""

    def setUp(self):
        self.doc = D.load(SDLC)
        self.segments = [s["step"] for s in self.doc["steps"] if s.get("kind") == "segment"]
        self.text = PLAYBOOK.read_text()

    def test_there_are_six_segments_to_document(self):
        self.assertEqual(6, len(self.segments), self.segments)

    def test_every_segment_is_named_in_the_playbook(self):
        for seg in self.segments:
            with self.subTest(segment=seg):
                self.assertIn(f"`{seg}`", self.text)

    def test_every_node_is_named_in_the_playbook(self):
        """The nodes, not just the segments: the trace records node names."""
        for step in self.doc["steps"]:
            for node in step.get("nodes") or []:
                with self.subTest(node=node):
                    self.assertIn(node, self.text)

    def test_every_hand_off_artifact_is_named(self):
        for step in self.doc["steps"]:
            with self.subTest(artifact=step["artifact"]):
                self.assertIn(step["artifact"], self.text)


class TestTheCertificationStateIsNotOverstated(unittest.TestCase):
    """The one claim a reader could act on wrongly: what may run unattended."""

    def setUp(self):
        self.flags = _certified_steps()
        self.doc = D.load(SDLC)

    def test_readiness_is_the_only_certified_segment(self):
        """If this fails, a segment was certified and the docs below need updating with it."""
        certified = {s["step"] for s in self.doc["steps"]
                     if s.get("kind") == "segment"
                     and all(self.flags.get(n) for n in (s.get("nodes") or []))}
        self.assertEqual({"readiness"}, certified,
                         "the certified set changed — update the segment tables in "
                         f"{', '.join(MIRRORS)} and docs/figures/sdlc-pipeline.svg")

    def test_the_playbook_marks_each_segments_certification_state(self):
        """Per segment, not as one sentence — a reader checks the row for the segment at hand.

        The playbook's segment table carries a `Certified?` column; every uncertified segment
        must be marked `no` in it. Asserting on a summary sentence instead (my first version of
        this test) passes on a table whose rows all say `yes`.
        """
        text = PLAYBOOK.read_text()
        rows = {}
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip().strip("*` ") for c in line.strip("|").split("|")]
            if len(cells) == 4 and cells[3] in ("yes", "no"):
                rows[cells[0]] = cells[3]
        self.assertEqual(6, len(rows), f"the segment table did not parse: {rows}")
        for seg, flag in rows.items():
            with self.subTest(segment=seg):
                self.assertEqual("yes" if self.flags_for(seg) else "no", flag)

    def flags_for(self, segment: str) -> bool:
        nodes = next((s.get("nodes") or [] for s in self.doc["steps"]
                      if s.get("step") == segment), [])
        return bool(nodes) and all(self.flags.get(n) for n in nodes)

    def test_the_playbook_says_uncertified_blocks_unattended_not_everything(self):
        """The distinction a reader needs: uncertified is not disabled, just not unattended."""
        text = PLAYBOOK.read_text()
        self.assertIn("check-certification.py", text)
        self.assertIn("not a disabled segment", text)

    def test_the_figure_marks_readiness_as_the_certified_one(self):
        svg = (ROOT / "docs" / "figures" / "sdlc-pipeline.svg").read_text()
        self.assertIn("CERTIFIED", svg)
        self.assertEqual(1, svg.count("CERTIFIED"),
                         "more than one segment is badged certified in the figure")


class TestTheCompositionRuleIsRecordedAsUnconfirmed(unittest.TestCase):
    """8.6 — the claim is this project's reading, and saying so is the point."""

    def test_the_certification_skill_states_the_rule(self):
        text = CERTIFICATION.read_text()
        self.assertIn("intra-segment hand-off is", text)
        self.assertIn("punch-out", text)

    def test_it_says_no_reviewer_has_confirmed_it(self):
        """A rule recorded without its status reads as settled. It is not settled.

        Asserted against the *status line itself*, not against the word appearing anywhere in
        the file: the first version of this test searched the whole text, and the word also
        occurs in a passing mention further down, so deleting the actual status declaration
        left it green.
        """
        text = CERTIFICATION.read_text()
        self.assertRegex(text, r"Status of that claim:\s*\*{0,2}unconfirmed")
        self.assertIn("No reviewer has been asked", text)

    def test_the_playbook_repeats_the_caveat_where_the_claim_appears(self):
        """The convenient place to drop the caveat is the playbook. It stays."""
        text = PLAYBOOK.read_text().lower()
        self.assertIn("this project's reading", text)


class TestTheModelPolicyCorrectionLanded(unittest.TestCase):
    """8.4 — "separate, stronger model" was wrong in both halves (design D7)."""

    SOURCES = {
        **MIRRORS,
        "skills/requirements-engineering/SKILL.md":
            ROOT / "skills" / "requirements-engineering" / "SKILL.md",
        "skills/agentic-workflows/references/patterns-and-frameworks.md":
            ROOT / "skills" / "agentic-workflows" / "references"
            / "patterns-and-frameworks.md",
    }

    def test_no_file_still_instructs_a_stronger_model(self):
        """Allowed only where a file quotes the old wording to correct it."""
        pattern = re.compile(r"(stronger model|separate/stronger)", re.I)
        for name, path in self.SOURCES.items():
            for i, line in enumerate(path.read_text().splitlines(), 1):
                if not pattern.search(line):
                    continue
                with self.subTest(file=name, line=i):
                    self.assertTrue(
                        "used to" in line or "conflated" in line,
                        f"{name}:{i} still prescribes a stronger model for validation")

    def test_the_orchestrator_states_the_haiku_first_order(self):
        text = ORCHESTRATOR.read_text().lower()
        self.assertIn("haiku first", text)

    def test_the_skill_states_independence_is_the_mechanism(self):
        text = SKILL.read_text().lower()
        self.assertIn("fresh context", text)
        self.assertIn("refute", text)


class TestTheReadinessGateIsNotDescribedAsSelfInvoked(unittest.TestCase):
    """8.3 — the mirrors said the orchestrator runs the validators. It must not."""

    def test_the_declared_edge_check_exists_on_disk(self):
        checks = D.load(SDLC).get("edge_checks") or {}
        self.assertTrue(checks, "no edge_checks are declared")
        for artifact, rel in checks.items():
            with self.subTest(artifact=artifact):
                self.assertTrue((D.PLUGIN_ROOT / rel).is_file(), f"{rel} is not on disk")

    def test_each_mirror_attributes_the_gate_to_the_hook(self):
        for name, path in MIRRORS.items():
            if name == "skills/prime/SKILL.md":
                continue   # prime describes detection, not the gate's mechanism
            with self.subTest(file=name):
                self.assertIn("check-edge.py", path.read_text(),
                              f"{name} describes the readiness gate without naming the hook "
                              "that runs it")

    def test_the_skill_still_forbids_the_orchestrator_running_them(self):
        self.assertIn("do not run those gates yourself", SKILL.read_text())


class TestEveryReferencedFigureExists(unittest.TestCase):
    """A broken figure reference degrades silently to a missing image."""

    def test_the_playbook_references_resolve(self):
        text = PLAYBOOK.read_text()
        refs = re.findall(r"\]\((figures/[^)]+)\)", text)
        self.assertTrue(refs, "the playbook references no figures at all")
        for ref in refs:
            with self.subTest(figure=ref):
                self.assertTrue((PLAYBOOK.parent / ref).is_file(), f"{ref} is missing")

    def test_the_figures_are_well_formed_xml(self):
        import xml.etree.ElementTree as ET
        for svg in sorted((ROOT / "docs" / "figures").glob("*.svg")):
            with self.subTest(figure=svg.name):
                try:
                    ET.fromstring(svg.read_text())
                except ET.ParseError as e:
                    self.fail(f"{svg.name} is not well-formed: {e}")

    def test_the_changed_figures_describe_themselves(self):
        """`<desc>` is what a screen reader reads; an empty one is the figure missing."""
        for name in ("sdlc-pipeline.svg", "readiness-gate.svg", "human-gates.svg"):
            with self.subTest(figure=name):
                text = (ROOT / "docs" / "figures" / name).read_text()
                desc = re.search(r"<desc>(.*?)</desc>", text, re.S)
                self.assertIsNotNone(desc, f"{name} has no <desc>")
                self.assertGreater(len(desc.group(1).strip()), 120,
                                   f"{name}'s <desc> is too thin to replace the image")


class TestTheEvalsReadmeExplainsNodeSuites(unittest.TestCase):
    """8.5 — node suites are wired differently from skill suites."""

    def setUp(self):
        self.text = EVALS_README.read_text()

    def test_it_names_the_registry_as_the_binding(self):
        self.assertIn("steps.yaml", self.text)
        self.assertIn("prompt_sha256", self.text)

    def test_it_says_editing_a_prompt_uncertifies_the_step(self):
        """The consequence someone will otherwise discover by being blocked."""
        self.assertIn("un-certifies", self.text)

    def test_both_node_suites_it_names_are_on_disk(self):
        for suite in ("readiness-stories", "readiness-review"):
            with self.subTest(suite=suite):
                self.assertIn(f"evals/{suite}/", self.text)
                self.assertTrue((ROOT / "evals" / suite / "promptfooconfig.yaml").is_file())

    def test_the_required_artifacts_it_names_exist_in_those_suites(self):
        for suite in ("readiness-stories", "readiness-review"):
            for artifact in ("load-bearing.md", "iteration-log.md"):
                with self.subTest(suite=suite, artifact=artifact):
                    self.assertTrue((ROOT / "evals" / suite / artifact).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
