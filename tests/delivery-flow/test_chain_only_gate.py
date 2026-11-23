"""The evidence package gates on the chain, which is what it claims.

`package-evidence.py`'s refusal has always read "a chain step is not certified", while
`certification_state()` gated on `--all` — every step in the registry. The two agreed only
because every registered step happened to be certified.

Registering the uncertified `review` step broke that: a step declared under
`allow_uncertified`, outside the chain, took the Stage 4 package back to DRAFT while the
certified chain was untouched. `--chain-only` narrows the gate to the claim.

The risk in narrowing a gate is turning it into one that cannot fail, so most of what is
asserted here is that it still refuses: an uncertified chain step, and an empty chain.
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "delivery-flow" / "check-certification.py"
REGISTRY = ROOT / "skills" / "delivery-flow" / "steps.yaml"


def _gate(*args):
    out = subprocess.run([sys.executable, "-I", str(GATE), *args],
                         capture_output=True, text=True)
    return out.returncode, (out.stdout or "") + (out.stderr or "")


def _registry_entries():
    spec = importlib.util.spec_from_file_location("check_certification", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_registry(REGISTRY.read_text())["steps"]


class TestTheChainOnlyGate(unittest.TestCase):
    def test_the_chain_steps_are_certified(self):
        code, out = _gate("--all", "--chain-only", "--registry", str(REGISTRY))
        self.assertEqual(code, 0, out)
        self.assertNotIn("FAIL", out)

    def test_it_checks_fewer_steps_than_all(self):
        """If chain-only checked the same set, narrowing achieved nothing."""
        _, chain = _gate("--all", "--chain-only", "--registry", str(REGISTRY))
        _, every = _gate("--all", "--registry", str(REGISTRY))
        self.assertLess(len(chain.splitlines()), len(every.splitlines()))

    def test_all_still_reports_the_non_chain_steps(self):
        """Narrowing the gate must not narrow the report: a reader asking for the
        registry's state still gets every step, including the uncertified ones."""
        _, every = _gate("--all", "--registry", str(REGISTRY))
        self.assertIn("review", every)
        self.assertIn("pr-description", every)

    def test_every_registry_step_is_either_chain_or_not(self):
        """Guard against a step that is silently neither — which under chain-only would
        mean a registered step no gate ever looks at."""
        for e in _registry_entries():
            with self.subTest(step=e.get("step")):
                self.assertIn("chain", e, f"{e.get('step')} declares no chain flag")


class TestItStillRefuses(unittest.TestCase):
    """The half that matters: a narrowed gate that cannot fail is worse than the bug."""

    def _registry(self, text: str) -> Path:
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        p = d / "steps.yaml"
        p.write_text(text)
        return p

    def test_an_uncertified_chain_step_still_fails(self):
        reg = self._registry(
            "steps:\n"
            "  - step: triage\n"
            "    chain: true\n"
            "    prompt: skills/delivery-flow/references/triage.md\n"
            "    tier: sonnet\n"
            "    certified: false\n")
        code, out = _gate("--all", "--chain-only", "--registry", str(reg))
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL triage", out)

    def test_an_empty_chain_refuses_rather_than_passing(self):
        """`chain:` dropped from every step would otherwise report success over nothing."""
        reg = self._registry(
            "steps:\n"
            "  - step: review\n"
            "    chain: false\n"
            "    prompt: skills/delivery-flow/references/review.md\n"
            "    tier: sonnet\n"
            "    certified: false\n")
        code, out = _gate("--all", "--chain-only", "--registry", str(reg))
        self.assertEqual(code, 1, out)
        self.assertIn("refusing to pass by absence", out)

    def test_a_non_chain_step_does_not_block_the_chain_gate(self):
        """The actual fix: `review` is uncertified and must not block the package."""
        code, out = _gate("review", "--registry", str(REGISTRY))
        self.assertEqual(code, 1, "review should be refused on its own merits")
        chain_code, _ = _gate("--all", "--chain-only", "--registry", str(REGISTRY))
        self.assertEqual(chain_code, 0, "but it must not fail the chain gate")


if __name__ == "__main__":
    unittest.main()
