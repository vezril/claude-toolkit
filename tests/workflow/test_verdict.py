#!/usr/bin/env python3
"""The verdict harness: fixed rules in the substrate, not interpretation in the orchestrator.

Design D5, task 4.7. A reviewer node emits REFUTED / WEAKENED / SURVIVED plus findings; this
decides what happens next, so that a model is never the thing deciding what its own reviewer's
verdict implies.

The test that matters most is `TestDeliveryFlowsBehaviourIsUnchanged`. delivery-flow documents
"a verdict of WEAKENED never blocks", while design D5 for the SDLC pipeline says WEAKENED
requires every finding addressed. Both are right for their own pipeline — one feeds a brief a
human reads, the other feeds a build — and a shared harness that imposed either would silently
change one of them. The policy is declared per workflow for exactly that reason, and these
tests pin both halves.

Run: python3 tests/workflow/test_verdict.py
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
import descriptor as D  # noqa: E402
import verdict as V  # noqa: E402

SDLC = D.load(ROOT / "skills" / "sdlc-orchestration" / "workflow.yaml")
DELIVERY = D.load(ROOT / "skills" / "delivery-flow" / "workflow.yaml")


def doc(value, findings=0):
    return {"verdict": value,
            "findings": [{"finding": f"f{i}", "evidence": "e"} for i in range(findings)]}


class TestSurvived(unittest.TestCase):
    def test_it_advances(self):
        d = V.decide(doc(V.SURVIVED), target_changed=False, descriptor=SDLC)
        self.assertEqual(d["action"], V.ADVANCE)

    def test_survived_with_findings_is_a_contradiction_and_blocks(self):
        """The reviewer said the artifact stands *and* named something wrong with it.

        Resolving that in favour of either side guesses at what it meant. Only its author
        knows, so the flow stops.
        """
        d = V.decide(doc(V.SURVIVED, findings=2), target_changed=False, descriptor=SDLC)
        self.assertEqual(d["action"], V.BLOCKED)
        self.assertIn("cannot both stand and carry defects", d["reason"])

    def test_the_policy_does_not_affect_it(self):
        for desc in (SDLC, DELIVERY, None):
            with self.subTest(desc=(desc or {}).get("workflow")):
                self.assertEqual(
                    V.decide(doc(V.SURVIVED), target_changed=False, descriptor=desc)["action"],
                    V.ADVANCE)


class TestRefuted(unittest.TestCase):
    def test_it_reruns_the_producer(self):
        d = V.decide(doc(V.REFUTED, findings=1), target_changed=False, refutations=1,
                     descriptor=SDLC)
        self.assertEqual(d["action"], V.RERUN_PRODUCER)

    def test_twice_on_the_same_target_is_a_punch_out(self):
        """Not a third attempt: a node that cannot satisfy its reviewer twice is a decision."""
        d = V.decide(doc(V.REFUTED, findings=1), target_changed=False, refutations=2,
                     descriptor=SDLC)
        self.assertEqual(d["action"], V.PUNCH_OUT)
        self.assertIn("limit", d["reason"])

    def test_the_limit_matches_delivery_flows_loop_bound(self):
        """One number for one idea, rather than a second limit meaning the same thing."""
        self.assertEqual(V.REFUTE_LIMIT, 2)

    def test_the_policy_does_not_affect_it(self):
        for desc in (SDLC, DELIVERY, None):
            with self.subTest(desc=(desc or {}).get("workflow")):
                self.assertEqual(
                    V.decide(doc(V.REFUTED), target_changed=True, descriptor=desc)["action"],
                    V.RERUN_PRODUCER)


class TestWeakenedUnderRequireAddressed(unittest.TestCase):
    """The SDLC pipeline's rule (design D5)."""

    def test_an_unchanged_target_means_nothing_was_addressed(self):
        d = V.decide(doc(V.WEAKENED, findings=3), target_changed=False, descriptor=SDLC)
        self.assertEqual(d["action"], V.BLOCKED)
        self.assertIn("unchanged since the verdict", d["reason"])

    def test_a_rewritten_target_reruns_the_reviewer_not_the_producer(self):
        """WEAKENED says the plan is right but incomplete, so it is not re-decomposed."""
        d = V.decide(doc(V.WEAKENED, findings=3), target_changed=True, descriptor=SDLC)
        self.assertEqual(d["action"], V.RERUN_REVIEWER)

    def test_there_is_no_path_from_weakened_straight_to_advance(self):
        """A caller cannot mark findings resolved — that is the claim the edge exists to not
        take on trust. Every route out passes through a fresh verdict."""
        for changed in (True, False):
            for n in (0, 1, 5):
                with self.subTest(changed=changed, findings=n):
                    action = V.decide(doc(V.WEAKENED, findings=n), target_changed=changed,
                                      descriptor=SDLC)["action"]
                    self.assertNotEqual(action, V.ADVANCE)

    def test_the_findings_travel_with_the_decision(self):
        d = V.decide(doc(V.WEAKENED, findings=2), target_changed=False, descriptor=SDLC)
        self.assertEqual(len(d["findings"]), 2)


