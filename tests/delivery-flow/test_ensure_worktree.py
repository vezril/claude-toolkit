#!/usr/bin/env python3
"""One ticket, one worktree, once.

Three sessions sharing one checkout spent an afternoon stepping on each other: a branch switch
with uncommitted work in it, a merge left half-resolved, and one `git add -A` that swept
another session's files into a commit describing something else. A ticket that owns its own
worktree cannot do that to another ticket.

The property these are mostly about is the trap rather than the feature. `.delivery-flow.yaml`
is often untracked — in `nx-neptune` it is in `.git/info/exclude`, because it carries a
client's Jira project and local paths and the repo is a public AWS checkout. A fresh worktree
therefore has no config, `is_delivery_repo()` is false for it, and **every hook goes inert**:
no edge checks, no punch-out enforcement, no trace, and nothing saying so. A per-ticket
worktree that silently turns off the guardrails is worse than no worktree at all.

Run: python3 tests/delivery-flow/test_ensure_worktree.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
ENSURE = SCRIPTS / "ensure-worktree.py"
EDGE = ROOT / "hooks" / "check-edge.py"
sys.path.insert(0, str(SCRIPTS))

import common  # noqa: E402

CONFIG = ("tracker:\n  kind: jira\n  project: AN\n  external: true\n"
          "forge:\n  kind: github-pr\n  base: main\n"
          "artifacts:\n  in_repo_ack: test fixture, no real ticket text\n")


class Repo:
    """A git repo with one commit on `main`, opted into delivery-flow."""

    def __init__(self, track_config=False):
        self.dir = Path(tempfile.mkdtemp()) / "code"
        self.dir.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        (self.dir / "README.md").write_text("x\n")
        (self.dir / common.CONFIG_NAME).write_text(CONFIG)
        if track_config:
            self.git("add", "-A")
        else:
            # The real shape: the config is excluded, so a worktree will not have it.
            (self.dir / ".git" / "info").mkdir(parents=True, exist_ok=True)
            (self.dir / ".git" / "info" / "exclude").write_text(
                f"{common.CONFIG_NAME}\n")
            self.git("add", "README.md")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "initial")
        self.registry = self.dir.parent / "repos"

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, capture_output=True, text=True)

    def run(self, *args):
        env = {**os.environ, "DELIVERY_FLOW_REPOS": str(self.registry)}
        return subprocess.run([sys.executable, str(ENSURE), *args, "--repo", str(self.dir)],
                              capture_output=True, text=True, env=env)

    def worktrees(self):
        out = self.git("worktree", "list", "--porcelain").stdout
        return [l[len("worktree "):] for l in out.splitlines() if l.startswith("worktree ")]


class TestItIsMadeOnce(unittest.TestCase):

    def test_a_worktree_is_created_for_the_ticket(self):
        r = Repo()
        out = r.run("AN-1", "--json")
        self.assertEqual(0, out.returncode, out.stderr)
        doc = json.loads(out.stdout)
        self.assertTrue(doc["created"])
        self.assertEqual("delivery/AN-1", doc["branch"])
        self.assertTrue(Path(doc["worktree"]).is_dir())
        self.assertIn(doc["worktree"], r.worktrees())

    def test_a_second_call_reports_the_same_one(self):
        """Idempotent, because it runs again on every resumption."""
        r = Repo()
        first = json.loads(r.run("AN-1", "--json").stdout)
        second = json.loads(r.run("AN-1", "--json").stdout)
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual(first["worktree"], second["worktree"])
        self.assertEqual(2, len(r.worktrees()), "a second worktree was created")

    def test_two_tickets_get_two_worktrees(self):
        r = Repo()
        a = json.loads(r.run("AN-1", "--json").stdout)
        b = json.loads(r.run("AN-2", "--json").stdout)
        self.assertNotEqual(a["worktree"], b["worktree"])
        self.assertNotEqual(a["branch"], b["branch"])

    def test_it_is_found_by_branch_not_by_path(self):
        """So a worktree someone moved is still recognised rather than duplicated."""
        r = Repo()
        first = json.loads(r.run("AN-1", "--json").stdout)
        moved = Path(first["worktree"]).parent / "moved-elsewhere"
        self.assertEqual(0, r.git("worktree", "move", first["worktree"], str(moved)).returncode)
        second = json.loads(r.run("AN-1", "--json").stdout)
        self.assertFalse(second["created"])
        self.assertEqual(str(moved), second["worktree"])


class TestTheHooksAreNotLeftInert(unittest.TestCase):
    """The trap. A worktree with no config is not a delivery repo, and silence is the failure."""

    def test_an_untracked_config_is_copied_in(self):
        r = Repo(track_config=False)
        doc = json.loads(r.run("AN-1", "--json").stdout)
        self.assertTrue(doc["config_copied"])
        self.assertTrue((Path(doc["worktree"]) / common.CONFIG_NAME).exists())

    def test_the_worktree_is_a_delivery_repo_afterwards(self):
        """The assertion the script makes about itself before reporting success."""
        r = Repo(track_config=False)
        doc = json.loads(r.run("AN-1", "--json").stdout)
        self.assertTrue(common.is_delivery_repo(Path(doc["worktree"])))

    def test_the_edge_hook_is_live_in_the_worktree(self):
        """End to end: the thing that was silently off. A bad artifact must be rejected."""
        r = Repo(track_config=False)
        wt = Path(json.loads(r.run("AN-1", "--json").stdout)["worktree"])
        item_dir = wt / "delivery" / "AN-1"
        item_dir.mkdir(parents=True)
        (item_dir / "triage.json").write_text(json.dumps(
            {"item": "AN-1", "type": "enhancement"}))  # not a valid type, and no sentinel
        payload = json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Write",
                              "cwd": str(wt),
                              "tool_input": {"file_path": str(item_dir / "triage.json")}})
        out = subprocess.run([sys.executable, str(EDGE)], input=payload,
                             capture_output=True, text=True)
        self.assertEqual(2, out.returncode,
                         f"the edge was inert in the worktree: {out.stdout} {out.stderr}")

    def test_a_tracked_config_is_not_copied(self):
        """Where git already carries it, a copy would be a second version to drift."""
        r = Repo(track_config=True)
        doc = json.loads(r.run("AN-1", "--json").stdout)
        self.assertFalse(doc["config_copied"])
        self.assertTrue((Path(doc["worktree"]) / common.CONFIG_NAME).exists())

    def test_the_worktree_is_registered(self):
        """`candidate_repos` reads the registry; an unregistered worktree is reachable only
        when the session's cwd happens to be inside it."""
        r = Repo()
        doc = json.loads(r.run("AN-1", "--json").stdout)
        self.assertTrue(doc["registered"])
        self.assertIn(doc["worktree"], r.registry.read_text())


