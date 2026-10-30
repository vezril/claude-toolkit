#!/usr/bin/env python3
"""Tests for defect 12: the realized-diff gates must read *this item's* diff.

The bug these cover: `check-punch-out.py` read `git diff main...HEAD` and matched the whole
branch against `punch_out.contract_paths`. On the AN-3704 re-run that meant a two-file
docker-compose fix inherited four commits implementing AN-3630, and raised a breaking-change
punch-out whose evidence named three files it never touched.

Unlike `test_punch_outs.py`, whose fixture fakes `.git` with a bare directory, these build a
real repository with real commits — the attribution is a property of git history, so there is
nothing to test without one.

Run: python3 tests/delivery-flow/test_diff_attribution.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
CHECK = SCRIPTS / "check-punch-out.py"

TRIAGE = {"type": "feature", "path": "standard", "domains": ["backend"],
          "summary": "s", "rationale": "r", "handoff": False, "handoff_reason": None,
          "architecture_change": False, "breaking_change": False}


class Repo:
    """A real git repo with a `main` and a feature branch, opted into delivery-flow."""

    def __init__(self, contract=("lib",), protected=(".github",)):
        self.dir = Path(tempfile.mkdtemp())
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        cfg = ["tracker:", "  kind: local-markdown", "  external: false",
               "forge:", "  kind: github-pr", "  base: main",
               "punch_out:",
               f"  contract_paths: [{', '.join(contract)}]",
               f"  protected_paths: [{', '.join(protected)}]"]
        (self.dir / ".delivery-flow.yaml").write_text("\n".join(cfg) + "\n")
        self.write("README.md", "start")
        self.commit("initial commit")
        self.git("checkout", "-q", "-b", "work")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, capture_output=True, text=True)

    def write(self, rel, text="x"):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def item(self, key):
        d = self.dir / "delivery" / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "triage.json").write_text(json.dumps({**TRIAGE, "item": key}))
        return d

    def check(self, key, step="triage"):
        r = subprocess.run([sys.executable, str(CHECK), key, "--step", step,
                            "--repo", str(self.dir), "--json", "--dry-run"],
                           capture_output=True, text=True)
        return json.loads(r.stdout), r.stderr

    def fired(self, key, step="triage"):
        doc, _ = self.check(key, step)
        return {t["trigger"] for t in doc["triggered"]}

    def evidence(self, key, trigger, step="triage"):
        doc, _ = self.check(key, step)
        return next(t["evidence"] for t in doc["triggered"] if t["trigger"] == trigger)


class TestAttribution(unittest.TestCase):
    """Defect 12 itself: one branch, two items, neither inherits the other's diff."""

    def test_an_item_whose_commit_touches_a_contract_path_fires(self):
        r = Repo()
        r.item("AN-1")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the exported core")
        self.assertIn("breaking", r.fired("AN-1"))

    def test_a_second_item_on_the_same_branch_does_not_inherit_the_first(self):
        """The regression. AN-2 touches no contract path, so it must not fire."""
        r = Repo()
        r.item("AN-1")
        r.item("AN-2")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the exported core")
        r.write("proxy/docker-compose.yml", "ports: []")
        r.commit("AN-2: fix the proxy compose file")
        self.assertNotIn("breaking", r.fired("AN-2"))
        self.assertIn("breaking", r.fired("AN-1"))

    def test_the_evidence_names_the_item_it_was_attributed_to(self):
        """Defect 12's punch-out was indistinguishable from a true one. This is the tell."""
        r = Repo()
        r.item("AN-1")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the exported core")
        ev = r.evidence("AN-1", "breaking")
        self.assertIn("attributed to AN-1", ev)
        self.assertIn("1 commit naming AN-1", ev)
        self.assertIn("lib/core.py", ev)

    def test_an_uncommitted_change_is_attributed_to_the_item_being_checked(self):
        """Work in progress has no commit message to name, and must still be gated."""
        r = Repo()
        r.item("AN-1")
        r.write("lib/core.py", "changed")
        self.assertIn("breaking", r.fired("AN-1"))
        self.assertIn("the uncommitted working tree", r.evidence("AN-1", "breaking"))

    def test_a_clean_tree_with_no_commits_naming_the_item_fires_nothing(self):
        r = Repo()
        r.item("AN-1")
        r.item("AN-2")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the exported core")
        self.assertEqual(set(), r.fired("AN-2") & {"breaking", "protected-path"})

    def test_an_untracked_new_file_under_a_contract_path_is_seen(self):
        """`git diff HEAD` omits untracked files, so a brand-new file slipped the gate."""
        r = Repo()
        r.item("AN-1")
        r.write("lib/brand_new.py", "def f(): ...")
        self.assertIn("breaking", r.fired("AN-1"))
        self.assertIn("lib/brand_new.py", r.evidence("AN-1", "breaking"))

    def test_an_ignored_file_is_not_mistaken_for_a_change(self):
        r = Repo()
        r.item("AN-1")
        r.write(".gitignore", "lib/generated/\n")
        r.commit("AN-1: ignore generated output")
        r.write("lib/generated/out.py", "generated")
        self.assertNotIn("lib/generated/out.py", json.dumps(r.check("AN-1")[0]))

    def test_protected_paths_are_attributed_the_same_way(self):
        r = Repo()
        r.item("AN-1")
        r.item("AN-2")
        r.write(".github/workflows/ci.yml", "on: push")
        r.commit("AN-1: add CI")
        self.assertNotIn("protected-path", r.fired("AN-2"))
        self.assertIn("protected-path", r.fired("AN-1"))

    def test_several_commits_naming_the_item_are_all_attributed(self):
        r = Repo()
        r.item("AN-1")
        r.write("lib/a.py", "a")
        r.commit("AN-1: first")
        r.write("lib/b.py", "b")
        r.commit("AN-1: second")
        ev = r.evidence("AN-1", "breaking")
        self.assertIn("2 commits naming AN-1", ev)
        self.assertIn("lib/a.py", ev)
        self.assertIn("lib/b.py", ev)


