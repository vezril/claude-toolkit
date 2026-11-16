#!/usr/bin/env python3
"""Tests for init: a repo opts in with one command, and nothing un-guessable is guessed.

Run: python3 tests/delivery-flow/test_init.py
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
INIT = SCRIPTS / "init-delivery-flow.py"
FLOW = SCRIPTS / "flow-status.py"
sys.path.insert(0, str(SCRIPTS))
import common  # noqa: E402
from common import CONFIG_NAME, load_config, load_profiles, select_profile  # noqa: E402

import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("init_df", INIT)
init = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(init)


def repo(files=(), dirs=(), remote="git@github.com:acme/svc.git", branch="main", git=True):
    d = Path(tempfile.mkdtemp())
    for sub in dirs:
        (d / sub).mkdir(parents=True, exist_ok=True)
    for name, body in files:
        (d / name).parent.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body)
    if git:
        subprocess.run(["git", "init", "-q", "-b", branch, "."], cwd=d, capture_output=True)
        if remote:
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=d, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "i"],
                       cwd=d, capture_output=True)
    return d


def run(d, *args):
    """Init with a placement already chosen, since it now refuses to guess one.

    Defaults to the in-repo acknowledgement so every test that is not *about* placement reads
    as it did before. The tests that are about it pass `--vault-path` or their own
    `--artifacts-in-repo` explicitly.
    """
    if not any(a.startswith("--vault-path") or a.startswith("--artifacts-in-repo")
               for a in args):
        args = (*args, "--artifacts-in-repo", "test fixture")
    return subprocess.run([sys.executable, str(INIT), str(d), *args],
                          capture_output=True, text=True,
                              env={**os.environ, "DELIVERY_FLOW_REPOS": str(Path(tempfile.gettempdir()) / "df-test-repos")})


class TestDetection(unittest.TestCase):
    def test_scala_gets_sbt(self):
        d = repo(files=[("build.sbt", 'name := "x"\n')])
        run(d)
        self.assertEqual(load_config(d)["test_command"], "sbt test")

    def test_python_gets_pytest(self):
        d = repo(files=[("pyproject.toml", "[project]\nname='x'\n")])
        run(d)
        self.assertEqual(load_config(d)["test_command"], "pytest")

    def test_node_with_a_test_script_gets_npm(self):
        d = repo(files=[("package.json", json.dumps({"scripts": {"test": "jest"}}))])
        run(d)
        self.assertEqual(load_config(d)["test_command"], "npm test")

    def test_node_without_a_test_script_is_not_claimed(self):
        d = repo(files=[("package.json", json.dumps({"scripts": {"build": "tsc"}}))])
        run(d)
        self.assertFalse(load_config(d)["test_command"])

    def test_a_makefile_test_target_is_used_as_a_fallback(self):
        d = repo(files=[("Makefile", "build:\n\techo x\ntest:\n\techo t\n")])
        run(d)
        self.assertEqual(load_config(d)["test_command"], "make test")

    def test_an_undetectable_test_command_is_flagged_not_invented(self):
        d = repo(files=[("README.md", "# x\n")])
        out = run(d)
        self.assertIn("NOT DETECTED", out.stdout)
        self.assertFalse(load_config(d)["test_command"])

    def test_the_base_branch_comes_from_the_repo(self):
        d = repo(files=[("build.sbt", "x\n")], branch="trunk")
        run(d)
        self.assertEqual(load_config(d)["forge"]["base"], "trunk")

    def test_protected_paths_are_only_those_that_exist(self):
        d = repo(files=[("build.sbt", "x\n")], dirs=[".github/workflows", "charts"])
        run(d)
        protected = load_config(d)["punch_out"]["protected_paths"]
        self.assertIn(".github", protected)
        self.assertIn("charts", protected)
        self.assertNotIn("terraform", protected)

    def test_a_repo_with_none_of_them_gets_an_empty_list(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d)
        self.assertEqual(load_config(d)["punch_out"]["protected_paths"], [])

    def test_a_non_github_remote_is_flagged(self):
        d = repo(files=[("build.sbt", "x\n")], remote="git@gitlab.com:acme/svc.git")
        run(d)
        self.assertIn("not GitHub", (d / CONFIG_NAME).read_text())


class TestUndetectableFactsAreNotGuessed(unittest.TestCase):
    def test_contract_paths_start_empty_with_a_comment(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d)
        self.assertEqual(load_config(d)["punch_out"]["contract_paths"], [])
        self.assertIn("Only a human knows", (d / CONFIG_NAME).read_text())
        self.assertIn("contract_paths", out.stdout)

    def test_contract_paths_can_be_supplied(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--contract-paths", "the-lexicon,proto")
        self.assertEqual(load_config(d)["punch_out"]["contract_paths"], ["the-lexicon", "proto"])

    def test_a_jira_project_selects_the_jira_tracker(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--jira-project", "LDGR")
        tracker = load_config(d)["tracker"]
        self.assertEqual(tracker["kind"], "jira")
        self.assertEqual(tracker["project"], "LDGR")

    def test_a_jira_tracker_is_assumed_external_and_says_so(self):
        """The cautious reading costs a prompt; the wrong one posts to someone else's tracker."""
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d, "--jira-project", "LDGR")
        self.assertIs(load_config(d)["tracker"]["external"], True)
        self.assertIn("ASSUMED true", (d / CONFIG_NAME).read_text())
        self.assertIn("assumed true", out.stdout)

    def test_internal_can_be_declared(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--jira-project", "LDGR", "--internal")
        self.assertIs(load_config(d)["tracker"]["external"], False)
        self.assertNotIn("ASSUMED", (d / CONFIG_NAME).read_text())

    def test_external_and_internal_together_are_refused(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d, "--jira-project", "L", "--external", "--internal")
        self.assertEqual(out.returncode, 2)
        self.assertFalse((d / CONFIG_NAME).exists())

    def test_no_credential_is_ever_written(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d, "--jira-project", "LDGR")
        text = (d / CONFIG_NAME).read_text()
        for secret in ("JIRA_API_TOKEN=", "atlassian.net/rest", "password", "token:"):
            self.assertNotIn(secret, text)
        self.assertIn("JIRA_API_TOKEN", out.stdout)  # named, in the instructions

    def test_the_github_default_is_not_external(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d)
        self.assertEqual(load_config(d)["tracker"]["kind"], "github-issues")
        self.assertIs(load_config(d)["tracker"]["external"], False)


class TestTheResultIsUsable(unittest.TestCase):
    def test_the_config_parses_and_the_profile_resolves(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--jira-project", "LDGR")
        cfg = load_config(d)
        profile, err = select_profile(cfg, load_profiles())
        self.assertIsNone(err)
        self.assertEqual(profile["profile"], "triage")

    def test_flow_status_routes_in_the_new_repo(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--jira-project", "LDGR")
        (d / "delivery" / "LDGR-1").mkdir(parents=True)
        out = subprocess.run([sys.executable, str(FLOW), "LDGR-1", "--repo", str(d)],
                             capture_output=True, text=True,
                              env={**os.environ, "DELIVERY_FLOW_REPOS": str(Path(tempfile.gettempdir()) / "df-test-repos")})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("profile triage", out.stdout)
        self.assertIn("Next: intake", out.stdout)

    def test_the_full_profile_declares_its_uncertified_steps(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--profile", "full")
        self.assertEqual(sorted(load_config(d)["allow_uncertified"]), ["propose", "vault-update"])

    def test_the_triage_profile_declares_none(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d)
        self.assertEqual(load_config(d)["allow_uncertified"], [])

    def test_an_unknown_profile_is_refused(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d, "--profile", "nope")
        self.assertEqual(out.returncode, 2)
        self.assertIn("unknown profile", out.stderr)
        self.assertFalse((d / CONFIG_NAME).exists())


class TestAdditiveAndConfined(unittest.TestCase):
    def test_an_existing_config_is_not_clobbered(self):
        d = repo(files=[("build.sbt", "x\n"), (CONFIG_NAME, "tracker:\n  kind: local-markdown\n")])
        before = (d / CONFIG_NAME).read_text()
        out = run(d)
        self.assertEqual(out.returncode, 2)
        self.assertIn("already exists", out.stderr)
        self.assertEqual((d / CONFIG_NAME).read_text(), before)

    def test_force_replaces_it(self):
        d = repo(files=[("build.sbt", "x\n"), (CONFIG_NAME, "tracker:\n  kind: local-markdown\n")])
        self.assertEqual(run(d, "--force").returncode, 0)
        self.assertEqual(load_config(d)["tracker"]["kind"], "github-issues")

    def test_dry_run_writes_nothing(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d, "--dry-run")
        self.assertEqual(out.returncode, 0)
        self.assertIn("profile: triage", out.stdout)
        self.assertFalse((d / CONFIG_NAME).exists())

    def test_a_non_git_directory_is_refused(self):
        d = repo(files=[("build.sbt", "x\n")], git=False)
        out = run(d)
        self.assertEqual(out.returncode, 2)
        self.assertIn("not a git repository", out.stderr)
        self.assertFalse((d / CONFIG_NAME).exists())


class TestArtifactPlacement(unittest.TestCase):
    """Where a run's artifacts live, which init now refuses to guess.

    They hold the ticket body, the triage rationale, the breakdown and the brief — someone
    else's words, most of the time. The old default put them in the repo under `delivery/`
    with `artifacts.commit: true` on a private repo, which is one `git add` from a branch and
    one push from publishing a client's text.

    `artifacts.commit` is gone rather than defaulted differently. Nothing ever read it — it
    was written into every config and consumed by no code — and the question it was trying to
    answer ("may we commit the trail?") does not arise once the trail is not in the repo.
    """

    def test_it_refuses_to_guess(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = subprocess.run([sys.executable, str(INIT), str(d)],
                             capture_output=True, text=True,
                             env={**os.environ, "DELIVERY_FLOW_REPOS":
                                  str(Path(tempfile.gettempdir()) / "df-test-repos")})
        self.assertEqual(2, out.returncode)
        self.assertIn("--vault-path", out.stderr)
        self.assertIn("--artifacts-in-repo", out.stderr)
        self.assertFalse((d / CONFIG_NAME).exists(), "it wrote a config while refusing")

    def test_a_vault_path_derives_the_runs_directory(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--vault-path", "/tmp/Vault", "--graph-root", "Atlas/RAG")
        cfg = load_config(d)
        self.assertEqual("/tmp/Vault/Atlas/RAG/_runs", str(cfg["artifacts"]["root"]))
        self.assertNotIn("in_repo_ack", cfg["artifacts"])

    def test_a_vault_path_without_a_graph_root_still_derives(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--vault-path", "/tmp/Vault")
        self.assertEqual("/tmp/Vault/_runs", str(load_config(d)["artifacts"]["root"]))

    def test_the_in_repo_reason_is_written_into_the_file(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--artifacts-in-repo", "our own tracker, private repo")
        cfg = load_config(d)
        self.assertEqual("our own tracker, private repo", cfg["artifacts"]["in_repo_ack"])
        self.assertNotIn("root", cfg["artifacts"])

    def test_the_two_choices_are_contradictory(self):
        d = repo(files=[("build.sbt", "x\n")])
        out = run(d, "--vault-path", "/tmp/Vault", "--artifacts-in-repo", "why")
        self.assertEqual(2, out.returncode)
        self.assertIn("contradictory", out.stderr)

    def test_commit_is_gone(self):
        """It was written into every config and read by nothing."""
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--vault-path", "/tmp/Vault")
        self.assertNotIn("commit:", (d / CONFIG_NAME).read_text())

    def test_a_vault_rooted_repo_passes_the_preflight(self):
        """The point of all of it: the generated config is runnable without an ack."""
        d = repo(files=[("build.sbt", "x\n")])
        vault = Path(tempfile.mkdtemp()) / "Vault With Spaces"
        (vault / "Atlas" / "RAG" / "_runs").mkdir(parents=True)
        run(d, "--vault-path", str(vault), "--graph-root", "Atlas/RAG")
        self.assertEqual([], common.artifact_root_problems(d))

    def test_an_unexplained_in_repo_root_fails_the_preflight(self):
        d = repo(files=[("build.sbt", "x\n")])
        run(d, "--artifacts-in-repo", "declared")
        text = (d / CONFIG_NAME).read_text().replace("in_repo_ack: declared", "root: delivery")
        (d / CONFIG_NAME).write_text(text)
        problems = common.artifact_root_problems(d)
        self.assertTrue(problems)
        self.assertIn("inside the repository", problems[0])


class TestTestCommandPrecedence(unittest.TestCase):
    def test_a_makefile_target_beats_a_language_default(self):
        """The project declaring `make test` knows better than our inference from pyproject."""
        d = repo(files=[("pyproject.toml", "[project]\nname='x'\n"),
                        ("Makefile", "test: lint\n\tpytest -q\n")])
        run(d)
        self.assertEqual(load_config(d)["test_command"], "make test")

    def test_a_makefile_without_a_test_target_falls_through(self):
        d = repo(files=[("pyproject.toml", "[project]\nname='x'\n"),
                        ("Makefile", "build:\n\techo x\n")])
        run(d)
        self.assertEqual(load_config(d)["test_command"], "pytest")


if __name__ == "__main__":
    unittest.main(verbosity=2)
