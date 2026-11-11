#!/usr/bin/env python3
"""The readiness gate as an edge check rather than an instruction (design D4, task 4.5).

`skills/sdlc-orchestration/SKILL.md` used to tell the orchestrator to run `lint-story.py` and
`openspec validate`. Both are deterministic and neither was a guardrail, because a model that
skipped them produced no failure — the gate existed only while something chose to run it.

Two things these tests defend, and the second matters more:

1. **The gate blocks on what it should.** No change directory, no stories, a malformed story,
   a missing `openspec` CLI — each is a failure, and none passes by absence.
2. **The dispatch cannot go inert.** A declared checker that is missing from disk, or that
   raises, must become a *problem*. A gate that reports success because its own script was
   broken is the failure this project has found five times, and the code that runs the gates is
   the one place it must not come back.

Run: python3 tests/workflow/test_readiness_gate.py
"""

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
import common  # noqa: E402
import descriptor as D  # noqa: E402

GATE = ROOT / "scripts" / "sdlc" / "readiness-gate.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = load("readiness_gate", GATE)

STORY = """# Story 1.1: Verify TOTP at login
Status: ready-for-dev

## Story
As a user, I want to confirm a TOTP code, so that my account is protected.

## Acceptance Criteria
- AC-1: Given an enrolled user, when a valid code is entered, then the session is created.

## Tasks / Subtasks
- [ ] Validate the code (AC: 1)

## Dev Notes
- FR-1 covers this.

### References
- [Source: openspec/changes/add-2fa/proposal.md]
"""


class Fixture:
    """A code repo with an OpenSpec change, and a verdict artifact outside it."""

    def __init__(self, change="add-2fa", stories=True, well_formed=True):
        self.dir = Path(tempfile.mkdtemp()).resolve()
        self.repo = self.dir / "repo"
        self.change_dir = self.repo / "openspec" / "changes" / change
        self.change_dir.mkdir(parents=True)
        (self.change_dir / "proposal.md").write_text("# Proposal\n\n## FR-1\n")
        if stories:
            (self.change_dir / "stories").mkdir()
            text = STORY if well_formed else "# not a story\n"
            (self.change_dir / "stories" / "1-1-totp.md").write_text(text)
        # The artifact lives outside the repo, as it would under a configured artifacts root.
        self.runs = self.dir / "runs" / "SDLC-1"
        self.runs.mkdir(parents=True)
        self.verdict = self.runs / "readiness-verdict.json"
        self.verdict.write_text(json.dumps({
            "change": change, "verdict": "SURVIVED",
            "attacks": [{"attack": f"a{i}", "method": "m", "result": "failed"}
                        for i in range(3)],
            "findings": []}))


class TestTheGateBlocksOnFormNotJudgement(unittest.TestCase):
    def test_a_missing_change_directory_fails(self):
        f = Fixture()
        shutil.rmtree(f.change_dir)
        found, _info = gate.problems(f.verdict, f.repo)
        self.assertTrue(any("no change directory" in p for p in found), found)

    def test_the_change_directory_is_looked_for_in_the_repo_not_beside_the_artifact(self):
        """The defect that blocked a live run at propose, in its new home.

        The verdict sits outside the repo. Inferring the repo from the artifact's own path
        finds the runs directory, where no `openspec/changes/` will ever be.
        """
        f = Fixture()
        with_repo, _ = gate.problems(f.verdict, f.repo)
        without, _ = gate.problems(f.verdict, None)
        self.assertFalse(any("no change directory" in p for p in with_repo), with_repo)
        self.assertTrue(any("no change directory" in p for p in without), without)

    def test_no_stories_is_a_failure_not_an_empty_pass(self):
        f = Fixture(stories=False)
        found, info = gate.problems(f.verdict, f.repo)
        self.assertTrue(any("no story files" in p for p in found), found)
        self.assertEqual(info.get("stories"), 0)

    def test_a_malformed_story_fails(self):
        f = Fixture(well_formed=False)
        found, _info = gate.problems(f.verdict, f.repo)
        self.assertTrue(found, "lint-story.py accepted a file that is not a story")

    def test_a_verdict_naming_no_change_fails(self):
        f = Fixture()
        f.verdict.write_text(json.dumps({"change": "", "verdict": "SURVIVED",
                                         "attacks": [], "findings": []}))
        found, _info = gate.problems(f.verdict, f.repo)
        self.assertEqual(found, ["the verdict names no change"])

    def test_an_unreadable_artifact_is_a_problem_not_a_crash(self):
        f = Fixture()
        f.verdict.write_text("{ not json")
        found, _info = gate.problems(f.verdict, f.repo)
        self.assertTrue(found)
        self.assertIn("not valid JSON", found[0])

    def test_a_missing_openspec_cli_blocks_rather_than_passing(self):
        """The inert-gate trap in its most tempting form.

        Skipping when `openspec` is absent would make the gate pass on every machine without
        it, while the report claimed the change-artifact form had been checked.
        """
        f = Fixture()
        found, info = gate.problems(f.verdict, f.repo)
        if shutil.which("openspec") is None:
            self.assertTrue(any("openspec is not on PATH" in p for p in found), found)
            self.assertIs(info.get("openspec_validate_ran"), False)
        else:
            self.assertIs(info.get("openspec_validate_ran"), True)

    def test_it_does_not_read_the_verdicts_judgement(self):
        """`verdict` is the node's claim; this gate is about form only (design D5).

        A REFUTED verdict and a SURVIVED one must produce the same gate problems, or the
        deterministic layer would be taking the reviewer's word for something.
        """
        f = Fixture()
        base, _ = gate.problems(f.verdict, f.repo)
        doc = json.loads(f.verdict.read_text())
        doc["verdict"] = "REFUTED"
        f.verdict.write_text(json.dumps(doc))
        after, _ = gate.problems(f.verdict, f.repo)
        self.assertEqual(base, after)


