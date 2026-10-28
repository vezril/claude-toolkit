#!/usr/bin/env python3
"""Tests for the Jira adapter: the mapping, determinism, typed failures, and the refusals.

No network. The Jira endpoint is replaced by a recorded fixture, which is the point of making
adapters scripts: the contract is testable without a site.

Run: python3 tests/delivery-flow/test_jira_adapter.py
"""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "delivery-flow"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location("jira_adapter", SCRIPTS / "adapters" / "jira.py")
jira = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jira)

ENV = {"JIRA_BASE_URL": "https://client.atlassian.net/",
       "JIRA_EMAIL": "me@example.invalid", "JIRA_API_TOKEN": "t0ken"}

# A recorded issue: ADF description, labels and components, two links and an epic parent.
ISSUE = {
    "key": "CLI-7",
    "fields": {
        "summary": "  Retries hammer the DLQ consumer  ",
        "issuetype": {"name": "Story"},
        "status": {"name": "In Progress"},
        "labels": ["dlq", "ingest"],
        "components": [{"name": "consumer"}, {"name": "ingest"}],
        "parent": {"key": "CLI-1"},
        "issuelinks": [
            {"type": {"name": "Relates"}, "outwardIssue": {"key": "CLI-3"}},
            {"type": {"name": "Documented by"}, "outwardIssue": {"key": "CLI-9"}},
        ],
        "description": {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "The consumer retries with no backoff."},
                {"type": "hardBreak"},
                {"type": "text", "text": "It collapses the downstream."}]},
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [{"type": "paragraph", "content": [
                    {"type": "text", "text": "Acceptance: delays grow to a 30s cap"}]}]}]},
        ]},
        # A site-specific custom field the adapter must ignore rather than guess at.
        "customfield_10016": 5,
    },
}

TRANSITIONS = {"transitions": [
    {"id": "31", "name": "Done", "to": {"name": "Done"}},
    {"id": "21", "name": "Start", "to": {"name": "In Progress"}},
]}


class FakeJira:
    """Replaces jira.call. Records what was asked for; raises what it is told to."""

    def __init__(self, issue=ISSUE, raise_for=None):
        self.issue, self.raise_for, self.calls = issue, raise_for, []

    def __call__(self, method, path, body=None, query=None):
        self.calls.append({"method": method, "path": path, "body": body, "query": query})
        if self.raise_for:
            raise self.raise_for
        if path.endswith("/transitions") and method == "GET":
            return TRANSITIONS
        if path.endswith("/transitions"):
            return {}
        if path.endswith("/comment"):
            return {"id": "10501", "self": "https://client.atlassian.net/rest/api/3/comment/10501"}
        return self.issue


class Base(unittest.TestCase):
    def setUp(self):
        self._env = dict(os.environ)
        os.environ.update(ENV)
        self._call = jira.call
        self.fake = FakeJira()
        jira.call = self.fake
        self.cwd = Path.cwd()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        jira.call = self._call
        os.chdir(self.cwd)

    def run_cmd(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = jira.main(list(argv))
        return code, out.getvalue()

    def repo(self, external=True, punch_out=False, decision=None, item="CLI-7"):
        """`decision` is None, "unsigned", or "signed"."""
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        key = d / "signing_key"
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "test", "-f", str(key)],
                       capture_output=True, check=True)
        pub = (key.with_suffix(".pub")).read_text().strip()
        signers = d / "allowed_signers"
        signers.write_text(f"calvin {' '.join(pub.split()[:2])}\n")
        (d / ".delivery-flow.yaml").write_text(
            "tracker:\n  kind: jira\n" + f"  external: {str(external).lower()}\n"
            + "profile: triage\nvault:\n  binding: null\n"
            + f"decisions:\n  allowed_signers: {signers}\n")
        item_dir = d / "delivery" / item
        item_dir.mkdir(parents=True)
        if punch_out:
            (item_dir / "punch-out-1.md").write_text("# Punch-out 1: architecture\n\nbody\n")
        if decision:
            (item_dir / "decisions").mkdir()
            doc = {"id": "punch-out-1", "item": item, "choice": "proceed", "decider": "calvin"}
            if decision == "signed":
                payload = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
                out = subprocess.run(
                    ["ssh-keygen", "-Y", "sign", "-f", str(key), "-n", "delivery-flow-decision"],
                    input=payload, capture_output=True, check=True)
                doc["signature"] = out.stdout.decode()
            (item_dir / "decisions" / "punch-out-1.json").write_text(json.dumps(doc))
        os.chdir(d)
        return d, item_dir


