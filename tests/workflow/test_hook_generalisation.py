#!/usr/bin/env python3
"""`check-edge` serving more than one workflow, and still serving none (tasks 2.1, 2.4, 2.5).

The hook used to answer three questions from hard-coded strings: is this repo mine
(`.delivery-flow.yaml`), is this path an artifact (`delivery/<ITEM>/<file>`), and which repos
are registered. All three now come from the descriptors.

Two properties are worth more than the mechanics, and they pull in opposite directions:

- **It must serve a second workflow.** A repo opted into one is not special; the hook scans
  every descriptor's artifact directory and consults every workflow's registry with that
  workflow's own membership predicate.
- **It must stay inert.** This runs on every tool call in every session, including the
  overwhelming majority that touch no workflow repo at all. A generalisation that made the
  hook fire more widely would be worse than the coupling it removed.

The fixtures build a throwaway plugin root with two descriptors and point
`CLAUDE_PLUGIN_ROOT` at it, which is also the check that `descriptor.PLUGIN_ROOT` honours
that variable — it did not at first, so the descriptors and the schemas they point at would
have come from different trees.

Run: python3 tests/workflow/test_hook_generalisation.py
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "check-edge.py"
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))

STEPS = """steps:
  - artifact: item.json
    step: intake
    kind: adapter
"""


def descriptor_text(name, config_name, artifact_dir):
    return (f"workflow: {name}\n"
            f"config_name: {config_name}\n"
            f"artifact_dir: {artifact_dir}\n"
            f"sign_namespace: {name}-decision\n"
            f"schemas: schemas\n" + STEPS)


class TwoWorkflowPlugin:
    """A plugin root defining two workflows, with a repo opted into each."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp()).resolve()
        (self.root / "schemas").mkdir()
        for name, cfg, art in (("alpha", ".alpha.yaml", "alpha-runs"),
                               ("beta", ".beta.yaml", "beta-runs")):
            d = self.root / "skills" / name
            d.mkdir(parents=True)
            (d / "workflow.yaml").write_text(descriptor_text(name, cfg, art))

    def repo(self, name, configs):
        p = self.root / "repos" / name
        p.mkdir(parents=True)
        (p / ".git").mkdir()
        for c in configs:
            (p / c).write_text("\n")
        return p


class HookUnder:
    """check-edge imported against a fixture plugin root, as a context manager.

    Three things have to happen together, and the first version of this helper did only one:

    1. `CLAUDE_PLUGIN_ROOT` must be set *and stay set*. `workflows()` is lazy, so it reads the
       variable when a test calls it, not when the module is imported.
    2. the substrate modules must be evicted from `sys.modules`. `descriptor.PLUGIN_ROOT` is
       module-level, so a cached import keeps whichever root was current the first time — the
       bug that made four of these tests report another fixture's workflows.
    3. the hook's own descriptor cache must be fresh, which falls out of re-importing it.

    This is only a problem in tests. A hook is one invocation in one process.
    """

    PURGE = ("descriptor", "layout", "registry", "schema", "trace", "pricing", "common")

    def __init__(self, plugin_root):
        self.plugin_root = Path(plugin_root)
        self._saved_env = None
        self._saved_modules = {}

    def __enter__(self):
        self._saved_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(self.plugin_root)
        for name in self.PURGE:
            if name in sys.modules:
                self._saved_modules[name] = sys.modules.pop(name)
        spec = importlib.util.spec_from_file_location(f"ce_{id(self)}", HOOK)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def __exit__(self, *exc):
        if self._saved_env is None:
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
        else:
            os.environ["CLAUDE_PLUGIN_ROOT"] = self._saved_env
        for name in self.PURGE:
            sys.modules.pop(name, None)
        sys.modules.update(self._saved_modules)
        return False


class TestItSeesEveryWorkflow(unittest.TestCase):
    def setUp(self):
        self.plugin = TwoWorkflowPlugin()
        self._ctx = HookUnder(self.plugin.root)
        self.hook = self._ctx.__enter__()
        self.addCleanup(self._ctx.__exit__, None, None, None)

    def test_both_descriptors_are_found(self):
        self.assertEqual(sorted(d["workflow"] for d in self.hook.workflows()),
                         ["alpha", "beta"])

    def test_both_artifact_directories_are_scanned(self):
        self.assertEqual(set(self.hook.artifact_dirs()), {"alpha-runs", "beta-runs"})

    def test_artifact_directories_are_longest_first(self):
        """A directory name that is a suffix of another must not win the match."""
        dirs = self.hook.artifact_dirs()
        self.assertEqual(dirs, sorted(dirs, key=len, reverse=True))

    def test_both_opt_in_files_count(self):
        self.assertEqual(self.hook.config_names(), [".alpha.yaml", ".beta.yaml"])

    def test_a_repo_opted_into_either_is_recognised(self):
        for cfg in (".alpha.yaml", ".beta.yaml"):
            with self.subTest(cfg=cfg):
                repo = self.plugin.repo(f"r{cfg}", [cfg])
                self.assertTrue(self.hook.any_workflow_repo([repo]))

    def test_a_repo_opted_into_both_is_recognised_once(self):
        repo = self.plugin.repo("both", [".alpha.yaml", ".beta.yaml"])
        self.assertTrue(self.hook.any_workflow_repo([repo]))

    def test_a_repo_opted_into_neither_is_not(self):
        repo = self.plugin.repo("plain", [])
        self.assertFalse(self.hook.any_workflow_repo([repo]))


