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

# Loaded by path under unique names, NOT via `sys.path` + `import verdict`.
#
# `scripts/application-review/verdict.py` and `scripts/workflow/verdict.py` are two different
# modules that both import as `verdict`, so whichever test file ran first won
# `sys.modules["verdict"]` and the other silently got the wrong module. That is the whole of
# the ~38 "pre-existing failures" this suite carried: not a pytest basename artifact, as it was
# repeatedly described, but one module shadowing another — and the symptom was an
# `AttributeError` for a function that exists, in a file that passes in isolation.
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


D = _load("workflow_descriptor_for_tests", ROOT / "scripts" / "workflow" / "descriptor.py")
V = _load("workflow_verdict_for_tests", ROOT / "scripts" / "workflow" / "verdict.py")

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


class TestThePolicyIsPerStep(unittest.TestCase):
    """One workflow legitimately wants both answers.

    delivery-flow's breakdown challenge feeds a brief a human reads and must not block on
    WEAKENED — documented behaviour of the certified triage chain. Its `review` step feeds a
    merge, where unaddressed findings are exactly what must block. A single workflow-wide value
    cannot say both, and setting the workflow to `require-addressed` to get the review's
    behaviour would silently change the certified chain's.
    """

    DESC = {"verdict_policy": {"weakened": "advance",
                               "weakened_review": "require-addressed"}}

    def test_a_per_step_rule_wins_over_the_workflow_default(self):
        self.assertEqual("require-addressed", V.weakened_policy(self.DESC, "review"))

    def test_a_step_with_no_rule_inherits_the_workflow_default(self):
        self.assertEqual("advance", V.weakened_policy(self.DESC, "challenge-breakdown"))

    def test_no_step_given_falls_back_to_the_workflow_default(self):
        self.assertEqual("advance", V.weakened_policy(self.DESC))

    def test_an_unrecognised_per_step_value_falls_back_rather_than_blocking(self):
        """Guessing which policy a typo meant is how a merge-blocking rule quietly becomes a
        non-blocking one without anybody editing it — so it falls back and does not invent."""
        desc = {"verdict_policy": {"weakened": "advance", "weakened_review": "requre-adressed"}}
        self.assertEqual("advance", V.weakened_policy(desc, "review"))

    def test_the_same_verdict_routes_differently_by_step(self):
        """The behaviour this exists for, asserted end to end through decide()."""
        weak = {"verdict": "WEAKENED", "findings": [{"finding": "f", "evidence": "e"}]}
        advanced = V.decide(weak, target_changed=False, descriptor=self.DESC,
                                  step="challenge-breakdown")
        blocked = V.decide(weak, target_changed=False, descriptor=self.DESC,
                                 step="review")
        self.assertEqual(V.ADVANCE, advanced["action"])
        self.assertEqual(V.BLOCKED, blocked["action"])

    def test_a_rewritten_target_reruns_the_reviewer_rather_than_advancing(self):
        """There is deliberately no path from WEAKENED to advance that skips a fresh verdict."""
        weak = {"verdict": "WEAKENED", "findings": [{"finding": "f", "evidence": "e"}]}
        d = V.decide(weak, target_changed=True, descriptor=self.DESC, step="review")
        self.assertEqual(V.RERUN_REVIEWER, d["action"])

    def test_the_real_descriptor_declares_it_this_way(self):
        """Against the shipped file, so a rename of the key fails here rather than silently
        reverting `review` to the non-blocking policy."""
        desc = DELIVERY
        self.assertEqual("require-addressed", V.weakened_policy(desc, "review"))
        self.assertEqual("advance", V.weakened_policy(desc, "challenge-breakdown"))
