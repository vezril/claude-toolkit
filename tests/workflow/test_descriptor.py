#!/usr/bin/env python3
"""The workflow descriptor and its resolver — the substrate's first module.

The thing these tests mostly defend is **equivalence**: the routing table moved out of a
Python literal in `flow-status.py` and into `skills/delivery-flow/workflow.yaml`, and a move
like that is only safe if the result is provably identical. One test compares them directly,
so a typo in the YAML cannot quietly drop or reorder a step — which would route a flow past a
missing step and still look like a successful run.

The rest defend inertness and refusal. A repo that opted into nothing must resolve to nothing
(this code is on the path of every hook invocation in every unrelated session), and anything
the parser cannot represent faithfully must raise rather than return a partial descriptor.

Run: python3 tests/workflow/test_descriptor.py
Standard library only, like the code under test.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
import descriptor as D  # noqa: E402

DELIVERY = ROOT / "skills" / "delivery-flow" / "workflow.yaml"

MINIMAL = """
workflow: demo
config_name: .demo.yaml
artifact_dir: demo
steps:
  - artifact: a.json
    step: first
    kind: adapter
  - artifact: b.json
    step: second
    kind: node
    optional_when: vault
"""


def flow_status():
    spec = importlib.util.spec_from_file_location(
        "fs", ROOT / "scripts" / "delivery-flow" / "flow-status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestEquivalenceWithTheTableItReplaced(unittest.TestCase):
    def test_the_descriptor_is_the_routing_table(self):
        """`flow-status.STEPS` must come from the descriptor and be unchanged by the move."""
        steps = flow_status().STEPS
        self.assertEqual(steps, D.step_table(D.load(DELIVERY)))

    def test_the_table_shape_is_the_one_callers_expect(self):
        """Four-tuples of (artifact, step, kind, optional_when) — not dicts."""
        for row in flow_status().STEPS:
            self.assertIsInstance(row, tuple)
            self.assertEqual(len(row), 4)

    def test_every_step_is_named_once(self):
        steps = [s for _a, s, _k, _o in flow_status().STEPS]
        self.assertEqual(sorted(steps), sorted(set(steps)))

    def test_optional_when_is_none_not_a_string(self):
        """An absent `optional_when` must read as None, as the Python literal did.

        The string "null" or "" here would make every step look conditional, and
        `flow-status` skips a step whose config question answers no.
        """
        by_step = {s: o for _a, s, _k, o in flow_status().STEPS}
        self.assertIsNone(by_step["intake"])
        self.assertEqual(by_step["project-memory"], "vault")


class TestResolution(unittest.TestCase):
    def test_a_repo_that_opted_into_nothing_resolves_to_nothing(self):
        """Inertness. This runs on every hook invocation in unrelated sessions."""
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(D.for_repo(Path(d), ROOT), [])
            found, err = D.resolve(Path(d), ROOT)
            self.assertIsNone(found)
            self.assertIsNone(err, "no workflow is the common case, not an error")

    def test_a_repo_with_the_config_resolves_to_that_workflow(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".delivery-flow.yaml").write_text("profile: full\n")
            found, err = D.resolve(Path(d), ROOT)
            self.assertIsNone(err)
            self.assertEqual(found["workflow"], "delivery-flow")

    def test_two_active_workflows_are_an_error_not_a_choice(self):
        """Picking one silently routes a step by the wrong table and still looks fine."""
        with tempfile.TemporaryDirectory() as plugin, tempfile.TemporaryDirectory() as repo:
            skills = Path(plugin) / "skills"
            for name in ("one", "two"):
                (skills / name).mkdir(parents=True)
                (skills / name / "workflow.yaml").write_text(
                    MINIMAL.replace("workflow: demo", f"workflow: {name}")
                           .replace("config_name: .demo.yaml", f"config_name: .{name}.yaml"))
                (Path(repo) / f".{name}.yaml").write_text("\n")
            self.assertEqual(len(D.for_repo(Path(repo), Path(plugin))), 2)
            found, err = D.resolve(Path(repo), Path(plugin))
            self.assertIsNone(found)
            self.assertIn("more than one workflow", err)

    def test_two_descriptors_claiming_one_name_is_an_error(self):
        with tempfile.TemporaryDirectory() as plugin:
            skills = Path(plugin) / "skills"
            for dirname in ("a", "b"):
                (skills / dirname).mkdir(parents=True)
                (skills / dirname / "workflow.yaml").write_text(MINIMAL)
            with self.assertRaises(ValueError) as cm:
                D.descriptors(Path(plugin))
            self.assertIn("same workflow name", str(cm.exception))


class TestTheParserRefusesRatherThanGuesses(unittest.TestCase):
    def test_a_minimal_descriptor_parses(self):
        doc = D.parse(MINIMAL)
        self.assertEqual(doc["workflow"], "demo")
        self.assertEqual(len(doc["steps"]), 2)
        self.assertEqual(D.step_table(doc),
                         [("a.json", "first", "adapter", None),
                          ("b.json", "second", "node", "vault")])

    def test_a_missing_required_key_raises(self):
        for key in ("workflow", "config_name", "artifact_dir"):
            with self.subTest(key=key):
                text = "\n".join(l for l in MINIMAL.splitlines()
                                 if not l.startswith(key + ":"))
                with self.assertRaises(ValueError) as cm:
                    D.parse(text)
                self.assertIn(key, str(cm.exception))

    def test_no_steps_raises(self):
        with self.assertRaises(ValueError):
            D.parse("workflow: d\nconfig_name: .d\nartifact_dir: d\nsteps:\n")

    def test_a_step_missing_a_field_raises(self):
        text = MINIMAL.replace("    kind: adapter\n", "")
        with self.assertRaises(ValueError) as cm:
            D.parse(text)
        self.assertIn("kind", str(cm.exception))

    def test_an_unclosed_inline_list_raises(self):
        """Same refusal as the profiles parser: truncation would look like success."""
        with self.assertRaises(ValueError) as cm:
            D.parse(MINIMAL + "\nextras: [a, b\n")
        self.assertIn("does not close", str(cm.exception))

    def test_comments_and_blank_lines_are_ignored(self):
        doc = D.parse("# a comment\n" + MINIMAL + "\n\n# trailing\n")
        self.assertEqual(len(doc["steps"]), 2)


class TestTheRealDescriptorIsCoherent(unittest.TestCase):
    def setUp(self):
        self.doc = D.load(DELIVERY)

    def test_its_pointers_exist(self):
        for key in ("schemas", "registry", "profiles", "pricing", "roster"):
            target = ROOT / self.doc[key]
            self.assertTrue(target.exists(), f"{key} points at {target}, which is absent")

    def test_it_names_the_opt_in_file_the_code_uses(self):
        """The descriptor and `common.CONFIG_NAME` must agree, or the hooks go inert."""
        sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
        import common
        self.assertEqual(self.doc["config_name"], common.CONFIG_NAME)
        self.assertEqual(self.doc["artifact_dir"], common.ARTIFACT_DIR)
        self.assertEqual(self.doc["sign_namespace"], common.SIGN_NAMESPACE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
