#!/usr/bin/env python3
"""Tests for derived punch-out triggers: the gate must not depend on the gated node's flags.

Run: python3 tests/delivery-flow/test_triggers.py
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
import triggers  # noqa: E402

CLEAN_ITEM = {"key": "T-1", "title": "Add a date range option",
              "body": "Callers want a date range. Acceptance: a range request is answered.",
              "labels": []}
CLEAN_TRIAGE = {"item": "T-1", "type": "feature", "path": "standard", "domains": ["backend"],
                "summary": "Add a date range option.", "rationale": "Callers asked.",
                "handoff": False, "handoff_reason": None,
                "architecture_change": False, "breaking_change": False}


def breakdown(epics=1, stories_per=1, domains=("backend",), text="Add a date range option"):
    return {"item": "T-1", "epics": [
        {"id": f"E{e}", "title": "Range option", "stories": [
            {"id": f"S{e}{s}", "statement": text, "domains": list(domains),
             "acceptance_criteria": [{"id": f"AC{e}{s}", "given": "a request",
                                      "when": "it arrives", "then": "it is answered"}]}
            for s in range(stories_per)]}
        for e in range(1, epics + 1)]}


class TestTheGateDoesNotDependOnTheFlags(unittest.TestCase):
    def test_a_suppressed_flag_does_not_skip_the_gate(self):
        item = {**CLEAN_ITEM, "body": "This is a breaking change for callers. Acceptance: ok."}
        got = triggers.combine(item, CLEAN_TRIAGE, breakdown(), {})
        self.assertTrue(got["breaking"]["fired"])
        self.assertEqual(got["breaking"]["source"], "derivation")

    def test_a_node_asking_for_a_human_is_never_overruled(self):
        triage = {**CLEAN_TRIAGE, "handoff": True}
        got = triggers.combine(CLEAN_ITEM, triage, breakdown(), {})
        self.assertTrue(got["scope"]["fired"])
        self.assertEqual(got["scope"]["source"], "claim")

    def test_agreement_is_marked_as_both(self):
        item = {**CLEAN_ITEM, "body": "A breaking change. Acceptance: ok."}
        triage = {**CLEAN_TRIAGE, "breaking_change": True}
        got = triggers.combine(item, triage, breakdown(), {})
        self.assertEqual(got["breaking"]["source"], "both")
        self.assertFalse(got["breaking"]["disagreement"])

    def test_nothing_fires_on_a_clean_routine_item(self):
        got = triggers.combine(CLEAN_ITEM, CLEAN_TRIAGE, breakdown(), {})
        self.assertEqual([t for t, v in got.items() if v["fired"]], [])


class TestDerivations(unittest.TestCase):
    def test_architecture_fires_on_the_vocabulary_of_moving_a_boundary(self):
        for phrase in ("we must migrate the ledger", "extract a service for this",
                       "a new service is needed", "this crosses a boundary",
                       "a schema migration is required"):
            item = {**CLEAN_ITEM, "body": f"{phrase}. Acceptance: ok."}
            got = triggers.derive(item, CLEAN_TRIAGE, None, {})
            self.assertTrue(got["architecture"]["fired"], phrase)

    def test_breaking_fires_on_the_vocabulary_of_breaking_callers(self):
        for phrase in ("remove the endpoint", "rename the column", "drop the table",
                       "this is backward incompatible", "bump the major version"):
            item = {**CLEAN_ITEM, "body": f"{phrase}. Acceptance: ok."}
            got = triggers.derive(item, CLEAN_TRIAGE, None, {})
            self.assertTrue(got["breaking"]["fired"], phrase)

    def test_architecture_fires_on_breadth_of_domains(self):
        got = triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE,
                              breakdown(epics=3, domains=("backend",)), {})
        self.assertFalse(got["architecture"]["fired"])
        wide = {"item": "T-1", "epics": [
            {"id": "E1", "title": "t", "stories": [
                {"id": f"S{i}", "statement": "s", "domains": [d],
                 "acceptance_criteria": [{"id": "AC1", "given": "g", "when": "w", "then": "t"}]}
                for i, d in enumerate(["backend", "frontend", "infra"])]}]}
        got = triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE, wide, {})
        self.assertTrue(got["architecture"]["fired"])
        self.assertIn("spans 3 domains", got["architecture"]["evidence"])

    def test_scope_fires_over_the_epic_ceiling(self):
        got = triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE, breakdown(epics=9), {})
        self.assertTrue(got["scope"]["fired"])
        self.assertIn("over the ceiling", got["scope"]["evidence"])

    def test_scope_fires_when_the_item_states_no_expected_outcome(self):
        got = triggers.derive({**CLEAN_ITEM, "body": "it is broken"}, CLEAN_TRIAGE, None, {})
        self.assertTrue(got["scope"]["fired"])
        self.assertIn("states no expected outcome", got["scope"]["evidence"])

    def test_the_acceptance_signal_derivation_can_be_switched_off(self):
        terse = {**CLEAN_ITEM, "body": "it is broken"}
        cfg = {"punch_out": {"require_acceptance_signal": False}}
        self.assertFalse(triggers.derive(terse, CLEAN_TRIAGE, None, cfg)["scope"]["fired"])

    def test_a_contract_path_named_in_the_text_fires_both_boundary_triggers(self):
        cfg = {"punch_out": {"contract_paths": ["the-lexicon"]}}
        item = {**CLEAN_ITEM, "body": "Update the-lexicon for this. Acceptance: ok."}
        got = triggers.derive(item, CLEAN_TRIAGE, None, cfg)
        self.assertTrue(got["architecture"]["fired"])
        self.assertTrue(got["breaking"]["fired"])

    def test_derivations_read_the_acceptance_criteria_too(self):
        """Laundering the statements is not enough if the criteria still say it."""
        b = {"item": "T-1", "epics": [{"id": "E1", "title": "Range", "stories": [
            {"id": "S1", "statement": "Add an option", "domains": ["backend"],
             "acceptance_criteria": [{"id": "AC1", "given": "a request", "when": "it arrives",
                                      "then": "the ledger answers from the new boundary"}]}]}]}
        got = triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE, b, {})
        self.assertTrue(got["architecture"]["fired"])

    def test_ceilings_come_from_config(self):
        cfg = {"punch_out": {"epic_ceiling": 2, "domain_ceiling": 1}}
        self.assertTrue(triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE, breakdown(epics=3), cfg)["scope"]["fired"])
        self.assertFalse(triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE, breakdown(epics=3), {})["scope"]["fired"])

    def test_a_junk_ceiling_falls_back_to_the_default(self):
        cfg = {"punch_out": {"epic_ceiling": "lots"}}
        self.assertEqual(triggers.ceilings(cfg)["epics"], triggers.DEFAULT_EPIC_CEILING)


class TestUndeterminedIsNotFalse(unittest.TestCase):
    def test_counts_are_undetermined_before_the_breakdown_exists(self):
        got = triggers.derive(CLEAN_ITEM, CLEAN_TRIAGE, None, {})
        self.assertIs(got["scope"]["fired"], False)  # the text derivation is determinable
        self.assertNotIn("ceiling", got["scope"]["evidence"])

    def test_scope_is_undetermined_without_the_item(self):
        got = triggers.derive(None, CLEAN_TRIAGE, None, {})
        self.assertIsNone(got["scope"]["fired"])

    def test_an_undetermined_derivation_is_not_a_disagreement(self):
        triage = {**CLEAN_TRIAGE, "handoff": True}
        got = triggers.combine(None, triage, None, {})
        self.assertFalse(got["scope"]["disagreement"])
        self.assertTrue(got["scope"]["fired"])

    def test_claims_are_none_without_triage(self):
        self.assertEqual(set(triggers.claimed(None).values()), {None})


class TestDisagreement(unittest.TestCase):
    def test_a_contradicted_claim_is_recorded(self):
        item = {**CLEAN_ITEM, "body": "This is a breaking change. Acceptance: ok."}
        got = triggers.disagreements(item, CLEAN_TRIAGE, breakdown(), {})
        self.assertEqual([d["trigger"] for d in got], ["breaking"])
        self.assertEqual(got[0]["claimed"], False)
        self.assertEqual(got[0]["derived"], True)
        self.assertIn("breaking change", got[0]["evidence"])

    def test_agreement_records_nothing(self):
        self.assertEqual(triggers.disagreements(CLEAN_ITEM, CLEAN_TRIAGE, breakdown(), {}), [])

    def test_a_claim_the_derivation_cannot_see_is_a_disagreement_only_when_determinable(self):
        """handoff: true with a clean item is a disagreement; the node saw something we cannot."""
        triage = {**CLEAN_TRIAGE, "handoff": True}
        got = triggers.disagreements(CLEAN_ITEM, triage, breakdown(), {})
        self.assertEqual([d["trigger"] for d in got], ["scope"])


def proposal(tasks=2, files=None, deps=(), **flags):
    files = files or ["src/a.scala", "src/b.scala"]
    doc = {"item": "T-1", "change_id": "add-thing", "change_path": "openspec/changes/add-thing",
           "specs_touched": ["s"], "dependencies_added": list(deps),
           "scope": False, "architecture": False, "breaking": False,
           "tasks": [{"id": f"T{i}", "description": "d", "files": [files[i % len(files)]]}
                     for i in range(1, tasks + 1)]}
    doc.update(flags)
    return doc


POLICY = {"punch_out": {"contract_paths": ["the-lexicon"], "protected_paths": [".github", "charts"]}}


class TestProposalDerivations(unittest.TestCase):
    def test_a_small_routine_change_fires_nothing(self):
        got = triggers.combine_proposal(proposal(), POLICY)
        self.assertEqual([t for t, v in got.items() if v["fired"]], [])

    def test_a_protected_path_in_the_plan_fires(self):
        got = triggers.combine_proposal(
            proposal(files=["src/a.scala", ".github/workflows/ci.yml"]), POLICY)
        self.assertTrue(got["protected-path"]["fired"])
        self.assertEqual(got["protected-path"]["source"], "derivation")
        self.assertIn(".github", got["protected-path"]["evidence"])

    def test_a_contract_path_fires_breaking(self):
        got = triggers.combine_proposal(
            proposal(files=["the-lexicon/orders.json", "src/b.scala"]), POLICY)
        self.assertTrue(got["proposal-breaking"]["fired"])

    def test_rewording_cannot_evade_a_path_derivation(self):
        """No prose anywhere in the derivation: it is a path match."""
        doc = proposal(files=["the-lexicon/orders.json"])
        for t in doc["tasks"]:
            t["description"] = "a small, routine, entirely safe tidy-up"
        self.assertTrue(triggers.combine_proposal(doc, POLICY)["proposal-breaking"]["fired"])

    def test_a_dependency_addition_fires(self):
        got = triggers.combine_proposal(proposal(deps=["cats-effect"]), POLICY)
        self.assertTrue(got["new-dependency"]["fired"])
        self.assertIn("cats-effect", got["new-dependency"]["evidence"])

    def test_the_task_ceiling_fires_scope(self):
        got = triggers.combine_proposal(proposal(tasks=20), POLICY)
        self.assertTrue(got["proposal-scope"]["fired"])
        self.assertIn("over the ceiling", got["proposal-scope"]["evidence"])

    def test_the_file_ceiling_fires_scope(self):
        files = [f"src/f{i}.scala" for i in range(30)]
        cfg = {"punch_out": {**POLICY["punch_out"], "proposal_task_ceiling": 99}}
        got = triggers.combine_proposal(proposal(tasks=30, files=files), cfg)
        self.assertTrue(got["proposal-scope"]["fired"])
        self.assertIn("files", got["proposal-scope"]["evidence"])

    def test_ceilings_come_from_config(self):
        cfg = {"punch_out": {"proposal_task_ceiling": 1}}
        self.assertTrue(triggers.combine_proposal(proposal(tasks=2), cfg)["proposal-scope"]["fired"])
        self.assertFalse(triggers.combine_proposal(proposal(tasks=2), {})["proposal-scope"]["fired"])

    def test_a_suppressed_proposal_claim_does_not_skip_the_gate(self):
        doc = proposal(files=["the-lexicon/orders.json"], breaking=False)
        got = triggers.combine_proposal(doc, POLICY)
        self.assertTrue(got["proposal-breaking"]["fired"])
        self.assertTrue(got["proposal-breaking"]["disagreement"])

    def test_a_node_claim_alone_still_fires(self):
        got = triggers.combine_proposal(proposal(architecture=True), POLICY)
        self.assertTrue(got["proposal-architecture"]["fired"])
        self.assertEqual(got["proposal-architecture"]["source"], "claim")

    def test_no_proposal_is_undetermined_not_false(self):
        got = triggers.derive_proposal(None, POLICY)
        self.assertTrue(all(v["fired"] is None for v in got.values()))
        self.assertEqual(triggers.proposal_disagreements(None, POLICY), [])

    def test_a_path_prefix_must_match_a_whole_segment(self):
        """`.github` must not match `.githubby/x`, or the derivation is noise."""
        got = triggers.combine_proposal(proposal(files=[".githubby/x.yml"]), POLICY)
        self.assertFalse(got["protected-path"]["fired"])

    def test_disagreement_is_recorded_with_its_evidence(self):
        doc = proposal(files=["the-lexicon/orders.json"], breaking=False)
        found = triggers.proposal_disagreements(doc, POLICY)
        names = [d["trigger"] for d in found]
        self.assertIn("proposal-breaking", names)
        entry = [d for d in found if d["trigger"] == "proposal-breaking"][0]
        self.assertEqual(entry["claimed"], False)
        self.assertEqual(entry["derived"], True)
        self.assertIn("the-lexicon", entry["evidence"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