class TestMapping(Base):
    def test_fetch_emits_a_valid_item(self):
        code, out = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(code, 0)
        item = json.loads(out)
        self.assertEqual(item["key"], "CLI-7")
        self.assertEqual(item["title"], "Retries hammer the DLQ consumer")  # stripped
        self.assertEqual(item["type_hint"], "Story")
        self.assertEqual(item["status"], "In Progress")
        self.assertEqual(item["source"], "jira")
        self.assertEqual(item["url"], "https://client.atlassian.net/browse/CLI-7")

    def test_the_item_satisfies_its_schema(self):
        from common import load_schemas
        validator_spec = importlib.util.spec_from_file_location(
            "validate_artifact", SCRIPTS / "validate-artifact.py")
        validator = importlib.util.module_from_spec(validator_spec)
        validator_spec.loader.exec_module(validator)
        _, out = self.run_cmd("fetch", "CLI-7")
        problems = []
        validator.validate(json.loads(out), load_schemas()["item.json"], "", problems)
        self.assertEqual(problems, [])

    def test_labels_and_components_merge_and_dedupe(self):
        _, out = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(json.loads(out)["labels"], ["consumer", "dlq", "ingest"])

    def test_links_include_the_parent_and_are_sorted(self):
        _, out = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(json.loads(out)["links"], ["CLI-1", "CLI-3", "CLI-9"])

    def test_custom_fields_are_omitted_not_guessed(self):
        _, out = self.run_cmd("fetch", "CLI-7")
        item = json.loads(out)
        self.assertNotIn("customfield_10016", item)
        self.assertNotIn("story_points", item)

    def test_only_the_named_fields_are_requested(self):
        self.run_cmd("fetch", "CLI-7")
        self.assertEqual(self.fake.calls[0]["query"], {"fields": ",".join(jira.FIELDS)})

    def test_adf_is_flattened_to_text(self):
        _, out = self.run_cmd("fetch", "CLI-7")
        body = json.loads(out)["body"]
        self.assertIn("The consumer retries with no backoff.", body)
        self.assertIn("It collapses the downstream.", body)
        self.assertIn("- Acceptance: delays grow to a 30s cap", body)
        self.assertNotIn("hardBreak", body)
        self.assertNotIn("{", body)

    def test_a_plain_string_description_still_works(self):
        """Some sites and the v2 API return a string, not ADF."""
        self.fake.issue = {**ISSUE, "fields": {**ISSUE["fields"], "description": "just text"}}
        _, out = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(json.loads(out)["body"], "just text")

    def test_a_missing_description_is_an_empty_body_not_a_crash(self):
        fields = {k: v for k, v in ISSUE["fields"].items() if k != "description"}
        self.fake.issue = {**ISSUE, "fields": fields}
        code, out = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["body"], "")


class TestDeterminism(Base):
    def test_two_fetches_are_byte_identical(self):
        _, first = self.run_cmd("fetch", "CLI-7")
        _, second = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(first, second)

    def test_reordered_labels_and_links_produce_the_same_bytes(self):
        _, first = self.run_cmd("fetch", "CLI-7")
        shuffled = json.loads(json.dumps(ISSUE))
        shuffled["fields"]["labels"] = ["ingest", "dlq"]
        shuffled["fields"]["components"] = [{"name": "ingest"}, {"name": "consumer"}]
        shuffled["fields"]["issuelinks"].reverse()
        self.fake.issue = shuffled
        _, second = self.run_cmd("fetch", "CLI-7")
        self.assertEqual(first, second)


class TestRelated(Base):
    def test_related_splits_design_links_from_the_rest(self):
        code, out = self.run_cmd("related", "CLI-7")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out),
                         {"design": ["CLI-9"], "parent": "CLI-1", "related": ["CLI-3"]})


