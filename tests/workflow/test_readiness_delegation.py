"""The readiness segment's runtime delegation claims, enforced rather than reported.

Task 5.6 asked for two things to be confirmed at runtime: that delegation to the
certified `readiness` nodes is permitted, and that editing a live node prompt
re-blocks it. `tests/workflow/readiness/run-readiness.py` drives the real gate and
writes a report; this file is what makes the report's claims fail a build when
they stop being true.

The report alone would not be enough. Task 8.7 found the same thing about
`CLAUDE.md`'s "docs change in the same commit" rule: it was prose, and prose is
what nobody re-reads.
"""

import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tests" / "workflow" / "readiness" / "run-readiness.py"
REPORT = ROOT / "tests" / "workflow" / "readiness" / "readiness-gate-report.results.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ReadinessHarnessCase(unittest.TestCase):
    """One fixture for the whole class — the harness copies ~2 MB per build."""

    @classmethod
    def setUpClass(cls):
        cls.h = _load("run_readiness", HARNESS)
        cls.reg = cls.h.load_registry()
        cls.base = Path(tempfile.mkdtemp(prefix="readiness-test-"))
        cls.fx = cls.h.build_fixture(cls.base, cls.reg)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)


class TestTheGateAnswersAtRuntime(ReadinessHarnessCase):
    def test_every_probe_reports_as_expected(self):
        for name, fn, expect in self.h.PROBES:
            with self.subTest(probe=name):
                ok, detail = fn(self.fx, self.reg)
                self.assertTrue(ok, f"{name} unexpected: {json.dumps(detail, indent=2)}")

    def test_delegation_to_both_certified_nodes_is_permitted(self):
        """The first of task 5.6's two open claims, asserted on its own."""
        for node in self.h.NODES:
            with self.subTest(node=node):
                code, said = self.h.gate(self.fx, node)
                self.assertEqual(code, 0, said)
                self.assertTrue(said.startswith("PASS"), said)

    def test_editing_either_live_prompt_reblocks_its_node(self):
        """The second claim. Both nodes, because one would not prove the rule."""
        for node in self.h.NODES:
            with self.subTest(node=node):
                target = self.fx / self.reg[node]["prompt"]
                original = target.read_text()
                try:
                    self.h.edit(target)
                    code, said = self.h.gate(self.fx, node)
                finally:
                    target.write_text(original)
                self.assertEqual(code, 1, f"{node} stayed delegable after an edit: {said}")
                self.assertIn("prompt changed since certification", said)


class TestTheHarnessCannotGoVacuous(ReadinessHarnessCase):
    """The probes are only worth their result if they keep their ability to fail."""

    def test_it_probes_both_polarities(self):
        """A suite of only-permits or only-refuses proves nothing about the other.

        The gate returning 0 for everything would satisfy every permit-probe, so
        the refuse set is what gives those their meaning — and vice versa.
        """
        names = {p[0] for p in self.h.PROBES}
        self.assertTrue(self.h.PERMITS & names, "no permit-probe is registered")
        self.assertTrue(self.h.REFUSES & names, "no refuse-probe is registered")

    def test_the_control_node_is_genuinely_uncertified(self):
        """If the control ever becomes certified, its probe silently stops testing.

        `uncertified-sibling-refused` is what shows the gate is not a yes-machine.
        Certifying `analysis` without repointing the control would leave a probe
        that asserts a certified node is refused — which would fail loudly — but
        marking it certified *and* relaxing the probe would not, so the registry
        flag is asserted here too.
        """
        entry = self.reg[self.h.UNCERTIFIED_CONTROL]
        self.assertFalse(entry.get("certified"),
                         f"{self.h.UNCERTIFIED_CONTROL} is now certified; "
                         "point UNCERTIFIED_CONTROL at a node that is not")

    def test_the_committed_report_covers_every_probe(self):
        """Adding a probe without regenerating the evidence fails here.

        The report is task 5.6's artifact. A probe that exists in code but not in
        the committed run means the evidence describes a smaller suite than the
        one that runs.
        """
        self.assertTrue(REPORT.exists(), f"no committed report at {REPORT}")
        data = json.loads(REPORT.read_text())
        recorded = {p["probe"] for p in data["probes"]}
        self.assertEqual(recorded, {p[0] for p in self.h.PROBES},
                         "re-run tests/workflow/readiness/run-readiness.py")
        self.assertEqual(data.get("inconclusive", ""), "",
                         "the committed run was inconclusive")
        for p in data["probes"]:
            self.assertTrue(p["ok"], f"committed report records {p['probe']} as unexpected")


class TestTheHarnessLeavesTheRealTreeAlone(ReadinessHarnessCase):
    """Probes edit prompts to prove an edit re-blocks. None may edit the real one."""

    def test_the_live_prompts_still_match_the_registry(self):
        """Run every probe, then check the real prompts are byte-identical.

        This is the invariant that matters: a harness that un-certifies the thing
        it is measuring would be worse than no harness, and a crash between an
        edit and its restore is the realistic way that happens. The fixture copy
        is the design that prevents it; this is the assertion that it held.
        """
        for name, fn, _ in self.h.PROBES:
            fn(self.fx, self.reg)
        for node in self.h.NODES:
            with self.subTest(node=node):
                live = ROOT / self.reg[node]["prompt"]
                actual = hashlib.sha256(live.read_bytes()).hexdigest()
                self.assertEqual(actual, self.reg[node]["prompt_sha256"],
                                 f"{live} no longer matches its recorded sha")


if __name__ == "__main__":
    unittest.main()
