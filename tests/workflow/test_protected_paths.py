#!/usr/bin/env python3
"""The protected-path gate, for both config shapes (task 6.5).

`scripts/check-protected-paths.py` is the mechanical half of "the pipeline never modifies CI
config, its own policy, hooks, or validators". A run that can edit its own guardrails has none.

The reason this file exists: the checker matched `protected_paths:` only at column 0, which is
the shape `templates/unattended/unattended-policy.yml` uses. `.delivery-flow.yaml` and
`templates/sdlc/sdlc.yaml` nest the same key under `punch_out:`, so on either of those the
checker found no block. It was caught only because an empty list exits 2 — "refusing to pass by
absence" — rather than permitting everything, which is the single most important line in that
script and the one these tests defend hardest.

Run: python3 tests/workflow/test_protected_paths.py
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "scripts" / "check-protected-paths.py"
SDLC_POLICY = ROOT / "templates" / "sdlc" / "sdlc.yaml"
UNATTENDED_POLICY = ROOT / "templates" / "unattended" / "unattended-policy.yml"


def checker():
    spec = importlib.util.spec_from_file_location("cpp", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Repo:
    """A two-commit repo whose work branch edits one protected and one ordinary file."""

    def __init__(self, touch="hooks/guard.py"):
        self.dir = Path(tempfile.mkdtemp()) / "repo"
        self.dir.mkdir(parents=True)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "t@t")
        self._git("config", "user.name", "t")
        for rel in ("ok.txt", touch):
            p = self.dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("one\n")
        self._git("add", "-A")
        self._git("commit", "-qm", "base")
        self._git("checkout", "-q", "-b", "work")
        self.touch = touch

    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, capture_output=True, text=True)

    def edit(self, rel):
        (self.dir / rel).write_text("two\n")
        self._git("add", "-A")
        self._git("commit", "-qm", f"edit {rel}")

    def check(self, policy):
        return subprocess.run(
            [sys.executable, str(CHECK), "--policy", str(policy),
             "--base", "main", "--head", "HEAD", "--repo", str(self.dir)],
            capture_output=True, text=True)


class TestItReadsBothConfigShapes(unittest.TestCase):
    def test_a_top_level_block_is_read(self):
        globs = checker().parse_protected_paths(UNATTENDED_POLICY)
        self.assertTrue(globs)
        self.assertIn("hooks/**", globs)

    def test_a_nested_block_is_read(self):
        """Under `punch_out:`, which is where the sdlc and delivery-flow configs put it."""
        globs = checker().parse_protected_paths(SDLC_POLICY)
        self.assertTrue(globs, "the nested block came back empty")
        self.assertIn("hooks/**", globs)

    def test_a_sibling_key_ends_the_block(self):
        """The list must stop at the next key, not swallow the rest of the file."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "policy.yml"
            p.write_text("punch_out:\n"
                         "  protected_paths:\n"
                         "    - hooks/**\n"
                         "    - scripts/**\n"
                         "  retry_limit: 3\n"
                         "other:\n"
                         "  - not-a-protected-path\n")
            self.assertEqual(checker().parse_protected_paths(p), ["hooks/**", "scripts/**"])

    def test_comments_do_not_truncate_the_list(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "policy.yml"
            p.write_text("protected_paths:\n"
                         "  - hooks/**        # the enforcement hooks\n"
                         "  # a standalone comment\n"
                         "  - scripts/**\n")
            self.assertEqual(checker().parse_protected_paths(p), ["hooks/**", "scripts/**"])


class TestItFailsOnViolation(unittest.TestCase):
    def test_editing_a_protected_path_fails_under_the_sdlc_policy(self):
        r = Repo()
        r.edit("hooks/guard.py")
        out = r.check(SDLC_POLICY)
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        self.assertIn("hooks/guard.py", out.stdout)

    def test_editing_a_protected_path_fails_under_the_unattended_policy(self):
        r = Repo()
        r.edit("hooks/guard.py")
        self.assertEqual(r.check(UNATTENDED_POLICY).returncode, 1)

    def test_editing_an_ordinary_file_passes(self):
        """The gate has to let real work through, or it would just stop everything."""
        r = Repo()
        r.edit("ok.txt")
        out = r.check(SDLC_POLICY)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_the_sdlc_policy_protects_its_own_config(self):
        """A pipeline that can rewrite `.sdlc.yaml` can widen its own permissions."""
        r = Repo(touch=".sdlc.yaml")
        r.edit(".sdlc.yaml")
        self.assertEqual(r.check(SDLC_POLICY).returncode, 1)


class TestItRefusesToPassByAbsence(unittest.TestCase):
    """The most important behaviour in the script, and how the nested-block bug was found."""

    def test_a_policy_with_no_block_is_an_error_not_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "policy.yml"
            p.write_text("budget:\n  max_minutes_per_job: 30\n")
            r = Repo()
            r.edit("hooks/guard.py")
            out = r.check(p)
            self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
            self.assertIn("refusing to pass by absence", out.stdout + out.stderr)

    def test_a_missing_policy_file_is_an_error(self):
        r = Repo()
        out = r.check(Path("/nonexistent/policy.yml"))
        self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