class TestCredentialsAndFailures(Base):
    def test_a_missing_token_is_a_usage_error(self):
        jira.call = self._call  # the real call, so credentials() runs
        del os.environ["JIRA_API_TOKEN"]
        err = io.StringIO()
        with redirect_stdout(io.StringIO()):
            sys.stderr, old = err, sys.stderr
            try:
                code = jira.main(["fetch", "CLI-7"])
            finally:
                sys.stderr = old
        self.assertEqual(code, 2)
        self.assertIn("JIRA_API_TOKEN", err.getvalue())

    def test_a_rejected_credential_is_a_remote_failure(self):
        self.fake.raise_for = jira.Remote("Jira rejected the credentials (401).")
        err = io.StringIO()
        sys.stderr, old = err, sys.stderr
        try:
            code = jira.main(["fetch", "CLI-7"])
        finally:
            sys.stderr = old
        self.assertEqual(code, 3)
        self.assertIn("401", err.getvalue())

    def test_an_http_error_maps_to_exit_3(self):
        """401/403/404 and anything unexpected belong to the other end, not the caller."""
        jira.call = self._call
        real_urlopen = jira.urllib.request.urlopen

        def boom(*a, **k):
            raise urllib.error.HTTPError("u", 403, "Forbidden", {}, io.BytesIO(b"nope"))
        jira.urllib.request.urlopen = boom
        try:
            with self.assertRaises(jira.Remote) as cm:
                jira.call("GET", "/rest/api/3/issue/CLI-7")
            self.assertIn("rejected the credentials", str(cm.exception))
        finally:
            jira.urllib.request.urlopen = real_urlopen

    def test_no_partial_artifact_is_written_on_failure(self):
        self.fake.raise_for = jira.Remote("down")
        out = io.StringIO()
        err = io.StringIO()
        sys.stderr, old = err, sys.stderr
        try:
            with redirect_stdout(out):
                code = jira.main(["fetch", "CLI-7"])
        finally:
            sys.stderr = old
        self.assertEqual(code, 3)
        self.assertEqual(out.getvalue(), "")


class TestRefusals(Base):
    def _comment(self, item_dir, text="the brief"):
        body = item_dir / "summary.md"
        body.write_text(text)
        err = io.StringIO()
        out = io.StringIO()
        sys.stderr, old = err, sys.stderr
        try:
            with redirect_stdout(out):
                code = jira.main(["comment", "CLI-7", "--body-file", str(body)])
        finally:
            sys.stderr = old
        return code, out.getvalue(), err.getvalue()

    def test_comment_refuses_while_a_punch_out_is_open(self):
        _, item_dir = self.repo(external=False, punch_out=True)
        code, _, err = self._comment(item_dir)
        self.assertEqual(code, 2)
        self.assertIn("unresolved punch-out is open", err)
        self.assertEqual(self.fake.calls, [])

    def test_comment_on_an_external_tracker_needs_a_decision(self):
        _, item_dir = self.repo(external=True)
        code, _, err = self._comment(item_dir)
        self.assertEqual(code, 2)
        self.assertIn("signed decision", err)
        self.assertEqual(self.fake.calls, [])

    def test_comment_proceeds_on_an_internal_tracker(self):
        _, item_dir = self.repo(external=False)
        code, out, err = self._comment(item_dir)
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["posted"], True)

    def test_comment_proceeds_on_an_external_tracker_with_a_signed_decision(self):
        _, item_dir = self.repo(external=True, decision="signed")
        code, out, err = self._comment(item_dir)
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["id"], "10501")

    def test_an_unsigned_decision_does_not_authorize_a_post(self):
        """A file an agent can write is not a human decision."""
        _, item_dir = self.repo(external=True, decision="unsigned")
        code, _, err = self._comment(item_dir)
        self.assertEqual(code, 2)
        self.assertIn("verifiable human signature", err)
        self.assertEqual(self.fake.calls, [])

    def test_a_decision_signed_by_a_key_outside_allowed_signers_is_refused(self):
        d, item_dir = self.repo(external=True, decision="signed")
        # Replace allowed_signers with a different key: the signature no longer verifies.
        other = d / "other_key"
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-C", "x", "-f", str(other)],
                       capture_output=True, check=True)
        pub = (other.with_suffix(".pub")).read_text().strip()
        (d / "allowed_signers").write_text(f"calvin {' '.join(pub.split()[:2])}\n")
        code, _, err = self._comment(item_dir)
        self.assertEqual(code, 2)
        self.assertEqual(self.fake.calls, [])

    def test_an_external_tracker_with_no_allowed_signers_refuses(self):
        d, item_dir = self.repo(external=True, decision="signed")
        cfg = (d / ".delivery-flow.yaml").read_text()
        (d / ".delivery-flow.yaml").write_text(
            "\n".join(l for l in cfg.split("\n") if "allowed_signers" not in l))
        code, _, err = self._comment(item_dir)
        self.assertEqual(code, 2)
        self.assertIn("allowed_signers", err)

    def test_an_empty_body_is_refused(self):
        _, item_dir = self.repo(external=False)
        code, _, err = self._comment(item_dir, text="   \n")
        self.assertEqual(code, 2)
        self.assertIn("empty", err)

    def test_the_comment_body_is_sent_as_adf(self):
        _, item_dir = self.repo(external=False)
        self._comment(item_dir, text="first block\n\nsecond block")
        body = [c for c in self.fake.calls if c["path"].endswith("/comment")][0]["body"]
        self.assertEqual(body["body"]["type"], "doc")
        texts = [p["content"][0]["text"] for p in body["body"]["content"]]
        self.assertEqual(texts, ["first block", "second block"])

    def test_transition_refuses_while_a_punch_out_is_open(self):
        _, _ = self.repo(external=False, punch_out=True)
        err = io.StringIO()
        sys.stderr, old = err, sys.stderr
        try:
            code = jira.main(["transition", "CLI-7", "Done"])
        finally:
            sys.stderr = old
        self.assertEqual(code, 2)
        self.assertIn("unresolved punch-out", err.getvalue())


