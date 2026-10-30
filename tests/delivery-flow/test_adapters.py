#!/usr/bin/env python3
"""Tests for the GitHub and local-markdown adapters: mapping, determinism, typed failures,
and the refusals.

No network. `gh` is replaced by a fake on PATH that records every invocation, which is what
lets a test assert the strongest thing about a refusal: that **no remote call was made**. A
mocked function would prove the adapter returned 2; the call log proves it stayed home.

Run: python3 tests/delivery-flow/test_adapters.py
"""

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "adapters"))

import github_issues  # noqa: E402
import github_pr  # noqa: E402
import local_markdown  # noqa: E402
from common import load_schemas  # noqa: E402

_spec = importlib.util.spec_from_file_location("validate_artifact", SCRIPTS / "validate-artifact.py")
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

ISSUE = {
    "number": 7,
    "title": "  Retries hammer the DLQ consumer  ",
    "body": "The consumer retries with no backoff.\n"
            "\n"
            "Epic: #1\n"
            "Design doc: #9\n"
            "See also #3 and https://github.com/acme/widgets/issues/4\n"
            "Another repo's issue: https://github.com/other/repo/issues/99\n",
    "labels": [{"name": "bug"}, {"name": "ingest"}, {"name": "consumer"}],
    "state": "OPEN",
    "stateReason": None,
    "url": "https://github.com/acme/widgets/issues/7",
}

PR = {
    "number": 42,
    "url": "https://github.com/acme/widgets/pull/42",
    "statusCheckRollup": [
        {"name": "build", "status": "COMPLETED", "conclusion": "SUCCESS", "detailsUrl": "https://x/1"},
        {"name": "test", "status": "IN_PROGRESS", "conclusion": "", "detailsUrl": "https://x/2"},
        {"context": "legacy/status", "state": "SUCCESS", "targetUrl": "https://x/3"},
    ],
}

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
argv = sys.argv[1:]
log = os.environ["FAKE_GH_LOG"]
with open(log, "a") as f:
    f.write(json.dumps(argv) + "\n")

mode = os.environ.get("FAKE_GH_MODE", "ok")
if mode == "auth":
    sys.stderr.write("gh: To get started with GitHub CLI, please run: gh auth login\n")
    sys.exit(4)
if mode == "notfound":
    sys.stderr.write("could not resolve to an Issue with the number of 7\n")
    sys.exit(1)
if mode == "garbage":
    sys.stdout.write("this is not json")
    sys.exit(0)

payload = json.load(open(os.environ["FAKE_GH_PAYLOAD"]))
if argv[:2] == ["issue", "view"]:
    print(json.dumps(payload["issue"]))
elif argv[:2] == ["issue", "comment"]:
    print("https://github.com/acme/widgets/issues/7#issuecomment-901")
elif argv[:2] in (["issue", "close"], ["issue", "reopen"]):
    pass
elif argv[:2] == ["pr", "view"]:
    print(json.dumps(payload["pr"]))
elif argv[:2] == ["pr", "create"]:
    print("Creating pull request for feat/x into main in acme/widgets")
    print("https://github.com/acme/widgets/pull/42")
else:
    sys.stderr.write("fake gh: unhandled " + " ".join(argv) + "\n")
    sys.exit(1)