class TestTheBashPatternCoversEveryWorkflow(unittest.TestCase):
    def setUp(self):
        self.plugin = TwoWorkflowPlugin()
        self._ctx = HookUnder(self.plugin.root)
        self.hook = self._ctx.__enter__()
        self.addCleanup(self._ctx.__exit__, None, None, None)

    def test_each_workflows_paths_are_matched(self):
        pattern = self.hook.bash_path_re()
        for art in ("alpha-runs", "beta-runs"):
            with self.subTest(art=art):
                self.assertTrue(pattern.findall(f"cat x > {art}/AN-1/item.json"))

    def test_an_unrelated_directory_is_not_matched(self):
        self.assertEqual(self.hook.bash_path_re().findall("cat x > other/AN-1/item.json"), [])

    def test_a_variable_base_still_yields_the_fragment(self):
        """The shape that defeated the earlier versions: `"$R/<art>/K/f.json"`."""
        payload = {"tool_name": "Bash", "cwd": str(self.plugin.root),
                   "tool_input": {"command": 'R=/abs; cat x > "$R/alpha-runs/AN-1/item.json"'}}
        found = [str(p) for p in self.hook.written_paths(payload)]
        self.assertTrue(any(p.endswith("alpha-runs/AN-1/item.json") for p in found), found)

    def test_the_metacharacter_case(self):
        """A workflow whose artifact dir contains a `.` must not match any character."""
        root = Path(tempfile.mkdtemp()).resolve()
        (root / "skills" / "dotty").mkdir(parents=True)
        (root / "skills" / "dotty" / "workflow.yaml").write_text(
            descriptor_text("dotty", ".dotty.yaml", "my.runs"))
        with HookUnder(root) as hook:
            self.assertTrue(hook.bash_path_re().findall("x > my.runs/AN-1/item.json"))
            self.assertEqual(hook.bash_path_re().findall("x > myXruns/AN-1/item.json"), [])


class TestItStaysInert(unittest.TestCase):
    """Task 2.5: a repo with no descriptor must see no behaviour change at all."""

    def test_a_plain_repo_produces_no_output_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / ".git").mkdir()
            payload = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                       "cwd": str(repo),
                       "tool_input": {"file_path": str(repo / "delivery" / "AN-1" / "x.json")}}
            r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "")
            self.assertEqual(r.stderr.strip(), "")

    def test_a_malformed_payload_never_fails_a_tool_call(self):
        r = subprocess.run([sys.executable, str(HOOK)], input="not json",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)

    def test_a_broken_descriptor_degrades_to_inert_rather_than_crashing(self):
        """A plugin whose descriptor cannot be parsed must not take every tool call down."""
        root = Path(tempfile.mkdtemp()).resolve()
        (root / "skills" / "bad").mkdir(parents=True)
        (root / "skills" / "bad" / "workflow.yaml").write_text("workflow: bad\nsteps:\n")
        with HookUnder(root) as hook:
            self.assertEqual(hook.workflows(), [])
            self.assertEqual(hook.artifact_dirs(), [])
            self.assertIsNone(hook.bash_path_re())
            self.assertFalse(hook.any_workflow_repo([root]))


class TestTheRealDescriptorStillDrivesDeliveryFlow(unittest.TestCase):
    """The regression guard: the shipped workflow must behave as before."""

    def setUp(self):
        self._ctx = HookUnder(ROOT)
        self.hook = self._ctx.__enter__()
        self.addCleanup(self._ctx.__exit__, None, None, None)

    def test_delivery_flow_is_the_only_workflow(self):
        self.assertEqual([d["workflow"] for d in self.hook.workflows()], ["delivery-flow"])

    def test_the_artifact_dir_is_delivery(self):
        self.assertEqual(self.hook.artifact_dirs(), ["delivery"])

    def test_the_pattern_is_what_it_was_before_the_generalisation(self):
        """One workflow in, character-for-character the original behaviour out."""
        pattern = self.hook.bash_path_re()
        self.assertTrue(pattern.findall("cat x > delivery/AN-1/item.json"))
        self.assertTrue(pattern.findall('R=/abs; cat x > "$R/delivery/K/f.json"'))
        self.assertEqual(pattern.findall("cat x > notdelivery_x/AN-1/item.json"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