STUB_DESCRIPTION = {"type": "doc", "version": 1, "content": [
    {"type": "paragraph", "content": [
        {"type": "text", "text": "github reference: "},
        {"type": "text", "text": "https://github.com/awslabs/widgets/issues/579"}]}]}

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
argv = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a") as f:
    f.write(json.dumps(argv) + "\n")
if os.environ.get("FAKE_GH_MODE") == "fail":
    sys.stderr.write("could not resolve to an Issue with the number of 579\n")
    sys.exit(1)
print(json.dumps(json.load(open(os.environ["FAKE_GH_PAYLOAD"]))))
'''

LINKED = {
    "number": 579,
    "title": "Proxy state lost on every make up",
    "body": "The compose file mounts no volume for proxy.db, so state resets.\n\n"
            "Acceptance: proxy.db survives a restart.",
    "labels": [{"name": "bug"}],
    "state": "OPEN",
    "stateReason": None,
    "url": "https://github.com/awslabs/widgets/issues/579",
}


class FollowBase(Base):
    """A Jira issue whose description is only a GitHub link, plus a fake `gh` on PATH."""

    def setUp(self):
        super().setUp()
        self.tmp = Path(tempfile.mkdtemp())
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.payload = self.tmp / "linked.json"
        self.payload.write_text(json.dumps(LINKED))
        self.log = self.tmp / "gh.log"
        os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"
        os.environ["FAKE_GH_LOG"] = str(self.log)
        os.environ["FAKE_GH_PAYLOAD"] = str(self.payload)
        os.environ["FAKE_GH_MODE"] = "ok"
        self.fake.issue = {**ISSUE, "fields": {**ISSUE["fields"],
                                               "description": STUB_DESCRIPTION}}

    def gh_calls(self) -> list:
        if not self.log.exists():
            return []
        return [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]

    def fetch(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        real, sys.stderr = sys.stderr, err
        try:
            with redirect_stdout(out):
                code = jira.main(["fetch", "CLI-7", *extra])
        finally:
            sys.stderr = real
        return code, out.getvalue(), err.getvalue()


class TestFollowGithubReference(FollowBase):
    def test_a_stub_ticket_gains_the_linked_requirement(self):
        code, out, err = self.fetch()
        self.assertEqual(code, 0, err)
        body = json.loads(out)["body"]
        self.assertIn("github reference:", body)              # the Jira text is kept
        self.assertIn("Proxy state lost on every make up", body)
        self.assertIn("mounts no volume for proxy.db", body)
        self.assertIn("Acceptance: proxy.db survives a restart.", body)

    def test_the_reference_is_recorded_with_its_repo_and_number(self):
        _, out, _ = self.fetch()
        self.assertEqual(json.loads(out)["references"], [{
            "url": "https://github.com/awslabs/widgets/issues/579",
            "repo": "awslabs/widgets", "number": "579", "kind": "issue",
            "title": "Proxy state lost on every make up"}])

    def test_the_linked_body_is_fenced_and_marked_unverified(self):
        """A stranger's issue text must not read as the client's own requirement."""
        _, out, _ = self.fetch()
        body = json.loads(out)["body"]
        self.assertIn("----- referenced issue awslabs/widgets#579", body)
        self.assertIn("unverified", body)
        self.assertIn("----- end referenced issue awslabs/widgets#579", body)
        self.assertLess(body.index("----- referenced issue"),
                        body.index("mounts no volume"))

    def test_the_repo_comes_from_the_url_not_the_working_directory(self):
        self.fetch()
        self.assertIn(["issue", "view", "579", "--json", github_issues_fields(),
                       "--repo", "awslabs/widgets"], self.gh_calls())

    def test_the_item_still_satisfies_its_schema(self):
        from common import load_schemas
        vspec = importlib.util.spec_from_file_location(
            "validate_artifact", SCRIPTS / "validate-artifact.py")
        v = importlib.util.module_from_spec(vspec)
        vspec.loader.exec_module(v)
        _, out, _ = self.fetch()
        problems = []
        v.validate(json.loads(out), load_schemas()["item.json"], "", problems)
        self.assertEqual(problems, [])

    def test_links_stay_jira_keys_only(self):
        """A GitHub number in `links` would be read downstream as a tracker key."""
        _, out, _ = self.fetch()
        self.assertEqual(json.loads(out)["links"], ["CLI-1", "CLI-3", "CLI-9"])
        self.assertNotIn("579", json.loads(out)["links"])

    def test_two_fetches_are_byte_identical(self):
        _, first, _ = self.fetch()
        _, second, _ = self.fetch()
        self.assertEqual(first, second)

    def test_a_repeated_url_is_fetched_once(self):
        self.fake.issue = {**ISSUE, "fields": {**ISSUE["fields"], "description":
                           "see https://github.com/awslabs/widgets/issues/579 — "
                           "again https://github.com/awslabs/widgets/issues/579"}}
        _, out, _ = self.fetch()
        self.assertEqual(len(json.loads(out)["references"]), 1)
        self.assertEqual(len([c for c in self.gh_calls() if c[:2] == ["issue", "view"]]), 1)

    def test_a_pull_request_reference_is_labelled_as_one(self):
        self.fake.issue = {**ISSUE, "fields": {**ISSUE["fields"], "description":
                           "fixed by https://github.com/awslabs/widgets/pull/42"}}
        _, out, _ = self.fetch()
        self.assertEqual(json.loads(out)["references"][0]["kind"], "pull request")

    def test_an_empty_linked_body_is_stated_not_silently_omitted(self):
        self.payload.write_text(json.dumps({**LINKED, "body": ""}))
        _, out, _ = self.fetch()
        self.assertIn("the referenced issue has an empty body", json.loads(out)["body"])


class TestFollowFailures(FollowBase):
    def test_an_unfetchable_reference_is_exit_3_not_a_thinner_body(self):
        """Soft-failing would make `body` a function of network state."""
        os.environ["FAKE_GH_MODE"] = "fail"
        code, out, err = self.fetch()
        self.assertEqual(code, 3)
        self.assertEqual(out, "")                      # no partial item
        self.assertIn("issues/579", err)
        self.assertIn("--no-follow", err)

    def test_no_follow_takes_the_ticket_at_face_value(self):
        os.environ["FAKE_GH_MODE"] = "fail"
        code, out, err = self.fetch("--no-follow")
        self.assertEqual(code, 0, err)
        item = json.loads(out)
        self.assertNotIn("referenced issue", item["body"])
        self.assertEqual(self.gh_calls(), [])

    def test_no_follow_still_records_what_it_did_not_fetch(self):
        code, out, _ = self.fetch("--no-follow")
        self.assertEqual(code, 0)
        refs = json.loads(out)["references"]
        self.assertEqual(refs[0]["number"], "579")
        self.assertNotIn("title", refs[0])             # nothing was read, so nothing is claimed

    def test_a_ticket_with_no_reference_makes_no_gh_call(self):
        code, out, err = self.fetch()                  # the default ISSUE has no GitHub link
        self.fake.issue = ISSUE
        code, out, err = self.fetch()
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["references"], [])


def github_issues_fields() -> str:
    sys.path.insert(0, str(SCRIPTS / "adapters"))
    import github_issues
    return github_issues.FIELDS


class TestTransition(Base):
    def test_a_known_transition_reports_from_and_to(self):
        self.repo(external=False)
        code, out = self.run_cmd("transition", "CLI-7", "Done")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"from": "In Progress", "to": "Done"})

    def test_an_unknown_state_lists_what_is_available(self):
        self.repo(external=False)
        err = io.StringIO()
        sys.stderr, old = err, sys.stderr
        try:
            code = jira.main(["transition", "CLI-7", "Shipped"])
        finally:
            sys.stderr = old
        self.assertEqual(code, 2)
        self.assertIn("Available:", err.getvalue())
        self.assertIn("Done", err.getvalue())

    def test_the_target_state_name_also_matches(self):
        self.repo(external=False)
        code, out = self.run_cmd("transition", "CLI-7", "in progress")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["to"], "In Progress")


if __name__ == "__main__":
    unittest.main(verbosity=2)