'''

BACKLOG = """# Delivery backlog

## Payments service

### DEM-3: Retries hammer the DLQ consumer
Type: bug
Status: todo
Parent: DEM-1
Design: DEM-9
Related: DEM-4, DEM-5
Labels: ingest consumer

The consumer retries with no backoff and collapses the downstream.

Acceptance: delays grow to a 30s cap.

#### Comment 1 — 2026-01-01

An earlier post-back the next run must not read as a requirement.

### DEM-4: Add a dead-letter dashboard
Type: task

No status line on this one, on purpose.
"""

BULLETS = """# Feature wishlist

## Payments service

- Retry with backoff on the DLQ consumer
  - must cap at 30s
- Dead-letter dashboard

## Ledger

- Idempotency keys on posting
"""


class Harness(unittest.TestCase):
    """A temp git repo, a fake `gh` on PATH, and a call log."""

    def setUp(self):
        self._env = dict(os.environ)
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp())

        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "gh"
        fake.write_text(FAKE_GH)
        fake.chmod(0o755)
        self.payload = self.tmp / "payload.json"
        self.payload.write_text(json.dumps({"issue": ISSUE, "pr": PR}))
        self.log = self.tmp / "gh.log"
        os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"
        os.environ["FAKE_GH_LOG"] = str(self.log)
        os.environ["FAKE_GH_PAYLOAD"] = str(self.payload)
        os.environ["FAKE_GH_MODE"] = "ok"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        os.chdir(self._cwd)

    # --- the repo under test -------------------------------------------------

    def repo(self, external=False, punch_out=False, backlog=None, item="DEM-3", signers=True):
        d = self.tmp / "repo"
        d.mkdir(exist_ok=True)
        (d / ".git").mkdir(exist_ok=True)
        allowed = d / "allowed_signers"
        allowed.write_text("")   # configured but holding no key: nothing can verify against it
        (d / ".delivery-flow.yaml").write_text(
            "profile: triage\ntracker:\n  kind: local-markdown\n"
            f"  backlog: docs/backlog.md\n  external: {str(external).lower()}\n"
            + (f"decisions:\n  allowed_signers: {allowed}\n" if signers else ""))
        (d / "docs").mkdir(exist_ok=True)
        (d / "docs" / "backlog.md").write_text(backlog if backlog is not None else BACKLOG)
        item_dir = d / "delivery" / item
        item_dir.mkdir(parents=True, exist_ok=True)
        if punch_out:
            (item_dir / "punch-out-1.md").write_text("# Punch-out 1: architecture\n\nbody\n")
        os.chdir(d)
        return d

    # --- calling an adapter --------------------------------------------------

    def run_cmd(self, module, *argv):
        out, err = io.StringIO(), io.StringIO()
        real_stderr, sys.stderr = sys.stderr, err
        try:
            with redirect_stdout(out):
                code = module.main(list(argv))
        finally:
            sys.stderr = real_stderr
        return code, out.getvalue(), err.getvalue()

    def gh_calls(self) -> list:
        if not self.log.exists():
            return []
        return [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]

    def assert_valid_item(self, doc):
        problems = []
        validator.validate(doc, load_schemas()["item.json"], "", problems)
        self.assertEqual(problems, [])

    def issue(self, **overrides):
        self.payload.write_text(json.dumps({"issue": {**ISSUE, **overrides}, "pr": PR}))

    def pr(self, **overrides):
        self.payload.write_text(json.dumps({"issue": ISSUE, "pr": {**PR, **overrides}}))


class TestGithubIssuesMapping(Harness):
    def test_fetch_emits_a_valid_item(self):
        code, out, err = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(code, 0, err)
        item = json.loads(out)
        self.assertEqual(item["key"], "7")
        self.assertEqual(item["title"], "Retries hammer the DLQ consumer")  # stripped
        self.assertEqual(item["type_hint"], "bug")
        self.assertEqual(item["status"], "open")
        self.assertEqual(item["source"], "github-issues")
        self.assertEqual(item["url"], "https://github.com/acme/widgets/issues/7")
        self.assert_valid_item(item)

    def test_labels_are_sorted_and_deduped(self):
        self.issue(labels=[{"name": "ingest"}, {"name": "bug"}, {"name": "ingest"}])
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(json.loads(out)["labels"], ["bug", "ingest"])

    def test_the_type_hint_prefers_the_more_specific_label(self):
        self.issue(labels=[{"name": "task"}, {"name": "bug"}])
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(json.loads(out)["type_hint"], "bug")

    def test_no_type_label_is_a_null_hint_not_a_guess(self):
        self.issue(labels=[{"name": "ingest"}])
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertIsNone(json.loads(out)["type_hint"])

    def test_a_close_reason_survives_into_the_status(self):
        self.issue(state="CLOSED", stateReason="NOT_PLANNED")
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(json.loads(out)["status"], "closed:not_planned")

    def test_links_come_from_the_body_and_stay_in_this_repo(self):
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        # #1, #9, #3 and the same-repo URL for 4. Not 99: that is another repository's issue.
        self.assertEqual(json.loads(out)["links"], ["1", "3", "4", "9"])

    def test_the_issue_does_not_link_to_itself(self):
        self.issue(body="This duplicates #7 itself and relates to #3")
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(json.loads(out)["links"], ["3"])

    def test_a_word_glued_to_a_hash_is_not_a_reference(self):
        self.issue(body="tracked in acme#12 and at /issues/#13, relates to #3")
        _, out, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(json.loads(out)["links"], ["3"])

    def test_a_non_numeric_key_is_a_usage_error(self):
        code, _, err = self.run_cmd(github_issues, "fetch", "DEM-3")
        self.assertEqual(code, 2)
        self.assertIn("number", err)
        self.assertEqual(self.gh_calls(), [])

    def test_only_the_named_fields_are_requested(self):
        self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(self.gh_calls()[0],
                         ["issue", "view", "7", "--json", github_issues.FIELDS])

    def test_the_repo_flag_is_passed_through(self):
        self.run_cmd(github_issues, "fetch", "7", "--repo", "acme/widgets")
        self.assertEqual(self.gh_calls()[0][-2:], ["--repo", "acme/widgets"])


class TestGithubIssuesDeterminism(Harness):
    def test_two_fetches_are_byte_identical(self):
        _, first, _ = self.run_cmd(github_issues, "fetch", "7")
        _, second, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(first, second)

    def test_reordered_labels_produce_the_same_bytes(self):
        _, first, _ = self.run_cmd(github_issues, "fetch", "7")
        self.issue(labels=list(reversed(ISSUE["labels"])))
        _, second, _ = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(first, second)


class TestGithubIssuesRelated(Harness):
    def test_related_reads_the_line_each_reference_sits_on(self):
        code, out, err = self.run_cmd(github_issues, "related", "7")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out),
                         {"parent": "1", "design": ["9"], "related": ["3", "4"]})

    def test_a_parent_line_does_not_relabel_the_lines_below_it(self):
        self.issue(body="Epic: #1\nRelates to #3\n")
        _, out, _ = self.run_cmd(github_issues, "related", "7")
        self.assertEqual(json.loads(out)["related"], ["3"])

    def test_a_body_with_no_references_is_empty_not_absent(self):
        self.issue(body="No references at all.")
        code, out, _ = self.run_cmd(github_issues, "related", "7")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"parent": None, "design": [], "related": []})


class TestGithubIssuesFailures(Harness):
    def test_an_unauthenticated_gh_is_exit_3_with_the_remediation(self):
        os.environ["FAKE_GH_MODE"] = "auth"
        code, out, err = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(code, 3)
        self.assertIn("gh auth login", err)
        self.assertEqual(out, "")  # no partial item.json

    def test_a_missing_gh_is_exit_3_with_an_install_hint(self):
        os.environ["PATH"] = str(self.tmp / "empty")
        code, _, err = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(code, 3)
        self.assertIn("not installed", err)

    def test_an_unresolvable_issue_is_a_remote_failure(self):
        os.environ["FAKE_GH_MODE"] = "notfound"
        code, out, err = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(code, 3)
        self.assertEqual(out, "")

    def test_non_json_from_gh_is_a_remote_failure_not_a_crash(self):
        os.environ["FAKE_GH_MODE"] = "garbage"
        code, _, err = self.run_cmd(github_issues, "fetch", "7")
        self.assertEqual(code, 3)
        self.assertIn("not JSON", err)


class TestGithubIssuesWrites(Harness):
    def body_file(self, text="the brief"):
        p = self.tmp / "body.md"
        p.write_text(text)
        return str(p)

    def test_comment_posts_and_reports_its_id(self):
        self.repo()
        code, out, err = self.run_cmd(github_issues, "comment", "7",
                                      "--body-file", self.body_file())
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), {
            "posted": True, "id": "901",
            "url": "https://github.com/acme/widgets/issues/7#issuecomment-901"})

    def test_comment_refuses_while_a_punch_out_is_open_and_makes_no_call(self):
        self.repo(punch_out=True, item="7")
        code, _, err = self.run_cmd(github_issues, "comment", "7",
                                    "--body-file", self.body_file())
        self.assertEqual(code, 2)
        self.assertIn("unresolved punch-out is open", err)
        self.assertEqual(self.gh_calls(), [])

    def test_comment_on_an_external_tracker_needs_a_signed_decision(self):
        self.repo(external=True, item="7")
        code, _, err = self.run_cmd(github_issues, "comment", "7",
                                    "--body-file", self.body_file())
        self.assertEqual(code, 2)
        self.assertIn("signed decision", err)
        self.assertEqual(self.gh_calls(), [])

    def test_an_external_tracker_with_no_allowed_signers_refuses(self):
        """Nothing to verify against is a refusal, not a free pass."""
        self.repo(external=True, item="7", signers=False)
        code, _, err = self.run_cmd(github_issues, "comment", "7",
                                    "--body-file", self.body_file())
        self.assertEqual(code, 2)
        self.assertIn("allowed_signers", err)
        self.assertEqual(self.gh_calls(), [])

    def test_an_empty_body_is_refused(self):
        self.repo()
        code, _, err = self.run_cmd(github_issues, "comment", "7",
                                    "--body-file", self.body_file("  \n"))
        self.assertEqual(code, 2)
        self.assertIn("empty", err)
        self.assertEqual(self.gh_calls(), [])

    def test_transition_closes_with_a_reason(self):
        self.repo(item="7")
        code, out, err = self.run_cmd(github_issues, "transition", "7", "closed:not_planned")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), {"from": "open", "to": "closed:not_planned"})
        self.assertIn(["issue", "close", "7", "--reason", "not planned"], self.gh_calls())

    def test_transition_to_the_current_state_makes_no_call(self):
        self.repo(item="7")
        code, out, _ = self.run_cmd(github_issues, "transition", "7", "open")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"from": "open", "to": "open"})
        self.assertNotIn(["issue", "reopen", "7"], self.gh_calls())

    def test_an_unknown_state_lists_what_is_available(self):
        self.repo(item="7")
        code, _, err = self.run_cmd(github_issues, "transition", "7", "Shipped")
        self.assertEqual(code, 2)
        self.assertIn("available: open, closed", err)
        self.assertEqual(self.gh_calls(), [])

    def test_transition_refuses_while_a_punch_out_is_open(self):
        self.repo(punch_out=True, item="7")
        code, _, err = self.run_cmd(github_issues, "transition", "7", "closed")
        self.assertEqual(code, 2)
        self.assertIn("unresolved punch-out", err)
        self.assertEqual(self.gh_calls(), [])


class TestGithubPr(Harness):
    def body_file(self, text="## What\n\nthe change"):
        p = self.tmp / "pr-body.md"
        p.write_text(text)
        return str(p)

    def test_ci_status_normalizes_both_check_shapes(self):
        code, out, err = self.run_cmd(github_pr, "ci-status", "feat/x")
        self.assertEqual(code, 0, err)
        doc = json.loads(out)
        self.assertEqual(doc["state"], "pending")   # one check is still running
        self.assertEqual([(c["name"], c["state"]) for c in doc["checks"]],
                         [("build", "passing"), ("legacy/status", "passing"), ("test", "pending")])

    def test_a_failing_check_fails_the_rollup(self):
        self.pr(statusCheckRollup=[
            {"name": "build", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "test", "status": "COMPLETED", "conclusion": "FAILURE"}])
        _, out, _ = self.run_cmd(github_pr, "ci-status", "feat/x")
        self.assertEqual(json.loads(out)["state"], "failing")

    def test_no_checks_is_none_not_passing(self):
        self.pr(statusCheckRollup=[])
        _, out, _ = self.run_cmd(github_pr, "ci-status", "feat/x")
        self.assertEqual(json.loads(out)["state"], "none")

    def test_an_unrecognized_conclusion_does_not_count_as_green(self):
        """A rollup this adapter does not understand must not read as passing."""
        self.pr(statusCheckRollup=[
            {"name": "build", "status": "COMPLETED", "conclusion": "SOMETHING_NEW"}])
        _, out, _ = self.run_cmd(github_pr, "ci-status", "feat/x")
        doc = json.loads(out)
        self.assertEqual(doc["state"], "failing")
        self.assertEqual(doc["checks"][0]["state"], "something_new")

    def test_a_skipped_check_does_not_hold_the_rollup_back(self):
        self.pr(statusCheckRollup=[
            {"name": "build", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "optional", "status": "COMPLETED", "conclusion": "SKIPPED"}])
        _, out, _ = self.run_cmd(github_pr, "ci-status", "feat/x")
        self.assertEqual(json.loads(out)["state"], "passing")

    def test_ci_status_is_deterministic(self):
        _, first, _ = self.run_cmd(github_pr, "ci-status", "feat/x")
        self.pr(statusCheckRollup=list(reversed(PR["statusCheckRollup"])))
        _, second, _ = self.run_cmd(github_pr, "ci-status", "feat/x")
        self.assertEqual(first, second)

    def test_open_pr_reports_the_url_and_number(self):
        self.repo(item="DEM-12")
        code, out, err = self.run_cmd(
            github_pr, "open-pr", "--item", "DEM-12", "--head", "feat/x", "--base", "main",
            "--title", "Fix the DLQ", "--body-file", self.body_file())
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out),
                         {"url": "https://github.com/acme/widgets/pull/42", "number": "42"})

    def test_open_pr_refuses_during_a_punch_out_and_makes_no_call(self):
        self.repo(item="DEM-12", punch_out=True)
        code, _, err = self.run_cmd(
            github_pr, "open-pr", "--item", "DEM-12", "--head", "feat/x", "--base", "main",
            "--title", "Fix the DLQ", "--body-file", self.body_file())
        self.assertEqual(code, 2)
        self.assertIn("punch-out-1.md", err)
        self.assertEqual(self.gh_calls(), [])

    def test_open_pr_refuses_an_empty_body(self):
        self.repo(item="DEM-12")
        code, _, err = self.run_cmd(
            github_pr, "open-pr", "--item", "DEM-12", "--head", "feat/x", "--base", "main",
            "--title", "t", "--body-file", self.body_file("\n  \n"))
        self.assertEqual(code, 2)
        self.assertIn("empty", err)
        self.assertEqual(self.gh_calls(), [])

    def test_open_pr_outside_a_delivery_repo_refuses(self):
        os.chdir(self.tmp)
        code, _, err = self.run_cmd(
            github_pr, "open-pr", "--item", "DEM-12", "--head", "feat/x", "--base", "main",
            "--title", "t", "--body-file", self.body_file())
        self.assertEqual(code, 2)
        self.assertIn("not a delivery-flow repo", err)
        self.assertEqual(self.gh_calls(), [])


class TestLocalMarkdown(Harness):
    def test_fetch_emits_a_valid_item(self):
        self.repo()
        code, out, err = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.assertEqual(code, 0, err)
        item = json.loads(out)
        self.assertEqual(item["key"], "DEM-3")
        self.assertEqual(item["title"], "Retries hammer the DLQ consumer")
        self.assertEqual(item["type_hint"], "bug")
        self.assertEqual(item["status"], "todo")
        self.assertEqual(item["source"], "local-markdown")
        self.assertEqual(item["labels"], ["consumer", "ingest"])
        self.assertEqual(item["links"], ["DEM-1", "DEM-4", "DEM-5", "DEM-9"])
        self.assert_valid_item(item)

    def test_the_body_excludes_the_flows_own_comments(self):
        self.repo()
        _, out, _ = self.run_cmd(local_markdown, "fetch", "DEM-3")
        body = json.loads(out)["body"]
        self.assertIn("collapses the downstream", body)
        self.assertIn("Acceptance: delays grow to a 30s cap.", body)
        self.assertNotIn("post-back", body)
        self.assertNotIn("Comment 1", body)

    def test_the_url_is_repo_relative_so_two_machines_agree(self):
        self.repo()
        _, out, _ = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.assertEqual(json.loads(out)["url"], "docs/backlog.md#DEM-3")

    def test_two_fetches_are_byte_identical(self):
        self.repo()
        _, first, _ = self.run_cmd(local_markdown, "fetch", "DEM-3")
        _, second, _ = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.assertEqual(first, second)

    def test_an_item_without_a_status_line_reports_an_empty_status(self):
        self.repo()
        _, out, _ = self.run_cmd(local_markdown, "fetch", "DEM-4")
        self.assertEqual(json.loads(out)["status"], "")

    def test_an_unknown_key_lists_what_the_backlog_holds(self):
        self.repo()
        code, _, err = self.run_cmd(local_markdown, "fetch", "DEM-99")
        self.assertEqual(code, 2)
        self.assertIn("DEM-3", err)
        self.assertIn("DEM-4", err)

    def test_a_missing_backlog_is_a_usage_error_with_the_fix(self):
        d = self.repo()
        (d / "docs" / "backlog.md").unlink()
        code, _, err = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.assertEqual(code, 2)
        self.assertIn("import", err)

    def test_outside_a_delivery_repo_the_backlog_must_be_named(self):
        os.chdir(self.tmp)
        code, _, err = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.assertEqual(code, 2)
        self.assertIn("--backlog", err)

    def test_related_splits_the_metadata_lines(self):
        self.repo()
        code, out, err = self.run_cmd(local_markdown, "related", "DEM-3")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), {"parent": "DEM-1", "design": ["DEM-9"],
                                           "related": ["DEM-4", "DEM-5"]})


class TestLocalMarkdownWrites(Harness):
    def body_file(self, text="Triaged as a bug."):
        p = self.tmp / "comment.md"
        p.write_text(text)
        return str(p)

    def test_comment_appends_a_numbered_dated_block(self):
        d = self.repo()
        code, out, err = self.run_cmd(local_markdown, "comment", "DEM-3",
                                      "--body-file", self.body_file())
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["id"], "comment-2")  # Comment 1 is already there
        text = (d / "docs" / "backlog.md").read_text()
        self.assertIn("#### Comment 2 — ", text)
        self.assertIn("Triaged as a bug.", text)

    def test_a_comment_lands_inside_its_own_item(self):
        d = self.repo()
        self.run_cmd(local_markdown, "comment", "DEM-3", "--body-file", self.body_file())
        text = (d / "docs" / "backlog.md").read_text()
        self.assertLess(text.index("Triaged as a bug."), text.index("### DEM-4:"))

    def test_a_posted_comment_does_not_become_the_next_runs_requirement(self):
        self.repo()
        _, before, _ = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.run_cmd(local_markdown, "comment", "DEM-3", "--body-file", self.body_file())
        _, after, _ = self.run_cmd(local_markdown, "fetch", "DEM-3")
        self.assertEqual(json.loads(before)["body"], json.loads(after)["body"])

    def test_comment_refuses_while_a_punch_out_is_open_and_writes_nothing(self):
        d = self.repo(punch_out=True)
        before = (d / "docs" / "backlog.md").read_text()
        code, _, err = self.run_cmd(local_markdown, "comment", "DEM-3",
                                    "--body-file", self.body_file())
        self.assertEqual(code, 2)
        self.assertIn("unresolved punch-out is open", err)
        self.assertEqual((d / "docs" / "backlog.md").read_text(), before)

    def test_transition_rewrites_the_status_line(self):
        d = self.repo()
        code, out, err = self.run_cmd(local_markdown, "transition", "DEM-3", "in-progress")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), {"from": "todo", "to": "in-progress"})
        self.assertIn("Status: in-progress", (d / "docs" / "backlog.md").read_text())

    def test_transition_adds_a_status_line_where_the_item_has_none(self):
        d = self.repo()
        code, out, err = self.run_cmd(local_markdown, "transition", "DEM-4", "done")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), {"from": "", "to": "done"})
        _, item, _ = self.run_cmd(local_markdown, "fetch", "DEM-4")
        self.assertEqual(json.loads(item)["status"], "done")

    def test_an_unknown_state_lists_what_is_available(self):
        d = self.repo()
        before = (d / "docs" / "backlog.md").read_text()
        code, _, err = self.run_cmd(local_markdown, "transition", "DEM-3", "shipped")
        self.assertEqual(code, 2)
        self.assertIn("Available: todo, in-progress", err)
        self.assertEqual((d / "docs" / "backlog.md").read_text(), before)

    def test_transition_refuses_while_a_punch_out_is_open(self):
        d = self.repo(punch_out=True)
        before = (d / "docs" / "backlog.md").read_text()
        code, _, err = self.run_cmd(local_markdown, "transition", "DEM-3", "done")
        self.assertEqual(code, 2)
        self.assertEqual((d / "docs" / "backlog.md").read_text(), before)


class TestLocalMarkdownImport(Harness):
    def source(self, text=BULLETS):
        p = self.tmp / "wishlist.md"
        p.write_text(text)
        return p

    def test_import_leaves_the_source_untouched(self):
        src = self.source()
        before = src.read_text()
        out = self.tmp / "imported.md"
        code, stdout, err = self.run_cmd(local_markdown, "import", str(src),
                                         "--prefix", "OLY", "--out", str(out))
        self.assertEqual(code, 0, err)
        self.assertEqual(src.read_text(), before)
        self.assertEqual(json.loads(stdout)["imported"], 3)

    def test_imported_items_are_keyed_and_fetchable(self):
        src = self.source()
        d = self.repo()
        out = d / "docs" / "imported.md"
        self.run_cmd(local_markdown, "import", str(src), "--prefix", "OLY", "--out", str(out))
        code, item, err = self.run_cmd(local_markdown, "fetch", "OLY-1",
                                       "--backlog", str(out))
        self.assertEqual(code, 0, err)
        doc = json.loads(item)
        self.assertEqual(doc["title"], "Retry with backoff on the DLQ consumer")
        self.assertEqual(doc["status"], "todo")
        self.assert_valid_item(doc)

    def test_a_sub_bullet_is_body_not_a_second_item(self):
        src = self.source()
        out = self.tmp / "imported.md"
        _, stdout, _ = self.run_cmd(local_markdown, "import", str(src),
                                    "--prefix", "OLY", "--out", str(out))
        self.assertEqual(json.loads(stdout)["imported"], 3)
        _, item, _ = self.run_cmd(local_markdown, "fetch", "OLY-1", "--backlog", str(out))
        self.assertIn("must cap at 30s", json.loads(item)["body"])

    def test_the_source_headings_survive_as_group_headings(self):
        src = self.source()
        out = self.tmp / "imported.md"
        self.run_cmd(local_markdown, "import", str(src), "--prefix", "OLY", "--out", str(out))
        text = out.read_text()
        self.assertIn("## Payments service", text)
        self.assertIn("## Ledger", text)

    def test_import_refuses_to_overwrite(self):
        src = self.source()
        out = self.tmp / "imported.md"
        out.write_text("mine\n")
        code, _, err = self.run_cmd(local_markdown, "import", str(src),
                                    "--prefix", "OLY", "--out", str(out))
        self.assertEqual(code, 2)
        self.assertIn("--force", err)
        self.assertEqual(out.read_text(), "mine\n")

    def test_import_refuses_to_write_over_its_own_source(self):
        src = self.source()
        code, _, err = self.run_cmd(local_markdown, "import", str(src),
                                    "--prefix", "OLY", "--out", str(src), "--force")
        self.assertEqual(code, 2)
        self.assertIn("never rewrites the source", err)

    def test_a_bad_prefix_is_refused_before_anything_is_written(self):
        src = self.source()
        out = self.tmp / "imported.md"
        code, _, err = self.run_cmd(local_markdown, "import", str(src),
                                    "--prefix", "OLY 3/x", "--out", str(out))
        self.assertEqual(code, 2)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
