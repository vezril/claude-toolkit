#!/usr/bin/env python3
"""The schemas' `consumed_by` and the step registry's `inputs` must describe one pipeline.

Open decision 3 is what this locks down. `project-context.schema.json` declared
`consumed_by: [breakdown, propose]`, but `steps.yaml` lists breakdown's inputs as
`[item.json, triage.json]` — so the schema asserted a dataflow the pipeline does not have.
Breakdown's certified prompt (`prompt_v6`) never mentions project context, and adding the
input instead would have un-certified the step, so the ruling was that the schema overstated.

The consequence is worth stating plainly rather than hiding: on the `triage` profile,
`project-memory` now has no downstream consumer at all. Recall still earns its place by
writing the vault trail the next run reads, but nothing in that profile's chain reads
`project-context.json`, and the registry is now honest about it.

`consumed_by` is not inert documentation — `hooks/check-edge.py` loops it and runs each named
consumer's input contract, so an overstated entry silently changes which checks run at an
edge. That is why this is a test and not a comment.

**Scope.** `steps.yaml` is the *certification* registry: it holds the LLM-prompt steps that
carry eval evidence (triage, breakdown, challenge-breakdown, pr-description), not every step
in the pipeline. So the cross-check only binds consumers that appear there. Deterministic
steps (`intake`, `brief`, `report`), steps not yet certified (`propose`, `implementation`),
and consumers that are not pipeline steps at all (`check-edge`, `harness`, `policy-check`,
the dev pair) declare no `inputs` to compare against, and are left alone rather than
asserted about with a registry that cannot see them.

Run: python3 tests/delivery-flow/test_schema_consumers.py
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
REGISTRY = ROOT / "skills" / "delivery-flow" / "steps.yaml"


def _certification_module():
    spec = importlib.util.spec_from_file_location(
        "check_certification", ROOT / "scripts" / "delivery-flow" / "check-certification.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_steps() -> dict:
    """step name -> its registry entry."""
    parsed = _certification_module().parse_registry(REGISTRY.read_text())
    return {s["step"]: s for s in parsed["steps"]}


def load_schemas() -> dict:
    return {p.name: json.loads(p.read_text()) for p in sorted(SCHEMAS.glob("*.schema.json"))}


class TestConsumedByMatchesTheRegistry(unittest.TestCase):

    def setUp(self):
        self.steps = load_steps()
        self.schemas = load_schemas()

    def test_every_certified_consumer_declares_the_artifact_as_an_input(self):
        """The invariant open decision 3 violated."""
        checked = 0
        for name, schema in self.schemas.items():
            artifact = schema["artifact"]
            for consumer in schema.get("consumed_by") or []:
                if consumer not in self.steps:
                    continue  # not in the certification registry; see the module docstring
                with self.subTest(schema=name, consumer=consumer):
                    checked += 1
                    inputs = self.steps[consumer].get("inputs") or []
                    self.assertIn(artifact, inputs,
                                  f"{name} claims {consumer!r} consumes it, but steps.yaml "
                                  f"lists that step's inputs as {inputs}")
        # A cross-check that silently stops checking anything is the failure mode here: if the
        # registry is renamed or its `inputs` keys drop out, every subTest above is skipped and
        # the test still passes. So assert it had something to say.
        self.assertGreater(checked, 0, "no schema consumer was cross-checked at all")

    def test_every_certified_producer_outputs_the_artifact_it_claims(self):
        for name, schema in self.schemas.items():
            producer = schema.get("produced_by")
            if not producer or producer not in self.steps:
                continue
            with self.subTest(schema=name, producer=producer):
                self.assertIn(schema["artifact"], self.steps[producer].get("outputs") or [])

    def test_consumed_by_and_consumers_describe_the_same_set(self):
        """Every declared consumer has a contract, and every contract has a declaration.

        Both halves matter and they fail differently: a `consumers` entry missing from
        `consumed_by` is a check that never runs (`check-edge.py:205` iterates `consumed_by`),
        while a `consumed_by` entry with no contract is a declaration that checks nothing.
        """
        # The sentinel's reader is the edge hook itself, not a pipeline step: it is checked
        # against the schema body directly, so it has no input contract to declare.
        exempt = {("sentinel.schema.json", "check-edge")}
        for name, schema in self.schemas.items():
            declared = {c for c in (schema.get("consumed_by") or []) if (name, c) not in exempt}
            with self.subTest(schema=name):
                self.assertEqual(sorted(declared), sorted(schema.get("consumers") or {}),
                                 f"{name} declares one set of consumers and contracts another")

    def test_the_registry_declares_inputs_the_schemas_do_not_claim_as_consumers(self):
        """A known, deliberate gap — recorded here so it is countable rather than forgotten.

        Three registry steps declare an input whose schema does not name them:
        breakdown and challenge-breakdown both read `item.json`, and challenge-breakdown reads
        `triage.json`. Unlike open decision 3 these are *under*-declarations, so no check runs
        that shouldn't; the cost is that no input contract is enforced for them either.

        Closing it means inventing a `consumers` contract for each — i.e. deciding which
        fields those certified steps require — which would start failing edges in a chain
        whose evals were run without it. That is a ruling, not a cleanup, so this test pins
        the gap at exactly three and fails if it grows.
        """
        gaps = []
        for step, entry in sorted(self.steps.items()):
            for artifact in entry.get("inputs") or []:
                schema = self.schemas.get(artifact.replace(".json", ".schema.json"))
                if schema is not None and step not in (schema.get("consumed_by") or []):
                    gaps.append((step, artifact))
        self.assertEqual([("breakdown", "item.json"),
                          ("challenge-breakdown", "item.json"),
                          ("challenge-breakdown", "triage.json")], gaps)


class TestProjectContextRuling(unittest.TestCase):
    """Open decision 3, decided: the schema overstated and breakdown is gone from it."""

    def setUp(self):
        self.schema = load_schemas()["project-context.schema.json"]

    def test_breakdown_is_not_claimed_as_a_consumer(self):
        self.assertNotIn("breakdown", self.schema["consumed_by"])
        self.assertNotIn("breakdown", self.schema.get("consumers") or {})

    def test_propose_remains_the_consumer_with_the_cold_start_contract(self):
        """Removing breakdown must not weaken the check: propose's contract is the stronger."""
        self.assertEqual(["propose"], self.schema["consumed_by"])
        propose = self.schema["consumers"]["propose"]
        self.assertEqual(["item", "project", "matched", "coverage"], propose["requires"])
        self.assertEqual(["decisions"], propose["requires_present"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