class TestDeliveryFlowsBehaviourIsUnchanged(unittest.TestCase):
    """"A verdict of WEAKENED never blocks" — the documented rule, still true.

    If this fails, adding the harness changed the workflow that existed before it, which is
    the one outcome a substrate extraction must never produce.
    """

    def test_weakened_advances(self):
        d = V.decide(doc(V.WEAKENED, findings=3), target_changed=False, descriptor=DELIVERY)
        self.assertEqual(d["action"], V.ADVANCE)

    def test_it_advances_whether_or_not_the_target_moved(self):
        for changed in (True, False):
            with self.subTest(changed=changed):
                self.assertEqual(
                    V.decide(doc(V.WEAKENED, findings=1), target_changed=changed,
                             descriptor=DELIVERY)["action"], V.ADVANCE)

    def test_the_findings_are_still_reported(self):
        """Advancing is not ignoring: they travel as constraints for the consuming step."""
        d = V.decide(doc(V.WEAKENED, findings=2), target_changed=False, descriptor=DELIVERY)
        self.assertEqual(len(d["findings"]), 2)
        self.assertIn("constraints", d["reason"])

    def test_the_default_is_delivery_flows_rule(self):
        """A workflow that declares nothing must behave as delivery-flow did, not as D5 says.

        The default has to favour the pipeline that predates this module, or adding the module
        would have been a behaviour change disguised as a refactor.
        """
        self.assertEqual(V.weakened_policy({}), V.ADVANCE_ON_WEAKENED)
        self.assertEqual(V.weakened_policy(None), V.ADVANCE_ON_WEAKENED)
        self.assertEqual(
            V.decide(doc(V.WEAKENED, findings=1), target_changed=False)["action"], V.ADVANCE)


class TestTheDescriptorsDeclareTheirPolicy(unittest.TestCase):
    def test_both_declare_explicitly_rather_than_relying_on_the_default(self):
        """Reading the descriptor should tell you the rule."""
        for desc in (SDLC, DELIVERY):
            with self.subTest(workflow=desc["workflow"]):
                self.assertIn("verdict_policy", desc)
                self.assertIn((desc["verdict_policy"] or {}).get("weakened"),
                              V.WEAKENED_POLICIES)

    def test_they_declare_different_policies(self):
        self.assertNotEqual(V.weakened_policy(SDLC), V.weakened_policy(DELIVERY))

    def test_an_unrecognised_policy_falls_back_rather_than_raising(self):
        """A typo must not block every verdict in the workflow; it reads as the default."""
        self.assertEqual(V.weakened_policy({"verdict_policy": {"weakened": "nonsense"}}),
                         V.ADVANCE_ON_WEAKENED)


class TestAnUnreadableVerdictBlocks(unittest.TestCase):
    """A verdict is what a segment's advance turns on, so "I could not tell" must stop."""

    def test_an_unknown_verdict_value_blocks(self):
        for value in ("PASSED", "", None, "survived", 3):
            with self.subTest(value=value):
                d = V.decide({"verdict": value}, target_changed=False, descriptor=SDLC)
                self.assertEqual(d["action"], V.BLOCKED)

    def test_an_empty_or_missing_document_blocks(self):
        for bad in ({}, None):
            with self.subTest(bad=bad):
                self.assertEqual(
                    V.decide(bad, target_changed=False, descriptor=SDLC)["action"], V.BLOCKED)

    def test_it_does_not_guess_either_way(self):
        """Treating it as SURVIVED would advance a build on a malformed artifact; treating it
        as REFUTED would rerun a node that may have been right."""
        d = V.decide({"verdict": "???"}, target_changed=False, descriptor=SDLC)
        self.assertNotIn(d["action"], (V.ADVANCE, V.RERUN_PRODUCER))

    def test_malformed_findings_do_not_crash_it(self):
        d = V.decide({"verdict": V.WEAKENED, "findings": ["a string", None, {"finding": "f"}]},
                     target_changed=False, descriptor=SDLC)
        self.assertEqual(d["action"], V.BLOCKED)
        self.assertEqual(len(d["findings"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