class TestRefusals(unittest.TestCase):

    def test_a_non_delivery_repo_is_refused(self):
        d = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=d, capture_output=True)
        out = subprocess.run([sys.executable, str(ENSURE), "AN-1", "--repo", str(d)],
                             capture_output=True, text=True)
        self.assertEqual(2, out.returncode)
        self.assertIn("not a delivery-flow repo", out.stderr)

    def test_a_worktree_of_a_worktree_is_refused(self):
        """Legal to git, confusing to everyone, and it would copy a copy of the config."""
        r = Repo()
        wt = Path(json.loads(r.run("AN-1", "--json").stdout)["worktree"])
        out = subprocess.run([sys.executable, str(ENSURE), "AN-2", "--repo", str(wt)],
                             capture_output=True, text=True,
                             env={**os.environ, "DELIVERY_FLOW_REPOS": str(r.registry)})
        self.assertEqual(1, out.returncode)
        self.assertIn("is itself a worktree", out.stderr)

    def test_dry_run_creates_nothing(self):
        r = Repo()
        out = r.run("AN-1", "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual(1, len(r.worktrees()))

    def test_the_worktree_dir_is_excluded_locally_not_in_gitignore(self):
        """The tracked .gitignore belongs to the project; on a public upstream it is not ours
        to edit for a local convenience."""
        r = Repo()
        r.run("AN-1")
        self.assertIn(".worktrees", (r.dir / ".git" / "info" / "exclude").read_text())
        self.assertFalse((r.dir / ".gitignore").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
