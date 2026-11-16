#!/usr/bin/env python3
"""The audit trail's five facts per step (task 7.1).

Stage 4's criterion 5 asks which step produced which output, on which model, for how many
tokens and at what cost. Those five facts are spread across two record kinds — `trace-step`
writes the model/token/cost side, `check-edge` writes the artifact/sha/edge side — so the
question is whether all five exist for a step, not whether one record carries them all.

Two defects these tests pin, both found by auditing real runs rather than reading the hooks:

1. **`trace-step` records carried no `hook` field.** `check-edge`'s did. 93 of AN-3702's 127
   records were therefore anonymous, and anything grouping by `hook` dropped every step record
   into an unlabelled bucket — including the first version of my own audit script, which
   reported "model: NO" for every step while the data was right there.
2. **A model missing from the pricing table yields no cost.** The table covers
   `claude-haiku-4-5` and not `claude-haiku-5-5`, so every haiku step records
   `api_equivalent_cost_usd: null` with `pricing_missing: true`. The flag is right — a guessed
   price would be worse than none — but a report must read that as *unpriced*, never as zero,
   or the cheapest and most-used tier silently costs nothing.

Run: python3 tests/workflow/test_audit_trail.py
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
import common  # noqa: E402

TRACE_STEP = ROOT / "hooks" / "trace-step.py"
CHECK_EDGE = ROOT / "hooks" / "check-edge.py"


class TestEveryRecordNamesItsAuthor(unittest.TestCase):
    """A record whose author is unknown cannot be grouped, filtered or audited."""

    def test_trace_step_sets_the_hook_field(self):
        text = TRACE_STEP.read_text()
        self.assertIn('"hook": "trace-step"', text)

    def test_check_edge_sets_the_hook_field(self):
        self.assertIn('"hook": "check-edge"', CHECK_EDGE.read_text())

    def test_both_of_trace_steps_record_shapes_set_it(self):
        """It writes two shapes — a full record and a `trace_error` one — and both must.

        The error shape is the one that matters most for an audit: it is written exactly when
        something went wrong, so an anonymous error record is a failure nobody can attribute.
        """
        text = TRACE_STEP.read_text()
        self.assertEqual(text.count('"hook": "trace-step"'), 2,
                         "one of trace-step's two record shapes is still anonymous")


class TestTheFiveFactsAreNamed(unittest.TestCase):
    """The field names a report reads. Renaming one silently empties a column."""

    FIELDS = {
        "model actually used": "model",
        "tokens in": "input_tokens",
        "tokens out": "output_tokens",
        "cost": "api_equivalent_cost_usd",
        "declared tier": "declared_tier",
    }

    def test_trace_step_writes_each_of_them(self):
        text = TRACE_STEP.read_text()
        for label, field in self.FIELDS.items():
            with self.subTest(fact=label):
                self.assertIn(f'"{field}"', text)

    def test_check_edge_writes_the_artifact_side(self):
        text = CHECK_EDGE.read_text()
        for field in ("artifact", "sha256", "edge"):
            with self.subTest(field=field):
                self.assertIn(f'"{field}"', text)

    def test_drift_from_the_declared_tier_is_recorded(self):
        """Design D7 allows escalation with evidence; the trace is where that evidence is.

        Without `model_conformant` a run on a heavier model than its registry tier is
        indistinguishable from one that obeyed.
        """
        self.assertIn('"model_conformant"', TRACE_STEP.read_text())


class TestAnUnpricedModelIsFlaggedNotZeroed(unittest.TestCase):
    def setUp(self):
        self.table = common.load_pricing()

    def test_the_table_states_when_it_was_written(self):
        """A cost figure with no date behind it cannot be judged stale."""
        self.assertTrue(self.table.get("meta", {}).get("as_of"))

    def test_an_unknown_model_is_unpriced_rather_than_free(self):
        self.assertIsNone(common.price_for("claude-not-a-real-model", self.table))

    def test_cost_is_none_for_an_unpriced_model(self):
        """`cost_usd` must not return 0 for a row it could not price.

        Zero and unknown are different claims, and a report that adds them together
        under-reports the total while looking complete.
        """
        self.assertIsNone(common.cost_usd({"input_tokens": 1000, "output_tokens": 1000}, None))

    def test_the_hook_flags_a_missing_price(self):
        self.assertIn('"pricing_missing"', TRACE_STEP.read_text())

    def test_the_haiku_gap_is_recorded_rather_than_hidden(self):
        """The live gap, asserted so it cannot be forgotten.

        `claude-haiku-5-5` is not in the table and is the tier design D7 pushes work toward —
        both readiness nodes are certified on it. Until the table lists it, every haiku step
        costs `null`. This test documents the gap by asserting it exists; when a real published
        price is added, it fails and should be deleted.
        """
        priced = common.price_for("claude-haiku-5-5", self.table)
        self.assertIsNone(
            priced,
            "claude-haiku-5-5 is now priced — delete this test and the note in tasks.md 7.1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