class TestPrefixMatching(unittest.TestCase):
    """The realized diff matches paths by segment, like the planned paths already did."""

    def test_a_sibling_directory_sharing_a_prefix_does_not_match(self):
        """`lib` must not match `lib_extra/`. The old `startswith` said it did."""
        r = Repo(contract=("lib",))
        r.item("AN-1")
        r.write("lib_extra/thing.py", "x")
        r.commit("AN-1: touch a neighbour of the contract path")
        self.assertNotIn("breaking", r.fired("AN-1"))

    def test_a_file_named_exactly_as_the_prefix_matches(self):
        r = Repo(contract=("lib/core.py",))
        r.item("AN-1")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the one declared file")
        self.assertIn("breaking", r.fired("AN-1"))


class TestAttributionReport(unittest.TestCase):
    """What the gate could not see has to be countable, or the rate overstates coverage."""

    def test_unattributed_commits_are_counted(self):
        r = Repo()
        r.item("AN-1")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the core")
        r.write("other.py", "x")
        r.commit("drive-by fix with no item key")
        doc, stderr = r.check("AN-1")
        self.assertEqual(1, doc["diff_attribution"]["commits_attributed"])
        self.assertEqual(2, doc["diff_attribution"]["commits_in_range"])
        self.assertEqual(1, doc["diff_attribution"]["commits_unattributed"])
        self.assertIn("name no item key", stderr)

    def test_a_fully_attributed_branch_reports_no_gap(self):
        r = Repo()
        r.item("AN-1")
        r.write("lib/core.py", "changed")
        r.commit("AN-1: change the core")
        doc, stderr = r.check("AN-1")
        self.assertEqual(0, doc["diff_attribution"]["commits_unattributed"])
        self.assertNotIn("name no item key", stderr)

    def test_the_resolved_range_is_recorded(self):
        r = Repo()
        r.item("AN-1")
        doc, _ = r.check("AN-1")
        self.assertEqual("main..HEAD", doc["diff_attribution"]["range"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