class TestTheDescriptorDeclaresIt(unittest.TestCase):
    def setUp(self):
        self.doc = D.load(ROOT / "skills" / "sdlc-orchestration" / "workflow.yaml")

    def test_the_sdlc_descriptor_declares_the_gate(self):
        self.assertEqual((self.doc.get("edge_checks") or {}).get("readiness-verdict.json"),
                         "scripts/sdlc/readiness-gate.py")

    def test_the_declared_script_exists(self):
        for artifact, script in (self.doc.get("edge_checks") or {}).items():
            with self.subTest(artifact=artifact):
                self.assertTrue((ROOT / script).is_file(), script)

    def test_the_declared_script_exposes_the_checker_contract(self):
        """`problems(path, repo) -> (problems, info)`, the same shape validate-proposal has."""
        for _artifact, script in (self.doc.get("edge_checks") or {}).items():
            mod = load(Path(script).stem.replace("-", "_"), ROOT / script)
            self.assertTrue(callable(getattr(mod, "problems", None)), script)

    def test_delivery_flow_declares_none(self):
        """Its proposal check is still the older hard-coded branch, and that is recorded."""
        other = D.load(ROOT / "skills" / "delivery-flow" / "workflow.yaml")
        self.assertFalse(other.get("edge_checks"))


class TestTheDispatchCannotGoInert(unittest.TestCase):
    """A broken checker must become a problem. This is the code that runs the gates."""

    def setUp(self):
        self.hook = load("ce_gate", ROOT / "hooks" / "check-edge.py")

    def test_a_declared_script_missing_from_disk_is_a_problem(self):
        f = Fixture()
        fake = [{"workflow": "ghost", "config_name": ".ghost",
                 "edge_checks": {"readiness-verdict.json": "scripts/nope/gone.py"}}]
        self.hook.workflows = lambda: fake
        out = self.hook.declared_checks(f.verdict, f.repo, common)
        self.assertEqual(len(out), 1)
        _name, found = out[0]
        self.assertTrue(any("not on disk" in p for p in found), found)

    def test_a_checker_that_raises_is_a_problem(self):
        f = Fixture()
        broken = Path(tempfile.mkdtemp()) / "broken-gate.py"
        broken.write_text("def problems(path, repo):\n    raise RuntimeError('boom')\n")
        rel = broken.relative_to(broken.parents[1])
        fake = [{"workflow": "ghost", "config_name": ".ghost",
                 "edge_checks": {"readiness-verdict.json": str(rel)}}]
        self.hook.workflows = lambda: fake
        # Restored afterwards. Without the cleanup this repointed the *shared* descriptor
        # module's plugin root at a temp directory for the rest of the process, so every later
        # test in the same run saw a plugin with no workflows in it — and the ones that noticed
        # were the ones resolving an artifact root from a descriptor, two modules away.
        original = self.hook.workflow_descriptor.PLUGIN_ROOT
        self.addCleanup(setattr, self.hook.workflow_descriptor, "PLUGIN_ROOT", original)
        self.hook.workflow_descriptor.PLUGIN_ROOT = broken.parents[1]
        out = self.hook.declared_checks(f.verdict, f.repo, common)
        _name, found = out[0]
        self.assertTrue(any("could not run" in p and "RuntimeError" in p for p in found), found)

    def test_an_artifact_nobody_declares_runs_no_extra_check(self):
        f = Fixture()
        self.assertEqual(self.hook.declared_checks(f.runs / "item.json", f.repo, common), [])


class TestTheOrchestratorNoLongerInvokesThem(unittest.TestCase):
    """The other half of D4: the instruction has to be gone, not merely duplicated."""

    def setUp(self):
        self.text = (ROOT / "skills" / "sdlc-orchestration" / "SKILL.md").read_text()

    def test_the_skill_says_the_hook_runs_them(self):
        self.assertIn("edge_checks", self.text)
        self.assertIn("do not run those gates yourself", self.text)

    def test_the_skill_does_not_instruct_the_orchestrator_to_run_them(self):
        """No imperative `run lint-story.py` remains.

        Mentioning the scripts is fine and necessary — the orchestrator has to know what gates
        it is subject to. Being told to invoke them is what made the gate skippable.
        """
        for bad in ("run `scripts/lint-story.py`", "Run `scripts/lint-story.py`",
                    "invoke `lint-story.py`", "run `openspec validate`"):
            self.assertNotIn(bad, self.text, bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
