#!/usr/bin/env python3
"""The opted-in repo registry, and the injection that keeps workflows apart.

This is the module the hook generalisation (section 2) depends on. A hook is handed the
*session's* cwd, never the directory a command wrote to, so it cannot learn the target repo
from its payload — a command can `cd`, hold the path in a variable, or write to an absolute
path from an unrelated cwd. The registry is what the hooks consult instead of guessing.

Two properties matter more than the mechanics:

1. **Workflows must not read each other's registries.** A second workflow inheriting
   delivery-flow's list would fire hooks in repos that never opted into it. The registry path
   and the membership predicate are both injected for that reason.
2. **`candidates` must find the repository root and then ask whether it opted in** — not the
   nearest ancestor holding the opt-in file. The first draft of that function conflated the
   two, which would have made a git repo without the config resolve to a configured parent
   directory. The test for it is below, because the difference is invisible until someone
   nests a repo inside a configured tree.

Run: python3 tests/workflow/test_registry.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "workflow"))
sys.path.insert(0, str(ROOT / "scripts" / "delivery-flow"))
import common  # noqa: E402
import registry as reg  # noqa: E402


def member_of(name):
    """`is_member` for a workflow whose opt-in file is `name`."""
    return lambda p: (Path(p) / name).is_file()


class TestWhereTheRegistryLives(unittest.TestCase):
    def test_the_env_var_is_derived_from_the_workflow_name(self):
        self.assertEqual(reg.env_var("delivery-flow"), "DELIVERY_FLOW_REPOS")
        self.assertEqual(reg.env_var("sdlc"), "SDLC_REPOS")

    def test_the_default_path_is_derived_too(self):
        saved = os.environ.pop("DELIVERY_FLOW_REPOS", None)
        try:
            self.assertEqual(reg.path_for("delivery-flow"),
                             Path("~/.config/delivery-flow/repos").expanduser())
        finally:
            if saved is not None:
                os.environ["DELIVERY_FLOW_REPOS"] = saved

    def test_the_generic_rule_reproduces_delivery_flows_existing_location(self):
        """Why this is a move and not a migration: no fixture or shell export changes."""
        saved = os.environ.pop("DELIVERY_FLOW_REPOS", None)
        try:
            self.assertEqual(common.repo_registry(), reg.path_for("delivery-flow"))
        finally:
            if saved is not None:
                os.environ["DELIVERY_FLOW_REPOS"] = saved

    def test_the_override_is_read_per_call_not_at_import(self):
        """A subprocess started later must see it; reading once at import broke that."""
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "repos"
            saved = os.environ.get("DELIVERY_FLOW_REPOS")
            os.environ["DELIVERY_FLOW_REPOS"] = str(target)
            try:
                self.assertEqual(reg.path_for("delivery-flow"), target)
                self.assertEqual(common.repo_registry(), target)
            finally:
                if saved is None:
                    del os.environ["DELIVERY_FLOW_REPOS"]
                else:
                    os.environ["DELIVERY_FLOW_REPOS"] = saved

    def test_two_workflows_get_two_registries(self):
        self.assertNotEqual(reg.path_for("delivery-flow"), reg.path_for("sdlc"))


class TestKnown(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.registry = self.dir / "repos"
        self.repo = self.dir / "a"
        self.repo.mkdir()
        (self.repo / ".demo.yaml").write_text("\n")

    def test_a_registered_member_is_listed(self):
        self.registry.write_text(f"{self.repo}\n")
        self.assertEqual(reg.known(self.registry, member_of(".demo.yaml")), [self.repo])

    def test_a_missing_registry_is_empty_not_an_error(self):
        self.assertEqual(reg.known(self.dir / "nope", member_of(".demo.yaml")), [])

    def test_a_stale_entry_is_dropped(self):
        """Entries are re-checked: a repo can lose its config after registering."""
        (self.repo / ".demo.yaml").unlink()
        self.registry.write_text(f"{self.repo}\n")
        self.assertEqual(reg.known(self.registry, member_of(".demo.yaml")), [])

    def test_comments_and_blanks_are_ignored(self):
        self.registry.write_text(f"# a note\n\n{self.repo}  # trailing\n")
        self.assertEqual(reg.known(self.registry, member_of(".demo.yaml")), [self.repo])

    def test_duplicates_are_collapsed(self):
        self.registry.write_text(f"{self.repo}\n{self.repo}\n")
        self.assertEqual(len(reg.known(self.registry, member_of(".demo.yaml"))), 1)

    def test_another_workflows_predicate_sees_nothing(self):
        """The isolation property: one registry, two workflows, no bleed."""
        self.registry.write_text(f"{self.repo}\n")
        self.assertEqual(reg.known(self.registry, member_of(".other.yaml")), [])


class TestRegister(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.registry = self.dir / "nested" / "repos"
        self.repo = self.dir / "a"
        self.repo.mkdir()

    def test_registering_creates_the_file_and_returns_true(self):
        self.assertTrue(reg.register(self.repo, self.registry))
        self.assertIn(str(self.repo.resolve()), self.registry.read_text())

    def test_registering_twice_is_false_and_does_not_duplicate(self):
        reg.register(self.repo, self.registry)
        self.assertFalse(reg.register(self.repo, self.registry))
        self.assertEqual(self.registry.read_text().strip().count("\n"), 0)

    def test_it_appends_rather_than_rewriting(self):
        """Concurrent sessions register; a read-modify-write would lose one."""
        other = self.dir / "b"
        other.mkdir()
        reg.register(self.repo, self.registry)
        reg.register(other, self.registry)
        self.assertEqual(len(self.registry.read_text().strip().splitlines()), 2)


class TestCandidates(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()).resolve()
        self.registry = self.dir / "repos"
        self.is_member = member_of(".demo.yaml")

    def _repo(self, name, configured=True):
        # Resolved: on macOS a tempdir is /var/... which resolves to /private/var/..., and
        # `_root_of` resolves while the fixture path would not. Comparing the two unresolved
        # forms fails for a reason that has nothing to do with the code under test.
        p = (self.dir / name).resolve()
        p.mkdir(parents=True)
        (p / ".git").mkdir()
        if configured:
            (p / ".demo.yaml").write_text("\n")
        return p

    def _root_of(self, start):
        """A git-root finder, mirroring `common.repo_root`."""
        cur = Path(start).resolve()
        for path in [cur, *cur.parents]:
            if (path / ".git").exists():
                return path
        return cur

    def test_the_sessions_own_repo_leads(self):
        mine = self._repo("mine")
        listed = self._repo("listed")
        self.registry.write_text(f"{listed}\n")
        found = reg.candidates({"cwd": str(mine)}, self.is_member, self.registry, self._root_of)
        self.assertEqual(found[0], mine)
        self.assertIn(listed, found)

    def test_a_cwd_below_the_root_still_resolves_to_the_root(self):
        mine = self._repo("mine")
        deep = mine / "src" / "pkg"
        deep.mkdir(parents=True)
        found = reg.candidates({"cwd": str(deep)}, self.is_member, self.registry, self._root_of)
        self.assertEqual(found, [mine])

    def test_an_unconfigured_repo_under_a_configured_parent_is_not_a_candidate(self):
        """The bug the first draft would have introduced.

        `root_of` finds the git root; the root either opted in or it did not. Walking up for
        the nearest opt-in file instead would wrongly claim this nested repo for the parent.
        """
        parent = self.dir / "tree"
        parent.mkdir()
        (parent / ".demo.yaml").write_text("\n")
        nested = parent / "inner"
        nested.mkdir()
        (nested / ".git").mkdir()          # a git repo, but it never opted in

        found = reg.candidates({"cwd": str(nested)}, self.is_member, self.registry,
                               self._root_of)
        self.assertEqual(found, [], f"nested repo was claimed for its parent: {found}")

    def test_no_candidates_when_nothing_opted_in(self):
        plain = self.dir / "plain"
        plain.mkdir()
        self.assertEqual(
            reg.candidates({"cwd": str(plain)}, self.is_member, self.registry, self._root_of),
            [])


class TestTheDeliveryFlowShims(unittest.TestCase):
    def test_the_shims_delegate(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "repos"
            repo = Path(d) / "r"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / ".delivery-flow.yaml").write_text("profile: full\n")

            saved = os.environ.get("DELIVERY_FLOW_REPOS")
            os.environ["DELIVERY_FLOW_REPOS"] = str(target)
            try:
                self.assertTrue(common.register_repo(repo))
                self.assertFalse(common.register_repo(repo))
                self.assertEqual(common.known_repos(), [repo.resolve()])
                self.assertIn(repo.resolve(), common.candidate_repos({"cwd": str(repo)}))
            finally:
                if saved is None:
                    del os.environ["DELIVERY_FLOW_REPOS"]
                else:
                    os.environ["DELIVERY_FLOW_REPOS"] = saved


if __name__ == "__main__":
    unittest.main(verbosity=2)
